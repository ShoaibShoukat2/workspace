"""
Customer CRUD Operations
Real database integration for customer portal
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta

from app.models.auth import User
from app.models.workspace import Job
from app.schemas.customer import (
    CustomerProfileUpdate, CustomerPreferencesUpdate, IssueReportCreate
)


class CustomerCRUD:
    """Customer CRUD operations with real database integration"""
    
    async def get_customer_dashboard(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """Get customer dashboard data from database"""
        # Get user
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            return {}
        
        # Get customer's jobs
        jobs_result = await db.execute(
            select(Job).where(Job.customer_email == user.email)
            .order_by(desc(Job.created_at))
        )
        jobs = jobs_result.scalars().all()
        
        # Calculate dashboard metrics
        active_jobs = [job for job in jobs if job.status in ['open', 'in_progress', 'assigned']]
        completed_jobs = [job for job in jobs if job.status == 'completed']
        
        # Get latest active job for tracking
        latest_job = active_jobs[0] if active_jobs else None
        
        return {
            "total_jobs": len(jobs),
            "active_jobs": len(active_jobs),
            "completed_jobs": len(completed_jobs),
            "latest_job": {
                "id": latest_job.id,
                "title": latest_job.title,
                "status": latest_job.status,
                "property_address": latest_job.property_address,
                "scheduled_date": latest_job.scheduled_date.isoformat() if latest_job.scheduled_date else None,
                "contractor_name": "Alex M.",  # TODO: Get from contractor relationship
                "estimated_completion": (datetime.now() + timedelta(days=3)).isoformat()
            } if latest_job else None,
            "recent_activity": [
                {
                    "type": "job_created",
                    "message": f"Job '{job.title}' was created",
                    "timestamp": job.created_at.isoformat(),
                    "job_id": job.id
                } for job in jobs[:5]
            ]
        }
    
    async def get_customer_jobs(
        self,
        db: AsyncSession,
        customer_email: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> List[Job]:
        """Get jobs for customer from database"""
        query = select(Job).where(Job.customer_email == customer_email)
        
        if status:
            query = query.where(Job.status == status)
        
        query = query.order_by(desc(Job.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_customer_job(
        self,
        db: AsyncSession,
        job_id: int,
        customer_email: str
    ) -> Optional[Job]:
        """Get specific job for customer from database"""
        result = await db.execute(
            select(Job).where(
                and_(Job.id == job_id, Job.customer_email == customer_email)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_job_tracking(self, db: AsyncSession, job_id: int) -> Dict[str, Any]:
        """Get real-time job tracking data"""
        # Get job
        job_result = await db.execute(select(Job).where(Job.id == job_id))
        job = job_result.scalar_one_or_none()
        
        if not job:
            return {}
        
        # Mock real-time tracking data (in production, this would come from GPS tracking)
        return {
            "job_id": job_id,
            "status": job.status,
            "contractor_location": {
                "latitude": 38.9072,
                "longitude": -77.0369,
                "last_updated": datetime.now().isoformat(),
                "eta_minutes": 12 if job.status == 'assigned' else 0
            },
            "job_location": {
                "latitude": 38.9022,
                "longitude": -77.0319,
                "address": job.property_address
            },
            "timeline": [
                {
                    "step": "Job Created",
                    "status": "completed",
                    "timestamp": job.created_at.isoformat(),
                    "description": "Your job request has been received"
                },
                {
                    "step": "Contractor Assigned",
                    "status": "completed" if job.assigned_to_id else "pending",
                    "timestamp": job.updated_at.isoformat() if job.assigned_to_id else None,
                    "description": "Professional contractor has been assigned"
                },
                {
                    "step": "En Route",
                    "status": "active" if job.status == 'assigned' else "pending",
                    "timestamp": None,
                    "description": "Contractor is traveling to your location"
                },
                {
                    "step": "Work in Progress",
                    "status": "completed" if job.status == 'in_progress' else "pending",
                    "timestamp": None,
                    "description": "Work is being performed"
                },
                {
                    "step": "Completed",
                    "status": "completed" if job.status == 'completed' else "pending",
                    "timestamp": None,
                    "description": "Job has been completed successfully"
                }
            ]
        }
    
    async def get_contractor_location(self, db: AsyncSession, job_id: int) -> Optional[Dict[str, Any]]:
        """Get real-time contractor location"""
        # Get job with contractor
        job_result = await db.execute(
            select(Job).where(Job.id == job_id)
        )
        job = job_result.scalar_one_or_none()
        
        if not job or not job.assigned_to_id:
            return None
        
        # Mock real-time location (in production, this would come from contractor's mobile app)
        return {
            "contractor_id": job.assigned_to_id,
            "contractor_name": "Alex M.",
            "location": {
                "latitude": 38.9072,
                "longitude": -77.0369,
                "accuracy": 10,
                "last_updated": datetime.now().isoformat()
            },
            "status": "en_route",
            "eta_minutes": 12,
            "phone": "+1-555-0123"
        }
    
    async def get_job_materials(self, db: AsyncSession, job_id: int) -> List[Dict[str, Any]]:
        """Get materials for job"""
        # Mock materials data (in production, this would come from materials table)
        return [
            {
                "id": 1,
                "name": "Premium Interior Paint",
                "description": "High-quality latex paint for interior walls",
                "quantity": 3,
                "unit": "gallons",
                "estimated_cost": 45.99,
                "supplier": "Home Depot",
                "sku": "HD-PAINT-001",
                "status": "pending_purchase",
                "purchase_url": "https://www.homedepot.com/p/paint"
            },
            {
                "id": 2,
                "name": "Paint Brushes & Rollers",
                "description": "Professional painting tools set",
                "quantity": 1,
                "unit": "set",
                "estimated_cost": 29.99,
                "supplier": "Home Depot",
                "sku": "HD-TOOLS-002",
                "status": "pending_purchase",
                "purchase_url": "https://www.homedepot.com/p/tools"
            }
        ]
    
    async def approve_checkpoint(
        self,
        db: AsyncSession,
        checkpoint_id: int,
        customer_note: Optional[str] = None,
        rating: Optional[int] = None
    ) -> bool:
        """Approve job checkpoint"""
        # Mock checkpoint approval (in production, this would update checkpoint table)
        return True
    
    async def reject_checkpoint(
        self,
        db: AsyncSession,
        checkpoint_id: int,
        rejection_reason: str
    ) -> bool:
        """Reject job checkpoint"""
        # Mock checkpoint rejection (in production, this would update checkpoint table)
        return True
    
    async def report_job_issue(
        self,
        db: AsyncSession,
        job_id: int,
        issue_data: IssueReportCreate,
        customer_id: int
    ) -> Dict[str, Any]:
        """Report an issue with the job"""
        # Create dispute record (this would integrate with dispute system)
        issue = {
            "id": 999,  # Would be generated by database
            "job_id": job_id,
            "customer_id": customer_id,
            "title": issue_data.title,
            "description": issue_data.description,
            "category": issue_data.category,
            "severity": issue_data.severity,
            "status": "open",
            "created_at": datetime.now(),
            "reference_number": f"ISSUE-{job_id}-{datetime.now().strftime('%Y%m%d%H%M')}"
        }
        
        return issue
    
    async def get_customer_notifications(
        self,
        db: AsyncSession,
        customer_id: int,
        skip: int = 0,
        limit: int = 20,
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get customer notifications"""
        # Mock notifications (in production, this would come from notifications table)
        notifications = [
            {
                "id": 1,
                "title": "Contractor En Route",
                "message": "Alex M. is on the way to your property",
                "type": "job_update",
                "read": False,
                "created_at": datetime.now() - timedelta(minutes=5),
                "job_id": 101
            },
            {
                "id": 2,
                "title": "Materials Ready for Purchase",
                "message": "Your materials list is ready for review",
                "type": "materials",
                "read": True,
                "created_at": datetime.now() - timedelta(hours=2),
                "job_id": 101
            }
        ]
        
        if unread_only:
            notifications = [n for n in notifications if not n["read"]]
        
        return notifications[skip:skip + limit]
    
    async def mark_notification_read(
        self,
        db: AsyncSession,
        notification_id: int,
        customer_id: int
    ) -> bool:
        """Mark notification as read"""
        # Mock notification update (in production, this would update notifications table)
        return True
    
    async def mark_all_notifications_read(
        self,
        db: AsyncSession,
        customer_id: int
    ) -> int:
        """Mark all notifications as read"""
        # Mock bulk update (in production, this would update notifications table)
        return 5  # Number of notifications marked as read
    
    async def get_customer_profile(self, db: AsyncSession, customer_id: int) -> Dict[str, Any]:
        """Get customer profile"""
        user_result = await db.execute(select(User).where(User.id == customer_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            return {}
        
        return {
            "id": user.id,
            "name": user.full_name or user.email.split('@')[0],
            "email": user.email,
            "phone": user.phone,
            "address": None,  # TODO: Add address field to user model
            "preferences": {
                "notifications_email": True,
                "notifications_sms": False,
                "marketing_emails": False
            }
        }
    
    async def update_customer_profile(
        self,
        db: AsyncSession,
        customer_id: int,
        profile_data: CustomerProfileUpdate
    ) -> Dict[str, Any]:
        """Update customer profile"""
        user_result = await db.execute(select(User).where(User.id == customer_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            return {}
        
        # Update user fields
        if profile_data.name:
            user.full_name = profile_data.name
        if profile_data.phone:
            user.phone = profile_data.phone
        
        await db.commit()
        await db.refresh(user)
        
        return {
            "id": user.id,
            "name": user.full_name,
            "email": user.email,
            "phone": user.phone
        }
    
    async def get_customer_preferences(self, db: AsyncSession, customer_id: int) -> Dict[str, Any]:
        """Get customer notification preferences"""
        # Mock preferences (in production, this would come from preferences table)
        return {
            "notifications_email": True,
            "notifications_sms": False,
            "marketing_emails": False,
            "job_updates": True,
            "contractor_messages": True,
            "payment_reminders": True
        }
    
    async def update_customer_preferences(
        self,
        db: AsyncSession,
        customer_id: int,
        preferences_data: CustomerPreferencesUpdate
    ) -> Dict[str, Any]:
        """Update customer notification preferences"""
        # Mock preferences update (in production, this would update preferences table)
        return {
            "notifications_email": preferences_data.notifications_email,
            "notifications_sms": preferences_data.notifications_sms,
            "marketing_emails": preferences_data.marketing_emails,
            "updated_at": datetime.now().isoformat()
        }
    
    # Public endpoints for token-based access
    async def get_job_by_token(self, db: AsyncSession, token: str) -> Optional[Dict[str, Any]]:
        """Get job details using magic token"""
        # Mock token validation (in production, this would validate against job tokens table)
        if token in ["mock-token-123", "demo-token-456"]:
            # Return mock job data
            return {
                "id": 101,
                "title": "Master Bathroom Renovation",
                "property_address": "123 Main Street",
                "city": "Los Angeles",
                "customer_name": "Sarah Johnson",
                "customer_email": "sarah@example.com",
                "status": "in_progress",
                "trade": "painting",
                "estimated_cost": "$2,500.00",
                "description": "Complete bathroom renovation including painting, tiling, and fixture installation",
                "scheduled_date": datetime.now().isoformat(),
                "contractor_name": "Alex M.",
                "contractor_phone": "+1-555-0123",
                "materials": [
                    {
                        "name": "Premium Interior Paint",
                        "quantity": 3,
                        "unit": "gallons",
                        "estimated_cost": 45.99
                    }
                ]
            }
        
        return None
    
    async def get_job_tracking_by_token(self, db: AsyncSession, token: str) -> Optional[Dict[str, Any]]:
        """Get job tracking using magic token"""
        job_data = await self.get_job_by_token(db, token)
        if not job_data:
            return None
        
        return await self.get_job_tracking(db, job_data["id"])
    
    async def approve_quote_by_token(
        self,
        db: AsyncSession,
        token: str,
        signature: Optional[str] = None
    ) -> bool:
        """Approve quote using magic token"""
        job_data = await self.get_job_by_token(db, token)
        if not job_data:
            return False
        
        # Mock quote approval (in production, this would update job status and create approval record)
        return True
    
    async def generate_customer_credentials(
        self,
        db: AsyncSession,
        email: str,
        job_number: str
    ) -> Optional[Dict[str, Any]]:
        """Generate temporary credentials for customer access"""
        # Validate job and email match
        try:
            job_id = int(job_number.replace('JOB-', ''))
            job_result = await db.execute(
                select(Job).where(
                    and_(Job.customer_email == email, Job.id == job_id)
                )
            )
            job = job_result.scalar_one_or_none()
            
            if not job:
                return None
            
            # Generate temporary credentials
            temp_password = f"apex-{job.id}-temp"
            
            return {
                "email": email,
                "temporary_password": temp_password,
                "portal_url": f"/customer/dashboard",
                "expires_at": (datetime.now() + timedelta(days=30)).isoformat(),
                "job_id": job.id
            }
        except ValueError:
            return None


# Create instance
customer_crud = CustomerCRUD()