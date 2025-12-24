"""
Workspace and Job Models
Core business logic models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date, JSON, Index, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.core.database import Base


class Workspace(Base):
    """Workspace for each customer/project with unique ID"""
    __tablename__ = "workspaces"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    name = Column(String(255), nullable=False)
    workspace_type = Column(String(20), default="PROJECT")  # PROJECT, CUSTOMER, FACILITY
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User")
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="workspace", cascade="all, delete-orphan")
    contractors = relationship("Contractor", back_populates="workspace", cascade="all, delete-orphan")
    estimates = relationship("Estimate", back_populates="workspace", cascade="all, delete-orphan")
    payouts = relationship("Payout", back_populates="workspace", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="workspace", cascade="all, delete-orphan")
    compliance_data = relationship("ComplianceData", back_populates="workspace", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="workspace", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_workspace_id_active', 'workspace_id', 'is_active'),
        Index('idx_owner_type', 'owner_id', 'workspace_type'),
    )


class WorkspaceMember(Base):
    """Members associated with a workspace"""
    __tablename__ = "workspace_members"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), default="MEMBER")  # OWNER, ADMIN, MEMBER, VIEWER
    joined_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User")
    
    # Constraints
    __table_args__ = (
        Index('idx_workspace_user', 'workspace_id', 'user_id', unique=True),
    )


class Job(Base):
    """Jobs within a workspace"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    job_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(30), default="LEAD")  # LEAD, EVALUATION_SCHEDULED, etc.
    priority = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH, URGENT
    
    # Assignment
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Estimates and costs
    estimated_hours = Column(Numeric(10, 2), nullable=True)
    actual_hours = Column(Numeric(10, 2), nullable=True)
    estimated_cost = Column(Numeric(12, 2), nullable=True)
    actual_cost = Column(Numeric(12, 2), nullable=True)
    
    # Dates
    start_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    completed_date = Column(Date, nullable=True)
    
    # Location and customer info
    location = Column(String(255), nullable=True)
    customer_name = Column(String(255), nullable=True)
    customer_email = Column(String(254), nullable=True)
    customer_phone = Column(String(20), nullable=True)
    customer_address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # FM-related fields
    requires_site_visit = Column(Boolean, default=False)
    materials_list = Column(Text, nullable=True)  # JSON string
    materials_verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    materials_verified_at = Column(DateTime, nullable=True)
    
    # Branding
    brand_name = Column(String(255), default="Apex")
    powered_by = Column(String(255), default="Apex")
    
    # Evaluation scheduling
    scheduled_evaluation_at = Column(DateTime, nullable=True)
    expected_start = Column(Date, nullable=True)
    expected_end = Column(Date, nullable=True)
    
    # Evaluation fee
    evaluation_fee = Column(Numeric(10, 2), default=99.00)
    evaluation_fee_credited = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    workspace = relationship("Workspace", back_populates="jobs")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    evaluation = relationship("JobEvaluation", back_populates="job", uselist=False, cascade="all, delete-orphan")
    photos = relationship("JobPhoto", back_populates="job", cascade="all, delete-orphan")
    quotes = relationship("JobQuote", back_populates="job", cascade="all, delete-orphan")
    checkpoints = relationship("JobCheckpoint", back_populates="job", cascade="all, delete-orphan")
    progress_notes = relationship("JobProgressNote", back_populates="job", cascade="all, delete-orphan")
    material_suggestions = relationship("MaterialSuggestion", back_populates="job", cascade="all, delete-orphan")
    attachments = relationship("JobAttachment", back_populates="job", cascade="all, delete-orphan")
    estimates = relationship("Estimate", back_populates="job", cascade="all, delete-orphan")
    disputes = relationship("Dispute", cascade="all, delete-orphan")
    material_deliveries = relationship("MaterialDelivery", cascade="all, delete-orphan")
    job_tokens = relationship("JobToken", cascade="all, delete-orphan")
    notifications = relationship("Notification", cascade="all, delete-orphan")
    site_visits = relationship("SiteVisit", back_populates="job", cascade="all, delete-orphan")
    change_orders = relationship("ChangeOrder", back_populates="job", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_workspace_status', 'workspace_id', 'status'),
        Index('idx_job_number', 'job_number'),
        Index('idx_created_by_status', 'created_by_id', 'status'),
    )


class JobEvaluation(Base):
    """Job evaluation data captured by contractor"""
    __tablename__ = "job_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, unique=True)
    
    # Measurements
    room_count = Column(Integer, nullable=True)
    square_feet = Column(Numeric(10, 2), nullable=True)
    measurements_data = Column(JSON, default=dict)
    
    # Scope and requirements
    scope = Column(Text, nullable=True)
    tools_required = Column(JSON, default=list)
    labor_required = Column(Integer, nullable=True)
    estimated_hours = Column(Numeric(8, 2), nullable=True)
    safety_concerns = Column(Text, nullable=True)
    
    # Status
    is_submitted = Column(Boolean, default=False)
    submitted_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="evaluation")


class JobPhoto(Base):
    """Photos for jobs at different stages"""
    __tablename__ = "job_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    photo_type = Column(String(20), nullable=False)  # BEFORE, EVALUATION, PROGRESS, AFTER, CUSTOMER_MATERIALS
    file_path = Column(String(500), nullable=False)
    file_url = Column(Text, nullable=False)
    caption = Column(String(255), nullable=True)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="photos")
    uploaded_by = relationship("User")


class JobQuote(Base):
    """AI-generated quotes for jobs"""
    __tablename__ = "job_quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    quote_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Pricing
    gbb_total = Column(Numeric(12, 2), nullable=False)
    evaluation_fee = Column(Numeric(10, 2), default=99.00)
    total_after_credit = Column(Numeric(12, 2), nullable=False)
    
    # Line items
    line_items = Column(JSON, default=list)
    
    # Generation metadata
    generated_by_ai = Column(Boolean, default=True)
    generation_context = Column(JSON, default=dict)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="quotes")


class JobCheckpoint(Base):
    """Job checkpoints for customer approval workflow"""
    __tablename__ = "job_checkpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    checkpoint_type = Column(String(20), nullable=False)  # PRE_START, MID_PROJECT, FINAL
    status = Column(String(20), default="PENDING")  # PENDING, APPROVED, REJECTED, ISSUE
    
    # Content
    scope_summary = Column(Text, nullable=True)
    progress_note = Column(Text, nullable=True)
    
    # Customer feedback
    customer_note = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    customer_rating = Column(Integer, nullable=True)
    customer_review = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    approved_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    
    # Relationships
    job = relationship("Job", back_populates="checkpoints")
    
    # Constraints
    __table_args__ = (
        Index('idx_job_checkpoint_type', 'job_id', 'checkpoint_type', unique=True),
    )


class JobProgressNote(Base):
    """Progress notes added during job execution"""
    __tablename__ = "job_progress_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    note = Column(Text, nullable=False)
    added_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    checkpoint_id = Column(Integer, ForeignKey("job_checkpoints.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="progress_notes")
    added_by = relationship("User")
    checkpoint = relationship("JobCheckpoint")


class MaterialSuggestion(Base):
    """AI-suggested materials for jobs"""
    __tablename__ = "material_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    # Material details
    item_name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=True)
    vendor = Column(String(100), nullable=False)
    vendor_logo_url = Column(Text, nullable=True)
    price_range = Column(String(50), nullable=False)  # "$35-$45 / gallon"
    suggested_qty = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(50), nullable=False)
    product_url = Column(Text, nullable=False)
    
    # Contractor verification
    contractor_confirmed_qty = Column(Numeric(10, 2), nullable=True)
    contractor_status = Column(String(20), default="pending")  # confirmed, removed, edited
    
    # Customer material handling
    customer_material_source = Column(String(20), default="links")  # links, customer_supplied
    customer_liability_accepted = Column(Boolean, default=False)
    contractor_verified_customer_materials = Column(Boolean, default=False)
    contractor_verification_note = Column(Text, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="material_suggestions")
    deliveries = relationship("MaterialDelivery", cascade="all, delete-orphan")


class JobAttachment(Base):
    """Attachments for jobs"""
    __tablename__ = "job_attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)  # File size in bytes
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="attachments")
    uploaded_by = relationship("User")


class Estimate(Base):
    """Estimates for jobs"""
    __tablename__ = "estimates"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    estimate_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="DRAFT")  # DRAFT, SENT, APPROVED, REJECTED, EXPIRED
    
    # Pricing
    subtotal = Column(Numeric(12, 2), default=0)
    tax_rate = Column(Numeric(5, 2), default=0)  # Tax rate in percentage
    tax_amount = Column(Numeric(12, 2), default=0)
    discount_amount = Column(Numeric(12, 2), default=0)
    total_amount = Column(Numeric(12, 2), default=0)
    
    # Validity
    valid_until = Column(Date, nullable=True)
    
    # Users
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Customer signature
    customer_signature = Column(Text, nullable=True)  # Base64 encoded signature image
    customer_signed_at = Column(DateTime, nullable=True)
    customer_ip_address = Column(String(45), nullable=True)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    workspace = relationship("Workspace", back_populates="estimates")
    job = relationship("Job", back_populates="estimates")
    created_by = relationship("User", foreign_keys=[created_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    line_items = relationship("EstimateLineItem", back_populates="estimate", cascade="all, delete-orphan")


class EstimateLineItem(Base):
    """Line items for estimates"""
    __tablename__ = "estimate_line_items"
    
    id = Column(Integer, primary_key=True, index=True)
    estimate_id = Column(Integer, ForeignKey("estimates.id"), nullable=False)
    item_order = Column(Integer, default=0)
    description = Column(String(500), nullable=False)
    quantity = Column(Numeric(10, 2), default=1)
    unit_price = Column(Numeric(12, 2), nullable=False)
    total = Column(Numeric(12, 2), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    estimate = relationship("Estimate", back_populates="line_items")


class Contractor(Base):
    """Contractors working in workspaces"""
    __tablename__ = "contractors"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_name = Column(String(255), nullable=True)
    license_number = Column(String(100), nullable=True)
    specialization = Column(String(255), nullable=True)
    hourly_rate = Column(Numeric(10, 2), nullable=True)
    status = Column(String(20), default="ACTIVE")  # ACTIVE, INACTIVE, SUSPENDED
    rating = Column(Numeric(3, 2), nullable=True)
    total_jobs_completed = Column(Integer, default=0)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    workspace = relationship("Workspace", back_populates="contractors")
    user = relationship("User")
    payouts = relationship("Payout", back_populates="contractor", cascade="all, delete-orphan")
    compliance_records = relationship("ComplianceData", back_populates="contractor", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        Index('idx_workspace_user', 'workspace_id', 'user_id', unique=True),
    )


class Payout(Base):
    """Payouts to contractors"""
    __tablename__ = "payouts"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    contractor_id = Column(Integer, ForeignKey("contractors.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    payout_number = Column(String(50), unique=True, index=True, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(20), default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED
    payment_method = Column(String(20), default="BANK_TRANSFER")  # BANK_TRANSFER, CHECK, CASH, PAYPAL, OTHER
    description = Column(Text, nullable=True)
    scheduled_date = Column(Date, nullable=True)
    paid_date = Column(Date, nullable=True)
    processed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    transaction_reference = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    workspace = relationship("Workspace", back_populates="payouts")
    contractor = relationship("Contractor", back_populates="payouts")
    job = relationship("Job")
    processed_by = relationship("User")


class Report(Base):
    """Reports generated for workspaces"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    report_type = Column(String(20), nullable=False)  # JOBS, ESTIMATES, CONTRACTORS, PAYOUTS, COMPLIANCE, FINANCIAL
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    generated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    file_path = Column(String(500), nullable=True)
    date_from = Column(Date, nullable=True)
    date_to = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    workspace = relationship("Workspace", back_populates="reports")
    generated_by = relationship("User")


class ComplianceData(Base):
    """Compliance tracking for contractors and jobs"""
    __tablename__ = "compliance_data"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    contractor_id = Column(Integer, ForeignKey("contractors.id"), nullable=False)
    compliance_type = Column(String(20), nullable=False)  # ID, LICENSE, INSURANCE, CERTIFICATION, CONTRACT, SAFETY, OTHER
    document_name = Column(String(255), nullable=False)
    document_number = Column(String(100), nullable=True)
    status = Column(String(20), default="PENDING")  # PENDING, APPROVED, REJECTED, EXPIRED, EXPIRING_SOON
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)  # File size in bytes
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    workspace = relationship("Workspace", back_populates="compliance_data")
    contractor = relationship("Contractor", back_populates="compliance_records")
    verified_by = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_workspace_status', 'workspace_id', 'status'),
        Index('idx_contractor_type', 'contractor_id', 'compliance_type'),
    )
    
    @property
    def is_expiring_soon(self) -> bool:
        """Check if document expires within 30 days"""
        if self.expiry_date and self.status == "APPROVED":
            from datetime import date, timedelta
            days_until_expiry = (self.expiry_date - date.today()).days
            return 0 < days_until_expiry <= 30
        return False
    
    @property
    def is_expired(self) -> bool:
        """Check if document is expired"""
        if self.expiry_date:
            from datetime import date
            return self.expiry_date < date.today()
        return False


class Dispute(Base):
    """Customer disputes and issue tracking"""
    __tablename__ = "disputes"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contractor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Dispute details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # QUALITY, TIMELINE, COST, COMMUNICATION, SAFETY, OTHER
    severity = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(20), default="OPEN")  # OPEN, IN_PROGRESS, RESOLVED, CLOSED, ESCALATED
    
    # Resolution
    resolution = Column(Text, nullable=True)
    resolved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Reference and tracking
    reference_number = Column(String(50), unique=True, index=True, nullable=False)
    priority = Column(String(20), default="NORMAL")  # LOW, NORMAL, HIGH, URGENT
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    job = relationship("Job")
    customer = relationship("User", foreign_keys=[customer_id])
    contractor = relationship("User", foreign_keys=[contractor_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])
    messages = relationship("DisputeMessage", back_populates="dispute", cascade="all, delete-orphan")
    change_order = relationship("ChangeOrder", back_populates="dispute", uselist=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_job_status', 'job_id', 'status'),
        Index('idx_customer_status', 'customer_id', 'status'),
        Index('idx_reference_number', 'reference_number'),
    )


class DisputeMessage(Base):
    """Messages in dispute conversations"""
    __tablename__ = "dispute_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    dispute_id = Column(Integer, ForeignKey("disputes.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal admin notes
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    dispute = relationship("Dispute", back_populates="messages")
    sender = relationship("User")


class Notification(Base):
    """User notifications"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Notification content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # JOB_UPDATE, PAYMENT, SYSTEM, MARKETING, etc.
    
    # Status
    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Related entities
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True)
    
    # Metadata
    notification_data = Column(JSON, default=dict)  # Additional data for the notification
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    read_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")
    job = relationship("Job")
    workspace = relationship("Workspace")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_read', 'user_id', 'is_read'),
        Index('idx_user_type', 'user_id', 'notification_type'),
        Index('idx_created_at', 'created_at'),
    )


class MaterialDelivery(Base):
    """Material delivery tracking"""
    __tablename__ = "material_deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    material_suggestion_id = Column(Integer, ForeignKey("material_suggestions.id"), nullable=True)
    
    # Delivery details
    delivery_date = Column(Date, nullable=False)
    delivery_time = Column(String(20), nullable=True)  # "9:00 AM - 12:00 PM"
    delivery_address = Column(Text, nullable=False)
    
    # Status tracking
    status = Column(String(20), default="SCHEDULED")  # SCHEDULED, IN_TRANSIT, DELIVERED, FAILED, CANCELLED
    tracking_number = Column(String(100), nullable=True)
    carrier = Column(String(100), nullable=True)
    
    # Confirmation
    confirmed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    delivery_notes = Column(Text, nullable=True)
    
    # Photos
    delivery_photo_url = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    job = relationship("Job")
    material_suggestion = relationship("MaterialSuggestion")
    confirmed_by = relationship("User")


class JobToken(Base):
    """Magic tokens for customer access to jobs"""
    __tablename__ = "job_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    token = Column(String(100), unique=True, index=True, nullable=False)
    token_type = Column(String(20), nullable=False)  # TRACKING, QUOTE_APPROVAL, FULL_ACCESS
    
    # Permissions
    can_view_details = Column(Boolean, default=True)
    can_approve_quote = Column(Boolean, default=False)
    can_track_progress = Column(Boolean, default=True)
    can_communicate = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Usage tracking
    last_used_at = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    job = relationship("Job")
    
    # Indexes
    __table_args__ = (
        Index('idx_token_active', 'token', 'is_active'),
        Index('idx_job_type', 'job_id', 'token_type'),
    )


class Investor(Base):
    """Investors in the platform"""
    __tablename__ = "investors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Investment details
    investment_amount = Column(Numeric(15, 2), nullable=False)
    split_percentage = Column(Numeric(5, 2), nullable=False)  # Percentage of profits
    status = Column(String(20), default="ACTIVE")  # ACTIVE, INACTIVE, SUSPENDED
    investment_date = Column(Date, nullable=False)
    
    # Calculated fields (updated by triggers/jobs)
    total_revenue = Column(Numeric(15, 2), default=0)
    total_payouts = Column(Numeric(15, 2), default=0)
    current_balance = Column(Numeric(15, 2), default=0)
    roi_percentage = Column(Numeric(8, 4), default=0)
    
    # Metadata
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    payouts = relationship("InvestorPayout", back_populates="investor", cascade="all, delete-orphan")
    reports = relationship("InvestorReport", back_populates="investor", cascade="all, delete-orphan")
    job_investments = relationship("JobInvestment", back_populates="investor", cascade="all, delete-orphan")
    split_history = relationship("InvestorSplitHistory", back_populates="investor", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_investment_date', 'investment_date'),
    )


class InvestorPayout(Base):
    """Payouts to investors"""
    __tablename__ = "investor_payouts"
    
    id = Column(Integer, primary_key=True, index=True)
    investor_id = Column(Integer, ForeignKey("investors.id"), nullable=False)
    
    # Payout details
    amount = Column(Numeric(12, 2), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    status = Column(String(20), default="PENDING")  # PENDING, PROCESSING, PAID, FAILED, CANCELLED
    
    # Job details for this payout
    job_count = Column(Integer, default=0)
    total_revenue = Column(Numeric(15, 2), default=0)
    
    # Processing
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    processed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    paid_at = Column(DateTime, nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    transaction_reference = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    investor = relationship("Investor", back_populates="payouts")
    created_by = relationship("User", foreign_keys=[created_by_id])
    processed_by = relationship("User", foreign_keys=[processed_by_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_investor_status', 'investor_id', 'status'),
        Index('idx_period', 'period_start', 'period_end'),
    )


class InvestorReport(Base):
    """Reports generated for investors"""
    __tablename__ = "investor_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    investor_id = Column(Integer, ForeignKey("investors.id"), nullable=False)
    
    # Report details
    report_type = Column(String(20), nullable=False)  # MONTHLY, QUARTERLY, ANNUAL, PERFORMANCE, TAX
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="PROCESSING")  # PROCESSING, COMPLETED, FAILED
    
    # Date range
    date_from = Column(Date, nullable=True)
    date_to = Column(Date, nullable=True)
    
    # File details
    file_path = Column(String(500), nullable=True)
    file_url = Column(Text, nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Report data (JSON for flexibility)
    data = Column(JSON, default=dict)
    filters = Column(JSON, default=dict)
    
    # Processing
    generated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    investor = relationship("Investor", back_populates="reports")
    generated_by = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_investor_type', 'investor_id', 'report_type'),
        Index('idx_status_created', 'status', 'created_at'),
    )


class JobInvestment(Base):
    """Investment tracking per job"""
    __tablename__ = "job_investments"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    investor_id = Column(Integer, ForeignKey("investors.id"), nullable=False)
    
    # Investment details for this job
    investment_amount = Column(Numeric(12, 2), nullable=False)
    split_percentage = Column(Numeric(5, 2), nullable=False)
    
    # Financial breakdown
    total_revenue = Column(Numeric(12, 2), default=0)
    total_expenses = Column(Numeric(12, 2), default=0)
    platform_fee = Column(Numeric(12, 2), default=0)
    net_profit = Column(Numeric(12, 2), default=0)
    investor_share = Column(Numeric(12, 2), default=0)
    
    # Performance metrics
    roi_percentage = Column(Numeric(8, 4), default=0)
    profit_margin = Column(Numeric(8, 4), default=0)
    
    # Status
    status = Column(String(20), default="ACTIVE")  # ACTIVE, COMPLETED, CANCELLED
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    job = relationship("Job")
    investor = relationship("Investor", back_populates="job_investments")
    
    # Indexes
    __table_args__ = (
        Index('idx_job_investor', 'job_id', 'investor_id', unique=True),
        Index('idx_investor_status', 'investor_id', 'status'),
    )


class InvestorSplitHistory(Base):
    """History of investor split percentage changes"""
    __tablename__ = "investor_split_history"
    
    id = Column(Integer, primary_key=True, index=True)
    investor_id = Column(Integer, ForeignKey("investors.id"), nullable=False)
    
    # Split change details
    old_percentage = Column(Numeric(5, 2), nullable=True)
    new_percentage = Column(Numeric(5, 2), nullable=False)
    effective_date = Column(Date, nullable=False)
    
    # Change tracking
    changed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    investor = relationship("Investor", back_populates="split_history")
    changed_by = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_investor_effective', 'investor_id', 'effective_date'),
    )


class SiteVisit(Base):
    """Site visits by Facility Managers"""
    __tablename__ = "site_visits"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    fm_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Visit details
    status = Column(String(50), default="SCHEDULED")  # SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED
    material_status = Column(String(50), default="AI Generated")  # AI Generated, FM Verified, Issues Found
    scheduled_date = Column(DateTime, nullable=True)
    completed_date = Column(DateTime, nullable=True)
    
    # Visit data
    measurements = Column(Text, nullable=True)  # JSON string
    scope_confirmed = Column(Boolean, default=False)
    photos_uploaded = Column(Boolean, default=False)
    tools_required = Column(Text, nullable=True)  # JSON string
    labor_required = Column(Integer, nullable=True)
    estimated_time = Column(Float, nullable=True)
    safety_concerns = Column(Text, nullable=True)
    materials_list = Column(Text, nullable=True)  # JSON string
    signature_saved = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="site_visits")
    fm_user = relationship("User", foreign_keys=[fm_user_id])


class ChangeOrder(Base):
    """Change orders created by Facility Managers"""
    __tablename__ = "change_orders"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    dispute_id = Column(Integer, ForeignKey("disputes.id"), nullable=True)
    
    # Change order details
    reason = Column(Text, nullable=False)
    line_items = Column(Text, nullable=False)  # JSON string
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default="PENDING")  # PENDING, APPROVED, REJECTED, CANCELLED
    notes = Column(Text, nullable=True)
    
    # Approval workflow
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="change_orders")
    created_by = relationship("User", foreign_keys=[created_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    dispute = relationship("Dispute", back_populates="change_order")