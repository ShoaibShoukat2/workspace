"""
Investor CRUD Operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc, text
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
import uuid

from app.models.auth import User
from app.models.workspace import (
    Investor, InvestorPayout, InvestorReport, JobInvestment, 
    InvestorSplitHistory, Job, Workspace
)
from app.schemas.investor import (
    InvestorCreate, InvestorUpdate, InvestorPayoutCreate, InvestorReportCreate
)


class InvestorCRUD:
    """Investor CRUD operations"""
    
    async def create_investor(
        self, 
        db: AsyncSession, 
        investor_data: InvestorCreate
    ) -> Investor:
        """Create a new investor"""
        investor = Investor(
            user_id=investor_data.user_id,
            investment_amount=investor_data.investment_amount,
            split_percentage=investor_data.split_percentage,
            investment_date=investor_data.investment_date or date.today(),
            notes=investor_data.notes
        )
        
        db.add(investor)
        await db.commit()
        await db.refresh(investor)
        return investor
    
    async def get_investor_by_id(self, db: AsyncSession, investor_id: int) -> Optional[Investor]:
        """Get investor by ID"""
        result = await db.execute(
            select(Investor)
            .options(joinedload(Investor.user))
            .where(Investor.id == investor_id)
        )
        return result.scalar_one_or_none()
    
    async def get_investor_by_user_id(self, db: AsyncSession, user_id: int) -> Optional[Investor]:
        """Get investor by user ID"""
        result = await db.execute(
            select(Investor)
            .options(joinedload(Investor.user))
            .where(Investor.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def update_investor(
        self, 
        db: AsyncSession, 
        investor_id: int, 
        investor_data: InvestorUpdate
    ) -> Optional[Investor]:
        """Update investor"""
        result = await db.execute(
            select(Investor).where(Investor.id == investor_id)
        )
        investor = result.scalar_one_or_none()
        
        if not investor:
            return None
        
        update_data = investor_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(investor, field, value)
        
        await db.commit()
        await db.refresh(investor)
        return investor
    
    async def get_investor_dashboard(self, db: AsyncSession, investor_id: int) -> Dict[str, Any]:
        """Get investor dashboard data"""
        investor = await self.get_investor_by_id(db, investor_id)
        if not investor:
            return {}
        
        # Get job investments for this investor
        job_investments_result = await db.execute(
            select(JobInvestment)
            .options(joinedload(JobInvestment.job))
            .where(JobInvestment.investor_id == investor_id)
        )
        job_investments = job_investments_result.scalars().all()
        
        # Calculate metrics
        active_jobs = len([ji for ji in job_investments if ji.status == "ACTIVE"])
        completed_jobs = len([ji for ji in job_investments if ji.status == "COMPLETED"])
        
        # Get pending payouts
        pending_payouts_result = await db.execute(
            select(func.coalesce(func.sum(InvestorPayout.amount), 0))
            .where(
                and_(
                    InvestorPayout.investor_id == investor_id,
                    InvestorPayout.status == "PENDING"
                )
            )
        )
        pending_payouts = float(pending_payouts_result.scalar() or 0)
        
        # Calculate monthly revenue (last 6 months)
        monthly_revenue = []
        for i in range(6):
            month_start = date.today().replace(day=1) - timedelta(days=i*30)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            month_revenue_result = await db.execute(
                select(func.coalesce(func.sum(JobInvestment.investor_share), 0))
                .join(Job)
                .where(
                    and_(
                        JobInvestment.investor_id == investor_id,
                        Job.completed_date.between(month_start, month_end)
                    )
                )
            )
            month_revenue = float(month_revenue_result.scalar() or 0)
            
            monthly_revenue.insert(0, {
                "month": month_start.strftime("%b"),
                "revenue": month_revenue
            })
        
        # Calculate performance metrics
        total_jobs = len(job_investments)
        completion_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
        
        avg_profit_margin_result = await db.execute(
            select(func.avg(JobInvestment.profit_margin))
            .where(
                and_(
                    JobInvestment.investor_id == investor_id,
                    JobInvestment.status == "COMPLETED"
                )
            )
        )
        avg_profit_margin = float(avg_profit_margin_result.scalar() or 0)
        
        return {
            "total_investment": float(investor.investment_amount),
            "current_balance": float(investor.current_balance),
            "total_revenue": float(investor.total_revenue),
            "total_payouts": float(investor.total_payouts),
            "roi_percentage": float(investor.roi_percentage),
            "active_jobs": active_jobs,
            "completed_jobs": completed_jobs,
            "pending_payouts": pending_payouts,
            "monthly_revenue": monthly_revenue,
            "job_performance": {
                "completion_rate": completion_rate,
                "average_profit_margin": avg_profit_margin,
                "customer_satisfaction": 4.7  # This would come from job ratings
            },
            "market_insights": {
                "market_growth": 12.5,
                "sector_performance": "strong",
                "recommended_actions": [
                    "Increase investment in painting jobs", 
                    "Consider expansion to new markets"
                ]
            }
        }
    
    async def get_job_breakdowns(
        self, 
        db: AsyncSession, 
        investor_id: int,
        skip: int = 0,
        limit: int = 20,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        job_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get job breakdowns for investor"""
        query = (
            select(JobInvestment)
            .options(joinedload(JobInvestment.job))
            .where(JobInvestment.investor_id == investor_id)
        )
        
        # Apply filters
        if date_from:
            query = query.join(Job).where(Job.completed_date >= date_from)
        if date_to:
            query = query.join(Job).where(Job.completed_date <= date_to)
        if job_type:
            query = query.join(Job).where(Job.title.ilike(f"%{job_type}%"))
        
        query = query.offset(skip).limit(limit).order_by(desc(JobInvestment.created_at))
        
        result = await db.execute(query)
        job_investments = result.scalars().all()
        
        breakdowns = []
        for ji in job_investments:
            breakdown = {
                "job_id": ji.job.id,
                "job_number": ji.job.job_number,
                "property_address": ji.job.location or "N/A",
                "job_type": ji.job.title,
                "completion_date": ji.job.completed_date,
                "total_revenue": float(ji.total_revenue),
                "total_expenses": float(ji.total_expenses),
                "platform_fee": float(ji.platform_fee),
                "net_profit": float(ji.net_profit),
                "investor_share": float(ji.investor_share),
                "investor_percentage": float(ji.split_percentage),
                "roi": float(ji.roi_percentage),
                "profit_margin": float(ji.profit_margin)
            }
            breakdowns.append(breakdown)
        
        return breakdowns
    
    async def get_investor_performance(
        self,
        db: AsyncSession,
        investor_id: int,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get investor performance metrics"""
        investor = await self.get_investor_by_id(db, investor_id)
        if not investor:
            return {}
        
        # Build query for job investments
        query = select(JobInvestment).where(JobInvestment.investor_id == investor_id)
        
        if date_from or date_to:
            query = query.join(Job)
            if date_from:
                query = query.where(Job.completed_date >= date_from)
            if date_to:
                query = query.where(Job.completed_date <= date_to)
        
        result = await db.execute(query)
        job_investments = result.scalars().all()
        
        # Calculate metrics
        total_returns = sum(float(ji.investor_share) for ji in job_investments)
        total_investment = float(investor.investment_amount)
        roi_percentage = (total_returns / total_investment * 100) if total_investment > 0 else 0
        
        # Calculate annualized return (simplified)
        days_invested = (date.today() - investor.investment_date).days
        years_invested = days_invested / 365.25 if days_invested > 0 else 1
        annualized_return = (roi_percentage / years_invested) if years_invested > 0 else 0
        
        # Win rate (jobs with positive ROI)
        positive_roi_jobs = len([ji for ji in job_investments if ji.roi_percentage > 0])
        win_rate = (positive_roi_jobs / len(job_investments) * 100) if job_investments else 0
        
        # Average job return
        avg_job_return = (total_returns / len(job_investments)) if job_investments else 0
        
        # Performance over time (last 6 months)
        performance_history = []
        cumulative_value = total_investment
        
        for i in range(6):
            month_start = date.today().replace(day=1) - timedelta(days=i*30)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            month_returns_result = await db.execute(
                select(func.coalesce(func.sum(JobInvestment.investor_share), 0))
                .join(Job)
                .where(
                    and_(
                        JobInvestment.investor_id == investor_id,
                        Job.completed_date.between(month_start, month_end)
                    )
                )
            )
            month_returns = float(month_returns_result.scalar() or 0)
            
            cumulative_value += month_returns
            month_return_pct = (month_returns / total_investment * 100) if total_investment > 0 else 0
            
            performance_history.insert(0, {
                "date": month_start.strftime("%Y-%m"),
                "value": cumulative_value,
                "return": month_return_pct
            })
        
        return {
            "total_investment": total_investment,
            "total_returns": total_returns,
            "roi_percentage": roi_percentage,
            "annualized_return": annualized_return,
            "sharpe_ratio": 1.2,  # Would need more complex calculation
            "max_drawdown": -5.2,  # Would need historical tracking
            "win_rate": win_rate,
            "average_job_return": avg_job_return,
            "best_performing_sector": "painting",  # Would need job categorization
            "performance_over_time": performance_history
        }
    
    async def get_investor_payouts(
        self,
        db: AsyncSession,
        investor_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get investor payout history"""
        query = select(InvestorPayout).where(InvestorPayout.investor_id == investor_id)
        
        # Apply filters
        if status:
            query = query.where(InvestorPayout.status == status)
        if date_from:
            query = query.where(InvestorPayout.period_start >= date_from)
        if date_to:
            query = query.where(InvestorPayout.period_end <= date_to)
        
        query = query.offset(skip).limit(limit).order_by(desc(InvestorPayout.created_at))
        
        result = await db.execute(query)
        payouts = result.scalars().all()
        
        payout_list = []
        for payout in payouts:
            payout_dict = {
                "id": payout.id,
                "amount": float(payout.amount),
                "period_start": payout.period_start,
                "period_end": payout.period_end,
                "status": payout.status,
                "created_at": payout.created_at,
                "paid_at": payout.paid_at,
                "job_count": payout.job_count,
                "total_revenue": float(payout.total_revenue),
                "notes": payout.notes
            }
            payout_list.append(payout_dict)
        
        return payout_list
    
    async def get_investor_reports(
        self,
        db: AsyncSession,
        investor_id: int,
        skip: int = 0,
        limit: int = 20,
        report_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get investor reports"""
        query = select(InvestorReport).where(InvestorReport.investor_id == investor_id)
        
        if report_type:
            query = query.where(InvestorReport.report_type == report_type)
        
        query = query.offset(skip).limit(limit).order_by(desc(InvestorReport.created_at))
        
        result = await db.execute(query)
        reports = result.scalars().all()
        
        report_list = []
        for report in reports:
            report_dict = {
                "id": report.id,
                "report_type": report.report_type,
                "title": report.title,
                "description": report.description,
                "status": report.status,
                "created_at": report.created_at,
                "completed_at": report.completed_at,
                "file_url": report.file_url,
                "data": report.data
            }
            report_list.append(report_dict)
        
        return report_list
    
    async def generate_investor_report(
        self,
        db: AsyncSession,
        investor_id: int,
        report_type: str,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate new investor report"""
        report = InvestorReport(
            investor_id=investor_id,
            report_type=report_type,
            title=f"{report_type.title()} Investor Report",
            date_from=date_from,
            date_to=date_to,
            filters=filters or {}
        )
        
        db.add(report)
        await db.commit()
        await db.refresh(report)
        
        return {
            "id": report.id,
            "report_type": report.report_type,
            "title": report.title,
            "status": report.status,
            "created_at": report.created_at,
            "estimated_completion": report.created_at + timedelta(minutes=30)
        }
    
    async def get_investor_portfolio(self, db: AsyncSession, investor_id: int) -> Dict[str, Any]:
        """Get investor portfolio overview"""
        investor = await self.get_investor_by_id(db, investor_id)
        if not investor:
            return {}
        
        # Get job investments
        job_investments_result = await db.execute(
            select(JobInvestment).where(JobInvestment.investor_id == investor_id)
        )
        job_investments = job_investments_result.scalars().all()
        
        active_investments = len([ji for ji in job_investments if ji.status == "ACTIVE"])
        completed_investments = len([ji for ji in job_investments if ji.status == "COMPLETED"])
        
        # Calculate current value
        current_value = float(investor.investment_amount) + float(investor.current_balance)
        
        # Performance history (last 6 months)
        performance_history = []
        for i in range(6):
            month_start = date.today().replace(day=1) - timedelta(days=i*30)
            value = current_value - (i * 1000)  # Simplified calculation
            performance_history.insert(0, {
                "date": month_start.strftime("%Y-%m"),
                "value": value
            })
        
        return {
            "total_investment": float(investor.investment_amount),
            "current_value": current_value,
            "total_returns": float(investor.current_balance),
            "roi_percentage": float(investor.roi_percentage),
            "active_investments": active_investments,
            "completed_investments": completed_investments,
            "performance_history": performance_history,
            "risk_score": 6.5,  # Would need risk calculation
            "diversification_score": 8.2  # Would need portfolio analysis
        }
    
    async def get_roi_analysis(
        self,
        db: AsyncSession,
        investor_id: int,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        group_by: str = "month"
    ) -> Dict[str, Any]:
        """Get ROI analysis for investor"""
        investor = await self.get_investor_by_id(db, investor_id)
        if not investor:
            return {}
        
        # Get job investments with job details
        query = (
            select(JobInvestment)
            .options(joinedload(JobInvestment.job))
            .where(JobInvestment.investor_id == investor_id)
        )
        
        if date_from or date_to:
            query = query.join(Job)
            if date_from:
                query = query.where(Job.completed_date >= date_from)
            if date_to:
                query = query.where(Job.completed_date <= date_to)
        
        result = await db.execute(query)
        job_investments = result.scalars().all()
        
        # Calculate overall ROI
        total_investment = float(investor.investment_amount)
        total_returns = sum(float(ji.investor_share) for ji in job_investments)
        overall_roi = (total_returns / total_investment * 100) if total_investment > 0 else 0
        
        # Calculate annualized ROI
        days_invested = (date.today() - investor.investment_date).days
        years_invested = days_invested / 365.25 if days_invested > 0 else 1
        annualized_roi = (overall_roi / years_invested) if years_invested > 0 else 0
        
        # ROI by period (last 6 months)
        roi_by_period = []
        for i in range(6):
            month_start = date.today().replace(day=1) - timedelta(days=i*30)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            month_jobs = [
                ji for ji in job_investments 
                if ji.job.completed_date and month_start <= ji.job.completed_date <= month_end
            ]
            
            month_returns = sum(float(ji.investor_share) for ji in month_jobs)
            month_roi = (month_returns / total_investment * 100) if total_investment > 0 else 0
            
            roi_by_period.insert(0, {
                "period": month_start.strftime("%Y-%m"),
                "roi": month_roi
            })
        
        # ROI by job type (simplified categorization)
        roi_by_job_type = {}
        job_types = ["painting", "plumbing", "electrical", "general"]
        
        for job_type in job_types:
            type_jobs = [
                ji for ji in job_investments 
                if job_type.lower() in ji.job.title.lower()
            ]
            
            if type_jobs:
                type_investment = sum(float(ji.investment_amount) for ji in type_jobs)
                type_returns = sum(float(ji.investor_share) for ji in type_jobs)
                type_roi = (type_returns / type_investment * 100) if type_investment > 0 else 0
                roi_by_job_type[job_type] = type_roi
            else:
                roi_by_job_type[job_type] = 0
        
        return {
            "overall_roi": overall_roi,
            "annualized_roi": annualized_roi,
            "roi_by_period": roi_by_period,
            "roi_by_job_type": roi_by_job_type,
            "benchmark_comparison": {
                "market_average": 15.2,
                "sector_average": 19.8,
                "outperformance": overall_roi - 15.2
            }
        }
    
    async def get_market_insights(self, db: AsyncSession, investor_id: int) -> Dict[str, Any]:
        """Get market insights for investor"""
        # This would typically involve complex market analysis
        # For now, returning structured mock data that could be populated by market analysis services
        
        return {
            "market_trends": {
                "overall_growth": 12.5,
                "sector_performance": {
                    "painting": "strong",
                    "plumbing": "moderate", 
                    "electrical": "strong",
                    "general": "stable"
                },
                "seasonal_patterns": {
                    "peak_months": ["April", "May", "June", "September"],
                    "low_months": ["December", "January", "February"]
                }
            },
            "opportunities": [
                {
                    "type": "sector_expansion",
                    "description": "Electrical work showing 35% growth",
                    "potential_roi": 31.2,
                    "risk_level": "medium"
                },
                {
                    "type": "geographic_expansion",
                    "description": "New market opportunities in suburbs", 
                    "potential_roi": 28.8,
                    "risk_level": "low"
                }
            ],
            "recommendations": [
                "Increase allocation to electrical jobs by 15%",
                "Consider seasonal investment adjustments",
                "Monitor competitor pricing in painting sector"
            ]
        }
    
    async def get_all_investors(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all investors (admin view)"""
        query = (
            select(Investor)
            .options(joinedload(Investor.user))
            .order_by(desc(Investor.created_at))
        )
        
        if search:
            query = query.join(User).where(
                or_(
                    User.email.ilike(f"%{search}%"),
                    User.first_name.ilike(f"%{search}%"),
                    User.last_name.ilike(f"%{search}%")
                )
            )
        
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        investors = result.scalars().all()
        
        investor_list = []
        for investor in investors:
            investor_dict = {
                "id": investor.id,
                "user_id": investor.user_id,
                "name": f"{investor.user.first_name} {investor.user.last_name}",
                "email": investor.user.email,
                "investment_amount": float(investor.investment_amount),
                "split_percentage": float(investor.split_percentage),
                "total_revenue": float(investor.total_revenue),
                "total_payouts": float(investor.total_payouts),
                "current_balance": float(investor.current_balance),
                "roi_percentage": float(investor.roi_percentage),
                "status": investor.status,
                "investment_date": investor.investment_date,
                "created_at": investor.created_at,
                "updated_at": investor.updated_at
            }
            investor_list.append(investor_dict)
        
        return investor_list
    
    async def create_investor_payout(
        self,
        db: AsyncSession,
        investor_id: int,
        amount: float,
        period_start: date,
        period_end: date,
        notes: Optional[str] = None,
        created_by_id: int = None
    ) -> Dict[str, Any]:
        """Create investor payout"""
        # Calculate job count and total revenue for the period
        job_count_result = await db.execute(
            select(func.count(JobInvestment.id))
            .join(Job)
            .where(
                and_(
                    JobInvestment.investor_id == investor_id,
                    Job.completed_date.between(period_start, period_end)
                )
            )
        )
        job_count = job_count_result.scalar() or 0
        
        total_revenue_result = await db.execute(
            select(func.coalesce(func.sum(JobInvestment.total_revenue), 0))
            .join(Job)
            .where(
                and_(
                    JobInvestment.investor_id == investor_id,
                    Job.completed_date.between(period_start, period_end)
                )
            )
        )
        total_revenue = float(total_revenue_result.scalar() or 0)
        
        payout = InvestorPayout(
            investor_id=investor_id,
            amount=amount,
            period_start=period_start,
            period_end=period_end,
            job_count=job_count,
            total_revenue=total_revenue,
            notes=notes,
            created_by_id=created_by_id
        )
        
        db.add(payout)
        await db.commit()
        await db.refresh(payout)
        
        return {
            "id": payout.id,
            "investor_id": payout.investor_id,
            "amount": float(payout.amount),
            "period_start": payout.period_start,
            "period_end": payout.period_end,
            "status": payout.status,
            "notes": payout.notes,
            "created_by_id": payout.created_by_id,
            "created_at": payout.created_at
        }
    
    async def update_investor_split(
        self,
        db: AsyncSession,
        investor_id: int,
        split_percentage: float,
        effective_date: Optional[date] = None,
        updated_by_id: int = None
    ) -> bool:
        """Update investor split percentage"""
        investor = await self.get_investor_by_id(db, investor_id)
        if not investor:
            return False
        
        # Record the change in history
        split_history = InvestorSplitHistory(
            investor_id=investor_id,
            old_percentage=investor.split_percentage,
            new_percentage=split_percentage,
            effective_date=effective_date or date.today(),
            changed_by_id=updated_by_id
        )
        
        # Update the investor
        investor.split_percentage = split_percentage
        
        db.add(split_history)
        await db.commit()
        
        return True
    
    async def create_job_investment(
        self,
        db: AsyncSession,
        job_id: int,
        investor_id: int,
        investment_amount: float,
        split_percentage: Optional[float] = None
    ) -> JobInvestment:
        """Create a job investment record"""
        # Get investor's default split if not provided
        if split_percentage is None:
            investor = await self.get_investor_by_id(db, investor_id)
            if not investor:
                raise ValueError("Investor not found")
            split_percentage = float(investor.split_percentage)
        
        job_investment = JobInvestment(
            job_id=job_id,
            investor_id=investor_id,
            investment_amount=investment_amount,
            split_percentage=split_percentage
        )
        
        db.add(job_investment)
        await db.commit()
        await db.refresh(job_investment)
        return job_investment
    
    async def update_job_investment_financials(
        self,
        db: AsyncSession,
        job_investment_id: int,
        total_revenue: float,
        total_expenses: float,
        platform_fee: float
    ) -> Optional[JobInvestment]:
        """Update job investment financial data"""
        result = await db.execute(
            select(JobInvestment).where(JobInvestment.id == job_investment_id)
        )
        job_investment = result.scalar_one_or_none()
        
        if not job_investment:
            return None
        
        # Calculate derived values
        net_profit = total_revenue - total_expenses - platform_fee
        investor_share = net_profit * (job_investment.split_percentage / 100)
        roi_percentage = (investor_share / job_investment.investment_amount * 100) if job_investment.investment_amount > 0 else 0
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Update the record
        job_investment.total_revenue = total_revenue
        job_investment.total_expenses = total_expenses
        job_investment.platform_fee = platform_fee
        job_investment.net_profit = net_profit
        job_investment.investor_share = investor_share
        job_investment.roi_percentage = roi_percentage
        job_investment.profit_margin = profit_margin
        
        await db.commit()
        await db.refresh(job_investment)
        return job_investment
    
    async def complete_job_investment(
        self,
        db: AsyncSession,
        job_investment_id: int
    ) -> bool:
        """Mark job investment as completed and update investor totals"""
        result = await db.execute(
            select(JobInvestment)
            .options(joinedload(JobInvestment.investor))
            .where(JobInvestment.id == job_investment_id)
        )
        job_investment = result.scalar_one_or_none()
        
        if not job_investment:
            return False
        
        # Mark as completed
        job_investment.status = "COMPLETED"
        
        # Update investor totals
        investor = job_investment.investor
        investor.total_revenue += job_investment.investor_share or 0
        investor.current_balance += job_investment.investor_share or 0
        
        # Recalculate ROI
        if investor.investment_amount > 0:
            investor.roi_percentage = (investor.total_revenue / investor.investment_amount * 100)
        
        await db.commit()
        return True
    
    async def get_investor_summary_stats(
        self,
        db: AsyncSession,
        investor_id: int
    ) -> Dict[str, Any]:
        """Get summary statistics for an investor"""
        # Get basic investor info
        investor = await self.get_investor_by_id(db, investor_id)
        if not investor:
            return {}
        
        # Get job investment counts
        active_jobs_result = await db.execute(
            select(func.count(JobInvestment.id))
            .where(
                and_(
                    JobInvestment.investor_id == investor_id,
                    JobInvestment.status == "ACTIVE"
                )
            )
        )
        active_jobs = active_jobs_result.scalar() or 0
        
        completed_jobs_result = await db.execute(
            select(func.count(JobInvestment.id))
            .where(
                and_(
                    JobInvestment.investor_id == investor_id,
                    JobInvestment.status == "COMPLETED"
                )
            )
        )
        completed_jobs = completed_jobs_result.scalar() or 0
        
        # Get pending payouts
        pending_payouts_result = await db.execute(
            select(func.coalesce(func.sum(InvestorPayout.amount), 0))
            .where(
                and_(
                    InvestorPayout.investor_id == investor_id,
                    InvestorPayout.status == "PENDING"
                )
            )
        )
        pending_payouts = float(pending_payouts_result.scalar() or 0)
        
        # Get average ROI for completed jobs
        avg_roi_result = await db.execute(
            select(func.avg(JobInvestment.roi_percentage))
            .where(
                and_(
                    JobInvestment.investor_id == investor_id,
                    JobInvestment.status == "COMPLETED",
                    JobInvestment.roi_percentage.isnot(None)
                )
            )
        )
        avg_roi = float(avg_roi_result.scalar() or 0)
        
        return {
            "investor_id": investor.id,
            "total_investment": float(investor.investment_amount),
            "current_balance": float(investor.current_balance),
            "total_revenue": float(investor.total_revenue),
            "total_payouts": float(investor.total_payouts),
            "roi_percentage": float(investor.roi_percentage),
            "active_jobs": active_jobs,
            "completed_jobs": completed_jobs,
            "total_jobs": active_jobs + completed_jobs,
            "pending_payouts": pending_payouts,
            "average_job_roi": avg_roi,
            "investment_date": investor.investment_date,
            "status": investor.status
        }


# Create global instance
investor_crud = InvestorCRUD()