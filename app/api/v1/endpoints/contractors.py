"""
Contractor Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_active_user, get_contractor_user, get_admin_user
from app.models.auth import User
from app.models.workspace import Job
from app.schemas.contractor import (
    ContractorCreate, ContractorUpdate, ContractorResponse, ContractorListResponse,
    ContractorDashboardResponse, JobAssignmentResponse, PayoutResponse,
    ComplianceUpload, ComplianceResponse, WalletResponse
)
from app.crud.contractor import contractor_crud

router = APIRouter()


@router.get("/", response_model=ContractorListResponse)
async def list_contractors(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    workspace_id: Optional[UUID] = None,
    status: Optional[str] = None,
    specialization: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List contractors with filtering"""
    contractors, total = await contractor_crud.get_contractors(
        db, current_user.id, skip, limit, workspace_id, status, specialization, search
    )
    
    return ContractorListResponse(
        contractors=[ContractorResponse(**{
            **contractor.__dict__,
            "user_email": contractor.user.email if contractor.user else None,
            "user_name": f"{contractor.user.first_name} {contractor.user.last_name}" if contractor.user and contractor.user.first_name else contractor.user.email if contractor.user else None,
            "workspace_name": contractor.workspace.name if contractor.workspace else None
        }) for contractor in contractors],
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=ContractorResponse, status_code=status.HTTP_201_CREATED)
async def create_contractor(
    contractor_data: ContractorCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new contractor profile"""
    contractor = await contractor_crud.create_contractor(db, contractor_data, current_user.id)
    return ContractorResponse(**{
        **contractor.__dict__,
        "user_email": contractor.user.email if contractor.user else None,
        "user_name": f"{contractor.user.first_name} {contractor.user.last_name}" if contractor.user and contractor.user.first_name else contractor.user.email if contractor.user else None,
        "workspace_name": contractor.workspace.name if contractor.workspace else None
    })


@router.get("/{contractor_id}", response_model=ContractorResponse)
async def get_contractor(
    contractor_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get contractor by ID"""
    contractor = await contractor_crud.get_contractor(db, contractor_id)
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor not found"
        )
    
    # Check access permissions
    has_access = await contractor_crud.user_has_contractor_access(
        db, current_user.id, contractor.id
    )
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this contractor"
        )
    
    return ContractorResponse(**{
        **contractor.__dict__,
        "user_email": contractor.user.email if contractor.user else None,
        "user_name": f"{contractor.user.first_name} {contractor.user.last_name}" if contractor.user and contractor.user.first_name else contractor.user.email if contractor.user else None,
        "workspace_name": contractor.workspace.name if contractor.workspace else None
    })


@router.patch("/{contractor_id}", response_model=ContractorResponse)
async def update_contractor(
    contractor_id: int,
    contractor_data: ContractorUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update contractor profile"""
    contractor = await contractor_crud.get_contractor(db, contractor_id)
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor not found"
        )
    
    # Check if user can edit this contractor
    can_edit = await contractor_crud.user_can_edit_contractor(
        db, current_user.id, contractor.id
    )
    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied to edit this contractor"
        )
    
    updated_contractor = await contractor_crud.update_contractor(
        db, contractor.id, contractor_data
    )
    return ContractorResponse(**{
        **updated_contractor.__dict__,
        "user_email": updated_contractor.user.email if updated_contractor.user else None,
        "user_name": f"{updated_contractor.user.first_name} {updated_contractor.user.last_name}" if updated_contractor.user and updated_contractor.user.first_name else updated_contractor.user.email if updated_contractor.user else None,
        "workspace_name": updated_contractor.workspace.name if updated_contractor.workspace else None
    })


# Contractor Dashboard
@router.get("/dashboard/overview", response_model=ContractorDashboardResponse)
async def contractor_dashboard(
    contractor_user: User = Depends(get_contractor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get contractor dashboard data"""
    contractor = await contractor_crud.get_contractor_by_user_id(db, contractor_user.id)
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor profile not found"
        )
    
    dashboard_data = await contractor_crud.get_contractor_dashboard(db, contractor.id)
    return ContractorDashboardResponse(**dashboard_data)


@router.get("/assignments", response_model=List[JobAssignmentResponse])
async def get_job_assignments(
    status: Optional[str] = None,
    contractor_user: User = Depends(get_contractor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get job assignments for contractor"""
    contractor = await contractor_crud.get_contractor_by_user_id(db, contractor_user.id)
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor profile not found"
        )
    
    assignments = await contractor_crud.get_job_assignments(db, contractor.id, status)
    return [JobAssignmentResponse(**assignment) for assignment in assignments]


@router.post("/assignments/{assignment_id}/accept", response_model=dict)
async def accept_job_assignment(
    assignment_id: int,
    contractor_user: User = Depends(get_contractor_user),
    db: AsyncSession = Depends(get_db)
):
    """Accept job assignment"""
    contractor = await contractor_crud.get_contractor_by_user_id(db, contractor_user.id)
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor profile not found"
        )
    
    success = await contractor_crud.accept_job_assignment(db, assignment_id, contractor.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found or already processed"
        )
    
    return {"message": "Job assignment accepted successfully"}


@router.post("/assignments/{assignment_id}/reject", response_model=dict)
async def reject_job_assignment(
    assignment_id: int,
    rejection_reason: Optional[str] = None,
    contractor_user: User = Depends(get_contractor_user),
    db: AsyncSession = Depends(get_db)
):
    """Reject job assignment"""
    contractor = await contractor_crud.get_contractor_by_user_id(db, contractor_user.id)
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor profile not found"
        )
    
    success = await contractor_crud.reject_job_assignment(
        db, assignment_id, contractor.id, rejection_reason
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found or already processed"
        )
    
    return {"message": "Job assignment rejected"}


# Wallet and Payouts
@router.get("/wallet", response_model=WalletResponse)
async def get_contractor_wallet(
    contractor_user: User = Depends(get_contractor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get contractor wallet information"""
    contractor = await contractor_crud.get_contractor_by_user_id(db, contractor_user.id)
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor profile not found"
        )
    
    wallet = await contractor_crud.get_contractor_wallet(db, contractor.id)
    return WalletResponse(**wallet)


@router.get("/payouts", response_model=List[PayoutResponse])
async def get_contractor_payouts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    contractor_user: User = Depends(get_contractor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get contractor payout history"""
    contractor = await contractor_crud.get_contractor_by_user_id(db, contractor_user.id)
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor profile not found"
        )
    
    payouts = await contractor_crud.get_contractor_payouts(
        db, contractor.id, skip, limit, status
    )
    
    payout_list = []
    for payout in payouts:
        payout_dict = {
            **payout.__dict__,
            "job_number": f"JOB-{payout.job_id:06d}" if payout.job_id else None,
            "processed_by_name": None  # Would need to join with user table
        }
        payout_list.append(PayoutResponse(**payout_dict))
    
    return payout_list


@router.post("/payout-request", response_model=dict)
async def request_payout(
    amount: float,
    payment_method: str,
    notes: Optional[str] = None,
    contractor_user: User = Depends(get_contractor_user),
    db: AsyncSession = Depends(get_db)
):
    """Request payout from wallet"""
    contractor = await contractor_crud.get_contractor_by_user_id(db, contractor_user.id)
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor profile not found"
        )
    
    # Check wallet balance
    wallet = await contractor_crud.get_contractor_wallet(db, contractor.id)
    if wallet.balance < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient wallet balance"
        )
    
    payout_request = await contractor_crud.create_payout_request(
        db, contractor.id, amount, payment_method, notes
    )
    
    return {
        "message": "Payout request submitted successfully",
        "request_id": payout_request.id
    }


# Compliance Management
@router.get("/compliance", response_model=List[ComplianceResponse])
async def get_contractor_compliance(
    contractor_user: User = Depends(get_contractor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get contractor compliance documents"""
    contractor = await contractor_crud.get_contractor_by_user_id(db, contractor_user.id)
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor profile not found"
        )
    
    compliance_docs = await contractor_crud.get_contractor_compliance(db, contractor.id)
    
    compliance_list = []
    for doc in compliance_docs:
        doc_dict = {
            **doc.__dict__,
            "is_expiring_soon": doc.is_expiring_soon if hasattr(doc, 'is_expiring_soon') else False,
            "is_expired": doc.is_expired if hasattr(doc, 'is_expired') else False,
            "verified_by_name": None  # Would need to join with user table
        }
        compliance_list.append(ComplianceResponse(**doc_dict))
    
    return compliance_list


@router.post("/compliance/upload", status_code=status.HTTP_201_CREATED)
async def upload_compliance_document(
    compliance_type: str,
    document_name: str,
    file: UploadFile = File(...),
    document_number: Optional[str] = None,
    issue_date: Optional[str] = None,
    expiry_date: Optional[str] = None,
    contractor_user: User = Depends(get_contractor_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload compliance document"""
    contractor = await contractor_crud.get_contractor_by_user_id(db, contractor_user.id)
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor profile not found"
        )
    
    compliance_doc = await contractor_crud.upload_compliance_document(
        db, contractor.id, compliance_type, document_name, file,
        document_number, issue_date, expiry_date
    )
    
    return {
        "message": "Compliance document uploaded successfully",
        "document_id": compliance_doc.id
    }


# Admin endpoints for contractor management
@router.post("/{contractor_id}/approve", response_model=dict)
async def approve_contractor(
    contractor_id: int,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve contractor (Admin only)"""
    contractor = await contractor_crud.get_contractor(db, contractor_id)
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor not found"
        )
    
    await contractor_crud.approve_contractor(db, contractor.id)
    return {"message": "Contractor approved successfully"}


@router.post("/{contractor_id}/suspend", response_model=dict)
async def suspend_contractor(
    contractor_id: int,
    reason: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Suspend contractor (Admin only)"""
    contractor = await contractor_crud.get_contractor(db, contractor_id)
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor not found"
        )
    
    await contractor_crud.suspend_contractor(db, contractor.id, reason)
    return {"message": "Contractor suspended successfully"}


@router.get("/{contractor_id}/performance", response_model=dict)
async def get_contractor_performance(
    contractor_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get contractor performance metrics"""
    contractor = await contractor_crud.get_contractor(db, contractor_id)
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor not found"
        )
    
    # Check access
    has_access = await contractor_crud.user_has_contractor_access(
        db, current_user.id, contractor.id
    )
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this contractor"
        )
    
    performance = await contractor_crud.get_contractor_performance(db, contractor.id)
    return performance


# Additional endpoints for frontend integration
@router.get("/jobs/available", response_model=List[dict])
async def get_available_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    city: Optional[str] = None,
    job_type: Optional[str] = None,
    contractor_user: User = Depends(get_contractor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get available jobs for contractor"""
    contractor = await contractor_crud.get_contractor_by_user_id(db, contractor_user.id)
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor profile not found"
        )
    
    jobs = await contractor_crud.get_available_jobs(
        db, contractor.id, skip, limit, city, job_type
    )
    return jobs


@router.get("/jobs/my-jobs", response_model=List[dict])
async def get_my_jobs(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    contractor_user: User = Depends(get_contractor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get contractor's assigned jobs"""
    contractor = await contractor_crud.get_contractor_by_user_id(db, contractor_user.id)
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor profile not found"
        )
    
    jobs = await contractor_crud.get_contractor_jobs(
        db, contractor.id, skip, limit, status
    )
    
    job_list = []
    for job in jobs:
        job_dict = {
            "id": job.id,
            "job_number": job.job_number,
            "title": job.title,
            "description": job.description,
            "status": job.status,
            "property_address": job.location,
            "customer_name": job.customer_name,
            "customer_phone": job.customer_phone,
            "estimated_cost": float(job.estimated_cost) if job.estimated_cost else 0,
            "actual_cost": float(job.actual_cost) if job.actual_cost else 0,
            "estimated_hours": float(job.estimated_hours) if job.estimated_hours else 0,
            "actual_hours": float(job.actual_hours) if job.actual_hours else 0,
            "start_date": job.start_date.isoformat() if job.start_date else None,
            "due_date": job.due_date.isoformat() if job.due_date else None,
            "completed_date": job.completed_date.isoformat() if job.completed_date else None,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat()
        }
        job_list.append(job_dict)
    
    return job_list


@router.post("/jobs/{job_id}/accept", response_model=dict)
async def accept_available_job(
    job_id: int,
    contractor_user: User = Depends(get_contractor_user),
    db: AsyncSession = Depends(get_db)
):
    """Accept an available job"""
    contractor = await contractor_crud.get_contractor_by_user_id(db, contractor_user.id)
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor profile not found"
        )
    
    # Check if job exists and is available
    job_result = await db.execute(
        select(Job).where(
            and_(
                Job.id == job_id,
                Job.assigned_to_id.is_(None),
                Job.status == "LEAD"
            )
        )
    )
    job = job_result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or already assigned"
        )
    
    # Assign job to contractor
    await db.execute(
        update(Job)
        .where(Job.id == job_id)
        .values(
            assigned_to_id=contractor.user_id,
            status="assigned",
            updated_at=datetime.utcnow()
        )
    )
    await db.commit()
    
    return {
        "message": "Job accepted successfully",
        "job_id": job_id,
        "job_number": job.job_number
    }


@router.get("/notifications", response_model=List[dict])
async def get_contractor_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    contractor_user: User = Depends(get_contractor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get contractor notifications"""
    contractor = await contractor_crud.get_contractor_by_user_id(db, contractor_user.id)
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor profile not found"
        )
    
    notifications = await contractor_crud.get_contractor_notifications(
        db, contractor.id, skip, limit
    )
    return notifications


@router.get("/compliance/status", response_model=dict)
async def get_compliance_status(
    contractor_user: User = Depends(get_contractor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get contractor compliance status summary"""
    contractor = await contractor_crud.get_contractor_by_user_id(db, contractor_user.id)
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor profile not found"
        )
    
    compliance_docs = await contractor_crud.get_contractor_compliance(db, contractor.id)
    
    # Check compliance status
    required_types = ["ID", "LICENSE", "INSURANCE"]
    compliance_status = "active"
    missing_docs = []
    expired_docs = []
    
    for req_type in required_types:
        type_docs = [doc for doc in compliance_docs if doc.compliance_type == req_type]
        if not type_docs:
            missing_docs.append(req_type)
            compliance_status = "blocked"
        else:
            for doc in type_docs:
                if doc.status != "APPROVED":
                    compliance_status = "blocked"
                elif doc.expiry_date and doc.expiry_date < date.today():
                    expired_docs.append(req_type)
                    compliance_status = "blocked"
    
    return {
        "status": compliance_status,
        "total_documents": len(compliance_docs),
        "approved_documents": len([doc for doc in compliance_docs if doc.status == "APPROVED"]),
        "pending_documents": len([doc for doc in compliance_docs if doc.status == "PENDING"]),
        "missing_documents": missing_docs,
        "expired_documents": expired_docs,
        "compliance_score": (len([doc for doc in compliance_docs if doc.status == "APPROVED"]) / max(len(required_types), 1)) * 100
    }