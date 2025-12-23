import React, { useMemo } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import type { UserRole } from '@/types';

interface ProtectedRouteProps {
    children: React.ReactNode;
    allowedRoles?: UserRole[];
}

export default function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
    const { currentUser, isAuthenticated, loading } = useAuth();

    // Memoize the authentication check to prevent unnecessary re-renders
    const authCheck = useMemo(() => {
        if (loading) {
            return { status: 'loading' };
        }
        
        if (!isAuthenticated || !currentUser) {
            return { status: 'unauthenticated' };
        }

        if (allowedRoles && !allowedRoles.includes(currentUser.role)) {
            return { status: 'unauthorized' };
        }

        return { status: 'authorized' };
    }, [isAuthenticated, currentUser, allowedRoles, loading]);

    if (authCheck.status === 'loading') {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
                    <p className="mt-2 text-gray-600">Loading...</p>
                </div>
            </div>
        );
    }

    if (authCheck.status === 'unauthenticated' || authCheck.status === 'unauthorized') {
        return <Navigate to="/login" replace />;
    }

    return <>{children}</>;
}
