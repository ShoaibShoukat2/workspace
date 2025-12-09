import csv
from io import StringIO
from django.http import HttpResponse
from django.utils import timezone


def generate_job_number(workspace_id):
    """Generate unique job number"""
    from .models import Job
    count = Job.objects.filter(workspace__workspace_id=workspace_id).count()
    return f"JOB-{workspace_id.hex[:8].upper()}-{count + 1:05d}"


def generate_estimate_number(workspace_id):
    """Generate unique estimate number"""
    from .models import Estimate
    count = Estimate.objects.filter(workspace__workspace_id=workspace_id).count()
    return f"EST-{workspace_id.hex[:8].upper()}-{count + 1:05d}"


def generate_payout_number(workspace_id):
    """Generate unique payout number"""
    from .models import Payout
    count = Payout.objects.filter(workspace__workspace_id=workspace_id).count()
    return f"PAY-{workspace_id.hex[:8].upper()}-{count + 1:05d}"


def export_jobs_to_csv(queryset):
    """Export jobs to CSV format"""
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Job Number', 'Title', 'Status', 'Priority', 'Assigned To',
        'Estimated Hours', 'Actual Hours', 'Start Date', 'Due Date',
        'Completed Date', 'Location', 'Created At', 'Updated At'
    ])
    
    # Write data
    for job in queryset:
        writer.writerow([
            job.job_number,
            job.title,
            job.get_status_display(),
            job.get_priority_display(),
            job.assigned_to.email if job.assigned_to else 'Unassigned',
            job.estimated_hours or '',
            job.actual_hours or '',
            job.start_date or '',
            job.due_date or '',
            job.completed_date or '',
            job.location or '',
            job.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            job.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return output.getvalue()


def export_estimates_to_csv(queryset):
    """Export estimates to CSV format"""
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Estimate Number', 'Title', 'Job Number', 'Status', 'Subtotal',
        'Tax Amount', 'Discount Amount', 'Total Amount', 'Valid Until',
        'Created By', 'Approved By', 'Approved At', 'Created At'
    ])
    
    # Write data
    for estimate in queryset:
        writer.writerow([
            estimate.estimate_number,
            estimate.title,
            estimate.job.job_number if estimate.job else 'N/A',
            estimate.get_status_display(),
            f"${estimate.subtotal:.2f}",
            f"${estimate.tax_amount:.2f}",
            f"${estimate.discount_amount:.2f}",
            f"${estimate.total_amount:.2f}",
            estimate.valid_until or '',
            estimate.created_by.email if estimate.created_by else '',
            estimate.approved_by.email if estimate.approved_by else '',
            estimate.approved_at.strftime('%Y-%m-%d %H:%M:%S') if estimate.approved_at else '',
            estimate.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return output.getvalue()


def export_contractors_to_csv(queryset):
    """Export contractors to CSV format"""
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Email', 'Company Name', 'License Number', 'Specialization',
        'Hourly Rate', 'Status', 'Rating', 'Total Jobs Completed',
        'Phone', 'Address', 'Created At'
    ])
    
    # Write data
    for contractor in queryset:
        writer.writerow([
            contractor.user.email,
            contractor.company_name or '',
            contractor.license_number or '',
            contractor.specialization or '',
            f"${contractor.hourly_rate:.2f}" if contractor.hourly_rate else '',
            contractor.get_status_display(),
            contractor.rating or '',
            contractor.total_jobs_completed,
            contractor.phone or '',
            contractor.address or '',
            contractor.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return output.getvalue()


def export_payouts_to_csv(queryset):
    """Export payouts to CSV format"""
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Payout Number', 'Contractor Email', 'Company Name', 'Job Number',
        'Amount', 'Status', 'Payment Method', 'Scheduled Date',
        'Paid Date', 'Processed By', 'Transaction Reference', 'Created At'
    ])
    
    # Write data
    for payout in queryset:
        writer.writerow([
            payout.payout_number,
            payout.contractor.user.email,
            payout.contractor.company_name or '',
            payout.job.job_number if payout.job else 'N/A',
            f"${payout.amount:.2f}",
            payout.get_status_display(),
            payout.get_payment_method_display(),
            payout.scheduled_date or '',
            payout.paid_date or '',
            payout.processed_by.email if payout.processed_by else '',
            payout.transaction_reference or '',
            payout.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return output.getvalue()


def export_compliance_to_csv(queryset):
    """Export compliance data to CSV format"""
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Contractor Email', 'Company Name', 'Compliance Type', 'Document Name',
        'Document Number', 'Status', 'Issue Date', 'Expiry Date',
        'Verified By', 'Verified At', 'Created At'
    ])
    
    # Write data
    for compliance in queryset:
        writer.writerow([
            compliance.contractor.user.email,
            compliance.contractor.company_name or '',
            compliance.get_compliance_type_display(),
            compliance.document_name,
            compliance.document_number or '',
            compliance.get_status_display(),
            compliance.issue_date or '',
            compliance.expiry_date or '',
            compliance.verified_by.email if compliance.verified_by else '',
            compliance.verified_at.strftime('%Y-%m-%d %H:%M:%S') if compliance.verified_at else '',
            compliance.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return output.getvalue()


def create_csv_response(csv_content, filename):
    """Create HTTP response with CSV content"""
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
