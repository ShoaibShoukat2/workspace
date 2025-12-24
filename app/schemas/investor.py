"""
Investor Pydantic Schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal


class InvestorDashboardResponse(BaseModel):
    """Investor dashboard response"""
    total_investment: float = Field(..., description="Total investment amount")
    current_balance: float = Field(..., description="Current balance")
    total_revenue: float = Field(..., description="Total revenue generated")
    total_payouts: float = Field(..., description="Total payouts received")
    roi_percentage: float = Field(..., description="Return on investment percentage")
    active_jobs: int = Field(..., description="Number of active jobs")
    completed_jobs: int = Field(..., description="Number of completed jobs")
    pending_payouts: float = Field(..., description="Pending payout amount")
    
    # Performance metrics
    monthly_revenue: List[Dict[str, Any]] = Field(default_factory=list, description="Monthly revenue data")
    job_performance: Dict[str, Any] = Field(default_factory=dict, description="Job performance metrics")
    market_insights: Dict[str, Any] = Field(default_factory=dict, description="Market insights")
    
    class Config:
        from_attributes = True


class InvestorJobBreakdownResponse(BaseModel):
    """Investor job breakdown response"""
    job_id: int = Field(..., description="Job ID")
    job_number: str = Field(..., description="Job number")
    property_address: str = Field(..., description="Property address")
    job_type: str = Field(..., description="Job type")
    completion_date: Optional[datetime] = Field(None, description="Job completion date")
    
    # Financial breakdown
    total_revenue: float = Field(..., description="Total job revenue")
    total_expenses: float = Field(..., description="Total job expenses")
    platform_fee: float = Field(..., description="Platform fee")
    net_profit: float = Field(..., description="Net profit")
    investor_share: float = Field(..., description="Investor share amount")
    investor_percentage: float = Field(..., description="Investor share percentage")
    
    # Performance metrics
    roi: Optional[float] = Field(None, description="Return on investment for this job")
    profit_margin: Optional[float] = Field(None, description="Profit margin percentage")
    
    class Config:
        from_attributes = True


class InvestorPayoutResponse(BaseModel):
    """Investor payout response"""
    id: int = Field(..., description="Payout ID")
    amount: float = Field(..., description="Payout amount")
    period_start: date = Field(..., description="Payout period start date")
    period_end: date = Field(..., description="Payout period end date")
    status: str = Field(..., description="Payout status")
    created_at: datetime = Field(..., description="Payout creation date")
    paid_at: Optional[datetime] = Field(None, description="Payment date")
    
    # Additional details
    job_count: int = Field(..., description="Number of jobs included")
    total_revenue: float = Field(..., description="Total revenue for period")
    notes: Optional[str] = Field(None, description="Payout notes")
    
    class Config:
        from_attributes = True


class InvestorReportResponse(BaseModel):
    """Investor report response"""
    id: int = Field(..., description="Report ID")
    report_type: str = Field(..., description="Report type")
    title: str = Field(..., description="Report title")
    description: Optional[str] = Field(None, description="Report description")
    status: str = Field(..., description="Report status")
    created_at: datetime = Field(..., description="Report creation date")
    completed_at: Optional[datetime] = Field(None, description="Report completion date")
    
    # Report data
    file_url: Optional[str] = Field(None, description="Report file URL")
    data: Optional[Dict[str, Any]] = Field(None, description="Report data")
    
    class Config:
        from_attributes = True


class InvestorCreate(BaseModel):
    """Create investor schema"""
    user_id: int = Field(..., description="User ID")
    investment_amount: float = Field(..., gt=0, description="Initial investment amount")
    split_percentage: float = Field(..., ge=0, le=100, description="Profit split percentage")
    investment_date: Optional[date] = Field(None, description="Investment date")
    notes: Optional[str] = Field(None, max_length=1000, description="Investment notes")


class InvestorUpdate(BaseModel):
    """Update investor schema"""
    investment_amount: Optional[float] = Field(None, gt=0, description="Investment amount")
    split_percentage: Optional[float] = Field(None, ge=0, le=100, description="Profit split percentage")
    status: Optional[str] = Field(None, description="Investor status")
    notes: Optional[str] = Field(None, max_length=1000, description="Investment notes")


class InvestorResponse(BaseModel):
    """Investor response schema"""
    id: int = Field(..., description="Investor ID")
    user_id: int = Field(..., description="User ID")
    investment_amount: float = Field(..., description="Investment amount")
    split_percentage: float = Field(..., description="Profit split percentage")
    status: str = Field(..., description="Investor status")
    investment_date: date = Field(..., description="Investment date")
    
    # Calculated fields
    total_revenue: float = Field(..., description="Total revenue generated")
    total_payouts: float = Field(..., description="Total payouts received")
    current_balance: float = Field(..., description="Current balance")
    roi_percentage: float = Field(..., description="ROI percentage")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class InvestorListResponse(BaseModel):
    """Investor list response"""
    investors: List[InvestorResponse] = Field(..., description="List of investors")
    total: int = Field(..., description="Total number of investors")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


class InvestorPortfolioResponse(BaseModel):
    """Investor portfolio response"""
    total_investment: float = Field(..., description="Total investment")
    current_value: float = Field(..., description="Current portfolio value")
    total_returns: float = Field(..., description="Total returns")
    roi_percentage: float = Field(..., description="ROI percentage")
    
    # Asset breakdown
    active_investments: int = Field(..., description="Number of active investments")
    completed_investments: int = Field(..., description="Number of completed investments")
    
    # Performance over time
    performance_history: List[Dict[str, Any]] = Field(default_factory=list, description="Performance history")
    
    # Risk metrics
    risk_score: Optional[float] = Field(None, description="Portfolio risk score")
    diversification_score: Optional[float] = Field(None, description="Diversification score")
    
    class Config:
        from_attributes = True


class InvestorPayoutCreate(BaseModel):
    """Create investor payout schema"""
    investor_id: int = Field(..., description="Investor ID")
    amount: float = Field(..., gt=0, description="Payout amount")
    period_start: date = Field(..., description="Payout period start")
    period_end: date = Field(..., description="Payout period end")
    notes: Optional[str] = Field(None, max_length=1000, description="Payout notes")
    
    @validator('period_end')
    def validate_period_end(cls, v, values):
        if 'period_start' in values and v <= values['period_start']:
            raise ValueError('Period end must be after period start')
        return v


class InvestorReportCreate(BaseModel):
    """Create investor report schema"""
    report_type: str = Field(..., description="Report type")
    title: str = Field(..., max_length=200, description="Report title")
    description: Optional[str] = Field(None, max_length=1000, description="Report description")
    date_from: Optional[date] = Field(None, description="Report start date")
    date_to: Optional[date] = Field(None, description="Report end date")
    filters: Optional[Dict[str, Any]] = Field(None, description="Report filters")
    
    @validator('date_to')
    def validate_date_to(cls, v, values):
        if 'date_from' in values and values['date_from'] and v and v <= values['date_from']:
            raise ValueError('End date must be after start date')
        return v