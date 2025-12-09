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
