from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Workspace, WorkspaceMember, Job, JobAttachment, 
    Estimate, EstimateLineItem, Contractor, Payout, 
    Report, ComplianceData, JobAssignment, JobChecklist,
    ChecklistStep, StepMedia, JobCompletion, JobNotification,
    ContractorWallet, WalletTransaction, PayoutRequest, JobPayoutEligibility,
    Dispute, DisputeMessage, DisputeAttachment,
    # Job workflow models
    JobEvaluation, JobPhoto, JobQuote, JobCheckpoint, JobProgressNote, MaterialSuggestion,
    # New models
    CustomerProfile, ContractorLocation, JobTracking, CustomerNotification,
    MaterialReference, InvestorProfile, PropertyInvestment, InvestorPayout,
    SupportTicket, SupportMessage,
    # Angi and AI models
    AngiConnection, Lead, LeadActivity, PriceIntelligence,
    InsuranceVerification, AIConversation, TwilioIntegration, CommunicationLog
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
    completion = JobCompletionSerializer(read_only=True)
    attachments = JobAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Job
        fields = [
            'id', 'workspace', 'workspace_name', 'job_number', 'title',
            'description', 'status', 'priority', 'created_by', 'created_by_email',
            'estimated_hours', 'estimated_cost', 'start_date', 'due_date',
            'location', 'customer_name', 'customer_email', 'customer_phone',
            'customer_address', 'notes', 'assignment',
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


# ==================== Customer Dashboard Serializers ====================

class CustomerProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    
    class Meta:
        model = CustomerProfile
        fields = [
            'id', 'user', 'user_email', 'workspace', 'workspace_name',
            'company_name', 'address', 'phone', 'emergency_contact',
            'emergency_phone', 'preferred_contact_method', 'notification_preferences',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'workspace']


class ContractorLocationSerializer(serializers.ModelSerializer):
    contractor_email = serializers.EmailField(source='contractor.user.email', read_only=True)
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    coordinates = serializers.ReadOnlyField()
    
    class Meta:
        model = ContractorLocation
        fields = [
            'id', 'contractor', 'contractor_email', 'job', 'job_number',
            'latitude', 'longitude', 'coordinates', 'accuracy', 'speed',
            'heading', 'altitude', 'is_active', 'timestamp'
        ]
        read_only_fields = ['contractor', 'timestamp']


class JobTrackingSerializer(serializers.ModelSerializer):
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    
    class Meta:
        model = JobTracking
        fields = [
            'id', 'job', 'job_number', 'job_title', 'status',
            'estimated_arrival', 'actual_arrival', 'started_at',
            'completed_at', 'delay_reason', 'customer_notified',
            'last_location_update', 'created_at', 'updated_at'
        ]
        read_only_fields = ['job', 'actual_arrival', 'started_at', 'completed_at']


class CustomerNotificationSerializer(serializers.ModelSerializer):
    customer_email = serializers.EmailField(source='customer.user.email', read_only=True)
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    
    class Meta:
        model = CustomerNotification
        fields = [
            'id', 'customer', 'customer_email', 'job', 'job_number',
            'notification_type', 'title', 'message', 'sent_via',
            'is_read', 'sent_at', 'read_at'
        ]
        read_only_fields = ['customer', 'sent_at', 'read_at']


class MaterialReferenceSerializer(serializers.ModelSerializer):
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    price_range = serializers.ReadOnlyField()
    
    class Meta:
        model = MaterialReference
        fields = [
            'id', 'job', 'job_number', 'job_title', 'item_name',
            'quantity', 'supplier', 'supplier_logo', 'sku',
            'price_low', 'price_high', 'price_range', 'purchase_url',
            'description', 'created_at', 'updated_at'
        ]


# ==================== Enhanced Investor Serializers ====================

class InvestorProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    
    class Meta:
        model = InvestorProfile
        fields = [
            'id', 'user', 'user_email', 'workspace', 'workspace_name',
            'investment_amount', 'profit_share_percentage', 'total_earnings',
            'total_payouts_received', 'roi_percentage', 'investment_date',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'workspace', 'total_earnings', 'total_payouts_received', 'roi_percentage']


class PropertyInvestmentSerializer(serializers.ModelSerializer):
    investor_email = serializers.EmailField(source='investor.user.email', read_only=True)
    
    class Meta:
        model = PropertyInvestment
        fields = [
            'id', 'investor', 'investor_email', 'property_name',
            'property_address', 'investment_amount', 'total_revenue',
            'total_profit', 'active_jobs_count', 'completed_jobs_count',
            'issues_flagged', 'created_at', 'updated_at'
        ]
        read_only_fields = ['total_revenue', 'total_profit', 'active_jobs_count', 'completed_jobs_count', 'issues_flagged']


class InvestorPayoutSerializer(serializers.ModelSerializer):
    investor_email = serializers.EmailField(source='investor.user.email', read_only=True)
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    property_name = serializers.CharField(source='property_investment.property_name', read_only=True)
    processed_by_email = serializers.EmailField(source='processed_by.email', read_only=True)
    
    class Meta:
        model = InvestorPayout
        fields = [
            'id', 'investor', 'investor_email', 'job', 'job_number',
            'property_investment', 'property_name', 'payout_number',
            'amount', 'apex_earnings', 'investor_earnings', 'profit_split_percentage',
            'status', 'payout_date', 'processed_by', 'processed_by_email',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['payout_number', 'processed_by']


# ==================== Support System Serializers ====================

class SupportMessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    
    class Meta:
        model = SupportMessage
        fields = [
            'id', 'ticket', 'sender', 'sender_email', 'sender_name',
            'message', 'is_internal', 'attachments', 'created_at'
        ]
        read_only_fields = ['sender']


class SupportTicketSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    assigned_to_email = serializers.EmailField(source='assigned_to.email', read_only=True)
    message_count = serializers.SerializerMethodField()
    latest_message = serializers.SerializerMethodField()
    
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'ticket_number', 'user', 'user_email', 'workspace',
            'workspace_name', 'subject', 'description', 'status',
            'priority', 'category', 'assigned_to', 'assigned_to_email',
            'resolved_at', 'message_count', 'latest_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['ticket_number', 'user', 'resolved_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_latest_message(self, obj):
        latest = obj.messages.order_by('-created_at').first()
        if latest:
            return {
                'message': latest.message[:100] + '...' if len(latest.message) > 100 else latest.message,
                'sender_email': latest.sender.email,
                'created_at': latest.created_at
            }
        return None


# ==================== Angi Integration Serializers ====================

class AngiConnectionSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    is_token_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = AngiConnection
        fields = [
            'id', 'user', 'user_email', 'workspace', 'workspace_name',
            'angi_account_id', 'is_active', 'is_token_expired',
            'last_sync', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'workspace', 'access_token', 'refresh_token']


class LeadActivitySerializer(serializers.ModelSerializer):
    performed_by_email = serializers.EmailField(source='performed_by.email', read_only=True)
    
    class Meta:
        model = LeadActivity
        fields = [
            'id', 'lead', 'activity_type', 'description',
            'performed_by', 'performed_by_email', 'metadata', 'created_at'
        ]
        read_only_fields = ['performed_by']


class LeadSerializer(serializers.ModelSerializer):
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    assigned_to_email = serializers.EmailField(source='assigned_to.email', read_only=True)
    angi_account_id = serializers.CharField(source='angi_connection.angi_account_id', read_only=True)
    converted_job_number = serializers.CharField(source='converted_job.job_number', read_only=True)
    activities = LeadActivitySerializer(many=True, read_only=True)
    activity_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Lead
        fields = [
            'id', 'workspace', 'workspace_name', 'lead_number', 'source', 'status',
            'customer_name', 'customer_phone', 'customer_email', 'service_type',
            'location', 'description', 'angi_lead_id', 'angi_account_id',
            'ai_contacted', 'ai_contact_preference', 'converted_job', 'converted_job_number',
            'created_by', 'created_by_email', 'assigned_to', 'assigned_to_email',
            'activities', 'activity_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['lead_number', 'workspace', 'created_by', 'converted_job']
    
    def get_activity_count(self, obj):
        return obj.activities.count()


# ==================== Price Intelligence Serializers ====================

class PriceIntelligenceSerializer(serializers.ModelSerializer):
    price_change_percentage = serializers.ReadOnlyField()
    supplier_display = serializers.CharField(source='get_supplier_display', read_only=True)
    
    class Meta:
        model = PriceIntelligence
        fields = [
            'id', 'material_name', 'sku', 'supplier', 'supplier_display',
            'category', 'current_price', 'previous_price', 'price_change_percentage',
            'price_per_unit', 'brand', 'description', 'product_url', 'image_url',
            'in_stock', 'stock_level', 'last_scraped', 'created_at'
        ]
        read_only_fields = ['last_scraped', 'created_at']


# ==================== Insurance Verification Serializers ====================

class InsuranceVerificationSerializer(serializers.ModelSerializer):
    contractor_email = serializers.EmailField(source='contractor.user.email', read_only=True)
    contractor_company = serializers.CharField(source='contractor.company_name', read_only=True)
    verified_by_email = serializers.EmailField(source='verified_by.email', read_only=True)
    is_expiring_soon = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = InsuranceVerification
        fields = [
            'id', 'contractor', 'contractor_email', 'contractor_company',
            'insurance_company', 'policy_number', 'coverage_amount',
            'effective_date', 'expiry_date', 'status', 'apex_co_insured',
            'document_path', 'document_parsed_data', 'last_verified',
            'verified_by', 'verified_by_email', 'verification_notes',
            'auto_flagged', 'flag_reason', 'is_expiring_soon', 'is_expired',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['verified_by', 'last_verified', 'auto_flagged', 'flag_reason']


# ==================== Job Workflow Serializers ====================

class JobEvaluationSerializer(serializers.ModelSerializer):
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    
    class Meta:
        model = JobEvaluation
        fields = [
            'id', 'job', 'job_number', 'room_count', 'square_feet',
            'measurements_data', 'scope', 'tools_required', 'labor_required',
            'estimated_hours', 'safety_concerns', 'is_submitted', 'submitted_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['job', 'submitted_at']


class JobPhotoSerializer(serializers.ModelSerializer):
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    uploaded_by_email = serializers.EmailField(source='uploaded_by.email', read_only=True)
    
    class Meta:
        model = JobPhoto
        fields = [
            'id', 'job', 'job_number', 'photo_type', 'file_path', 'file_url',
            'caption', 'uploaded_by', 'uploaded_by_email', 'created_at'
        ]
        read_only_fields = ['uploaded_by']


class JobQuoteSerializer(serializers.ModelSerializer):
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    
    class Meta:
        model = JobQuote
        fields = [
            'id', 'job', 'job_number', 'quote_id', 'gbb_total',
            'evaluation_fee', 'total_after_credit', 'line_items',
            'generated_by_ai', 'generation_context', 'created_at'
        ]
        read_only_fields = ['job', 'quote_id', 'generated_by_ai']


class JobCheckpointSerializer(serializers.ModelSerializer):
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    
    class Meta:
        model = JobCheckpoint
        fields = [
            'id', 'job', 'job_number', 'checkpoint_type', 'status',
            'scope_summary', 'progress_note', 'customer_note', 'rejection_reason',
            'customer_rating', 'customer_review', 'created_at', 'approved_at', 'rejected_at'
        ]
        read_only_fields = ['job', 'approved_at', 'rejected_at']


class JobProgressNoteSerializer(serializers.ModelSerializer):
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    added_by_email = serializers.EmailField(source='added_by.email', read_only=True)
    checkpoint_type = serializers.CharField(source='checkpoint.checkpoint_type', read_only=True)
    
    class Meta:
        model = JobProgressNote
        fields = [
            'id', 'job', 'job_number', 'note', 'added_by', 'added_by_email',
            'checkpoint', 'checkpoint_type', 'created_at'
        ]
        read_only_fields = ['added_by']


class JobChecklistSerializer(serializers.ModelSerializer):
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    
    class Meta:
        model = JobChecklist
        fields = [
            'id', 'job', 'job_number', 'items', 'completion_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['job', 'completion_percentage']


class MaterialSuggestionSerializer(serializers.ModelSerializer):
    job_number = serializers.CharField(source='job.job_number', read_only=True)
    
    class Meta:
        model = MaterialSuggestion
        fields = [
            'id', 'job', 'job_number', 'item_name', 'sku', 'vendor',
            'vendor_logo_url', 'price_range', 'suggested_qty', 'unit', 'product_url',
            'contractor_confirmed_qty', 'contractor_status', 'customer_material_source',
            'customer_liability_accepted', 'contractor_verified_customer_materials',
            'contractor_verification_note', 'created_at', 'updated_at'
        ]
        read_only_fields = ['job']


class ContractorJobSerializer(serializers.ModelSerializer):
    """Serializer for contractor job list and detail views"""
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    customer_info = serializers.SerializerMethodField()
    evaluation_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'workspace', 'workspace_name', 'job_number', 'title',
            'description', 'status', 'priority', 'customer_info',
            'location', 'customer_address', 'evaluation_status',
            'scheduled_evaluation_at', 'expected_start', 'expected_end',
            'evaluation_fee', 'evaluation_fee_credited', 'brand_name', 'powered_by',
            'created_at', 'updated_at'
        ]
    
    def get_customer_info(self, obj):
        return {
            'name': obj.customer_name,
            'email': obj.customer_email,
            'phone': obj.customer_phone,
            'address': obj.customer_address
        }
    
    def get_evaluation_status(self, obj):
        try:
            evaluation = obj.evaluation
            return {
                'exists': True,
                'submitted': evaluation.is_submitted,
                'submitted_at': evaluation.submitted_at
            }
        except JobEvaluation.DoesNotExist:
            return {
                'exists': False,
                'submitted': False,
                'submitted_at': None
            }


class CustomerJobSerializer(serializers.ModelSerializer):
    """Serializer for customer job views"""
    contractor_info = serializers.SerializerMethodField()
    tracking_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'job_number', 'title', 'description', 'status',
            'contractor_info', 'tracking_status', 'customer_address',
            'scheduled_evaluation_at', 'expected_start', 'expected_end',
            'brand_name', 'powered_by', 'created_at', 'updated_at'
        ]
    
    def get_contractor_info(self, obj):
        if obj.assigned_to:
            try:
                contractor = obj.assigned_to.contractor_profiles.first()
                return {
                    'name': obj.assigned_to.get_full_name() or obj.assigned_to.username,
                    'email': obj.assigned_to.email,
                    'company': contractor.company_name if contractor else None,
                    'phone': contractor.phone if contractor else None
                }
            except:
                return None
        return None
    
    def get_tracking_status(self, obj):
        try:
            tracking = obj.tracking
            return {
                'status': tracking.status,
                'estimated_arrival': tracking.estimated_arrival,
                'actual_arrival': tracking.actual_arrival,
                'last_update': tracking.updated_at
            }
        except JobTracking.DoesNotExist:
            return None


# ==================== AI Voice Agent Serializers ====================

class AIConversationSerializer(serializers.ModelSerializer):
    lead_number = serializers.CharField(source='lead.lead_number', read_only=True)
    customer_name = serializers.CharField(source='lead.customer_name', read_only=True)
    
    class Meta:
        model = AIConversation
        fields = [
            'id', 'lead', 'lead_number', 'customer_name', 'conversation_type',
            'status', 'phone_number', 'preferred_method', 'conversation_transcript',
            'ai_responses', 'customer_responses', 'appointment_scheduled',
            'scheduled_datetime', 'customer_qualified', 'qualification_score',
            'call_sid', 'recording_url', 'duration_seconds',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['lead', 'call_sid', 'recording_url', 'duration_seconds']


class TwilioIntegrationSerializer(serializers.ModelSerializer):
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    
    class Meta:
        model = TwilioIntegration
        fields = [
            'id', 'workspace', 'workspace_name', 'phone_number',
            'sms_enabled', 'voice_enabled', 'recording_enabled',
            'sms_webhook_url', 'voice_webhook_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['workspace', 'account_sid', 'auth_token']  # Hide sensitive data


class CommunicationLogSerializer(serializers.ModelSerializer):
    lead_number = serializers.CharField(source='lead.lead_number', read_only=True)
    customer_name = serializers.CharField(source='lead.customer_name', read_only=True)
    
    class Meta:
        model = CommunicationLog
        fields = [
            'id', 'workspace', 'lead', 'lead_number', 'customer_name',
            'ai_conversation', 'message_type', 'status', 'from_number',
            'to_number', 'message_body', 'twilio_sid', 'recording_url',
            'duration_seconds', 'cost', 'error_message', 'created_at'
        ]
        read_only_fields = ['workspace', 'twilio_sid', 'cost']
