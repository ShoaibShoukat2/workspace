const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export interface AdminDashboardStats {
    total_active_jobs: number;
    total_completed_jobs: number;
    pending_disputes: number;
    pending_payouts: number;
    total_pending_payout_amount: number;
    blocked_contractors: number;
    total_users: number;
    total_revenue: number;
}

export interface JobData {
    id: number;
    title: string;
    status: string;
    customer_email: string;
    assigned_contractor?: string;
    address: string;
    created_at: string;
    estimated_cost: number;
    actual_cost?: number;
}

export interface DisputeData {
    id: number;
    job_id: number;
    status: string;
    description: string;
    created_at: string;
    messages_count: number;
}

export interface PayoutData {
    id: number;
    contractor_id: number;
    contractor_name: string;
    job_id: number;
    amount: number;
    status: string;
    created_at: string;
}

export interface ComplianceData {
    id: number;
    contractor_id: number;
    contractor_name: string;
    document_type: string;
    status: string;
    expiry_date: string;
    created_at: string;
}

class AdminApiService {
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

    async getDashboardStats(): Promise<AdminDashboardStats> {
        return this.request('/workspace/admin/dashboard/');
    }

    async getJobs(params?: { status?: string; limit?: number; offset?: number }): Promise<{ results: JobData[]; count: number }> {
        const queryParams = new URLSearchParams();
        if (params?.status) queryParams.append('status', params.status);
        if (params?.limit) queryParams.append('limit', params.limit.toString());
        if (params?.offset) queryParams.append('offset', params.offset.toString());

        return this.request(`/workspace/admin/jobs/?${queryParams.toString()}`);
    }

    async getJobDetail(jobId: number): Promise<JobData> {
        return this.request(`/workspace/admin/jobs/${jobId}/`);
    }

    async getDisputes(params?: { status?: string; limit?: number; offset?: number }): Promise<{ results: DisputeData[]; count: number }> {
        const queryParams = new URLSearchParams();
        if (params?.status) queryParams.append('status', params.status);
        if (params?.limit) queryParams.append('limit', params.limit.toString());
        if (params?.offset) queryParams.append('offset', params.offset.toString());

        return this.request(`/workspace/compliance/disputes/?${queryParams.toString()}`);
    }

    async getDisputeDetail(disputeId: number): Promise<DisputeData & { messages: any[] }> {
        return this.request(`/workspace/compliance/disputes/${disputeId}/`);
    }

    async getPayouts(params?: { status?: string; limit?: number; offset?: number }): Promise<{ results: PayoutData[]; count: number }> {
        const queryParams = new URLSearchParams();
        if (params?.status) queryParams.append('status', params.status);
        if (params?.limit) queryParams.append('limit', params.limit.toString());
        if (params?.offset) queryParams.append('offset', params.offset.toString());

        return this.request(`/workspace/payout/ready-for-payout/?${queryParams.toString()}`);
    }

    async approveJobPayout(jobId: number): Promise<{ message: string }> {
        return this.request(`/workspace/payout/approve-job-payout/`, {
            method: 'POST',
            body: JSON.stringify({ job_id: jobId }),
        });
    }

    async rejectJobPayout(jobId: number, reason: string): Promise<{ message: string }> {
        return this.request(`/workspace/payout/reject-job-payout/`, {
            method: 'POST',
            body: JSON.stringify({ job_id: jobId, reason }),
        });
    }

    async getCompliance(params?: { status?: string; limit?: number; offset?: number }): Promise<{ results: ComplianceData[]; count: number }> {
        const queryParams = new URLSearchParams();
        if (params?.status) queryParams.append('status', params.status);
        if (params?.limit) queryParams.append('limit', params.limit.toString());
        if (params?.offset) queryParams.append('offset', params.offset.toString());

        return this.request(`/workspace/compliance/admin-compliance/?${queryParams.toString()}`);
    }

    async approveCompliance(complianceId: number): Promise<{ message: string }> {
        return this.request(`/workspace/compliance/approve-compliance/`, {
            method: 'POST',
            body: JSON.stringify({ compliance_id: complianceId }),
        });
    }

    async rejectCompliance(complianceId: number, reason: string): Promise<{ message: string }> {
        return this.request(`/workspace/compliance/reject-compliance/`, {
            method: 'POST',
            body: JSON.stringify({ compliance_id: complianceId, reason }),
        });
    }

    async getLeads(params?: { limit?: number; offset?: number }): Promise<{ results: any[]; count: number }> {
        const queryParams = new URLSearchParams();
        if (params?.limit) queryParams.append('limit', params.limit.toString());
        if (params?.offset) queryParams.append('offset', params.offset.toString());

        return this.request(`/workspace/angi/leads/?${queryParams.toString()}`);
    }

    async exportJobsCSV(): Promise<Blob> {
        const response = await fetch(`${this.baseURL}/workspace/admin/jobs/export/`, {
            headers: this.getHeaders(),
        });

        if (!response.ok) throw new Error('Failed to export jobs');
        return response.blob();
    }
}

export const adminApiService = new AdminApiService(API_BASE_URL);
