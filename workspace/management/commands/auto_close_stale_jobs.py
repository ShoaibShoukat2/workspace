"""
Auto Close Stale Jobs
Automatically closes jobs that have been inactive for too long
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from workspace.models import Job, JobNotification
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Automatically close stale jobs'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Number of days of inactivity before closing (default: 90)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be closed without actually closing'
        )
    
    def handle(self, *args, **options):
        days_threshold = options['days']
        dry_run = options['dry_run']
        
        self.stdout.write(f'Checking for stale jobs (inactive for {days_threshold}+ days)...')
        
        threshold_date = timezone.now() - timedelta(days=days_threshold)
        
        # Find stale jobs
        # Jobs that are PENDING or IN_PROGRESS and haven't been updated in X days
        stale_jobs = Job.objects.filter(
            status__in=['PENDING', 'IN_PROGRESS'],
            updated_at__lt=threshold_date
        )
        
        if not stale_jobs.exists():
            self.stdout.write(self.style.SUCCESS('No stale jobs found'))
            return
        
        self.stdout.write(f'Found {stale_jobs.count()} stale jobs')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No jobs will be closed'))
            for job in stale_jobs:
                days_inactive = (timezone.now() - job.updated_at).days
                self.stdout.write(
                    f'  • {job.job_number}: {job.title} ({days_inactive} days inactive)'
                )
            return
        
        # Close stale jobs
        closed_count = 0
        for job in stale_jobs:
            days_inactive = (timezone.now() - job.updated_at).days
            
            # Update job status
            old_status = job.status
            job.status = 'CANCELLED'
            job.notes = (job.notes or '') + f'\n\nAuto-closed on {timezone.now().strftime("%Y-%m-%d")} due to {days_inactive} days of inactivity (previous status: {old_status})'
            job.save()
            
            # Notify assigned contractor
            if job.assigned_to:
                JobNotification.objects.create(
                    recipient=job.assigned_to,
                    job=job,
                    notification_type='REVISION_REQUIRED',
                    title='Job Auto-Closed',
                    message=f'Job {job.job_number} has been automatically closed due to {days_inactive} days of inactivity.'
                )
                
                # Send email
                try:
                    send_mail(
                        subject=f'Job {job.job_number} Auto-Closed',
                        message=f"""
Hello,

Job {job.job_number}: {job.title} has been automatically closed due to {days_inactive} days of inactivity.

Previous Status: {old_status}
New Status: CANCELLED

If this job should remain active, please contact your manager.

Best regards,
Job Management System
                        """,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[job.assigned_to.email],
                        fail_silently=True,
                    )
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Failed to send email: {str(e)}'))
            
            # Notify job creator
            if job.created_by and job.created_by != job.assigned_to:
                JobNotification.objects.create(
                    recipient=job.created_by,
                    job=job,
                    notification_type='REVISION_REQUIRED',
                    title='Job Auto-Closed',
                    message=f'Job {job.job_number} has been automatically closed due to {days_inactive} days of inactivity.'
                )
                
                # Send email
                try:
                    send_mail(
                        subject=f'Job {job.job_number} Auto-Closed',
                        message=f"""
Hello,

Job {job.job_number}: {job.title} has been automatically closed due to {days_inactive} days of inactivity.

Previous Status: {old_status}
New Status: CANCELLED

If this job should remain active, please reopen it.

Best regards,
Job Management System
                        """,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[job.created_by.email],
                        fail_silently=True,
                    )
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Failed to send email: {str(e)}'))
            
            closed_count += 1
            self.stdout.write(
                f'  ✓ Closed: {job.job_number} ({days_inactive} days inactive)'
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Auto-closed {closed_count} stale jobs'
            )
        )
