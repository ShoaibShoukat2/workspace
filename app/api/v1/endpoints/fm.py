"""
Facility Manager (FM) Dashboard Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.core.security import get_fm_user, get_current_active_user
from app.models.auth import User
from app.schemas.fm import (
    FMDashboardResponse, FMJobVisitResponse, FMJobVisitUpdate,
    ChangeOrderCreate, MaterialVerificationRequest, SiteVisitCreate
)
from app.crud.fm import fm_crud

router = APIRouter()


@router.get("/dashboard", response_model=dict)
async def fm_dashboard(
    fm_user: User = Depends(get_fm_user),
    db: AsyncSession = Depends(get_db)
):
    """Get FM dashboard overview"""
    dashboard_data = await fm_crud.get_fm_dashboard(db, fm_user.id)
    return dashboard_data


# Site Visit Management
@router.get("/site-visits", response_model=List[dict])
async def list_site_visits(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    fm_user: User = Depends(get_fm_user),
    db: AsyncSession = Depends(get_db)
):
    """List all site visits for FM"""
    visits = await fm_crud.get_site_visits(
        db, fm_user.id, skip, limit, status, date_from, date_to
    )
    
    visit_list = []
    for visit in visits:
        visit_dict = {
            "id": visit.id,
            "job_id": visit.job_id,
            "job_number": visit.job.job_number if visit.job else None,
            "propertyAddress": visit.job.location if visit.job else "Unknown",
            "customerName": visit.job.customer_name if visit.job else "Unknown",
            "trade": visit.job.title.split()[0].lower() if visit.job and visit.job.title else "general",
            "status": visit.job.status if visit.job else "unknown",
            "visitStatus": visit.status,
            "mandatorySiteVisit": True,  # All FM visits are mandatory
            "materialStatus": visit.material_status,
            "city": visit.job.location.split(',')[-2].strip() if visit.job and visit.job.location else "Unknown",
            "isProject": visit.is_project,
            "materials": visit.materials_list if visit.materials_list else [],
            "created_at": visit.created_at.isoformat(),
            "scheduled_date": visit.scheduled_date.isoformat() if visit.scheduled_date else None,
            "completed_date": visit.completed_date.isoformat() if visit.completed_date else None
        }
        visit_list.append(visit_dict)
    
    return visit_list


@router.get("/site-visits/{visit_id}", response_model=dict)
async def get_site_visit(
    visit_id: int,
    fm_user: User = Depends(get_fm_user),
    db: AsyncSession = Depends(get_db)
):
    """Get site visit details"""
    visit = await fm_crud.get_site_visit(db, visit_id, fm_user.id)
    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site visit not found"
        )
    
    return {
        "id": visit.id,
        "job_id": visit.job_id,
        "job": {
            "id": visit.job.id,
            "job_number": visit.job.job_number,
            "propertyAddress": visit.job.location,
            "customerName": visit.job.customer_name,
            "type": visit.job.title.split()[0].lower() if visit.job.title else "general",
            "trade": visit.job.title.split()[0].lower() if visit.job.title else "general",
            "status": visit.job.status,
            "magicToken": visit.job.magic_token
        },
        "status": visit.status,
        "material_status": visit.material_status,
        "measurements": visit.measurements,
        "scope_confirmed": visit.scope_confirmed,
        "photos_uploaded": visit.photos_uploaded,
        "tools_required": visit.tools_required,
        "labor_required": visit.labor_required,
        "estimated_time": visit.estimated_time,
        "safety_concerns": visit.safety_concerns,
        "materials": visit.materials_list if visit.materials_list else [],
        "signature_saved": visit.signature_saved,
        "created_at": visit.created_at.isoformat(),
        "updated_at": visit.updated_at.isoformat()
    }


@router.post("/site-visits", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_site_visit(
    visit_data: SiteVisitCreate,
    fm_user: User = Depends(get_fm_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new site visit"""
    visit = await fm_crud.create_site_visit(db, visit_data, fm_user.id)
    return {
        "message": "Site visit created successfully",
        "visit_id": visit.id
    }


@router.patch("/site-visits/{visit_id}", response_model=dict)
async def update_site_visit(
    visit_id: int,
    visit_update: FMJobVisitUpdate,
    fm_user: User = Depends(get_fm_user),
    db: AsyncSession = Depends(get_db)
):
    """Update site visit details"""
    success = await fm_crud.update_site_visit(
        db, visit_id, visit_update, fm_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site visit not found"
        )
    
    return {"message": "Site visit updated successfully"}


@router.post("/site-visits/{visit_id}/submit", response_model=dict)
async def submit_site_visit(
    visit_id: int,
    fm_user: User = Depends(get_fm_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit completed site visit"""
    success = await fm_crud.submit_site_visit(db, visit_id, fm_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site visit not found or not ready for submission"
        )
    
    return {"message": "Site visit submitted successfully"}


# Material Management
@router.post("/materials/verify", response_model=dict)
async def verify_materials(
    verification_data: MaterialVerificationRequest,
    fm_user: User = Depends(get_fm_user),
    db: AsyncSession = Depends(get_db)
):
    """Verify AI-generated materials list"""
    success = await fm_crud.verify_materials(
        db, verification_data, fm_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job or materials not found"
        )
    
    return {"message": "Materials verified successfully"}


@router.get("/materials/ai-suggestions/{job_id}", response_model=List[dict])
async def get_ai_material_suggestions(
    job_id: int,
    fm_user: User = Depends(get_fm_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI-generated material suggestions for a job"""
    materials = await fm_crud.get_ai_material_suggestions(db, job_id)
    return materials


# Change Order Management
@router.post("/change-orders", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_change_order(
    change_order_data: ChangeOrderCreate,
    fm_user: User = Depends(get_fm_user),
    db: AsyncSession = Depends(get_db)
):
    """Create change order request"""
    change_order = await fm_crud.create_change_order(
        db, change_order_data, fm_user.id
    )
    
    return {
        "message": "Change order request created successfully",
        "change_order_id": change_order.id,
        "dispute_id": change_order.dispute_id  # Change orders create disputes for approval
    }


@router.get("/change-orders", response_model=List[dict])
async def list_change_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    fm_user: User = Depends(get_fm_user),
    db: AsyncSession = Depends(get_db)
):
    """List change orders created by FM"""
    change_orders = await fm_crud.get_change_orders(
        db, fm_user.id, skip, limit, status
    )
    
    change_order_list = []
    for co in change_orders:
        co_dict = {
            "id": co.id,
            "job_id": co.job_id,
            "job_number": co.job.job_number if co.job else None,
            "propertyAddress": co.job.location if co.job else "Unknown",
            "customerName": co.job.customer_name if co.job else "Unknown",
            "reason": co.reason,
            "line_items": co.line_items,
            "total_amount": float(co.total_amount),
            "status": co.status,
            "dispute_id": co.dispute_id,
            "created_at": co.created_at.isoformat(),
            "updated_at": co.updated_at.isoformat()
        }
        change_order_list.append(co_dict)
    
    return change_order_list


@router.get("/change-orders/{change_order_id}", response_model=dict)
async def get_change_order(
    change_order_id: int,
    fm_user: User = Depends(get_fm_user),
    db: AsyncSession = Depends(get_db)
):
    """Get change order details"""
    change_order = await fm_crud.get_change_order(db, change_order_id, fm_user.id)
    if not change_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Change order not found"
        )
    
    return {
        "id": change_order.id,
        "job_id": change_order.job_id,
        "job": {
            "id": change_order.job.id,
            "job_number": change_order.job.job_number,
            "propertyAddress": change_order.job.location,
            "customerName": change_order.job.customer_name,
            "trade": change_order.job.title.split()[0].lower() if change_order.job.title else "general"
        },
        "reason": change_order.reason,
        "line_items": change_order.line_items,
        "total_amount": float(change_order.total_amount),
        "status": change_order.status,
        "dispute_id": change_order.dispute_id,
        "created_by_id": change_order.created_by_id,
        "created_at": change_order.created_at.isoformat(),
        "updated_at": change_order.updated_at.isoformat()
    }


# Job Assignment and Management
@router.get("/jobs/assigned", response_model=List[dict])
async def get_assigned_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    fm_user: User = Depends(get_fm_user),
    db: AsyncSession = Depends(get_db)
):
    """Get jobs assigned to FM for site visits"""
    jobs = await fm_crud.get_assigned_jobs(
        db, fm_user.id, skip, limit, status
    )
    
    job_list = []
    for job in jobs:
        job_dict = {
            "id": job.id,
            "job_number": job.job_number,
            "propertyAddress": job.location,
            "customerName": job.customer_name,
            "type": job.title.split()[0].lower() if job.title else "general",
            "trade": job.title.split()[0].lower() if job.title else "general",
            "status": job.status,
            "assignedContractorId": job.assigned_to_id,
            "assignedContractorName": job.assigned_to.full_name if job.assigned_to else None,
            "mandatorySiteVisit": True,
            "visitStatus": "Pending",  # Would be determined from site visit records
            "materialStatus": "AI Generated",  # Default status
            "city": job.location.split(',')[-2].strip() if job.location else "Unknown",
            "isProject": job.estimated_cost and job.estimated_cost > 5000,
            "materials": [],
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat()
        }
        job_list.append(job_dict)
    
    return job_list


# Quote Generation
@router.post("/quotes/generate", response_model=dict)
async def generate_quote(
    job_id: int,
    materials: List[dict],
    labor_hours: float,
    labor_rate: float = 80.0,
    fm_user: User = Depends(get_fm_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate quote from verified materials and labor"""
    quote = await fm_crud.generate_quote(
        db, job_id, materials, labor_hours, labor_rate, fm_user.id
    )
    
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return {
        "message": "Quote generated successfully",
        "quote_id": quote.id,
        "total_amount": float(quote.total_amount),
        "magic_link": f"/quote/{quote.magic_token}"
    }


# Analytics and Reports
@router.get("/analytics/overview", response_model=dict)
async def get_fm_analytics(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    fm_user: User = Depends(get_fm_user),
    db: AsyncSession = Depends(get_db)
):
    """Get FM analytics overview"""
    analytics = await fm_crud.get_fm_analytics(db, fm_user.id, date_from, date_to)
    return analytics


@router.get("/performance/metrics", response_model=dict)
async def get_fm_performance_metrics(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    fm_user: User = Depends(get_fm_user),
    db: AsyncSession = Depends(get_db)
):
    """Get FM performance metrics"""
    metrics = await fm_crud.get_performance_metrics(db, fm_user.id, date_from, date_to)
    return metrics


# Photo Upload
@router.post("/photos/upload", response_model=dict)
async def upload_site_photos(
    visit_id: int,
    photo_type: str = "before",  # before, after, progress
    fm_user: User = Depends(get_fm_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload site visit photos (mock implementation)"""
    # In real implementation, this would handle file uploads
    success = await fm_crud.upload_photos(db, visit_id, photo_type, fm_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site visit not found"
        )
    
    return {
        "message": "Photos uploaded successfully",
        "photo_count": 3,  # Mock count
        "photo_type": photo_type
    }


# Map View Data
@router.get("/map/jobs", response_model=List[dict])
async def get_map_jobs(
    fm_user: User = Depends(get_fm_user),
    db: AsyncSession = Depends(get_db)
):
    """Get jobs for map view with coordinates"""
    jobs = await fm_crud.get_map_jobs(db, fm_user.id)
    
    map_jobs = []
    for job in jobs:
        # Mock coordinates - in real implementation, would geocode addresses
        lat = 40.7128 + (job.id * 0.001)  # Mock latitude
        lng = -74.0060 + (job.id * 0.001)  # Mock longitude
        
        map_jobs.append({
            "id": job.id,
            "propertyAddress": job.location,
            "customerName": job.customer_name,
            "status": job.status,
            "coordinates": {"lat": lat, "lng": lng},
            "visitStatus": "Pending",
            "priority": "normal"
        })
    
    return map_jobs