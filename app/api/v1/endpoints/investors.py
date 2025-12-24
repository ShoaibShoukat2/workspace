"""
Investor Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date, datetime

from app.core.database import get_db
from app.core.security import get_current_active_user, get_investor_user, get_admin_user
from app.models.auth import User
from app.schemas.investor import (
    InvestorDashboardResponse, InvestorJobBreakdownResponse, 
    InvestorReportResponse, InvestorPayoutResponse, InvestorCreate, InvestorUpdate
)
from app.crud.investor import investor_crud

router = APIRouter()


@router.get("/dashboard", response_model=InvestorDashboardResponse)
async def investor_dashboard(
    investor_user: User = Depends(get_investor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get investor dashboard data"""
    dashboard_data = await investor_crud.get_investor_dashboard(db, investor_user.id)
    return InvestorDashboardResponse(**dashboard_data)


@router.get("/job-breakdowns", response_model=List[InvestorJobBreakdownResponse])
async def get_job_breakdowns(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    job_type: Optional[str] = None,
    investor_user: User = Depends(get_investor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get job breakdowns for investor"""
    breakdowns = await investor_crud.get_job_breakdowns(
        db, investor_user.id, skip, limit, date_from, date_to, job_type
    )
    return [InvestorJobBreakdownResponse(**breakdown) for breakdown in breakdowns]


@router.get("/performance", response_model=dict)
async def get_investor_performance(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    investor_user: User = Depends(get_investor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get investor performance metrics"""
    performance = await investor_crud.get_investor_performance(
        db, investor_user.id, date_from, date_to
    )
    return performance


@router.get("/payouts", response_model=List[InvestorPayoutResponse])
async def get_investor_payouts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    investor_user: User = Depends(get_investor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get investor payout history"""
    payouts = await investor_crud.get_investor_payouts(
        db, investor_user.id, skip, limit, status, date_from, date_to
    )
    return [InvestorPayoutResponse(**payout) for payout in payouts]


@router.get("/reports", response_model=List[InvestorReportResponse])
async def get_investor_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    report_type: Optional[str] = None,
    investor_user: User = Depends(get_investor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get investor reports"""
    reports = await investor_crud.get_investor_reports(
        db, investor_user.id, skip, limit, report_type
    )
    return [InvestorReportResponse(**report) for report in reports]


@router.post("/reports/generate", response_model=dict)
async def generate_investor_report(
    report_type: str,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    filters: Optional[dict] = None,
    investor_user: User = Depends(get_investor_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate new investor report"""
    report = await investor_crud.generate_investor_report(
        db, investor_user.id, report_type, date_from, date_to, filters
    )
    
    return {
        "message": "Report generation started",
        "report_id": report.id,
        "status": "processing"
    }


@router.get("/portfolio", response_model=dict)
async def get_investor_portfolio(
    investor_user: User = Depends(get_investor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get investor portfolio overview"""
    portfolio = await investor_crud.get_investor_portfolio(db, investor_user.id)
    return portfolio


@router.get("/roi-analysis", response_model=dict)
async def get_roi_analysis(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    group_by: str = "month",  # day, week, month, quarter, year
    investor_user: User = Depends(get_investor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get ROI analysis for investor"""
    roi_data = await investor_crud.get_roi_analysis(
        db, investor_user.id, date_from, date_to, group_by
    )
    return roi_data


@router.get("/market-insights", response_model=dict)
async def get_market_insights(
    investor_user: User = Depends(get_investor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get market insights for investor"""
    insights = await investor_crud.get_market_insights(db, investor_user.id)
    return insights


# Admin endpoints for investor management
@router.get("/", response_model=List[dict])
async def list_all_investors(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List all investors (Admin only)"""
    investors = await investor_crud.get_all_investors(db, skip, limit, search)
    return investors


@router.get("/{investor_id}/performance", response_model=dict)
async def get_investor_performance_admin(
    investor_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get investor performance (Admin view)"""
    performance = await investor_crud.get_investor_performance(
        db, investor_id, date_from, date_to
    )
    return performance


@router.post("/{investor_id}/payout", response_model=dict)
async def create_investor_payout(
    investor_id: int,
    amount: float,
    period_start: date,
    period_end: date,
    notes: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create investor payout (Admin only)"""
    payout = await investor_crud.create_investor_payout(
        db, investor_id, amount, period_start, period_end, notes, admin_user.id
    )
    
    return {
        "message": "Investor payout created successfully",
        "payout_id": payout.id,
        "amount": amount
    }


@router.patch("/{investor_id}/split-percentage", response_model=dict)
async def update_investor_split(
    investor_id: int,
    split_percentage: float,
    effective_date: Optional[date] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update investor split percentage (Admin only)"""
    if not (0 <= split_percentage <= 100):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Split percentage must be between 0 and 100"
        )
    
    success = await investor_crud.update_investor_split(
        db, investor_id, split_percentage, effective_date, admin_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investor not found"
        )
    
    return {
        "message": "Investor split percentage updated successfully",
        "split_percentage": split_percentage
    }


@router.get("/properties", response_model=List[dict])
async def get_investor_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    investor_user: User = Depends(get_investor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get investor properties"""
    properties = await investor_crud.get_investor_properties(
        db, investor_user.id, skip, limit
    )
    return properties


@router.get("/properties/{property_id}", response_model=dict)
async def get_property_details(
    property_id: int,
    investor_user: User = Depends(get_investor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get property details for investor"""
    property_details = await investor_crud.get_property_details(
        db, property_id, investor_user.id
    )
    
    if not property_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    return property_details


@router.get("/leads", response_model=List[dict])
async def get_investor_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    investor_user: User = Depends(get_investor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get investor leads"""
    leads = await investor_crud.get_investor_leads(
        db, investor_user.id, skip, limit, status
    )
    return leads


@router.post("/leads", response_model=dict)
async def create_investor_lead(
    lead_data: dict,
    investor_user: User = Depends(get_investor_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new investor lead"""
    lead = await investor_crud.create_investor_lead(
        db, investor_user.id, lead_data
    )
    
    return {
        "message": "Lead created successfully",
        "lead_id": lead.get("id"),
        "status": "created"
    }


@router.get("/earnings-breakdown", response_model=dict)
async def get_earnings_breakdown(
    investor_user: User = Depends(get_investor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed earnings breakdown"""
    breakdown = await investor_crud.get_earnings_breakdown(db, investor_user.id)
    return breakdown


@router.get("/allocation-data", response_model=List[dict])
async def get_portfolio_allocation(
    investor_user: User = Depends(get_investor_user),
    db: AsyncSession = Depends(get_db)
):
    """Get portfolio allocation data for charts"""
    allocation = await investor_crud.get_portfolio_allocation(db, investor_user.id)
    return allocation


# Additional endpoints for investor management
@router.get("/{investor_id}/summary", response_model=dict)
async def get_investor_summary(
    investor_id: int,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get investor summary statistics (Admin only)"""
    summary = await investor_crud.get_investor_summary_stats(db, investor_id)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investor not found"
        )
    
    return summary


@router.post("/", response_model=dict)
async def create_investor(
    investor_data: InvestorCreate,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new investor (Admin only)"""
    try:
        investor = await investor_crud.create_investor(db, investor_data)
        return {
            "message": "Investor created successfully",
            "investor_id": investor.id,
            "user_id": investor.user_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create investor: {str(e)}"
        )


@router.patch("/{investor_id}", response_model=dict)
async def update_investor(
    investor_id: int,
    investor_data: InvestorUpdate,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update investor (Admin only)"""
    investor = await investor_crud.update_investor(db, investor_id, investor_data)
    
    if not investor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investor not found"
        )
    
    return {
        "message": "Investor updated successfully",
        "investor_id": investor.id
    }


@router.post("/{investor_id}/job-investments", response_model=dict)
async def create_job_investment(
    investor_id: int,
    job_id: int,
    investment_amount: float,
    split_percentage: Optional[float] = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create job investment (Admin only)"""
    try:
        job_investment = await investor_crud.create_job_investment(
            db, job_id, investor_id, investment_amount, split_percentage
        )
        return {
            "message": "Job investment created successfully",
            "job_investment_id": job_investment.id,
            "job_id": job_id,
            "investor_id": investor_id,
            "investment_amount": investment_amount
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create job investment: {str(e)}"
        )