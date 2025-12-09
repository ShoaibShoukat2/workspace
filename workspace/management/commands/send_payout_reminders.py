"""
Payout Reminders
Sends reminders for pending payout requests and ready-for-payout jobs
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from workspace.models import PayoutRequest, JobPayoutEligibility, JobNotification
from authentication.models import User
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Send payout reminders to admins and contractors'
    
    def handle(self, *args, **options):
        self.stdout.write('Starting payout reminders...')
        
        # Find pending payout requests
        pending_requests = PayoutRequest.objects.filter(status='PENDING')
        
        # Find ready-for-payout jobs
        ready_for_payout = JobPayoutEligibility.objects.filter(status='READY')
        
        # Send reminders to admins
        admin_users = User.objects.filter(role='ADMIN', is_active=True)
        
        if pending_requests.exists() or ready_for_payout.exists():
            admin_count = 0
            for admin in admin_users:
                # Create notification
                JobNotification.objects.create(
                    recipient=admin,
                    job=None,
                    notification_type='JOB_VERIFIED',
                    title='Payout Reminders',
                    message=f'You have {pending_requests.count()} pending payout requests and {ready_for_payout.count()} jobs ready for payout.'
                )
                
                # Send email
                try:
                    email_body = f"""
Hello {admin.username},

Payout Reminder:

📋 PENDING PAYOUT REQUESTS: {pending_requests.count()}
"""
                    
                    if pending_requests.exists():
                        email_body += "\nTop 5 Pending Requests:\n"
                        for req in pending_requests[:5]:
                            email_body += f"  • {req.request_number}: {req.contractor.user.email} - ${req.amount:,.2f}\n"
                    
                    email_body += f"\n💰 READY FOR PAYOUT: {ready_for_payout.count()}\n"
                    
                    if ready_for_payout.exists():
                        email_body += "\nTop 5 Ready for Payout:\n"
                        for eligibility in ready_for_payout[:5]:
                            email_body += f"  • {eligibility.job.job_number}: {eligibility.contractor.user.email} - ${eligibility.amount:,.2f}\n"
                    
                    email_body += """
Please review and process these payouts.

Best regards,
Job Management System
                    """
                    
                    send_mail(
                        subject='Payout Reminders',
                        message=email_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[admin.email],
                        fail_silently=True,
                    )
                    admin_count += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Failed to send email to {admin.email}: {str(e)}'))
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Admin reminders sent: {admin_count} emails'
                )
            )
        
        # Send reminders to contractors with old pending requests (>7 days)
        old_threshold = timezone.now() - timedelta(days=7)
        old_requests = PayoutRequest.objects.filter(
            status='PENDING',
            created_at__lt=old_threshold
        )
        
        contractor_count = 0
        for request in old_requests:
            # Create notification
            JobNotification.objects.create(
                recipient=request.contractor.user,
                job=None,
                notification_type='JOB_VERIFIED',
                title='Payout Request Pending',
                message=f'Your payout request {request.request_number} for ${request.amount:,.2f} is still pending review.'
            )
            
            # Send email
            try:
                send_mail(
                    subject='Payout Request Status Update',
                    message=f"""
Hello,

Your payout request {request.request_number} for ${request.amount:,.2f} submitted on {request.created_at.strftime('%B %d, %Y')} is still pending review.

We are processing your request and will update you soon.

Best regards,
Job Management System
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.contractor.user.email],
                    fail_silently=True,
                )
                contractor_count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Failed to send email: {str(e)}'))
        
        if contractor_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Contractor reminders sent: {contractor_count} emails'
                )
            )
        
        self.stdout.write(self.style.SUCCESS('Payout reminders complete'))
