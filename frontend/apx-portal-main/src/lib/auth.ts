import { apiService } from './api';

export interface TokenPayload {
    user_id: number;
    email: string;
    role: string;
    exp: number;
    iat: number;
}

export class AuthUtils {
    static getToken(): string | null {
        return localStorage.getItem('access_token');
    }

    static getRefreshToken(): string | null {
        return localStorage.getItem('refresh_token');
    }

    static setTokens(accessToken: string, refreshToken: string): void {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
    }

    static clearTokens(): void {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        sessionStorage.removeItem('currentUser');
    }

    static decodeToken(token: string): TokenPayload | null {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(
                atob(base64)
                    .split('')
                    .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
                    .join('')
            );
            return JSON.parse(jsonPayload);
        } catch (error) {
            console.error('Error decoding token:', error);
            return null;
        }
    }

    static isTokenExpired(token: string): boolean {
        const payload = this.decodeToken(token);
        if (!payload) return true;
        
        const currentTime = Date.now() / 1000;
        return payload.exp < currentTime;
    }

    static isAuthenticated(): boolean {
        const token = this.getToken();
        if (!token) return false;
        
        return !this.isTokenExpired(token);
    }

    static async refreshTokenIfNeeded(): Promise<boolean> {
        const token = this.getToken();
        const refreshToken = this.getRefreshToken();
        
        if (!token || !refreshToken) return false;
        
        // Check if token expires in the next 5 minutes
        const payload = this.decodeToken(token);
        if (!payload) return false;
        
        const currentTime = Date.now() / 1000;
        const timeUntilExpiry = payload.exp - currentTime;
        
        if (timeUntilExpiry < 300) { // 5 minutes
            try {
                await apiService.refreshToken();
                return true;
            } catch (error) {
                console.error('Token refresh failed:', error);
                this.clearTokens();
                return false;
            }
        }
        
        return true;
    }

    static getUserFromToken(): TokenPayload | null {
        const token = this.getToken();
        if (!token) return null;
        
        return this.decodeToken(token);
    }

    static hasRole(requiredRole: string): boolean {
        const user = this.getUserFromToken();
        if (!user) return false;
        
        return user.role === requiredRole;
    }

    static hasAnyRole(roles: string[]): boolean {
        const user = this.getUserFromToken();
        if (!user) return false;
        
        return roles.includes(user.role);
    }
}

// Auto-refresh token on app load
export const initializeAuth = async (): Promise<void> => {
    if (AuthUtils.isAuthenticated()) {
        await AuthUtils.refreshTokenIfNeeded();
    }
};

// Set up periodic token refresh (every 4 minutes)
export const startTokenRefreshTimer = (): NodeJS.Timeout => {
    return setInterval(async () => {
        if (AuthUtils.isAuthenticated()) {
            await AuthUtils.refreshTokenIfNeeded();
        }
    }, 4 * 60 * 1000); // 4 minutes
};