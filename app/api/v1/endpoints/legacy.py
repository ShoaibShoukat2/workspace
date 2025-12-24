"""
Legacy API Endpoints (Frontend Compatibility)
Provides backward compatibility with existing frontend expectations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_active_user, create_access_token
from app.models.auth import User
from app.crud import auth as auth_crud, job as job_crud
from app.schemas.auth import UserLogin, UserRegister
from app.utils.helpers import get_client_ip, get_user_agent

router = APIRouter()


@router.post("/signup", response_model=dict)
async def legacy_signup(
    user_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Legacy signup endpoint for frontend compatibility"""
    # Convert to backend format
    register_data = UserRegister(
        email=user_data["email"],
        password=user_data["password"],
        role=user_data.get("user_role", "customer"),
        full_name=user_data.get("name"),
        phone=user_data.get("phone")
    )
    
    # Check if user already exists
    existing_user = await auth_crud.get_user_by_email(db, register_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user
    try:
        user = await auth_crud.create_user(db, register_data)
        
        # Generate profileID for frontend compatibility
        profile_id = f"{user.role}-{user.id:03d}"
        
        return {
            "message": "User created successfully",
            "profileID": profile_id,
            "email": user.email,
            "user_role": user.role,
            "success": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=dict)
async def legacy_login(
    user_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Legacy login endpoint for frontend compatibility"""
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    # Get user
    user = await auth_crud.get_user_by_email(db, user_data["email"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Authenticate
    authenticated_user = await auth_crud.authenticate_user(
        db, user_data["email"], user_data["password"]
    )
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if user is active
    if not authenticated_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login
    await auth_crud.update_last_login(db, authenticated_user.id, ip_address)
    
    # Create token
    access_token = create_access_token(authenticated_user.email)
    
    # Generate profileID for frontend compatibility
    profile_id = f"{authenticated_user.role}-{authenticated_user.id:03d}"
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "profile": {
            "profileID": profile_id,
            "email": authenticated_user.email,
            "user_role": authenticated_user.role,
            "name": authenticated_user.full_name or authenticated_user.email.split('@')[0],
            "phone": authenticated_user.phone,
            "is_active": authenticated_user.is_active
        },
        "success": True
    }


@router.get("/profiles", response_model=List[dict])
async def legacy_get_profiles(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Legacy profiles endpoint for frontend compatibility"""
    users, total = await auth_crud.get_users(db, 0, 100)
    
    profiles = []
    for user in users:
        profile = {
            "profileID": f"{user.role}-{user.id:03d}",
            "email": user.email,
            "user_role": user.role,
            "name": user.full_name or user.email.split('@')[0],
            "phone": user.phone,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        profiles.append(profile)
    
    return profiles


@router.get("/profiles/{profile_id}", response_model=dict)
async def legacy_get_profile(
    profile_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Legacy get profile endpoint for frontend compatibility"""
    # Parse profileID format: role-001, role-002, etc.
    try:
        if '-' in profile_id:
            role_part, id_part = profile_id.rsplit('-', 1)
            user_id = int(id_part)
        else:
            user_id = int(profile_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid profile ID format"
        )
    
    user = await auth_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return {
        "profileID": profile_id,
        "email": user.email,
        "user_role": user.role,
        "name": user.full_name or user.email.split('@')[0],
        "phone": user.phone,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login_at.isoformat() if user.last_login_at else None
    }


@router.post("/jobs", response_model=dict)
async def legacy_create_job(
    job_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Legacy create job endpoint for frontend compatibility"""
    from app.schemas.job import JobCreate
    
    # Convert frontend format to backend format
    create_data = JobCreate(
        title=job_data.get("jobName", "New Job"),
        description=job_data.get("description", ""),
        property_address=job_data["propertyAddress"],
        city=job_data.get("city", ""),
        customer_name=job_data.get("customerName", ""),
        customer_email=job_data.get("customerEmail", ""),
        trade=job_data.get("trade", "general"),
        estimated_duration=job_data.get("estimatedTime", 4),
        estimated_cost=job_data.get("estimatedPay", "$0"),
        scheduled_date=job_data.get("scheduledTime"),
        requirements=job_data.get("squareFootage", "")
    )
    
    # Create job
    job = await job_crud.create_job(db, create_data, current_user.id)
    
    return {
        "jobID": job.id,
        "jobNumber": f"JOB-{job.id:06d}",
        "status": job.status,
        "message": "Job created successfully",
        "success": True
    }


@router.get("/jobs", response_model=List[dict])
async def legacy_get_jobs(
    status: Optional[str] = None,
    profileID: Optional[str] = None,
    assignedContractorId: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Legacy get jobs endpoint for frontend compatibility"""
    # Parse filters
    assigned_to = None
    if assignedContractorId:
        try:
            if '-' in assignedContractorId:
                role_part, id_part = assignedContractorId.rsplit('-', 1)
                assigned_to = int(id_part)
            else:
                assigned_to = int(assignedContractorId)
        except ValueError:
            pass
    
    # Get jobs
    jobs, total = await job_crud.get_jobs(
        db, current_user.id, 0, 100, None, status, assigned_to
    )
    
    # Convert to frontend format
    job_list = []
    for job in jobs:
        job_dict = {
            "jobID": job.id,
            "jobNumber": f"JOB-{job.id:06d}",
            "status": job.status,
            "propertyAddress": job.property_address,
            "city": job.city,
            "customerName": job.customer_name,
            "customerEmail": job.customer_email,
            "trade": job.trade,
            "estimatedPay": job.estimated_cost,
            "description": job.description,
            "scheduledTime": job.scheduled_date.isoformat() if job.scheduled_date else None,
            "assignedContractorId": f"contractor-{job.assigned_to_id:03d}" if job.assigned_to_id else None,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "contractorProgress": {
                "currentStep": 1,
                "acknowledged": False,
                "lastUpdated": job.updated_at.isoformat() if job.updated_at else None
            }
        }
        job_list.append(job_dict)
    
    return job_list


@router.post("/jobs/{job_id}/assign", response_model=dict)
async def legacy_assign_job(
    job_id: int,
    assignment_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Legacy assign job endpoint for frontend compatibility"""
    # Parse contractor ID
    contractor_id_str = assignment_data["contractorId"]
    try:
        if '-' in contractor_id_str:
            role_part, id_part = contractor_id_str.rsplit('-', 1)
            contractor_id = int(id_part)
        else:
            contractor_id = int(contractor_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid contractor ID format"
        )
    
    # Get job
    job = await job_crud.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Update job assignment
    from app.schemas.job import JobUpdate
    update_data = JobUpdate(assigned_to_id=contractor_id, status="assigned")
    
    updated_job = await job_crud.update_job(db, job.id, update_data)
    
    return {
        "message": "Job assigned successfully",
        "jobID": updated_job.id,
        "assignedContractorId": f"contractor-{contractor_id:03d}",
        "success": True
    }


@router.put("/jobs/{job_id}", response_model=dict)
async def legacy_update_job(
    job_id: int,
    job_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Legacy update job endpoint for frontend compatibility"""
    # Get job
    job = await job_crud.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Update contractor progress if provided
    if "contractorProgress" in job_data:
        progress = job_data["contractorProgress"]
        # Store progress in job notes or separate progress table
        # For now, just update the job status based on progress
        if progress.get("currentStep", 0) >= 3:
            from app.schemas.job import JobUpdate
            update_data = JobUpdate(status="in_progress")
            await job_crud.update_job(db, job.id, update_data)
    
    return {
        "message": "Job updated successfully",
        "jobID": job.id,
        "success": True
    }