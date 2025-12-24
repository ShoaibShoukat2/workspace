"""
Admin Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.core.security import get_admin_user, get_fm_user
from app.models.auth import User
from app.schemas.admin import (
    AdminDashboardResponse, AdminJobResponse, AdminLeadResponse,
    AdminComplianceResponse, AdminPayoutResponse, AdminReportResponse,
    LeadCreate, ComplianceActionRequest
)
from app.crud.admin import admin_crud

router = APIRouter()


@router.get("/dashboard", response_model=dict)
async def admin_dashboard(
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get admin dashboard overview"""
    dashboard_data = await admin_crud.get_admin_dashboard(db)
    return dashboard_data


# Job Management
@router.get("/jobs", response_model=List[dict])
async def list_all_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    workspace_id: Optional[str] = None,
    contractor_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List all jobs with admin filters"""
    jobs = await admin_crud.get_all_jobs(
        db, skip, limit, status, workspace_id, contractor_id, 
        date_from, date_to, search
    )
    
    job_list = []
    for job in jobs:
        job_dict = {
            "id": job.id,
            "job_number": job.job_number,
            "title": job.title,
            "propertyAddress": job.location,
            "customerName": job.customer_name,
            "type": job.title.split()[0].lower() if job.title else "general",
            "status": job.status,
            "assignedContractorId": job.assigned_to_id,
            "assignedContractorName": job.assigned_to.full_name if job.assigned_to else None,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
            "estimated_cost": float(job.estimated_cost) if job.estimated_cost else 0,
            "actual_cost": float(job.actual_cost) if job.actual_cost else 0
        }
        job_list.append(job_dict)
    
    return job_list


@router.get("/jobs/{job_id}", response_model=AdminJobResponse)
async def get_job_admin(
    job_id: int,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get job details (admin view)"""
    job = await admin_crud.get_job_admin(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return AdminJobResponse.from_orm(job)


@router.patch("/jobs/{job_id}/assign", response_model=dict)
async def assign_job_to_contractor(
    job_id: int,
    contractor_id: int,
    notes: Optional[str] = None,
    admin_user: User = Depends(get_fm_user),  # FM or Admin can assign
    db: AsyncSession = Depends(get_db)
):
    """Assign job to contractor"""
    success = await admin_crud.assign_job_to_contractor(
        db, job_id, contractor_id, admin_user.id, notes
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job or contractor not found"
        )
    
    return {"message": "Job assigned successfully"}


@router.post("/jobs/{job_id}/cancel", response_model=dict)
async def cancel_job(
    job_id: int,
    cancellation_reason: str,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel job"""
    success = await admin_crud.cancel_job(db, job_id, cancellation_reason, admin_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return {"message": "Job cancelled successfully"}


# Lead Management
@router.get("/leads", response_model=List[AdminLeadResponse])
async def list_all_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    source: Optional[str] = None,
    assigned_to: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List all leads with admin filters"""
    leads = await admin_crud.get_all_leads(
        db, skip, limit, status, source, assigned_to, date_from, date_to
    )
    return [AdminLeadResponse.from_orm(lead) for lead in leads]


@router.post("/leads", response_model=AdminLeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead_data: LeadCreate,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new lead manually"""
    lead = await admin_crud.create_lead(db, lead_data, admin_user.id)
    return AdminLeadResponse.from_orm(lead)


@router.get("/leads/{lead_id}", response_model=AdminLeadResponse)
async def get_lead_admin(
    lead_id: int,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get lead details (admin view)"""
    lead = await admin_crud.get_lead_admin(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return AdminLeadResponse.from_orm(lead)


@router.patch("/leads/{lead_id}/assign", response_model=dict)
async def assign_lead(
    lead_id: int,
    assigned_to: int,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Assign lead to user"""
    success = await admin_crud.assign_lead(db, lead_id, assigned_to, admin_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return {"message": "Lead assigned successfully"}


@router.post("/leads/{lead_id}/convert", response_model=dict)
async def convert_lead_to_job(
    lead_id: int,
    workspace_id: str,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Convert lead to job"""
    job = await admin_crud.convert_lead_to_job(db, lead_id, workspace_id, admin_user.id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found or already converted"
        )
    
    return {
        "message": "Lead converted to job successfully",
        "job_id": job.id,
        "job_number": job.job_number
    }


# Compliance Management
@router.get("/compliance", response_model=List[dict])
async def list_all_compliance(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    compliance_type: Optional[str] = None,
    contractor_id: Optional[int] = None,
    expiring_soon: bool = False,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List all compliance documents"""
    compliance_docs = await admin_crud.get_all_compliance(
        db, skip, limit, status, compliance_type, contractor_id, expiring_soon
    )
    
    compliance_list = []
    for doc in compliance_docs:
        doc_dict = {
            "id": doc.id,
            "contractor_id": doc.contractor_id,
            "contractor_name": doc.contractor.user.full_name if doc.contractor and doc.contractor.user else "Unknown",
            "compliance_type": doc.compliance_type,
            "document_name": doc.document_name,
            "document_number": doc.document_number,
            "status": doc.status,
            "issue_date": doc.issue_date.isoformat() if doc.issue_date else None,
            "expiry_date": doc.expiry_date.isoformat() if doc.expiry_date else None,
            "verified_by_id": doc.verified_by_id,
            "verified_at": doc.verified_at.isoformat() if doc.verified_at else None,
            "rejection_reason": doc.rejection_reason,
            "created_at": doc.created_at.isoformat(),
            "updated_at": doc.updated_at.isoformat()
        }
        compliance_list.append(doc_dict)
    
    return compliance_list


@router.post("/compliance/{compliance_id}/approve", response_model=dict)
async def approve_compliance(
    compliance_id: int,
    notes: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve compliance document"""
    success = await admin_crud.approve_compliance(
        db, compliance_id, admin_user.id, notes
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance document not found"
        )
    
    return {"message": "Compliance document approved"}


@router.post("/compliance/{compliance_id}/reject", response_model=dict)
async def reject_compliance(
    compliance_id: int,
    rejection_reason: str,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Reject compliance document"""
    success = await admin_crud.reject_compliance(
        db, compliance_id, admin_user.id, rejection_reason
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance document not found"
        )
    
    return {"message": "Compliance document rejected"}


@router.get("/compliance/overview", response_model=dict)
async def compliance_overview(
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get compliance overview statistics"""
    overview = await admin_crud.get_compliance_overview(db)
    return overview


@router.post("/contractors/{contractor_id}/compliance-action", response_model=dict)
async def contractor_compliance_action(
    contractor_id: int,
    action_data: ComplianceActionRequest,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Take compliance action on contractor"""
    success = await admin_crud.contractor_compliance_action(
        db, contractor_id, action_data, admin_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor not found"
        )
    
    return {"message": f"Compliance action '{action_data.action}' completed"}


# Payout Management
@router.get("/payouts", response_model=List[dict])
async def list_all_payouts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    contractor_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List all payouts"""
    payouts = await admin_crud.get_all_payouts(
        db, skip, limit, status, contractor_id, date_from, date_to
    )
    
    payout_list = []
    for payout in payouts:
        payout_dict = {
            "id": payout.id,
            "contractor_id": payout.contractor_id,
            "contractor_name": payout.contractor.user.full_name if payout.contractor and payout.contractor.user else "Unknown",
            "amount": float(payout.amount),
            "status": payout.status,
            "payment_method": payout.payment_method,
            "description": payout.description,
            "scheduled_date": payout.scheduled_date.isoformat() if payout.scheduled_date else None,
            "paid_date": payout.paid_date.isoformat() if payout.paid_date else None,
            "created_at": payout.created_at.isoformat(),
            "updated_at": payout.updated_at.isoformat(),
            "job_id": payout.job_id,
            "jobType": "standard"  # Mock job type for frontend compatibility
        }
        payout_list.append(payout_dict)
    
    return payout_list


@router.get("/payouts/ready", response_model=List[dict])
async def get_ready_for_payout_jobs(
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get jobs ready for payout"""
    ready_jobs = await admin_crud.get_ready_for_payout_jobs(db)
    return ready_jobs


@router.post("/payouts/{payout_id}/approve", response_model=dict)
async def approve_payout(
    payout_id: int,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve payout"""
    success = await admin_crud.approve_payout(db, payout_id, admin_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payout not found"
        )
    
    return {"message": "Payout approved successfully"}


@router.post("/payouts/{payout_id}/reject", response_model=dict)
async def reject_payout(
    payout_id: int,
    rejection_reason: str,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Reject payout"""
    success = await admin_crud.reject_payout(
        db, payout_id, admin_user.id, rejection_reason
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payout not found"
        )
    
    return {"message": "Payout rejected"}


@router.post("/payouts/bulk-approve", response_model=dict)
async def bulk_approve_payouts(
    payout_ids: List[int],
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Bulk approve payouts"""
    approved_count = await admin_crud.bulk_approve_payouts(
        db, payout_ids, admin_user.id
    )
    
    return {
        "message": f"Approved {approved_count} payouts successfully",
        "approved_count": approved_count
    }


# Reports and Analytics
@router.get("/reports", response_model=List[AdminReportResponse])
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    report_type: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List generated reports"""
    reports = await admin_crud.get_reports(db, skip, limit, report_type)
    return [AdminReportResponse.from_orm(report) for report in reports]


@router.post("/reports/generate", response_model=dict)
async def generate_report(
    report_type: str,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    filters: Optional[dict] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate new report"""
    report = await admin_crud.generate_report(
        db, report_type, admin_user.id, date_from, date_to, filters
    )
    
    return {
        "message": "Report generation started",
        "report_id": report.id,
        "status": "processing"
    }


@router.get("/analytics/overview", response_model=dict)
async def get_analytics_overview(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics overview"""
    analytics = await admin_crud.get_analytics_overview(db, date_from, date_to)
    return analytics


@router.get("/analytics/revenue", response_model=dict)
async def get_revenue_analytics(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    group_by: str = "month",  # day, week, month, year
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get revenue analytics"""
    revenue_data = await admin_crud.get_revenue_analytics(db, date_from, date_to, group_by)
    return revenue_data


@router.get("/analytics/performance", response_model=dict)
async def get_performance_analytics(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get performance analytics"""
    performance_data = await admin_crud.get_performance_analytics(db, date_from, date_to)
    return performance_data


# System Management
@router.get("/system/health", response_model=dict)
async def system_health_check(
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get system health status"""
    health_data = await admin_crud.get_system_health(db)
    return health_data


@router.get("/system/logs", response_model=List[dict])
async def get_system_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    level: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get system logs"""
    logs = await admin_crud.get_system_logs(db, skip, limit, level, date_from, date_to)
    return logs


@router.post("/system/maintenance", response_model=dict)
async def toggle_maintenance_mode(
    enabled: bool,
    message: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Toggle maintenance mode"""
    await admin_crud.toggle_maintenance_mode(db, enabled, message, admin_user.id)
    
    status_msg = "enabled" if enabled else "disabled"
    return {"message": f"Maintenance mode {status_msg}"}


# Investor Accounting
@router.get("/investor-accounting", response_model=dict)
async def get_investor_accounting(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get investor accounting data"""
    accounting_data = await admin_crud.get_investor_accounting(db, date_from, date_to)
    return accounting_data


@router.get("/ledger", response_model=List[dict])
async def get_admin_ledger(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    transaction_type: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get admin ledger entries"""
    ledger_entries = await admin_crud.get_admin_ledger(
        db, skip, limit, transaction_type, date_from, date_to
    )
    return ledger_entries


# Additional endpoints for frontend integration
@router.get("/contractors", response_model=List[dict])
async def list_all_contractors(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    search: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List all contractors for admin management"""
    from app.crud.contractor import contractor_crud
    
    contractors, total = await contractor_crud.get_contractors(
        db, admin_user.id, skip, limit, None, status, None, search
    )
    
    contractor_list = []
    for contractor in contractors:
        contractor_dict = {
            "id": contractor.id,
            "user_id": contractor.user_id,
            "name": contractor.user.full_name if contractor.user else "Unknown",
            "email": contractor.user.email if contractor.user else "Unknown",
            "company_name": contractor.company_name,
            "license_number": contractor.license_number,
            "specialization": contractor.specialization,
            "status": contractor.status,
            "complianceStatus": "active" if contractor.status == "ACTIVE" else "blocked",
            "rating": float(contractor.rating) if contractor.rating else 0.0,
            "total_jobs_completed": contractor.total_jobs_completed,
            "created_at": contractor.created_at.isoformat(),
            "updated_at": contractor.updated_at.isoformat()
        }
        contractor_list.append(contractor_dict)
    
    return contractor_list


@router.get("/users", response_model=List[dict])
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    search: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List all users for admin management"""
    from app.crud.auth import auth_crud
    
    users, total = await auth_crud.get_users(db, skip, limit, role, search)
    
    user_list = []
    for user in users:
        user_dict = {
            "id": user.id,
            "email": user.email,
            "name": user.full_name or user.email.split('@')[0],
            "role": user.role,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "avatarUrl": None,
            "trade": "General" if user.role == "CONTRACTOR" else None,
            "complianceStatus": "active" if user.is_active else "blocked"
        }
        user_list.append(user_dict)
    
    return user_list


@router.get("/meetings", response_model=List[dict])
async def list_admin_meetings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List admin meetings (mock implementation)"""
    # Mock meetings data
    meetings = []
    for i in range(1, min(limit + 1, 4)):
        meeting = {
            "id": i,
            "title": f"Admin Meeting {i}",
            "description": f"Weekly admin meeting {i}",
            "scheduled_date": (datetime.now() + timedelta(days=i)).isoformat(),
            "duration": 60,
            "attendees": ["admin@example.com", "manager@example.com"],
            "status": "SCHEDULED",
            "meeting_type": "WEEKLY",
            "created_at": datetime.now().isoformat()
        }
        meetings.append(meeting)
    
    return meetings[skip:skip + limit]


@router.post("/meetings", response_model=dict)
async def create_admin_meeting(
    title: str,
    description: Optional[str] = None,
    scheduled_date: datetime = None,
    duration: int = 60,
    attendees: List[str] = [],
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create admin meeting (mock implementation)"""
    meeting = {
        "id": 999,
        "title": title,
        "description": description,
        "scheduled_date": scheduled_date.isoformat() if scheduled_date else None,
        "duration": duration,
        "attendees": attendees,
        "status": "SCHEDULED",
        "created_by_id": admin_user.id,
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "message": "Meeting created successfully",
        "meeting": meeting
    }


@router.get("/disputes/statistics", response_model=dict)
async def get_dispute_statistics(
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dispute statistics for admin dashboard"""
    from app.crud.dispute import dispute_crud
    
    stats = await dispute_crud.get_dispute_statistics(db)
    return stats