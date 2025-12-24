"""
Authentication Schemas
Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    FM = "FM"
    CONTRACTOR = "CONTRACTOR"
    CUSTOMER = "CUSTOMER"
    INVESTOR = "INVESTOR"


class TokenType(str, Enum):
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION"
    PASSWORD_RESET = "PASSWORD_RESET"
    MAGIC_LINK = "MAGIC_LINK"


# Base User Schema
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=150)
    last_name: Optional[str] = Field(None, max_length=150)
    phone_number: Optional[str] = Field(None, max_length=20)
    role: UserRole = UserRole.CUSTOMER


# User Registration
class UserRegister(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    password2: str = Field(..., min_length=8, max_length=128)
    
    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


# User Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


# User Response
class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# User Update
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=150)
    first_name: Optional[str] = Field(None, max_length=150)
    last_name: Optional[str] = Field(None, max_length=150)
    phone_number: Optional[str] = Field(None, max_length=20)
    profile_picture: Optional[str] = None


# Token Response
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


# Token Refresh
class TokenRefresh(BaseModel):
    refresh_token: str


# Magic Link Request
class MagicLinkRequest(BaseModel):
    email: EmailStr


# Magic Link Verify
class MagicLinkVerify(BaseModel):
    token: str


# Password Reset Request
class PasswordResetRequest(BaseModel):
    email: EmailStr


# Password Reset Confirm
class PasswordResetConfirm(BaseModel):
    token: str
    password: str = Field(..., min_length=8, max_length=128)
    password2: str = Field(..., min_length=8, max_length=128)
    
    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


# Change Password
class ChangePassword(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    new_password2: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


# Email Verification
class EmailVerification(BaseModel):
    token: str


# Verification Token Response
class VerificationTokenResponse(BaseModel):
    id: int
    token_type: TokenType
    expires_at: datetime
    is_used: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Refresh Token Session Response
class RefreshTokenSessionResponse(BaseModel):
    id: int
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_used_at: datetime
    
    class Config:
        from_attributes = True


# Login History Response
class LoginHistoryResponse(BaseModel):
    id: int
    ip_address: str
    user_agent: Optional[str] = None
    login_method: str
    success: bool
    failure_reason: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


# User List Response (Admin)
class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int


# User Statistics (Admin)
class UserStatsResponse(BaseModel):
    total_users: int
    verified_users: int
    active_users: int
    inactive_users: int
    role_distribution: dict


# Logout Request
class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None


# Session Revoke
class SessionRevoke(BaseModel):
    session_id: int


# Response Messages
class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    error: str
    details: Optional[dict] = None