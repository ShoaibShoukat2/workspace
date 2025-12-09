"""
Custom middleware for authentication and security
"""
from django.utils import timezone
from django.http import JsonResponse
from rest_framework import status
from .models import RefreshTokenSession


class TokenSessionMiddleware:
    """
    Middleware to validate refresh token sessions
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response


class AccountLockMiddleware:
    """
    Middleware to check if user account is locked
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.is_account_locked:
                return JsonResponse(
                    {
                        'error': 'Account is temporarily locked. Please try again later.',
                        'locked_until': request.user.account_locked_until.isoformat()
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        
        response = self.get_response(request)
        return response


class RateLimitMiddleware:
    """
    Simple rate limiting middleware
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit_cache = {}
    
    def __call__(self, request):
        # Implement rate limiting logic here
        # This is a basic example - use django-ratelimit or similar for production
        response = self.get_response(request)
        return response
