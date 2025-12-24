"""
FM (Facility Manager) CRUD Operations
Real database integration for FM dashboard and site visit management
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, text, update
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any, Tuple
from datetime import date, datetime, timedelta
from decimal import Decimal
import json

from app.models.workspace import (
    Job, Workspace, Contractor, Payout, ComplianceData, 
    Estimate, WorkspaceMember, SiteVisit, ChangeOrder, Dispute
)
from app.models.auth import User
from app.schemas.fm import (
    SiteVisitCreate, FMJobVisitUpdate, MaterialVerificationRequest,
    ChangeOrderCreate, MaterialItem
)


class FMCRUD:
    
    async def get_fm_dashboard(self, db: AsyncSession, fm_user_id: int) -> Dict[str, Any]:
        """Get comprehensive FM dashboard data"""
        
        # Get pending site visits (jobs requiring FM visits)
        pending_visits_result = await db.execute(
            select(func.count(Job.id)).where(
                and_(
                    Job.status.in_(['LEAD', 'assigned']),
                    Job.requires_site_visit == True
                )
            )
        )
        pending_visits = pending_visits_result.scalar() or 0
        
        # Get active jobs (in progress)
        active_jobs_result = await db.execute(
            select(func.count(Job.id)).where(Job.status == 'in_progress')
        )
        active_jobs = active_jobs_result.scalar() or 0
        
        # Get completed today
        today = date.today()
        completed_today_result = await db.execute(
            select(func.count(Job.id)).where(
                and_(
                    Job.status == 'completed',
                    func.date(Job.completed_date) == today
                )
            )
        )
        completed_today = completed_today_result.scalar() or 0
        
        # Get total visits this month
        month_start = today.replace(day=1)
        visits_this_month_result = await db.execute(
            select(func.count(SiteVisit.id)).where(
                and_(
                    SiteVisit.created_at >= month_start,
                    SiteVisit.fm_user_id == fm_user_id
                )
            )
        )
        visits_this_month = visits_this_month_result.scalar() or 0
        
        # Get material issues count
        material_issues_result = await db.execute(
            select(func.count(SiteVisit.id)).where(
                and_(
                    SiteVisit.material_status == 'Issues Found',
                    SiteVisit.fm_user_id == fm_user_id
                )
            )
        )
        material_issues = material_issues_result.scalar() or 0
        
        # Get pending change orders
        pending_change_orders_result = await db.execute(
            select(func.count(ChangeOrder.id)).where(
                and_(
                    ChangeOrder.status == 'PENDING',
                    ChangeOrder.created_by_id == fm_user_id
                )
            )
        )
        pending_change_orders = pending_change_orders_result.scalar() or 0
        
        # Calculate average completion time (mock for now)
        average_completion_time = 4.5  # hours
        
        return {
            "pending_visits": pending_visits,
            "active_jobs": active_jobs,
            "completed_today": completed_today,
            "total_visits_this_month": visits_this_month,
            "average_completion_time": average_completion_time,
            "material_issues_count": material_issues,
            "change_orders_pending": pending_change_orders
        }
    
    async def get_site_visits(
        self,
        db: AsyncSession,
        fm_user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[SiteVisit]:
        """Get site visits for FM"""
        query = select(SiteVisit).options(
            selectinload(SiteVisit.job)
        ).where(SiteVisit.fm_user_id == fm_user_id)
        
        filters = []
        if status:
            filters.append(SiteVisit.status == status)
        if date_from:
            filters.append(SiteVisit.created_at >= date_from)
        if date_to:
            filters.append(SiteVisit.created_at <= date_to)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.order_by(desc(SiteVisit.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_site_visit(
        self,
        db: AsyncSession,
        visit_id: int,
        fm_user_id: int
    ) -> Optional[SiteVisit]:
        """Get specific site visit"""
        result = await db.execute(
            select(SiteVisit)
            .options(selectinload(SiteVisit.job))
            .where(
                and_(
                    SiteVisit.id == visit_id,
                    SiteVisit.fm_user_id == fm_user_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def create_site_visit(
        self,
        db: AsyncSession,
        visit_data: SiteVisitCreate,
        fm_user_id: int
    ) -> SiteVisit:
        """Create new site visit"""
        site_visit = SiteVisit(
            job_id=visit_data.job_id,
            fm_user_id=fm_user_id,
            scheduled_date=visit_data.scheduled_date,
            status="SCHEDULED",
            material_status="AI Generated",
            notes=visit_data.notes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(site_visit)
        await db.commit()
        await db.refresh(site_visit)
        return site_visit
    
    async def update_site_visit(
        self,
        db: AsyncSession,
        visit_id: int,
        visit_update: FMJobVisitUpdate,
        fm_user_id: int
    ) -> bool:
        """Update site visit details"""
        update_data = {}
        
        if visit_update.measurements is not None:
            update_data["measurements"] = json.dumps(visit_update.measurements)
        if visit_update.scope_confirmed is not None:
            update_data["scope_confirmed"] = visit_update.scope_confirmed
        if visit_update.photos_uploaded is not None:
            update_data["photos_uploaded"] = visit_update.photos_uploaded
        if visit_update.tools_required is not None:
            update_data["tools_required"] = json.dumps(visit_update.tools_required)
        if visit_update.labor_required is not None:
            update_data["labor_required"] = visit_update.labor_required
        if visit_update.estimated_time is not None:
            update_data["estimated_time"] = visit_update.estimated_time
        if visit_update.safety_concerns is not None:
            update_data["safety_concerns"] = visit_update.safety_concerns
        if visit_update.materials is not None:
            materials_data = [material.dict() for material in visit_update.materials]
            update_data["materials_list"] = json.dumps(materials_data)
            update_data["material_status"] = "FM Verified"
        if visit_update.signature_saved is not None:
            update_data["signature_saved"] = visit_update.signature_saved
        if visit_update.status is not None:
            update_data["status"] = visit_update.status
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.execute(
            update(SiteVisit)
            .where(
                and_(
                    SiteVisit.id == visit_id,
                    SiteVisit.fm_user_id == fm_user_id
                )
            )
            .values(**update_data)
        )
        
        await db.commit()
        return result.rowcount > 0
    
    async def submit_site_visit(
        self,
        db: AsyncSession,
        visit_id: int,
        fm_user_id: int
    ) -> bool:
        """Submit completed site visit"""
        result = await db.execute(
            update(SiteVisit)
            .where(
                and_(
                    SiteVisit.id == visit_id,
                    SiteVisit.fm_user_id == fm_user_id
                )
            )
            .values(
                status="COMPLETED",
                completed_date=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )
        
        await db.commit()
        return result.rowcount > 0
    
    async def verify_materials(
        self,
        db: AsyncSession,
        verification_data: MaterialVerificationRequest,
        fm_user_id: int
    ) -> bool:
        """Verify AI-generated materials list"""
        # Update job materials status
        materials_data = [material.dict() for material in verification_data.materials]
        
        result = await db.execute(
            update(Job)
            .where(Job.id == verification_data.job_id)
            .values(
                materials_list=json.dumps(materials_data),
                materials_verified_by_id=fm_user_id,
                materials_verified_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )
        
        await db.commit()
        return result.rowcount > 0
    
    async def get_ai_material_suggestions(
        self,
        db: AsyncSession,
        job_id: int
    ) -> List[Dict[str, Any]]:
        """Get AI-generated material suggestions for a job"""
        # Mock AI material suggestions
        suggestions = [
            {
                "id": "mat-001",
                "name": "Premium Interior Paint",
                "sku": "PPG-INT-001",
                "quantity": 2,
                "unit": "gallon",
                "supplier": "Home Depot",
                "price_range": "$45-60/gal",
                "category": "Paint",
                "ai_confidence": 0.95,
                "reasoning": "Based on room dimensions and surface type"
            },
            {
                "id": "mat-002",
                "name": "Painter's Tape",
                "sku": "3M-TAPE-001",
                "quantity": 3,
                "unit": "roll",
                "supplier": "3M Distributor",
                "price_range": "$3-5/roll",
                "category": "Supplies",
                "ai_confidence": 0.88,
                "reasoning": "Standard requirement for clean paint lines"
            }
        ]
        
        return suggestions
    
    async def create_change_order(
        self,
        db: AsyncSession,
        change_order_data: ChangeOrderCreate,
        fm_user_id: int
    ) -> ChangeOrder:
        """Create change order request"""
        # Calculate total amount
        total_amount = sum(
            item.quantity * item.rate for item in change_order_data.line_items
        )
        
        # Create change order
        change_order = ChangeOrder(
            job_id=change_order_data.job_id,
            reason=change_order_data.reason,
            line_items=json.dumps([item.dict() for item in change_order_data.line_items]),
            total_amount=Decimal(str(total_amount)),
            status="PENDING",
            created_by_id=fm_user_id,
            notes=change_order_data.notes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(change_order)
        await db.commit()
        await db.refresh(change_order)
        
        # Create associated dispute for approval workflow
        dispute = Dispute(
            job_id=change_order_data.job_id,
            reported_by_id=fm_user_id,
            dispute_type="CHANGE_ORDER",
            title=f"Change Order Request - Job #{change_order_data.job_id}",
            description=f"Change order request: {change_order_data.reason}",
            status="OPEN",
            priority="MEDIUM",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(dispute)
        await db.commit()
        await db.refresh(dispute)
        
        # Link dispute to change order
        change_order.dispute_id = dispute.id
        await db.commit()
        
        return change_order
    
    async def get_change_orders(
        self,
        db: AsyncSession,
        fm_user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> List[ChangeOrder]:
        """Get change orders created by FM"""
        query = select(ChangeOrder).options(
            selectinload(ChangeOrder.job)
        ).where(ChangeOrder.created_by_id == fm_user_id)
        
        if status:
            query = query.where(ChangeOrder.status == status)
        
        query = query.order_by(desc(ChangeOrder.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_change_order(
        self,
        db: AsyncSession,
        change_order_id: int,
        fm_user_id: int
    ) -> Optional[ChangeOrder]:
        """Get specific change order"""
        result = await db.execute(
            select(ChangeOrder)
            .options(selectinload(ChangeOrder.job))
            .where(
                and_(
                    ChangeOrder.id == change_order_id,
                    ChangeOrder.created_by_id == fm_user_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_assigned_jobs(
        self,
        db: AsyncSession,
        fm_user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> List[Job]:
        """Get jobs assigned to FM for site visits"""
        query = select(Job).options(
            selectinload(Job.assigned_to)
        ).where(Job.requires_site_visit == True)
        
        if status:
            query = query.where(Job.status == status)
        
        query = query.order_by(desc(Job.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def generate_quote(
        self,
        db: AsyncSession,
        job_id: int,
        materials: List[dict],
        labor_hours: float,
        labor_rate: float,
        fm_user_id: int
    ) -> Optional[Estimate]:
        """Generate quote from verified materials and labor"""
        # Get job
        job_result = await db.execute(
            select(Job).where(Job.id == job_id)
        )
        job = job_result.scalar_one_or_none()
        
        if not job:
            return None
        
        # Calculate totals
        material_cost = sum(
            float(material.get('quantity', 0)) * float(material.get('rate', 0))
            for material in materials
        )
        labor_cost = labor_hours * labor_rate
        subtotal = material_cost + labor_cost
        markup = subtotal * 0.15  # 15% markup
        total_amount = subtotal + markup
        
        # Create estimate
        estimate = Estimate(
            job_id=job_id,
            workspace_id=job.workspace_id,
            line_items=json.dumps({
                "materials": materials,
                "labor": {
                    "hours": labor_hours,
                    "rate": labor_rate,
                    "total": labor_cost
                }
            }),
            subtotal=Decimal(str(subtotal)),
            tax_amount=Decimal('0.00'),
            total_amount=Decimal(str(total_amount)),
            status="DRAFT",
            created_by_id=fm_user_id,
            magic_token=f"quote-{job_id}-{datetime.now().timestamp()}",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(estimate)
        await db.commit()
        await db.refresh(estimate)
        return estimate
    
    async def get_fm_analytics(
        self,
        db: AsyncSession,
        fm_user_id: int,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get FM analytics overview"""
        # Mock analytics data
        return {
            "total_visits_completed": 45,
            "average_visit_duration": 2.5,
            "material_accuracy_rate": 94.2,
            "change_order_rate": 8.5,
            "customer_satisfaction_score": 4.7,
            "on_time_completion_rate": 92.3
        }
    
    async def get_performance_metrics(
        self,
        db: AsyncSession,
        fm_user_id: int,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get FM performance metrics"""
        # Mock performance metrics
        return {
            "visits_this_month": 12,
            "visits_last_month": 15,
            "average_completion_time": 2.3,
            "material_issues_identified": 3,
            "change_orders_created": 2,
            "quotes_generated": 8,
            "approval_rate": 96.5
        }
    
    async def upload_photos(
        self,
        db: AsyncSession,
        visit_id: int,
        photo_type: str,
        fm_user_id: int
    ) -> bool:
        """Upload site visit photos (mock implementation)"""
        # Update site visit with photo upload status
        result = await db.execute(
            update(SiteVisit)
            .where(
                and_(
                    SiteVisit.id == visit_id,
                    SiteVisit.fm_user_id == fm_user_id
                )
            )
            .values(
                photos_uploaded=True,
                updated_at=datetime.utcnow()
            )
        )
        
        await db.commit()
        return result.rowcount > 0
    
    async def get_map_jobs(
        self,
        db: AsyncSession,
        fm_user_id: int
    ) -> List[Job]:
        """Get jobs for map view"""
        result = await db.execute(
            select(Job)
            .where(Job.requires_site_visit == True)
            .order_by(desc(Job.created_at))
            .limit(50)
        )
        return result.scalars().all()


# Create global instance
fm_crud = FMCRUD()