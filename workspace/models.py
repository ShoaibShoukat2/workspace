from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Workspace(models.Model):
    """Workspace for each customer/project with unique ID"""
    
    class WorkspaceType(models.TextChoices):
        PROJECT = 'PROJECT', 'Project'
        CUSTOMER = 'CUSTOMER', 'Customer'
        FACILITY = 'FACILITY', 'Facility'
    
    workspace_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    name = models.CharField(max_length=255)
    workspace_type = models.CharField(max_length=20, choices=WorkspaceType.choices, default=WorkspaceType.PROJECT)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_workspaces')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.workspace_id})"
    
    class Meta:
        db_table = 'workspaces'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace_id', 'is_active']),
            models.Index(fields=['owner', 'workspace_type']),
        ]


class WorkspaceMember(models.Model):
    """Members associated with a workspace"""
    
    class MemberRole(models.TextChoices):
        OWNER = 'OWNER', 'Owner'
        ADMIN = 'ADMIN', 'Admin'
        MEMBER = 'MEMBER', 'Member'
        VIEWER = 'VIEWER', 'Viewer'
    
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workspace_memberships')
    role = models.CharField(max_length=20, choices=MemberRole.choices, default=MemberRole.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.workspace.name} ({self.role})"
    
    class Meta:
        db_table = 'workspace_members'
        unique_together = ['workspace', 'user']
        ordering = ['-joined_at']


class Job(models.Model):
    """Jobs within a workspace"""
    
    class JobStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    class JobPriority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent'
    
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='jobs')
    job_number = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=JobStatus.choices, default=JobStatus.PENDING)
    priority = models.CharField(max_length=20, choices=JobPriority.choices, default=JobPriority.MEDIUM)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_jobs')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_jobs')
    estimated_hours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    customer_address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.job_number} - {self.title}"
    
    class Meta:
        db_table = 'jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace', 'status']),
            models.Index(fields=['job_number']),
            models.Index(fields=['created_by', 'status']),
        ]


class JobAttachment(models.Model):
    """Attachments for jobs"""
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='attachments')
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_type = models.CharField(max_length=50)
    file_size = models.IntegerField(help_text='File size in bytes')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.job.job_number} - {self.file_name}"
    
    class Meta:
        db_table = 'job_attachments'
        ordering = ['-created_at']


class Estimate(models.Model):
    """Estimates for jobs"""
    
    class EstimateStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SENT = 'SENT', 'Sent'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        EXPIRED = 'EXPIRED', 'Expired'
    
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='estimates')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='estimates', null=True, blank=True)
    estimate_number = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=EstimateStatus.choices, default=EstimateStatus.DRAFT)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Tax rate in percentage')
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valid_until = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_estimates')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_estimates')
    approved_at = models.DateTimeField(null=True, blank=True)
    customer_signature = models.TextField(blank=True, null=True, help_text='Base64 encoded signature image')
    customer_signed_at = models.DateTimeField(null=True, blank=True)
    customer_ip_address = models.GenericIPAddressField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_totals(self):
        """Calculate subtotal, tax, and total from line items"""
        line_items = self.line_items.all()
        self.subtotal = sum(item.total for item in line_items)
        self.tax_amount = (self.subtotal * self.tax_rate) / 100
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.save(update_fields=['subtotal', 'tax_amount', 'total_amount'])
    
    def __str__(self):
        return f"{self.estimate_number} - {self.title}"
    
    class Meta:
        db_table = 'estimates'
        ordering = ['-created_at']


class EstimateLineItem(models.Model):
    """Line items for estimates"""
    
    estimate = models.ForeignKey(Estimate, on_delete=models.CASCADE, related_name='line_items')
    item_order = models.IntegerField(default=0)
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Calculate total
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Update estimate totals
        self.estimate.calculate_totals()
    
    def __str__(self):
        return f"{self.estimate.estimate_number} - {self.description}"
    
    class Meta:
        db_table = 'estimate_line_items'
        ordering = ['item_order', 'created_at']


class Contractor(models.Model):
    """Contractors working in workspaces"""
    
    class ContractorStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        SUSPENDED = 'SUSPENDED', 'Suspended'
    
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='contractors')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contractor_profiles')
    company_name = models.CharField(max_length=255, blank=True, null=True)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=255, blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=ContractorStatus.choices, default=ContractorStatus.ACTIVE)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    total_jobs_completed = models.IntegerField(default=0)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.company_name or 'No Company'}"
    
    class Meta:
        db_table = 'contractors'
        unique_together = ['workspace', 'user']
        ordering = ['-created_at']


class Payout(models.Model):
    """Payouts to contractors"""
    
    class PayoutStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    class PaymentMethod(models.TextChoices):
        BANK_TRANSFER = 'BANK_TRANSFER', 'Bank Transfer'
        CHECK = 'CHECK', 'Check'
        CASH = 'CASH', 'Cash'
        PAYPAL = 'PAYPAL', 'PayPal'
        OTHER = 'OTHER', 'Other'
    
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='payouts')
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE, related_name='payouts')
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True, related_name='payouts')
    payout_number = models.CharField(max_length=50, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=PayoutStatus.choices, default=PayoutStatus.PENDING)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.BANK_TRANSFER)
    description = models.TextField(blank=True, null=True)
    scheduled_date = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_payouts')
    transaction_reference = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.payout_number} - {self.contractor.user.email} - ${self.amount}"
    
    class Meta:
        db_table = 'payouts'
        ordering = ['-created_at']


class Report(models.Model):
    """Reports generated for workspaces"""
    
    class ReportType(models.TextChoices):
        JOBS = 'JOBS', 'Jobs Report'
        ESTIMATES = 'ESTIMATES', 'Estimates Report'
        CONTRACTORS = 'CONTRACTORS', 'Contractors Report'
        PAYOUTS = 'PAYOUTS', 'Payouts Report'
        COMPLIANCE = 'COMPLIANCE', 'Compliance Report'
        FINANCIAL = 'FINANCIAL', 'Financial Report'
    
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    file_path = models.CharField(max_length=500, blank=True, null=True)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.title}"
    
    class Meta:
        db_table = 'reports'
        ordering = ['-created_at']


class ComplianceData(models.Model):
    """Compliance tracking for contractors and jobs"""
    
    class ComplianceType(models.TextChoices):
        ID = 'ID', 'ID Document'
        LICENSE = 'LICENSE', 'License'
        INSURANCE = 'INSURANCE', 'Insurance'
        CERTIFICATION = 'CERTIFICATION', 'Certification'
        CONTRACT = 'CONTRACT', 'Contract'
        SAFETY = 'SAFETY', 'Safety Training'
        OTHER = 'OTHER', 'Other'
    
    class ComplianceStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Verification'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        EXPIRED = 'EXPIRED', 'Expired'
        EXPIRING_SOON = 'EXPIRING_SOON', 'Expiring Soon'
    
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='compliance_data')
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE, related_name='compliance_records')
    compliance_type = models.CharField(max_length=20, choices=ComplianceType.choices)
    document_name = models.CharField(max_length=255)
    document_number = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=ComplianceStatus.choices, default=ComplianceStatus.PENDING)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_compliance')
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.IntegerField(null=True, blank=True, help_text='File size in bytes')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.contractor.user.email} - {self.get_compliance_type_display()}"
    
    @property
    def is_expiring_soon(self):
        """Check if document expires within 30 days"""
        if self.expiry_date and self.status == 'APPROVED':
            days_until_expiry = (self.expiry_date - timezone.now().date()).days
            return 0 < days_until_expiry <= 30
        return False
    
    @property
    def is_expired(self):
        """Check if document is expired"""
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False
    
    def approve(self, admin_user):
        """Approve compliance document"""
        self.status = 'APPROVED'
        self.verified_by = admin_user
        self.verified_at = timezone.now()
        self.save()
    
    def reject(self, admin_user, reason):
        """Reject compliance document"""
        self.status = 'REJECTED'
        self.verified_by = admin_user
        self.verified_at = timezone.now()
        self.rejection_reason = reason
        self.save()
    
    class Meta:
        db_table = 'compliance_data'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace', 'status']),
            models.Index(fields=['contractor', 'compliance_type']),
        ]


# ==================== Dispute System Models ====================

class Dispute(models.Model):
    """Dispute management system"""
    
    class DisputeStatus(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        ESCALATED_TO_FM = 'ESCALATED_TO_FM', 'Escalated to FM'
        ESCALATED_TO_ADMIN = 'ESCALATED_TO_ADMIN', 'Escalated to Admin'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'
    
    class DisputeCategory(models.TextChoices):
        QUALITY = 'QUALITY', 'Quality Issue'
        PAYMENT = 'PAYMENT', 'Payment Issue'
        TIMELINE = 'TIMELINE', 'Timeline Issue'
        COMMUNICATION = 'COMMUNICATION', 'Communication Issue'
        SAFETY = 'SAFETY', 'Safety Concern'
        OTHER = 'OTHER', 'Other'
    
    dispute_number = models.CharField(max_length=50, unique=True, db_index=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='disputes')
    raised_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='raised_disputes')
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE, related_name='disputes')
    
    category = models.CharField(max_length=20, choices=DisputeCategory.choices)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=30, choices=DisputeStatus.choices, default=DisputeStatus.OPEN)
    
    # Resolution
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_disputes')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.dispute_number} - {self.title}"
    
    def escalate_to_fm(self):
        """Escalate dispute to FM"""
        self.status = 'ESCALATED_TO_FM'
        self.save()
    
    def escalate_to_admin(self):
        """Escalate dispute to Admin"""
        self.status = 'ESCALATED_TO_ADMIN'
        self.save()
    
    def resolve(self, admin_user, resolution_notes):
        """Resolve dispute"""
        self.status = 'RESOLVED'
        self.resolved_by = admin_user
        self.resolved_at = timezone.now()
        self.resolution_notes = resolution_notes
        self.save()
    
    class Meta:
        db_table = 'disputes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['contractor', 'status']),
        ]


class DisputeMessage(models.Model):
    """Messages/comments in dispute thread"""
    
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dispute_messages')
    message = models.TextField()
    is_internal = models.BooleanField(default=False, help_text='Internal note visible only to FM/Admin')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.dispute.dispute_number} - {self.sender.email}"
    
    class Meta:
        db_table = 'dispute_messages'
        ordering = ['created_at']


class DisputeAttachment(models.Model):
    """Attachments/evidence for disputes"""
    
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_type = models.CharField(max_length=50)
    file_size = models.IntegerField(help_text='File size in bytes')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.dispute.dispute_number} - {self.file_name}"
    
    class Meta:
        db_table = 'dispute_attachments'
        ordering = ['-created_at']


# ==================== Contractor Module Models ====================

class JobAssignment(models.Model):
    """Job assignments to contractors with acceptance/rejection"""
    
    class AssignmentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='assignments')
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE, related_name='job_assignments')
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='assigned_jobs_by')
    status = models.CharField(max_length=20, choices=AssignmentStatus.choices, default=AssignmentStatus.PENDING)
    assigned_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.job.job_number} - {self.contractor.user.email} ({self.status})"
    
    class Meta:
        db_table = 'job_assignments'
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['contractor', 'status']),
            models.Index(fields=['job', 'status']),
        ]


class JobChecklist(models.Model):
    """Checklist template for jobs"""
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='checklists')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.job.job_number} - {self.title}"
    
    @property
    def completion_percentage(self):
        """Calculate completion percentage"""
        total_steps = self.steps.count()
        if total_steps == 0:
            return 0
        completed_steps = self.steps.filter(is_completed=True).count()
        return (completed_steps / total_steps) * 100
    
    class Meta:
        db_table = 'job_checklists'
        ordering = ['order', 'created_at']


class ChecklistStep(models.Model):
    """Individual steps in a checklist"""
    
    checklist = models.ForeignKey(JobChecklist, on_delete=models.CASCADE, related_name='steps')
    step_number = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_required = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    completed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Step {self.step_number}: {self.title}"
    
    def mark_complete(self, user):
        """Mark step as completed"""
        self.is_completed = True
        self.completed_by = user
        self.completed_at = timezone.now()
        self.save()
    
    class Meta:
        db_table = 'checklist_steps'
        ordering = ['step_number']
        indexes = [
            models.Index(fields=['checklist', 'is_completed']),
        ]


class StepMedia(models.Model):
    """Photos/videos uploaded for checklist steps"""
    
    class MediaType(models.TextChoices):
        PHOTO = 'PHOTO', 'Photo'
        VIDEO = 'VIDEO', 'Video'
        DOCUMENT = 'DOCUMENT', 'Document'
    
    step = models.ForeignKey(ChecklistStep, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=20, choices=MediaType.choices)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.IntegerField(help_text='File size in bytes')
    thumbnail_path = models.CharField(max_length=500, blank=True, null=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    caption = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.step.title} - {self.file_name}"
    
    class Meta:
        db_table = 'step_media'
        ordering = ['-created_at']


class JobCompletion(models.Model):
    """Job completion submission and verification"""
    
    class CompletionStatus(models.TextChoices):
        SUBMITTED = 'SUBMITTED', 'Submitted'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        REVISION_REQUIRED = 'REVISION_REQUIRED', 'Revision Required'
    
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='completion')
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE, related_name='completed_jobs')
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=CompletionStatus.choices, default=CompletionStatus.SUBMITTED)
    completion_notes = models.TextField(blank=True, null=True)
    actual_hours_worked = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Verification
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_completions')
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True, null=True)
    
    # Rating
    quality_rating = models.IntegerField(null=True, blank=True, help_text='Rating 1-5')
    timeliness_rating = models.IntegerField(null=True, blank=True, help_text='Rating 1-5')
    professionalism_rating = models.IntegerField(null=True, blank=True, help_text='Rating 1-5')
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_overall_rating(self):
        """Calculate overall rating from individual ratings"""
        ratings = [
            self.quality_rating,
            self.timeliness_rating,
            self.professionalism_rating
        ]
        valid_ratings = [r for r in ratings if r is not None]
        if valid_ratings:
            self.overall_rating = sum(valid_ratings) / len(valid_ratings)
            self.save(update_fields=['overall_rating'])
    
    def __str__(self):
        return f"{self.job.job_number} - {self.status}"
    
    class Meta:
        db_table = 'job_completions'
        ordering = ['-submitted_at']


class JobNotification(models.Model):
    """Notifications for job-related events"""
    
    class NotificationType(models.TextChoices):
        JOB_ASSIGNED = 'JOB_ASSIGNED', 'Job Assigned'
        JOB_ACCEPTED = 'JOB_ACCEPTED', 'Job Accepted'
        JOB_REJECTED = 'JOB_REJECTED', 'Job Rejected'
        JOB_STARTED = 'JOB_STARTED', 'Job Started'
        JOB_COMPLETED = 'JOB_COMPLETED', 'Job Completed'
        JOB_VERIFIED = 'JOB_VERIFIED', 'Job Verified'
        REVISION_REQUIRED = 'REVISION_REQUIRED', 'Revision Required'
        STEP_COMPLETED = 'STEP_COMPLETED', 'Step Completed'
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_notifications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
    
    def __str__(self):
        return f"{self.recipient.email} - {self.title}"
    
    class Meta:
        db_table = 'job_notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['job', 'notification_type']),
        ]



# ==================== Payout & Financial Flow Models ====================

class ContractorWallet(models.Model):
    """Contractor wallet for managing earnings"""
    
    contractor = models.OneToOneField(Contractor, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_withdrawn = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pending_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.contractor.user.email} - Balance: ${self.balance}"
    
    def credit(self, amount, description=''):
        """Credit amount to wallet"""
        self.balance += amount
        self.total_earned += amount
        self.save()
        
        # Create transaction record
        WalletTransaction.objects.create(
            wallet=self,
            transaction_type='CREDIT',
            amount=amount,
            balance_after=self.balance,
            description=description
        )
    
    def debit(self, amount, description=''):
        """Debit amount from wallet"""
        if self.balance >= amount:
            self.balance -= amount
            self.total_withdrawn += amount
            self.save()
            
            # Create transaction record
            WalletTransaction.objects.create(
                wallet=self,
                transaction_type='DEBIT',
                amount=amount,
                balance_after=self.balance,
                description=description
            )
            return True
        return False
    
    def add_pending(self, amount):
        """Add to pending amount"""
        self.pending_amount += amount
        self.save()
    
    def clear_pending(self, amount):
        """Clear pending amount"""
        self.pending_amount -= amount
        if self.pending_amount < 0:
            self.pending_amount = 0
        self.save()
    
    class Meta:
        db_table = 'contractor_wallets'


class WalletTransaction(models.Model):
    """Transaction history for contractor wallet"""
    
    class TransactionType(models.TextChoices):
        CREDIT = 'CREDIT', 'Credit'
        DEBIT = 'DEBIT', 'Debit'
    
    class TransactionStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    wallet = models.ForeignKey(ContractorWallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=TransactionStatus.choices, default=TransactionStatus.COMPLETED)
    description = models.TextField(blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    payout = models.ForeignKey(Payout, on_delete=models.SET_NULL, null=True, blank=True, related_name='wallet_transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_type} - ${self.amount} - {self.wallet.contractor.user.email}"
    
    class Meta:
        db_table = 'wallet_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet', 'transaction_type']),
            models.Index(fields=['created_at']),
        ]


class PayoutRequest(models.Model):
    """Payout requests from contractors"""
    
    class RequestStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
    
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE, related_name='payout_requests')
    request_number = models.CharField(max_length=50, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=RequestStatus.choices, default=RequestStatus.PENDING)
    payment_method = models.CharField(max_length=20, choices=Payout.PaymentMethod.choices)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    bank_routing_number = models.CharField(max_length=50, blank=True, null=True)
    paypal_email = models.EmailField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Admin actions
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_payout_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Payout tracking
    payout = models.OneToOneField(Payout, on_delete=models.SET_NULL, null=True, blank=True, related_name='payout_request')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.request_number} - {self.contractor.user.email} - ${self.amount}"
    
    class Meta:
        db_table = 'payout_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['contractor', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]


class JobPayoutEligibility(models.Model):
    """Track jobs eligible for payout"""
    
    class EligibilityStatus(models.TextChoices):
        READY = 'READY', 'Ready for Payout'
        PROCESSING = 'PROCESSING', 'Processing'
        PAID = 'PAID', 'Paid'
        ON_HOLD = 'ON_HOLD', 'On Hold'
    
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='payout_eligibility')
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE, related_name='eligible_payouts')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=EligibilityStatus.choices, default=EligibilityStatus.READY)
    verified_at = models.DateTimeField(auto_now_add=True)
    payout = models.ForeignKey(Payout, on_delete=models.SET_NULL, null=True, blank=True, related_name='eligible_jobs')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.job.job_number} - {self.contractor.user.email} - ${self.amount}"
    
    def mark_as_paid(self, payout):
        """Mark job as paid"""
        self.status = 'PAID'
        self.payout = payout
        self.save()
    
    class Meta:
        db_table = 'job_payout_eligibility'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['contractor', 'status']),
            models.Index(fields=['status']),
        ]


# ==================== Customer Dashboard & GPS Tracking Models ====================

class CustomerProfile(models.Model):
    """Customer profile for dashboard access"""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_profile')
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='customers')
    company_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact = models.CharField(max_length=255, blank=True, null=True)
    emergency_phone = models.CharField(max_length=20, blank=True, null=True)
    preferred_contact_method = models.CharField(max_length=20, default='EMAIL')
    notification_preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.company_name or 'Individual'}"
    
    class Meta:
        db_table = 'customer_profiles'
        unique_together = ['user', 'workspace']


class ContractorLocation(models.Model):
    """Real-time GPS tracking for contractors"""
    
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE, related_name='locations')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='contractor_locations', null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    accuracy = models.FloatField(help_text='GPS accuracy in meters')
    speed = models.FloatField(null=True, blank=True, help_text='Speed in km/h')
    heading = models.FloatField(null=True, blank=True, help_text='Direction in degrees')
    altitude = models.FloatField(null=True, blank=True, help_text='Altitude in meters')
    is_active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.contractor.user.email} - {self.latitude}, {self.longitude}"
    
    @property
    def coordinates(self):
        return {'lat': float(self.latitude), 'lng': float(self.longitude)}
    
    class Meta:
        db_table = 'contractor_locations'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['contractor', 'timestamp']),
            models.Index(fields=['job', 'timestamp']),
            models.Index(fields=['is_active', 'timestamp']),
        ]


class JobTracking(models.Model):
    """Enhanced job tracking with customer-facing status updates"""
    
    class TrackingStatus(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        EN_ROUTE = 'EN_ROUTE', 'En Route'
        ARRIVED = 'ARRIVED', 'Arrived'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        DELAYED = 'DELAYED', 'Delayed'
    
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=20, choices=TrackingStatus.choices, default=TrackingStatus.SCHEDULED)
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    actual_arrival = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    delay_reason = models.TextField(blank=True, null=True)
    customer_notified = models.BooleanField(default=False)
    last_location_update = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.job.job_number} - {self.status}"
    
    def update_status(self, new_status, notify_customer=True):
        """Update tracking status and optionally notify customer"""
        self.status = new_status
        self.updated_at = timezone.now()
        
        if new_status == 'ARRIVED':
            self.actual_arrival = timezone.now()
        elif new_status == 'IN_PROGRESS':
            self.started_at = timezone.now()
        elif new_status == 'COMPLETED':
            self.completed_at = timezone.now()
        
        self.save()
        
        if notify_customer:
            self.send_customer_notification(new_status)
    
    def send_customer_notification(self, status):
        """Send notification to customer about status change"""
        # This would integrate with notification service
        pass
    
    class Meta:
        db_table = 'job_tracking'
        indexes = [
            models.Index(fields=['status', 'updated_at']),
        ]


class CustomerNotification(models.Model):
    """Notifications sent to customers"""
    
    class NotificationType(models.TextChoices):
        JOB_SCHEDULED = 'JOB_SCHEDULED', 'Job Scheduled'
        TECH_EN_ROUTE = 'TECH_EN_ROUTE', 'Technician En Route'
        TECH_ARRIVED = 'TECH_ARRIVED', 'Technician Arrived'
        JOB_STARTED = 'JOB_STARTED', 'Job Started'
        JOB_COMPLETED = 'JOB_COMPLETED', 'Job Completed'
        JOB_DELAYED = 'JOB_DELAYED', 'Job Delayed'
        MATERIAL_DELIVERED = 'MATERIAL_DELIVERED', 'Material Delivered'
    
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='notifications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='customer_notifications')
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    sent_via = models.CharField(max_length=20, default='EMAIL')  # EMAIL, SMS, PUSH
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.customer.user.email} - {self.title}"
    
    class Meta:
        db_table = 'customer_notifications'
        ordering = ['-sent_at']


class MaterialDelivery(models.Model):
    """Track material deliveries for jobs"""
    
    class DeliveryStatus(models.TextChoices):
        ORDERED = 'ORDERED', 'Ordered'
        SHIPPED = 'SHIPPED', 'Shipped'
        OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY', 'Out for Delivery'
        DELIVERED = 'DELIVERED', 'Delivered'
        DELAYED = 'DELAYED', 'Delayed'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='material_deliveries')
    item_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    supplier = models.CharField(max_length=255, blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=DeliveryStatus.choices, default=DeliveryStatus.ORDERED)
    ordered_date = models.DateField(auto_now_add=True)
    expected_delivery = models.DateField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)
    delivery_photo = models.CharField(max_length=500, blank=True, null=True)
    delivery_notes = models.TextField(blank=True, null=True)
    received_by = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.job.job_number} - {self.item_name}"
    
    class Meta:
        db_table = 'material_deliveries'
        ordering = ['-created_at']


# ==================== Enhanced Investor Models ====================

class InvestorProfile(models.Model):
    """Investor profile with enhanced tracking"""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='investor_profile')
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='investors')
    investment_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    profit_share_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_earnings = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_payouts_received = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    roi_percentage = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    investment_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.profit_share_percentage}%"
    
    def calculate_roi(self):
        """Calculate current ROI"""
        if self.investment_amount > 0:
            self.roi_percentage = (self.total_earnings / self.investment_amount) * 100
            self.save(update_fields=['roi_percentage'])
        return self.roi_percentage
    
    class Meta:
        db_table = 'investor_profiles'
        unique_together = ['user', 'workspace']


class PropertyInvestment(models.Model):
    """Track property-level investments and performance"""
    
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name='property_investments')
    property_name = models.CharField(max_length=255)
    property_address = models.TextField()
    investment_amount = models.DecimalField(max_digits=15, decimal_places=2)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    active_jobs_count = models.IntegerField(default=0)
    completed_jobs_count = models.IntegerField(default=0)
    issues_flagged = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.property_name} - {self.investor.user.email}"
    
    class Meta:
        db_table = 'property_investments'
        ordering = ['-created_at']


class InvestorPayout(models.Model):
    """Track payouts to investors"""
    
    class PayoutStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
    
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name='payouts')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='investor_payouts', null=True, blank=True)
    property_investment = models.ForeignKey(PropertyInvestment, on_delete=models.CASCADE, related_name='payouts', null=True, blank=True)
    payout_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    apex_earnings = models.DecimalField(max_digits=12, decimal_places=2)
    investor_earnings = models.DecimalField(max_digits=12, decimal_places=2)
    profit_split_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, choices=PayoutStatus.choices, default=PayoutStatus.PENDING)
    payout_date = models.DateField(null=True, blank=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.payout_number} - {self.investor.user.email} - ${self.amount}"
    
    class Meta:
        db_table = 'investor_payouts'
        ordering = ['-created_at']


# ==================== Support System Models ====================

class SupportTicket(models.Model):
    """Support tickets for contractors and customers"""
    
    class TicketStatus(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        WAITING_RESPONSE = 'WAITING_RESPONSE', 'Waiting for Response'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'
    
    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent'
    
    ticket_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets')
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=TicketStatus.choices, default=TicketStatus.OPEN)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    category = models.CharField(max_length=50, blank=True, null=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"
    
    class Meta:
        db_table = 'support_tickets'
        ordering = ['-created_at']


class SupportMessage(models.Model):
    """Messages in support tickets"""
    
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_internal = models.BooleanField(default=False)
    attachments = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.ticket.ticket_number} - {self.sender.email}"
    
    class Meta:
        db_table = 'support_messages'
        ordering = ['created_at']
