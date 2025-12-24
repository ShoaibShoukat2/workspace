"""
Security utilities
JWT authentication, password hashing, etc.
"""
from datetime import datetime, timedelta
from typing import Optional, Union, Any, Dict
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.password import verify_password, get_password_hash
from app.models.auth import User

# JWT Security
security = HTTPBearer()


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT refresh token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    """Verify JWT token and return subject"""
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check token type
        if payload.get("type") != token_type:
            return None
            
        subject: str = payload.get("sub")
        if subject is None:
            return None
            
        return subject
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Get current authenticated user"""
    # Import here to avoid circular import
    from app.crud.csv_auth import get_user_by_email_async
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token
        token = credentials.credentials
        
        # Verify token
        email = verify_token(token, "access")
        if email is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from CSV
    user = await get_user_by_email_async(email)
    if user is None:
        raise credentials_exception
        
    # Check if user is active
    if not user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current active user"""
    if not current_user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_roles(allowed_roles: list):
    """Decorator to require specific user roles"""
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker


# Role-based dependencies
async def get_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Require admin role"""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_fm_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Require FM or Admin role"""
    if current_user.role not in ["ADMIN", "FM"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Facility Manager or Admin access required"
        )
    return current_user


async def get_contractor_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Require contractor role"""
    if current_user.role != "CONTRACTOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Contractor access required"
        )
    return current_user


async def get_customer_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Require customer role"""
    if current_user.role != "CUSTOMER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer access required"
        )
    return current_user


async def get_investor_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Require investor role"""
    if current_user.role != "INVESTOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Investor access required"
        )
    return current_user