"""
Workspace CRUD Operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, List, Tuple
from uuid import UUID

from app.models.workspace import Workspace, WorkspaceMember, Job, Contractor, Estimate, Payout
from app.models.auth import User
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


class WorkspaceCRUD:
    
    async def get_workspace(self, db: AsyncSession, workspace_id: UUID) -> Optional[Workspace]:
        """Get workspace by UUID"""
        result = await db.execute(
            select(Workspace)
            .options(selectinload(Workspace.owner))
            .where(Workspace.workspace_id == workspace_id)
        )
        return result.scalar_one_or_none()
    
    async def get_workspace_by_id(self, db: AsyncSession, id: int) -> Optional[Workspace]:
        """Get workspace by ID"""
        result = await db.execute(
            select(Workspace)
            .options(selectinload(Workspace.owner))
            .where(Workspace.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_workspaces(
        self, 
        db: AsyncSession, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 20,
        search: Optional[str] = None,
        workspace_type: Optional[str] = None
    ) -> Tuple[List[Workspace], int]:
        """Get workspaces for a user with filtering"""
        # Base query for workspaces user has access to
        base_query = select(Workspace).join(WorkspaceMember).where(
            and_(
                WorkspaceMember.user_id == user_id,
                Workspace.is_active == True
            )
        )
        
        # Apply filters
        filters = []
        if search:
            filters.append(
                or_(
                    Workspace.name.ilike(f"%{search}%"),
                    Workspace.description.ilike(f"%{search}%")
                )
            )
        if workspace_type:
            filters.append(Workspace.workspace_type == workspace_type)
        
        if filters:
            base_query = base_query.where(and_(*filters))
        
        # Get total count
        count_result = await db.execute(
            select(func.count(Workspace.id)).select_from(base_query.subquery())
        )
        total = count_result.scalar()
        
        # Get paginated results
        result = await db.execute(
            base_query
            .options(selectinload(Workspace.owner))
            .order_by(Workspace.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        workspaces = result.scalars().all()
        
        return workspaces, total
    
    async def create_workspace(
        self, 
        db: AsyncSession, 
        workspace_data: WorkspaceCreate, 
        owner_id: int
    ) -> Workspace:
        """Create new workspace"""
        workspace = Workspace(
            name=workspace_data.name,
            workspace_type=workspace_data.workspace_type.value,
            description=workspace_data.description,
            owner_id=owner_id
        )
        
        db.add(workspace)
        await db.flush()  # Get the ID
        
        # Add owner as workspace member
        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=owner_id,
            role="OWNER"
        )
        db.add(member)
        
        await db.commit()
        await db.refresh(workspace)
        return workspace
    
    async def update_workspace(
        self, 
        db: AsyncSession, 
        workspace_id: int, 
        workspace_data: WorkspaceUpdate
    ) -> Optional[Workspace]:
        """Update workspace"""
        workspace = await self.get_workspace_by_id(db, workspace_id)
        if not workspace:
            return None
        
        update_data = workspace_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(workspace, field):
                setattr(workspace, field, value)
        
        await db.commit()
        await db.refresh(workspace)
        return workspace
    
    async def delete_workspace(self, db: AsyncSession, workspace_id: int) -> bool:
        """Soft delete workspace"""
        result = await db.execute(
            update(Workspace)
            .where(Workspace.id == workspace_id)
            .values(is_active=False)
        )
        await db.commit()
        return result.rowcount > 0
    
    async def user_has_workspace_access(
        self, 
        db: AsyncSession, 
        user_id: int, 
        workspace_id: int
    ) -> bool:
        """Check if user has access to workspace"""
        result = await db.execute(
            select(WorkspaceMember.id)
            .where(
                and_(
                    WorkspaceMember.user_id == user_id,
                    WorkspaceMember.workspace_id == workspace_id
                )
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def user_is_workspace_owner_or_admin(
        self, 
        db: AsyncSession, 
        user_id: int, 
        workspace_id: int
    ) -> bool:
        """Check if user is workspace owner or admin"""
        result = await db.execute(
            select(WorkspaceMember.id)
            .where(
                and_(
                    WorkspaceMember.user_id == user_id,
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.role.in_(["OWNER", "ADMIN"])
                )
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def get_workspace_members(
        self, 
        db: AsyncSession, 
        workspace_id: int
    ) -> List[WorkspaceMember]:
        """Get workspace members"""
        result = await db.execute(
            select(WorkspaceMember)
            .options(selectinload(WorkspaceMember.user))
            .where(WorkspaceMember.workspace_id == workspace_id)
            .order_by(WorkspaceMember.joined_at.desc())
        )
        return result.scalars().all()
    
    async def add_workspace_member(
        self, 
        db: AsyncSession, 
        workspace_id: int, 
        user_id: int, 
        role: str = "MEMBER"
    ) -> WorkspaceMember:
        """Add member to workspace"""
        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user_id,
            role=role
        )
        
        db.add(member)
        await db.commit()
        await db.refresh(member)
        return member
    
    async def remove_workspace_member(
        self, 
        db: AsyncSession, 
        workspace_id: int, 
        user_id: int
    ) -> bool:
        """Remove member from workspace"""
        result = await db.execute(
            delete(WorkspaceMember)
            .where(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == user_id
                )
            )
        )
        await db.commit()
        return result.rowcount > 0
    
    async def update_member_role(
        self, 
        db: AsyncSession, 
        workspace_id: int, 
        user_id: int, 
        new_role: str
    ) -> bool:
        """Update workspace member role"""
        result = await db.execute(
            update(WorkspaceMember)
            .where(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == user_id
                )
            )
            .values(role=new_role)
        )
        await db.commit()
        return result.rowcount > 0
    
    async def get_workspace_stats(self, db: AsyncSession, workspace_id: int) -> dict:
        """Get workspace statistics"""
        # Jobs stats
        jobs_result = await db.execute(
            select(
                func.count(Job.id).label('total_jobs'),
                func.count(Job.id).filter(Job.status.in_(['IN_PROGRESS', 'EVALUATION_SCHEDULED'])).label('active_jobs'),
                func.count(Job.id).filter(Job.status == 'COMPLETED').label('completed_jobs')
            )
            .where(Job.workspace_id == workspace_id)
        )
        jobs_stats = jobs_result.first()
        
        # Contractors stats
        contractors_result = await db.execute(
            select(
                func.count(Contractor.id).label('total_contractors'),
                func.count(Contractor.id).filter(Contractor.status == 'ACTIVE').label('active_contractors')
            )
            .where(Contractor.workspace_id == workspace_id)
        )
        contractors_stats = contractors_result.first()
        
        # Estimates stats
        estimates_result = await db.execute(
            select(
                func.count(Estimate.id).label('total_estimates'),
                func.count(Estimate.id).filter(Estimate.status == 'SENT').label('pending_estimates'),
                func.count(Estimate.id).filter(Estimate.status == 'APPROVED').label('approved_estimates')
            )
            .where(Estimate.workspace_id == workspace_id)
        )
        estimates_stats = estimates_result.first()
        
        # Revenue stats
        revenue_result = await db.execute(
            select(
                func.coalesce(func.sum(Job.actual_cost), 0).label('total_revenue')
            )
            .where(
                and_(
                    Job.workspace_id == workspace_id,
                    Job.status == 'COMPLETED'
                )
            )
        )
        total_revenue = revenue_result.scalar()
        
        # Pending payouts
        payouts_result = await db.execute(
            select(
                func.coalesce(func.sum(Payout.amount), 0).label('pending_payouts')
            )
            .where(
                and_(
                    Payout.workspace_id == workspace_id,
                    Payout.status.in_(['PENDING', 'PROCESSING'])
                )
            )
        )
        pending_payouts = payouts_result.scalar()
        
        # Recent activity (simplified)
        recent_activity = []
        
        return {
            'total_jobs': jobs_stats.total_jobs or 0,
            'active_jobs': jobs_stats.active_jobs or 0,
            'completed_jobs': jobs_stats.completed_jobs or 0,
            'total_contractors': contractors_stats.total_contractors or 0,
            'active_contractors': contractors_stats.active_contractors or 0,
            'total_estimates': estimates_stats.total_estimates or 0,
            'pending_estimates': estimates_stats.pending_estimates or 0,
            'approved_estimates': estimates_stats.approved_estimates or 0,
            'total_revenue': float(total_revenue or 0),
            'pending_payouts': float(pending_payouts or 0),
            'compliance_issues': 0,  # TODO: Implement compliance counting
            'recent_activity': recent_activity
        }


# Create global instance
workspace_crud = WorkspaceCRUD()