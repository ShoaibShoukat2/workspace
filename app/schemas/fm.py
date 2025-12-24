"""
FM (Facility Manager) Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal


class FMDashboardResponse(BaseModel):
    pending_visits: int
    active_jobs: int
    completed_today: int
    total_visits_this_month: int
    average_completion_time: float
    material_issues_count: int
    change_orders_pending: int


class MaterialItem(BaseModel):
    id: str
    name: str
    sku: Optional[str] = None
    quantity: int
    supplier: Optional[str] = None
    price_range: Optional[str] = None
    status: str = "AI Generated"


class SiteVisitCreate(BaseModel):
    job_id: int
    scheduled_date: Optional[datetime] = None
    notes: Optional[str] = None


class FMJobVisitUpdate(BaseModel):
    measurements: Optional[Dict[str, Any]] = None
    scope_confirmed: Optional[bool] = None
    photos_uploaded: Optional[bool] = None
    tools_required: Optional[List[str]] = None
    labor_required: Optional[int] = None
    estimated_time: Optional[float] = None
    safety_concerns: Optional[str] = None
    materials: Optional[List[MaterialItem]] = None
    signature_saved: Optional[bool] = None
    status: Optional[str] = None


class FMJobVisitResponse(BaseModel):
    id: int
    job_id: int
    status: str
    material_status: Optional[str] = None
    measurements: Optional[Dict[str, Any]] = None
    scope_confirmed: bool = False
    photos_uploaded: bool = False
    tools_required: Optional[List[str]] = None
    labor_required: Optional[int] = None
    estimated_time: Optional[float] = None
    safety_concerns: Optional[str] = None
    materials: Optional[List[MaterialItem]] = None
    signature_saved: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MaterialVerificationRequest(BaseModel):
    job_id: int
    materials: List[MaterialItem]
    verified_by_notes: Optional[str] = None


class ChangeOrderLineItem(BaseModel):
    description: str
    category: str = Field(..., pattern="^(Labor|Material)$")
    quantity: float = Field(..., gt=0)
    rate: float = Field(..., gt=0)


class ChangeOrderCreate(BaseModel):
    job_id: int
    reason: str = Field(..., min_length=10)
    line_items: List[ChangeOrderLineItem]
    notes: Optional[str] = None


class ChangeOrderResponse(BaseModel):
    id: int
    job_id: int
    reason: str
    line_items: List[ChangeOrderLineItem]
    total_amount: Decimal
    status: str
    dispute_id: Optional[int] = None
    created_by_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuoteGenerationRequest(BaseModel):
    job_id: int
    materials: List[MaterialItem]
    labor_hours: float = Field(..., gt=0)
    labor_rate: float = Field(default=80.0, gt=0)
    markup_percentage: float = Field(default=15.0, ge=0, le=50)


class QuoteResponse(BaseModel):
    id: int
    job_id: int
    line_items: List[Dict[str, Any]]
    subtotal: Decimal
    markup: Decimal
    total_amount: Decimal
    magic_token: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class FMAnalyticsResponse(BaseModel):
    total_visits_completed: int
    average_visit_duration: float
    material_accuracy_rate: float
    change_order_rate: float
    customer_satisfaction_score: float
    on_time_completion_rate: float


class FMPerformanceMetrics(BaseModel):
    visits_this_month: int
    visits_last_month: int
    average_completion_time: float
    material_issues_identified: int
    change_orders_created: int
    quotes_generated: int
    approval_rate: float


class PhotoUploadRequest(BaseModel):
    visit_id: int
    photo_type: str = Field(..., pattern="^(before|after|progress|issue)$")
    photo_count: int = Field(..., gt=0, le=10)


class MapJobLocation(BaseModel):
    id: int
    property_address: str
    customer_name: str
    status: str
    coordinates: Dict[str, float]  # {"lat": float, "lng": float}
    visit_status: str
    priority: str = "normal"


class SiteVisitSummary(BaseModel):
    id: int
    job_id: int
    job_number: Optional[str] = None
    property_address: str
    customer_name: str
    trade: str
    status: str
    visit_status: str
    material_status: Optional[str] = None
    mandatory_site_visit: bool = True
    is_project: bool = False
    materials_count: int = 0
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None


class AIGeneratedMaterial(BaseModel):
    id: str
    name: str
    sku: Optional[str] = None
    quantity: int
    unit: str = "each"
    supplier: Optional[str] = None
    price_range: Optional[str] = None
    category: str
    ai_confidence: float = Field(..., ge=0, le=1)
    reasoning: Optional[str] = None


class AIMaterialSuggestionResponse(BaseModel):
    job_id: int
    trade: str
    scope_analysis: str
    suggested_materials: List[AIGeneratedMaterial]
    total_estimated_cost: Optional[str] = None
    confidence_score: float = Field(..., ge=0, le=1)
    generated_at: datetime