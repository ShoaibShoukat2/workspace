"""
Dispute Pydantic Schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DisputeStatus(str, Enum):
    """Dispute status enum"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"


class DisputeSeverity(str, Enum):
    """Dispute severity enum"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DisputeCategory(str, Enum):
    """Dispute category enum"""
    QUALITY = "quality"
    PAYMENT = "payment"
    TIMELINE = "timeline"
    COMMUNICATION = "communication"
    MATERIALS = "materials"
    SAFETY = "safety"
    OTHER = "other"


class DisputeCreate(BaseModel):
    """Create dispute schema"""
    job_id: int = Field(..., description="Job ID")
    title: str = Field(..., min_length=5, max_length=200, description="Dispute title")
    description: str = Field(..., min_length=10, max_length=2000, description="Dispute description")
    category: DisputeCategory = Field(..., description="Dispute category")
    severity: DisputeSeverity = Field(DisputeSeverity.MEDIUM, description="Dispute severity")
    
    # Evidence
    photos: Optional[List[str]] = Field(None, description="Photo URLs as evidence")
    documents: Optional[List[str]] = Field(None, description="Document URLs as evidence")
    
    # Contact info (for customers without accounts)
    customer_name: Optional[str] = Field(None, max_length=100, description="Customer name")
    customer_email: Optional[str] = Field(None, description="Customer email")
    customer_phone: Optional[str] = Field(None, max_length=20, description="Customer phone")


class DisputeUpdate(BaseModel):
    """Update dispute schema"""
    title: Optional[str] = Field(None, min_length=5, max_length=200, description="Dispute title")
    description: Optional[str] = Field(None, min_length=10, max_length=2000, description="Dispute description")
    category: Optional[DisputeCategory] = Field(None, description="Dispute category")
    severity: Optional[DisputeSeverity] = Field(None, description="Dispute severity")
    status: Optional[DisputeStatus] = Field(None, description="Dispute status")
    
    # Internal fields (admin/FM only)
    assigned_to_id: Optional[int] = Field(None, description="Assigned user ID")
    priority_score: Optional[int] = Field(None, ge=1, le=10, description="Priority score")
    internal_notes: Optional[str] = Field(None, max_length=1000, description="Internal notes")


class DisputeMessageCreate(BaseModel):
    """Create dispute message schema"""
    message: str = Field(..., min_length=1, max_length=2000, description="Message content")
    is_internal: bool = Field(False, description="Internal message (not visible to customer)")
    attachments: Optional[List[str]] = Field(None, description="Attachment URLs")


class DisputeMessageResponse(BaseModel):
    """Dispute message response"""
    id: int = Field(..., description="Message ID")
    dispute_id: int = Field(..., description="Dispute ID")
    sender_id: int = Field(..., description="Sender user ID")
    sender_name: str = Field(..., description="Sender name")
    sender_role: str = Field(..., description="Sender role")
    message: str = Field(..., description="Message content")
    is_internal: bool = Field(..., description="Internal message flag")
    attachments: List[str] = Field(default_factory=list, description="Attachment URLs")
    created_at: datetime = Field(..., description="Message timestamp")
    
    class Config:
        from_attributes = True


class DisputeResolutionCreate(BaseModel):
    """Create dispute resolution schema"""
    resolution_type: str = Field(..., description="Resolution type")
    resolution_summary: str = Field(..., min_length=10, max_length=1000, description="Resolution summary")
    resolution_details: Optional[str] = Field(None, max_length=2000, description="Detailed resolution")
    
    # Financial resolution
    refund_amount: Optional[float] = Field(None, ge=0, description="Refund amount")
    compensation_amount: Optional[float] = Field(None, ge=0, description="Compensation amount")
    
    # Actions taken
    actions_taken: Optional[List[str]] = Field(None, description="Actions taken to resolve")
    follow_up_required: bool = Field(False, description="Follow-up required")
    follow_up_date: Optional[datetime] = Field(None, description="Follow-up date")


class DisputeResponse(BaseModel):
    """Dispute response schema"""
    id: int = Field(..., description="Dispute ID")
    job_id: int = Field(..., description="Job ID")
    title: str = Field(..., description="Dispute title")
    description: str = Field(..., description="Dispute description")
    category: str = Field(..., description="Dispute category")
    severity: str = Field(..., description="Dispute severity")
    status: str = Field(..., description="Dispute status")
    
    # Parties involved
    raised_by_id: int = Field(..., description="User who raised the dispute")
    raised_by_role: str = Field(..., description="Role of user who raised dispute")
    assigned_to_id: Optional[int] = Field(None, description="Assigned user ID")
    
    # Customer info (for disputes raised by customers without accounts)
    customer_name: Optional[str] = Field(None, description="Customer name")
    customer_email: Optional[str] = Field(None, description="Customer email")
    customer_phone: Optional[str] = Field(None, description="Customer phone")
    
    # Metadata
    priority_score: int = Field(..., description="Priority score")
    estimated_resolution_time: Optional[int] = Field(None, description="Estimated resolution time in hours")
    
    # Evidence
    photos: List[str] = Field(default_factory=list, description="Photo URLs")
    documents: List[str] = Field(default_factory=list, description="Document URLs")
    
    # Resolution
    resolution_type: Optional[str] = Field(None, description="Resolution type")
    resolution_summary: Optional[str] = Field(None, description="Resolution summary")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    resolved_by_id: Optional[int] = Field(None, description="Resolver user ID")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Related data
    job_title: Optional[str] = Field(None, description="Related job title")
    job_address: Optional[str] = Field(None, description="Related job address")
    contractor_name: Optional[str] = Field(None, description="Contractor name")
    
    class Config:
        from_attributes = True


class DisputeListResponse(BaseModel):
    """Dispute list response"""
    disputes: List[DisputeResponse] = Field(..., description="List of disputes")
    total: int = Field(..., description="Total number of disputes")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


class DisputeAttachmentResponse(BaseModel):
    """Dispute attachment response"""
    id: int = Field(..., description="Attachment ID")
    dispute_id: int = Field(..., description="Dispute ID")
    filename: str = Field(..., description="Original filename")
    file_url: str = Field(..., description="File URL")
    file_type: str = Field(..., description="File type")
    file_size: int = Field(..., description="File size in bytes")
    description: Optional[str] = Field(None, description="Attachment description")
    uploaded_by_id: int = Field(..., description="Uploader user ID")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    
    class Config:
        from_attributes = True


class DisputeStatisticsResponse(BaseModel):
    """Dispute statistics response"""
    total_disputes: int = Field(..., description="Total number of disputes")
    open_disputes: int = Field(..., description="Number of open disputes")
    resolved_disputes: int = Field(..., description="Number of resolved disputes")
    escalated_disputes: int = Field(..., description="Number of escalated disputes")
    
    # By severity
    low_severity: int = Field(..., description="Low severity disputes")
    medium_severity: int = Field(..., description="Medium severity disputes")
    high_severity: int = Field(..., description="High severity disputes")
    critical_severity: int = Field(..., description="Critical severity disputes")
    
    # By category
    category_breakdown: Dict[str, int] = Field(..., description="Disputes by category")
    
    # Performance metrics
    average_resolution_time: float = Field(..., description="Average resolution time in hours")
    resolution_rate: float = Field(..., description="Resolution rate percentage")
    customer_satisfaction: Optional[float] = Field(None, description="Customer satisfaction score")
    
    # Trends
    monthly_trends: List[Dict[str, Any]] = Field(default_factory=list, description="Monthly dispute trends")


class DisputeEscalationCreate(BaseModel):
    """Create dispute escalation schema"""
    escalation_reason: str = Field(..., min_length=10, max_length=500, description="Escalation reason")
    escalation_level: int = Field(..., ge=1, le=3, description="Escalation level")
    escalated_to_id: Optional[int] = Field(None, description="Escalated to user ID")
    urgent: bool = Field(False, description="Urgent escalation flag")


class DisputePublicResponse(BaseModel):
    """Public dispute response (limited info for customers)"""
    id: int = Field(..., description="Dispute ID")
    reference_number: str = Field(..., description="Public reference number")
    title: str = Field(..., description="Dispute title")
    status: str = Field(..., description="Dispute status")
    severity: str = Field(..., description="Dispute severity")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_updated: datetime = Field(..., description="Last update timestamp")
    
    # Resolution info (if resolved)
    resolution_summary: Optional[str] = Field(None, description="Resolution summary")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    
    # Customer can see their own messages
    messages: List[DisputeMessageResponse] = Field(default_factory=list, description="Dispute messages")
    
    class Config:
        from_attributes = True