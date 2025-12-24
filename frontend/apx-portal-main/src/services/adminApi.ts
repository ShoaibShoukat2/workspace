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
    getLead: (leadId: number) => apiClient.get(`/admin/leads/${leadId}`),
    assignLead: (leadId: number, assignedTo: number) => 
        apiClient.patch(`/admin/leads/${leadId}/assign`, { assigned_to: assignedTo }),
    convertLead: (leadId: number, workspaceId: string) => 
        apiClient.post(`/admin/leads/${leadId}/convert`, { workspace_id: workspaceId }),
    
    // Compliance
    getCompliance: (params = {}) => apiClient.get('/admin/compliance', { params }),
    getComplianceOverview: () => apiClient.get('/admin/compliance/overview'),
    approveCompliance: (complianceId: number, notes?: string) => 
        apiClient.post(`/admin/compliance/${complianceId}/approve`, { notes }),
    rejectCompliance: (complianceId: number, reason: string) => 
        apiClient.post(`/admin/compliance/${complianceId}/reject`, { rejection_reason: reason }),
    contractorComplianceAction: (contractorId: number, action: string, notes?: string) =>
        apiClient.post(`/admin/contractors/${contractorId}/compliance-action`, { action, notes }),
    
    // Payouts
    getPayouts: (params = {}) => apiClient.get('/admin/payouts', { params }),
    getReadyForPayoutJobs: () => apiClient.get('/admin/payouts/ready'),
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
    generateReport: (reportType: string, dateFrom?: string, dateTo?: string, filters?: any) => 
        apiClient.post('/admin/reports/generate', { 
            report_type: reportType, 
            date_from: dateFrom, 
            date_to: dateTo, 
            filters 
        }),
    getAnalyticsOverview: (params = {}) => apiClient.get('/admin/analytics/overview', { params }),
    getRevenueAnalytics: (params = {}) => apiClient.get('/admin/analytics/revenue', { params }),
    getPerformanceAnalytics: (params = {}) => apiClient.get('/admin/analytics/performance', { params }),
    
    // System Management
    getSystemHealth: () => apiClient.get('/admin/system/health'),
    getSystemLogs: (params = {}) => apiClient.get('/admin/system/logs', { params }),
    toggleMaintenanceMode: (enabled: boolean, message?: string) => 
        apiClient.post('/admin/system/maintenance', { enabled, message }),
    
    // Meetings
    getMeetings: (params = {}) => apiClient.get('/admin/meetings', { params }),
    createMeeting: (title: string, description?: string, scheduledDate?: string, duration?: number, attendees?: string[]) => 
        apiClient.post('/admin/meetings', { 
            title, 
            description, 
            scheduled_date: scheduledDate, 
            duration, 
            attendees 
        }),
    
    // Financial Management
    getLedger: (params = {}) => apiClient.get('/admin/ledger', { params }),
    getInvestorAccounting: (params = {}) => apiClient.get('/admin/investor-accounting', { params }),
    
    // Dispute Statistics
    getDisputeStatistics: () => apiClient.get('/admin/disputes/statistics'),
};