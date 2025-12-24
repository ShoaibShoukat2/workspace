"""
Customer Portal Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class NotificationType(str, Enum):
    JOB_SCHEDULED = "JOB_SCHEDULED"
    TECH_EN_ROUTE = "TECH_EN_ROUTE"
    TECH_ARRIVED = "TECH_ARRIVED"
    JOB_STARTED = "JOB_STARTED"
    JOB_COMPLETED = "JOB_COMPLETED"
    JOB_DELAYED = "JOB_DELAYED"
    MATERIAL_DELIVERED = "MATERIAL_DELIVERED"


class TrackingStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    EN_ROUTE = "EN_ROUTE"
    ARRIVED = "ARRIVED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DELAYED = "DELAYED"


class IssueCategory(str, Enum):
    QUALITY = "QUALITY"
    TIMELINE = "TIMELINE"
    COMMUNICATION = "COMMUNICATION"
    SAFETY = "SAFETY"
    MATERIALS = "MATERIALS"
    OTHER = "OTHER"


class IssuePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


# Customer Dashboard Response
class CustomerDashboardResponse(BaseModel):
    customer_id: int
    total_jobs: int
    active_jobs: int
    completed_jobs: int
    upcoming_appointments: int
    pending_approvals: int
    unread_notifications: int
    recent_jobs: List[dict]
    upcoming_jobs: List[dict]
    recent_notifications: List[dict]
    satisfaction_score: Optional[float] = None


# Customer Job Response
class CustomerJobResponse(BaseModel):
    id: int
    job_number: str
    title: str
    description: str
    status: str
    priority: str
    location: Optional[str] = None
    estimated_cost: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    completed_date: Optional[date] = None
    evaluation_fee: Decimal
    evaluation_fee_credited: bool
    created_at: datetime
    updated_at: datetime
    
    # Contractor information
    contractor_name: Optional[str] = None
    contractor_phone: Optional[str] = None
    contractor_company: Optional[str] = None
    contractor_rating: Optional[Decimal] = None
    
    # Progress information
    completion_percentage: Optional[float] = None
    current_phase: Optional[str] = None
    next_milestone: Optional[str] = None
    
    # Tracking information
    tracking_status: Optional[TrackingStatus] = None
    estimated_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Customer Notification Response
class CustomerNotificationResponse(BaseModel):
    id: int
    customer_id: int
    job_id: int
    notification_type: NotificationType
    title: str
    message: str
    sent_via: str
    is_read: bool
    sent_at: datetime
    read_at: Optional[datetime] = None
    
    # Job information
    job_number: Optional[str] = None
    job_title: Optional[str] = None
    
    class Config:
        from_attributes = True


# Customer Profile Update
class CustomerProfileUpdate(BaseModel):
    company_name: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    emergency_contact: Optional[str] = Field(None, max_length=255)
    emergency_phone: Optional[str] = Field(None, max_length=20)
    preferred_contact_method: Optional[str] = Field(None, max_length=20)


# Customer Preferences Update
class CustomerPreferencesUpdate(BaseModel):
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    job_updates: Optional[bool] = None
    marketing_emails: Optional[bool] = None
    appointment_reminders: Optional[bool] = None
    completion_surveys: Optional[bool] = None


# Issue Report Create
class IssueReportCreate(BaseModel):
    category: IssueCategory
    priority: IssuePriority = IssuePriority.MEDIUM
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    location: Optional[str] = None
    photos: Optional[List[str]] = None  # List of photo URLs
    preferred_contact_method: Optional[str] = None
    urgency_notes: Optional[str] = None


class IssueReportResponse(BaseModel):
    id: int
    job_id: int
    customer_id: int
    category: IssueCategory
    priority: IssuePriority
    title: str
    description: str
    status: str  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    location: Optional[str] = None
    photos: List[str]
    preferred_contact_method: Optional[str] = None
    urgency_notes: Optional[str] = None
    assigned_to_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    job_number: Optional[str] = None
    assigned_to_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# Job Timeline Response
class JobTimelineResponse(BaseModel):
    job_id: int
    timeline_events: List[Dict[str, Any]]
    current_status: str
    progress_percentage: float
    estimated_completion: Optional[datetime] = None
    milestones: List[Dict[str, Any]]
    checkpoints: List[Dict[str, Any]]


# Job Tracking Response
class JobTrackingResponse(BaseModel):
    job_id: int
    status: TrackingStatus
    estimated_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    delay_reason: Optional[str] = None
    last_location_update: Optional[datetime] = None
    contractor_location: Optional[Dict[str, Any]] = None
    progress_updates: List[Dict[str, Any]]


# Contractor Location Response
class ContractorLocationResponse(BaseModel):
    contractor_id: int
    job_id: int
    latitude: Decimal
    longitude: Decimal
    accuracy: float
    speed: Optional[float] = None
    heading: Optional[float] = None
    is_active: bool
    timestamp: datetime
    
    # Computed fields
    distance_to_job: Optional[float] = None  # in miles/km
    estimated_arrival: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Material Reference Response (Read-only for customers)
class MaterialReferenceResponse(BaseModel):
    id: int
    job_id: int
    item_name: str
    quantity: int
    supplier: str
    supplier_logo: Optional[str] = None
    sku: Optional[str] = None
    price_low: Optional[Decimal] = None
    price_high: Optional[Decimal] = None
    purchase_url: str
    description: Optional[str] = None
    price_range: str  # Computed property
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Checkpoint Approval/Rejection
class CheckpointApprovalRequest(BaseModel):
    customer_note: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)


class CheckpointRejectionRequest(BaseModel):
    rejection_reason: str = Field(..., min_length=1)


# Customer Credentials (for token-based access)
class CustomerCredentialsResponse(BaseModel):
    access_token: str
    job_token: str
    expires_in: int
    job_number: str
    customer_email: str


# Quote Approval (token-based)
class QuoteApprovalRequest(BaseModel):
    signature: Optional[str] = None  # Base64 encoded signature
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


# Material Delivery Confirmation
class MaterialDeliveryConfirmation(BaseModel):
    delivery_date: date
    delivered_items: List[Dict[str, Any]]
    delivery_notes: Optional[str] = None
    photos: Optional[List[str]] = None  # Photo URLs
    customer_signature: Optional[str] = None  # Base64 encoded


# Customer Satisfaction Survey
class CustomerSatisfactionSurvey(BaseModel):
    job_id: int
    overall_rating: int = Field(..., ge=1, le=5)
    quality_rating: int = Field(..., ge=1, le=5)
    timeliness_rating: int = Field(..., ge=1, le=5)
    communication_rating: int = Field(..., ge=1, le=5)
    professionalism_rating: int = Field(..., ge=1, le=5)
    would_recommend: bool
    feedback: Optional[str] = None
    areas_for_improvement: Optional[List[str]] = None
    contractor_strengths: Optional[List[str]] = None


class CustomerSatisfactionResponse(BaseModel):
    id: int
    job_id: int
    customer_id: int
    overall_rating: int
    quality_rating: int
    timeliness_rating: int
    communication_rating: int
    professionalism_rating: int
    would_recommend: bool
    feedback: Optional[str] = None
    areas_for_improvement: List[str]
    contractor_strengths: List[str]
    created_at: datetime
    
    # Related data
    job_number: Optional[str] = None
    contractor_name: Optional[str] = None
    
    class Config:
        from_attributes = True