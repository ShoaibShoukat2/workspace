from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, VerificationToken, RefreshTokenSession, LoginHistory


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model"""
    
    list_display = ('email', 'username', 'role', 'is_verified', 'is_active', 'is_staff', 'created_at')
    list_filter = ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('email', 'username', 'phone_number')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'phone_number', 'profile_picture')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Security', {'fields': ('last_login', 'last_login_ip', 'failed_login_attempts', 'account_locked_until')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role', 'is_staff', 'is_superuser'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'last_login_ip', 'failed_login_attempts')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()


@admin.register(VerificationToken)
class VerificationTokenAdmin(admin.ModelAdmin):
    """Admin for VerificationToken model"""
    
    list_display = ('user', 'token_type', 'is_used', 'is_expired', 'created_at', 'expires_at')
    list_filter = ('token_type', 'is_used', 'created_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('token', 'created_at', 'used_at', 'ip_address')
    ordering = ('-created_at',)
    
    def is_expired(self, obj):
        """Display if token is expired"""
        if obj.is_valid:
            return format_html('<span style="color: green;">✓ Valid</span>')
        return format_html('<span style="color: red;">✗ Expired/Used</span>')
    is_expired.short_description = 'Status'


@admin.register(RefreshTokenSession)
class RefreshTokenSessionAdmin(admin.ModelAdmin):
    """Admin for RefreshTokenSession model"""
    
    list_display = ('user', 'device_info', 'ip_address', 'is_active', 'created_at', 'last_used_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__email', 'ip_address', 'device_info')
    readonly_fields = ('refresh_token', 'created_at', 'last_used_at')
    ordering = ('-created_at',)
    
    actions = ['revoke_sessions']
    
    def revoke_sessions(self, request, queryset):
        """Bulk revoke sessions"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} session(s) revoked successfully.')
    revoke_sessions.short_description = 'Revoke selected sessions'


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    """Admin for LoginHistory model"""
    
    list_display = ('user', 'login_method', 'success_status', 'ip_address', 'timestamp')
    list_filter = ('success', 'login_method', 'timestamp')
    search_fields = ('user__email', 'ip_address')
    readonly_fields = ('user', 'ip_address', 'user_agent', 'login_method', 'success', 'failure_reason', 'timestamp')
    ordering = ('-timestamp',)
    
    def success_status(self, obj):
        """Display success status with color"""
        if obj.success:
            return format_html('<span style="color: green;">✓ Success</span>')
        return format_html('<span style="color: red;">✗ Failed: {}</span>', obj.failure_reason)
    success_status.short_description = 'Status'
    
    def has_add_permission(self, request):
        """Disable manual addition"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing"""
        return False
