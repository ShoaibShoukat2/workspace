"""
Daily Compliance Expiry Check
Checks for expiring and expired compliance documents
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from workspace.models import ComplianceData, JobNotification
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Check for expiring and expired compliance documents'
    
    def handle(self, *args, **options):
        self.stdout.write('Starting compliance expiry check...')
        
        today = timezone.now().date()
        expiry_threshold = today + timedelta(days=30)
        
        # Find expiring documents (within 30 days)
        expiring_docs = ComplianceData.objects.filter(
            status='APPROVED',
            expiry_date__lte=expiry_threshold,
            expiry_date__gt=today
        )
        
        expiring_count = 0
        for doc in expiring_docs:
            # Update status
            doc.status = 'EXPIRING_SOON'
            doc.save()
            
            # Create notification
            JobNotification.objects.create(
                recipient=doc.contractor.user,
                job=doc.contractor.job_assignments.first().job if doc.contractor.job_assignments.exists() else None,
                notification_type='REVISION_REQUIRED',
                title='Compliance Document Expiring Soon',
                message=f'Your {doc.get_compliance_type_display()} document "{doc.document_name}" will expire on {doc.expiry_date}. Please renew it.'
            )
            
            # Send email
            try:
                send_mail(
                    subject='Compliance Document Expiring Soon',
                    message=f'Your {doc.get_compliance_type_display()} document "{doc.document_name}" will expire on {doc.expiry_date}. Please renew it to maintain compliance.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[doc.contractor.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Failed to send email: {str(e)}'))
            
            expiring_count += 1
        
        # Find expired documents
        expired_docs = ComplianceData.objects.filter(
            expiry_date__lt=today
        ).exclude(status='EXPIRED')
        
        expired_count = 0
        for doc in expired_docs:
            # Update status
            doc.status = 'EXPIRED'
            doc.save()
            
            # Create notification
            JobNotification.objects.create(
                recipient=doc.contractor.user,
                job=doc.contractor.job_assignments.first().job if doc.contractor.job_assignments.exists() else None,
                notification_type='REVISION_REQUIRED',
                title='Compliance Document Expired',
                message=f'Your {doc.get_compliance_type_display()} document "{doc.document_name}" has expired. Please renew immediately.'
            )
            
            # Send email
            try:
                send_mail(
                    subject='URGENT: Compliance Document Expired',
                    message=f'Your {doc.get_compliance_type_display()} document "{doc.document_name}" has expired on {doc.expiry_date}. Please renew immediately to maintain compliance.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[doc.contractor.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Failed to send email: {str(e)}'))
            
            expired_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Compliance check complete: {expiring_count} expiring, {expired_count} expired'
            )
        )
