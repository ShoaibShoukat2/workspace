"""
Admin Management Schemas
"""
from pydantic import BaseModel, Field, UUID4
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class ReportType(str, Enum):
    JOBS = "JOBS"
    ESTIMATES = "ESTIMATES"
    CONTRACTORS = "CONTRACTORS"
    PAYOUTS = "PAYOUTS"
    COMPLIANCE = "COMPLIANCE"
    FINANCIAL = "FINANCIAL"


class LeadSource(str, Enum):
    ANGI = "ANGI"
    MANUAL = "MANUAL"
    WEBSITE = "WEBSITE"
    REFERRAL = "REFERRAL"
    OTHER = "OTHER"


class LeadStatus(str, Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    APPOINTMENT_SCHEDULED = "APPOINTMENT_SCHEDULED"
    CONVERTED = "CONVERTED"
    LOST = "LOST"


class ComplianceAction(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REQUEST_UPDATE = "REQUEST_UPDATE"
    SUSPEND = "SUSPEND"
    ACTIVATE = "ACTIVATE"


# Admin Dashboard Response
class AdminDashboardResponse(BaseModel):
    total_workspaces: int
    total_jobs: int
    active_jobs: int
    completed_jobs: int
    total_contractors: int
    active_contractors: int
    total_customers: int
    total_revenue: Decimal
    monthly_revenue: Decimal
    pending_payouts: Decimal
    compliance_issues: int
    system_health: str
    recent_activities: List[Dict[str, Any]]
    revenue_trend: List[Dict[str, Any]]
    job_status_distribution: Dict[str, int]
    contractor_performance_summary: Dict[str, Any]


# Admin Job Response
class AdminJobResponse(BaseModel):
    id: int
    workspace_id: UUID4
    job_number: str
    title: str
    description: str
    status: str
    priority: str
    assigned_to_id: Optional[int] = None
    created_by_id: Optional[int] = None
    estimated_cost: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    completed_date: Optional[date] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    workspace_name: Optional[str] = None
    assigned_to_name: Optional[str] = None
    created_by_name: Optional[str] = None
    contractor_company: Optional[str] = None
    
    # Admin-specific data
    profit_margin: Optional[Decimal] = None
    customer_satisfaction: Optional[float] = None
    compliance_status: Optional[str] = None
    
    class Config:
        from_attributes = True


# Admin Lead Response
class AdminLeadResponse(BaseModel):
    id: int
    workspace_id: UUID4
    lead_number: str
    source: LeadSource
    status: LeadStatus
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    service_type: str
    location: str
    description: str
    angi_lead_id: Optional[str] = None
    ai_contacted: bool
    ai_contact_preference: Optional[str] = None
    converted_job_id: Optional[int] = None
    created_by_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    created_by_name: Optional[str] = None
    assigned_to_name: Optional[str] = None
    converted_job_number: Optional[str] = None
    
    # Admin-specific data
    lead_score: Optional[int] = None
    estimated_value: Optional[Decimal] = None
    conversion_probability: Optional[float] = None
    
    class Config:
        from_attributes = True


# Lead Create
class LeadCreate(BaseModel):
    workspace_id: UUID4
    source: LeadSource = LeadSource.MANUAL
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_phone: str = Field(..., min_length=1, max_length=20)
    customer_email: Optional[str] = None
    service_type: str = Field(..., min_length=1, max_length=255)
    location: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    assigned_to_id: Optional[int] = None
    estimated_value: Optional[Decimal] = None
    notes: Optional[str] = None


# Admin Compliance Response
class AdminComplianceResponse(BaseModel):
    id: int
    workspace_id: UUID4
    contractor_id: int
    compliance_type: str
    document_name: str
    document_number: Optional[str] = None
    status: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    verified_by_id: Optional[int] = None
    verified_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    contractor_name: Optional[str] = None
    contractor_company: Optional[str] = None
    contractor_email: Optional[str] = None
    verified_by_name: Optional[str] = None
    workspace_name: Optional[str] = None
    
    # Admin-specific data
    days_until_expiry: Optional[int] = None
    risk_level: Optional[str] = None
    
    class Config:
        from_attributes = True


# Compliance Action Request
class ComplianceActionRequest(BaseModel):
    action: ComplianceAction
    notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    suspension_duration: Optional[int] = None  # days


# Admin Payout Response
class AdminPayoutResponse(BaseModel):
    id: int
    workspace_id: UUID4
    contractor_id: int
    job_id: Optional[int] = None
    payout_number: str
    amount: Decimal
    status: str
    payment_method: str
    description: Optional[str] = None
    scheduled_date: Optional[date] = None
    paid_date: Optional[date] = None
    processed_by_id: Optional[int] = None
    transaction_reference: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    contractor_name: Optional[str] = None
    contractor_company: Optional[str] = None
    contractor_email: Optional[str] = None
    job_number: Optional[str] = None
    workspace_name: Optional[str] = None
    processed_by_name: Optional[str] = None
    
    # Admin-specific data
    approval_required: bool = False
    risk_flags: List[str] = []
    
    class Config:
        from_attributes = True


# Admin Report Response
class AdminReportResponse(BaseModel):
    id: int
    workspace_id: UUID4
    report_type: ReportType
    title: str
    description: Optional[str] = None
    generated_by_id: Optional[int] = None
    file_path: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    created_at: datetime
    
    # Related data
    workspace_name: Optional[str] = None
    generated_by_name: Optional[str] = None
    
    # Report metadata
    file_size: Optional[int] = None
    download_count: int = 0
    status: str = "COMPLETED"  # PROCESSING, COMPLETED, FAILED
    
    class Config:
        from_attributes = True


# Analytics Responses
class RevenueAnalyticsResponse(BaseModel):
    period: str
    total_revenue: Decimal
    job_revenue: Decimal
    estimate_revenue: Decimal
    recurring_revenue: Decimal
    growth_rate: float
    data_points: List[Dict[str, Any]]


class PerformanceAnalyticsResponse(BaseModel):
    total_jobs: int
    completed_jobs: int
    cancelled_jobs: int
    average_completion_time: float  # days
    customer_satisfaction_avg: float
    contractor_utilization: float
    revenue_per_job: Decimal
    profit_margin: float
    performance_trends: List[Dict[str, Any]]


class SystemHealthResponse(BaseModel):
    overall_status: str  # HEALTHY, WARNING, CRITICAL
    database_status: str
    cache_status: str
    api_response_time: float  # milliseconds
    error_rate: float  # percentage
    active_users: int
    system_load: float
    disk_usage: float  # percentage
    memory_usage: float  # percentage
    uptime: int  # seconds
    last_backup: Optional[datetime] = None
    alerts: List[Dict[str, Any]]


# System Log Response
class SystemLogResponse(BaseModel):
    id: int
    timestamp: datetime
    level: str  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    logger: str
    message: str
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    request_id: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


# Investor Accounting Response
class InvestorAccountingResponse(BaseModel):
    period_start: date
    period_end: date
    total_revenue: Decimal
    total_expenses: Decimal
    gross_profit: Decimal
    net_profit: Decimal
    investor_share: Decimal
    apex_share: Decimal
    outstanding_payouts: Decimal
    investor_breakdown: List[Dict[str, Any]]
    expense_breakdown: List[Dict[str, Any]]
    profit_trends: List[Dict[str, Any]]


# Ledger Entry Response
class LedgerEntryResponse(BaseModel):
    id: int
    transaction_date: datetime
    transaction_type: str  # REVENUE, EXPENSE, PAYOUT, REFUND
    category: str
    description: str
    amount: Decimal
    balance_after: Decimal
    reference_type: Optional[str] = None  # JOB, PAYOUT, EXPENSE
    reference_id: Optional[int] = None
    workspace_id: Optional[UUID4] = None
    contractor_id: Optional[int] = None
    created_by_id: Optional[int] = None
    created_at: datetime
    
    # Related data
    workspace_name: Optional[str] = None
    contractor_name: Optional[str] = None
    created_by_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# Bulk Operations
class BulkJobUpdateRequest(BaseModel):
    job_ids: List[int]
    updates: Dict[str, Any]
    reason: Optional[str] = None


class BulkContractorActionRequest(BaseModel):
    contractor_ids: List[int]
    action: str  # ACTIVATE, SUSPEND, APPROVE
    reason: Optional[str] = None
    duration: Optional[int] = None  # for suspensions


class BulkPayoutApprovalRequest(BaseModel):
    payout_ids: List[int]
    notes: Optional[str] = None