"""
Utility functions for authentication module
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Extract user agent from request"""
    return request.META.get('HTTP_USER_AGENT', '')[:255]


def send_verification_email(user, token):
    """Send email verification link"""
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    subject = 'Verify Your Email Address'
    html_message = f"""
    <html>
        <body>
            <h2>Welcome {user.username}!</h2>
            <p>Thank you for registering. Please verify your email address by clicking the link below:</p>
            <p><a href="{verification_url}">Verify Email</a></p>
            <p>This link will expire in 48 hours.</p>
            <p>If you didn't create this account, please ignore this email.</p>
        </body>
    </html>
    """
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_magic_link_email(user, token):
    """Send magic link for passwordless login"""
    magic_link_url = f"{settings.FRONTEND_URL}/magic-link?token={token}"
    
    subject = 'Your Magic Login Link'
    html_message = f"""
    <html>
        <body>
            <h2>Hello {user.username}!</h2>
            <p>Click the link below to login to your account:</p>
            <p><a href="{magic_link_url}">Login Now</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this link, please ignore this email.</p>
        </body>
    </html>
    """
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_password_reset_email(user, token):
    """Send password reset link"""
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    subject = 'Reset Your Password'
    html_message = f"""
    <html>
        <body>
            <h2>Hello {user.username}!</h2>
            <p>You requested to reset your password. Click the link below to proceed:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>This link will expire in 2 hours.</p>
            <p>If you didn't request this, please ignore this email and your password will remain unchanged.</p>
        </body>
    </html>
    """
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_account_locked_email(user):
    """Send notification when account is locked"""
    subject = 'Account Security Alert'
    html_message = f"""
    <html>
        <body>
            <h2>Hello {user.username}!</h2>
            <p>Your account has been temporarily locked due to multiple failed login attempts.</p>
            <p>Your account will be automatically unlocked in 30 minutes.</p>
            <p>If this wasn't you, please reset your password immediately.</p>
        </body>
    </html>
    """
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_password_changed_email(user):
    """Send notification when password is changed"""
    subject = 'Password Changed Successfully'
    html_message = f"""
    <html>
        <body>
            <h2>Hello {user.username}!</h2>
            <p>Your password has been changed successfully.</p>
            <p>If you didn't make this change, please contact support immediately.</p>
        </body>
    </html>
    """
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )
