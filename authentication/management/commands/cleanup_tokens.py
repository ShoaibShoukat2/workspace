"""
Management command to cleanup expired tokens and sessions
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from authentication.models import VerificationToken, RefreshTokenSession


class Command(BaseCommand):
    help = 'Cleanup expired verification tokens and refresh token sessions'
    
    def handle(self, *args, **options):
        now = timezone.now()
        
        # Delete expired verification tokens
        expired_tokens = VerificationToken.objects.filter(expires_at__lt=now)
        token_count = expired_tokens.count()
        expired_tokens.delete()
        
        # Delete expired refresh token sessions
        expired_sessions = RefreshTokenSession.objects.filter(expires_at__lt=now)
        session_count = expired_sessions.count()
        expired_sessions.delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully cleaned up {token_count} expired tokens and {session_count} expired sessions'
            )
        )
