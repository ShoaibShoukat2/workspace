"""
Admin Payout & Financial Flow Views
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from datetime import datetime, timedelta
import csv
from io import StringIO

from .models import (
    Contractor, ContractorWallet, WalletTransaction, PayoutRequest,
    JobPayoutEligibility, Payout, Job, JobCompletion
)
from .serializers import (
    ContractorWalletSerializer, WalletTransactionSerializer,
    PayoutRequestSerializer, JobPayoutEligibilitySerializer,
    PayoutSerializer
)
from .utils import generate_payout_number
from authentication.permissions import IsAdmin, IsAdminOrFM


# ==================== Admin Payout Management ====================

class ReadyForPayoutJobsView(generics.ListAPIView):
    """Admin views all jobs ready for payout"""
    serializer_class = JobPayoutEligibilitySerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        queryset = JobPayoutEligibility.objects.filter(status='READY')
        
        # Filter by contractor
        contractor_id = self.request.query_params.get('contractor_id')
        if contractor_id:
            queryset = queryset.filter(contractor_id=contractor_id)
        
        return queryset.order_by('-created_at')


class ApproveJobPayoutView(APIView):
    """Admin approves job for payout"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, eligibility_id):
        eligibility = get_object_or_404(JobPayoutEligibility, id=eligibility_id)
        
        if eligibility.status != 'READY':
            return Response(
                {'error': 'Job is not ready for payout'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create contractor wallet
        wallet, created = ContractorWallet.objects.get_or_create(
            contractor=eligibility.contractor
        )
        
        # Create payout record
        payout_number = generate_payout_number(eligibility.job.workspace.workspace_id)
        payout = Payout.objects.create(
            workspace=eligibility.job.workspace,
            contractor=eligibility.contractor,
            job=eligibility.job,
            payout_number=payout_number,
            amount=eligibility.amount,
            status='COMPLETED',
            payment_method='BANK_TRANSFER',
            description=f'Payment for job {eligibility.job.job_number}',
            paid_date=timezone.now().date(),
            processed_by=request.user
        )
        
        # Credit contractor wallet
        wallet.credit(
            amount=eligibility.amount,
            description=f'Payment for job {eligibility.job.job_number}'
        )
        
        # Mark eligibility as paid
        eligibility.mark_as_paid(payout)
        
        # Create notification
        from .models import JobNotification
        JobNotification.objects.create(
            recipient=eligibility.contractor.user,
            job=eligibility.job,
            notification_type='JOB_VERIFIED',
            title=f'Payment Received: ${eligibility.amount}',
            message=f'Payment of ${eligibility.amount} has been credited to your wallet for job {eligibility.job.job_number}'
        )
        
        return Response({
            'message': 'Payout approved and wallet credited successfully',
            'payout': PayoutSerializer(payout).data,
            'wallet': ContractorWalletSerializer(wallet).data
        })


class RejectJobPayoutView(APIView):
    """Admin rejects job payout"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, eligibility_id):
        eligibility = get_object_or_404(JobPayoutEligibility, id=eligibility_id)
        
        if eligibility.status != 'READY':
            return Response(
                {'error': 'Job is not ready for payout'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rejection_reason = request.data.get('rejection_reason', '')
        
        # Update status
        eligibility.status = 'ON_HOLD'
        eligibility.notes = rejection_reason
        eligibility.save()
        
        # Create notification
        from .models import JobNotification
        JobNotification.objects.create(
            recipient=eligibility.contractor.user,
            job=eligibility.job,
            notification_type='REVISION_REQUIRED',
            title=f'Payout On Hold: {eligibility.job.job_number}',
            message=f'Payout for job {eligibility.job.job_number} has been put on hold. Reason: {rejection_reason}'
        )
        
        return Response({
            'message': 'Payout rejected and put on hold',
            'eligibility': JobPayoutEligibilitySerializer(eligibility).data
        })


class BulkApprovePayoutsView(APIView):
    """Admin approves multiple payouts at once"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request):
        eligibility_ids = request.data.get('eligibility_ids', [])
        
        if not eligibility_ids:
            return Response(
                {'error': 'No eligibility IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        approved_count = 0
        failed_count = 0
        results = []
        
        for eligibility_id in eligibility_ids:
            try:
                eligibility = JobPayoutEligibility.objects.get(id=eligibility_id, status='READY')
                
                # Get or create wallet
                wallet, _ = ContractorWallet.objects.get_or_create(
                    contractor=eligibility.contractor
                )
                
                # Create payout
                payout_number = generate_payout_number(eligibility.job.workspace.workspace_id)
                payout = Payout.objects.create(
                    workspace=eligibility.job.workspace,
                    contractor=eligibility.contractor,
                    job=eligibility.job,
                    payout_number=payout_number,
                    amount=eligibility.amount,
                    status='COMPLETED',
                    payment_method='BANK_TRANSFER',
                    paid_date=timezone.now().date(),
                    processed_by=request.user
                )
                
                # Credit wallet
                wallet.credit(
                    amount=eligibility.amount,
                    description=f'Payment for job {eligibility.job.job_number}'
                )
                
                # Mark as paid
                eligibility.mark_as_paid(payout)
                
                approved_count += 1
                results.append({
                    'eligibility_id': eligibility_id,
                    'status': 'approved',
                    'payout_number': payout_number
                })
                
            except Exception as e:
                failed_count += 1
                results.append({
                    'eligibility_id': eligibility_id,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return Response({
            'message': f'Processed {len(eligibility_ids)} payouts',
            'approved': approved_count,
            'failed': failed_count,
            'results': results
        })


class PayoutStatisticsView(APIView):
    """Admin views payout statistics"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Ready for payout
        ready_jobs = JobPayoutEligibility.objects.filter(status='READY')
        ready_count = ready_jobs.count()
        ready_amount = ready_jobs.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Processing
        processing_jobs = JobPayoutEligibility.objects.filter(status='PROCESSING')
        processing_count = processing_jobs.count()
        processing_amount = processing_jobs.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Paid this month
        this_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0)
        paid_this_month = JobPayoutEligibility.objects.filter(
            status='PAID',
            updated_at__gte=this_month_start
        )
        paid_count = paid_this_month.count()
        paid_amount = paid_this_month.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # On hold
        on_hold_jobs = JobPayoutEligibility.objects.filter(status='ON_HOLD')
        on_hold_count = on_hold_jobs.count()
        on_hold_amount = on_hold_jobs.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Total wallet balances
        total_wallet_balance = ContractorWallet.objects.aggregate(Sum('balance'))['balance__sum'] or 0
        total_pending = ContractorWallet.objects.aggregate(Sum('pending_amount'))['pending_amount__sum'] or 0
        
        return Response({
            'ready_for_payout': {
                'count': ready_count,
                'total_amount': float(ready_amount)
            },
            'processing': {
                'count': processing_count,
                'total_amount': float(processing_amount)
            },
            'paid_this_month': {
                'count': paid_count,
                'total_amount': float(paid_amount)
            },
            'on_hold': {
                'count': on_hold_count,
                'total_amount': float(on_hold_amount)
            },
            'wallet_summary': {
                'total_balance': float(total_wallet_balance),
                'total_pending': float(total_pending)
            }
        })


# ==================== Contractor Wallet ====================

class ContractorWalletView(APIView):
    """Contractor views their wallet"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        contractor = get_object_or_404(Contractor, user=request.user)
        wallet, created = ContractorWallet.objects.get_or_create(contractor=contractor)
        
        return Response(ContractorWalletSerializer(wallet).data)


class WalletTransactionsView(generics.ListAPIView):
    """Contractor views wallet transactions (ledger)"""
    serializer_class = WalletTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        contractor = get_object_or_404(Contractor, user=self.request.user)
        wallet = get_object_or_404(ContractorWallet, contractor=contractor)
        
        queryset = WalletTransaction.objects.filter(wallet=wallet)
        
        # Filter by transaction type
        transaction_type = self.request.query_params.get('transaction_type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type.upper())
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset.order_by('-created_at')


class DownloadWalletLedgerView(APIView):
    """Download wallet ledger as CSV"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        contractor = get_object_or_404(Contractor, user=request.user)
        wallet = get_object_or_404(ContractorWallet, contractor=contractor)
        
        # Get transactions
        transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Date', 'Transaction Type', 'Amount', 'Balance After',
            'Status', 'Description', 'Reference Number'
        ])
        
        # Write data
        for transaction in transactions:
            writer.writerow([
                transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                transaction.get_transaction_type_display(),
                f"${transaction.amount:.2f}",
                f"${transaction.balance_after:.2f}",
                transaction.get_status_display(),
                transaction.description or '',
                transaction.reference_number or ''
            ])
        
        # Create response
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        filename = f'wallet_ledger_{contractor.user.email}_{timezone.now().strftime("%Y%m%d")}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response


class RequestPayoutView(APIView):
    """Contractor requests payout from wallet"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        contractor = get_object_or_404(Contractor, user=request.user)
        wallet = get_object_or_404(ContractorWallet, contractor=contractor)
        
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method')
        
        if not amount or float(amount) <= 0:
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if float(amount) > wallet.balance:
            return Response(
                {'error': 'Insufficient balance'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate request number
        count = PayoutRequest.objects.filter(contractor=contractor).count()
        request_number = f"PR-{contractor.id:05d}-{count + 1:05d}"
        
        # Create payout request
        payout_request = PayoutRequest.objects.create(
            contractor=contractor,
            request_number=request_number,
            amount=amount,
            payment_method=payment_method,
            bank_account_number=request.data.get('bank_account_number'),
            bank_name=request.data.get('bank_name'),
            bank_routing_number=request.data.get('bank_routing_number'),
            paypal_email=request.data.get('paypal_email'),
            notes=request.data.get('notes')
        )
        
        # Add to pending
        wallet.add_pending(float(amount))
        
        return Response({
            'message': 'Payout request submitted successfully',
            'payout_request': PayoutRequestSerializer(payout_request).data
        }, status=status.HTTP_201_CREATED)


class ContractorPayoutRequestsView(generics.ListAPIView):
    """Contractor views their payout requests"""
    serializer_class = PayoutRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        contractor = get_object_or_404(Contractor, user=self.request.user)
        return PayoutRequest.objects.filter(contractor=contractor).order_by('-created_at')


# ==================== Admin Payout Request Management ====================

class AdminPayoutRequestsView(generics.ListAPIView):
    """Admin views all payout requests"""
    serializer_class = PayoutRequestSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        queryset = PayoutRequest.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        
        return queryset.order_by('-created_at')


class ApprovePayoutRequestView(APIView):
    """Admin approves payout request"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, request_id):
        payout_request = get_object_or_404(PayoutRequest, id=request_id)
        
        if payout_request.status != 'PENDING':
            return Response(
                {'error': 'Payout request is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        contractor = payout_request.contractor
        wallet = get_object_or_404(ContractorWallet, contractor=contractor)
        
        # Check balance
        if wallet.balance < payout_request.amount:
            return Response(
                {'error': 'Insufficient wallet balance'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Debit wallet
        if wallet.debit(payout_request.amount, f'Payout request {payout_request.request_number}'):
            # Update payout request
            payout_request.status = 'APPROVED'
            payout_request.reviewed_by = request.user
            payout_request.reviewed_at = timezone.now()
            payout_request.save()
            
            # Clear pending
            wallet.clear_pending(payout_request.amount)
            
            # Create notification
            from .models import JobNotification
            # Note: We need a job reference, using latest job for now
            latest_job = Job.objects.filter(assigned_to=contractor.user).first()
            if latest_job:
                JobNotification.objects.create(
                    recipient=contractor.user,
                    job=latest_job,
                    notification_type='JOB_VERIFIED',
                    title=f'Payout Request Approved',
                    message=f'Your payout request of ${payout_request.amount} has been approved and processed.'
                )
            
            return Response({
                'message': 'Payout request approved successfully',
                'payout_request': PayoutRequestSerializer(payout_request).data
            })
        else:
            return Response(
                {'error': 'Failed to process payout'},
                status=status.HTTP_400_BAD_REQUEST
            )


class RejectPayoutRequestView(APIView):
    """Admin rejects payout request"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, request_id):
        payout_request = get_object_or_404(PayoutRequest, id=request_id)
        
        if payout_request.status != 'PENDING':
            return Response(
                {'error': 'Payout request is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rejection_reason = request.data.get('rejection_reason', '')
        
        # Update payout request
        payout_request.status = 'REJECTED'
        payout_request.reviewed_by = request.user
        payout_request.reviewed_at = timezone.now()
        payout_request.rejection_reason = rejection_reason
        payout_request.save()
        
        # Clear pending
        wallet = get_object_or_404(ContractorWallet, contractor=payout_request.contractor)
        wallet.clear_pending(payout_request.amount)
        
        return Response({
            'message': 'Payout request rejected',
            'payout_request': PayoutRequestSerializer(payout_request).data
        })


# ==================== Reports ====================

class DownloadPayoutReportView(APIView):
    """Download payout report as CSV"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Get date range
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        queryset = JobPayoutEligibility.objects.filter(status='PAID')
        
        if date_from:
            queryset = queryset.filter(updated_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(updated_at__lte=date_to)
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Job Number', 'Job Title', 'Contractor Email', 'Contractor Company',
            'Amount', 'Payout Number', 'Paid Date', 'Status'
        ])
        
        # Write data
        for eligibility in queryset:
            writer.writerow([
                eligibility.job.job_number,
                eligibility.job.title,
                eligibility.contractor.user.email,
                eligibility.contractor.company_name or '',
                f"${eligibility.amount:.2f}",
                eligibility.payout.payout_number if eligibility.payout else '',
                eligibility.payout.paid_date if eligibility.payout else '',
                eligibility.get_status_display()
            ])
        
        # Create response
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        filename = f'payout_report_{timezone.now().strftime("%Y%m%d")}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response


# ==================== Auto-create payout eligibility on job verification ====================

def create_payout_eligibility_on_verification(job_completion):
    """
    Automatically create payout eligibility when job is verified
    This should be called from VerifyJobCompletionView in contractor_views.py
    """
    if job_completion.status == 'APPROVED':
        # Check if eligibility already exists
        if not hasattr(job_completion.job, 'payout_eligibility'):
            # Calculate amount (use actual_cost or estimated_cost)
            amount = job_completion.job.actual_cost or job_completion.job.estimated_cost or 0
            
            if amount > 0:
                JobPayoutEligibility.objects.create(
                    job=job_completion.job,
                    contractor=job_completion.contractor,
                    amount=amount,
                    status='READY'
                )
