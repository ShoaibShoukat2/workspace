from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta
import secrets


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email.split('@')[0])
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('role', 'ADMIN')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model with role-based access control"""
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        FM = 'FM', 'Facility Manager'
        CONTRACTOR = 'CONTRACTOR', 'Contractor'
        CUSTOMER = 'CUSTOMER', 'Customer'
        INVESTOR = 'INVESTOR', 'Investor'
    
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    is_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.URLField(blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    @property
    def is_account_locked(self):
        """Check if account is currently locked"""
        if self.account_locked_until and self.account_locked_until > timezone.now():
            return True
        return False
    
    def lock_account(self, duration_minutes=30):
        """Lock account for specified duration"""
        self.account_locked_until = timezone.now() + timedelta(minutes=duration_minutes)
        self.save(update_fields=['account_locked_until'])
    
    def unlock_account(self):
        """Unlock account and reset failed attempts"""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['account_locked_until', 'failed_login_attempts'])
    
    def increment_failed_login(self):
        """Increment failed login attempts and lock if threshold reached"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.lock_account()
        self.save(update_fields=['failed_login_attempts'])
    
    def reset_failed_login(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        self.save(update_fields=['failed_login_attempts'])
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'role']),
            models.Index(fields=['is_verified']),
        ]


class VerificationToken(models.Model):
    """Email verification and password reset tokens"""
    
    class TokenType(models.TextChoices):
        EMAIL_VERIFICATION = 'EMAIL_VERIFICATION', 'Email Verification'
        PASSWORD_RESET = 'PASSWORD_RESET', 'Password Reset'
        MAGIC_LINK = 'MAGIC_LINK', 'Magic Link'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.CharField(max_length=100, unique=True, db_index=True)
    token_type = models.CharField(max_length=20, choices=TokenType.choices)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    @classmethod
    def generate_token(cls, user, token_type, expiry_hours=24):
        """Generate a new verification token"""
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=expiry_hours)
        return cls.objects.create(
            user=user,
            token=token,
            token_type=token_type,
            expires_at=expires_at
        )
    
    @property
    def is_valid(self):
        """Check if token is valid and not expired"""
        return not self.is_used and self.expires_at > timezone.now()
    
    def mark_as_used(self, ip_address=None):
        """Mark token as used"""
        self.is_used = True
        self.used_at = timezone.now()
        if ip_address:
            self.ip_address = ip_address
        self.save(update_fields=['is_used', 'used_at', 'ip_address'])
    
    def __str__(self):
        return f"{self.get_token_type_display()} - {self.user.email}"
    
    class Meta:
        db_table = 'verification_tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token', 'is_used']),
            models.Index(fields=['expires_at']),
        ]


class RefreshTokenSession(models.Model):
    """Track active refresh token sessions for better security"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='token_sessions')
    refresh_token = models.CharField(max_length=500, unique=True)
    device_info = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"{self.user.email} - {self.device_info}"
    
    @property
    def is_expired(self):
        """Check if session is expired"""
        return self.expires_at < timezone.now()
    
    def revoke(self):
        """Revoke this session"""
        self.is_active = False
        self.save(update_fields=['is_active'])
    
    class Meta:
        db_table = 'refresh_token_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['refresh_token']),
        ]


class LoginHistory(models.Model):
    """Track user login history for security auditing"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    login_method = models.CharField(max_length=50)  # password, magic_link, etc.
    success = models.BooleanField(default=True)
    failure_reason = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.user.email} - {status} - {self.timestamp}"
    
    class Meta:
        db_table = 'login_history'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['ip_address']),
        ]
