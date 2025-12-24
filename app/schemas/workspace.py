"""
Workspace Schemas
"""
from pydantic import BaseModel, Field, UUID4
from typing import Optional, List
from datetime import datetime
from enum import Enum


class WorkspaceType(str, Enum):
    PROJECT = "PROJECT"
    CUSTOMER = "CUSTOMER"
    FACILITY = "FACILITY"


class MemberRole(str, Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"


# Base Workspace Schema
class WorkspaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    workspace_type: WorkspaceType = WorkspaceType.PROJECT
    description: Optional[str] = None


# Workspace Creation
class WorkspaceCreate(WorkspaceBase):
    pass


# Workspace Update
class WorkspaceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    workspace_type: Optional[WorkspaceType] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# Workspace Response
class WorkspaceResponse(WorkspaceBase):
    id: int
    workspace_id: UUID4
    owner_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Workspace List Response
class WorkspaceListResponse(BaseModel):
    workspaces: List[WorkspaceResponse]
    total: int
    page: int
    size: int
    pages: int


# Workspace Member Response
class WorkspaceMemberResponse(BaseModel):
    id: int
    user_id: int
    role: MemberRole
    joined_at: datetime
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# Workspace Statistics
class WorkspaceStatsResponse(BaseModel):
    total_jobs: int
    active_jobs: int
    completed_jobs: int
    total_contractors: int
    active_contractors: int
    total_estimates: int
    pending_estimates: int
    approved_estimates: int
    total_revenue: float
    pending_payouts: float
    compliance_issues: int
    recent_activity: List[dict]