"""
API Router
Main API router that includes all endpoint modules
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, workspaces, jobs, contractors, customers, admin,
    profiles, legacy, investors, disputes, fm
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(contractors.router, prefix="/contractors", tags=["Contractors"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(fm.router, prefix="/fm", tags=["Facility Manager"])
api_router.include_router(investors.router, prefix="/investors", tags=["Investors"])
api_router.include_router(disputes.router, prefix="/disputes", tags=["Disputes"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["Profiles"])

# Legacy endpoints for frontend compatibility (flat structure)
api_router.include_router(legacy.router, tags=["Legacy Compatibility"])