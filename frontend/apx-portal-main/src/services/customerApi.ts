import { apiClient } from './apiClient';

export const customerApi = {
    // Dashboard
    getDashboard: () => apiClient.get('/customers/dashboard'),
    
    // Jobs Management
    getJobs: (params = {}) => apiClient.get('/customers/jobs', { params }),
    getJob: (jobId: number) => apiClient.get(`/customers/jobs/${jobId}`),
    
    // Real-time Tracking
    getJobTracking: (jobId: number) => apiClient.get(`/customers/jobs/${jobId}/tracking`),
    getContractorLocation: (jobId: number) => 
        apiClient.get(`/customers/jobs/${jobId}/contractor-location`),
    
    // Materials
    getMaterials: (jobId: number) => apiClient.get(`/customers/jobs/${jobId}/materials`),
    
    // Checkpoint Approvals
    approveCheckpoint: (jobId: number, checkpointId: number) => 
        apiClient.post(`/customers/jobs/${jobId}/approve-checkpoint/${checkpointId}`),
    
    // Issue Reporting
    reportIssue: (jobId: number, issueData: any) => 
        apiClient.post(`/customers/jobs/${jobId}/report-issue`, issueData),
    
    // Notifications
    getNotifications: (params = {}) => apiClient.get('/customers/notifications', { params }),
    markNotificationRead: (notificationId: number) => 
        apiClient.patch(`/customers/notifications/${notificationId}/read`),
    
    // Public Access (Magic Link)
    getPublicJob: (token: string) => apiClient.get(`/customers/public/job/${token}`),
    
    // Additional Customer Features
    getJobHistory: (params = {}) => apiClient.get('/customers/jobs/history', { params }),
    downloadInvoice: (jobId: number) => apiClient.get(`/customers/jobs/${jobId}/invoice`),
    submitFeedback: (jobId: number, feedback: any) => 
        apiClient.post(`/customers/jobs/${jobId}/feedback`, feedback),
};