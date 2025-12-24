"""
Customer Portal Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_active_user, get_customer_user
from app.models.auth import User
from app.schemas.customer import (
    CustomerDashboardResponse, CustomerJobResponse, CustomerNotificationResponse,
    CustomerProfileUpdate, CustomerPreferencesUpdate, IssueReportCreate
)
from app.crud.customer import customer_crud

router = APIRouter()


@router.get("/dashboard", response_model=CustomerDashboardResponse)
async def customer_dashboard(
    customer_user: User = Depends(get_customer_user),
    db: AsyncSession = Depends(get_db)
):
    """Get customer dashboard data"""
    dashboard_data = await customer_crud.get_customer_dashboard(db, customer_user.id)
    return CustomerDashboardResponse(**dashboard_data)


@router.get("/jobs", response_model=List[CustomerJobResponse])
async def list_customer_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    customer_user: User = Depends(get_customer_user),
    db: AsyncSession = Depends(get_db)
):
    """List jobs for customer"""
    jobs = await customer_crud.get_customer_jobs(
        db, customer_user.email, skip, limit, status
    )
    return [CustomerJobResponse.from_orm(job) for job in jobs]


@router.get("/jobs/{job_id}", response_model=CustomerJobResponse)
async def get_customer_job(
    job_id: int,
    customer_user: User = Depends(get_customer_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific job details for customer"""
    job = await customer_crud.get_customer_job(db, job_id, customer_user.email)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return CustomerJobResponse.from_orm(job)


@router.get("/jobs/{job_id}/tracking", response_model=dict)
async def get_job_tracking(
    job_id: int,
    customer_user: User = Depends(get_customer_user),
    db: AsyncSession = Depends(get_db)
):
    """Get real-time job tracking information"""
    job = await customer_crud.get_customer_job(db, job_id, customer_user.email)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    tracking_data = await customer_crud.get_job_tracking(db, job_id)
    return tracking_data


@router.get("/jobs/{job_id}/contractor-location", response_model=dict)
async def get_contractor_location(
    job_id: int,
    customer_user: User = Depends(get_customer_user),
    db: AsyncSession = Depends(get_db)
):
    """Get real-time contractor location for job"""
    job = await customer_crud.get_customer_job(db, job_id, customer_user.email)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    location_data = await customer_crud.get_contractor_location(db, job_id)
    if not location_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor location not available"
        )
    
    return location_data


@router.get("/jobs/{job_id}/materials", response_model=List[dict])
async def get_job_materials(
    job_id: int,
    customer_user: User = Depends(get_customer_user),
    db: AsyncSession = Depends(get_db)
):
    """Get material references for job (read-only for transparency)"""
    job = await customer_crud.get_customer_job(db, job_id, customer_user.email)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    materials = await customer_crud.get_job_materials(db, job_id)
    return materials


@router.post("/jobs/{job_id}/approve-checkpoint/{checkpoint_id}", response_model=dict)
async def approve_job_checkpoint(
    job_id: int,
    checkpoint_id: int,
    customer_note: Optional[str] = None,
    rating: Optional[int] = None,
    customer_user: User = Depends(get_customer_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve job checkpoint"""
    job = await customer_crud.get_customer_job(db, job_id, customer_user.email)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    success = await customer_crud.approve_checkpoint(
        db, checkpoint_id, customer_note, rating
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checkpoint not found"
        )
    
    return {"message": "Checkpoint approved successfully"}


@router.post("/jobs/{job_id}/reject-checkpoint/{checkpoint_id}", response_model=dict)
async def reject_job_checkpoint(
    job_id: int,
    checkpoint_id: int,
    rejection_reason: str,
    customer_user: User = Depends(get_customer_user),
    db: AsyncSession = Depends(get_db)
):
    """Reject job checkpoint"""
    job = await customer_crud.get_customer_job(db, job_id, customer_user.email)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    success = await customer_crud.reject_checkpoint(db, checkpoint_id, rejection_reason)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checkpoint not found"
        )
    
    return {"message": "Checkpoint rejected"}


@router.post("/jobs/{job_id}/report-issue", response_model=dict)
async def report_job_issue(
    job_id: int,
    issue_data: IssueReportCreate,
    customer_user: User = Depends(get_customer_user),
    db: AsyncSession = Depends(get_db)
):
    """Report an issue with the job"""
    job = await customer_crud.get_customer_job(db, job_id, customer_user.email)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    issue = await customer_crud.report_job_issue(
        db, job_id, issue_data, customer_user.id
    )
    
    return {
        "message": "Issue reported successfully",
        "issue_id": issue.id
    }


@router.get("/notifications", response_model=List[CustomerNotificationResponse])
async def get_customer_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
    customer_user: User = Depends(get_customer_user),
    db: AsyncSession = Depends(get_db)
):
    """Get customer notifications"""
    notifications = await customer_crud.get_customer_notifications(
        db, customer_user.id, skip, limit, unread_only
    )
    return [CustomerNotificationResponse.from_orm(notif) for notif in notifications]


@router.post("/notifications/{notification_id}/read", response_model=dict)
async def mark_notification_read(
    notification_id: int,
    customer_user: User = Depends(get_customer_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark notification as read"""
    success = await customer_crud.mark_notification_read(
        db, notification_id, customer_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification marked as read"}


@router.post("/notifications/read-all", response_model=dict)
async def mark_all_notifications_read(
    customer_user: User = Depends(get_customer_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark all notifications as read"""
    count = await customer_crud.mark_all_notifications_read(db, customer_user.id)
    return {"message": f"Marked {count} notifications as read"}


@router.get("/profile", response_model=dict)
async def get_customer_profile(
    customer_user: User = Depends(get_customer_user),
    db: AsyncSession = Depends(get_db)
):
    """Get customer profile"""
    profile = await customer_crud.get_customer_profile(db, customer_user.id)
    return profile


@router.patch("/profile", response_model=dict)
async def update_customer_profile(
    profile_data: CustomerProfileUpdate,
    customer_user: User = Depends(get_customer_user),
    db: AsyncSession = Depends(get_db)
):
    """Update customer profile"""
    updated_profile = await customer_crud.update_customer_profile(
        db, customer_user.id, profile_data
    )
    return {"message": "Profile updated successfully", "profile": updated_profile}


@router.get("/preferences", response_model=dict)
async def get_customer_preferences(
    customer_user: User = Depends(get_customer_user),
    db: AsyncSession = Depends(get_db)
):
    """Get customer notification preferences"""
    preferences = await customer_crud.get_customer_preferences(db, customer_user.id)
    return preferences


@router.patch("/preferences", response_model=dict)
async def update_customer_preferences(
    preferences_data: CustomerPreferencesUpdate,
    customer_user: User = Depends(get_customer_user),
    db: AsyncSession = Depends(get_db)
):
    """Update customer notification preferences"""
    updated_preferences = await customer_crud.update_customer_preferences(
        db, customer_user.id, preferences_data
    )
    return {"message": "Preferences updated successfully", "preferences": updated_preferences}


# Public endpoints for token-based access (for customers without accounts)
@router.get("/public/job/{token}", response_model=dict)
async def get_job_by_token(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Get job details using magic token (for customers without accounts)"""
    job_data = await customer_crud.get_job_by_token(db, token)
    if not job_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired token"
        )
    
    return job_data


@router.get("/public/job/{token}/tracking", response_model=dict)
async def get_job_tracking_by_token(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Get job tracking using magic token"""
    tracking_data = await customer_crud.get_job_tracking_by_token(db, token)
    if not tracking_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired token"
        )
    
    return tracking_data


@router.post("/public/job/{token}/approve-quote", response_model=dict)
async def approve_quote_by_token(
    token: str,
    signature: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Approve quote using magic token"""
    success = await customer_crud.approve_quote_by_token(db, token, signature)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired token"
        )
    
    return {"message": "Quote approved successfully"}


@router.post("/generate-credentials", response_model=dict)
async def generate_customer_credentials(
    email: str,
    job_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Generate temporary credentials for customer access"""
    credentials = await customer_crud.generate_customer_credentials(
        db, email, job_number
    )
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or email mismatch"
        )
    
    return credentials