import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '@/services/authApi';
import type { User } from '@/types';

interface AuthContextType {
    currentUser: User | null;
    login: (email: string, password: string) => Promise<void>;
    register: (userData: any) => Promise<void>;
    logout: () => void;
    updateUser: (updates: Partial<User>) => void;
    isAuthenticated: boolean;
    loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [currentUser, setCurrentUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check for existing token and validate
        const token = localStorage.getItem('authToken');
        if (token) {
            validateToken();
        } else {
            setLoading(false);
        }
    }, []);

    const validateToken = async () => {
        try {
            const profile = await authApi.getProfile();
            const user: User = {
                id: profile.id,
                name: profile.full_name || profile.email.split('@')[0],
                email: profile.email,
                role: profile.role.toLowerCase(),
                profileID: profile.profile_id,
            };
            setCurrentUser(user);
        } catch (error) {
            console.error('Token validation failed:', error);
            localStorage.removeItem('authToken');
        } finally {
            setLoading(false);
        }
    };

    const login = async (email: string, password: string) => {
        try {
            // Try new auth endpoint first
            let response;
            try {
                response = await authApi.login(email, password);
            } catch (error) {
                // Fallback to legacy endpoint
                console.log('Trying legacy login endpoint...');
                response = await authApi.legacyLogin(email, password);
            }
            
            // Store token
            if (response.access_token) {
                localStorage.setItem('authToken', response.access_token);
            }
            
            // Set user from response
            const user: User = {
                id: response.user?.id || response.profile?.id || 1,
                name: response.user?.full_name || response.profile?.email?.split('@')[0] || 'User',
                email: response.user?.email || response.profile?.email || email,
                role: (response.user?.role || response.profile?.user_role || 'customer').toLowerCase(),
                profileID: response.profile?.profileID || response.profile?.profile_id,
            };
            
            setCurrentUser(user);
            
            // Navigate to appropriate dashboard
            const dashboardRoute = getDashboardRoute(user.role);
            window.location.href = dashboardRoute;
            
        } catch (error: any) {
            console.error('Login failed:', error);
            throw new Error(error.response?.data?.detail || error.message || 'Login failed');
        }
    };

    const register = async (userData: any) => {
        try {
            let response;
            try {
                response = await authApi.register(userData);
            } catch (error) {
                // Fallback to legacy endpoint
                response = await authApi.legacyRegister(userData);
            }
            
            // Auto-login after registration if token provided
            if (response.access_token) {
                localStorage.setItem('authToken', response.access_token);
                await validateToken();
            }
        } catch (error: any) {
            throw new Error(error.response?.data?.detail || 'Registration failed');
        }
    };

    const logout = () => {
        localStorage.removeItem('authToken');
        setCurrentUser(null);
        
        // Optional: Call logout API
        authApi.logout().catch(() => {
            // Ignore logout API errors
        });
        
        // Redirect to login
        window.location.href = '/login';
    };

    const updateUser = (updates: Partial<User>) => {
        if (currentUser) {
            const updatedUser = { ...currentUser, ...updates };
            setCurrentUser(updatedUser);
        }
    };

    return (
        <AuthContext.Provider
            value={{
                currentUser,
                login,
                register,
                logout,
                updateUser,
                isAuthenticated: !!currentUser,
                loading,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
}

export function getDashboardRoute(role: string): string {
    switch (role.toLowerCase()) {
        case 'admin':
            return '/admin/dashboard';
        case 'fm':
            return '/fm/dashboard';
        case 'contractor':
            return '/contractor/dashboard';
        case 'investor':
            return '/investor/dashboard';
        case 'customer':
            return '/customer/dashboard';
        default:
            return '/login';
    }
}