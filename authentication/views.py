from rest_framework import generics, status, filters, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

from .models import VerificationToken, RefreshTokenSession, LoginHistory
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    MagicLinkRequestSerializer, MagicLinkVerifySerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    ChangePasswordSerializer, EmailVerificationSerializer,
    UpdateProfileSerializer, RefreshTokenSessionSerializer,
    LoginHistorySerializer
)
from .permissions import IsAdmin, IsAdminOrFM, IsOwnerOrAdmin
from .utils import get_client_ip, get_user_agent, send_verification_email, send_magic_link_email, send_password_reset_email

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint
    POST /api/auth/register/
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            # Log the validation errors for debugging
            print(f"Registration validation errors: {e.detail}")
            return Response(
                {'error': 'Validation failed', 'details': e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = serializer.save()
        
        # Send verification email
        token = VerificationToken.objects.filter(
            user=user,
            token_type=VerificationToken.TokenType.EMAIL_VERIFICATION,
            is_used=False
        ).first()
        
        if token:
            send_verification_email(user, token.token)
        
        return Response({
            'message': 'Registration successful. Please check your email to verify your account.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    Email/Password login endpoint
    POST /api/auth/login/
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self._log_failed_login(email, 'User not found')
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if account is locked
        if user.is_account_locked:
            self._log_failed_login(email, 'Account locked', user)
            return Response(
                {'error': 'Account is temporarily locked due to multiple failed login attempts. Please try again later.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Authenticate user
        user_auth = authenticate(username=email, password=password)
        
        if user_auth is None:
            user.increment_failed_login()
            self._log_failed_login(email, 'Invalid password', user)
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if user is active
        if not user.is_active:
            self._log_failed_login(email, 'Account inactive', user)
            return Response(
                {'error': 'Account is inactive. Please contact support.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Reset failed login attempts
        user.reset_failed_login()
        
        # Update last login IP
        user.last_login_ip = get_client_ip(request)
        user.save(update_fields=['last_login_ip'])
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Create token session
        RefreshTokenSession.objects.create(
            user=user,
            refresh_token=str(refresh),
            device_info=get_user_agent(request),
            ip_address=get_client_ip(request),
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        # Log successful login
        LoginHistory.objects.create(
            user=user,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            login_method='password',
            success=True
        )
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })
    
    def _log_failed_login(self, email, reason, user=None):
        """Log failed login attempt"""
        if user:
            LoginHistory.objects.create(
                user=user,
                ip_address=get_client_ip(self.request),
                user_agent=get_user_agent(self.request),
                login_method='password',
                success=False,
                failure_reason=reason
            )


class MagicLinkRequestView(APIView):
    """
    Request magic link for passwordless login
    POST /api/auth/magic-link/request/
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = MagicLinkRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Check if account is locked
        if user.is_account_locked:
            return Response(
                {'error': 'Account is temporarily locked. Please try again later.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate magic link token
        token = VerificationToken.generate_token(
            user=user,
            token_type=VerificationToken.TokenType.MAGIC_LINK,
            expiry_hours=1  # Magic links expire in 1 hour
        )
        
        # Send magic link email
        send_magic_link_email(user, token.token)
        
        return Response({
            'message': 'Magic link sent to your email. Please check your inbox.'
        })


class MagicLinkVerifyView(APIView):
    """
    Verify magic link and login
    POST /api/auth/magic-link/verify/
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = MagicLinkVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token_str = serializer.validated_data['token']
        
        try:
            token = VerificationToken.objects.get(
                token=token_str,
                token_type=VerificationToken.TokenType.MAGIC_LINK
            )
        except VerificationToken.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired magic link'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not token.is_valid:
            return Response(
                {'error': 'Invalid or expired magic link'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = token.user
        
        # Check if account is active
        if not user.is_active:
            return Response(
                {'error': 'Account is inactive. Please contact support.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Mark token as used
        token.mark_as_used(ip_address=get_client_ip(request))
        
        # Update last login IP
        user.last_login_ip = get_client_ip(request)
        user.save(update_fields=['last_login_ip'])
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Create token session
        RefreshTokenSession.objects.create(
            user=user,
            refresh_token=str(refresh),
            device_info=get_user_agent(request),
            ip_address=get_client_ip(request),
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        # Log successful login
        LoginHistory.objects.create(
            user=user,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            login_method='magic_link',
            success=True
        )
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })


class VerifyEmailView(APIView):
    """
    Verify email address
    POST /api/auth/verify-email/
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token_str = serializer.validated_data['token']
        
        try:
            token = VerificationToken.objects.get(
                token=token_str,
                token_type=VerificationToken.TokenType.EMAIL_VERIFICATION
            )
        except VerificationToken.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired verification link'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not token.is_valid:
            return Response(
                {'error': 'Invalid or expired verification link'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = token.user
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        
        token.mark_as_used(ip_address=get_client_ip(request))
        
        return Response({
            'message': 'Email verified successfully'
        })


class ResendVerificationEmailView(APIView):
    """
    Resend verification email
    POST /api/auth/resend-verification/
    """
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        user = request.user
        
        if user.is_verified:
            return Response(
                {'message': 'Email is already verified'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Invalidate old tokens
        VerificationToken.objects.filter(
            user=user,
            token_type=VerificationToken.TokenType.EMAIL_VERIFICATION,
            is_used=False
        ).update(is_used=True)
        
        # Generate new token
        token = VerificationToken.generate_token(
            user=user,
            token_type=VerificationToken.TokenType.EMAIL_VERIFICATION,
            expiry_hours=48
        )
        
        # Send verification email
        send_verification_email(user, token.token)
        
        return Response({
            'message': 'Verification email sent successfully'
        })


class PasswordResetRequestView(APIView):
    """
    Request password reset
    POST /api/auth/password-reset/request/
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Generate password reset token
        token = VerificationToken.generate_token(
            user=user,
            token_type=VerificationToken.TokenType.PASSWORD_RESET,
            expiry_hours=2  # Password reset links expire in 2 hours
        )
        
        # Send password reset email
        send_password_reset_email(user, token.token)
        
        return Response({
            'message': 'Password reset link sent to your email'
        })


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset
    POST /api/auth/password-reset/confirm/
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token_str = serializer.validated_data['token']
        new_password = serializer.validated_data['password']
        
        try:
            token = VerificationToken.objects.get(
                token=token_str,
                token_type=VerificationToken.TokenType.PASSWORD_RESET
            )
        except VerificationToken.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired reset link'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not token.is_valid:
            return Response(
                {'error': 'Invalid or expired reset link'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = token.user
        user.set_password(new_password)
        user.unlock_account()  # Unlock account if it was locked
        user.save()
        
        token.mark_as_used(ip_address=get_client_ip(request))
        
        # Revoke all active sessions
        RefreshTokenSession.objects.filter(user=user, is_active=True).update(is_active=False)
        
        return Response({
            'message': 'Password reset successful. Please login with your new password.'
        })


class ChangePasswordView(APIView):
    """
    Change password for authenticated user
    POST /api/auth/change-password/
    """
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        # Verify old password
        if not user.check_password(old_password):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        # Revoke all other sessions except current
        RefreshTokenSession.objects.filter(user=user, is_active=True).update(is_active=False)
        
        return Response({
            'message': 'Password changed successfully'
        })


class LogoutView(APIView):
    """
    Logout user and revoke refresh token
    POST /api/auth/logout/
    """
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                # Revoke the session
                RefreshTokenSession.objects.filter(
                    refresh_token=refresh_token,
                    user=request.user
                ).update(is_active=False)
            
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)


class LogoutAllView(APIView):
    """
    Logout from all devices
    POST /api/auth/logout-all/
    """
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        # Revoke all active sessions
        RefreshTokenSession.objects.filter(
            user=request.user,
            is_active=True
        ).update(is_active=False)
        
        return Response({
            'message': 'Logged out from all devices successfully'
        })


class MeView(APIView):
    """
    Get current user profile
    GET /api/auth/me/
    """
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UpdateProfileView(APIView):
    """
    Update user profile
    PATCH /api/auth/profile/
    """
    permission_classes = (IsAuthenticated,)
    
    def patch(self, request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Profile updated successfully',
            'user': UserSerializer(request.user).data
        })


class ActiveSessionsView(generics.ListAPIView):
    """
    List all active sessions for current user
    GET /api/auth/sessions/
    """
    serializer_class = RefreshTokenSessionSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        return RefreshTokenSession.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-last_used_at')


class RevokeSessionView(APIView):
    """
    Revoke a specific session
    POST /api/auth/sessions/<id>/revoke/
    """
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, session_id):
        try:
            session = RefreshTokenSession.objects.get(
                id=session_id,
                user=request.user
            )
            session.revoke()
            return Response({
                'message': 'Session revoked successfully'
            })
        except RefreshTokenSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class LoginHistoryView(generics.ListAPIView):
    """
    View login history for current user
    GET /api/auth/login-history/
    """
    serializer_class = LoginHistorySerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        return LoginHistory.objects.filter(
            user=self.request.user
        ).order_by('-timestamp')[:50]  # Last 50 login attempts


class UserListView(generics.ListAPIView):
    """
    List all users (Admin only)
    GET /api/auth/users/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdmin)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'username', 'role']
    ordering_fields = ['created_at', 'email', 'role']
    ordering = ['-created_at']


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a user (Admin only)
    GET/PUT/PATCH/DELETE /api/auth/users/<id>/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdminOrFM)
    
    def perform_destroy(self, instance):
        # Soft delete by deactivating user
        instance.is_active = False
        instance.save()


class UserStatsView(APIView):
    """
    Get user statistics (Admin only)
    GET /api/auth/stats/
    """
    permission_classes = (IsAuthenticated, IsAdmin)
    
    def get(self, request):
        total_users = User.objects.count()
        verified_users = User.objects.filter(is_verified=True).count()
        active_users = User.objects.filter(is_active=True).count()
        
        role_distribution = {}
        for role_code, role_name in User.Role.choices:
            role_distribution[role_name] = User.objects.filter(role=role_code).count()
        
        return Response({
            'total_users': total_users,
            'verified_users': verified_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'role_distribution': role_distribution
        })
