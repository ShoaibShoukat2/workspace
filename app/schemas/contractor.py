"""
Contractor Management Schemas
"""
from pydantic import BaseModel, Field, UUID4
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class ContractorStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class AssignmentStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class PayoutStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, Enum):
    BANK_TRANSFER = "BANK_TRANSFER"
    CHECK = "CHECK"
    CASH = "CASH"
    PAYPAL = "PAYPAL"
    OTHER = "OTHER"


class ComplianceType(str, Enum):
    ID = "ID"
    LICENSE = "LICENSE"
    INSURANCE = "INSURANCE"
    CERTIFICATION = "CERTIFICATION"
    CONTRACT = "CONTRACT"
    SAFETY = "SAFETY"
    OTHER = "OTHER"


class ComplianceStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    EXPIRING_SOON = "EXPIRING_SOON"


# Base Contractor Schema
class ContractorBase(BaseModel):
    company_name: Optional[str] = Field(None, max_length=255)
    license_number: Optional[str] = Field(None, max_length=100)
    specialization: Optional[str] = Field(None, max_length=255)
    hourly_rate: Optional[Decimal] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    notes: Optional[str] = None


# Contractor Creation
class ContractorCreate(ContractorBase):
    workspace_id: UUID4
    user_id: Optional[int] = None  # If creating for existing user


# Contractor Update
class ContractorUpdate(ContractorBase):
    status: Optional[ContractorStatus] = None


# Contractor Response
class ContractorResponse(ContractorBase):
    id: int
    workspace_id: UUID4
    user_id: int
    status: ContractorStatus
    rating: Optional[Decimal] = None
    total_jobs_completed: int
    created_at: datetime
    updated_at: datetime
    
    # Related data
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    workspace_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# Contractor List Response
class ContractorListResponse(BaseModel):
    contractors: List[ContractorResponse]
    total: int
    page: int
    size: int
    pages: int


# Contractor Dashboard Response
class ContractorDashboardResponse(BaseModel):
    contractor_id: int
    total_jobs: int
    active_jobs: int
    completed_jobs: int
    pending_assignments: int
    wallet_balance: Decimal
    pending_earnings: Decimal
    total_earnings: Decimal
    current_rating: Optional[Decimal] = None
    compliance_status: str
    recent_jobs: List[dict]
    upcoming_jobs: List[dict]
    notifications_count: int


# Job Assignment Schema
class JobAssignmentResponse(BaseModel):
    id: int
    job_id: int
    contractor_id: int
    assigned_by_id: Optional[int] = None
    status: AssignmentStatus
    assigned_at: datetime
    responded_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None
    
    # Job details
    job_number: Optional[str] = None
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    job_location: Optional[str] = None
    estimated_hours: Optional[Decimal] = None
    estimated_cost: Optional[Decimal] = None
    due_date: Optional[date] = None
    
    class Config:
        from_attributes = True


# Payout Schema
class PayoutResponse(BaseModel):
    id: int
    workspace_id: UUID4
    contractor_id: int
    job_id: Optional[int] = None
    payout_number: str
    amount: Decimal
    status: PayoutStatus
    payment_method: PaymentMethod
    description: Optional[str] = None
    scheduled_date: Optional[date] = None
    paid_date: Optional[date] = None
    processed_by_id: Optional[int] = None
    transaction_reference: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    job_number: Optional[str] = None
    processed_by_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# Wallet Schema
class WalletResponse(BaseModel):
    id: int
    contractor_id: int
    balance: Decimal
    total_earned: Decimal
    total_withdrawn: Decimal
    pending_amount: Decimal
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WalletTransactionResponse(BaseModel):
    id: int
    wallet_id: int
    transaction_type: str  # CREDIT, DEBIT
    amount: Decimal
    balance_after: Decimal
    status: str
    description: Optional[str] = None
    reference_number: Optional[str] = None
    payout_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Compliance Schema
class ComplianceUpload(BaseModel):
    compliance_type: ComplianceType
    document_name: str = Field(..., min_length=1, max_length=255)
    document_number: Optional[str] = Field(None, max_length=100)
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    notes: Optional[str] = None


class ComplianceResponse(BaseModel):
    id: int
    workspace_id: UUID4
    contractor_id: int
    compliance_type: ComplianceType
    document_name: str
    document_number: Optional[str] = None
    status: ComplianceStatus
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    verified_by_id: Optional[int] = None
    verified_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    is_expiring_soon: bool = False
    is_expired: bool = False
    
    # Related data
    verified_by_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# Payout Request Schema
class PayoutRequestCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    payment_method: PaymentMethod
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    bank_routing_number: Optional[str] = None
    paypal_email: Optional[str] = None
    notes: Optional[str] = None


class PayoutRequestResponse(BaseModel):
    id: int
    contractor_id: int
    request_number: str
    amount: Decimal
    status: str  # PENDING, APPROVED, REJECTED, PROCESSING, COMPLETED
    payment_method: PaymentMethod
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    bank_routing_number: Optional[str] = None
    paypal_email: Optional[str] = None
    notes: Optional[str] = None
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    payout_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    reviewed_by_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# Performance Metrics Schema
class ContractorPerformanceResponse(BaseModel):
    contractor_id: int
    total_jobs: int
    completed_jobs: int
    cancelled_jobs: int
    completion_rate: float
    average_rating: Optional[Decimal] = None
    on_time_completion_rate: float
    total_earnings: Decimal
    average_job_value: Decimal
    customer_satisfaction_score: Optional[float] = None
    compliance_score: float
    recent_performance_trend: str  # IMPROVING, STABLE, DECLINING
    strengths: List[str]
    areas_for_improvement: List[str]
    monthly_performance: List[dict]  # Last 12 months data