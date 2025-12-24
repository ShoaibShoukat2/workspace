import { apiClient } from './apiClient';

export const fmApi = {
    // Dashboard Overview
    getDashboard: () => apiClient.get('/fm/dashboard'),
    
    // Site Visits Management
    getSiteVisits: (params = {}) => apiClient.get('/fm/site-visits', { params }),
    getSiteVisit: (visitId: number) => apiClient.get(`/fm/site-visits/${visitId}`),
    createSiteVisit: (visitData: any) => apiClient.post('/fm/site-visits', visitData),
    updateSiteVisit: (visitId: number, updateData: any) => 
        apiClient.patch(`/fm/site-visits/${visitId}`, updateData),
    submitSiteVisit: (visitId: number) => 
        apiClient.post(`/fm/site-visits/${visitId}/submit`),
    
    // Materials Management
    verifyMaterials: (verificationData: any) => 
        apiClient.post('/fm/materials/verify', verificationData),
    getAiMaterialSuggestions: (jobId: number) => 
        apiClient.get(`/fm/materials/ai-suggestions/${jobId}`),
    
    // Change Orders
    getChangeOrders: (params = {}) => apiClient.get('/fm/change-orders', { params }),
    createChangeOrder: (changeOrderData: any) => 
        apiClient.post('/fm/change-orders', changeOrderData),
    getChangeOrder: (changeOrderId: number) => 
        apiClient.get(`/fm/change-orders/${changeOrderId}`),
    updateChangeOrder: (changeOrderId: number, data: any) => 
        apiClient.patch(`/fm/change-orders/${changeOrderId}`, data),
    
    // Job Management
    getAssignedJobs: (params = {}) => apiClient.get('/fm/jobs/assigned', { params }),
    getJobDetails: (jobId: number) => apiClient.get(`/fm/jobs/${jobId}`),
    
    // Quote Generation
    generateQuote: (quoteData: any) => apiClient.post('/fm/quotes/generate', quoteData),
    getQuotes: (params = {}) => apiClient.get('/fm/quotes', { params }),
    updateQuote: (quoteId: number, data: any) => 
        apiClient.patch(`/fm/quotes/${quoteId}`, data),
    
    // Photo Management
    uploadPhotos: (visitId: number, photoType: string, files?: FormData) => 
        apiClient.post('/fm/photos/upload', { 
            visit_id: visitId, 
            photo_type: photoType,
            ...(files && { files })
        }),
    getPhotos: (visitId: number) => apiClient.get(`/fm/photos/${visitId}`),
    
    // Analytics and Performance
    getAnalytics: (params = {}) => apiClient.get('/fm/analytics/overview', { params }),
    getPerformanceMetrics: (params = {}) => 
        apiClient.get('/fm/performance/metrics', { params }),
    
    // Map and Location Services
    getMapJobs: () => apiClient.get('/fm/map/jobs'),
    updateJobLocation: (jobId: number, coordinates: any) => 
        apiClient.patch(`/fm/jobs/${jobId}/location`, coordinates),
    
    // Quality Control
    createQualityReport: (visitId: number, reportData: any) => 
        apiClient.post(`/fm/quality-reports`, { visit_id: visitId, ...reportData }),
    getQualityReports: (params = {}) => apiClient.get('/fm/quality-reports', { params }),
};