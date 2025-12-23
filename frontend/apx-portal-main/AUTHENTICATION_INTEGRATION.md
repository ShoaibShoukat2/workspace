# Authentication Integration Guide

This document explains the complete authentication integration between the frontend and backend APIs.

## Overview

The authentication system includes:
- User registration with email verification
- Login with JWT tokens
- Password reset functionality
- Automatic token refresh
- Role-based access control
- Session management

## Backend APIs Integrated

### Authentication Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/token/refresh/` - Refresh access token

### Password Management
- `POST /api/auth/password-reset/request/` - Request password reset
- `POST /api/auth/password-reset/confirm/` - Confirm password reset
- `POST /api/auth/change-password/` - Change password (authenticated)

### Email Verification
- `POST /api/auth/verify-email/` - Verify email address
- `POST /api/auth/resend-verification/` - Resend verification email

### User Profile
- `GET /api/auth/me/` - Get current user profile
- `PATCH /api/auth/profile/` - Update user profile

## Frontend Components

### Pages
1. **Login.tsx** - Login form with demo and API modes
2. **Register.tsx** - Registration form with email verification
3. **ForgotPassword.tsx** - Password reset request form
4. **ResetPassword.tsx** - Password reset confirmation form

### Services
1. **api.ts** - API service with automatic token refresh
2. **auth.ts** - Authentication utilities and token management
3. **useApi.ts** - React hooks for API operations

### Context
1. **AuthContext.tsx** - Global authentication state management

## Features

### 1. Dual Mode Authentication
The login page supports both:
- **Demo Mode**: Uses mock data for testing
- **API Mode**: Connects to real backend APIs

Toggle between modes using the checkbox on the login page.

### 2. Automatic Token Refresh
- Tokens are automatically refreshed before expiration
- Failed refresh redirects to login page
- Refresh timer runs every 4 minutes

### 3. Error Handling
- Comprehensive error messages
- Network error handling
- Token expiration handling
- Form validation

### 4. Security Features
- JWT token storage in localStorage
- Automatic token cleanup on logout
- Role-based route protection
- CSRF protection ready

## Environment Configuration

Create a `.env` file in the frontend root:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_NODE_ENV=development
```

## Usage Examples

### Login with API
```typescript
import { useAuth } from '@/context/AuthContext';

const { loginWithAPI, loading, error } = useAuth();

const handleLogin = async () => {
  try {
    await loginWithAPI({
      email: 'user@example.com',
      password: 'password123'
    });
    // User is now logged in
  } catch (err) {
    console.error('Login failed:', err);
  }
};
```

### Register New User
```typescript
import { useAuth } from '@/context/AuthContext';

const { register, loading, error } = useAuth();

const handleRegister = async () => {
  try {
    await register({
      email: 'user@example.com',
      username: 'username',
      password: 'password123',
      role: 'customer'
    });
    // Registration successful, check email for verification
  } catch (err) {
    console.error('Registration failed:', err);
  }
};
```

### Check Authentication Status
```typescript
import { useAuth } from '@/context/AuthContext';

const { isAuthenticated, currentUser } = useAuth();

if (isAuthenticated) {
  console.log('User is logged in:', currentUser);
} else {
  console.log('User is not authenticated');
}
```

## API Service Usage

### Direct API Calls
```typescript
import { apiService } from '@/lib/api';

// Get current user
const user = await apiService.getCurrentUser();

// Update profile
const result = await apiService.updateProfile({
  username: 'newusername'
});

// Change password
await apiService.changePassword('oldpass', 'newpass');
```

### Using API Hooks
```typescript
import { useLogin, useRegister } from '@/hooks/useApi';

const LoginComponent = () => {
  const { execute: login, loading, error } = useLogin();
  
  const handleSubmit = async (credentials) => {
    try {
      await login(credentials);
    } catch (err) {
      // Error is automatically handled by the hook
    }
  };
};
```

## Route Protection

Routes are protected using the `ProtectedRoute` component:

```typescript
<Route
  path="/admin/dashboard"
  element={
    <ProtectedRoute allowedRoles={['admin']}>
      <AdminDashboard />
    </ProtectedRoute>
  }
/>
```

## Token Management

### Manual Token Operations
```typescript
import { AuthUtils } from '@/lib/auth';

// Check if user is authenticated
const isAuth = AuthUtils.isAuthenticated();

// Get user info from token
const user = AuthUtils.getUserFromToken();

// Check user role
const isAdmin = AuthUtils.hasRole('admin');
const hasAccess = AuthUtils.hasAnyRole(['admin', 'fm']);

// Clear all tokens
AuthUtils.clearTokens();
```

## Error Handling

The system handles various error scenarios:

1. **Network Errors**: Shows user-friendly messages
2. **Token Expiration**: Automatic refresh or redirect to login
3. **Invalid Credentials**: Clear error messages
4. **Server Errors**: Graceful degradation

## Testing

### Demo Users
The system includes demo users for testing:
- Admin user
- Field Manager user
- Contractor user
- Investor user
- Customer user

### API Testing
Toggle "Use Real API" checkbox on login page to test with actual backend.

## Security Considerations

1. **Token Storage**: Tokens are stored in localStorage (consider httpOnly cookies for production)
2. **HTTPS**: Always use HTTPS in production
3. **Token Expiration**: Short-lived access tokens with refresh mechanism
4. **Role Validation**: Both frontend and backend validate user roles
5. **Input Validation**: All forms include client-side validation

## Deployment Notes

1. Update `VITE_API_BASE_URL` for production environment
2. Configure CORS settings on backend
3. Set up proper SSL certificates
4. Configure rate limiting on authentication endpoints
5. Set up monitoring for failed login attempts

## Troubleshooting

### Common Issues

1. **CORS Errors**: Check backend CORS configuration
2. **Token Refresh Fails**: Verify refresh token endpoint
3. **Login Redirects**: Check role-based routing logic
4. **Email Verification**: Ensure email service is configured

### Debug Mode

Enable debug logging by setting:
```env
VITE_NODE_ENV=development
```

This will show detailed API request/response logs in the browser console.