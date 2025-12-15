"""
Investor Module Views
Dashboard, Revenue Statistics, ROI Analytics, and Reports
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q, F
from django.http import HttpResponse
from datetime import datetime, timedelta
import csv
import io

from .models import (
    Workspace, Job, Estimate, Payout, ContractorWallet,
    WalletTransaction, JobPayoutEligibility, Contractor
)
from .serializers import (
    JobSerializer, EstimateSerializer, PayoutSerializer
)
from authentication.permissions import IsAdmin


# ==================== Investor Dashboard ====================

class InvestorDashboardView(APIView):
    """Investor dashboard with overall statistics"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Date filters
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Default to last 12 months if no dates provided
        if not date_from:
            date_from = (timezone.now() - timedelta(days=365)).date()
        else:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        
        if not date_to:
            date_to = timezone.now().date()
        else:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        # Filter jobs by date range
        jobs_queryset = Job.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        )
        
        # Total Revenue (from completed jobs)
        total_revenue = jobs_queryset.filter(
            status='COMPLETED'
        ).aggregate(
            total=Sum('actual_cost')
        )['total'] or 0
        
        # Total Payouts
        total_payouts = Payout.objects.filter(
            status='COMPLETED',
            paid_date__gte=date_from,
            paid_date__lte=date_to
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Net Profit
        net_profit = total_revenue - total_payouts
        
        # ROI Calculation
        if total_payouts > 0:
            roi_percentage = ((net_profit / total_payouts) * 100)
        else:
            roi_percentage = 0
        
        # Job Statistics
        total_jobs = jobs_queryset.count()
        completed_jobs = jobs_queryset.filter(status='COMPLETED').count()
        active_jobs = jobs_queryset.filter(status='IN_PROGRESS').count()
        pending_jobs = jobs_queryset.filter(status='PENDING').count()
        
        # Average job value
        avg_job_value = jobs_queryset.filter(
            status='COMPLETED'
        ).aggregate(
            avg=Avg('actual_cost')
        )['avg'] or 0
        
        # Contractor Statistics
        total_contractors = Contractor.objects.filter(status='ACTIVE').count()
        total_contractor_earnings = ContractorWallet.objects.aggregate(
            total=Sum('total_earned')
        )['total'] or 0
        
        # Pending Payouts
        pending_payout_amount = JobPayoutEligibility.objects.filter(
            status='READY'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Monthly Breakdown
        monthly_data = self._get_monthly_breakdown(date_from, date_to)
        
        return Response({
            'date_range': {
                'from': date_from,
                'to': date_to
            },
            'revenue': {
                'total_revenue': float(total_revenue),
                'total_payouts': float(total_payouts),
                'net_profit': float(net_profit),
                'roi_percentage': round(float(roi_percentage), 2),
                'pending_payouts': float(pending_payout_amount)
            },
            'jobs': {
                'total_jobs': total_jobs,
                'completed_jobs': completed_jobs,
                'active_jobs': active_jobs,
                'pending_jobs': pending_jobs,
                'completion_rate': round((completed_jobs / total_jobs * 100) if total_jobs > 0 else 0, 2),
                'average_job_value': float(avg_job_value)
            },
            'contractors': {
                'total_active_contractors': total_contractors,
                'total_contractor_earnings': float(total_contractor_earnings)
            },
            'monthly_breakdown': monthly_data
        })
    
    def _get_monthly_breakdown(self, date_from, date_to):
        """Get monthly revenue and payout breakdown"""
        monthly_data = []
        
        current_date = date_from.replace(day=1)
        end_date = date_to
        
        while current_date <= end_date:
            # Calculate next month
            if current_date.month == 12:
                next_month = current_date.replace(year=current_date.year + 1, month=1)
            else:
                next_month = current_date.replace(month=current_date.month + 1)
            
            # Revenue for this month
            month_revenue = Job.objects.filter(
                status='COMPLETED',
                completed_date__gte=current_date,
                completed_date__lt=next_month
            ).aggregate(
                total=Sum('actual_cost')
            )['total'] or 0
            
            # Payouts for this month
            month_payouts = Payout.objects.filter(
                status='COMPLETED',
                paid_date__gte=current_date,
                paid_date__lt=next_month
            ).aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            # Jobs count
            month_jobs = Job.objects.filter(
                created_at__date__gte=current_date,
                created_at__date__lt=next_month
            ).count()
            
            monthly_data.append({
                'month': current_date.strftime('%Y-%m'),
                'month_name': current_date.strftime('%B %Y'),
                'revenue': float(month_revenue),
                'payouts': float(month_payouts),
                'profit': float(month_revenue - month_payouts),
                'jobs_count': month_jobs
            })
            
            current_date = next_month
        
        return monthly_data


class RevenueStatisticsView(APIView):
    """Detailed revenue statistics"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Revenue by workspace
        workspace_revenue = Job.objects.filter(
            status='COMPLETED'
        ).values(
            'workspace__name',
            'workspace__workspace_id'
        ).annotate(
            total_revenue=Sum('actual_cost'),
            job_count=Count('id'),
            avg_revenue=Avg('actual_cost')
        ).order_by('-total_revenue')
        
        # Revenue by priority
        priority_revenue = Job.objects.filter(
            status='COMPLETED'
        ).values('priority').annotate(
            total_revenue=Sum('actual_cost'),
            job_count=Count('id')
        ).order_by('-total_revenue')
        
        # Top performing contractors
        top_contractors = Contractor.objects.annotate(
            total_earned=Sum('eligible_payouts__amount', filter=Q(eligible_payouts__status='PAID')),
            jobs_completed=Count('eligible_payouts', filter=Q(eligible_payouts__status='PAID'))
        ).filter(
            total_earned__isnull=False
        ).order_by('-total_earned')[:10]
        
        top_contractors_data = [{
            'contractor_email': c.user.email,
            'contractor_company': c.company_name,
            'total_earned': float(c.total_earned or 0),
            'jobs_completed': c.jobs_completed,
            'rating': float(c.rating or 0)
        } for c in top_contractors]
        
        return Response({
            'revenue_by_workspace': list(workspace_revenue),
            'revenue_by_priority': list(priority_revenue),
            'top_contractors': top_contractors_data
        })


class JobVolumeBreakdownView(APIView):
    """Job volume analysis"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Date filters
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if not date_from:
            date_from = (timezone.now() - timedelta(days=365)).date()
        else:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        
        if not date_to:
            date_to = timezone.now().date()
        else:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        jobs_queryset = Job.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        )
        
        # By Status
        by_status = jobs_queryset.values('status').annotate(
            count=Count('id'),
            total_value=Sum('estimated_cost')
        ).order_by('-count')
        
        # By Priority
        by_priority = jobs_queryset.values('priority').annotate(
            count=Count('id'),
            total_value=Sum('estimated_cost')
        ).order_by('-count')
        
        # By Workspace
        by_workspace = jobs_queryset.values(
            'workspace__name',
            'workspace__workspace_id'
        ).annotate(
            count=Count('id'),
            total_value=Sum('estimated_cost')
        ).order_by('-count')
        
        # Average completion time
        completed_jobs = jobs_queryset.filter(
            status='COMPLETED',
            start_date__isnull=False,
            completed_date__isnull=False
        )
        
        avg_completion_days = 0
        if completed_jobs.exists():
            total_days = sum([
                (job.completed_date - job.start_date).days 
                for job in completed_jobs 
                if job.start_date and job.completed_date
            ])
            avg_completion_days = total_days / completed_jobs.count() if completed_jobs.count() > 0 else 0
        
        return Response({
            'date_range': {
                'from': date_from,
                'to': date_to
            },
            'by_status': list(by_status),
            'by_priority': list(by_priority),
            'by_workspace': list(by_workspace),
            'average_completion_days': round(avg_completion_days, 1)
        })


class ROIAnalyticsView(APIView):
    """ROI and profitability analytics"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Date filters
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if not date_from:
            date_from = (timezone.now() - timedelta(days=365)).date()
        else:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        
        if not date_to:
            date_to = timezone.now().date()
        else:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        # Total Investment (Payouts)
        total_investment = Payout.objects.filter(
            status='COMPLETED',
            paid_date__gte=date_from,
            paid_date__lte=date_to
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Total Returns (Revenue)
        total_returns = Job.objects.filter(
            status='COMPLETED',
            completed_date__gte=date_from,
            completed_date__lte=date_to
        ).aggregate(
            total=Sum('actual_cost')
        )['total'] or 0
        
        # Net Profit
        net_profit = total_returns - total_investment
        
        # ROI Percentage
        roi_percentage = ((net_profit / total_investment) * 100) if total_investment > 0 else 0
        
        # Profit Margin
        profit_margin = ((net_profit / total_returns) * 100) if total_returns > 0 else 0
        
        # ROI by Workspace
        workspaces = Workspace.objects.all()
        workspace_roi = []
        
        for workspace in workspaces:
            ws_revenue = Job.objects.filter(
                workspace=workspace,
                status='COMPLETED',
                completed_date__gte=date_from,
                completed_date__lte=date_to
            ).aggregate(
                total=Sum('actual_cost')
            )['total'] or 0
            
            ws_payouts = Payout.objects.filter(
                workspace=workspace,
                status='COMPLETED',
                paid_date__gte=date_from,
                paid_date__lte=date_to
            ).aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            ws_profit = ws_revenue - ws_payouts
            ws_roi = ((ws_profit / ws_payouts) * 100) if ws_payouts > 0 else 0
            
            workspace_roi.append({
                'workspace_name': workspace.name,
                'workspace_id': str(workspace.workspace_id),
                'revenue': float(ws_revenue),
                'investment': float(ws_payouts),
                'profit': float(ws_profit),
                'roi_percentage': round(float(ws_roi), 2)
            })
        
        # Sort by ROI
        workspace_roi.sort(key=lambda x: x['roi_percentage'], reverse=True)
        
        return Response({
            'date_range': {
                'from': date_from,
                'to': date_to
            },
            'overall': {
                'total_investment': float(total_investment),
                'total_returns': float(total_returns),
                'net_profit': float(net_profit),
                'roi_percentage': round(float(roi_percentage), 2),
                'profit_margin': round(float(profit_margin), 2)
            },
            'by_workspace': workspace_roi
        })


class PayoutAnalyticsView(APIView):
    """Payout analytics and trends"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Date filters
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if not date_from:
            date_from = (timezone.now() - timedelta(days=365)).date()
        else:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        
        if not date_to:
            date_to = timezone.now().date()
        else:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        payouts_queryset = Payout.objects.filter(
            paid_date__gte=date_from,
            paid_date__lte=date_to
        )
        
        # Total payouts
        total_payouts = payouts_queryset.filter(status='COMPLETED').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Average payout
        avg_payout = payouts_queryset.filter(status='COMPLETED').aggregate(
            avg=Avg('amount')
        )['avg'] or 0
        
        # Payouts by status
        by_status = payouts_queryset.values('status').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        ).order_by('-total_amount')
        
        # Payouts by payment method
        by_method = payouts_queryset.filter(status='COMPLETED').values('payment_method').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        ).order_by('-total_amount')
        
        # Top contractors by earnings
        top_earners = payouts_queryset.filter(
            status='COMPLETED'
        ).values(
            'contractor__user__email',
            'contractor__company_name'
        ).annotate(
            total_earned=Sum('amount'),
            payout_count=Count('id')
        ).order_by('-total_earned')[:10]
        
        return Response({
            'date_range': {
                'from': date_from,
                'to': date_to
            },
            'summary': {
                'total_payouts': float(total_payouts),
                'average_payout': float(avg_payout),
                'payout_count': payouts_queryset.filter(status='COMPLETED').count()
            },
            'by_status': list(by_status),
            'by_payment_method': list(by_method),
            'top_earners': list(top_earners)
        })


# ==================== Downloadable Reports ====================

class DownloadInvestorReportCSVView(APIView):
    """Download investor report as CSV"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Date filters
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if not date_from:
            date_from = (timezone.now() - timedelta(days=365)).date()
        else:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        
        if not date_to:
            date_to = timezone.now().date()
        else:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['INVESTOR REPORT'])
        writer.writerow([f'Period: {date_from} to {date_to}'])
        writer.writerow([f'Generated: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'])
        writer.writerow([])
        
        # Revenue Summary
        writer.writerow(['REVENUE SUMMARY'])
        writer.writerow(['Metric', 'Value'])
        
        total_revenue = Job.objects.filter(
            status='COMPLETED',
            completed_date__gte=date_from,
            completed_date__lte=date_to
        ).aggregate(total=Sum('actual_cost'))['total'] or 0
        
        total_payouts = Payout.objects.filter(
            status='COMPLETED',
            paid_date__gte=date_from,
            paid_date__lte=date_to
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        net_profit = total_revenue - total_payouts
        roi = ((net_profit / total_payouts) * 100) if total_payouts > 0 else 0
        
        writer.writerow(['Total Revenue', f'${total_revenue:.2f}'])
        writer.writerow(['Total Payouts', f'${total_payouts:.2f}'])
        writer.writerow(['Net Profit', f'${net_profit:.2f}'])
        writer.writerow(['ROI', f'{roi:.2f}%'])
        writer.writerow([])
        
        # Job Statistics
        writer.writerow(['JOB STATISTICS'])
        writer.writerow(['Status', 'Count', 'Total Value'])
        
        job_stats = Job.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        ).values('status').annotate(
            count=Count('id'),
            total_value=Sum('actual_cost')
        )
        
        for stat in job_stats:
            writer.writerow([
                stat['status'],
                stat['count'],
                f"${stat['total_value'] or 0:.2f}"
            ])
        
        writer.writerow([])
        
        # Workspace Performance
        writer.writerow(['WORKSPACE PERFORMANCE'])
        writer.writerow(['Workspace', 'Jobs', 'Revenue', 'Payouts', 'Profit', 'ROI %'])
        
        workspaces = Workspace.objects.all()
        for workspace in workspaces:
            ws_revenue = Job.objects.filter(
                workspace=workspace,
                status='COMPLETED',
                completed_date__gte=date_from,
                completed_date__lte=date_to
            ).aggregate(total=Sum('actual_cost'))['total'] or 0
            
            ws_payouts = Payout.objects.filter(
                workspace=workspace,
                status='COMPLETED',
                paid_date__gte=date_from,
                paid_date__lte=date_to
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            ws_jobs = Job.objects.filter(
                workspace=workspace,
                created_at__date__gte=date_from,
                created_at__date__lte=date_to
            ).count()
            
            ws_profit = ws_revenue - ws_payouts
            ws_roi = ((ws_profit / ws_payouts) * 100) if ws_payouts > 0 else 0
            
            writer.writerow([
                workspace.name,
                ws_jobs,
                f'${ws_revenue:.2f}',
                f'${ws_payouts:.2f}',
                f'${ws_profit:.2f}',
                f'{ws_roi:.2f}%'
            ])
        
        # Create response
        output.seek(0)
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="investor_report_{date_from}_{date_to}.csv"'
        
        return response


class DownloadDetailedJobReportCSVView(APIView):
    """Download detailed job report as CSV"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Date filters
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if not date_from:
            date_from = (timezone.now() - timedelta(days=365)).date()
        else:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        
        if not date_to:
            date_to = timezone.now().date()
        else:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        # Get jobs
        jobs = Job.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        ).select_related('workspace', 'assigned_to', 'created_by')
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Job Number', 'Title', 'Workspace', 'Status', 'Priority',
            'Assigned To', 'Customer Name', 'Estimated Cost', 'Actual Cost',
            'Start Date', 'Due Date', 'Completed Date', 'Created At'
        ])
        
        # Data
        for job in jobs:
            writer.writerow([
                job.job_number,
                job.title,
                job.workspace.name,
                job.status,
                job.priority,
                job.assigned_to.email if job.assigned_to else 'Unassigned',
                job.customer_name or 'N/A',
                f'${job.estimated_cost or 0:.2f}',
                f'${job.actual_cost or 0:.2f}',
                job.start_date or 'N/A',
                job.due_date or 'N/A',
                job.completed_date or 'N/A',
                job.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Create response
        output.seek(0)
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="detailed_jobs_{date_from}_{date_to}.csv"'
        
        return response


class InvestorRecentActivityView(APIView):
    """Recent activity feed for investor"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        limit = int(request.query_params.get('limit', 20))
        
        # Recent completed jobs
        recent_jobs = Job.objects.filter(
            status='COMPLETED'
        ).order_by('-completed_date')[:limit]
        
        # Recent payouts
        recent_payouts = Payout.objects.filter(
            status='COMPLETED'
        ).order_by('-paid_date')[:limit]
        
        # Combine and sort by date
        activities = []
        
        for job in recent_jobs:
            activities.append({
                'type': 'JOB_COMPLETED',
                'date': job.completed_date,
                'description': f'Job {job.job_number} completed',
                'amount': float(job.actual_cost or 0),
                'details': {
                    'job_number': job.job_number,
                    'title': job.title,
                    'workspace': job.workspace.name
                }
            })
        
        for payout in recent_payouts:
            activities.append({
                'type': 'PAYOUT_COMPLETED',
                'date': payout.paid_date,
                'description': f'Payout {payout.payout_number} processed',
                'amount': float(payout.amount),
                'details': {
                    'payout_number': payout.payout_number,
                    'contractor': payout.contractor.user.email,
                    'payment_method': payout.payment_method
                }
            })
        
        # Sort by date
        activities.sort(key=lambda x: x['date'], reverse=True)
        
        return Response({
            'activities': activities[:limit]
        })


# ==================== Enhanced Investor Features ====================

class InvestorActiveWorkOrdersView(APIView):
    """Show all investor-linked jobs with detailed status"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Get all jobs with their current status
        jobs = Job.objects.select_related(
            'workspace', 'assigned_to', 'tracking'
        ).prefetch_related(
            'investor_payouts', 'material_deliveries'
        ).order_by('-created_at')
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            if status_filter == 'OPEN':
                jobs = jobs.filter(status='PENDING')
            elif status_filter == 'IN_PROGRESS':
                jobs = jobs.filter(status='IN_PROGRESS')
            elif status_filter == 'COMPLETED':
                jobs = jobs.filter(status='COMPLETED')
            elif status_filter == 'PENDING_PAYOUT':
                jobs = jobs.filter(
                    status='COMPLETED',
                    payout_eligibility__status='READY'
                )
        
        work_orders = []
        for job in jobs:
            # Calculate investor earnings for this job
            investor_earnings = job.investor_payouts.filter(
                status='COMPLETED'
            ).aggregate(total=Sum('investor_earnings'))['total'] or 0
            
            apex_earnings = job.investor_payouts.filter(
                status='COMPLETED'
            ).aggregate(total=Sum('apex_earnings'))['total'] or 0
            
            # Determine payout status
            payout_status = 'NOT_ELIGIBLE'
            if job.status == 'COMPLETED':
                if hasattr(job, 'payout_eligibility'):
                    payout_status = job.payout_eligibility.status
                else:
                    payout_status = 'PENDING_REVIEW'
            
            work_order = {
                'job_id': job.id,
                'job_number': job.job_number,
                'title': job.title,
                'workspace': job.workspace.name,
                'status': job.status,
                'priority': job.priority,
                'customer_name': job.customer_name,
                'assigned_contractor': job.assigned_to.email if job.assigned_to else None,
                'estimated_cost': float(job.estimated_cost or 0),
                'actual_cost': float(job.actual_cost or 0),
                'start_date': job.start_date,
                'due_date': job.due_date,
                'completed_date': job.completed_date,
                'payout_status': payout_status,
                'investor_earnings': float(investor_earnings),
                'apex_earnings': float(apex_earnings),
                'total_earnings': float(investor_earnings + apex_earnings),
                'created_at': job.created_at,
            }
            
            # Add tracking info if available
            if hasattr(job, 'tracking'):
                work_order['tracking_status'] = job.tracking.status
                work_order['estimated_arrival'] = job.tracking.estimated_arrival
                work_order['actual_arrival'] = job.tracking.actual_arrival
            
            # Add material delivery count
            work_order['material_deliveries_count'] = job.material_deliveries.count()
            work_order['pending_deliveries'] = job.material_deliveries.exclude(
                status='DELIVERED'
            ).count()
            
            work_orders.append(work_order)
        
        # Summary statistics
        summary = {
            'total_jobs': len(work_orders),
            'open_jobs': len([w for w in work_orders if w['status'] == 'PENDING']),
            'in_progress_jobs': len([w for w in work_orders if w['status'] == 'IN_PROGRESS']),
            'completed_jobs': len([w for w in work_orders if w['status'] == 'COMPLETED']),
            'pending_payout_jobs': len([w for w in work_orders if w['payout_status'] == 'READY']),
            'total_value': sum([w['actual_cost'] for w in work_orders if w['actual_cost']]),
            'total_investor_earnings': sum([w['investor_earnings'] for w in work_orders]),
            'total_apex_earnings': sum([w['apex_earnings'] for w in work_orders])
        }
        
        return Response({
            'summary': summary,
            'work_orders': work_orders
        })


class InvestorEarningsBreakdownView(APIView):
    """Detailed earnings breakdown for investors"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Date filters
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if not date_from:
            date_from = (timezone.now() - timedelta(days=365)).date()
        else:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        
        if not date_to:
            date_to = timezone.now().date()
        else:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        # Get all investor payouts in the period
        investor_payouts = InvestorPayout.objects.filter(
            payout_date__gte=date_from,
            payout_date__lte=date_to,
            status='COMPLETED'
        ).select_related('investor', 'job', 'property_investment')
        
        # Calculate totals
        total_apex_earnings = investor_payouts.aggregate(
            total=Sum('apex_earnings')
        )['total'] or 0
        
        total_investor_earnings = investor_payouts.aggregate(
            total=Sum('investor_earnings')
        )['total'] or 0
        
        total_revenue = total_apex_earnings + total_investor_earnings
        
        # Profit splits by investor
        investor_breakdown = {}
        for payout in investor_payouts:
            investor_email = payout.investor.user.email
            if investor_email not in investor_breakdown:
                investor_breakdown[investor_email] = {
                    'investor_email': investor_email,
                    'total_earnings': 0,
                    'apex_share': 0,
                    'investor_share': 0,
                    'jobs_count': 0,
                    'average_split': 0,
                    'roi_percentage': 0
                }
            
            investor_breakdown[investor_email]['total_earnings'] += float(payout.amount)
            investor_breakdown[investor_email]['apex_share'] += float(payout.apex_earnings)
            investor_breakdown[investor_email]['investor_share'] += float(payout.investor_earnings)
            investor_breakdown[investor_email]['jobs_count'] += 1
        
        # Calculate averages and ROI
        for investor_email, data in investor_breakdown.items():
            if data['jobs_count'] > 0:
                data['average_split'] = (data['investor_share'] / data['total_earnings']) * 100
            
            # Get investor profile for ROI calculation
            try:
                investor_profile = InvestorProfile.objects.get(user__email=investor_email)
                if investor_profile.investment_amount > 0:
                    data['roi_percentage'] = (data['investor_share'] / float(investor_profile.investment_amount)) * 100
            except InvestorProfile.DoesNotExist:
                pass
        
        # ROI per job analysis
        job_roi_analysis = []
        for payout in investor_payouts:
            if payout.job:
                job_roi = {
                    'job_number': payout.job.job_number,
                    'job_title': payout.job.title,
                    'total_revenue': float(payout.amount),
                    'apex_earnings': float(payout.apex_earnings),
                    'investor_earnings': float(payout.investor_earnings),
                    'profit_split': float(payout.profit_split_percentage),
                    'roi_percentage': (float(payout.investor_earnings) / float(payout.amount)) * 100 if payout.amount > 0 else 0,
                    'payout_date': payout.payout_date
                }
                job_roi_analysis.append(job_roi)
        
        # Sort by ROI
        job_roi_analysis.sort(key=lambda x: x['roi_percentage'], reverse=True)
        
        return Response({
            'date_range': {
                'from': date_from,
                'to': date_to
            },
            'summary': {
                'total_revenue': float(total_revenue),
                'total_apex_earnings': float(total_apex_earnings),
                'total_investor_earnings': float(total_investor_earnings),
                'apex_percentage': (float(total_apex_earnings) / float(total_revenue)) * 100 if total_revenue > 0 else 0,
                'investor_percentage': (float(total_investor_earnings) / float(total_revenue)) * 100 if total_revenue > 0 else 0,
                'total_payouts': investor_payouts.count()
            },
            'investor_breakdown': list(investor_breakdown.values()),
            'job_roi_analysis': job_roi_analysis[:20]  # Top 20 jobs by ROI
        })


class InvestorJobCategoriesView(APIView):
    """Job categories with filtering tabs"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        category = request.query_params.get('category', 'active')
        
        base_queryset = Job.objects.select_related('workspace', 'assigned_to')
        
        if category == 'active':
            jobs = base_queryset.filter(status__in=['PENDING', 'IN_PROGRESS'])
        elif category == 'closed':
            jobs = base_queryset.filter(status='COMPLETED')
        elif category == 'pending_payouts':
            jobs = base_queryset.filter(
                status='COMPLETED',
                payout_eligibility__status='READY'
            )
        elif category == 'payout_history':
            jobs = base_queryset.filter(
                status='COMPLETED',
                payout_eligibility__status='PAID'
            )
        else:
            jobs = base_queryset.all()
        
        # Paginate results
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = jobs.count()
        jobs_page = jobs[start:end]
        
        # Format job data
        jobs_data = []
        for job in jobs_page:
            # Get payout information
            payout_info = None
            if hasattr(job, 'payout_eligibility'):
                payout_info = {
                    'status': job.payout_eligibility.status,
                    'amount': float(job.payout_eligibility.amount),
                    'verified_at': job.payout_eligibility.verified_at
                }
            
            # Get investor earnings
            investor_earnings = job.investor_payouts.filter(
                status='COMPLETED'
            ).aggregate(total=Sum('investor_earnings'))['total'] or 0
            
            job_data = {
                'job_id': job.id,
                'job_number': job.job_number,
                'title': job.title,
                'workspace': job.workspace.name,
                'status': job.status,
                'priority': job.priority,
                'customer_name': job.customer_name,
                'assigned_contractor': job.assigned_to.email if job.assigned_to else None,
                'estimated_cost': float(job.estimated_cost or 0),
                'actual_cost': float(job.actual_cost or 0),
                'investor_earnings': float(investor_earnings),
                'start_date': job.start_date,
                'due_date': job.due_date,
                'completed_date': job.completed_date,
                'created_at': job.created_at,
                'payout_info': payout_info
            }
            jobs_data.append(job_data)
        
        # Category counts
        category_counts = {
            'active': Job.objects.filter(status__in=['PENDING', 'IN_PROGRESS']).count(),
            'closed': Job.objects.filter(status='COMPLETED').count(),
            'pending_payouts': Job.objects.filter(
                status='COMPLETED',
                payout_eligibility__status='READY'
            ).count(),
            'payout_history': Job.objects.filter(
                status='COMPLETED',
                payout_eligibility__status='PAID'
            ).count()
        }
        
        return Response({
            'category': category,
            'category_counts': category_counts,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            },
            'jobs': jobs_data
        })


class InvestorPropertyPerformanceView(APIView):
    """Property-level performance information"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        # Get all property investments
        properties = PropertyInvestment.objects.select_related('investor').all()
        
        property_performance = []
        for prop in properties:
            # Get jobs for this property (assuming property_name matches location or address)
            property_jobs = Job.objects.filter(
                Q(location__icontains=prop.property_name) |
                Q(customer_address__icontains=prop.property_address)
            )
            
            # Active jobs
            active_jobs = property_jobs.filter(status__in=['PENDING', 'IN_PROGRESS'])
            
            # Calculate revenue and profit
            total_revenue = property_jobs.filter(status='COMPLETED').aggregate(
                total=Sum('actual_cost')
            )['total'] or 0
            
            # Get payouts for this property
            property_payouts = InvestorPayout.objects.filter(
                property_investment=prop,
                status='COMPLETED'
            )
            
            total_profit = property_payouts.aggregate(
                total=Sum('investor_earnings')
            )['total'] or 0
            
            # Issues flagged (disputes related to property jobs)
            issues_flagged = 0
            for job in property_jobs:
                issues_flagged += job.disputes.count()
            
            # ROI calculation
            roi_percentage = 0
            if prop.investment_amount > 0:
                roi_percentage = (float(total_profit) / float(prop.investment_amount)) * 100
            
            property_data = {
                'property_id': prop.id,
                'property_name': prop.property_name,
                'property_address': prop.property_address,
                'investor_email': prop.investor.user.email,
                'investment_amount': float(prop.investment_amount),
                'active_jobs': active_jobs.count(),
                'total_jobs': property_jobs.count(),
                'completed_jobs': property_jobs.filter(status='COMPLETED').count(),
                'total_revenue': float(total_revenue),
                'total_profit': float(total_profit),
                'roi_percentage': round(roi_percentage, 2),
                'issues_flagged': issues_flagged,
                'last_job_date': property_jobs.order_by('-created_at').first().created_at if property_jobs.exists() else None
            }
            
            # Recent activity
            recent_jobs = property_jobs.order_by('-created_at')[:5]
            property_data['recent_jobs'] = [{
                'job_number': job.job_number,
                'title': job.title,
                'status': job.status,
                'created_at': job.created_at
            } for job in recent_jobs]
            
            property_performance.append(property_data)
        
        # Sort by ROI
        property_performance.sort(key=lambda x: x['roi_percentage'], reverse=True)
        
        # Summary statistics
        summary = {
            'total_properties': len(property_performance),
            'total_investment': sum([p['investment_amount'] for p in property_performance]),
            'total_revenue': sum([p['total_revenue'] for p in property_performance]),
            'total_profit': sum([p['total_profit'] for p in property_performance]),
            'average_roi': sum([p['roi_percentage'] for p in property_performance]) / len(property_performance) if property_performance else 0,
            'total_active_jobs': sum([p['active_jobs'] for p in property_performance]),
            'total_issues': sum([p['issues_flagged'] for p in property_performance])
        }
        
        return Response({
            'summary': summary,
            'properties': property_performance
        })
