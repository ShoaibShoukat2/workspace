"""
CSV-based Authentication
Simple authentication using CSV files
"""
from typing import Optional, Dict, Any
from app.data.csv_data import get_user_by_email, get_user_by_id, create_user
from app.core.password import verify_password, get_password_hash

async def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user with email and password"""
    user = get_user_by_email(email)
    if not user:
        return None
    
    if not verify_password(password, user['password_hash']):
        return None
    
    return user

async def get_user_by_email_async(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email (async version)"""
    return get_user_by_email(email)

async def get_user_by_id_async(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID (async version)"""
    return get_user_by_id(user_id)

async def create_user_async(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create new user (async version)"""
    # Hash password
    if 'password' in user_data:
        user_data['password_hash'] = get_password_hash(user_data['password'])
        del user_data['password']
    
    return create_user(user_data)