from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView, LogoutAllView,
    MagicLinkRequestView, MagicLinkVerifyView,
    VerifyEmailView, ResendVerificationEmailView,
    PasswordResetRequestView, PasswordResetConfirmView, ChangePasswordView,
    MeView, UpdateProfileView,
    ActiveSessionsView, RevokeSessionView, LoginHistoryView,
    UserListView, UserDetailView, UserStatsView
)

app_name = 'authentication'

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout-all/', LogoutAllView.as_view(), name='logout-all'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Magic Link
    path('magic-link/request/', MagicLinkRequestView.as_view(), name='magic-link-request'),
    path('magic-link/verify/', MagicLinkVerifyView.as_view(), name='magic-link-verify'),
    
    # Email Verification
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationEmailView.as_view(), name='resend-verification'),
    
    # Password Management
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # User Profile
    path('me/', MeView.as_view(), name='me'),
    path('profile/', UpdateProfileView.as_view(), name='update-profile'),
    
    # Session Management
    path('sessions/', ActiveSessionsView.as_view(), name='active-sessions'),
    path('sessions/<int:session_id>/revoke/', RevokeSessionView.as_view(), name='revoke-session'),
    path('login-history/', LoginHistoryView.as_view(), name='login-history'),
    
    # User Management (Admin)
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('stats/', UserStatsView.as_view(), name='user-stats'),
]
