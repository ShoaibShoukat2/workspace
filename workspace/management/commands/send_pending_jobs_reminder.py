"""
Pending Jobs Reminder
Sends reminders for pending jobs to FM and Admin
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from workspace.models import Job, JobNotification
from authentication.models import User
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Send reminders for pending jobs'
    
    def handle(self, *args, **options):
        self.stdout.write('Starting pending jobs reminder...')
        
        today = timezone.now().date()
        
        # Find pending jobs without assignment
        unassigned_jobs = Job.objects.filter(
            status='PENDING',
            assigned_to__isnull=True
        )
        
        # Find pending jobs approaching due date (within 7 days)
        approaching_due = Job.objects.filter(
            status='PENDING',
            due_date__lte=today + timedelta(days=7),
            due_date__gte=today
        )
        
        # Find overdue pending jobs
        overdue_jobs = Job.objects.filter(
            status='PENDING',
            due_date__lt=today
        )
        
        # Get all FMs and Admins
        fm_users = User.objects.filter(role='FM', is_active=True)
        admin_users = User.objects.filter(role='ADMIN', is_active=True)
        recipients = list(fm_users) + list(admin_users)
        
        if not recipients:
            self.stdout.write(self.style.WARNING('No FM or Admin users found'))
            return
        
        # Prepare summary
        summary_lines = []
        
        if unassigned_jobs.exists():
            summary_lines.append(f'\n📋 UNASSIGNED JOBS: {unassigned_jobs.count()}')
            for job in unassigned_jobs[:5]:  # Top 5
                summary_lines.append(f'  • {job.job_number}: {job.title}')
            if unassigned_jobs.count() > 5:
                summary_lines.append(f'  ... and {unassigned_jobs.count() - 5} more')
        
        if approaching_due.exists():
            summary_lines.append(f'\n⏰ APPROACHING DUE DATE: {approaching_due.count()}')
            for job in approaching_due[:5]:
                days_left = (job.due_date - today).days
                summary_lines.append(f'  • {job.job_number}: {job.title} (Due in {days_left} days)')
            if approaching_due.count() > 5:
                summary_lines.append(f'  ... and {approaching_due.count() - 5} more')
        
        if overdue_jobs.exists():
            summary_lines.append(f'\n🚨 OVERDUE JOBS: {overdue_jobs.count()}')
            for job in overdue_jobs[:5]:
                days_overdue = (today - job.due_date).days
                summary_lines.append(f'  • {job.job_number}: {job.title} ({days_overdue} days overdue)')
            if overdue_jobs.count() > 5:
                summary_lines.append(f'  ... and {overdue_jobs.count() - 5} more')
        
        if not summary_lines:
            self.stdout.write(self.style.SUCCESS('No pending jobs requiring attention'))
            return
        
        # Send notifications and emails
        notification_count = 0
        email_count = 0
        
        for user in recipients:
            # Create notification
            JobNotification.objects.create(
                recipient=user,
                job=unassigned_jobs.first() if unassigned_jobs.exists() else None,
                notification_type='REVISION_REQUIRED',
                title='Pending Jobs Reminder',
                message=f'You have {unassigned_jobs.count()} unassigned jobs, {approaching_due.count()} jobs approaching due date, and {overdue_jobs.count()} overdue jobs.'
            )
            notification_count += 1
            
            # Send email
            try:
                email_body = f"""
Hello {user.username},

This is your daily reminder for pending jobs:

{''.join(summary_lines)}

Please review and take necessary action.

Best regards,
Job Management System
                """
                
                send_mail(
                    subject='Daily Pending Jobs Reminder',
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
                f'Reminders sent: {notification_count} notifications, {email_count} emails'
            )
        )
