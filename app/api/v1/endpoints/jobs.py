"""
Job Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_active_user, get_contractor_user, get_customer_user
from app.models.auth import User
from app.schemas.job import (
    JobCreate, JobUpdate, JobResponse, JobListResponse, JobDetailResponse,
    JobEvaluationUpdate, JobPhotoUpload, MaterialSuggestionResponse,
    JobCheckpointResponse, JobProgressNoteCreate
)
from app.crud.job import job_crud

router = APIRouter()


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    workspace_id: Optional[UUID] = None,
    status: Optional[str] = None,
    assigned_to: Optional[int] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List jobs with filtering"""
    jobs, total = await job_crud.get_jobs(
        db, current_user.id, skip, limit, workspace_id, status, assigned_to, search
    )
    
    return JobListResponse(
        jobs=[JobResponse.from_orm(job) for job in jobs],
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new job"""
    job = await job_crud.create_job(db, job_data, current_user.id)
    return JobResponse.from_orm(job)


@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get job by ID with full details"""
    job = await job_crud.get_job_with_details(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check access
    has_access = await job_crud.user_has_job_access(db, current_user.id, job.id)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this job"
        )
    
    return JobDetailResponse.from_orm(job)


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    job_data: JobUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update job"""
    job = await job_crud.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check permissions
    can_edit = await job_crud.user_can_edit_job(db, current_user.id, job.id)
    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied to edit this job"
        )
    
    updated_job = await job_crud.update_job(db, job.id, job_data)
    return JobResponse.from_orm(updated_job)


@router.post("/{job_id}/photos", status_code=status.HTTP_201_CREATED)
async def upload_job_photo(
    job_id: int,
    photo_type: str,
    file: UploadFile = File(...),
    caption: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload job photo"""
    job = await job_crud.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check access
    has_access = await job_crud.user_has_job_access(db, current_user.id, job.id)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this job"
        )
    
    photo = await job_crud.upload_job_photo(
        db, job.id, photo_type, file, caption, current_user.id
    )
    return {"message": "Photo uploaded successfully", "photo_id": photo.id}


@router.patch("/{job_id}/evaluation", response_model=dict)
async def update_job_evaluation(
    job_id: int,
    evaluation_data: JobEvaluationUpdate,
    contractor_user: User = Depends(get_contractor_user),
    db: AsyncSession = Depends(get_db)
):
    """Update job evaluation (contractor only)"""
    job = await job_crud.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if contractor is assigned to this job
    if job.assigned_to_id != contractor_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only assigned contractor can update evaluation"
        )
    
    evaluation = await job_crud.update_job_evaluation(db, job.id, evaluation_data)
    return {"message": "Evaluation updated successfully"}


@router.post("/{job_id}/evaluation/submit", response_model=dict)
async def submit_job_evaluation(
    job_id: int,
    contractor_user: User = Depends(get_contractor_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit job evaluation (contractor only)"""
    job = await job_crud.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if contractor is assigned to this job
    if job.assigned_to_id != contractor_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only assigned contractor can submit evaluation"
        )
    
    await job_crud.submit_job_evaluation(db, job.id)
    return {"message": "Evaluation submitted successfully"}


@router.get("/{job_id}/materials", response_model=List[MaterialSuggestionResponse])
async def get_job_materials(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get material suggestions for job"""
    job = await job_crud.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check access
    has_access = await job_crud.user_has_job_access(db, current_user.id, job.id)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this job"
        )
    
    materials = await job_crud.get_job_materials(db, job.id)
    return [MaterialSuggestionResponse.from_orm(material) for material in materials]


@router.get("/{job_id}/checkpoints", response_model=List[JobCheckpointResponse])
async def get_job_checkpoints(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get job checkpoints"""
    job = await job_crud.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check access
    has_access = await job_crud.user_has_job_access(db, current_user.id, job.id)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this job"
        )
    
    checkpoints = await job_crud.get_job_checkpoints(db, job.id)
    return [JobCheckpointResponse.from_orm(checkpoint) for checkpoint in checkpoints]


@router.post("/{job_id}/progress-notes", status_code=status.HTTP_201_CREATED)
async def add_progress_note(
    job_id: int,
    note_data: JobProgressNoteCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Add progress note to job"""
    job = await job_crud.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check access
    has_access = await job_crud.user_has_job_access(db, current_user.id, job.id)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this job"
        )
    
    note = await job_crud.add_progress_note(db, job.id, note_data, current_user.id)
    return {"message": "Progress note added successfully", "note_id": note.id}


@router.post("/{job_id}/complete", response_model=dict)
async def complete_job(
    job_id: int,
    completion_notes: Optional[str] = None,
    contractor_user: User = Depends(get_contractor_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark job as completed (contractor only)"""
    job = await job_crud.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if contractor is assigned to this job
    if job.assigned_to_id != contractor_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only assigned contractor can complete job"
        )
    
    await job_crud.complete_job(db, job.id, completion_notes)
    return {"message": "Job marked as completed"}


# Customer-specific endpoints
@router.get("/{job_id}/timeline", response_model=dict)
async def get_job_timeline(
    job_id: int,
    customer_user: User = Depends(get_customer_user),
    db: AsyncSession = Depends(get_db)
):
    """Get job timeline for customer"""
    job = await job_crud.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if customer owns this job
    if job.customer_email != customer_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this job"
        )
    
    timeline = await job_crud.get_job_timeline(db, job.id)
    return timeline


@router.post("/{job_id}/checkpoints/{checkpoint_id}/approve", response_model=dict)
async def approve_checkpoint(
    job_id: int,
    checkpoint_id: int,
    customer_note: Optional[str] = None,
    customer_user: User = Depends(get_customer_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve job checkpoint (customer only)"""
    job = await job_crud.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if customer owns this job
    if job.customer_email != customer_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this job"
        )
    
    await job_crud.approve_checkpoint(db, checkpoint_id, customer_note)
    return {"message": "Checkpoint approved successfully"}


@router.post("/{job_id}/checkpoints/{checkpoint_id}/reject", response_model=dict)
async def reject_checkpoint(
    job_id: int,
    checkpoint_id: int,
    rejection_reason: str,
    customer_user: User = Depends(get_customer_user),
    db: AsyncSession = Depends(get_db)
):
    """Reject job checkpoint (customer only)"""
    job = await job_crud.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if customer owns this job
    if job.customer_email != customer_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this job"
        )
    
    await job_crud.reject_checkpoint(db, checkpoint_id, rejection_reason)
    return {"message": "Checkpoint rejected"}