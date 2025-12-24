"""
Job CRUD Operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime
import secrets

from app.models.workspace import (
    Job, JobEvaluation, JobPhoto, JobQuote, JobCheckpoint, 
    JobProgressNote, MaterialSuggestion, JobAttachment, Workspace
)
from app.models.auth import User
from app.schemas.job import JobCreate, JobUpdate, JobEvaluationUpdate, JobProgressNoteCreate
from app.utils.helpers import generate_job_number


class JobCRUD:
    
    async def get_job(self, db: AsyncSession, job_id: int) -> Optional[Job]:
        """Get job by ID"""
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
    
    async def get_job_with_details(self, db: AsyncSession, job_id: int) -> Optional[Job]:
        """Get job with all related details"""
        result = await db.execute(
            select(Job)
            .options(
                selectinload(Job.workspace),
                selectinload(Job.assigned_to),
                selectinload(Job.created_by),
                selectinload(Job.evaluation),
                selectinload(Job.photos),
                selectinload(Job.quotes),
                selectinload(Job.checkpoints),
                selectinload(Job.progress_notes).selectinload(JobProgressNote.added_by),
                selectinload(Job.material_suggestions),
                selectinload(Job.attachments).selectinload(JobAttachment.uploaded_by)
            )
            .where(Job.id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def get_jobs(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        workspace_id: Optional[UUID] = None,
        status: Optional[str] = None,
        assigned_to: Optional[int] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Job], int]:
        """Get jobs with filtering"""
        # Base query - user must have access to workspace
        base_query = select(Job).join(Workspace).join(
            WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id
        ).where(WorkspaceMember.user_id == user_id)
        
        # Apply filters
        filters = []
        if workspace_id:
            filters.append(Job.workspace_id == workspace_id)
        if status:
            filters.append(Job.status == status)
        if assigned_to:
            filters.append(Job.assigned_to_id == assigned_to)
        if search:
            filters.append(
                or_(
                    Job.title.ilike(f"%{search}%"),
                    Job.description.ilike(f"%{search}%"),
                    Job.job_number.ilike(f"%{search}%"),
                    Job.customer_name.ilike(f"%{search}%")
                )
            )
        
        if filters:
            base_query = base_query.where(and_(*filters))
        
        # Get total count
        count_result = await db.execute(
            select(func.count(Job.id)).select_from(base_query.subquery())
        )
        total = count_result.scalar()
        
        # Get paginated results
        result = await db.execute(
            base_query
            .options(
                selectinload(Job.workspace),
                selectinload(Job.assigned_to),
                selectinload(Job.created_by)
            )
            .order_by(Job.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        jobs = result.scalars().all()
        
        return jobs, total
    
    async def create_job(
        self, 
        db: AsyncSession, 
        job_data: JobCreate, 
        created_by_id: int
    ) -> Job:
        """Create new job"""
        job_number = generate_job_number()
        
        job = Job(
            workspace_id=job_data.workspace_id,
            job_number=job_number,
            title=job_data.title,
            description=job_data.description,
            priority=job_data.priority.value,
            assigned_to_id=job_data.assigned_to_id,
            created_by_id=created_by_id,
            estimated_hours=job_data.estimated_hours,
            estimated_cost=job_data.estimated_cost,
            start_date=job_data.start_date,
            due_date=job_data.due_date,
            location=job_data.location,
            customer_name=job_data.customer_name,
            customer_email=job_data.customer_email,
            customer_phone=job_data.customer_phone,
            customer_address=job_data.customer_address,
            scheduled_evaluation_at=job_data.scheduled_evaluation_at,
            expected_start=job_data.expected_start,
            expected_end=job_data.expected_end
        )
        
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job
    
    async def update_job(
        self, 
        db: AsyncSession, 
        job_id: int, 
        job_data: JobUpdate
    ) -> Optional[Job]:
        """Update job"""
        job = await self.get_job(db, job_id)
        if not job:
            return None
        
        update_data = job_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(job, field):
                if field in ['status', 'priority'] and value:
                    setattr(job, field, value.value if hasattr(value, 'value') else value)
                else:
                    setattr(job, field, value)
        
        await db.commit()
        await db.refresh(job)
        return job
    
    async def user_has_job_access(
        self, 
        db: AsyncSession, 
        user_id: int, 
        job_id: int
    ) -> bool:
        """Check if user has access to job"""
        result = await db.execute(
            select(Job.id)
            .join(Workspace)
            .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
            .where(
                and_(
                    Job.id == job_id,
                    WorkspaceMember.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def user_can_edit_job(
        self, 
        db: AsyncSession, 
        user_id: int, 
        job_id: int
    ) -> bool:
        """Check if user can edit job"""
        result = await db.execute(
            select(Job.id)
            .join(Workspace)
            .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
            .where(
                and_(
                    Job.id == job_id,
                    WorkspaceMember.user_id == user_id,
                    or_(
                        WorkspaceMember.role.in_(["OWNER", "ADMIN"]),
                        Job.assigned_to_id == user_id,
                        Job.created_by_id == user_id
                    )
                )
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def upload_job_photo(
        self,
        db: AsyncSession,
        job_id: int,
        photo_type: str,
        file,
        caption: Optional[str],
        uploaded_by_id: int
    ) -> JobPhoto:
        """Upload job photo"""
        # TODO: Implement actual file upload logic
        file_path = f"uploads/jobs/{job_id}/{file.filename}"
        file_url = f"/static/{file_path}"
        
        photo = JobPhoto(
            job_id=job_id,
            photo_type=photo_type,
            file_path=file_path,
            file_url=file_url,
            caption=caption,
            uploaded_by_id=uploaded_by_id
        )
        
        db.add(photo)
        await db.commit()
        await db.refresh(photo)
        return photo
    
    async def update_job_evaluation(
        self,
        db: AsyncSession,
        job_id: int,
        evaluation_data: JobEvaluationUpdate
    ) -> JobEvaluation:
        """Update job evaluation"""
        # Get or create evaluation
        result = await db.execute(
            select(JobEvaluation).where(JobEvaluation.job_id == job_id)
        )
        evaluation = result.scalar_one_or_none()
        
        if not evaluation:
            evaluation = JobEvaluation(job_id=job_id)
            db.add(evaluation)
        
        # Update fields
        update_data = evaluation_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(evaluation, field):
                setattr(evaluation, field, value)
        
        await db.commit()
        await db.refresh(evaluation)
        return evaluation
    
    async def submit_job_evaluation(self, db: AsyncSession, job_id: int) -> bool:
        """Submit job evaluation"""
        result = await db.execute(
            update(JobEvaluation)
            .where(JobEvaluation.job_id == job_id)
            .values(
                is_submitted=True,
                submitted_at=datetime.utcnow()
            )
        )
        
        # Update job status
        await db.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(status="EVALUATION_COMPLETED")
        )
        
        await db.commit()
        return result.rowcount > 0
    
    async def get_job_materials(
        self, 
        db: AsyncSession, 
        job_id: int
    ) -> List[MaterialSuggestion]:
        """Get material suggestions for job"""
        result = await db.execute(
            select(MaterialSuggestion)
            .where(MaterialSuggestion.job_id == job_id)
            .order_by(MaterialSuggestion.item_name)
        )
        return result.scalars().all()
    
    async def get_job_checkpoints(
        self, 
        db: AsyncSession, 
        job_id: int
    ) -> List[JobCheckpoint]:
        """Get job checkpoints"""
        result = await db.execute(
            select(JobCheckpoint)
            .where(JobCheckpoint.job_id == job_id)
            .order_by(JobCheckpoint.created_at)
        )
        return result.scalars().all()
    
    async def add_progress_note(
        self,
        db: AsyncSession,
        job_id: int,
        note_data: JobProgressNoteCreate,
        added_by_id: int
    ) -> JobProgressNote:
        """Add progress note to job"""
        note = JobProgressNote(
            job_id=job_id,
            note=note_data.note,
            added_by_id=added_by_id,
            checkpoint_id=note_data.checkpoint_id
        )
        
        db.add(note)
        await db.commit()
        await db.refresh(note)
        return note
    
    async def complete_job(
        self,
        db: AsyncSession,
        job_id: int,
        completion_notes: Optional[str] = None
    ) -> bool:
        """Mark job as completed"""
        result = await db.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(
                status="COMPLETED",
                completed_date=datetime.utcnow().date(),
                notes=completion_notes
            )
        )
        await db.commit()
        return result.rowcount > 0
    
    async def get_job_timeline(self, db: AsyncSession, job_id: int) -> dict:
        """Get job timeline for customer"""
        # Get job with related data
        job = await self.get_job_with_details(db, job_id)
        if not job:
            return {}
        
        timeline_events = []
        
        # Job created
        timeline_events.append({
            "event": "Job Created",
            "timestamp": job.created_at,
            "description": f"Job {job.job_number} was created",
            "status": "completed"
        })
        
        # Add evaluation events
        if job.evaluation and job.evaluation.submitted_at:
            timeline_events.append({
                "event": "Evaluation Completed",
                "timestamp": job.evaluation.submitted_at,
                "description": "Site evaluation completed by contractor",
                "status": "completed"
            })
        
        # Add checkpoint events
        for checkpoint in job.checkpoints:
            event_name = f"{checkpoint.checkpoint_type.replace('_', ' ').title()} Checkpoint"
            status = "completed" if checkpoint.status == "APPROVED" else "pending"
            
            timeline_events.append({
                "event": event_name,
                "timestamp": checkpoint.approved_at or checkpoint.created_at,
                "description": checkpoint.scope_summary or f"{event_name} created",
                "status": status
            })
        
        # Sort by timestamp
        timeline_events.sort(key=lambda x: x["timestamp"])
        
        return {
            "job_id": job_id,
            "timeline_events": timeline_events,
            "current_status": job.status,
            "progress_percentage": self._calculate_progress_percentage(job),
            "estimated_completion": job.expected_end
        }
    
    def _calculate_progress_percentage(self, job: Job) -> float:
        """Calculate job progress percentage"""
        status_progress = {
            "LEAD": 0,
            "EVALUATION_SCHEDULED": 10,
            "EVALUATION_COMPLETED": 20,
            "AWAITING_PRE_START_APPROVAL": 30,
            "IN_PROGRESS": 60,
            "MID_CHECKPOINT_PENDING": 70,
            "AWAITING_FINAL_APPROVAL": 90,
            "COMPLETED": 100,
            "CANCELLED": 0
        }
        return status_progress.get(job.status, 0)
    
    async def approve_checkpoint(
        self,
        db: AsyncSession,
        checkpoint_id: int,
        customer_note: Optional[str] = None
    ) -> bool:
        """Approve job checkpoint"""
        result = await db.execute(
            update(JobCheckpoint)
            .where(JobCheckpoint.id == checkpoint_id)
            .values(
                status="APPROVED",
                approved_at=datetime.utcnow(),
                customer_note=customer_note
            )
        )
        await db.commit()
        return result.rowcount > 0
    
    async def reject_checkpoint(
        self,
        db: AsyncSession,
        checkpoint_id: int,
        rejection_reason: str
    ) -> bool:
        """Reject job checkpoint"""
        result = await db.execute(
            update(JobCheckpoint)
            .where(JobCheckpoint.id == checkpoint_id)
            .values(
                status="REJECTED",
                rejected_at=datetime.utcnow(),
                rejection_reason=rejection_reason
            )
        )
        await db.commit()
        return result.rowcount > 0


# Import WorkspaceMember here to avoid circular import
from app.models.workspace import WorkspaceMember

# Create global instance
job_crud = JobCRUD()