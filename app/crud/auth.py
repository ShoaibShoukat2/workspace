"""
Authentication CRUD Operations
Database operations for user management
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, timedelta

from app.models.auth import User, VerificationToken, RefreshTokenSession, LoginHistory
from app.core.password import get_password_hash, verify_password
from app.schemas.auth import UserRegister, UserUpdate


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email"""
    result = await db.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: UserRegister) -> User:
    """Create new user"""
    # Generate username from email if not provided
    username = user_data.username or user_data.email.split('@')[0]
    
    # Ensure username is unique
    counter = 1
    original_username = username
    while await get_user_by_username(db, username):
        username = f"{original_username}{counter}"
        counter += 1
    
    # Create user
    db_user = User(
        username=username,
        email=user_data.email.lower(),
        password_hash=get_password_hash(user_data.password),
        first_name=user_data.first_name or "",
        last_name=user_data.last_name or "",
        phone_number=user_data.phone_number,
        role=user_data.role.value,
        is_active=True,
        is_verified=False
    )
    
    db.add(db_user)
    await db.flush()  # Get the ID
    
    # Create email verification token
    verification_token = VerificationToken.generate_token(
        user_id=db_user.id,
        token_type="EMAIL_VERIFICATION",
        expiry_hours=48
    )
    db.add(verification_token)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user


async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[User]:
    """Update user information"""
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_password(db: AsyncSession, user_id: int, new_password: str) -> bool:
    """Update user password"""
    result = await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(
            password_hash=get_password_hash(new_password),
            updated_at=datetime.utcnow()
        )
    )
    await db.commit()
    return result.rowcount > 0


async def update_last_login(db: AsyncSession, user_id: int, ip_address: str = None) -> None:
    """Update user's last login timestamp and IP"""
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(
            last_login=datetime.utcnow(),
            last_login_ip=ip_address
        )
    )
    await db.commit()


async def increment_failed_login(db: AsyncSession, user_id: int) -> None:
    """Increment failed login attempts"""
    user = await get_user_by_id(db, user_id)
    if user:
        user.increment_failed_login()
        await db.commit()


async def reset_failed_login(db: AsyncSession, user_id: int) -> None:
    """Reset failed login attempts"""
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(failed_login_attempts=0)
    )
    await db.commit()


async def lock_user_account(db: AsyncSession, user_id: int, duration_minutes: int = 30) -> None:
    """Lock user account"""
    lock_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(account_locked_until=lock_until)
    )
    await db.commit()


async def unlock_user_account(db: AsyncSession, user_id: int) -> None:
    """Unlock user account"""
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(
            account_locked_until=None,
            failed_login_attempts=0
        )
    )
    await db.commit()


# Verification Token Operations
async def create_verification_token(
    db: AsyncSession, 
    user_id: int, 
    token_type: str, 
    expiry_hours: int = 24
) -> VerificationToken:
    """Create verification token"""
    token = VerificationToken.generate_token(user_id, token_type, expiry_hours)
    db.add(token)
    await db.commit()
    await db.refresh(token)
    return token


async def get_verification_token(db: AsyncSession, token: str) -> Optional[VerificationToken]:
    """Get verification token"""
    result = await db.execute(
        select(VerificationToken)
        .options(selectinload(VerificationToken.user))
        .where(VerificationToken.token == token)
    )
    return result.scalar_one_or_none()


async def use_verification_token(db: AsyncSession, token: str, ip_address: str = None) -> bool:
    """Mark verification token as used"""
    db_token = await get_verification_token(db, token)
    if not db_token or not db_token.is_valid:
        return False
    
    db_token.mark_as_used(ip_address)
    await db.commit()
    return True


async def invalidate_user_tokens(db: AsyncSession, user_id: int, token_type: str = None) -> None:
    """Invalidate all tokens for a user"""
    query = update(VerificationToken).where(
        and_(
            VerificationToken.user_id == user_id,
            VerificationToken.is_used == False
        )
    )
    
    if token_type:
        query = query.where(VerificationToken.token_type == token_type)
    
    await db.execute(query.values(is_used=True, used_at=datetime.utcnow()))
    await db.commit()


# Refresh Token Session Operations
async def create_refresh_session(
    db: AsyncSession,
    user_id: int,
    refresh_token: str,
    device_info: str = None,
    ip_address: str = None,
    expires_at: datetime = None
) -> RefreshTokenSession:
    """Create refresh token session"""
    if not expires_at:
        expires_at = datetime.utcnow() + timedelta(days=7)
    
    session = RefreshTokenSession(
        user_id=user_id,
        refresh_token=refresh_token,
        device_info=device_info,
        ip_address=ip_address,
        expires_at=expires_at
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_refresh_session(db: AsyncSession, refresh_token: str) -> Optional[RefreshTokenSession]:
    """Get refresh token session"""
    result = await db.execute(
        select(RefreshTokenSession)
        .options(selectinload(RefreshTokenSession.user))
        .where(
            and_(
                RefreshTokenSession.refresh_token == refresh_token,
                RefreshTokenSession.is_active == True
            )
        )
    )
    return result.scalar_one_or_none()


async def revoke_refresh_session(db: AsyncSession, refresh_token: str) -> bool:
    """Revoke refresh token session"""
    result = await db.execute(
        update(RefreshTokenSession)
        .where(RefreshTokenSession.refresh_token == refresh_token)
        .values(is_active=False)
    )
    await db.commit()
    return result.rowcount > 0


async def revoke_user_sessions(db: AsyncSession, user_id: int, except_token: str = None) -> None:
    """Revoke all user sessions except specified token"""
    query = update(RefreshTokenSession).where(
        and_(
            RefreshTokenSession.user_id == user_id,
            RefreshTokenSession.is_active == True
        )
    )
    
    if except_token:
        query = query.where(RefreshTokenSession.refresh_token != except_token)
    
    await db.execute(query.values(is_active=False))
    await db.commit()


async def get_user_active_sessions(db: AsyncSession, user_id: int) -> List[RefreshTokenSession]:
    """Get user's active sessions"""
    result = await db.execute(
        select(RefreshTokenSession)
        .where(
            and_(
                RefreshTokenSession.user_id == user_id,
                RefreshTokenSession.is_active == True
            )
        )
        .order_by(RefreshTokenSession.last_used_at.desc())
    )
    return result.scalars().all()


# Login History Operations
async def create_login_history(
    db: AsyncSession,
    user_id: int,
    ip_address: str,
    user_agent: str = None,
    login_method: str = "password",
    success: bool = True,
    failure_reason: str = None
) -> LoginHistory:
    """Create login history record"""
    history = LoginHistory(
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        login_method=login_method,
        success=success,
        failure_reason=failure_reason
    )
    
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history


async def get_user_login_history(
    db: AsyncSession, 
    user_id: int, 
    limit: int = 50
) -> List[LoginHistory]:
    """Get user's login history"""
    result = await db.execute(
        select(LoginHistory)
        .where(LoginHistory.user_id == user_id)
        .order_by(LoginHistory.timestamp.desc())
        .limit(limit)
    )
    return result.scalars().all()


# User Management (Admin)
async def get_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    role: str = None,
    search: str = None,
    is_active: bool = None
) -> tuple[List[User], int]:
    """Get users with filtering and pagination"""
    query = select(User)
    count_query = select(User.id)
    
    # Apply filters
    filters = []
    if role:
        filters.append(User.role == role)
    if is_active is not None:
        filters.append(User.is_active == is_active)
    if search:
        search_filter = or_(
            User.email.ilike(f"%{search}%"),
            User.username.ilike(f"%{search}%"),
            User.first_name.ilike(f"%{search}%"),
            User.last_name.ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))
    
    # Get total count
    total_result = await db.execute(count_query)
    total = len(total_result.scalars().all())
    
    # Get paginated results
    result = await db.execute(
        query.order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()
    
    return users, total


async def get_user_stats(db: AsyncSession) -> dict:
    """Get user statistics"""
    # Total users
    total_result = await db.execute(select(User.id))
    total_users = len(total_result.scalars().all())
    
    # Verified users
    verified_result = await db.execute(select(User.id).where(User.is_verified == True))
    verified_users = len(verified_result.scalars().all())
    
    # Active users
    active_result = await db.execute(select(User.id).where(User.is_active == True))
    active_users = len(active_result.scalars().all())
    
    # Role distribution
    role_result = await db.execute(select(User.role))
    roles = role_result.scalars().all()
    role_distribution = {}
    for role in ["ADMIN", "FM", "CONTRACTOR", "CUSTOMER", "INVESTOR"]:
        role_distribution[role] = roles.count(role)
    
    return {
        "total_users": total_users,
        "verified_users": verified_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "role_distribution": role_distribution
    }


async def deactivate_user(db: AsyncSession, user_id: int) -> bool:
    """Deactivate user (soft delete)"""
    result = await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(is_active=False, updated_at=datetime.utcnow())
    )
    await db.commit()
    return result.rowcount > 0


async def verify_user_email(db: AsyncSession, user_id: int) -> bool:
    """Mark user email as verified"""
    result = await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(is_verified=True, updated_at=datetime.utcnow())
    )
    await db.commit()
    return result.rowcount > 0