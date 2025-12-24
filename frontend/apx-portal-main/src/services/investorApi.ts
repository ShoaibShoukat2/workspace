import { apiClient } from './apiClient';

export const investorApi = {
    // Dashboard Overview
    getDashboard: () => apiClient.get('/investors/dashboard'),
    
    // Job Breakdowns and Performance
    getJobBreakdowns: (params = {}) => apiClient.get('/investors/job-breakdowns', { params }),
    getPerformance: (params = {}) => apiClient.get('/investors/performance', { params }),
    getPortfolio: () => apiClient.get('/investors/portfolio'),
    getRoiAnalysis: (params = {}) => apiClient.get('/investors/roi-analysis', { params }),
    getMarketInsights: () => apiClient.get('/investors/market-insights'),
    
    // Payouts and Financial Data
    getPayouts: (params = {}) => apiClient.get('/investors/payouts', { params }),
    getEarningsBreakdown: () => apiClient.get('/investors/earnings-breakdown'),
    getAllocationData: () => apiClient.get('/investors/allocation-data'),
    
    // Reports Management
    getReports: (params = {}) => apiClient.get('/investors/reports', { params }),
    generateReport: (reportType: string, dateFrom?: string, dateTo?: string, filters?: any) => 
        apiClient.post('/investors/reports/generate', { 
            report_type: reportType, 
            date_from: dateFrom, 
            date_to: dateTo, 
            filters 
        }),
    
    // Properties Management
    getProperties: (params = {}) => apiClient.get('/investors/properties', { params }),
    getPropertyDetails: (propertyId: number) => 
        apiClient.get(`/investors/properties/${propertyId}`),
    
    // Investment Leads
    getLeads: (params = {}) => apiClient.get('/investors/leads', { params }),
    createLead: (leadData: any) => apiClient.post('/investors/leads', leadData),
    updateLead: (leadId: number, data: any) => 
        apiClient.patch(`/investors/leads/${leadId}`, data),
    deleteLead: (leadId: number) => apiClient.delete(`/investors/leads/${leadId}`),
    
    // Investment Analysis
    getInvestmentAnalysis: (params = {}) => apiClient.get('/investors/analysis', { params }),
    getMarketTrends: () => apiClient.get('/investors/market-trends'),
    getCompetitiveAnalysis: () => apiClient.get('/investors/competitive-analysis'),
    
    // Portfolio Management
    rebalancePortfolio: (allocationData: any) => 
        apiClient.post('/investors/portfolio/rebalance', allocationData),
    getPortfolioHistory: (params = {}) => apiClient.get('/investors/portfolio/history', { params }),
};