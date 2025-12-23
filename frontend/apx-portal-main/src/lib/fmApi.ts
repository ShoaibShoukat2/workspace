const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export interface FMDashboardData {
    total_jobs: number;
    jobs_open: number;
    jobs_in_progress: number;
    jobs_completed: number;
    pending_estimates: number;
    pending_site_visits: number;
    total_revenue: number;
}

export interface FMJob {
    id: number;
    title: string;
    status: string;
    location: string;
    customer_name: string;
    customer_email: string;
    created_at: string;
    assigned_contractor?: string;
}

export interface EstimateData {
    id: number;
    job_id: number;
    job_title: string;
    status: string;
    total_amount: number;
    line_items_count: number;
    created_at: string;
    customer_signed: boolean;
}

export interface LineItem {
    id: number;
    description: string;
    quantity: number;
    unit_price: number;
    total_price: number;
}

export interface SiteVisitData {
    id: number;
    job_id: number;
    status: string;
    visit_date: string;
    notes: string;
    photos_count: number;
}

class FMApiService {
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

    async getDashboard(): Promise<FMDashboardData> {
        return this.request('/workspace/fm/dashboard/');
    }

    async getJobs(params?: { status?: string; limit?: number; offset?: number }): Promise<{ results: FMJob[]; count: number }> {
        const queryParams = new URLSearchParams();
        if (params?.status) queryParams.append('status', params.status);
        if (params?.limit) queryParams.append('limit', params.limit.toString());
        if (params?.offset) queryParams.append('offset', params.offset.toString());

        return this.request(`/workspace/fm/jobs/?${queryParams.toString()}`);
    }

    async getJobDetail(jobId: number): Promise<FMJob & { estimate?: EstimateData; site_visit?: SiteVisitData }> {
        return this.request(`/workspace/fm/jobs/${jobId}/`);
    }

    async createJob(data: any): Promise<FMJob> {
        return this.request('/workspace/fm/jobs/create/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getEstimates(params?: { status?: string; limit?: number; offset?: number }): Promise<{ results: EstimateData[]; count: number }> {
        const queryParams = new URLSearchParams();
        if (params?.status) queryParams.append('status', params.status);
        if (params?.limit) queryParams.append('limit', params.limit.toString());
        if (params?.offset) queryParams.append('offset', params.offset.toString());

        return this.request(`/workspace/fm/estimates/?${queryParams.toString()}`);
    }

    async getEstimateDetail(estimateId: number): Promise<EstimateData & { line_items: LineItem[] }> {
        return this.request(`/workspace/fm/estimates/${estimateId}/`);
    }

    async createEstimate(jobId: number, data: any): Promise<EstimateData> {
        return this.request('/workspace/fm/estimates/create/', {
            method: 'POST',
            body: JSON.stringify({ job_id: jobId, ...data }),
        });
    }

    async addLineItem(estimateId: number, data: any): Promise<LineItem> {
        return this.request('/workspace/fm/estimates/line-items/', {
            method: 'POST',
            body: JSON.stringify({ estimate_id: estimateId, ...data }),
        });
    }

    async updateLineItem(itemId: number, data: any): Promise<LineItem> {
        return this.request(`/workspace/fm/estimates/line-items/${itemId}/`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    }

    async deleteLineItem(itemId: number): Promise<{ message: string }> {
        return this.request(`/workspace/fm/estimates/line-items/${itemId}/`, {
            method: 'DELETE',
        });
    }

    async sendEstimate(estimateId: number): Promise<{ message: string }> {
        return this.request(`/workspace/fm/estimates/${estimateId}/send/`, {
            method: 'POST',
        });
    }

    async recalculateEstimate(estimateId: number): Promise<EstimateData> {
        return this.request(`/workspace/fm/estimates/${estimateId}/recalculate/`, {
            method: 'POST',
        });
    }

    async getSiteVisit(jobId: number): Promise<SiteVisitData> {
        return this.request(`/workspace/fm/jobs/${jobId}/visit/`);
    }

    async startSiteVisit(jobId: number, data: any): Promise<SiteVisitData> {
        return this.request(`/workspace/fm/jobs/${jobId}/visit/start/`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateSiteVisit(jobId: number, data: any): Promise<SiteVisitData> {
        return this.request(`/workspace/fm/jobs/${jobId}/visit/update/`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    }

    async completeSiteVisit(jobId: number): Promise<{ message: string }> {
        return this.request(`/workspace/fm/jobs/${jobId}/visit/complete/`, {
            method: 'POST',
        });
    }

    async uploadSiteVisitPhoto(jobId: number, formData: FormData): Promise<{ message: string }> {
        const token = localStorage.getItem('access_token');
        const headers: HeadersInit = token ? { Authorization: `Token ${token}` } : {};
        
        const response = await fetch(`${this.baseURL}/workspace/fm/jobs/${jobId}/visit/photos/`, {
            method: 'POST',
            headers,
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || error.message || 'Upload failed');
        }

        return response.json();
    }

    async generateMaterials(jobId: number): Promise<{ materials: any[] }> {
        return this.request(`/workspace/fm/jobs/${jobId}/materials/generate/`, {
            method: 'POST',
        });
    }

    async verifyMaterials(jobId: number, materials: any[]): Promise<{ message: string }> {
        return this.request(`/workspace/fm/jobs/${jobId}/materials/verify/`, {
            method: 'POST',
            body: JSON.stringify({ materials }),
        });
    }

    async createChangeOrder(jobId: number, data: any): Promise<{ id: number; message: string }> {
        return this.request(`/workspace/fm/jobs/${jobId}/change-order/`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }
}

export const fmApiService = new FMApiService(API_BASE_URL);
