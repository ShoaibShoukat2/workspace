const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export interface InvestorDashboardData {
    total_properties: number;
    active_work_orders: number;
    total_revenue: number;
    roi_percentage: number;
    pending_payouts: number;
}

export interface PropertyData {
    id: number;
    address: string;
    status: string;
    total_investment: number;
    current_revenue: number;
    roi_percentage: number;
    active_jobs: number;
}

export interface WorkOrder {
    id: number;
    property_address: string;
    job_title: string;
    status: string;
    estimated_cost: number;
    actual_cost?: number;
    created_at: string;
}

export interface RevenueData {
    month: string;
    amount: number;
    count: number;
}

export interface JobCategoryBreakdown {
    category: string;
    count: number;
    revenue: number;
}

export interface PayoutData {
    id: number;
    amount: number;
    status: string;
    date: string;
}

class InvestorApiService {
    private baseURL: string;

    constructor(baseURL: string) {
        this.baseURL = baseURL;
    }

    private getHeaders(): HeadersInit {
        const token = localStorage.getItem('access_token');
        return {
            'Content-Type': 'application/json',
            ...(token && { Authorization: `Token ${token}` }),
        };
    }

    private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
        const url = `${this.baseURL}${endpoint}`;
        const response = await fetch(url, {
            ...options,
            headers: {
                ...this.getHeaders(),
                ...options.headers,
            },
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || error.message || 'API request failed');
        }

        return await response.json();
    }

    async getDashboard(): Promise<InvestorDashboardData> {
        return this.request('/workspace/investor/dashboard/');
    }

    async getProperties(): Promise<{ results: PropertyData[]; count: number }> {
        return this.request('/workspace/investor/properties/');
    }

    async getPropertyDetail(propertyId: number): Promise<PropertyData & { jobs: any[] }> {
        return this.request(`/workspace/investor/properties/${propertyId}/`);
    }

    async getActiveWorkOrders(): Promise<{ results: WorkOrder[]; count: number }> {
        return this.request('/workspace/investor/active-work-orders/');
    }

    async getRevenueStatistics(period?: string): Promise<RevenueData[]> {
        const params = new URLSearchParams();
        if (period) params.append('period', period);
        return this.request(`/workspace/investor/revenue-statistics/?${params.toString()}`);
    }

    async getROIAnalytics(): Promise<{
        total_roi: number;
        roi_by_property: Array<{ property: string; roi: number }>;
    }> {
        return this.request('/workspace/investor/roi-analytics/');
    }

    async getJobCategoryBreakdown(): Promise<JobCategoryBreakdown[]> {
        return this.request('/workspace/investor/job-categories/');
    }

    async getPayoutAnalytics(): Promise<PayoutData[]> {
        return this.request('/workspace/investor/payout-analytics/');
    }

    async getEarningsBreakdown(period?: string): Promise<any> {
        const params = new URLSearchParams();
        if (period) params.append('period', period);
        return this.request(`/workspace/investor/earnings-breakdown/?${params.toString()}`);
    }

    async getPropertyPerformance(): Promise<any> {
        return this.request('/workspace/investor/property-performance/');
    }

    async getRecentActivity(): Promise<any[]> {
        return this.request('/workspace/investor/recent-activity/');
    }

    async downloadReportCSV(): Promise<Blob> {
        const response = await fetch(`${this.baseURL}/workspace/investor/download-report/`, {
            headers: this.getHeaders(),
        });

        if (!response.ok) throw new Error('Failed to download report');
        return response.blob();
    }

    async downloadDetailedJobReportCSV(): Promise<Blob> {
        const response = await fetch(`${this.baseURL}/workspace/investor/download-detailed-report/`, {
            headers: this.getHeaders(),
        });

        if (!response.ok) throw new Error('Failed to download detailed report');
        return response.blob();
    }
}

export const investorApiService = new InvestorApiService(API_BASE_URL);
