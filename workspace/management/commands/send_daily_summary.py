"""
Daily Summary Email
Sends daily summary to FM and Admin with key metrics
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from workspace.models import Job, Estimate, Payout, JobCompletion
from authentication.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum, Count


class Command(BaseCommand):
    help = 'Send daily summary email to FM and Admin'
    
    def handle(self, *args, **options):
        self.stdout.write('Generating daily summary...')
        
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Get all FMs and Admins
        fm_users = User.objects.filter(role='FM', is_active=True)
        admin_users = User.objects.filter(role='ADMIN', is_active=True)
        recipients = list(fm_users) + list(admin_users)
        
        if not recipients:
            self.stdout.write(self.style.WARNING('No FM or Admin users found'))
            return
        
        # Calculate metrics
        
        # Jobs created yesterday
        new_jobs = Job.objects.filter(created_at__date=yesterday).count()
        
        # Jobs completed yesterday
        completed_jobs = Job.objects.filter(
            status='COMPLETED',
            completed_date=yesterday
        ).count()
        
        # Current status
        total_jobs = Job.objects.count()
        pending_jobs = Job.objects.filter(status='PENDING').count()
        active_jobs = Job.objects.filter(status='IN_PROGRESS').count()
        
        # Estimates
        new_estimates = Estimate.objects.filter(created_at__date=yesterday).count()
        pending_estimates = Estimate.objects.filter(status='DRAFT').count()
        
        # Payouts
        payouts_yesterday = Payout.objects.filter(
            paid_date=yesterday,
            status='COMPLETED'
        )
        payout_count = payouts_yesterday.count()
        payout_amount = payouts_yesterday.aggregate(total=Sum('amount'))['total'] or 0
        
        # Pending approvals
        pending_completions = JobCompletion.objects.filter(
            status='SUBMITTED'
        ).count()
        
        # Revenue yesterday
        revenue_yesterday = Job.objects.filter(
            status='COMPLETED',
            completed_date=yesterday
        ).aggregate(total=Sum('actual_cost'))['total'] or 0
        
        # Prepare email body
        email_body = f"""
Daily Summary Report - {today.strftime('%B %d, %Y')}
{'=' * 50}

📊 YESTERDAY'S ACTIVITY ({yesterday.strftime('%B %d, %Y')}):
  • New Jobs Created: {new_jobs}
  • Jobs Completed: {completed_jobs}
  • New Estimates: {new_estimates}
  • Payouts Processed: {payout_count} (${payout_amount:,.2f})
  • Revenue Generated: ${revenue_yesterday:,.2f}

📈 CURRENT STATUS:
  • Total Jobs: {total_jobs}
  • Pending Jobs: {pending_jobs}
  • Active Jobs: {active_jobs}
  • Pending Estimates: {pending_estimates}
  • Pending Completions: {pending_completions}

⚠️ REQUIRES ATTENTION:
"""
        
        # Add items requiring attention
        attention_items = []
        
        # Unassigned jobs
        unassigned = Job.objects.filter(status='PENDING', assigned_to__isnull=True).count()
        if unassigned > 0:
            attention_items.append(f'  • {unassigned} unassigned jobs')
        
        # Overdue jobs
        overdue = Job.objects.filter(status__in=['PENDING', 'IN_PROGRESS'], due_date__lt=today).count()
        if overdue > 0:
            attention_items.append(f'  • {overdue} overdue jobs')
        
        # Pending completions
        if pending_completions > 0:
            attention_items.append(f'  • {pending_completions} job completions awaiting verification')
        
        # Pending estimates
        if pending_estimates > 5:
            attention_items.append(f'  • {pending_estimates} draft estimates need review')
        
        if attention_items:
            email_body += '\n'.join(attention_items)
        else:
            email_body += '  ✅ No items requiring immediate attention'
        
        email_body += f"""

{'=' * 50}
This is an automated daily summary.
Login to the system for detailed information.

Best regards,
Job Management System
        """
        
        # Send emails
        email_count = 0
        for user in recipients:
            try:
                send_mail(
                    subject=f'Daily Summary - {today.strftime("%B %d, %Y")}',
                    message=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
                email_count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Failed to send email to {user.email}: {str(e)}'))
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Daily summary sent to {email_count} recipients'
            )
        )
