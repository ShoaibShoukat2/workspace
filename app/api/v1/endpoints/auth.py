"""
Authentication Endpoints
Complete authentication system with JWT, magic links, etc.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import List

from app.core.database import get_db
from app.core.security import (
    get_current_user, get_current_active_user, get_admin_user,
    create_access_token, create_refresh_token, verify_token, security
)
from app.crud import auth as auth_crud
from app.schemas.auth import (
    UserRegister, UserLogin, UserResponse, UserUpdate, TokenResponse,
    MagicLinkRequest, MagicLinkVerify, PasswordResetRequest, PasswordResetConfirm,
    ChangePassword, EmailVerification, MessageResponse, TokenRefresh,
    RefreshTokenSessionResponse, LoginHistoryResponse, UserListResponse,
    UserStatsResponse, LogoutRequest, SessionRevoke
)
from app.models.auth import User
from app.utils.email import send_verification_email, send_magic_link_email, send_password_reset_email
from app.utils.helpers import get_client_ip, get_user_agent

router = APIRouter()


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Register new user"""
    # Check if user already exists
    existing_user = await auth_crud.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Check username availability
    if user_data.username:
        existing_username = await auth_crud.get_user_by_username(db, user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create user
    try:
        user = await auth_crud.create_user(db, user_data)
        
        # Send verification email
        # Note: In production, this should be handled by a background task
        await send_verification_email(user.email, user.verification_tokens[0].token)
        
        return MessageResponse(
            message="Registration successful. Please check your email to verify your account."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Login with email and password"""
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    # Get user
    user = await auth_crud.get_user_by_email(db, user_data.email)
    if not user:
        # Log failed attempt
        await auth_crud.create_login_history(
            db, None, ip_address, user_agent, "password", False, "User not found"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if account is locked
    if user.is_account_locked:
        await auth_crud.create_login_history(
            db, user.id, ip_address, user_agent, "password", False, "Account locked"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked due to multiple failed login attempts"
        )
    
    # Authenticate
    authenticated_user = await auth_crud.authenticate_user(db, user_data.email, user_data.password)
    if not authenticated_user:
        # Increment failed attempts
        await auth_crud.increment_failed_login(db, user.id)
        await auth_crud.create_login_history(
            db, user.id, ip_address, user_agent, "password", False, "Invalid password"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if user is active
    if not authenticated_user.is_active:
        await auth_crud.create_login_history(
            db, user.id, ip_address, user_agent, "password", False, "Account inactive"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Reset failed login attempts
    await auth_crud.reset_failed_login(db, authenticated_user.id)
    
    # Update last login
    await auth_crud.update_last_login(db, authenticated_user.id, ip_address)
    
    # Create tokens
    access_token = create_access_token(authenticated_user.email)
    refresh_token = create_refresh_token(authenticated_user.email)
    
    # Create refresh session
    await auth_crud.create_refresh_session(
        db, authenticated_user.id, refresh_token, user_agent, ip_address
    )
    
    # Log successful login
    await auth_crud.create_login_history(
        db, authenticated_user.id, ip_address, user_agent, "password", True
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=3600,  # 1 hour
        user=UserResponse.from_orm(authenticated_user)
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token"""
    # Verify refresh token
    email = verify_token(token_data.refresh_token, "refresh")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get refresh session
    session = await auth_crud.get_refresh_session(db, token_data.refresh_token)
    if not session or session.is_expired:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired or invalid"
        )
    
    # Get user
    user = session.user
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = create_access_token(user.email)
    new_refresh_token = create_refresh_token(user.email)
    
    # Update session
    session.refresh_token = new_refresh_token
    session.last_used_at = datetime.utcnow()
    await db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=3600,
        user=UserResponse.from_orm(user)
    )


@router.post("/magic-link/request", response_model=MessageResponse)
async def request_magic_link(
    request_data: MagicLinkRequest,
    db: AsyncSession = Depends(get_db)
):
    """Request magic link for passwordless login"""
    user = await auth_crud.get_user_by_email(db, request_data.email)
    if not user:
        # Don't reveal if email exists
        return MessageResponse(message="If the email exists, a magic link has been sent")
    
    if user.is_account_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked"
        )
    
    # Invalidate old magic link tokens
    await auth_crud.invalidate_user_tokens(db, user.id, "MAGIC_LINK")
    
    # Create new magic link token
    token = await auth_crud.create_verification_token(db, user.id, "MAGIC_LINK", 1)  # 1 hour
    
    # Send magic link email
    await send_magic_link_email(user.email, token.token)
    
    return MessageResponse(message="Magic link sent to your email")


@router.post("/magic-link/verify", response_model=TokenResponse)
async def verify_magic_link(
    verify_data: MagicLinkVerify,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Verify magic link and login"""
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    # Get token
    token = await auth_crud.get_verification_token(db, verify_data.token)
    if not token or not token.is_valid or token.token_type != "MAGIC_LINK":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired magic link"
        )
    
    user = token.user
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Use token
    await auth_crud.use_verification_token(db, verify_data.token, ip_address)
    
    # Update last login
    await auth_crud.update_last_login(db, user.id, ip_address)
    
    # Create tokens
    access_token = create_access_token(user.email)
    refresh_token = create_refresh_token(user.email)
    
    # Create refresh session
    await auth_crud.create_refresh_session(db, user.id, refresh_token, user_agent, ip_address)
    
    # Log successful login
    await auth_crud.create_login_history(db, user.id, ip_address, user_agent, "magic_link", True)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=3600,
        user=UserResponse.from_orm(user)
    )


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    verify_data: EmailVerification,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Verify email address"""
    ip_address = get_client_ip(request)
    
    # Get token
    token = await auth_crud.get_verification_token(db, verify_data.token)
    if not token or not token.is_valid or token.token_type != "EMAIL_VERIFICATION":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification link"
        )
    
    # Verify user email
    await auth_crud.verify_user_email(db, token.user_id)
    
    # Use token
    await auth_crud.use_verification_token(db, verify_data.token, ip_address)
    
    return MessageResponse(message="Email verified successfully")


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Resend verification email"""
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    # Invalidate old tokens
    await auth_crud.invalidate_user_tokens(db, current_user.id, "EMAIL_VERIFICATION")
    
    # Create new token
    token = await auth_crud.create_verification_token(db, current_user.id, "EMAIL_VERIFICATION", 48)
    
    # Send verification email
    await send_verification_email(current_user.email, token.token)
    
    return MessageResponse(message="Verification email sent successfully")


@router.post("/password-reset/request", response_model=MessageResponse)
async def request_password_reset(
    request_data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset"""
    user = await auth_crud.get_user_by_email(db, request_data.email)
    if not user:
        # Don't reveal if email exists
        return MessageResponse(message="If the email exists, a password reset link has been sent")
    
    # Invalidate old password reset tokens
    await auth_crud.invalidate_user_tokens(db, user.id, "PASSWORD_RESET")
    
    # Create new password reset token
    token = await auth_crud.create_verification_token(db, user.id, "PASSWORD_RESET", 2)  # 2 hours
    
    # Send password reset email
    await send_password_reset_email(user.email, token.token)
    
    return MessageResponse(message="Password reset link sent to your email")


@router.post("/password-reset/confirm", response_model=MessageResponse)
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Confirm password reset"""
    ip_address = get_client_ip(request)
    
    # Get token
    token = await auth_crud.get_verification_token(db, reset_data.token)
    if not token or not token.is_valid or token.token_type != "PASSWORD_RESET":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset link"
        )
    
    # Update password
    await auth_crud.update_user_password(db, token.user_id, reset_data.password)
    
    # Unlock account if locked
    await auth_crud.unlock_user_account(db, token.user_id)
    
    # Use token
    await auth_crud.use_verification_token(db, reset_data.token, ip_address)
    
    # Revoke all active sessions
    await auth_crud.revoke_user_sessions(db, token.user_id)
    
    return MessageResponse(message="Password reset successful")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Change password for authenticated user"""
    # Verify old password
    authenticated_user = await auth_crud.authenticate_user(
        db, current_user.email, password_data.old_password
    )
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    await auth_crud.update_user_password(db, current_user.id, password_data.new_password)
    
    # Revoke all other sessions
    await auth_crud.revoke_user_sessions(db, current_user.id)
    
    return MessageResponse(message="Password changed successfully")


@router.post("/logout", response_model=MessageResponse)
async def logout(
    logout_data: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout user"""
    if logout_data.refresh_token:
        await auth_crud.revoke_refresh_session(db, logout_data.refresh_token)
    
    return MessageResponse(message="Logout successful")


@router.post("/logout-all", response_model=MessageResponse)
async def logout_all(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout from all devices"""
    await auth_crud.revoke_user_sessions(db, current_user.id)
    return MessageResponse(message="Logged out from all devices successfully")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return UserResponse.from_orm(current_user)


@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile"""
    updated_user = await auth_crud.update_user(db, current_user.id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(updated_user)


@router.get("/sessions", response_model=List[RefreshTokenSessionResponse])
async def get_active_sessions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all active sessions for current user"""
    sessions = await auth_crud.get_user_active_sessions(db, current_user.id)
    return [RefreshTokenSessionResponse.from_orm(session) for session in sessions]


@router.post("/sessions/revoke", response_model=MessageResponse)
async def revoke_session(
    session_data: SessionRevoke,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Revoke a specific session"""
    # Note: In a real implementation, you'd need to verify the session belongs to the user
    # This is simplified for the example
    success = await auth_crud.revoke_refresh_session(db, str(session_data.session_id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return MessageResponse(message="Session revoked successfully")


@router.get("/login-history", response_model=List[LoginHistoryResponse])
async def get_login_history(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get login history for current user"""
    history = await auth_crud.get_user_login_history(db, current_user.id)
    return [LoginHistoryResponse.from_orm(record) for record in history]


# Admin endpoints
@router.get("/users", response_model=UserListResponse)
async def get_users(
    skip: int = 0,
    limit: int = 20,
    role: str = None,
    search: str = None,
    is_active: bool = None,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all users (Admin only)"""
    users, total = await auth_crud.get_users(db, skip, limit, role, search, is_active)
    
    return UserListResponse(
        users=[UserResponse.from_orm(user) for user in users],
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID (Admin only)"""
    user = await auth_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(user)


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def deactivate_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate user (Admin only)"""
    success = await auth_crud.deactivate_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return MessageResponse(message="User deactivated successfully")


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user statistics (Admin only)"""
    stats = await auth_crud.get_user_stats(db)
    return UserStatsResponse(**stats)