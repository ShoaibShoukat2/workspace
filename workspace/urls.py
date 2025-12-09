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

app_name = 'workspace'

urlpatterns = [
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
]
