from django.contrib import admin
from .models import (
    Workspace, WorkspaceMember, Job, JobAttachment,
    Estimate, EstimateLineItem, Contractor, Payout, 
    Report, ComplianceData, JobAssignment, JobChecklist,
    ChecklistStep, StepMedia, JobCompletion, JobNotification,
    ContractorWallet, WalletTransaction, PayoutRequest, JobPayoutEligibility,
    Dispute, DisputeMessage, DisputeAttachment
)


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'workspace_id', 'workspace_type', 'owner', 'is_active', 'created_at']
    list_filter = ['workspace_type', 'is_active', 'created_at']
    search_fields = ['name', 'workspace_id', 'owner__email']
    readonly_fields = ['workspace_id', 'created_at', 'updated_at']


@admin.register(WorkspaceMember)
class WorkspaceMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'workspace', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['user__email', 'workspace__name']


class JobAttachmentInline(admin.TabularInline):
    model = JobAttachment
    extra = 0
    readonly_fields = ['uploaded_by', 'created_at']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['job_number', 'title', 'workspace', 'status', 'priority', 'assigned_to', 'customer_name', 'due_date']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['job_number', 'title', 'workspace__name', 'customer_name']
    readonly_fields = ['job_number', 'created_at', 'updated_at']
    inlines = [JobAttachmentInline]


@admin.register(JobAttachment)
class JobAttachmentAdmin(admin.ModelAdmin):
    list_display = ['job', 'file_name', 'file_type', 'file_size', 'uploaded_by', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['job__job_number', 'file_name']
    readonly_fields = ['uploaded_by', 'created_at']


class EstimateLineItemInline(admin.TabularInline):
    model = EstimateLineItem
    extra = 1
    readonly_fields = ['total']


@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = ['estimate_number', 'title', 'workspace', 'status', 'total_amount', 'is_signed', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['estimate_number', 'title', 'workspace__name']
    readonly_fields = ['estimate_number', 'subtotal', 'tax_amount', 'total_amount', 'created_at', 'updated_at']
    inlines = [EstimateLineItemInline]
    
    def is_signed(self, obj):
        return bool(obj.customer_signature)
    is_signed.boolean = True


@admin.register(EstimateLineItem)
class EstimateLineItemAdmin(admin.ModelAdmin):
    list_display = ['estimate', 'description', 'quantity', 'unit_price', 'total']
    list_filter = ['created_at']
    search_fields = ['estimate__estimate_number', 'description']
    readonly_fields = ['total']


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'workspace', 'status', 'rating', 'total_jobs_completed']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'company_name', 'license_number']


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ['payout_number', 'contractor', 'amount', 'status', 'payment_method', 'scheduled_date']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['payout_number', 'contractor__user__email']
    readonly_fields = ['payout_number', 'created_at', 'updated_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'workspace', 'generated_by', 'created_at']
    list_filter = ['report_type', 'created_at']
    search_fields = ['title', 'workspace__name']


@admin.register(ComplianceData)
class ComplianceDataAdmin(admin.ModelAdmin):
    list_display = ['contractor', 'compliance_type', 'document_name', 'status', 'expiry_date']
    list_filter = ['compliance_type', 'status', 'created_at']
    search_fields = ['contractor__user__email', 'document_name', 'document_number']
    readonly_fields = ['created_at', 'updated_at']



# ==================== Contractor Module Admin ====================

@admin.register(JobAssignment)
class JobAssignmentAdmin(admin.ModelAdmin):
    list_display = ['job', 'contractor', 'status', 'assigned_by', 'assigned_at', 'responded_at']
    list_filter = ['status', 'assigned_at']
    search_fields = ['job__job_number', 'contractor__user__email']
    readonly_fields = ['assigned_at', 'responded_at']


class ChecklistStepInline(admin.TabularInline):
    model = ChecklistStep
    extra = 1
    readonly_fields = ['completed_by', 'completed_at']


@admin.register(JobChecklist)
class JobChecklistAdmin(admin.ModelAdmin):
    list_display = ['job', 'completion_percentage', 'created_at']
    list_filter = ['created_at']
    search_fields = ['job__job_number']
    readonly_fields = ['completion_percentage']


@admin.register(ChecklistStep)
class ChecklistStepAdmin(admin.ModelAdmin):
    list_display = ['checklist', 'step_number', 'title', 'is_required', 'is_completed', 'completed_at']
    list_filter = ['is_required', 'is_completed', 'created_at']
    search_fields = ['checklist__job__job_number', 'title']
    readonly_fields = ['completed_by', 'completed_at']


@admin.register(StepMedia)
class StepMediaAdmin(admin.ModelAdmin):
    list_display = ['step', 'media_type', 'file_name', 'file_size', 'uploaded_by', 'created_at']
    list_filter = ['media_type', 'created_at']
    search_fields = ['step__title', 'file_name']
    readonly_fields = ['uploaded_by', 'created_at']


@admin.register(JobCompletion)
class JobCompletionAdmin(admin.ModelAdmin):
    list_display = ['job', 'contractor', 'status', 'overall_rating', 'submitted_at', 'verified_at']
    list_filter = ['status', 'submitted_at']
    search_fields = ['job__job_number', 'contractor__user__email']
    readonly_fields = ['submitted_at', 'verified_at', 'overall_rating']


@admin.register(JobNotification)
class JobNotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'job', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__email', 'job__job_number', 'title']
    readonly_fields = ['read_at', 'created_at']



# ==================== Payout & Financial Flow Admin ====================

@admin.register(ContractorWallet)
class ContractorWalletAdmin(admin.ModelAdmin):
    list_display = ['contractor', 'balance', 'total_earned', 'total_withdrawn', 'pending_amount', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['contractor__user__email', 'contractor__company_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'transaction_type', 'amount', 'balance_after', 'status', 'created_at']
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['wallet__contractor__user__email', 'reference_number', 'description']
    readonly_fields = ['created_at']


@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = ['request_number', 'contractor', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['request_number', 'contractor__user__email']
    readonly_fields = ['request_number', 'reviewed_at', 'created_at', 'updated_at']


@admin.register(JobPayoutEligibility)
class JobPayoutEligibilityAdmin(admin.ModelAdmin):
    list_display = ['job', 'contractor', 'amount', 'status', 'verified_at']
    list_filter = ['status', 'verified_at', 'created_at']
    search_fields = ['job__job_number', 'contractor__user__email']
    readonly_fields = ['verified_at', 'created_at', 'updated_at']



# ==================== Compliance & Disputes Admin ====================

class DisputeMessageInline(admin.TabularInline):
    model = DisputeMessage
    extra = 0
    readonly_fields = ['sender', 'created_at']


class DisputeAttachmentInline(admin.TabularInline):
    model = DisputeAttachment
    extra = 0
    readonly_fields = ['uploaded_by', 'created_at']


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ['dispute_number', 'job', 'contractor', 'category', 'status', 'raised_by', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['dispute_number', 'job__job_number', 'contractor__user__email', 'title']
    readonly_fields = ['dispute_number', 'resolved_at', 'created_at', 'updated_at']
    inlines = [DisputeMessageInline, DisputeAttachmentInline]


@admin.register(DisputeMessage)
class DisputeMessageAdmin(admin.ModelAdmin):
    list_display = ['dispute', 'sender', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['dispute__dispute_number', 'sender__email', 'message']
    readonly_fields = ['created_at']


@admin.register(DisputeAttachment)
class DisputeAttachmentAdmin(admin.ModelAdmin):
    list_display = ['dispute', 'file_name', 'file_type', 'file_size', 'uploaded_by', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['dispute__dispute_number', 'file_name']
    readonly_fields = ['uploaded_by', 'created_at']
