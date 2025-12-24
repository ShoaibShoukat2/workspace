"""
CSV-based API Router
Simple API using CSV files instead of database
"""
from fastapi import APIRouter

from app.api.v1.endpoints.csv_auth import router as auth_router
from app.api.v1.endpoints.csv_admin import router as admin_router

# Create main API router
api_router = APIRouter()

# Include auth routes
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Include admin routes  
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])

# Legacy routes for compatibility
api_router.include_router(auth_router, tags=["Legacy Auth"])  # For /login, /profiles endpoints

# Add other dashboard endpoints
@api_router.get("/contractors/dashboard/overview")
async def contractor_dashboard():
    """Contractor dashboard overview"""
    from app.data.csv_data import get_jobs, get_payouts
    
    # Mock contractor ID = 1
    contractor_jobs = get_jobs(contractor_id=1)
    contractor_payouts = get_payouts(contractor_id=1)
    
    return {
        "stats": {
            "active_jobs": len([j for j in contractor_jobs if j['status'] in ['Open', 'InProgress']]),
            "completed_jobs": len([j for j in contractor_jobs if j['status'] == 'Complete']),
            "total_earnings": sum(float(p['amount']) for p in contractor_payouts if p['status'] == 'COMPLETED'),
            "pending_payouts": sum(float(p['amount']) for p in contractor_payouts if p['status'] == 'PENDING')
        },
        "recent_jobs": contractor_jobs[:5],
        "compliance_status": "active"
    }

@api_router.get("/contractors/jobs/available")
async def available_jobs():
    """Get available jobs for contractors"""
    jobs = get_jobs(status='Open')
    return {
        "jobs": jobs,
        "total": len(jobs)
    }

@api_router.get("/contractors/jobs/my-jobs")
async def contractor_jobs():
    """Get contractor's jobs"""
    # Mock contractor ID = 1
    jobs = get_jobs(contractor_id=1)
    return {
        "jobs": jobs,
        "total": len(jobs)
    }

@api_router.get("/contractors/wallet")
async def contractor_wallet():
    """Get contractor wallet info"""
    # Mock contractor ID = 1
    payouts = get_payouts(contractor_id=1)
    
    total_paid = sum(float(p['amount']) for p in payouts if p['status'] == 'COMPLETED')
    pending_amount = sum(float(p['amount']) for p in payouts if p['status'] == 'PENDING')
    
    return {
        "total_paid": total_paid,
        "pending_amount": pending_amount,
        "available_balance": total_paid
    }

@api_router.get("/contractors/payouts")
async def contractor_payouts():
    """Get contractor payouts"""
    # Mock contractor ID = 1
    payouts = get_payouts(contractor_id=1)
    return {
        "payouts": payouts,
        "total": len(payouts)
    }

@api_router.get("/customers/dashboard")
async def customer_dashboard():
    """Customer dashboard"""
    jobs = get_jobs()
    active_job = next((j for j in jobs if j['status'] in ['Open', 'InProgress']), None)
    
    return {
        "active_job": active_job,
        "total_jobs": len(jobs),
        "completed_jobs": len([j for j in jobs if j['status'] == 'Complete'])
    }

@api_router.get("/customers/jobs")
async def customer_jobs():
    """Get customer jobs"""
    jobs = get_jobs()
    return {
        "jobs": jobs,
        "total": len(jobs)
    }

@api_router.get("/customers/jobs/{job_id}")
async def get_customer_job(job_id: int):
    """Get specific customer job"""
    jobs = get_jobs()
    job = next((j for j in jobs if int(j['id']) == job_id), None)
    
    if not job:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

@api_router.get("/customers/jobs/{job_id}/contractor-location")
async def get_contractor_location(job_id: int):
    """Get contractor location for job"""
    # Mock location data
    return {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "last_updated": "2024-12-24T10:30:00Z",
        "status": "En Route"
    }

@api_router.get("/investors/dashboard")
async def investor_dashboard():
    """Investor dashboard"""
    return {
        "total_investment": 50000.0,
        "total_returns": 12500.0,
        "active_projects": 3,
        "roi_percentage": 25.0,
        "investor": {
            "name": "Bob Investor",
            "email": "investor@apex.inc"
        },
        "roi_data": [
            {"month": "Jan", "value": 12},
            {"month": "Feb", "value": 19},
            {"month": "Mar", "value": 15},
            {"month": "Apr", "value": 22},
            {"month": "May", "value": 28},
            {"month": "Jun", "value": 25}
        ],
        "allocation_data": [
            {"name": "Flips", "value": 65, "color": "#8b5cf6"},
            {"name": "Rentals", "value": 25, "color": "#ec4899"},
            {"name": "Commercial", "value": 10, "color": "#3b82f6"}
        ]
    }

@api_router.get("/investors/reports")
async def investor_reports():
    """Get investor reports"""
    return {
        "reports": [
            {
                "id": 1,
                "title": "Q4 2024 Performance Report",
                "type": "Quarterly",
                "status": "Ready",
                "created_at": "2024-12-20",
                "file_size": "2.4 MB"
            }
        ],
        "total": 1
    }

@api_router.get("/fm/dashboard")
async def fm_dashboard():
    """FM dashboard"""
    return {
        "pending_visits": 2,
        "active_jobs": 5,
        "completed_today": 1,
        "total_visits": 15
    }

@api_router.get("/fm/jobs/assigned")
async def fm_assigned_jobs():
    """Get FM assigned jobs"""
    jobs = get_jobs()
    return {
        "jobs": jobs[:3],  # Mock assigned jobs
        "total": 3
    }