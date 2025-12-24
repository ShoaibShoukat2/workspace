"""
Email utility functions
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.config import settings


class EmailService:
    """Email service for sending various types of emails"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.use_tls = settings.SMTP_USE_TLS
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.backend = settings.EMAIL_BACKEND
        
    def _send_email_sync(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: Optional[str] = None
    ) -> bool:
        """Send email synchronously"""
        try:
            if self.backend == "console":
                # Console backend for development
                print(f"\n{'='*50}")
                print(f"EMAIL TO: {to_email}")
                print(f"SUBJECT: {subject}")
                print(f"{'='*50}")
                print(html_content)
                print(f"{'='*50}\n")
                return True
            
            # SMTP backend for production
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: Optional[str] = None
    ) -> bool:
        """Send email asynchronously"""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(
                executor, 
                self._send_email_sync, 
                to_email, 
                subject, 
                html_content, 
                text_content
            )


# Global email service instance
email_service = EmailService()


async def send_verification_email(email: str, token: str) -> bool:
    """Send email verification email"""
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    subject = "Verify Your Email Address"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Email Verification</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .button {{ 
                display: inline-block; 
                padding: 12px 24px; 
                background-color: #007bff; 
                color: white; 
                text-decoration: none; 
                border-radius: 4px; 
                margin: 20px 0;
            }}
            .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to Apex Workspace</h1>
            </div>
            <div class="content">
                <h2>Verify Your Email Address</h2>
                <p>Thank you for registering with Apex Workspace Management. To complete your registration, please verify your email address by clicking the button below:</p>
                
                <a href="{verification_url}" class="button">Verify Email Address</a>
                
                <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                <p><a href="{verification_url}">{verification_url}</a></p>
                
                <p>This verification link will expire in 48 hours.</p>
                
                <p>If you didn't create an account with us, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 Apex Workspace Management. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Welcome to Apex Workspace Management!
    
    Please verify your email address by visiting this link:
    {verification_url}
    
    This verification link will expire in 48 hours.
    
    If you didn't create an account with us, please ignore this email.
    """
    
    return await email_service.send_email(email, subject, html_content, text_content)


async def send_magic_link_email(email: str, token: str) -> bool:
    """Send magic link email for passwordless login"""
    magic_link_url = f"{settings.FRONTEND_URL}/magic-link?token={token}"
    
    subject = "Your Magic Link for Apex Workspace"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Magic Link Login</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .button {{ 
                display: inline-block; 
                padding: 12px 24px; 
                background-color: #28a745; 
                color: white; 
                text-decoration: none; 
                border-radius: 4px; 
                margin: 20px 0;
            }}
            .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Magic Link Login</h1>
            </div>
            <div class="content">
                <h2>Click to Login</h2>
                <p>You requested a magic link to login to your Apex Workspace account. Click the button below to login instantly:</p>
                
                <a href="{magic_link_url}" class="button">Login to Apex Workspace</a>
                
                <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                <p><a href="{magic_link_url}">{magic_link_url}</a></p>
                
                <p>This magic link will expire in 1 hour for security reasons.</p>
                
                <p>If you didn't request this login link, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 Apex Workspace Management. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Magic Link Login for Apex Workspace
    
    Click this link to login to your account:
    {magic_link_url}
    
    This magic link will expire in 1 hour.
    
    If you didn't request this login link, please ignore this email.
    """
    
    return await email_service.send_email(email, subject, html_content, text_content)


async def send_password_reset_email(email: str, token: str) -> bool:
    """Send password reset email"""
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    subject = "Reset Your Password"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Password Reset</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .button {{ 
                display: inline-block; 
                padding: 12px 24px; 
                background-color: #dc3545; 
                color: white; 
                text-decoration: none; 
                border-radius: 4px; 
                margin: 20px 0;
            }}
            .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Reset</h1>
            </div>
            <div class="content">
                <h2>Reset Your Password</h2>
                <p>You requested a password reset for your Apex Workspace account. Click the button below to create a new password:</p>
                
                <a href="{reset_url}" class="button">Reset Password</a>
                
                <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                <p><a href="{reset_url}">{reset_url}</a></p>
                
                <p>This password reset link will expire in 2 hours for security reasons.</p>
                
                <p>If you didn't request a password reset, please ignore this email. Your password will remain unchanged.</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 Apex Workspace Management. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Password Reset for Apex Workspace
    
    Click this link to reset your password:
    {reset_url}
    
    This password reset link will expire in 2 hours.
    
    If you didn't request a password reset, please ignore this email.
    """
    
    return await email_service.send_email(email, subject, html_content, text_content)


async def send_welcome_email(email: str, name: str) -> bool:
    """Send welcome email to new users"""
    subject = "Welcome to Apex Workspace Management"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Welcome</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to Apex Workspace</h1>
            </div>
            <div class="content">
                <h2>Hello {name}!</h2>
                <p>Welcome to Apex Workspace Management - your complete solution for managing jobs, contractors, and customer relationships.</p>
                
                <h3>What you can do:</h3>
                <ul>
                    <li>Manage jobs and track progress</li>
                    <li>Coordinate with contractors</li>
                    <li>Handle estimates and invoicing</li>
                    <li>Track compliance and documentation</li>
                    <li>Generate reports and analytics</li>
                </ul>
                
                <p>If you have any questions, our support team is here to help.</p>
                
                <p>Thank you for choosing Apex Workspace Management!</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 Apex Workspace Management. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Welcome to Apex Workspace Management!
    
    Hello {name}!
    
    Welcome to Apex Workspace Management - your complete solution for managing jobs, contractors, and customer relationships.
    
    What you can do:
    - Manage jobs and track progress
    - Coordinate with contractors
    - Handle estimates and invoicing
    - Track compliance and documentation
    - Generate reports and analytics
    
    If you have any questions, our support team is here to help.
    
    Thank you for choosing Apex Workspace Management!
    """
    
    return await email_service.send_email(email, subject, html_content, text_content)