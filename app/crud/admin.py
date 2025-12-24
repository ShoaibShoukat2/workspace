"""
Admin CRUD Operations
Real database integration for admin dashboard and management
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, text
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any, Tuple
from datetime import date, datetime, timedelta

from app.models.workspace import (
    Job, Workspace, Contractor, Payout, ComplianceData, 
    Estimate, WorkspaceMember
)
from app.models.auth import User
from app.schemas.admin import LeadCreate, ComplianceActionRequest


class AdminCRUD:
    
    async def get_admin_dashboard(self, db: AsyncSession) -> Dict[str, Any]:
        """Get comprehensive admin dashboard data"""
        
        # Get dispute statistics
        from app.models.workspace import Dispute
        pending_disputes_result = await db.execute(
            select(func.count(Dispute.id)).where(Dispute.status == 'OPEN')
        )
        pending_disputes = pending_disputes_result.scalar() or 0
        
        # Get payout statistics
        pending_payouts_result = await db.execute(
            select(func.count(Payout.id), func.coalesce(func.sum(Payout.amount), 0))
            .where(Payout.status == 'PENDING')
        )
        payout_data = pending_payouts_result.first()
        pending_payouts_count = payout_data[0] if payout_data else 0
        pending_payouts_amount = float(payout_data[1]) if payout_data else 0.0
        
        # Get blocked contractors
        blocked_contractors_result = await db.execute(
            select(func.count(Contractor.id))
            .where(Contractor.status == 'SUSPENDED')
        )
        blocked_contractors = blocked_contractors_result.scalar() or 0
        
        # Get active jobs (Open + InProgress)
        active_jobs_result = await db.execute(
            select(func.count(Job.id)).where(
                Job.status.in_(['LEAD', 'assigned', 'in_progress'])
            )
        )
        active_jobs = active_jobs_result.scalar() or 0
        
        # Get scheduled meetings (mock data for now)
        scheduled_meetings = 3
        
        # Get active leads (mock data for now)
        active_leads = 5
        
        # Get revenue data for chart (last 7 months)
        revenue_data = []
        for i in range(7):
            month_date = datetime.now() - timedelta(days=30 * i)
            month_start = month_date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            revenue_result = await db.execute(
                select(func.coalesce(func.sum(Job.actual_cost), 0))
                .where(
                    and_(
                        Job.status == 'completed',
                        Job.completed_date >= month_start.date(),
                        Job.completed_date <= month_end.date()
                    )
                )
            )
            revenue = float(revenue_result.scalar() or 0)
            
            revenue_data.insert(0, {
                "name": month_start.strftime("%b"),
                "value": revenue
            })
        
        # Get job status distribution
        job_stats_result = await db.execute(
            select(Job.status, func.count(Job.id))
            .group_by(Job.status)
        )
        
        job_stats_data = []
        status_mapping = {
            'LEAD': 'Open',
            'assigned': 'In Progress', 
            'in_progress': 'In Progress',
            'completed': 'Completed',
            'paid': 'Paid'
        }
        
        status_counts = {}
        for status, count in job_stats_result.fetchall():
            mapped_status = status_mapping.get(status, status)
            status_counts[mapped_status] = status_counts.get(mapped_status, 0) + count
        
        for status, count in status_counts.items():
            job_stats_data.append({
                "name": status,
                "count": count
            })
        
        # Get active investors
        active_investors_result = await db.execute(
            select(User)
            .where(User.role == 'INVESTOR')
            .order_by(desc(User.created_at))
            .limit(5)
        )
        active_investors = active_investors_result.scalars().all()
        
        investors_list = []
        for investor in active_investors:
            investors_list.append({
                "id": investor.id,
                "name": investor.full_name or investor.email.split('@')[0],
                "email": investor.email,
                "avatarUrl": None,
                "status": "Active"
            })
        
        # Get recent contractors
        recent_contractors_result = await db.execute(
            select(User)
            .where(User.role == 'CONTRACTOR')
            .order_by(desc(User.created_at))
            .limit(5)
        )
        recent_contractors = recent_contractors_result.scalars().all()
        
        contractors_list = []
        for contractor in recent_contractors:
            # Get contractor compliance status
            contractor_record_result = await db.execute(
                select(Contractor).where(Contractor.user_id == contractor.id)
            )
            contractor_record = contractor_record_result.scalar_one_or_none()
            
            compliance_status = "active"
            if contractor_record and contractor_record.status == "SUSPENDED":
                compliance_status = "blocked"
            
            contractors_list.append({
                "id": contractor.id,
                "name": contractor.full_name or contractor.email.split('@')[0],
                "email": contractor.email,
                "trade": "General",  # Would need to get from contractor profile
                "avatarUrl": None,
                "complianceStatus": compliance_status
            })
        
        return {
            # Stats for cards
            "pending_disputes": pending_disputes,
            "pending_payouts_count": pending_payouts_count,
            "pending_payouts_amount": pending_payouts_amount,
            "blocked_contractors": blocked_contractors,
            "active_jobs": active_jobs,
            "scheduled_meetings": scheduled_meetings,
            "active_leads": active_leads,
            
            # Chart data
            "revenue_data": revenue_data,
            "job_stats_data": job_stats_data,
            
            # Lists
            "active_investors": investors_list,
            "recent_contractors": contractors_list
        }
    
    async def _get_revenue_trend(self, db: AsyncSession, months: int) -> List[Dict[str, Any]]:
        """Get revenue trend for the last N months"""
        trend_data = []
        
        for i in range(months):
            # Calculate month start and end
            target_date = datetime.now() - timedelta(days=30 * i)
            month_start = target_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            if i == 0:
                month_end = datetime.now()
            else:
                next_month = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
                month_end = next_month - timedelta(days=1)
            
            # Get revenue for this month
            revenue_result = await db.execute(
                select(func.coalesce(func.sum(Job.actual_cost), 0))
                .where(
                    and_(
                        Job.status == 'completed',
                        Job.completed_date >= month_start.date(),
                        Job.completed_date <= month_end.date()
                    )
                )
            )
            revenue = float(revenue_result.scalar() or 0)
            
            trend_data.append({
                "month": month_start.strftime("%Y-%m"),
                "revenue": revenue,
                "month_name": month_start.strftime("%B %Y")
            })
        
        return list(reversed(trend_data))
    
    async def _get_job_status_distribution(self, db: AsyncSession) -> Dict[str, int]:
        """Get distribution of job statuses"""
        result = await db.execute(
            select(Job.status, func.count(Job.id))
            .group_by(Job.status)
        )
        
        distribution = {}
        for status, count in result.fetchall():
            distribution[status] = count
        
        return distribution
    
    async def _get_contractor_performance_summary(self, db: AsyncSession) -> Dict[str, Any]:
        """Get contractor performance summary"""
        # Get total contractors
        total_result = await db.execute(select(func.count(Contractor.id)))
        total_contractors = total_result.scalar() or 0
        
        # Get active contractors
        active_result = await db.execute(
            select(func.count(Contractor.id)).where(Contractor.status == 'ACTIVE')
        )
        active_contractors = active_result.scalar() or 0
        
        # Get average rating
        avg_rating_result = await db.execute(
            select(func.avg(Contractor.rating)).where(Contractor.rating.isnot(None))
        )
        avg_rating = float(avg_rating_result.scalar() or 0)
        
        return {
            "total_contractors": total_contractors,
            "active_contractors": active_contractors,
            "average_rating": avg_rating,
            "performance_trend": "stable"  # Would need historical data
        }
    
    async def get_all_jobs(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        workspace_id: Optional[str] = None,
        contractor_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        search: Optional[str] = None
    ) -> List[Job]:
        """Get all jobs with admin filters"""
        query = select(Job).options(
            selectinload(Job.workspace),
            selectinload(Job.assigned_to)
        )
        
        # Apply filters
        filters = []
        if status:
            if status == "Active":
                filters.append(Job.status.in_(['LEAD', 'assigned', 'in_progress']))
            else:
                filters.append(Job.status == status)
        
        if workspace_id:
            filters.append(Job.workspace_id == workspace_id)
        
        if contractor_id:
            filters.append(Job.assigned_to_id == contractor_id)
        
        if date_from:
            filters.append(Job.created_at >= date_from)
        
        if date_to:
            filters.append(Job.created_at <= date_to)
        
        if search:
            filters.append(
                or_(
                    Job.title.ilike(f"%{search}%"),
                    Job.customer_name.ilike(f"%{search}%"),
                    Job.location.ilike(f"%{search}%"),
                    Job.job_number.ilike(f"%{search}%")
                )
            )
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.order_by(desc(Job.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_job_admin(self, db: AsyncSession, job_id: int) -> Optional[Job]:
        """Get job details for admin view"""
        result = await db.execute(
            select(Job)
            .options(
                selectinload(Job.workspace),
                selectinload(Job.assigned_to),
                selectinload(Job.created_by)
            )
            .where(Job.id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def assign_job_to_contractor(
        self,
        db: AsyncSession,
        job_id: int,
        contractor_id: int,
        assigned_by_id: int,
        notes: Optional[str] = None
    ) -> bool:
        """Assign job to contractor"""
        # Get contractor user ID
        contractor_result = await db.execute(
            select(Contractor).where(Contractor.id == contractor_id)
        )
        contractor = contractor_result.scalar_one_or_none()
        
        if not contractor:
            return False
        
        # Update job
        from sqlalchemy import update
        result = await db.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(
                assigned_to_id=contractor.user_id,
                status="assigned",
                notes=notes,
                updated_at=datetime.utcnow()
            )
        )
        
        await db.commit()
        return result.rowcount > 0
    
    async def cancel_job(
        self,
        db: AsyncSession,
        job_id: int,
        cancellation_reason: str,
        cancelled_by_id: int
    ) -> bool:
        """Cancel job"""
        from sqlalchemy import update
        result = await db.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(
                status="cancelled",
                notes=f"Cancelled: {cancellation_reason}",
                updated_at=datetime.utcnow()
            )
        )
        
        await db.commit()
        return result.rowcount > 0
    
    async def get_all_leads(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        source: Optional[str] = None,
        assigned_to: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get all leads (mock implementation)"""
        # Mock leads data - in real implementation, this would be a separate Lead model
        leads = []
        for i in range(1, min(limit + 1, 11)):
            lead = {
                "id": i,
                "customer_name": f"Lead Customer {i}",
                "customer_email": f"lead{i}@example.com",
                "customer_phone": f"+1-555-{i:04d}",
                "property_address": f"{100 + i} Lead St, City, State",
                "service_type": "General Contracting",
                "status": "NEW" if i <= 3 else "CONTACTED" if i <= 6 else "QUALIFIED",
                "source": "Website" if i % 2 == 0 else "Referral",
                "assigned_to_id": None,
                "created_at": datetime.now() - timedelta(days=i),
                "notes": f"Lead notes for customer {i}"
            }
            leads.append(lead)
        
        return leads[skip:skip + limit]
    
    async def create_lead(
        self,
        db: AsyncSession,
        lead_data: LeadCreate,
        created_by_id: int
    ) -> Dict[str, Any]:
        """Create new lead (mock implementation)"""
        # Mock lead creation - in real implementation, this would create a Lead record
        lead = {
            "id": 999,  # Mock ID
            "customer_name": lead_data.customer_name,
            "customer_email": lead_data.customer_email,
            "customer_phone": lead_data.customer_phone,
            "property_address": lead_data.property_address,
            "service_type": lead_data.service_type,
            "status": "NEW",
            "source": lead_data.source,
            "assigned_to_id": None,
            "created_by_id": created_by_id,
            "created_at": datetime.now(),
            "notes": lead_data.notes
        }
        
        return lead
    
    async def get_lead_admin(self, db: AsyncSession, lead_id: int) -> Optional[Dict[str, Any]]:
        """Get lead details for admin view (mock implementation)"""
        # Mock lead data
        if lead_id <= 10:
            return {
                "id": lead_id,
                "customer_name": f"Lead Customer {lead_id}",
                "customer_email": f"lead{lead_id}@example.com",
                "customer_phone": f"+1-555-{lead_id:04d}",
                "property_address": f"{100 + lead_id} Lead St, City, State",
                "service_type": "General Contracting",
                "status": "NEW",
                "source": "Website",
                "assigned_to_id": None,
                "created_at": datetime.now() - timedelta(days=lead_id),
                "notes": f"Lead notes for customer {lead_id}"
            }
        return None
    
    async def assign_lead(
        self,
        db: AsyncSession,
        lead_id: int,
        assigned_to: int,
        assigned_by_id: int
    ) -> bool:
        """Assign lead to user (mock implementation)"""
        # Mock assignment - in real implementation, this would update Lead record
        return lead_id <= 10  # Mock success for valid lead IDs
    
    async def convert_lead_to_job(
        self,
        db: AsyncSession,
        lead_id: int,
        workspace_id: str,
        converted_by_id: int
    ) -> Optional[Job]:
        """Convert lead to job (mock implementation)"""
        # Mock conversion - in real implementation, this would:
        # 1. Get lead data
        # 2. Create job from lead
        # 3. Update lead status to converted
        
        if lead_id <= 10:
            # Create mock job
            job_number = f"JOB-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # In real implementation, you would create actual Job record
            # For now, return mock job data
            class MockJob:
                def __init__(self):
                    self.id = 999
                    self.job_number = job_number
            
            return MockJob()
        
        return None
    
    async def _get_contractor_performance_summary(self, db: AsyncSession) -> Dict[str, Any]:
        """Get contractor performance summary"""
        # Top performing contractors (by rating)
        top_contractors_result = await db.execute(
            select(Contractor, User.first_name, User.last_name)
            .join(User, Contractor.user_id == User.id)
            .where(Contractor.rating.isnot(None))
            .order_by(desc(Contractor.rating))
            .limit(5)
        )
        
        top_contractors = []
        for contractor, first_name, last_name in top_contractors_result.fetchall():
            top_contractors.append({
                "id": contractor.id,
                "name": f"{first_name} {last_name}".strip(),
                "company": contractor.company_name,
                "rating": float(contractor.rating) if contractor.rating else 0,
                "completed_jobs": contractor.total_jobs_completed
            })
        
        # Average contractor rating
        avg_rating_result = await db.execute(
            select(func.avg(Contractor.rating))
            .where(Contractor.rating.isnot(None))
        )
        avg_rating = float(avg_rating_result.scalar() or 0)
        
        return {
            "top_contractors": top_contractors,
            "average_rating": avg_rating,
            "total_active_contractors": len(top_contractors)  # This would be calculated properly
        }
    
    async def get_all_jobs(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        workspace_id: Optional[str] = None,
        contractor_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Job], int]:
        """Get all jobs with admin filters"""
        query = select(Job).options(
            selectinload(Job.workspace),
            selectinload(Job.assigned_to),
            selectinload(Job.created_by)
        )
        
        # Apply filters
        filters = []
        if status:
            filters.append(Job.status == status)
        if workspace_id:
            try:
                workspace_id_int = int(workspace_id)
                filters.append(Job.workspace_id == workspace_id_int)
            except ValueError:
                pass
        if contractor_id:
            filters.append(Job.assigned_to_id == contractor_id)
        if date_from:
            filters.append(Job.created_at >= date_from)
        if date_to:
            filters.append(Job.created_at <= date_to)
        if search:
            filters.append(
                or_(
                    Job.title.ilike(f"%{search}%"),
                    Job.description.ilike(f"%{search}%"),
                    Job.job_number.ilike(f"%{search}%"),
                    Job.customer_name.ilike(f"%{search}%"),
                    Job.customer_email.ilike(f"%{search}%")
                )
            )
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count
        count_query = select(func.count(Job.id))
        if filters:
            count_query = count_query.where(and_(*filters))
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Get paginated results
        result = await db.execute(
            query.order_by(desc(Job.created_at))
            .offset(skip)
            .limit(limit)
        )
        jobs = result.scalars().all()
        
        return jobs, total
    
    async def get_all_workspaces(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        workspace_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Workspace], int]:
        """Get all workspaces with admin filters"""
        query = select(Workspace).options(
            selectinload(Workspace.owner),
            selectinload(Workspace.members)
        )
        
        # Apply filters
        filters = []
        if workspace_type:
            filters.append(Workspace.workspace_type == workspace_type)
        if is_active is not None:
            filters.append(Workspace.is_active == is_active)
        if search:
            filters.append(
                or_(
                    Workspace.name.ilike(f"%{search}%"),
                    Workspace.description.ilike(f"%{search}%")
                )
            )
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count
        count_query = select(func.count(Workspace.id))
        if filters:
            count_query = count_query.where(and_(*filters))
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Get paginated results
        result = await db.execute(
            query.order_by(desc(Workspace.created_at))
            .offset(skip)
            .limit(limit)
        )
        workspaces = result.scalars().all()
        
        return workspaces, total
    
    async def get_all_contractors(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        specialization: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Contractor], int]:
        """Get all contractors with admin filters"""
        query = select(Contractor).options(
            selectinload(Contractor.workspace),
            selectinload(Contractor.user)
        )
        
        # Apply filters
        filters = []
        if status:
            filters.append(Contractor.status == status)
        if specialization:
            filters.append(Contractor.specialization.ilike(f"%{specialization}%"))
        if search:
            # Join with User for name search
            query = query.join(User, Contractor.user_id == User.id)
            filters.append(
                or_(
                    Contractor.company_name.ilike(f"%{search}%"),
                    User.first_name.ilike(f"%{search}%"),
                    User.last_name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    Contractor.license_number.ilike(f"%{search}%")
                )
            )
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count
        count_query = select(func.count(Contractor.id))
        if search:
            count_query = count_query.join(User, Contractor.user_id == User.id)
        if filters:
            count_query = count_query.where(and_(*filters))
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Get paginated results
        result = await db.execute(
            query.order_by(desc(Contractor.created_at))
            .offset(skip)
            .limit(limit)
        )
        contractors = result.scalars().all()
        
        return contractors, total
    
    async def get_all_payouts(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        contractor_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Tuple[List[Payout], int]:
        """Get all payouts with admin filters"""
        query = select(Payout).options(
            selectinload(Payout.contractor).selectinload(Contractor.user),
            selectinload(Payout.workspace),
            selectinload(Payout.job)
        )
        
        # Apply filters
        filters = []
        if status:
            filters.append(Payout.status == status)
        if contractor_id:
            filters.append(Payout.contractor_id == contractor_id)
        if date_from:
            filters.append(Payout.created_at >= date_from)
        if date_to:
            filters.append(Payout.created_at <= date_to)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count
        count_query = select(func.count(Payout.id))
        if filters:
            count_query = count_query.where(and_(*filters))
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Get paginated results
        result = await db.execute(
            query.order_by(desc(Payout.created_at))
            .offset(skip)
            .limit(limit)
        )
        payouts = result.scalars().all()
        
        return payouts, total
    
    async def get_compliance_overview(self, db: AsyncSession) -> Dict[str, Any]:
        """Get compliance overview for admin"""
        # Get compliance statistics
        total_records_result = await db.execute(select(func.count(ComplianceData.id)))
        total_records = total_records_result.scalar()
        
        # Status distribution
        status_result = await db.execute(
            select(ComplianceData.status, func.count(ComplianceData.id))
            .group_by(ComplianceData.status)
        )
        
        status_distribution = {}
        for status, count in status_result.fetchall():
            status_distribution[status] = count
        
        # Expiring soon (next 30 days)
        expiring_soon_result = await db.execute(
            select(func.count(ComplianceData.id))
            .where(
                and_(
                    ComplianceData.expiry_date.isnot(None),
                    ComplianceData.expiry_date <= (date.today() + timedelta(days=30)),
                    ComplianceData.expiry_date > date.today(),
                    ComplianceData.status == 'APPROVED'
                )
            )
        )
        expiring_soon = expiring_soon_result.scalar()
        
        # Expired
        expired_result = await db.execute(
            select(func.count(ComplianceData.id))
            .where(
                and_(
                    ComplianceData.expiry_date.isnot(None),
                    ComplianceData.expiry_date < date.today()
                )
            )
        )
        expired = expired_result.scalar()
        
        return {
            "total_records": total_records,
            "status_distribution": status_distribution,
            "expiring_soon": expiring_soon,
            "expired": expired,
            "compliance_rate": (status_distribution.get('APPROVED', 0) / total_records * 100) if total_records > 0 else 0
        }
    
    async def get_system_metrics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get system-wide metrics"""
        # User growth (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        new_users_result = await db.execute(
            select(func.count(User.id))
            .where(User.created_at >= thirty_days_ago)
        )
        new_users = new_users_result.scalar()
        
        # Job completion rate
        total_jobs_result = await db.execute(select(func.count(Job.id)))
        total_jobs = total_jobs_result.scalar()
        
        completed_jobs_result = await db.execute(
            select(func.count(Job.id)).where(Job.status == 'completed')
        )
        completed_jobs = completed_jobs_result.scalar()
        
        completion_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
        
        # Average job value
        avg_job_value_result = await db.execute(
            select(func.avg(Job.actual_cost))
            .where(Job.actual_cost.isnot(None))
        )
        avg_job_value = float(avg_job_value_result.scalar() or 0)
        
        return {
            "new_users_30_days": new_users,
            "job_completion_rate": completion_rate,
            "average_job_value": avg_job_value,
            "total_active_workspaces": await self._get_active_workspaces_count(db),
            "system_uptime": "99.9%",  # This would come from monitoring system
            "api_response_time": "120ms"  # This would come from monitoring system
        }
    
    async def _get_active_workspaces_count(self, db: AsyncSession) -> int:
        """Get count of active workspaces"""
        result = await db.execute(
            select(func.count(Workspace.id)).where(Workspace.is_active == True)
        )
        return result.scalar()


# Create global instance
admin_crud = AdminCRUD()