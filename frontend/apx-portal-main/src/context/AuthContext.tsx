import React, { createContext, useContext, useState } from 'react';
import type { User } from '@/types';
import { apiService, type LoginRequest, type RegisterRequest } from '@/lib/api';
import { AuthUtils } from '@/lib/auth';

interface AuthContextType {
    currentUser: User | null;
    login: (email: string) => Promise<void>;
    loginWithAPI: (credentials: LoginRequest) => Promise<User>;
    register: (userData: RegisterRequest) => Promise<void>;
    logout: () => Promise<void>;
    updateUser: (updates: Partial<User>) => void;
    isAuthenticated: boolean;
    loading: boolean;
    error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [currentUser, setCurrentUser] = useState<User | null>(() => {
        // Initialize from sessionStorage on mount - no useEffect needed
        const storedUser = sessionStorage.getItem('currentUser');
        return storedUser ? JSON.parse(storedUser) : null;
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const mapApiUserToUser = (apiUser: any): User => {
        console.log('Mapping API user:', apiUser);
        const userType = apiUser.user_type || apiUser.role || 'admin';
        let role: User['role'] = 'admin';
        
        if (userType === 'contractor') role = 'contractor';
        else if (userType === 'customer') role = 'customer';
        else if (userType === 'fm') role = 'fm';
        else if (userType === 'investor') role = 'investor';
        else if (userType === 'admin') role = 'admin';
        
        const mappedUser = {
            id: parseInt(apiUser.id.toString(), 10),
            name: apiUser.first_name && apiUser.last_name 
                ? `${apiUser.first_name} ${apiUser.last_name}`.trim()
                : apiUser.username || apiUser.email,
            email: apiUser.email,
            role: role,
            avatarUrl: '',
        };
        console.log('Mapped user:', mappedUser);
        return mappedUser;
    };

    // Demo login (legacy - can be removed if not needed)
    const login = async (email: string) => {
        setLoading(true);
        setError(null);
        try {
            // For demo purposes, create a basic user object
            const demoUser: User = {
                id: 1,
                name: email.split('@')[0],
                email: email,
                role: 'admin',
                avatarUrl: ''
            };
            setCurrentUser(demoUser);
            sessionStorage.setItem('currentUser', JSON.stringify(demoUser));
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Login failed';
            setError(errorMessage);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    // API-based login
    const loginWithAPI = async (credentials: LoginRequest) => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiService.login(credentials);
            const user = mapApiUserToUser(response.user);
            
            setCurrentUser(user);
            sessionStorage.setItem('currentUser', JSON.stringify(user));
            
            return user; // Return user for navigation
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Login failed';
            setError(errorMessage);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    // API-based registration
    const register = async (userData: RegisterRequest) => {
        setLoading(true);
        setError(null);
        try {
            await apiService.register(userData);
            // Note: User needs to verify email before they can login
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Registration failed';
            setError(errorMessage);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    const logout = async () => {
        setLoading(true);
        try {
            await apiService.logout();
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            AuthUtils.clearTokens();
            setCurrentUser(null);
            sessionStorage.removeItem('currentUser');
            setLoading(false);
        }
    };

    const updateUser = (updates: Partial<User>) => {
        if (currentUser) {
            const updatedUser = { ...currentUser, ...updates };
            setCurrentUser(updatedUser);
            sessionStorage.setItem('currentUser', JSON.stringify(updatedUser));
        }
    };

    return (
        <AuthContext.Provider
            value={{
                currentUser,
                login,
                loginWithAPI,
                register,
                logout,
                updateUser,
                isAuthenticated: !!currentUser,
                loading,
                error,
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

// Helper to get dashboard route by role
export function getDashboardRoute(role: User['role']): string {
    console.log('getDashboardRoute called with role:', role);
    switch (role) {
        case 'admin':
            return '/admin/dashboard';
        case 'fm':
            return '/fm/dashboard';
        case 'contractor':
            return '/contractor/dashboard';
        case 'investor':
            return '/investor/dashboard';
        case 'customer':
            console.log('Returning customer dashboard route');
            return '/customer/dashboard';
        default:
            console.log('Unknown role, returning login');
            return '/login';
    }
}
