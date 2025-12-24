import { apiClient } from './apiClient';

export const authApi = {
    login: (email: string, password: string) => 
        apiClient.post('/auth/login', { email, password }),
    
    register: (userData: any) => 
        apiClient.post('/auth/register', userData),
    
    logout: () => 
        apiClient.post('/auth/logout'),
    
    refreshToken: () => 
        apiClient.post('/auth/refresh'),
    
    getProfile: () => 
        apiClient.get('/auth/me'),
    
    updateProfile: (data: any) => 
        apiClient.patch('/auth/profile', data),
    
    resetPassword: (email: string) => 
        apiClient.post('/auth/password-reset/request', { email }),
    
    verifyEmail: (token: string) => 
        apiClient.post('/auth/verify-email', { token }),
    
    // Legacy endpoints for compatibility
    legacyLogin: (email: string, password: string) => 
        apiClient.post('/login', { email, password }),
    
    legacyRegister: (userData: any) => 
        apiClient.post('/signup', userData),
};