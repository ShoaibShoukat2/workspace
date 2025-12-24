"""
Profile Management Endpoints (Legacy Compatibility)
Provides compatibility with frontend expectations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_active_user, get_admin_user
from app.models.auth import User
from app.schemas.auth import UserResponse
from app.crud import auth as auth_crud

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    role: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all user profiles (for frontend compatibility)"""
    users, total = await auth_crud.get_users(db, skip, limit, role)
    
    # Convert to frontend-expected format
    profiles = []
    for user in users:
        profile = {
            "profileID": f"{user.role}-{user.id:03d}",
            "email": user.email,
            "name": user.full_name or user.email.split('@')[0],
            "user_role": user.role,
            "phone": user.phone,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login_at.isoformat() if user.last_login_at else None,
        }
        
        # Add role-specific fields
        if user.role == "contractor":
            profile.update({
                "trade": getattr(user, 'specialization', 'general'),
                "complianceStatus": "active" if user.is_active else "blocked",
                "insuranceExpiryDate": None,  # TODO: Add from contractor profile
            })
        
        profiles.append(profile)
    
    return profiles


@router.get("/{profile_id}", response_model=dict)
async def get_profile(
    profile_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific profile by profileID (for frontend compatibility)"""
    # Parse profileID format: role-001, role-002, etc.
    try:
        if '-' in profile_id:
            role_part, id_part = profile_id.rsplit('-', 1)
            user_id = int(id_part)
        else:
            # Fallback: try to parse as direct user ID
            user_id = int(profile_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid profile ID format"
        )
    
    user = await auth_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Convert to frontend-expected format
    profile = {
        "profileID": profile_id,
        "email": user.email,
        "name": user.full_name or user.email.split('@')[0],
        "user_role": user.role,
        "phone": user.phone,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login_at.isoformat() if user.last_login_at else None,
    }
    
    # Add role-specific fields
    if user.role == "contractor":
        profile.update({
            "trade": getattr(user, 'specialization', 'general'),
            "complianceStatus": "active" if user.is_active else "blocked",
            "insuranceExpiryDate": None,  # TODO: Add from contractor profile
        })
    elif user.role == "customer":
        profile.update({
            "properties": [],  # TODO: Add customer properties
            "activeJobs": 0,  # TODO: Count active jobs
        })
    elif user.role == "investor":
        profile.update({
            "investmentAmount": 0,  # TODO: Add investment data
            "roi": 0,  # TODO: Calculate ROI
        })
    
    return profile


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: dict,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new profile (admin only)"""
    # Convert frontend format to backend format
    from app.schemas.auth import UserRegister
    
    user_data = UserRegister(
        email=profile_data["email"],
        password=profile_data.get("password", "temp123"),  # Temporary password
        role=profile_data["user_role"],
        full_name=profile_data.get("name"),
        phone=profile_data.get("phone")
    )
    
    # Check if user already exists
    existing_user = await auth_crud.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user
    user = await auth_crud.create_user(db, user_data)
    
    # Generate profileID
    profile_id = f"{user.role}-{user.id:03d}"
    
    return {
        "profileID": profile_id,
        "email": user.email,
        "name": user.full_name or user.email.split('@')[0],
        "user_role": user.role,
        "message": "Profile created successfully"
    }


@router.patch("/{profile_id}", response_model=dict)
async def update_profile(
    profile_id: str,
    profile_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update profile"""
    # Parse profileID to get user_id
    try:
        if '-' in profile_id:
            role_part, id_part = profile_id.rsplit('-', 1)
            user_id = int(id_part)
        else:
            user_id = int(profile_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid profile ID format"
        )
    
    user = await auth_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Check permissions (user can update own profile, admin can update any)
    if current_user.id != user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    # Convert frontend format to backend format
    from app.schemas.auth import UserUpdate
    
    update_data = UserUpdate()
    if "name" in profile_data:
        update_data.full_name = profile_data["name"]
    if "phone" in profile_data:
        update_data.phone = profile_data["phone"]
    if "is_active" in profile_data and current_user.role == "admin":
        update_data.is_active = profile_data["is_active"]
    
    # Update user
    updated_user = await auth_crud.update_user(db, user.id, update_data)
    
    return {
        "profileID": profile_id,
        "email": updated_user.email,
        "name": updated_user.full_name or updated_user.email.split('@')[0],
        "user_role": updated_user.role,
        "message": "Profile updated successfully"
    }