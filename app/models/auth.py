"""
Authentication Models
Converted from Django authentication models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import uuid
import secrets

from app.core.database import Base


class User(Base):
    """User model with role-based access control"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, index=True)
    email = Column(String(254), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    
    # Profile fields
    first_name = Column(String(150), default="")
    last_name = Column(String(150), default="")
    phone_number = Column(String(20), nullable=True)
    profile_picture = Column(Text, nullable=True)  # URL
    
    # Role and permissions
    role = Column(String(20), default="CUSTOMER", index=True)  # ADMIN, FM, CONTRACTOR, CUSTOMER, INVESTOR
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # Security fields
    last_login_ip = Column(INET, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    verification_tokens = relationship("VerificationToken", back_populates="user", cascade="all, delete-orphan")
    token_sessions = relationship("RefreshTokenSession", back_populates="user", cascade="all, delete-orphan")
    login_history = relationship("LoginHistory", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_email_role', 'email', 'role'),
        Index('idx_user_is_verified', 'is_verified'),
    )
    
    @property
    def is_account_locked(self) -> bool:
        """Check if account is currently locked"""
        if self.account_locked_until and self.account_locked_until > datetime.utcnow():
            return True
        return False
    
    def lock_account(self, duration_minutes: int = 30):
        """Lock account for specified duration"""
        self.account_locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
    
    def unlock_account(self):
        """Unlock account and reset failed attempts"""
        self.account_locked_until = None
        self.failed_login_attempts = 0
    
    def increment_failed_login(self):
        """Increment failed login attempts and lock if threshold reached"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.lock_account()
    
    def reset_failed_login(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username


class VerificationToken(Base):
    """Email verification and password reset tokens"""
    __tablename__ = "verification_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(100), unique=True, index=True, nullable=False)
    token_type = Column(String(20), nullable=False)  # EMAIL_VERIFICATION, PASSWORD_RESET, MAGIC_LINK
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    used_at = Column(DateTime, nullable=True)
    ip_address = Column(INET, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="verification_tokens")
    
    # Indexes
    __table_args__ = (
        Index('idx_token_is_used', 'token', 'is_used'),
        Index('idx_expires_at', 'expires_at'),
    )
    
    @classmethod
    def generate_token(cls, user_id: int, token_type: str, expiry_hours: int = 24):
        """Generate a new verification token"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
        return cls(
            user_id=user_id,
            token=token,
            token_type=token_type,
            expires_at=expires_at
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if token is valid and not expired"""
        return not self.is_used and self.expires_at > datetime.utcnow()
    
    def mark_as_used(self, ip_address: str = None):
        """Mark token as used"""
        self.is_used = True
        self.used_at = datetime.utcnow()
        if ip_address:
            self.ip_address = ip_address


class RefreshTokenSession(Base):
    """Track active refresh token sessions for better security"""
    __tablename__ = "refresh_token_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    refresh_token = Column(String(500), unique=True, nullable=False)
    device_info = Column(String(255), nullable=True)
    ip_address = Column(INET, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    last_used_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="token_sessions")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_is_active', 'user_id', 'is_active'),
        Index('idx_refresh_token', 'refresh_token'),
    )
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return self.expires_at < datetime.utcnow()
    
    def revoke(self):
        """Revoke this session"""
        self.is_active = False


class LoginHistory(Base):
    """Track user login history for security auditing"""
    __tablename__ = "login_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ip_address = Column(INET, nullable=False)
    user_agent = Column(Text, nullable=True)
    login_method = Column(String(50), nullable=False)  # password, magic_link, etc.
    success = Column(Boolean, default=True)
    failure_reason = Column(String(255), nullable=True)
    timestamp = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="login_history")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_ip_address', 'ip_address'),
    )