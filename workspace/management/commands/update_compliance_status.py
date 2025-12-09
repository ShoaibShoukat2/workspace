from django.core.management.base import BaseCommand
from django.utils import timezone
from workspace.models import ComplianceData


class Command(BaseCommand):
    help = 'Update compliance document status based on expiry dates'
    
    def handle(self, *args, **options):
        today = timezone.now().date()
        updated_count = 0
        
        # Get all compliance records
        compliance_records = ComplianceData.objects.all()
        
        for compliance in compliance_records:
            if compliance.expiry_date:
                old_status = compliance.status
                
                if compliance.is_expired:
                    compliance.status = ComplianceData.ComplianceStatus.EXPIRED
                elif compliance.is_expiring_soon:
                    compliance.status = ComplianceData.ComplianceStatus.EXPIRING_SOON
                else:
                    compliance.status = ComplianceData.ComplianceStatus.VALID
                
                if old_status != compliance.status:
                    compliance.save(update_fields=['status'])
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated {compliance.contractor.user.email} - '
                            f'{compliance.document_name}: {old_status} -> {compliance.status}'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompliance status update completed. {updated_count} records updated.'
            )
        )
