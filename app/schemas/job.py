"""
Job Management Schemas
"""
from pydantic import BaseModel, Field, UUID4
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class JobStatus(str, Enum):
    LEAD = "LEAD"
    EVALUATION_SCHEDULED = "EVALUATION_SCHEDULED"
    EVALUATION_COMPLETED = "EVALUATION_COMPLETED"
    AWAITING_PRE_START_APPROVAL = "AWAITING_PRE_START_APPROVAL"
    IN_PROGRESS = "IN_PROGRESS"
    MID_CHECKPOINT_PENDING = "MID_CHECKPOINT_PENDING"
    AWAITING_FINAL_APPROVAL = "AWAITING_FINAL_APPROVAL"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class JobPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class PhotoType(str, Enum):
    BEFORE = "BEFORE"
    EVALUATION = "EVALUATION"
    PROGRESS = "PROGRESS"
    AFTER = "AFTER"
    CUSTOMER_MATERIALS = "CUSTOMER_MATERIALS"


class CheckpointType(str, Enum):
    PRE_START = "PRE_START"
    MID_PROJECT = "MID_PROJECT"
    FINAL = "FINAL"


class CheckpointStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ISSUE = "ISSUE"


# Base Job Schema
class JobBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    priority: JobPriority = JobPriority.MEDIUM
    location: Optional[str] = Field(None, max_length=255)
    customer_name: Optional[str] = Field(None, max_length=255)
    customer_email: Optional[str] = Field(None, max_length=254)
    customer_phone: Optional[str] = Field(None, max_length=20)
    customer_address: Optional[str] = None
    notes: Optional[str] = None


# Job Creation
class JobCreate(JobBase):
    workspace_id: UUID4
    assigned_to_id: Optional[int] = None
    estimated_hours: Optional[Decimal] = None
    estimated_cost: Optional[Decimal] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    scheduled_evaluation_at: Optional[datetime] = None
    expected_start: Optional[date] = None
    expected_end: Optional[date] = None


# Job Update
class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    status: Optional[JobStatus] = None
    priority: Optional[JobPriority] = None
    assigned_to_id: Optional[int] = None
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None
    estimated_cost: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    completed_date: Optional[date] = None
    location: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    notes: Optional[str] = None


# Job Response
class JobResponse(JobBase):
    id: int
    workspace_id: UUID4
    job_number: str
    status: JobStatus
    assigned_to_id: Optional[int] = None
    created_by_id: Optional[int] = None
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None
    estimated_cost: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    completed_date: Optional[date] = None
    evaluation_fee: Decimal
    evaluation_fee_credited: bool
    created_at: datetime
    updated_at: datetime
    
    # Related data
    assigned_to_name: Optional[str] = None
    created_by_name: Optional[str] = None
    workspace_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# Job List Response
class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    page: int
    size: int
    pages: int


# Job Evaluation Schema
class JobEvaluationUpdate(BaseModel):
    room_count: Optional[int] = None
    square_feet: Optional[Decimal] = None
    measurements_data: Optional[Dict[str, Any]] = None
    scope: Optional[str] = None
    tools_required: Optional[List[str]] = None
    labor_required: Optional[int] = None
    estimated_hours: Optional[Decimal] = None
    safety_concerns: Optional[str] = None


class JobEvaluationResponse(BaseModel):
    id: int
    job_id: int
    room_count: Optional[int] = None
    square_feet: Optional[Decimal] = None
    measurements_data: Dict[str, Any]
    scope: Optional[str] = None
    tools_required: List[str]
    labor_required: Optional[int] = None
    estimated_hours: Optional[Decimal] = None
    safety_concerns: Optional[str] = None
    is_submitted: bool
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Job Photo Schema
class JobPhotoUpload(BaseModel):
    photo_type: PhotoType
    caption: Optional[str] = None


class JobPhotoResponse(BaseModel):
    id: int
    job_id: int
    photo_type: PhotoType
    file_path: str
    file_url: str
    caption: Optional[str] = None
    uploaded_by_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Material Suggestion Schema
class MaterialSuggestionResponse(BaseModel):
    id: int
    job_id: int
    item_name: str
    sku: Optional[str] = None
    vendor: str
    vendor_logo_url: Optional[str] = None
    price_range: str
    suggested_qty: Decimal
    unit: str
    product_url: str
    contractor_confirmed_qty: Optional[Decimal] = None
    contractor_status: str
    customer_material_source: str
    customer_liability_accepted: bool
    contractor_verified_customer_materials: bool
    contractor_verification_note: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Job Checkpoint Schema
class JobCheckpointResponse(BaseModel):
    id: int
    job_id: int
    checkpoint_type: CheckpointType
    status: CheckpointStatus
    scope_summary: Optional[str] = None
    progress_note: Optional[str] = None
    customer_note: Optional[str] = None
    rejection_reason: Optional[str] = None
    customer_rating: Optional[int] = None
    customer_review: Optional[str] = None
    created_at: datetime
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Job Progress Note Schema
class JobProgressNoteCreate(BaseModel):
    note: str = Field(..., min_length=1)
    checkpoint_id: Optional[int] = None


class JobProgressNoteResponse(BaseModel):
    id: int
    job_id: int
    note: str
    added_by_id: Optional[int] = None
    checkpoint_id: Optional[int] = None
    created_at: datetime
    added_by_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# Job Detail Response (with all related data)
class JobDetailResponse(JobResponse):
    evaluation: Optional[JobEvaluationResponse] = None
    photos: List[JobPhotoResponse] = []
    material_suggestions: List[MaterialSuggestionResponse] = []
    checkpoints: List[JobCheckpointResponse] = []
    progress_notes: List[JobProgressNoteResponse] = []
    attachments: List[dict] = []
    
    class Config:
        from_attributes = True


# Job Quote Schema
class JobQuoteResponse(BaseModel):
    id: int
    job_id: int
    quote_id: str
    gbb_total: Decimal
    evaluation_fee: Decimal
    total_after_credit: Decimal
    line_items: List[Dict[str, Any]]
    generated_by_ai: bool
    generation_context: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Job Attachment Schema
class JobAttachmentResponse(BaseModel):
    id: int
    job_id: int
    file_name: str
    file_path: str
    file_type: str
    file_size: int
    uploaded_by_id: Optional[int] = None
    description: Optional[str] = None
    created_at: datetime
    uploaded_by_name: Optional[str] = None
    
    class Config:
        from_attributes = True