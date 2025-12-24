"""
CSV-based Authentication Endpoints
Simple authentication using CSV files
"""
from fastapi import APIRouter, HTTPException, status
from datetime import timedelta
from typing import Dict, Any

from app.core.security import create_access_token, create_refresh_token
from app.crud.csv_auth import authenticate_user, get_user_by_email_async
from app.data.csv_data import get_dashboard_stats

router = APIRouter()

@router.post("/login")
async def login(credentials: Dict[str, str]):
    """Login with email and password"""
    email = credentials.get("email")
    password = credentials.get("password")
    
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    # Authenticate user
    user = await authenticate_user(email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create tokens
    access_token = create_access_token(
        subject=user["email"],
        expires_delta=timedelta(minutes=60)
    )
    refresh_token = create_refresh_token(
        subject=user["email"],
        expires_delta=timedelta(days=7)
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": int(user["id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"]
        },
        "profile": {
            "id": int(user["id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "user_role": user["role"],
            "profileID": f"PROF-{user['id']:06d}",
            "profile_id": f"PROF-{user['id']:06d}"
        }
    }

@router.get("/me")
async def get_current_user_profile(current_user: Dict[str, Any] = None):
    """Get current user profile"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    return {
        "id": int(current_user["id"]),
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "role": current_user["role"],
        "is_active": current_user.get("is_active", True)
    }

@router.post("/logout")
async def logout():
    """Logout user"""
    return {"message": "Successfully logged out"}

# Legacy endpoints for compatibility
@router.post("/signup")
async def signup(user_data: Dict[str, Any]):
    """Legacy signup endpoint"""
    # For now, just return success - in real implementation would create user
    return {
        "message": "User created successfully",
        "user": {
            "id": 999,
            "email": user_data.get("email", ""),
            "role": user_data.get("role", "CUSTOMER")
        }
    }

@router.get("/profiles")
async def get_profiles():
    """Get all user profiles (legacy endpoint)"""
    from app.data.csv_data import get_users
    
    users = get_users()
    profiles = []
    
    for user in users:
        profiles.append({
            "id": int(user["id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "user_role": user["role"],
            "profileID": f"PROF-{user['id']:06d}",
            "profile_id": f"PROF-{user['id']:06d}"
        })
    
    return profiles