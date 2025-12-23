import { useState, useCallback } from 'react';
import { apiService } from '@/lib/api';

interface UseApiState<T> {
    data: T | null;
    loading: boolean;
    error: string | null;
}

interface UseApiReturn<T> extends UseApiState<T> {
    execute: (...args: any[]) => Promise<T>;
    reset: () => void;
}

export function useApi<T>(
    apiFunction: (...args: any[]) => Promise<T>
): UseApiReturn<T> {
    const [state, setState] = useState<UseApiState<T>>({
        data: null,
        loading: false,
        error: null,
    });

    const execute = useCallback(
        async (...args: any[]): Promise<T> => {
            setState(prev => ({ ...prev, loading: true, error: null }));
            
            try {
                const result = await apiFunction(...args);
                setState(prev => ({ ...prev, data: result, loading: false }));
                return result;
            } catch (error) {
                const errorMessage = error instanceof Error ? error.message : 'An error occurred';
                setState(prev => ({ ...prev, error: errorMessage, loading: false }));
                throw error;
            }
        },
        [apiFunction]
    );

    const reset = useCallback(() => {
        setState({
            data: null,
            loading: false,
            error: null,
        });
    }, []);

    return {
        ...state,
        execute,
        reset,
    };
}

// Specific hooks for common API operations
export function useLogin() {
    return useApi(apiService.login.bind(apiService));
}

export function useRegister() {
    return useApi(apiService.register.bind(apiService));
}

export function usePasswordReset() {
    return useApi(apiService.requestPasswordReset.bind(apiService));
}

export function usePasswordResetConfirm() {
    return useApi(apiService.resetPassword.bind(apiService));
}