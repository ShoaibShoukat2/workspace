// API configuration and utilities
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export interface LoginRequest {
    email: string;
    password: string;
}

export interface RegisterRequest {
    email: string;
    password: string;
    password2: string;
    username: string;
    role?: string;
}

export interface AuthResponse {
    access: string;
    refresh: string;
    user: {
        id: number;
        email: string;
        username: string;
        role: string;
        is_verified: boolean;
        is_active: boolean;
        created_at: string;
    };
}

export interface ApiError {
    error?: string;
    message?: string;
    detail?: string;
    [key: string]: any;
}

class ApiService {
    private baseURL: string;
    private refreshPromise: Promise<{ access: string }> | null = null;

    constructor(baseURL: string) {
        this.baseURL = baseURL;
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.baseURL}${endpoint}`;
        
        const config: RequestInit = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        // Add auth token if available
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers = {
                ...config.headers,
                Authorization: `Bearer ${token}`,
            };
        }

        try {
            const response = await fetch(url, config);
            
            // Handle token expiration
            if (response.status === 401 && token && endpoint !== '/auth/token/refresh/') {
                try {
                    await this.handleTokenRefresh();
                    // Retry the original request with new token
                    const newToken = localStorage.getItem('access_token');
                    if (newToken) {
                        config.headers = {
                            ...config.headers,
                            Authorization: `Bearer ${newToken}`,
                        };
                        const retryResponse = await fetch(url, config);
                        if (!retryResponse.ok) {
                            const errorData = await retryResponse.json().catch(() => ({}));
                            throw new Error(errorData.error || errorData.message || errorData.detail || 'An error occurred');
                        }
                        return await retryResponse.json();
                    }
                } catch (refreshError) {
                    // Refresh failed, redirect to login
                    this.clearTokens();
                    window.location.href = '/login';
                    throw new Error('Session expired. Please login again.');
                }
            }
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                console.error('API Error:', errorData); // Debug logging
                
                // Handle different error formats
                let errorMessage = 'An error occurred';
                if (errorData.error) {
                    errorMessage = errorData.error;
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                } else if (errorData.detail) {
                    errorMessage = errorData.detail;
                } else if (errorData.details) {
                    // Handle validation errors
                    if (typeof errorData.details === 'object') {
                        const errors = Object.values(errorData.details).flat();
                        errorMessage = errors.join(', ');
                    } else {
                        errorMessage = errorData.details;
                    }
                }
                
                throw new Error(errorMessage);
            }

            return await response.json();
        } catch (error) {
            if (error instanceof Error) {
                throw error;
            }
            throw new Error('Network error occurred');
        }
    }

    private async handleTokenRefresh(): Promise<void> {
        // Prevent multiple simultaneous refresh requests
        if (this.refreshPromise) {
            await this.refreshPromise;
            return;
        }

        this.refreshPromise = this.refreshToken();
        try {
            await this.refreshPromise;
        } finally {
            this.refreshPromise = null;
        }
    }

    private clearTokens(): void {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }

    // Authentication endpoints
    async login(credentials: LoginRequest): Promise<{ token: string; user: { id: number; email: string; user_type: string; first_name: string; last_name: string } }> {
        const response = await this.request<any>('/workspace/auth/login/', {
            method: 'POST',
            body: JSON.stringify(credentials),
        });

        // Store token
        if (response.token) {
            localStorage.setItem('access_token', response.token);
        }

        return response;
    }

    async register(userData: RegisterRequest): Promise<{ message: string; user: any }> {
        return await this.request('/authentication/register/', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    }

    async logout(): Promise<{ message: string }> {
        try {
            await this.request('/authentication/logout/', {
                method: 'POST',
            });
        } catch (error) {
            console.warn('Logout API call failed:', error);
        }

        this.clearTokens();
        return { message: 'Logged out successfully' };
    }

    async refreshToken(): Promise<{ access: string }> {
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        const response = await this.request<{ access: string }>('/authentication/token/refresh/', {
            method: 'POST',
            body: JSON.stringify({ refresh: refreshToken }),
        });

        localStorage.setItem('access_token', response.access);
        return response;
    }

    async getCurrentUser(): Promise<any> {
        return await this.request('/workspace/auth/user/');
    }

    async verifyEmail(token: string): Promise<{ message: string }> {
        return await this.request('/authentication/verify-email/', {
            method: 'POST',
            body: JSON.stringify({ token }),
        });
    }

    async requestPasswordReset(email: string): Promise<{ message: string }> {
        return await this.request('/authentication/password-reset/request/', {
            method: 'POST',
            body: JSON.stringify({ email }),
        });
    }

    async resetPassword(token: string, password: string): Promise<{ message: string }> {
        return await this.request('/authentication/password-reset/confirm/', {
            method: 'POST',
            body: JSON.stringify({ token, password }),
        });
    }

    async changePassword(oldPassword: string, newPassword: string): Promise<{ message: string }> {
        return await this.request('/authentication/change-password/', {
            method: 'POST',
            body: JSON.stringify({ 
                old_password: oldPassword, 
                new_password: newPassword 
            }),
        });
    }

    async updateProfile(updates: Partial<any>): Promise<{ message: string; user: any }> {
        return await this.request('/authentication/profile/', {
            method: 'PATCH',
            body: JSON.stringify(updates),
        });
    }
}

export const apiService = new ApiService(API_BASE_URL);