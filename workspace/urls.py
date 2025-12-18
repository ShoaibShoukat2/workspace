from django.urls import path
from .views import (
    # Workspace
    WorkspaceListCreateView, WorkspaceDetailView, WorkspaceStatsView,
    # Workspace Members
    WorkspaceMemberListView, WorkspaceMemberDetailView,
    # Jobs
    JobListCreateView, JobDetailView, JobExportCSVView,
    # Estimates
    EstimateListCreateView, EstimateDetailView, EstimateExportCSVView,
    # Contractors
    ContractorListCreateView, ContractorDetailView, ContractorExportCSVView,
    # Payouts
    PayoutListCreateView, PayoutDetailView, PayoutExportCSVView,
    # Reports
    ReportListCreateView, ReportDetailView,
    # Compliance
    ComplianceListCreateView, ComplianceDetailView, ComplianceExportCSVView,
    ComplianceExpiringView
)

from .fm_views import (
    # FM Dashboard
    FMDashboardView, FMJobsByStatusView,
    # FM Jobs
    FMCreateJobView, FMJobDetailView, FMJobListView,
    # Job Attachments
    JobAttachmentCreateView, JobAttachmentListView, JobAttachmentDeleteView,
    # FM Estimates
    FMCreateEstimateView, FMEstimateDetailView, FMEstimateListView,
    # Estimate Line Items
    EstimateLineItemCreateView, EstimateLineItemUpdateView, EstimateLineItemListView,
    # Customer Signature
    CustomerSignEstimateView, GetEstimateForSigningView,
    # Estimate Actions
    SendEstimateView, RecalculateEstimateView
)

from .contractor_views import (
    # Contractor Dashboard
    ContractorDashboardView,
    # Job Assignments
    ContractorAssignmentsView, AcceptJobView, RejectJobView,
    # Active Jobs
    ContractorActiveJobsView, ContractorJobDetailView,
    # Checklist Management
    ChecklistStepUpdateView, UploadStepMediaView, StepMediaListView, DeleteStepMediaView,
    # Job Completion
    SubmitJobCompletionView, ContractorCompletedJobsView,
    # Notifications
    ContractorNotificationsView, MarkNotificationReadView, MarkAllNotificationsReadView,
    # Support
    ContractorSupportInfoView,
    # Admin/FM Views
    AssignJobToContractorView, VerifyJobCompletionView,
    CreateJobChecklistView, CreateChecklistStepView
)

from .payout_views import (
    # Admin Payout Management
    ReadyForPayoutJobsView, ApproveJobPayoutView, RejectJobPayoutView,
    BulkApprovePayoutsView, PayoutStatisticsView,
    # Contractor Wallet
    ContractorWalletView, WalletTransactionsView, DownloadWalletLedgerView,
    RequestPayoutView, ContractorPayoutRequestsView,
    # Admin Payout Requests
    AdminPayoutRequestsView, ApprovePayoutRequestView, RejectPayoutRequestView,
    # Reports
    DownloadPayoutReportView
)

from .compliance_views import (
    # Contractor Compliance Hub
    ContractorComplianceListView, ContractorUploadComplianceView, ContractorComplianceStatsView,
    # Admin Compliance Center
    AdminComplianceListView, ApproveComplianceView, RejectComplianceView, AdminComplianceStatsView,
    # Dispute Center
    CreateDisputeView, DisputeListView, DisputeDetailView,
    EscalateDisputeToFMView, EscalateDisputeToAdminView, ResolveDisputeView,
    AddDisputeMessageView, DisputeMessagesView,
    AddDisputeAttachmentView, DisputeAttachmentsView, DisputeStatisticsView
)

from .investor_views import (
    # Investor Dashboard
    InvestorDashboardView, RevenueStatisticsView, JobVolumeBreakdownView,
    ROIAnalyticsView, PayoutAnalyticsView,
    # Enhanced Investor Views
    InvestorActiveWorkOrdersView, InvestorEarningsBreakdownView,
    InvestorJobCategoriesView, InvestorPropertyPerformanceView,
    # Reports
    DownloadInvestorReportCSVView, DownloadDetailedJobReportCSVView,
    InvestorRecentActivityView
)

from .ai_views import (
    # AI Job Description
    AIGenerateJobDescriptionView, AIGenerateChecklistView,
    # Anomaly Detection
    DetectPricingAnomaliesView, DetectMissingJobItemsView,
    # Smart Recommendations
    SmartRecommendationsView, RecommendContractorView
)

from .pdf_views import (
    # PDF Generation
    GenerateEstimatePDFView, GenerateJobReportPDFView,
    GeneratePayoutSlipPDFView, GenerateComplianceCertificatePDFView,
    GenerateInvestorReportPDFView
)

from .customer_views import (
    # Customer Dashboard
    CustomerDashboardView, CustomerJobListView, CustomerJobDetailView,
    # Live GPS Tracking
    LiveContractorTrackingView, JobTrackingUpdatesView,
    # Customer Notifications
    CustomerNotificationsView, MarkNotificationReadView, MarkAllNotificationsReadView,
    # Material Reference Viewing
    JobMaterialReferencesView as CustomerJobMaterialReferencesView, 
    MaterialReferenceDetailView as CustomerMaterialReferenceDetailView,
    # Customer Profile
    CustomerProfileView, CustomerPreferencesView,
    # Issue Reporting
    ReportIssueView
)

from .support_views import (
    # Support Tickets
    CreateSupportTicketView, SupportTicketListView, SupportTicketDetailView,
    AddSupportMessageView,
    # Admin Support
    AdminSupportTicketsView, AdminSupportTicketDetailView, AdminAddSupportMessageView,
    SupportStatisticsView,
    # FAQ and Help
    SupportFAQView, SupportGuidedHelpView
)

from .tracking_views import (
    # GPS Tracking
    UpdateContractorLocationView, ContractorLocationHistoryView,
    # Job Tracking
    UpdateJobTrackingView, JobTrackingDetailView,
    # Admin Tracking
    AdminTrackingDashboardView, ContractorTrackingStatusView
)

from .angi_views import (
    # Angi OAuth
    AngiOAuthInitiateView, AngiOAuthCallbackView, AngiConnectionStatusView, DisconnectAngiView,
    # Lead Management
    LeadListCreateView, LeadDetailView, LeadActivitiesView, ConvertLeadToJobView,
    # Lead Scraping
    SyncAngiLeadsView, BulkImportAngiLeadsView, ManualLeadCreateView, LeadStatisticsView
)

from .price_intelligence_views import (
    # Price Intelligence
    PriceIntelligenceListView, MaterialPriceComparisonView, MaterialSearchView,
    # Price Scraping
    TriggerPriceScrapingView, AutoScrapingScheduleView,
    # Material References
    JobMaterialReferencesView, MaterialReferenceDetailView, UpdateMaterialPricingView,
    # Analytics
    PriceAnalyticsView
)

from .insurance_views import (
    # Insurance Verification
    InsuranceVerificationListView, ContractorInsuranceView, ApproveInsuranceView, RejectInsuranceView,
    # Compliance Dashboard
    InsuranceComplianceDashboardView, InsuranceExpiryNotificationsView
)

from .ai_voice_views import (
    # AI Voice Agent
    TriggerAIContactView, AIConversationListView, AIConversationDetailView,
    # Twilio Webhooks
    TwilioSMSWebhookView, TwilioVoiceWebhookView,
    # Twilio Integration
    TwilioIntegrationView, CommunicationLogView, AIPerformanceAnalyticsView
)

from .contractor_job_views import (
    # Contractor Job Management
    ContractorJobListView, ContractorJobDetailView,
    # Job Evaluation
    JobPhotoUploadView, JobEvaluationUpdateView, JobEvaluationSubmitView,
    # Materials
    JobMaterialSuggestionsView, JobMaterialVerificationView,
    # Progress Updates
    JobProgressPhotoUploadView, JobProgressNoteCreateView,
    # Completion
    JobChecklistView, JobChecklistUpdateView, JobCompleteWorkView,
    # Customer Material Verification
    ContractorVerifyCustomerMaterialsView
)

from .customer_job_views import (
    # Customer Job Timeline
    CustomerJobTimelineView,
    # Pre-Start Checkpoint
    CustomerPreStartCheckpointView, CustomerApprovePreStartView, CustomerRejectPreStartView,
    # Mid-Project Checkpoint
    CustomerMidProjectCheckpointView, CustomerApproveMidProjectView, CustomerRejectMidProjectView,
    # Final Checkpoint
    CustomerFinalCheckpointView, CustomerApproveFinalView, CustomerRejectFinalView,
    # Customer Materials
    CustomerJobMaterialsView, CustomerMaterialSourceView, CustomerMaterialPhotosView, CustomerMaterialLiabilityView
)

from .rag_pricing_views import (
    RAGPricingServiceView, RAGPricingAnalyticsView
)

from .material_scraper_views import (
    MaterialScraperServiceView, MaterialScraperStatusView, TriggerMaterialScrapeView
)

# Authentication views
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomAuthToken(ObtainAuthToken):
    """Custom authentication token view that returns user info"""
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        # Determine user type
        user_type = 'admin'  # default
        if hasattr(user, 'contractor_profiles') and user.contractor_profiles.exists():
            user_type = 'contractor'
        elif hasattr(user, 'customer_profile'):
            user_type = 'customer'
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'user_type': user_type
        })

class CurrentUserView(APIView):
    """Get current user information"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Determine user type
        user_type = 'admin'  # default
        if hasattr(user, 'contractor_profiles') and user.contractor_profiles.exists():
            user_type = 'contractor'
        elif hasattr(user, 'customer_profile'):
            user_type = 'customer'
        
        return Response({
            'user_id': user.pk,
            'email': user.email,
            'user_type': user_type,
            'first_name': user.first_name,
            'last_name': user.last_name
        })

app_name = 'workspace'

urlpatterns = [
    # ==================== Authentication ====================
    path('auth/login/', CustomAuthToken.as_view(), name='auth-login'),
    path('auth/user/', CurrentUserView.as_view(), name='current-user'),
    
    # Workspace Management
    path('', WorkspaceListCreateView.as_view(), name='workspace-list'),
    path('<uuid:workspace_id>/', WorkspaceDetailView.as_view(), name='workspace-detail'),
    path('<uuid:workspace_id>/stats/', WorkspaceStatsView.as_view(), name='workspace-stats'),
    
    # Workspace Members
    path('<uuid:workspace_id>/members/', WorkspaceMemberListView.as_view(), name='member-list'),
    path('members/<int:pk>/', WorkspaceMemberDetailView.as_view(), name='member-detail'),
    
    # Jobs
    path('<uuid:workspace_id>/jobs/', JobListCreateView.as_view(), name='job-list'),
    path('jobs/<int:pk>/', JobDetailView.as_view(), name='job-detail'),
    path('<uuid:workspace_id>/jobs/export/', JobExportCSVView.as_view(), name='job-export'),
    
    # Estimates
    path('<uuid:workspace_id>/estimates/', EstimateListCreateView.as_view(), name='estimate-list'),
    path('estimates/<int:pk>/', EstimateDetailView.as_view(), name='estimate-detail'),
    path('<uuid:workspace_id>/estimates/export/', EstimateExportCSVView.as_view(), name='estimate-export'),
    
    # Contractors
    path('<uuid:workspace_id>/contractors/', ContractorListCreateView.as_view(), name='contractor-list'),
    path('contractors/<int:pk>/', ContractorDetailView.as_view(), name='contractor-detail'),
    path('<uuid:workspace_id>/contractors/export/', ContractorExportCSVView.as_view(), name='contractor-export'),
    
    # Payouts
    path('<uuid:workspace_id>/payouts/', PayoutListCreateView.as_view(), name='payout-list'),
    path('payouts/<int:pk>/', PayoutDetailView.as_view(), name='payout-detail'),
    path('<uuid:workspace_id>/payouts/export/', PayoutExportCSVView.as_view(), name='payout-export'),
    
    # Reports
    path('<uuid:workspace_id>/reports/', ReportListCreateView.as_view(), name='report-list'),
    path('reports/<int:pk>/', ReportDetailView.as_view(), name='report-detail'),
    
    # Compliance
    path('<uuid:workspace_id>/compliance/', ComplianceListCreateView.as_view(), name='compliance-list'),
    path('compliance/<int:pk>/', ComplianceDetailView.as_view(), name='compliance-detail'),
    path('<uuid:workspace_id>/compliance/export/', ComplianceExportCSVView.as_view(), name='compliance-export'),
    path('<uuid:workspace_id>/compliance/expiring/', ComplianceExpiringView.as_view(), name='compliance-expiring'),
    
    # ==================== FM Module ====================
    
    # FM Dashboard
    path('fm/dashboard/', FMDashboardView.as_view(), name='fm-dashboard'),
    path('fm/jobs/status/<str:status>/', FMJobsByStatusView.as_view(), name='fm-jobs-by-status'),
    
    # FM Job Management
    path('fm/jobs/', FMJobListView.as_view(), name='fm-job-list'),
    path('fm/jobs/create/', FMCreateJobView.as_view(), name='fm-job-create'),
    path('fm/jobs/<int:pk>/', FMJobDetailView.as_view(), name='fm-job-detail'),
    
    # Job Attachments
    path('fm/jobs/attachments/', JobAttachmentCreateView.as_view(), name='job-attachment-create'),
    path('fm/jobs/<int:job_id>/attachments/', JobAttachmentListView.as_view(), name='job-attachment-list'),
    path('fm/jobs/attachments/<int:pk>/', JobAttachmentDeleteView.as_view(), name='job-attachment-delete'),
    
    # FM Estimate Management
    path('fm/estimates/', FMEstimateListView.as_view(), name='fm-estimate-list'),
    path('fm/estimates/create/', FMCreateEstimateView.as_view(), name='fm-estimate-create'),
    path('fm/estimates/<int:pk>/', FMEstimateDetailView.as_view(), name='fm-estimate-detail'),
    
    # Estimate Line Items
    path('fm/estimates/line-items/', EstimateLineItemCreateView.as_view(), name='estimate-line-item-create'),
    path('fm/estimates/<int:estimate_id>/line-items/', EstimateLineItemListView.as_view(), name='estimate-line-item-list'),
    path('fm/estimates/line-items/<int:pk>/', EstimateLineItemUpdateView.as_view(), name='estimate-line-item-update'),
    
    # Estimate Actions
    path('fm/estimates/<int:estimate_id>/send/', SendEstimateView.as_view(), name='estimate-send'),
    path('fm/estimates/<int:estimate_id>/recalculate/', RecalculateEstimateView.as_view(), name='estimate-recalculate'),
    
    # Customer Signature (Public)
    path('public/estimates/<str:estimate_number>/', GetEstimateForSigningView.as_view(), name='estimate-public-view'),
    path('public/estimates/<int:estimate_id>/sign/', CustomerSignEstimateView.as_view(), name='estimate-sign'),
    
    # ==================== Contractor Module ====================
    
    # Contractor Dashboard
    path('contractor/dashboard/', ContractorDashboardView.as_view(), name='contractor-dashboard'),
    
    # Job Assignments
    path('contractor/assignments/', ContractorAssignmentsView.as_view(), name='contractor-assignments'),
    path('contractor/assignments/<int:assignment_id>/accept/', AcceptJobView.as_view(), name='accept-job'),
    path('contractor/assignments/<int:assignment_id>/reject/', RejectJobView.as_view(), name='reject-job'),
    
    # Active Jobs
    path('contractor/jobs/active/', ContractorActiveJobsView.as_view(), name='contractor-active-jobs'),
    path('contractor/jobs/<int:pk>/', ContractorJobDetailView.as_view(), name='contractor-job-detail'),
    
    # Checklist Management
    path('contractor/steps/<int:step_id>/', ChecklistStepUpdateView.as_view(), name='update-checklist-step'),
    path('contractor/steps/media/', UploadStepMediaView.as_view(), name='upload-step-media'),
    path('contractor/steps/<int:step_id>/media/', StepMediaListView.as_view(), name='step-media-list'),
    path('contractor/steps/media/<int:pk>/', DeleteStepMediaView.as_view(), name='delete-step-media'),
    
    # Job Completion
    path('contractor/jobs/<int:job_id>/complete/', SubmitJobCompletionView.as_view(), name='submit-job-completion'),
    path('contractor/completed-jobs/', ContractorCompletedJobsView.as_view(), name='contractor-completed-jobs'),
    
    # Notifications
    path('contractor/notifications/', ContractorNotificationsView.as_view(), name='contractor-notifications'),
    path('contractor/notifications/<int:notification_id>/read/', MarkNotificationReadView.as_view(), name='mark-notification-read'),
    path('contractor/notifications/read-all/', MarkAllNotificationsReadView.as_view(), name='mark-all-notifications-read'),
    
    # Contractor Support
    path('contractor/support/info/', ContractorSupportInfoView.as_view(), name='contractor-support-info'),
    
    # Admin/FM - Contractor Management
    path('admin/assign-job/', AssignJobToContractorView.as_view(), name='assign-job-to-contractor'),
    path('admin/verify-completion/<int:completion_id>/', VerifyJobCompletionView.as_view(), name='verify-job-completion'),
    path('admin/checklists/create/', CreateJobChecklistView.as_view(), name='create-job-checklist'),
    path('admin/checklist-steps/create/', CreateChecklistStepView.as_view(), name='create-checklist-step'),
    
    # ==================== Payout & Financial Flow ====================
    
    # Admin Payout Management
    path('admin/payouts/ready/', ReadyForPayoutJobsView.as_view(), name='ready-for-payout'),
    path('admin/payouts/<int:eligibility_id>/approve/', ApproveJobPayoutView.as_view(), name='approve-job-payout'),
    path('admin/payouts/<int:eligibility_id>/reject/', RejectJobPayoutView.as_view(), name='reject-job-payout'),
    path('admin/payouts/bulk-approve/', BulkApprovePayoutsView.as_view(), name='bulk-approve-payouts'),
    path('admin/payouts/statistics/', PayoutStatisticsView.as_view(), name='payout-statistics'),
    
    # Admin Payout Requests
    path('admin/payout-requests/', AdminPayoutRequestsView.as_view(), name='admin-payout-requests'),
    path('admin/payout-requests/<int:request_id>/approve/', ApprovePayoutRequestView.as_view(), name='approve-payout-request'),
    path('admin/payout-requests/<int:request_id>/reject/', RejectPayoutRequestView.as_view(), name='reject-payout-request'),
    
    # Reports
    path('admin/payouts/report/download/', DownloadPayoutReportView.as_view(), name='download-payout-report'),
    
    # Contractor Wallet
    path('contractor/wallet/', ContractorWalletView.as_view(), name='contractor-wallet'),
    path('contractor/wallet/transactions/', WalletTransactionsView.as_view(), name='wallet-transactions'),
    path('contractor/wallet/ledger/download/', DownloadWalletLedgerView.as_view(), name='download-wallet-ledger'),
    path('contractor/wallet/request-payout/', RequestPayoutView.as_view(), name='request-payout'),
    path('contractor/payout-requests/', ContractorPayoutRequestsView.as_view(), name='contractor-payout-requests'),
    
    # ==================== Compliance & Disputes System ====================
    
    # Contractor Compliance Hub
    path('contractor/compliance/', ContractorComplianceListView.as_view(), name='contractor-compliance-list'),
    path('contractor/compliance/upload/', ContractorUploadComplianceView.as_view(), name='contractor-upload-compliance'),
    path('contractor/compliance/stats/', ContractorComplianceStatsView.as_view(), name='contractor-compliance-stats'),
    
    # Admin Compliance Center
    path('admin/compliance/', AdminComplianceListView.as_view(), name='admin-compliance-list'),
    path('admin/compliance/<int:compliance_id>/approve/', ApproveComplianceView.as_view(), name='approve-compliance'),
    path('admin/compliance/<int:compliance_id>/reject/', RejectComplianceView.as_view(), name='reject-compliance'),
    path('admin/compliance/stats/', AdminComplianceStatsView.as_view(), name='admin-compliance-stats'),
    
    # Dispute Center
    path('disputes/create/', CreateDisputeView.as_view(), name='create-dispute'),
    path('disputes/', DisputeListView.as_view(), name='dispute-list'),
    path('disputes/<int:pk>/', DisputeDetailView.as_view(), name='dispute-detail'),
    path('disputes/<int:dispute_id>/escalate-to-fm/', EscalateDisputeToFMView.as_view(), name='escalate-dispute-to-fm'),
    path('disputes/<int:dispute_id>/escalate-to-admin/', EscalateDisputeToAdminView.as_view(), name='escalate-dispute-to-admin'),
    path('disputes/<int:dispute_id>/resolve/', ResolveDisputeView.as_view(), name='resolve-dispute'),
    path('disputes/messages/', AddDisputeMessageView.as_view(), name='add-dispute-message'),
    path('disputes/<int:dispute_id>/messages/', DisputeMessagesView.as_view(), name='dispute-messages'),
    path('disputes/attachments/', AddDisputeAttachmentView.as_view(), name='add-dispute-attachment'),
    path('disputes/<int:dispute_id>/attachments/', DisputeAttachmentsView.as_view(), name='dispute-attachments'),
    path('admin/disputes/stats/', DisputeStatisticsView.as_view(), name='dispute-statistics'),
    
    # ==================== Investor Module ====================
    
    # Investor Dashboard
    path('investor/dashboard/', InvestorDashboardView.as_view(), name='investor-dashboard'),
    path('investor/revenue-statistics/', RevenueStatisticsView.as_view(), name='revenue-statistics'),
    path('investor/job-volume/', JobVolumeBreakdownView.as_view(), name='job-volume-breakdown'),
    path('investor/roi-analytics/', ROIAnalyticsView.as_view(), name='roi-analytics'),
    path('investor/payout-analytics/', PayoutAnalyticsView.as_view(), name='payout-analytics'),
    path('investor/recent-activity/', InvestorRecentActivityView.as_view(), name='investor-recent-activity'),
    
    # Enhanced Investor Features
    path('investor/active-work-orders/', InvestorActiveWorkOrdersView.as_view(), name='investor-active-work-orders'),
    path('investor/earnings-breakdown/', InvestorEarningsBreakdownView.as_view(), name='investor-earnings-breakdown'),
    path('investor/job-categories/', InvestorJobCategoriesView.as_view(), name='investor-job-categories'),
    path('investor/property-performance/', InvestorPropertyPerformanceView.as_view(), name='investor-property-performance'),
    
    # Investor Reports
    path('investor/reports/download/', DownloadInvestorReportCSVView.as_view(), name='download-investor-report'),
    path('investor/reports/jobs/download/', DownloadDetailedJobReportCSVView.as_view(), name='download-detailed-job-report'),
    
    # ==================== AI-Assisted Features ====================
    
    # AI Job Description & Checklist
    path('ai/generate-job-description/', AIGenerateJobDescriptionView.as_view(), name='ai-generate-job-description'),
    path('ai/generate-checklist/', AIGenerateChecklistView.as_view(), name='ai-generate-checklist'),
    
    # Anomaly Detection
    path('ai/detect-pricing-anomalies/', DetectPricingAnomaliesView.as_view(), name='detect-pricing-anomalies'),
    path('ai/detect-missing-items/', DetectMissingJobItemsView.as_view(), name='detect-missing-items'),
    
    # Smart Recommendations
    path('ai/smart-recommendations/', SmartRecommendationsView.as_view(), name='smart-recommendations'),
    path('ai/recommend-contractor/', RecommendContractorView.as_view(), name='recommend-contractor'),
    
    # ==================== PDF Generation ====================
    
    # Estimate PDF
    path('pdf/estimate/<int:estimate_id>/', GenerateEstimatePDFView.as_view(), name='generate-estimate-pdf'),
    
    # Job Report PDF
    path('pdf/job-report/<int:job_id>/', GenerateJobReportPDFView.as_view(), name='generate-job-report-pdf'),
    
    # Payout Slip PDF
    path('pdf/payout-slip/<int:payout_id>/', GeneratePayoutSlipPDFView.as_view(), name='generate-payout-slip-pdf'),
    
    # Compliance Certificate PDF
    path('pdf/compliance-certificate/<int:compliance_id>/', GenerateComplianceCertificatePDFView.as_view(), name='generate-compliance-certificate-pdf'),
    
    # Investor Report PDF
    path('pdf/investor-report/', GenerateInvestorReportPDFView.as_view(), name='generate-investor-report-pdf'),
    
    # ==================== Customer Dashboard & GPS Tracking ====================
    
    # Customer Dashboard
    path('customer/dashboard/', CustomerDashboardView.as_view(), name='customer-dashboard'),
    path('customer/jobs/', CustomerJobListView.as_view(), name='customer-job-list'),
    path('customer/jobs/<int:job_id>/', CustomerJobDetailView.as_view(), name='customer-job-detail'),
    
    # Live GPS Tracking
    path('customer/jobs/<int:job_id>/tracking/', LiveContractorTrackingView.as_view(), name='live-contractor-tracking'),
    path('customer/jobs/<int:job_id>/tracking/updates/', JobTrackingUpdatesView.as_view(), name='job-tracking-updates'),
    
    # Customer Notifications
    path('customer/notifications/', CustomerNotificationsView.as_view(), name='customer-notifications'),
    path('customer/notifications/<int:notification_id>/read/', MarkNotificationReadView.as_view(), name='mark-customer-notification-read'),
    path('customer/notifications/read-all/', MarkAllNotificationsReadView.as_view(), name='mark-all-customer-notifications-read'),
    
    # Material Reference Viewing (Read-Only)
    path('customer/jobs/<int:job_id>/materials/', CustomerJobMaterialReferencesView.as_view(), name='customer-job-material-references'),
    path('customer/materials/<int:reference_id>/', CustomerMaterialReferenceDetailView.as_view(), name='customer-material-reference-detail'),
    
    # Customer Profile
    path('customer/profile/', CustomerProfileView.as_view(), name='customer-profile'),
    path('customer/preferences/', CustomerPreferencesView.as_view(), name='customer-preferences'),
    
    # Issue Reporting
    path('customer/jobs/<int:job_id>/report-issue/', ReportIssueView.as_view(), name='report-issue'),
    
    # ==================== Support System ====================
    
    # Support Tickets
    path('support/tickets/create/', CreateSupportTicketView.as_view(), name='create-support-ticket'),
    path('support/tickets/', SupportTicketListView.as_view(), name='support-ticket-list'),
    path('support/tickets/<str:ticket_number>/', SupportTicketDetailView.as_view(), name='support-ticket-detail'),
    path('support/tickets/<str:ticket_number>/messages/', AddSupportMessageView.as_view(), name='add-support-message'),
    
    # Admin Support Management
    path('admin/support/tickets/', AdminSupportTicketsView.as_view(), name='admin-support-tickets'),
    path('admin/support/tickets/<str:ticket_number>/', AdminSupportTicketDetailView.as_view(), name='admin-support-ticket-detail'),
    path('admin/support/tickets/<str:ticket_number>/messages/', AdminAddSupportMessageView.as_view(), name='admin-add-support-message'),
    path('admin/support/statistics/', SupportStatisticsView.as_view(), name='support-statistics'),
    
    # FAQ and Automated Support
    path('support/faq/', SupportFAQView.as_view(), name='support-faq'),
    path('support/guided-help/', SupportGuidedHelpView.as_view(), name='support-guided-help'),
    
    # ==================== GPS Tracking & Job Tracking ====================
    
    # Contractor GPS Tracking
    path('contractor/location/update/', UpdateContractorLocationView.as_view(), name='update-contractor-location'),
    path('contractor/<int:contractor_id>/location-history/', ContractorLocationHistoryView.as_view(), name='contractor-location-history'),
    
    # Job Tracking Management
    path('jobs/<int:job_id>/tracking/update/', UpdateJobTrackingView.as_view(), name='update-job-tracking'),
    path('jobs/<int:job_id>/tracking/', JobTrackingDetailView.as_view(), name='job-tracking-detail'),
    
    # Admin Tracking Dashboard
    path('admin/tracking/dashboard/', AdminTrackingDashboardView.as_view(), name='admin-tracking-dashboard'),
    path('admin/tracking/contractors/', ContractorTrackingStatusView.as_view(), name='contractor-tracking-status'),
    
    # ==================== Angi Integration & Lead Management ====================
    
    # Angi OAuth Integration
    path('angi/oauth/initiate/', AngiOAuthInitiateView.as_view(), name='angi-oauth-initiate'),
    path('angi/oauth/callback/', AngiOAuthCallbackView.as_view(), name='angi-oauth-callback'),
    path('angi/connection/status/', AngiConnectionStatusView.as_view(), name='angi-connection-status'),
    path('angi/disconnect/', DisconnectAngiView.as_view(), name='disconnect-angi'),
    
    # Lead Management
    path('leads/', LeadListCreateView.as_view(), name='lead-list-create'),
    path('leads/<int:pk>/', LeadDetailView.as_view(), name='lead-detail'),
    path('leads/<int:lead_id>/activities/', LeadActivitiesView.as_view(), name='lead-activities'),
    path('leads/<int:lead_id>/convert/', ConvertLeadToJobView.as_view(), name='convert-lead-to-job'),
    
    # Angi Lead Scraping
    path('angi/sync-leads/', SyncAngiLeadsView.as_view(), name='sync-angi-leads'),
    path('angi/bulk-import/', BulkImportAngiLeadsView.as_view(), name='bulk-import-angi-leads'),
    path('leads/create-manual/', ManualLeadCreateView.as_view(), name='manual-lead-create'),
    path('leads/statistics/', LeadStatisticsView.as_view(), name='lead-statistics'),
    
    # ==================== Price Intelligence System ====================
    
    # Price Intelligence
    path('price-intelligence/', PriceIntelligenceListView.as_view(), name='price-intelligence-list'),
    path('price-intelligence/compare/', MaterialPriceComparisonView.as_view(), name='material-price-comparison'),
    path('price-intelligence/search/', MaterialSearchView.as_view(), name='material-search'),
    
    # Price Scraping
    path('price-intelligence/scrape/', TriggerPriceScrapingView.as_view(), name='trigger-price-scraping'),
    path('price-intelligence/auto-scrape/', AutoScrapingScheduleView.as_view(), name='auto-scraping-schedule'),
    
    # Material References for Jobs
    path('jobs/<int:job_id>/materials/', JobMaterialReferencesView.as_view(), name='job-material-references'),
    path('materials/<int:pk>/', MaterialReferenceDetailView.as_view(), name='material-reference-detail'),
    path('materials/<int:material_ref_id>/update-pricing/', UpdateMaterialPricingView.as_view(), name='update-material-pricing'),
    
    # Price Analytics
    path('price-intelligence/analytics/', PriceAnalyticsView.as_view(), name='price-analytics'),
    
    # ==================== Insurance Verification System ====================
    
    # Insurance Verification
    path('insurance/verifications/', InsuranceVerificationListView.as_view(), name='insurance-verification-list'),
    path('contractors/<int:contractor_id>/insurance/', ContractorInsuranceView.as_view(), name='contractor-insurance'),
    path('insurance/<int:insurance_id>/approve/', ApproveInsuranceView.as_view(), name='approve-insurance'),
    path('insurance/<int:insurance_id>/reject/', RejectInsuranceView.as_view(), name='reject-insurance'),
    
    # Insurance Compliance Dashboard
    path('admin/insurance/dashboard/', InsuranceComplianceDashboardView.as_view(), name='insurance-compliance-dashboard'),
    path('admin/insurance/expiry-notifications/', InsuranceExpiryNotificationsView.as_view(), name='insurance-expiry-notifications'),
    
    # ==================== AI Voice Agent System ====================
    
    # AI Voice Agent
    path('ai/contact-lead/<int:lead_id>/', TriggerAIContactView.as_view(), name='trigger-ai-contact'),
    path('ai/conversations/', AIConversationListView.as_view(), name='ai-conversation-list'),
    path('ai/conversations/<int:pk>/', AIConversationDetailView.as_view(), name='ai-conversation-detail'),
    
    # Twilio Webhooks (Public)
    path('webhooks/twilio/sms/', TwilioSMSWebhookView.as_view(), name='twilio-sms-webhook'),
    path('webhooks/twilio/voice/', TwilioVoiceWebhookView.as_view(), name='twilio-voice-webhook'),
    
    # Twilio Integration Management
    path('admin/twilio/integration/', TwilioIntegrationView.as_view(), name='twilio-integration'),
    path('admin/communications/', CommunicationLogView.as_view(), name='communication-log'),
    path('admin/ai/analytics/', AIPerformanceAnalyticsView.as_view(), name='ai-performance-analytics'),
    
    # ==================== Job Workflow API Endpoints ====================
    
    # Contractor App - Job Management (B1-B13, B29)
    path('contractor/jobs/', ContractorJobListView.as_view(), name='contractor-job-list'),  # B1
    path('contractor/jobs/<int:job_id>/', ContractorJobDetailView.as_view(), name='contractor-job-detail'),  # B2
    path('contractor/jobs/<int:job_id>/photos/upload/', JobPhotoUploadView.as_view(), name='job-photo-upload'),  # B3
    path('contractor/jobs/<int:job_id>/evaluation/', JobEvaluationUpdateView.as_view(), name='job-evaluation-update'),  # B4
    path('contractor/jobs/<int:job_id>/evaluation/submit/', JobEvaluationSubmitView.as_view(), name='job-evaluation-submit'),  # B5
    path('contractor/jobs/<int:job_id>/materials/', JobMaterialSuggestionsView.as_view(), name='job-material-suggestions'),  # B6
    path('contractor/jobs/<int:job_id>/materials/verify/', JobMaterialVerificationView.as_view(), name='job-material-verification'),  # B7
    path('contractor/jobs/<int:job_id>/progress/photos/', JobProgressPhotoUploadView.as_view(), name='job-progress-photo-upload'),  # B8
    path('contractor/jobs/<int:job_id>/progress/notes/', JobProgressNoteCreateView.as_view(), name='job-progress-note-create'),  # B9
    path('contractor/jobs/<int:job_id>/checklist/', JobChecklistView.as_view(), name='job-checklist'),  # B10
    path('contractor/jobs/<int:job_id>/checklist/update/', JobChecklistUpdateView.as_view(), name='job-checklist-update'),  # B11
    # B12 - Mid-project checkpoint (handled by customer workflow)
    path('contractor/jobs/<int:job_id>/complete/', JobCompleteWorkView.as_view(), name='job-complete-work'),  # B13
    path('contractor/jobs/<int:job_id>/materials/verify-customer/', ContractorVerifyCustomerMaterialsView.as_view(), name='contractor-verify-customer-materials'),  # B29
    
    # Customer App - Job Experience (C1-C14)
    path('customer/jobs/<int:job_id>/timeline/', CustomerJobTimelineView.as_view(), name='customer-job-timeline'),  # C1
    path('customer/jobs/<int:job_id>/pre-start/', CustomerPreStartCheckpointView.as_view(), name='customer-pre-start-checkpoint'),  # C2
    path('customer/jobs/<int:job_id>/pre-start/approve/', CustomerApprovePreStartView.as_view(), name='customer-approve-pre-start'),  # C3
    path('customer/jobs/<int:job_id>/pre-start/reject/', CustomerRejectPreStartView.as_view(), name='customer-reject-pre-start'),  # C4
    path('customer/jobs/<int:job_id>/mid-project/', CustomerMidProjectCheckpointView.as_view(), name='customer-mid-project-checkpoint'),  # C5
    path('customer/jobs/<int:job_id>/mid-project/approve/', CustomerApproveMidProjectView.as_view(), name='customer-approve-mid-project'),  # C6
    path('customer/jobs/<int:job_id>/mid-project/reject/', CustomerRejectMidProjectView.as_view(), name='customer-reject-mid-project'),  # C7
    path('customer/jobs/<int:job_id>/final/', CustomerFinalCheckpointView.as_view(), name='customer-final-checkpoint'),  # C8
    path('customer/jobs/<int:job_id>/final/approve/', CustomerApproveFinalView.as_view(), name='customer-approve-final'),  # C9
    path('customer/jobs/<int:job_id>/final/reject/', CustomerRejectFinalView.as_view(), name='customer-reject-final'),  # C10
    path('customer/jobs/<int:job_id>/materials/', CustomerJobMaterialsView.as_view(), name='customer-job-materials'),  # C11
    path('customer/jobs/<int:job_id>/materials/source/', CustomerMaterialSourceView.as_view(), name='customer-material-source'),  # C12
    path('customer/jobs/<int:job_id>/materials/photos/', CustomerMaterialPhotosView.as_view(), name='customer-material-photos'),  # C13
    path('customer/jobs/<int:job_id>/materials/liability/', CustomerMaterialLiabilityView.as_view(), name='customer-material-liability'),  # C14
    
    # ==================== RAG Pricing & Material Scraper Services ====================
    
    # RAG Pricing Service (Endpoint 30)
    path('services/rag-pricing/<int:job_id>/', RAGPricingServiceView.as_view(), name='rag-pricing-service'),  # 30
    path('services/rag-pricing/analytics/', RAGPricingAnalyticsView.as_view(), name='rag-pricing-analytics'),
    
    # Material Scraper Service (Endpoint 31)
    path('services/material-scraper/<int:job_id>/', MaterialScraperServiceView.as_view(), name='material-scraper-service'),  # 31
    path('services/material-scraper/status/', MaterialScraperStatusView.as_view(), name='material-scraper-status'),
    path('services/material-scraper/trigger/', TriggerMaterialScrapeView.as_view(), name='trigger-material-scrape'),
]
