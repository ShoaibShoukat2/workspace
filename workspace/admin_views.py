"""
Admin Dashboard Backend API Views
Complete admin dashboard functionality matching frontend requirements
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from django.db.models.functions import TruncMonth, TruncWeek
from datetime import datetime, timedelta
import json
from django.contrib.auth import get_user_model

from .models import (
    Job, Contractor, CustomerProfile, Dispute, ContractorWallet,
    PayoutRequest, ComplianceData, Workspace, JobNotification,
    JobCompletion, Estimate, Lead, MaterialReference, InvestorProfile
)

User = get_user_model()
from .serializers import (
    JobSerializer, ContractorSerializer, DisputeSerializer,
    PayoutRequestSerializer, ComplianceDataSerializer, LeadSerializer
)
from authentication.permissions import IsAdmin


# ==================== Admin Dashboard Overview ====================

class AdminDashboardOverviewView(APIView):
    """Main admin dashboard with comprehensive statistics"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Get date range for filtering
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        # Core Statistics
        total_jobs = Job.objects.count()
        active_jobs = Job.objects.filter(status__in=['PENDING', 'IN_PROGRESS']).count()
        completed_jobs = Job.objects.filter(status='COMPLETED').count()
        
        # Dispute Statistics
        pending_disputes = Dispute.objects.filter(status='OPEN').count()
        total_disputes = Dispute.objects.count()
        
        # Payout Statistics
        pending_payouts = PayoutRequest.objects.filter(status='PENDING').count()
        total_pending_amount = PayoutRequest.objects.filter(
            status='PENDING'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Contractor Statistics
        active_contractors = Contractor.objects.filter(status='ACTIVE').count()
        blocked_contractors = Contractor.objects.filter(
            compliance_status='BLOCKED'
        ).count()
        
        # Lead Statistics
        active_leads = Lead.objects.filter(status='NEW').count()
        total_leads = Lead.objects.count()
        
        # Meeting Statistics (mock data - would come from meeting model)
        scheduled_meetings = 3  # This would be from a Meeting model
        
        # Revenue Analytics
        revenue_data = self._get_revenue_data(date_from)
        
        # Job Status Distribution
        job_stats = self._get_job_status_distribution()
        
        # Recent Activity
        recent_activity = self._get_recent_activity()
        
        # Active Investors (mock data)
        active_investors = User.objects.filter(role='INVESTOR').count()
        
        return Response({
            'summary': {
                'pending_disputes': pending_disputes,
                'total_disputes': total_disputes,
                'pending_payouts': pending_payouts,
                'total_pending_amount': float(total_pending_amount),
                'blocked_contractors': blocked_contractors,
                'active_contractors': active_contractors,
                'active_jobs': active_jobs,
                'total_jobs': total_jobs,
                'completed_jobs': completed_jobs,
                'scheduled_meetings': scheduled_meetings,
                'active_leads': active_leads,
                'total_leads': total_leads,
                'active_investors': active_investors
            },
            'charts': {
                'revenue_data': revenue_data,
                'job_status_distribution': job_stats
            },
            'recent_activity': recent_activity
        })
    
    def _get_revenue_data(self, date_from):
        """Generate revenue data for charts"""
        # This would typically come from actual revenue tracking
        # For now, generating mock data based on completed jobs
        revenue_by_month = []
        current_date = date_from
        
        while current_date <= timezone.now():
            month_jobs = Job.objects.filter(
                status='COMPLETED',
                completed_at__year=current_date.year,
                completed_at__month=current_date.month
            ).count()
            
            # Estimate revenue (mock calculation)
            estimated_revenue = month_jobs * 5000  # Average job value
            
            revenue_by_month.append({
                'name': current_date.strftime('%b'),
                'value': estimated_revenue
            })
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return revenue_by_month
    
    def _get_job_status_distribution(self):
        """Get job status distribution for charts"""
        statuses = ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'PAID']
        distribution = []
        
        for status in statuses:
            count = Job.objects.filter(status=status).count()
            distribution.append({
                'name': status.replace('_', ' ').title(),
                'count': count
            })
        
        return distribution
    
    def _get_recent_activity(self):
        """Get recent system activity"""
        activities = []
        
        # Recent jobs
        recent_jobs = Job.objects.order_by('-created_at')[:5]
        for job in recent_jobs:
            activities.append({
                'type': 'job_created',
                'title': f'New Job: {job.title}',
                'description': f'Job #{job.id} created',
                'timestamp': job.created_at,
                'user': job.created_by.email if job.created_by else 'System'
            })
        
        # Recent disputes
        recent_disputes = Dispute.objects.order_by('-created_at')[:3]
        for dispute in recent_disputes:
            activities.append({
                'type': 'dispute_created',
                'title': f'New Dispute: {dispute.title}',
                'description': f'Dispute #{dispute.id} opened',
                'timestamp': dispute.created_at,
                'user': dispute.raised_by.email
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return activities[:10]


# ==================== Admin Job Management ====================

class AdminJobListView(generics.ListAPIView):
    """Admin job list with advanced filtering"""
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        queryset = Job.objects.all().select_related(
            'assigned_to', 'workspace', 'created_by'
        ).order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            if status_filter.lower() == 'active':
                queryset = queryset.filter(status__in=['PENDING', 'IN_PROGRESS'])
            else:
                queryset = queryset.filter(status=status_filter.upper())
        
        # Filter by contractor
        contractor_id = self.request.query_params.get('contractor_id')
        if contractor_id:
            queryset = queryset.filter(assigned_to__contractor_profiles__id=contractor_id)
        
        # Filter by customer
        customer_email = self.request.query_params.get('customer_email')
        if customer_email:
            queryset = queryset.filter(customer_email__icontains=customer_email)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(property_address__icontains=search) |
                Q(customer_name__icontains=search)
            )
        
        return queryset


class AdminJobDetailView(generics.RetrieveUpdateAPIView):
    """Admin job detail with full management capabilities"""
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = Job.objects.all()
    
    def get_object(self):
        job = super().get_object()
        
        # Add additional context data
        job.dispute_count = Dispute.objects.filter(job=job).count()
        job.has_open_disputes = Dispute.objects.filter(
            job=job, status='OPEN'
        ).exists()
        
        return job


# ==================== Admin Lead Management ====================

class AdminLeadListView(generics.ListAPIView):
    """Admin lead pipeline management"""
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        queryset = Lead.objects.all().order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        
        # Filter by source
        source_filter = self.request.query_params.get('source')
        if source_filter:
            queryset = queryset.filter(source=source_filter.upper())
        
        return queryset


class AdminLeadDetailView(generics.RetrieveUpdateAPIView):
    """Admin lead detail management"""
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = Lead.objects.all()


class AdminLeadCreateView(generics.CreateAPIView):
    """Admin create manual lead"""
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def perform_create(self, serializer):
        serializer.save(
            source='MANUAL',
            created_by=self.request.user
        )


class AdminLeadStatsView(APIView):
    """Admin lead statistics"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        total_leads = Lead.objects.count()
        new_leads = Lead.objects.filter(status='NEW').count()
        contacted_leads = Lead.objects.filter(status='CONTACTED').count()
        won_leads = Lead.objects.filter(status='WON').count()
        
        # Lead sources
        source_breakdown = Lead.objects.values('source').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Conversion rate
        conversion_rate = (won_leads / total_leads * 100) if total_leads > 0 else 0
        
        return Response({
            'summary': {
                'total_leads': total_leads,
                'new_leads': new_leads,
                'contacted_leads': contacted_leads,
                'won_leads': won_leads,
                'conversion_rate': round(conversion_rate, 2)
            },
            'source_breakdown': list(source_breakdown)
        })


# ==================== Admin Meeting Management ====================

class AdminMeetingListView(APIView):
    """Admin meeting management (mock implementation)"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Mock meeting data - in real implementation, this would use a Meeting model
        meetings = [
            {
                'id': 1,
                'title': 'Site Walkthrough - 123 Main St',
                'date': '2025-12-20',
                'time': '10:00',
                'with': 'John Doe (Customer)',
                'type': 'SITE_VISIT',
                'status': 'SCHEDULED'
            },
            {
                'id': 2,
                'title': 'Compliance Review',
                'date': '2025-12-21',
                'time': '14:00',
                'with': 'Mike Smith (Contractor)',
                'type': 'COMPLIANCE',
                'status': 'SCHEDULED'
            },
            {
                'id': 3,
                'title': 'Investor Monthly Sync',
                'date': '2025-12-22',
                'time': '11:00',
                'with': 'Sarah Connor (Investor)',
                'type': 'INVESTOR_SYNC',
                'status': 'SCHEDULED'
            }
        ]
        
        return Response({
            'meetings': meetings,
            'summary': {
                'total_meetings': len(meetings),
                'today_meetings': 1,
                'this_week_meetings': 3
            }
        })
    
    def post(self, request):
        """Create new meeting"""
        # Mock implementation - would save to Meeting model
        meeting_data = {
            'id': 4,
            'title': request.data.get('title'),
            'date': request.data.get('date'),
            'time': request.data.get('time'),
            'with': request.data.get('with'),
            'type': request.data.get('type', 'GENERAL'),
            'status': 'SCHEDULED'
        }
        
        return Response({
            'message': 'Meeting scheduled successfully',
            'meeting': meeting_data
        }, status=status.HTTP_201_CREATED)


# ==================== Admin Investor Accounting ====================

class AdminInvestorAccountingView(APIView):
    """Admin investor accounting dashboard"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Get all jobs for investor calculations
        investor_jobs = Job.objects.all()
        
        # Calculate metrics
        total_investor_jobs = investor_jobs.count()
        completed_investor_jobs = investor_jobs.filter(status='COMPLETED').count()
        
        # Revenue calculation (mock - would use actual revenue tracking)
        total_revenue = completed_investor_jobs * 5000  # Average job value
        
        # Cost calculation
        total_contractor_costs = PayoutRequest.objects.filter(
            contractor__user__job_set__in=investor_jobs,
            status='APPROVED'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_material_costs = MaterialReference.objects.filter(
            job__in=investor_jobs
        ).aggregate(Sum('price_high'))['price_high__sum'] or 0
        
        total_costs = total_contractor_costs + total_material_costs
        net_profit = total_revenue - total_costs
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Job breakdown
        job_breakdown = []
        for job in investor_jobs:
            estimated_revenue = 5000  # Mock calculation
            job_breakdown.append({
                'job_id': job.id,
                'job_number': getattr(job, 'job_number', f'JOB-{job.id}'),
                'property_address': job.property_address,
                'status': job.status,
                'estimated_revenue': estimated_revenue,
                'actual_cost': getattr(job, 'actual_cost', 0),
                'profit': estimated_revenue - getattr(job, 'actual_cost', 0)
            })
        
        return Response({
            'summary': {
                'total_investor_jobs': total_investor_jobs,
                'completed_jobs': completed_investor_jobs,
                'total_revenue': float(total_revenue),
                'total_costs': float(total_costs),
                'net_profit': float(net_profit),
                'profit_margin': round(profit_margin, 2)
            },
            'cost_breakdown': {
                'contractor_costs': float(total_contractor_costs),
                'material_costs': float(total_material_costs)
            },
            'job_breakdown': job_breakdown
        })


# ==================== Admin Ledger Management ====================

class AdminLedgerView(APIView):
    """Complete accounting ledger for admin"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Get all financial transactions
        transactions = []
        
        # Contractor payouts
        payouts = PayoutRequest.objects.filter(
            status='APPROVED'
        ).select_related('contractor__user').order_by('-created_at')
        
        for payout in payouts:
            transactions.append({
                'id': f'payout-{payout.id}',
                'date': payout.created_at,
                'type': 'CONTRACTOR_PAYOUT',
                'description': f'Contractor Payment - {payout.contractor.user.email}',
                'amount': -float(payout.amount),  # Negative for expense
                'status': payout.status,
                'reference': f'PR-{payout.id}'
            })
        
        # Material references
        material_references = MaterialReference.objects.all().order_by('-created_at')
        for reference in material_references:
            transactions.append({
                'id': f'material-{reference.id}',
                'date': reference.created_at,
                'type': 'MATERIAL_REFERENCE',
                'description': f'Material Reference - {reference.item_name}',
                'amount': -float(reference.price_high or reference.price_low or 0),  # Negative for expense
                'status': 'ACTIVE',
                'reference': f'MR-{reference.id}'
            })
        
        # Sort by date
        transactions.sort(key=lambda x: x['date'], reverse=True)
        
        # Calculate totals
        total_payouts = sum([t['amount'] for t in transactions if t['type'] == 'CONTRACTOR_PAYOUT'])
        total_materials = sum([t['amount'] for t in transactions if t['type'] == 'MATERIAL_PURCHASE'])
        total_expenses = total_payouts + total_materials
        
        return Response({
            'summary': {
                'total_contractor_payouts': abs(total_payouts),
                'total_material_costs': abs(total_materials),
                'total_expenses': abs(total_expenses),
                'transaction_count': len(transactions)
            },
            'transactions': transactions[:100]  # Limit to recent 100
        })


# ==================== Admin Project Management ====================

# ==================== Enhanced Compliance Management ====================

class AdminComplianceOverviewView(APIView):
    """Enhanced compliance overview for admin"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Get all contractors with compliance status
        contractors = Contractor.objects.all().select_related('user')
        
        contractor_compliance = []
        for contractor in contractors:
            # Get compliance documents
            compliance_docs = ComplianceData.objects.filter(contractor=contractor)
            
            # Check compliance status
            has_w9 = compliance_docs.filter(
                compliance_type='W9_FORM', status='APPROVED'
            ).exists()
            has_insurance = compliance_docs.filter(
                compliance_type='INSURANCE_CERTIFICATE', status='APPROVED'
            ).exists()
            has_agreement = compliance_docs.filter(
                compliance_type='CONTRACTOR_AGREEMENT', status='APPROVED'
            ).exists()
            
            # Check insurance expiry
            insurance_expiry = None
            insurance_doc = compliance_docs.filter(
                compliance_type='INSURANCE_CERTIFICATE', status='APPROVED'
            ).first()
            if insurance_doc and insurance_doc.expiry_date:
                insurance_expiry = insurance_doc.expiry_date
            
            contractor_compliance.append({
                'contractor_id': contractor.id,
                'contractor_name': f"{contractor.user.first_name} {contractor.user.last_name}",
                'contractor_email': contractor.user.email,
                'company_name': getattr(contractor, 'company_name', ''),
                'trade': getattr(contractor, 'trade', ''),
                'compliance_status': getattr(contractor, 'compliance_status', 'PENDING'),
                'has_w9': has_w9,
                'has_insurance': has_insurance,
                'has_agreement': has_agreement,
                'insurance_expiry': insurance_expiry,
                'is_compliant': has_w9 and has_insurance and has_agreement,
                'documents_count': compliance_docs.count()
            })
        
        # Summary statistics
        total_contractors = len(contractor_compliance)
        compliant_contractors = len([c for c in contractor_compliance if c['is_compliant']])
        blocked_contractors = len([c for c in contractor_compliance if c['compliance_status'] == 'BLOCKED'])
        
        # Expiring insurance
        expiring_soon = len([
            c for c in contractor_compliance 
            if c['insurance_expiry'] and c['insurance_expiry'] <= timezone.now().date() + timedelta(days=30)
        ])
        
        return Response({
            'summary': {
                'total_contractors': total_contractors,
                'compliant_contractors': compliant_contractors,
                'blocked_contractors': blocked_contractors,
                'expiring_soon': expiring_soon
            },
            'contractors': contractor_compliance
        })


class AdminContractorComplianceActionView(APIView):
    """Admin actions on contractor compliance"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, contractor_id):
        contractor = get_object_or_404(Contractor, id=contractor_id)
        action = request.data.get('action')
        
        if action == 'approve':
            contractor.compliance_status = 'ACTIVE'
            contractor.save()
            
            # Create notification
            JobNotification.objects.create(
                recipient=contractor.user,
                notification_type='COMPLIANCE_APPROVED',
                title='Compliance Approved',
                message='Your compliance status has been approved. You can now accept job assignments.'
            )
            
            return Response({'message': 'Contractor approved successfully'})
        
        elif action == 'block':
            reason = request.data.get('reason', 'Compliance issues')
            contractor.compliance_status = 'BLOCKED'
            contractor.save()
            
            # Create notification
            JobNotification.objects.create(
                recipient=contractor.user,
                notification_type='COMPLIANCE_BLOCKED',
                title='Compliance Blocked',
                message=f'Your compliance status has been blocked. Reason: {reason}'
            )
            
            return Response({'message': 'Contractor blocked successfully'})
        
        else:
            return Response(
                {'error': 'Invalid action'},
                status=status.HTTP_400_BAD_REQUEST
            )