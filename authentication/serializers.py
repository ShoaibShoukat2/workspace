from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import VerificationToken, RefreshTokenSession, LoginHistory

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details"""
    
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'role', 'role_display', 
            'is_verified', 'phone_number', 'profile_picture',
            'created_at', 'last_login', 'is_active'
        )
        read_only_fields = ('id', 'created_at', 'last_login', 'is_verified')


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'role', 'phone_number')
        extra_kwargs = {
            'role': {'required': False},
            'phone_number': {'required': False}
        }
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value.lower()
    
    def validate(self, attrs):
        """Validate password match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        """Create user and send verification email"""
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        
        # Generate email verification token
        VerificationToken.generate_token(
            user=user,
            token_type=VerificationToken.TokenType.EMAIL_VERIFICATION,
            expiry_hours=48
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for email/password login"""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate_email(self, value):
        return value.lower()


class MagicLinkRequestSerializer(serializers.Serializer):
    """Serializer for requesting magic link"""
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validate email exists"""
        email = value.lower()
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("No account found with this email.")
        return email


class MagicLinkVerifySerializer(serializers.Serializer):
    """Serializer for verifying magic link token"""
    
    token = serializers.CharField()


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting password reset"""
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validate email exists"""
        email = value.lower()
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("No account found with this email.")
        return email


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming password reset"""
    
    token = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate password match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    
    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password2 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate password match"""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification"""
    
    token = serializers.CharField()


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = ('username', 'phone_number', 'profile_picture')


class RefreshTokenSessionSerializer(serializers.ModelSerializer):
    """Serializer for active sessions"""
    
    class Meta:
        model = RefreshTokenSession
        fields = ('id', 'device_info', 'ip_address', 'created_at', 'last_used_at', 'is_active')
        read_only_fields = fields


class LoginHistorySerializer(serializers.ModelSerializer):
    """Serializer for login history"""
    
    class Meta:
        model = LoginHistory
        fields = ('id', 'ip_address', 'user_agent', 'login_method', 'success', 'failure_reason', 'timestamp')
        read_only_fields = fields
