# Complete Frontend API Integration Plan

## 🎯 **Objective: Replace ALL Mock Data with Backend APIs**

This plan provides complete integration for all dashboards and authentication to use real backend APIs instead of mock data.

## 📋 **Current Mock Data Usage Analysis**

### **Pages Using Mock Data:**
1. **Authentication**: Login.tsx, AuthContext.tsx
2. **Admin Dashboard**: All 11 admin pages
3. **Contractor Dashboard**: All 7 contractor pages  
4. **Customer Dashboard**: All 12 customer pages
5. **FM Dashboard**: All 4 FM pages
6. **Investor Dashboard**: All 3 investor pages

### **Total Pages to Integrate: 38 pages**

## 🔧 **Step 1: Create API Service Layer**

### **1.1 Base API Client**
Create `src/services/apiClient.ts`:

```typescript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
    (response) => response.data,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('authToken');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);
```

### **1.2 Authentication API Service**
Create `src/services/authApi.ts`:

```typescript
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
};
```

### **1.3 Dashboard-Specific API Services**

#### **Admin API Service**
Create `src/services/adminApi.ts`:

```typescript
import { apiClient } from './apiClient';

export const adminApi = {
    // Dashboard
    getDashboard: () => apiClient.get('/admin/dashboard'),
    
    // Jobs
    getJobs: (params = {}) => apiClient.get('/admin/jobs', { params }),
    getJob: (jobId: number) => apiClient.get(`/admin/jobs/${jobId}`),
    assignJob: (jobId: number, contractorId: number, notes?: string) => 
        apiClient.patch(`/admin/jobs/${jobId}/assign`, { contractor_id: contractorId, notes }),
    cancelJob: (jobId: number, reason: string) => 
        apiClient.post(`/admin/jobs/${jobId}/cancel`, { cancellation_reason: reason }),
    
    // Leads
    getLeads: (params = {}) => apiClient.get('/admin/leads', { params }),
    createLead: (data: any) => apiClient.post('/admin/leads', data),
    convertLead: (leadId: number, workspaceId: string) => 
        apiClient.post(`/admin/leads/${leadId}/convert`, { workspace_id: workspaceId }),
    
    // Compliance
    getCompliance: (params = {}) => apiClient.get('/admin/compliance', { params }),
    approveCompliance: (complianceId: number, notes?: string) => 
        apiClient.post(`/admin/compliance/${complianceId}/approve`, { notes }),
    rejectCompliance: (complianceId: number, reason: string) => 
        apiClient.post(`/admin/compliance/${complianceId}/reject`, { rejection_reason: reason }),
    
    // Payouts
    getPayouts: (params = {}) => apiClient.get('/admin/payouts', { params }),
    approvePayout: (payoutId: number) => 
        apiClient.post(`/admin/payouts/${payoutId}/approve`),
    rejectPayout: (payoutId: number, reason: string) => 
        apiClient.post(`/admin/payouts/${payoutId}/reject`, { rejection_reason: reason }),
    bulkApprovePayouts: (payoutIds: number[]) => 
        apiClient.post('/admin/payouts/bulk-approve', { payout_ids: payoutIds }),
    
    // Users and Contractors
    getUsers: (params = {}) => apiClient.get('/admin/users', { params }),
    getContractors: (params = {}) => apiClient.get('/admin/contractors', { params }),
    
    // Reports and Analytics
    getReports: (params = {}) => apiClient.get('/admin/reports', { params }),
    generateReport: (data: any) => apiClient.post('/admin/reports/generate', data),
    getAnalytics: (params = {}) => apiClient.get('/admin/analytics/overview', { params }),
    
    // System
    getSystemHealth: () => apiClient.get('/admin/system/health'),
    getSystemLogs: (params = {}) => apiClient.get('/admin/system/logs', { params }),
    
    // Meetings
    getMeetings: (params = {}) => apiClient.get('/admin/meetings', { params }),
    createMeeting: (data: any) => apiClient.post('/admin/meetings', data),
    
    // Ledger
    getLedger: (params = {}) => apiClient.get('/admin/ledger', { params }),
    getInvestorAccounting: (params = {}) => apiClient.get('/admin/investor-accounting', { params }),
};
```

#### **Contractor API Service**
Create `src/services/contractorApi.ts`:

```typescript
import { apiClient } from './apiClient';

export const contractorApi = {
    // Dashboard
    getDashboard: () => apiClient.get('/contractors/dashboard/overview'),
    
    // Jobs
    getAssignments: (params = {}) => apiClient.get('/contractors/assignments', { params }),
    acceptAssignment: (assignmentId: number) => 
        apiClient.post(`/contractors/assignments/${assignmentId}/accept`),
    rejectAssignment: (assignmentId: number, reason?: string) => 
        apiClient.post(`/contractors/assignments/${assignmentId}/reject`, { reason }),
    
    getAvailableJobs: (params = {}) => apiClient.get('/contractors/jobs/available', { params }),
    getMyJobs: (params = {}) => apiClient.get('/contractors/jobs/my-jobs', { params }),
    acceptJob: (jobId: number) => apiClient.post(`/contractors/jobs/${jobId}/accept`),
    
    // Wallet and Payouts
    getWallet: () => apiClient.get('/contractors/wallet'),
    requestPayout: (amount: number, notes?: string) => 
        apiClient.post('/contractors/payout-request', { amount, notes }),
    getPayouts: (params = {}) => apiClient.get('/contractors/payouts', { params }),
    
    // Compliance
    getCompliance: () => apiClient.get('/contractors/compliance'),
    getComplianceStatus: () => apiClient.get('/contractors/compliance/status'),
    uploadDocument: (data: FormData) => 
        apiClient.post('/contractors/compliance/upload', data, {
            headers: { 'Content-Type': 'multipart/form-data' }
        }),
    
    // Notifications
    getNotifications: (params = {}) => apiClient.get('/contractors/notifications', { params }),
    
    // Performance
    getPerformance: (contractorId: number) => 
        apiClient.get(`/contractors/${contractorId}/performance`),
};
```

#### **Customer API Service**
Create `src/services/customerApi.ts`:

```typescript
import { apiClient } from './apiClient';

export const customerApi = {
    // Dashboard
    getDashboard: () => apiClient.get('/customers/dashboard'),
    
    // Jobs
    getJobs: (params = {}) => apiClient.get('/customers/jobs', { params }),
    getJob: (jobId: number) => apiClient.get(`/customers/jobs/${jobId}`),
    getJobTracking: (jobId: number) => apiClient.get(`/customers/jobs/${jobId}/tracking`),
    getContractorLocation: (jobId: number) => 
        apiClient.get(`/customers/jobs/${jobId}/contractor-location`),
    getMaterials: (jobId: number) => apiClient.get(`/customers/jobs/${jobId}/materials`),
    
    // Approvals and Issues
    approveCheckpoint: (jobId: number, checkpointId: number) => 
        apiClient.post(`/customers/jobs/${jobId}/approve-checkpoint/${checkpointId}`),
    reportIssue: (jobId: number, issue: any) => 
        apiClient.post(`/customers/jobs/${jobId}/report-issue`, issue),
    
    // Notifications
    getNotifications: (params = {}) => apiClient.get('/customers/notifications', { params }),
    
    // Public Access
    getPublicJob: (token: string) => apiClient.get(`/customers/public/job/${token}`),
};
```

#### **Investor API Service**
Create `src/services/investorApi.ts`:

```typescript
import { apiClient } from './apiClient';

export const investorApi = {
    // Dashboard
    getDashboard: () => apiClient.get('/investors/dashboard'),
    getJobBreakdowns: (params = {}) => apiClient.get('/investors/job-breakdowns', { params }),
    getPerformance: (params = {}) => apiClient.get('/investors/performance', { params }),
    getPortfolio: () => apiClient.get('/investors/portfolio'),
    getRoiAnalysis: (params = {}) => apiClient.get('/investors/roi-analysis', { params }),
    getMarketInsights: () => apiClient.get('/investors/market-insights'),
    
    // Payouts and Reports
    getPayouts: (params = {}) => apiClient.get('/investors/payouts', { params }),
    getReports: (params = {}) => apiClient.get('/investors/reports', { params }),
    generateReport: (data: any) => apiClient.post('/investors/reports/generate', data),
    
    // Properties
    getProperties: (params = {}) => apiClient.get('/investors/properties', { params }),
    getPropertyDetails: (propertyId: number) => 
        apiClient.get(`/investors/properties/${propertyId}`),
    
    // Leads
    getLeads: (params = {}) => apiClient.get('/investors/leads', { params }),
    createLead: (data: any) => apiClient.post('/investors/leads', data),
    
    // Additional Data
    getEarningsBreakdown: () => apiClient.get('/investors/earnings-breakdown'),
    getAllocationData: () => apiClient.get('/investors/allocation-data'),
};
```

#### **FM API Service**
Create `src/services/fmApi.ts`:

```typescript
import { apiClient } from './apiClient';

export const fmApi = {
    // Dashboard
    getDashboard: () => apiClient.get('/fm/dashboard'),
    
    // Site Visits
    getSiteVisits: (params = {}) => apiClient.get('/fm/site-visits', { params }),
    getSiteVisit: (visitId: number) => apiClient.get(`/fm/site-visits/${visitId}`),
    createSiteVisit: (data: any) => apiClient.post('/fm/site-visits', data),
    updateSiteVisit: (visitId: number, data: any) => 
        apiClient.patch(`/fm/site-visits/${visitId}`, data),
    submitSiteVisit: (visitId: number) => 
        apiClient.post(`/fm/site-visits/${visitId}/submit`),
    
    // Materials
    verifyMaterials: (data: any) => apiClient.post('/fm/materials/verify', data),
    getAiMaterialSuggestions: (jobId: number) => 
        apiClient.get(`/fm/materials/ai-suggestions/${jobId}`),
    
    // Change Orders
    getChangeOrders: (params = {}) => apiClient.get('/fm/change-orders', { params }),
    createChangeOrder: (data: any) => apiClient.post('/fm/change-orders', data),
    getChangeOrder: (changeOrderId: number) => 
        apiClient.get(`/fm/change-orders/${changeOrderId}`),
    
    // Jobs
    getAssignedJobs: (params = {}) => apiClient.get('/fm/jobs/assigned', { params }),
    
    // Quotes
    generateQuote: (data: any) => apiClient.post('/fm/quotes/generate', data),
    
    // Photos
    uploadPhotos: (visitId: number, photoType: string) => 
        apiClient.post('/fm/photos/upload', { visit_id: visitId, photo_type: photoType }),
    
    // Analytics
    getAnalytics: (params = {}) => apiClient.get('/fm/analytics/overview', { params }),
    getPerformanceMetrics: (params = {}) => 
        apiClient.get('/fm/performance/metrics', { params }),
    
    // Map
    getMapJobs: () => apiClient.get('/fm/map/jobs'),
};
```

## 🔧 **Step 2: Update Authentication System**

### **2.1 Update AuthContext**
Replace `src/context/AuthContext.tsx`:

```typescript
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
            localStorage.removeItem('authToken');
        } finally {
            setLoading(false);
        }
    };

    const login = async (email: string, password: string) => {
        try {
            const response = await authApi.login(email, password);
            
            // Store token
            localStorage.setItem('authToken', response.access_token);
            
            // Set user from response
            const user: User = {
                id: response.user.id,
                name: response.user.full_name || response.user.email.split('@')[0],
                email: response.user.email,
                role: response.user.role.toLowerCase(),
                profileID: response.profile?.profile_id,
            };
            
            setCurrentUser(user);
        } catch (error: any) {
            throw new Error(error.response?.data?.detail || 'Login failed');
        }
    };

    const register = async (userData: any) => {
        try {
            const response = await authApi.register(userData);
            
            // Auto-login after registration
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
        authApi.logout().catch(() => {});
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
```

### **2.2 Update Login Component**
Replace mock data usage in `src/pages/Login.tsx`:

```typescript
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth, getDashboardRoute } from '@/context/AuthContext';
import type { UserRole } from '@/types';
import AuthLayoutSplit from '@/components/auth/AuthLayoutSplit';
import RoleToggle, { RoleOption } from '@/components/auth/RoleToggle';
import GlassInput from '@/components/auth/GlassInput';
import PrimaryButton from '@/components/auth/PrimaryButton';

const ROLE_OPTIONS: RoleOption[] = [
    { id: 'admin', label: 'Admin', role: 'admin' },
    { id: 'contractor', label: 'Contractor Pro', role: 'contractor' },
    { id: 'investor', label: 'Investor', role: 'investor' },
    { id: 'customer', label: 'Homeowner', role: 'customer' },
];

export default function Login() {
    const navigate = useNavigate();
    const { login, loading } = useAuth();

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [selectedRole, setSelectedRole] = useState<UserRole>('contractor');
    const [error, setError] = useState('');

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        try {
            await login(email, password);
            // Navigation will be handled by auth context
        } catch (err: any) {
            setError(err.message || 'Login failed');
        }
    };

    // Demo login function for development
    const handleDemoLogin = async (role: UserRole) => {
        const demoCredentials = {
            admin: { email: 'admin@apex.inc', password: 'admin123' },
            contractor: { email: 'contractor@apex.inc', password: 'contractor123' },
            investor: { email: 'investor@apex.inc', password: 'investor123' },
            customer: { email: 'customer@apex.inc', password: 'customer123' },
            fm: { email: 'fm@apex.inc', password: 'fm123' },
        };

        const creds = demoCredentials[role];
        if (creds) {
            setEmail(creds.email);
            setPassword(creds.password);
            try {
                await login(creds.email, creds.password);
            } catch (err: any) {
                setError(err.message || 'Demo login failed');
            }
        }
    };

    return (
        <AuthLayoutSplit>
            <RoleToggle
                options={ROLE_OPTIONS}
                activeRole={selectedRole}
                onChange={(role) => setSelectedRole(role)}
            />

            <form onSubmit={handleLogin} className="space-y-6">
                <GlassInput
                    label="Email Address"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="user@apex.inc"
                    required
                />

                <GlassInput
                    label="Password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    required
                />

                {error && (
                    <div className="text-rose-300 text-xs bg-rose-500/10 border border-rose-400/30 rounded-xl px-3 py-2">
                        {error}
                    </div>
                )}

                <PrimaryButton type="submit" loading={loading}>
                    Sign In
                </PrimaryButton>
            </form>

            {/* Demo Login Buttons */}
            <div className="mt-6 space-y-2">
                <p className="text-xs text-slate-500 text-center">Demo Logins:</p>
                <div className="grid grid-cols-2 gap-2">
                    {ROLE_OPTIONS.map((option) => (
                        <button
                            key={option.id}
                            type="button"
                            onClick={() => handleDemoLogin(option.role)}
                            className="px-3 py-2 text-xs bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 transition-colors"
                        >
                            {option.label}
                        </button>
                    ))}
                </div>
            </div>
        </AuthLayoutSplit>
    );
}
```

## 🔧 **Step 3: Dashboard Integration Examples**

### **3.1 Admin Dashboard Integration**
Update `src/pages/admin/AdminDashboard.tsx`:

```typescript
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { adminApi } from '@/services/adminApi';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
// ... other imports

export default function AdminDashboard() {
    const navigate = useNavigate();
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            setLoading(true);
            const data = await adminApi.getDashboard();
            setDashboardData(data);
            setError(null);
        } catch (err) {
            setError('Failed to load dashboard data');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <PortalLayout title="Admin Dashboard" navItems={navItems}>
                <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                </div>
            </PortalLayout>
        );
    }

    if (error) {
        return (
            <PortalLayout title="Admin Dashboard" navItems={navItems}>
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-700">{error}</p>
                    <button 
                        onClick={loadDashboardData}
                        className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                    >
                        Retry
                    </button>
                </div>
            </PortalLayout>
        );
    }

    // Use real data from API
    const pendingDisputes = dashboardData?.pending_disputes || 0;
    const pendingPayouts = dashboardData?.pending_payouts_count || 0;
    const blockedContractors = dashboardData?.blocked_contractors || 0;
    const activeJobs = dashboardData?.active_jobs || 0;

    return (
        <PortalLayout title="Admin Dashboard" navItems={navItems}>
            {/* Rest of component using real data */}
        </PortalLayout>
    );
}
```

### **3.2 Contractor Dashboard Integration**
Similar pattern for `src/pages/contractor/ContractorDashboard.tsx`:

```typescript
import { useState, useEffect } from 'react';
import { contractorApi } from '@/services/contractorApi';
// ... other imports

export default function ContractorDashboard() {
    const [dashboardData, setDashboardData] = useState(null);
    const [assignments, setAssignments] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            setLoading(true);
            const [dashboard, assignmentsData] = await Promise.all([
                contractorApi.getDashboard(),
                contractorApi.getAssignments()
            ]);
            
            setDashboardData(dashboard);
            setAssignments(assignmentsData);
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    // Rest of component logic
}
```

## 🔧 **Step 4: Implementation Checklist**

### **Phase 1: Core Infrastructure**
- [ ] Create API service layer (`apiClient.ts`, `authApi.ts`)
- [ ] Update AuthContext with real API integration
- [ ] Update Login component to use backend authentication
- [ ] Test authentication flow

### **Phase 2: Dashboard APIs**
- [ ] Create dashboard-specific API services
- [ ] Update Admin dashboard pages (11 pages)
- [ ] Update Contractor dashboard pages (7 pages)
- [ ] Update Customer dashboard pages (12 pages)
- [ ] Update FM dashboard pages (4 pages)
- [ ] Update Investor dashboard pages (3 pages)

### **Phase 3: Testing & Validation**
- [ ] Test all authentication flows
- [ ] Test all dashboard functionalities
- [ ] Verify error handling
- [ ] Test loading states
- [ ] Validate data consistency

### **Phase 4: Production Readiness**
- [ ] Add proper error boundaries
- [ ] Implement retry mechanisms
- [ ] Add offline handling
- [ ] Performance optimization
- [ ] Security validation

## 🎯 **Expected Outcome**

After complete integration:

1. **Authentication**: Real JWT-based authentication
2. **All Dashboards**: Using live backend data
3. **Real-time Updates**: Live data refresh capabilities
4. **Error Handling**: Proper error states and recovery
5. **Performance**: Optimized API calls and caching
6. **Security**: Proper token management and validation

## 📊 **Integration Priority**

1. **High Priority**: Authentication, Admin Dashboard, Contractor Dashboard
2. **Medium Priority**: Customer Dashboard, Investor Dashboard
3. **Low Priority**: FM Dashboard (if needed)

This plan provides complete integration of all frontend components with the backend APIs, eliminating all mock data usage and providing a production-ready application.