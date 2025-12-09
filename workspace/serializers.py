from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Workspace, WorkspaceMember, Job, JobAttachment, 
    Estimate, EstimateLineItem, Contractor, Payout, 
    Report, ComplianceData, JobAssignment, JobChecklist,
    ChecklistStep, StepMedia, JobCompletion, JobNotification,
    ContractorWallet, WalletTransaction, PayoutRequest, JobPayoutEligibility,
    Dispute, DisputeMessage, DisputeAttachment
)

User = get_user_model()


class WorkspaceSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Workspace
        fields = [
            'id', 'workspace_id', 'name', 'workspace_type', 'owner', 
            'owner_email', 'description', 'is_active', 'member_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['workspace_id', 'owner']
    
    def get_member_count(self, obj):
        return obj.members.count()


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = WorkspaceMember
        fields = ['id', 'workspace', 'user', 'user_email', 'user_name', 'role', 'joined_at']
        read_only_fields = ['joined_at']


class JobAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.EmailField(source='uploaded_by.email', read_only=True)
    
    class Meta:
        model = JobAttachment
        fields = [
            'id', 'job', 'file_name', 'file_path', 'file_type', 
            'file_size', 'uploaded_by', 'uploaded_by_email', 
            'description', 'created_at'
        ]
        read_only_fields = ['uploaded_by']


class JobSerializer(serializers.ModelSerializer):
    assigned_to_email = serializers.EmailField(source='assigned_to.email', read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    attachments = JobAttachmentSerializer(many=True, read_only=True)
    attachment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'workspace', 'workspace_name', 'job_number', 'title', 
            'description', 'status', 'priority', 'assigned_to', 'assigned_to_email',
            'created_by', 'created_by_email', 'estimated_hours', 'actual_hours',
            'estimated_cost', 'actual_cost', 'start_date', 'due_date', 'completed_date', 
            'location', 'customer_name', 'customer_email', 'customer_phone', 
            'customer_address', 'notes', 'attachments', 'attachment_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['job_number', 'created_by']
    
    def get_attachment_count(self, obj):
        return obj.attachments.count()


class EstimateLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstimateLineItem
        fields = [
            'id', 'estimate', 'item_order', 'description', 
            'quantity', 'unit_price', 'total', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['total']


class EstimateSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    approved_by_email = serializers.EmailField(source='approved_by.email', read_only=True)
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    line_items = EstimateLineItemSerializer(many=True, read_only=True)
    line_item_count = serializers.SerializerMethodField()
    is_signed = serializers.SerializerMethodField()
    
    class Meta:
        model = Estimate
        fields = [
            'id', 'workspace', 'workspace_name', 'job', 'job_title',
            'estimate_number', 'title', 'description', 'status',
            'subtotal', 'tax_rate', 'tax_amount', 'discount_amount', 'total_amount',
            'valid_until', 'created_by', 'created_by_email',
            'approved_by', 'approved_by_email', 'approved_at',
            'customer_signature', 'customer_signed_at', 'customer_ip_address',
            'line_items', 'line_item_count', 'is_signed',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['estimate_number', 'created_by', 'subtotal', 'tax_amount', 'total_amount']
    
    def get_line_item_count(self, obj):
        return obj.line_items.count()
    
    def get_is_signed(self, obj):
        return bool(obj.customer_signature)


class EstimateWithLineItemsSerializer(serializers.ModelSerializer):
    """Serializer for creating estimate with line items in one request"""
    line_items = EstimateLineItemSerializer(many=True)
    
    class Meta:
        model = Estimate
        fields = [
            'id', 'workspace', 'job', 'estimate_number', 'title', 'description',
            'status', 'tax_rate', 'discount_amount', 'valid_until',
            'line_items', 'subtotal', 'tax_amount', 'total_amount',
            'notes', 'created_at'
        ]
        read_only_fields = ['estimate_number', 'subtotal', 'tax_amount', 'total_amount']
    
    def create(self, validated_data):
        line_items_data = validated_data.pop('line_items')
        estimate = Estimate.objects.create(**validated_data)
        
        for item_data in line_items_data:
            EstimateLineItem.objects.create(estimate=estimate, **item_data)
        
        return estimate


class ContractorSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    
    class Meta:
        model = Contractor
        fields = [
            'id', 'workspace', 'workspace_name', 'user', 'user_email', 'user_name',
            'company_name', 'license_number', 'specialization', 'hourly_rate',
            'status', 'rating', 'total_jobs_completed', 'phone', 'address',
            'notes', 'created_at', 'updated_at'
        ]


class PayoutSerializer(serializers.ModelSerializer):
    contractor_email = serializers.EmailField(source='contractor.user.email', read_only=True)
    contractor_company = serializers.CharField(source='contractor.company_name', read_only=True)
    processed_by_email = serializers.EmailField(source='processed_by.email', read_only=True)
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    
    class Meta:
        model = Payout
        fields = [
            'id', 'workspace', 'workspace_name', 'contractor', 'contractor_email',
            'contractor_company', 'job', 'job_title', 'payout_number', 'amount',
            'status', 'payment_method', 'description', 'scheduled_date',
            'paid_date', 'processed_by', 'processed_by_email',
            'transaction_reference', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['payout_number']


class ReportSerializer(serializers.ModelSerializer):
    generated_by_email = serializers.EmailField(source='generated_by.email', read_only=True)
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'workspace', 'workspace_name', 'report_type', 'title',
            'description', 'generated_by', 'generated_by_email', 'file_path',
            'date_from', 'date_to', 'created_at'
        ]
        read_only_fields = ['generated_by', 'file_path']


class ComplianceDataSerializer(serializers.ModelSerializer):
    contractor_email = serializers.EmailField(source='contractor.user.email', read_only=True)
    contractor_company = serializers.CharField(source='contractor.company_name', read_only=True)
    verified_by_email = serializers.EmailField(source='verified_by.email', read_only=True)
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    is_expiring_soon = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ComplianceData
        fields = [
            'id', 'workspace', 'workspace_name', 'contractor', 'contractor_email',
            'contractor_company', 'compliance_type', 'document_name', 'document_number',
            'status', 'issue_date', 'expiry_date', 'verified_by', 'verified_by_email',
            'verified_at', 'rejection_reason', 'file_path', 'file_size', 'notes', 
            'is_expiring_soon', 'is_expired', 'created_at', 'updated_at'
        ]
        read_only_fields = ['verified_by', 'verified_at']


# ==================== Dispute System Serializers ====================

class DisputeAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.EmailField(source='uploaded_by.email', read_only=True)
    
    class Meta:
        model = DisputeAttachment
        fields = [
            'id', 'dispute', 'uploaded_by', 'uploaded_by_email',
            'file_name', 'file_path', 'file_type', 'file_size',
            'description', 'created_at'
        ]
        read_only_fields = ['uploaded_by']


class DisputeMessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = DisputeMessage
        fields = [
            'id', 'dispute', 'sender', 'sender_email', 'sender_name',
            'message', 'is_internal', 'created_at'
        ]
        read_only_fields = ['sender']


class DisputeSerializer(serializers.ModelSerializer):
    raised_by_email = serializers.EmailField(source='raised_by.email', read_only=True)
    contractor_email = serializers.EmailField(source='contractor.user.email', read_only=True)
    contractor_company = serializers.CharField(source='contractor.company_name', read_only=True)
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    resolved_by_email = serializers.EmailField(source='resolved_by.email', read_only=True)
    messages = DisputeMessageSerializer(many=True, read_only=True)
    attachments = DisputeAttachmentSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Dispute
        fields = [
            'id', 'dispute_number', 'job', 'job_number', 'job_title',
            'raised_by', 'raised_by_email', 'contractor', 'contractor_email',
            'contractor_company', 'category', 'title', 'description', 'status',
            'resolved_by', 'resolved_by_email', 'resolved_at', 'resolution_notes',
            'messages', 'attachments', 'message_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['dispute_number', 'resolved_by', 'resolved_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()



# ==================== Contractor Module Serializers ====================

class JobAssignmentSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    contractor_email = serializers.EmailField(source='contractor.user.email', read_only=True)
    assigned_by_email = serializers.EmailField(source='assigned_by.email', read_only=True)
    
    class Meta:
        model = JobAssignment
        fields = [
            'id', 'job', 'job_title', 'job_number', 'contractor', 
            'contractor_email', 'assigned_by', 'assigned_by_email',
            'status', 'assigned_at', 'responded_at', 'rejection_reason', 'notes'
        ]
        read_only_fields = ['assigned_by', 'assigned_at']


class StepMediaSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.EmailField(source='uploaded_by.email', read_only=True)
    
    class Meta:
        model = StepMedia
        fields = [
            'id', 'step', 'media_type', 'file_name', 'file_path',
            'file_size', 'thumbnail_path', 'uploaded_by', 
            'uploaded_by_email', 'caption', 'created_at'
        ]
        read_only_fields = ['uploaded_by']


class ChecklistStepSerializer(serializers.ModelSerializer):
    media = StepMediaSerializer(many=True, read_only=True)
    media_count = serializers.SerializerMethodField()
    completed_by_email = serializers.EmailField(source='completed_by.email', read_only=True)
    
    class Meta:
        model = ChecklistStep
        fields = [
            'id', 'checklist', 'step_number', 'title', 'description',
            'is_required', 'is_completed', 'completed_by', 'completed_by_email',
            'completed_at', 'notes', 'media', 'media_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['completed_by', 'completed_at']
    
    def get_media_count(self, obj):
        return obj.media.count()


class JobChecklistSerializer(serializers.ModelSerializer):
    steps = ChecklistStepSerializer(many=True, read_only=True)
    completion_percentage = serializers.ReadOnlyField()
    total_steps = serializers.SerializerMethodField()
    completed_steps = serializers.SerializerMethodField()
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    
    class Meta:
        model = JobChecklist
        fields = [
            'id', 'job', 'title', 'description', 'order',
            'created_by', 'created_by_email', 'completion_percentage',
            'total_steps', 'completed_steps', 'steps',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by']
    
    def get_total_steps(self, obj):
        return obj.steps.count()
    
    def get_completed_steps(self, obj):
        return obj.steps.filter(is_completed=True).count()


class JobCompletionSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    contractor_email = serializers.EmailField(source='contractor.user.email', read_only=True)
    verified_by_email = serializers.EmailField(source='verified_by.email', read_only=True)
    
    class Meta:
        model = JobCompletion
        fields = [
            'id', 'job', 'job_title', 'job_number', 'contractor', 
            'contractor_email', 'submitted_at', 'status', 'completion_notes',
            'actual_hours_worked', 'verified_by', 'verified_by_email',
            'verified_at', 'verification_notes', 'quality_rating',
            'timeliness_rating', 'professionalism_rating', 'overall_rating',
            'updated_at'
        ]
        read_only_fields = ['contractor', 'submitted_at', 'verified_by', 'verified_at', 'overall_rating']


class JobNotificationSerializer(serializers.ModelSerializer):
    recipient_email = serializers.EmailField(source='recipient.email', read_only=True)
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    
    class Meta:
        model = JobNotification
        fields = [
            'id', 'recipient', 'recipient_email', 'job', 'job_number',
            'notification_type', 'title', 'message', 'is_read',
            'read_at', 'created_at'
        ]
        read_only_fields = ['recipient', 'read_at']


class ContractorJobDetailSerializer(serializers.ModelSerializer):
    """Detailed job serializer for contractor view"""
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    assignment = serializers.SerializerMethodField()
    checklists = JobChecklistSerializer(many=True, read_only=True)
    completion = JobCompletionSerializer(read_only=True)
    attachments = JobAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Job
        fields = [
            'id', 'workspace', 'workspace_name', 'job_number', 'title',
            'description', 'status', 'priority', 'created_by', 'created_by_email',
            'estimated_hours', 'estimated_cost', 'start_date', 'due_date',
            'location', 'customer_name', 'customer_email', 'customer_phone',
            'customer_address', 'notes', 'assignment', 'checklists',
            'completion', 'attachments', 'created_at', 'updated_at'
        ]
    
    def get_assignment(self, obj):
        # Get contractor from context
        contractor = self.context.get('contractor')
        if contractor:
            assignment = obj.assignments.filter(contractor=contractor).first()
            if assignment:
                return JobAssignmentSerializer(assignment).data
        return None



# ==================== Payout & Financial Flow Serializers ====================

class ContractorWalletSerializer(serializers.ModelSerializer):
    contractor_email = serializers.EmailField(source='contractor.user.email', read_only=True)
    contractor_company = serializers.CharField(source='contractor.company_name', read_only=True)
    
    class Meta:
        model = ContractorWallet
        fields = [
            'id', 'contractor', 'contractor_email', 'contractor_company',
            'balance', 'total_earned', 'total_withdrawn', 'pending_amount',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['balance', 'total_earned', 'total_withdrawn', 'pending_amount']


class WalletTransactionSerializer(serializers.ModelSerializer):
    contractor_email = serializers.EmailField(source='wallet.contractor.user.email', read_only=True)
    payout_number = serializers.CharField(source='payout.payout_number', read_only=True)
    
    class Meta:
        model = WalletTransaction
        fields = [
            'id', 'wallet', 'contractor_email', 'transaction_type', 'amount',
            'balance_after', 'status', 'description', 'reference_number',
            'payout', 'payout_number', 'created_at'
        ]
        read_only_fields = ['balance_after', 'created_at']


class PayoutRequestSerializer(serializers.ModelSerializer):
    contractor_email = serializers.EmailField(source='contractor.user.email', read_only=True)
    contractor_company = serializers.CharField(source='contractor.company_name', read_only=True)
    reviewed_by_email = serializers.EmailField(source='reviewed_by.email', read_only=True)
    payout_number = serializers.CharField(source='payout.payout_number', read_only=True)
    
    class Meta:
        model = PayoutRequest
        fields = [
            'id', 'contractor', 'contractor_email', 'contractor_company',
            'request_number', 'amount', 'status', 'payment_method',
            'bank_account_number', 'bank_name', 'bank_routing_number',
            'paypal_email', 'notes', 'reviewed_by', 'reviewed_by_email',
            'reviewed_at', 'rejection_reason', 'payout', 'payout_number',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['request_number', 'reviewed_by', 'reviewed_at', 'payout']


class JobPayoutEligibilitySerializer(serializers.ModelSerializer):
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    contractor_email = serializers.EmailField(source='contractor.user.email', read_only=True)
    contractor_company = serializers.CharField(source='contractor.company_name', read_only=True)
    payout_number = serializers.CharField(source='payout.payout_number', read_only=True)
    
    class Meta:
        model = JobPayoutEligibility
        fields = [
            'id', 'job', 'job_number', 'job_title', 'contractor',
            'contractor_email', 'contractor_company', 'amount', 'status',
            'verified_at', 'payout', 'payout_number', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['verified_at', 'payout']
