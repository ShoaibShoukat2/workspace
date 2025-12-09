from django.core.management.base import BaseCommand
from django.utils import timezone
from workspace.models import Workspace, Report
from workspace.utils import (
    export_jobs_to_csv, export_estimates_to_csv, export_contractors_to_csv,
    export_payouts_to_csv, export_compliance_to_csv
)
import os


class Command(BaseCommand):
    help = 'Generate comprehensive report for a workspace'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'workspace_id',
            type=str,
            help='Workspace UUID to generate report for'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='reports',
            help='Output directory for reports (default: reports/)'
        )
    
    def handle(self, *args, **options):
        workspace_id = options['workspace_id']
        output_dir = options['output_dir']
        
        try:
            workspace = Workspace.objects.get(workspace_id=workspace_id)
        except Workspace.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Workspace with ID {workspace_id} not found')
            )
            return
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        workspace_name = workspace.name.replace(' ', '_')
        
        # Generate reports
        reports_generated = []
        
        # Jobs report
        if workspace.jobs.exists():
            jobs_csv = export_jobs_to_csv(workspace.jobs.all())
            jobs_filename = f'{workspace_name}_jobs_{timestamp}.csv'
            jobs_path = os.path.join(output_dir, jobs_filename)
            with open(jobs_path, 'w', encoding='utf-8') as f:
                f.write(jobs_csv)
            reports_generated.append(('Jobs', jobs_path))
            self.stdout.write(self.style.SUCCESS(f'✓ Jobs report: {jobs_path}'))
        
        # Estimates report
        if workspace.estimates.exists():
            estimates_csv = export_estimates_to_csv(workspace.estimates.all())
            estimates_filename = f'{workspace_name}_estimates_{timestamp}.csv'
            estimates_path = os.path.join(output_dir, estimates_filename)
            with open(estimates_path, 'w', encoding='utf-8') as f:
                f.write(estimates_csv)
            reports_generated.append(('Estimates', estimates_path))
            self.stdout.write(self.style.SUCCESS(f'✓ Estimates report: {estimates_path}'))
        
        # Contractors report
        if workspace.contractors.exists():
            contractors_csv = export_contractors_to_csv(workspace.contractors.all())
            contractors_filename = f'{workspace_name}_contractors_{timestamp}.csv'
            contractors_path = os.path.join(output_dir, contractors_filename)
            with open(contractors_path, 'w', encoding='utf-8') as f:
                f.write(contractors_csv)
            reports_generated.append(('Contractors', contractors_path))
            self.stdout.write(self.style.SUCCESS(f'✓ Contractors report: {contractors_path}'))
        
        # Payouts report
        if workspace.payouts.exists():
            payouts_csv = export_payouts_to_csv(workspace.payouts.all())
            payouts_filename = f'{workspace_name}_payouts_{timestamp}.csv'
            payouts_path = os.path.join(output_dir, payouts_filename)
            with open(payouts_path, 'w', encoding='utf-8') as f:
                f.write(payouts_csv)
            reports_generated.append(('Payouts', payouts_path))
            self.stdout.write(self.style.SUCCESS(f'✓ Payouts report: {payouts_path}'))
        
        # Compliance report
        if workspace.compliance_data.exists():
            compliance_csv = export_compliance_to_csv(workspace.compliance_data.all())
            compliance_filename = f'{workspace_name}_compliance_{timestamp}.csv'
            compliance_path = os.path.join(output_dir, compliance_filename)
            with open(compliance_path, 'w', encoding='utf-8') as f:
                f.write(compliance_csv)
            reports_generated.append(('Compliance', compliance_path))
            self.stdout.write(self.style.SUCCESS(f'✓ Compliance report: {compliance_path}'))
        
        # Create report record in database
        if reports_generated:
            Report.objects.create(
                workspace=workspace,
                report_type='FINANCIAL',
                title=f'Comprehensive Report - {workspace.name}',
                description=f'Generated {len(reports_generated)} reports',
                file_path=output_dir
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Report generation completed for workspace: {workspace.name}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Total reports generated: {len(reports_generated)}'
            )
        )
