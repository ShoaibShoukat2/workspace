"""
CSV-based Admin Endpoints
Admin functionality using CSV files
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List, Optional

from app.data.csv_data import (
    get_dashboard_stats, get_jobs, get_contractors, get_payouts, 
    get_disputes, update_payout_status, csv_manager
)
from datetime import datetime, date

router = APIRouter()

@router.get("/dashboard")
async def get_admin_dashboard():
    """Get admin dashboard data"""
    stats = get_dashboard_stats()
    
    # Add some mock data for charts and lists
    return {
        **stats,
        "revenue_data": [
            {"month": "Jan", "value": 4000},
            {"month": "Feb", "value": 3000},
            {"month": "Mar", "value": 2000},
            {"month": "Apr", "value": 2780},
            {"month": "May", "value": 1890},
            {"month": "Jun", "value": 2390},
            {"month": "Jul", "value": 3490}
        ],
        "job_stats": [
            {"name": "Open", "count": len([j for j in get_jobs() if j['status'] == 'Open'])},
            {"name": "In Progress", "count": len([j for j in get_jobs() if j['status'] == 'InProgress'])},
            {"name": "Completed", "count": len([j for j in get_jobs() if j['status'] == 'Complete'])},
            {"name": "Paid", "count": len([j for j in get_jobs() if j['status'] == 'Paid'])}
        ],
        "recent_contractors": get_contractors()[:5],
        "active_investors": []  # Mock empty for now
    }

@router.get("/jobs")
async def get_admin_jobs(status: Optional[str] = None):
    """Get all jobs for admin"""
    jobs = get_jobs(status=status)
    
    return {
        "jobs": jobs,
        "total": len(jobs)
    }

@router.get("/payouts")
async def get_admin_payouts(status: Optional[str] = None):
    """Get all payouts for admin"""
    payouts = get_payouts(status=status)
    
    # Add contractor info
    contractors = {c['id']: c for c in get_contractors()}
    
    for payout in payouts:
        contractor_id = payout['contractor_id']
        if contractor_id in contractors:
            payout['contractor_name'] = contractors[contractor_id]['full_name']
            payout['contractor_email'] = contractors[contractor_id]['email']
    
    return {
        "payouts": payouts,
        "total": len(payouts)
    }

@router.post("/payouts/{payout_id}/approve")
async def approve_payout(payout_id: int):
    """Approve a payout"""
    try:
        update_payout_status(payout_id, "COMPLETED", datetime.now().isoformat())
        return {"message": "Payout approved successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to approve payout: {str(e)}"
        )

@router.post("/payouts/{payout_id}/reject")
async def reject_payout(payout_id: int, data: Dict[str, Any]):
    """Reject a payout"""
    try:
        update_payout_status(payout_id, "REJECTED")
        return {"message": "Payout rejected successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to reject payout: {str(e)}"
        )

@router.get("/contractors")
async def get_admin_contractors():
    """Get all contractors"""
    contractors = get_contractors()
    return {
        "contractors": contractors,
        "total": len(contractors)
    }

@router.get("/users")
async def get_admin_users():
    """Get all users"""
    from app.data.csv_data import get_users
    
    users = get_users()
    return {
        "users": users,
        "total": len(users)
    }

@router.get("/disputes/statistics")
async def get_dispute_statistics():
    """Get dispute statistics"""
    disputes = get_disputes()
    
    return {
        "total_disputes": len(disputes),
        "open_disputes": len([d for d in disputes if d['status'] == 'Open']),
        "resolved_disputes": len([d for d in disputes if d['status'] == 'Resolved']),
        "pending_disputes": len([d for d in disputes if d['status'] == 'Pending'])
    }

@router.get("/meetings")
async def get_admin_meetings():
    """Get admin meetings (mock data)"""
    return {
        "meetings": [
            {
                "id": 1,
                "title": "Weekly Team Meeting",
                "date": "2024-12-25",
                "time": "10:00 AM",
                "attendees": ["admin@apex.inc", "fm@apex.inc"]
            }
        ],
        "total": 1
    }

@router.get("/leads")
async def get_admin_leads():
    """Get admin leads (mock data)"""
    return {
        "leads": [
            {
                "id": 1,
                "name": "John Potential",
                "email": "john@example.com",
                "phone": "555-0123",
                "status": "New",
                "source": "Website",
                "created_at": "2024-12-20"
            }
        ],
        "total": 1
    }