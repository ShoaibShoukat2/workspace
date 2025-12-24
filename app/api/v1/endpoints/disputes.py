"""
Dispute Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_active_user, get_admin_user, get_fm_user
from app.models.auth import User
from app.schemas.dispute import (
    DisputeCreate, DisputeUpdate, DisputeResponse, DisputeListResponse,
    DisputeMessageCreate, DisputeMessageResponse, DisputeResolutionCreate
)
from app.crud.dispute import dispute_crud

router = APIRouter()


@router.get("/", response_model=DisputeListResponse)
async def list_disputes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    severity: Optional[str] = None,
    job_id: Optional[int] = None,
    raised_by_role: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List disputes with filtering"""
    disputes, total = await dispute_crud.get_disputes(
        db, current_user.id, skip, limit, status, severity, job_id, raised_by_role, search
    )
    
    return DisputeListResponse(
        disputes=[DisputeResponse.from_orm(dispute) for dispute in disputes],
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=DisputeResponse, status_code=status.HTTP_201_CREATED)
async def create_dispute(
    dispute_data: DisputeCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new dispute"""
    dispute = await dispute_crud.create_dispute(db, dispute_data, current_user.id)
    return DisputeResponse.from_orm(dispute)


@router.get("/{dispute_id}", response_model=DisputeResponse)
async def get_dispute(
    dispute_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dispute by ID"""
    dispute = await dispute_crud.get_dispute(db, dispute_id)
    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute not found"
        )
    
    # Check access permissions
    has_access = await dispute_crud.user_has_dispute_access(db, current_user.id, dispute.id)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this dispute"
        )
    
    return DisputeResponse.from_orm(dispute)


@router.patch("/{dispute_id}", response_model=DisputeResponse)
async def update_dispute(
    dispute_id: int,
    dispute_data: DisputeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update dispute"""
    dispute = await dispute_crud.get_dispute(db, dispute_id)
    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute not found"
        )
    
    # Check permissions
    can_edit = await dispute_crud.user_can_edit_dispute(db, current_user.id, dispute.id)
    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied to edit this dispute"
        )
    
    updated_dispute = await dispute_crud.update_dispute(db, dispute.id, dispute_data)
    return DisputeResponse.from_orm(updated_dispute)


@router.get("/{dispute_id}/messages", response_model=List[DisputeMessageResponse])
async def get_dispute_messages(
    dispute_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dispute messages"""
    dispute = await dispute_crud.get_dispute(db, dispute_id)
    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute not found"
        )
    
    # Check access
    has_access = await dispute_crud.user_has_dispute_access(db, current_user.id, dispute.id)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this dispute"
        )
    
    messages = await dispute_crud.get_dispute_messages(db, dispute.id)
    return [DisputeMessageResponse.from_orm(message) for message in messages]


@router.post("/{dispute_id}/messages", response_model=DisputeMessageResponse, status_code=status.HTTP_201_CREATED)
async def add_dispute_message(
    dispute_id: int,
    message_data: DisputeMessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Add message to dispute"""
    dispute = await dispute_crud.get_dispute(db, dispute_id)
    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute not found"
        )
    
    # Check access
    has_access = await dispute_crud.user_has_dispute_access(db, current_user.id, dispute.id)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this dispute"
        )
    
    message = await dispute_crud.add_dispute_message(db, dispute.id, message_data, current_user.id)
    return DisputeMessageResponse.from_orm(message)


@router.post("/{dispute_id}/attachments", status_code=status.HTTP_201_CREATED)
async def upload_dispute_attachment(
    dispute_id: int,
    file: UploadFile = File(...),
    description: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload attachment to dispute"""
    dispute = await dispute_crud.get_dispute(db, dispute_id)
    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute not found"
        )
    
    # Check access
    has_access = await dispute_crud.user_has_dispute_access(db, current_user.id, dispute.id)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this dispute"
        )
    
    attachment = await dispute_crud.upload_dispute_attachment(
        db, dispute.id, file, description, current_user.id
    )
    
    return {
        "message": "Attachment uploaded successfully",
        "attachment_id": attachment.id,
        "filename": attachment.filename
    }


@router.post("/{dispute_id}/escalate", response_model=dict)
async def escalate_dispute(
    dispute_id: int,
    escalation_reason: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Escalate dispute to higher authority"""
    dispute = await dispute_crud.get_dispute(db, dispute_id)
    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute not found"
        )
    
    # Check permissions
    can_escalate = await dispute_crud.user_can_escalate_dispute(db, current_user.id, dispute.id)
    if not can_escalate:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied to escalate this dispute"
        )
    
    await dispute_crud.escalate_dispute(db, dispute.id, escalation_reason, current_user.id)
    
    return {"message": "Dispute escalated successfully"}


@router.post("/{dispute_id}/resolve", response_model=dict)
async def resolve_dispute(
    dispute_id: int,
    resolution_data: DisputeResolutionCreate,
    admin_user: User = Depends(get_fm_user),  # FM or Admin can resolve
    db: AsyncSession = Depends(get_db)
):
    """Resolve dispute (FM/Admin only)"""
    dispute = await dispute_crud.get_dispute(db, dispute_id)
    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute not found"
        )
    
    if dispute.status == "resolved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dispute is already resolved"
        )
    
    await dispute_crud.resolve_dispute(db, dispute.id, resolution_data, admin_user.id)
    
    return {"message": "Dispute resolved successfully"}


@router.post("/{dispute_id}/reopen", response_model=dict)
async def reopen_dispute(
    dispute_id: int,
    reopen_reason: str,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Reopen resolved dispute (Admin only)"""
    dispute = await dispute_crud.get_dispute(db, dispute_id)
    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute not found"
        )
    
    if dispute.status != "resolved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only resolved disputes can be reopened"
        )
    
    await dispute_crud.reopen_dispute(db, dispute.id, reopen_reason, admin_user.id)
    
    return {"message": "Dispute reopened successfully"}


@router.get("/statistics", response_model=dict)
async def get_dispute_statistics(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dispute statistics (Admin only)"""
    stats = await dispute_crud.get_dispute_statistics(db, date_from, date_to)
    return stats


@router.get("/trends", response_model=dict)
async def get_dispute_trends(
    period: str = "month",  # day, week, month, quarter, year
    limit: int = Query(12, ge=1, le=50),
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dispute trends (Admin only)"""
    trends = await dispute_crud.get_dispute_trends(db, period, limit)
    return trends


# Customer-specific endpoints for public access
@router.post("/report", response_model=dict)
async def report_issue_public(
    job_token: str,
    issue_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Report issue using job token (public endpoint for customers)"""
    # Verify job token and create dispute
    dispute = await dispute_crud.create_dispute_from_token(db, job_token, issue_data)
    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid job token or job not found"
        )
    
    return {
        "message": "Issue reported successfully",
        "dispute_id": dispute.id,
        "reference_number": f"DISP-{dispute.id:06d}"
    }


@router.get("/public/{dispute_id}", response_model=dict)
async def get_dispute_public(
    dispute_id: int,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Get dispute details using public token"""
    dispute_data = await dispute_crud.get_dispute_by_token(db, dispute_id, token)
    if not dispute_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute not found or invalid token"
        )
    
    return dispute_data