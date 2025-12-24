"""
Contractor CRUD Operations
Real database integration for contractor management
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func, desc
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime, date, timedelta

from app.models.workspace import Contractor, Workspace, WorkspaceMember, Job, Payout, ComplianceData
from app.models.auth import User
from app.schemas.contractor import ContractorCreate, ContractorUpdate


class ContractorCRUD:
    
    async def get_contractor(self, db: AsyncSession, contractor_id: int) -> Optional[Contractor]:
        """Get contractor by ID with relationships"""
        result = await db.execute(
            select(Contractor)
            .options(
                selectinload(Contractor.workspace),
                selectinload(Contractor.user),
                selectinload(Contractor.payouts),
                selectinload(Contractor.compliance_records)
            )
            .where(Contractor.id == contractor_id)
        )
        return result.scalar_one_or_none()
    
    async def get_contractors(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        workspace_id: Optional[UUID] = None,
        status: Optional[str] = None,
        specialization: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Contractor], int]:
        """Get contractors with filtering"""
        # Base query - user must have access to workspace
        base_query = select(Contractor).join(Workspace).join(
            WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id
        ).where(WorkspaceMember.user_id == user_id)
        
        # Apply filters
        filters = []
        if workspace_id:
            filters.append(Contractor.workspace_id == workspace_id)
        if status:
            filters.append(Contractor.status == status)
        if specialization:
            filters.append(Contractor.specialization.ilike(f"%{specialization}%"))
        if search:
            # Join with User table for name search
            base_query = base_query.join(User, Contractor.user_id == User.id)
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
            base_query = base_query.where(and_(*filters))
        
        # Get total count
        count_result = await db.execute(
            select(func.count(Contractor.id)).select_from(base_query.subquery())
        )
        total = count_result.scalar()
        
        # Get paginated results
        result = await db.execute(
            base_query
            .options(
                selectinload(Contractor.workspace),
                selectinload(Contractor.user)
            )
            .order_by(Contractor.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        contractors = result.scalars().all()
        
        return contractors, total
    
    async def create_contractor(
        self, 
        db: AsyncSession, 
        contractor_data: ContractorCreate, 
        user_id: int
    ) -> Contractor:
        """Create new contractor"""
        contractor = Contractor(
            workspace_id=contractor_data.workspace_id,
            user_id=contractor_data.user_id,
            company_name=contractor_data.company_name,
            license_number=contractor_data.license_number,
            specialization=contractor_data.specialization,
            hourly_rate=contractor_data.hourly_rate,
            phone=contractor_data.phone,
            address=contractor_data.address,
            notes=contractor_data.notes,
            status="ACTIVE"
        )
        
        db.add(contractor)
        await db.commit()
        await db.refresh(contractor)
        return contractor
    
    async def update_contractor(
        self, 
        db: AsyncSession, 
        contractor_id: int, 
        contractor_data: ContractorUpdate
    ) -> Optional[Contractor]:
        """Update contractor"""
        contractor = await self.get_contractor(db, contractor_id)
        if not contractor:
            return None
        
        update_data = contractor_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(contractor, field):
                setattr(contractor, field, value)
        
        contractor.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(contractor)
        return contractor
    
    async def user_has_contractor_access(
        self, 
        db: AsyncSession, 
        user_id: int, 
        contractor_id: int
    ) -> bool:
        """Check if user has access to contractor"""
        result = await db.execute(
            select(Contractor.id)
            .join(Workspace)
            .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
            .where(
                and_(
                    Contractor.id == contractor_id,
                    WorkspaceMember.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def user_can_edit_contractor(
        self, 
        db: AsyncSession, 
        user_id: int, 
        contractor_id: int
    ) -> bool:
        """Check if user can edit contractor"""
        result = await db.execute(
            select(Contractor.id)
            .join(Workspace)
            .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
            .where(
                and_(
                    Contractor.id == contractor_id,
                    WorkspaceMember.user_id == user_id,
                    WorkspaceMember.role.in_(["OWNER", "ADMIN"])
                )
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def get_contractor_dashboard(
        self, 
        db: AsyncSession, 
        contractor_id: int
    ) -> Dict[str, Any]:
        """Get contractor dashboard data"""
        contractor = await self.get_contractor(db, contractor_id)
        if not contractor:
            return {}
        
        # Get contractor's jobs
        jobs_result = await db.execute(
            select(Job).where(Job.assigned_to_id == contractor.user_id)
            .order_by(desc(Job.created_at))
        )
        jobs = jobs_result.scalars().all()
        
        # Calculate metrics
        active_jobs = [job for job in jobs if job.status in ['assigned', 'in_progress', 'evaluation_scheduled']]
        completed_jobs = [job for job in jobs if job.status == 'completed']
        pending_assignments = [job for job in jobs if job.status == 'assigned']
        
        # Calculate earnings
        total_earnings = sum(job.actual_cost or 0 for job in completed_jobs)
        monthly_earnings = sum(
            job.actual_cost or 0 for job in completed_jobs 
            if job.completed_date and job.completed_date.month == datetime.now().month
        )
        
        # Get wallet info
        wallet = await self.get_contractor_wallet(db, contractor_id)
        
        # Get compliance status
        compliance_docs = await self.get_contractor_compliance(db, contractor_id)
        compliance_status = "active"
        if not compliance_docs:
            compliance_status = "blocked"
        else:
            # Check if any required docs are missing or expired
            required_types = ["ID", "LICENSE", "INSURANCE"]
            for req_type in required_types:
                type_docs = [doc for doc in compliance_docs if doc.compliance_type == req_type]
                if not type_docs or any(doc.status != "APPROVED" for doc in type_docs):
                    compliance_status = "blocked"
                    break
        
        # Get recent jobs for dashboard
        recent_jobs = []
        for job in jobs[:5]:
            recent_jobs.append({
                "id": job.id,
                "title": job.title,
                "status": job.status,
                "customer_name": job.customer_name,
                "scheduled_date": job.start_date.isoformat() if job.start_date else None,
                "estimated_cost": float(job.estimated_cost) if job.estimated_cost else 0,
                "property_address": job.location,
                "job_number": job.job_number
            })
        
        # Get upcoming jobs (next 7 days)
        upcoming_jobs = []
        next_week = datetime.now() + timedelta(days=7)
        for job in active_jobs:
            if job.start_date and job.start_date <= next_week.date():
                upcoming_jobs.append({
                    "id": job.id,
                    "title": job.title,
                    "customer_name": job.customer_name,
                    "scheduled_date": job.start_date.isoformat(),
                    "property_address": job.location,
                    "estimated_cost": float(job.estimated_cost) if job.estimated_cost else 0
                })
        
        return {
            "contractor_id": contractor_id,
            "total_jobs": len(jobs),
            "active_jobs": len(active_jobs),
            "completed_jobs": len(completed_jobs),
            "pending_assignments": len(pending_assignments),
            "wallet_balance": wallet["balance"],
            "pending_earnings": wallet["pending_amount"],
            "total_earnings": float(total_earnings),
            "current_rating": float(contractor.rating) if contractor.rating else None,
            "compliance_status": compliance_status,
            "recent_jobs": recent_jobs,
            "upcoming_jobs": upcoming_jobs,
            "notifications_count": len(pending_assignments)  # Simple notification count
        }
    
    async def get_contractor_jobs(
        self,
        db: AsyncSession,
        contractor_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> List[Job]:
        """Get jobs assigned to contractor"""
        contractor = await self.get_contractor(db, contractor_id)
        if not contractor:
            return []
        
        query = select(Job).where(Job.assigned_to_id == contractor.user_id)
        
        if status:
            query = query.where(Job.status == status)
        
        query = query.order_by(desc(Job.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_contractor_payouts(
        self,
        db: AsyncSession,
        contractor_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> List[Payout]:
        """Get contractor payouts"""
        query = select(Payout).where(Payout.contractor_id == contractor_id)
        
        if status:
            query = query.where(Payout.status == status)
        
        query = query.order_by(desc(Payout.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_contractor_compliance(
        self,
        db: AsyncSession,
        contractor_id: int
    ) -> List[ComplianceData]:
        """Get contractor compliance records"""
        result = await db.execute(
            select(ComplianceData)
            .where(ComplianceData.contractor_id == contractor_id)
            .order_by(ComplianceData.created_at.desc())
        )
        return result.scalars().all()
    
    async def update_contractor_rating(
        self,
        db: AsyncSession,
        contractor_id: int,
        new_rating: float
    ) -> bool:
        """Update contractor rating"""
        result = await db.execute(
            update(Contractor)
            .where(Contractor.id == contractor_id)
            .values(
                rating=new_rating,
                updated_at=datetime.utcnow()
            )
        )
        await db.commit()
        return result.rowcount > 0
    
    async def increment_completed_jobs(
        self,
        db: AsyncSession,
        contractor_id: int
    ) -> bool:
        """Increment completed jobs count"""
        result = await db.execute(
            update(Contractor)
            .where(Contractor.id == contractor_id)
            .values(
                total_jobs_completed=Contractor.total_jobs_completed + 1,
                updated_at=datetime.utcnow()
            )
        )
        await db.commit()
        return result.rowcount > 0
    
    async def deactivate_contractor(
        self,
        db: AsyncSession,
        contractor_id: int,
        reason: Optional[str] = None
    ) -> bool:
        """Deactivate contractor"""
        update_data = {
            "status": "INACTIVE",
            "updated_at": datetime.utcnow()
        }
        
        if reason:
            update_data["notes"] = f"Deactivated: {reason}"
        
        result = await db.execute(
            update(Contractor)
            .where(Contractor.id == contractor_id)
            .values(**update_data)
        )
        await db.commit()
        return result.rowcount > 0
    
    async def get_contractor_by_user_id(self, db: AsyncSession, user_id: int) -> Optional[Contractor]:
        """Get contractor by user ID"""
        result = await db.execute(
            select(Contractor)
            .options(
                selectinload(Contractor.workspace),
                selectinload(Contractor.user),
                selectinload(Contractor.payouts),
                selectinload(Contractor.compliance_records)
            )
            .where(Contractor.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_job_assignments(
        self,
        db: AsyncSession,
        contractor_id: int,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get job assignments for contractor"""
        contractor = await self.get_contractor(db, contractor_id)
        if not contractor:
            return []
        
        # Get jobs assigned to this contractor
        query = select(Job).where(Job.assigned_to_id == contractor.user_id)
        
        if status:
            if status == "PENDING":
                query = query.where(Job.status == "assigned")
            elif status == "ACCEPTED":
                query = query.where(Job.status.in_(["in_progress", "evaluation_scheduled"]))
            elif status == "COMPLETED":
                query = query.where(Job.status == "completed")
        
        result = await db.execute(query.order_by(desc(Job.created_at)))
        jobs = result.scalars().all()
        
        assignments = []
        for job in jobs:
            assignment = {
                "id": job.id,
                "job_id": job.id,
                "contractor_id": contractor_id,
                "status": "ACCEPTED" if job.status in ["in_progress", "evaluation_scheduled"] else "PENDING",
                "assigned_at": job.created_at,
                "job_number": job.job_number,
                "job_title": job.title,
                "job_description": job.description,
                "job_location": job.location,
                "estimated_hours": job.estimated_hours,
                "estimated_cost": job.estimated_cost,
                "due_date": job.due_date,
                "customer_name": job.customer_name,
                "customer_phone": job.customer_phone
            }
            assignments.append(assignment)
        
        return assignments
    
    async def accept_job_assignment(
        self,
        db: AsyncSession,
        assignment_id: int,
        contractor_id: int
    ) -> bool:
        """Accept job assignment"""
        # Update job status to in_progress
        result = await db.execute(
            update(Job)
            .where(Job.id == assignment_id)
            .values(status="in_progress", updated_at=datetime.utcnow())
        )
        await db.commit()
        return result.rowcount > 0
    
    async def reject_job_assignment(
        self,
        db: AsyncSession,
        assignment_id: int,
        contractor_id: int,
        rejection_reason: Optional[str] = None
    ) -> bool:
        """Reject job assignment"""
        # Update job status back to lead or unassigned
        result = await db.execute(
            update(Job)
            .where(Job.id == assignment_id)
            .values(
                status="lead",
                assigned_to_id=None,
                notes=f"Rejected by contractor: {rejection_reason}" if rejection_reason else "Rejected by contractor",
                updated_at=datetime.utcnow()
            )
        )
        await db.commit()
        return result.rowcount > 0
    
    async def get_contractor_wallet(
        self,
        db: AsyncSession,
        contractor_id: int
    ) -> Dict[str, Any]:
        """Get contractor wallet information"""
        # Calculate wallet data from payouts
        payouts_result = await db.execute(
            select(Payout).where(Payout.contractor_id == contractor_id)
        )
        payouts = payouts_result.scalars().all()
        
        total_earned = sum(float(p.amount) for p in payouts if p.status == "COMPLETED")
        total_withdrawn = sum(float(p.amount) for p in payouts if p.status == "COMPLETED")
        pending_amount = sum(float(p.amount) for p in payouts if p.status == "PENDING")
        balance = total_earned - total_withdrawn
        
        return {
            "id": 1,  # Mock wallet ID
            "contractor_id": contractor_id,
            "balance": balance,
            "total_earned": total_earned,
            "total_withdrawn": total_withdrawn,
            "pending_amount": pending_amount,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    
    async def create_payout_request(
        self,
        db: AsyncSession,
        contractor_id: int,
        amount: float,
        payment_method: str,
        notes: Optional[str] = None
    ) -> Payout:
        """Create payout request"""
        # Generate payout number
        payout_number = f"PAY-{contractor_id:03d}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        payout = Payout(
            workspace_id=None,  # Will need to get from contractor
            contractor_id=contractor_id,
            payout_number=payout_number,
            amount=amount,
            payment_method=payment_method,
            description=f"Payout request - {payment_method}",
            notes=notes,
            status="PENDING"
        )
        
        db.add(payout)
        await db.commit()
        await db.refresh(payout)
        return payout
    
    async def upload_compliance_document(
        self,
        db: AsyncSession,
        contractor_id: int,
        compliance_type: str,
        document_name: str,
        file,
        document_number: Optional[str] = None,
        issue_date: Optional[str] = None,
        expiry_date: Optional[str] = None
    ) -> ComplianceData:
        """Upload compliance document"""
        # In a real implementation, you would save the file and get the path
        file_path = f"/uploads/compliance/{contractor_id}/{document_name}"
        
        compliance_doc = ComplianceData(
            workspace_id=None,  # Will need to get from contractor
            contractor_id=contractor_id,
            compliance_type=compliance_type,
            document_name=document_name,
            document_number=document_number,
            status="PENDING",
            issue_date=datetime.strptime(issue_date, "%Y-%m-%d").date() if issue_date else None,
            expiry_date=datetime.strptime(expiry_date, "%Y-%m-%d").date() if expiry_date else None,
            file_path=file_path,
            file_size=1024  # Mock file size
        )
        
        db.add(compliance_doc)
        await db.commit()
        await db.refresh(compliance_doc)
        return compliance_doc
    
    async def approve_contractor(
        self,
        db: AsyncSession,
        contractor_id: int
    ) -> bool:
        """Approve contractor"""
        result = await db.execute(
            update(Contractor)
            .where(Contractor.id == contractor_id)
            .values(status="ACTIVE", updated_at=datetime.utcnow())
        )
        await db.commit()
        return result.rowcount > 0
    
    async def suspend_contractor(
        self,
        db: AsyncSession,
        contractor_id: int,
        reason: Optional[str] = None
    ) -> bool:
        """Suspend contractor"""
        update_data = {
            "status": "SUSPENDED",
            "updated_at": datetime.utcnow()
        }
        
        if reason:
            update_data["notes"] = f"Suspended: {reason}"
        
        result = await db.execute(
            update(Contractor)
            .where(Contractor.id == contractor_id)
            .values(**update_data)
        )
        await db.commit()
        return result.rowcount > 0
    
    async def get_contractor_performance_stats(
        self,
        db: AsyncSession,
        contractor_id: int,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get contractor performance statistics"""
        contractor = await self.get_contractor(db, contractor_id)
        if not contractor:
            return {}
        
        # Build date filter
        date_filter = []
        if date_from:
            date_filter.append(Job.created_at >= date_from)
        if date_to:
            date_filter.append(Job.created_at <= date_to)
        
        # Get jobs in date range
        query = select(Job).where(Job.assigned_to_id == contractor.user_id)
        if date_filter:
            query = query.where(and_(*date_filter))
        
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        # Calculate performance metrics
        total_jobs = len(jobs)
        completed_jobs = [job for job in jobs if job.status == 'completed']
        on_time_jobs = [
            job for job in completed_jobs 
            if job.due_date and job.completed_date and job.completed_date <= job.due_date
        ]
        
        avg_rating = 0.0
        if contractor.rating:
            avg_rating = float(contractor.rating)
        
        total_revenue = sum(job.actual_cost or 0 for job in completed_jobs)
        
        return {
            "contractor_id": contractor_id,
            "total_jobs": total_jobs,
            "completed_jobs": len(completed_jobs),
            "completion_rate": len(completed_jobs) / total_jobs if total_jobs > 0 else 0,
            "on_time_completion_rate": len(on_time_jobs) / len(completed_jobs) if completed_jobs else 0,
            "average_rating": avg_rating,
            "total_revenue": float(total_revenue),
            "average_job_value": float(total_revenue / len(completed_jobs)) if completed_jobs else 0
        }
    
    async def get_available_jobs(
        self,
        db: AsyncSession,
        contractor_id: int,
        skip: int = 0,
        limit: int = 20,
        city: Optional[str] = None,
        job_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get available jobs for contractor"""
        contractor = await self.get_contractor(db, contractor_id)
        if not contractor:
            return []
        
        # Get unassigned jobs
        query = select(Job).where(
            and_(
                Job.assigned_to_id.is_(None),
                Job.status == "LEAD"
            )
        )
        
        # Apply filters
        if city:
            query = query.where(Job.location.ilike(f"%{city}%"))
        if job_type:
            query = query.where(Job.title.ilike(f"%{job_type}%"))
        
        query = query.order_by(desc(Job.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        available_jobs = []
        for job in jobs:
            available_jobs.append({
                "id": job.id,
                "job_number": job.job_number,
                "title": job.title,
                "description": job.description,
                "property_address": job.location,
                "customer_name": job.customer_name,
                "customer_phone": job.customer_phone,
                "estimated_cost": float(job.estimated_cost) if job.estimated_cost else 0,
                "estimated_hours": float(job.estimated_hours) if job.estimated_hours else 0,
                "due_date": job.due_date.isoformat() if job.due_date else None,
                "created_at": job.created_at.isoformat(),
                "status": job.status,
                "city": job.location.split(",")[-1].strip() if job.location and "," in job.location else "Unknown"
            })
        
        return available_jobs
    
    async def get_contractor_notifications(
        self,
        db: AsyncSession,
        contractor_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get contractor notifications"""
        contractor = await self.get_contractor(db, contractor_id)
        if not contractor:
            return []
        
        # Get recent job assignments and updates
        jobs_result = await db.execute(
            select(Job)
            .where(Job.assigned_to_id == contractor.user_id)
            .order_by(desc(Job.updated_at))
            .offset(skip)
            .limit(limit)
        )
        jobs = jobs_result.scalars().all()
        
        notifications = []
        for job in jobs:
            if job.status == "assigned":
                notifications.append({
                    "id": f"job-{job.id}",
                    "type": "job_assignment",
                    "title": "New Job Assignment",
                    "message": f"You have been assigned to job {job.job_number}",
                    "job_id": job.id,
                    "created_at": job.updated_at.isoformat(),
                    "read": False
                })
            elif job.status == "in_progress":
                notifications.append({
                    "id": f"job-progress-{job.id}",
                    "type": "job_update",
                    "title": "Job In Progress",
                    "message": f"Job {job.job_number} is now in progress",
                    "job_id": job.id,
                    "created_at": job.updated_at.isoformat(),
                    "read": True
                })
        
        return notifications


# Create global instance
contractor_crud = ContractorCRUD()