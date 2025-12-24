import { apiClient } from './apiClient';

export const contractorApi = {
    // Dashboard
    getDashboard: () => apiClient.get('/contractors/dashboard/overview'),
    
    // Job Assignments
    getAssignments: (params = {}) => apiClient.get('/contractors/assignments', { params }),
    acceptAssignment: (assignmentId: number) => 
        apiClient.post(`/contractors/assignments/${assignmentId}/accept`),
    rejectAssignment: (assignmentId: number, reason?: string) => 
        apiClient.post(`/contractors/assignments/${assignmentId}/reject`, { reason }),
    
    // Available Jobs
    getAvailableJobs: (params = {}) => apiClient.get('/contractors/jobs/available', { params }),
    getMyJobs: (params = {}) => apiClient.get('/contractors/jobs/my-jobs', { params }),
    acceptJob: (jobId: number) => apiClient.post(`/contractors/jobs/${jobId}/accept`),
    
    // Wallet and Payouts
    getWallet: () => apiClient.get('/contractors/wallet'),
    requestPayout: (amount: number, notes?: string) => 
        apiClient.post('/contractors/payout-request', { amount, notes }),
    getPayouts: (params = {}) => apiClient.get('/contractors/payouts', { params }),
    
    // Compliance Management
    getCompliance: () => apiClient.get('/contractors/compliance'),
    getComplianceStatus: () => apiClient.get('/contractors/compliance/status'),
    uploadComplianceDocument: (data: FormData) => 
        apiClient.post('/contractors/compliance/upload', data, {
            headers: { 'Content-Type': 'multipart/form-data' }
        }),
    
    // Notifications
    getNotifications: (params = {}) => apiClient.get('/contractors/notifications', { params }),
    markNotificationRead: (notificationId: number) => 
        apiClient.patch(`/contractors/notifications/${notificationId}/read`),
    
    // Performance Metrics
    getPerformance: (contractorId: number) => 
        apiClient.get(`/contractors/${contractorId}/performance`),
    
    // Profile Management (Admin endpoints for contractor management)
    getContractors: (params = {}) => apiClient.get('/contractors/', { params }),
    createContractor: (data: any) => apiClient.post('/contractors/', data),
    updateContractor: (contractorId: number, data: any) => 
        apiClient.patch(`/contractors/${contractorId}`, data),
    getContractor: (contractorId: number) => 
        apiClient.get(`/contractors/${contractorId}`),
};