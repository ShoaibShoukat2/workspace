const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export interface ContractorDashboardData {
    active_jobs_count: number;
    completed_jobs_count: number;
    total_earnings: number;
    available_jobs_count: number;
    compliance_status: string;
    wallet_balance: number;
}

export interface ContractorJob {
    id: number;
    title: string;
    status: string;
    location: string;
    customer_name: string;
    estimated_hours: number;
    created_at: string;
}

export interface JobAssignment {
    id: number;
    job_id: number;
    job_title: string;
    customer_name: string;
    location: string;
    estimated_hours: number;
    pay_amount: number;
    status: string;
}

export interface WalletData {
    balance: number;
    total_earned: number;
    pending_payout: number;
    last_payout_date?: string;
}

export interface NotificationData {
    id: number;
    type: string;
    title: string;
    message: string;
    read: boolean;
    created_at: string;
}

export interface ComplianceDocument {
    id: number;
    document_type: string;
    status: string;
    expiry_date: string;
    uploaded_date: string;
}

class ContractorApiService {
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

    async getDashboard(): Promise<ContractorDashboardData> {
        return this.request('/workspace/contractor/dashboard/');
    }

    async getActiveJobs(): Promise<{ results: ContractorJob[]; count: number }> {
        return this.request('/workspace/contractor/active-jobs/');
    }

    async getJobDetail(jobId: number): Promise<any> {
        return this.request(`/workspace/contractor/jobs/${jobId}/`);
    }

    async getAssignments(): Promise<{ results: JobAssignment[]; count: number }> {
        return this.request('/workspace/contractor/assignments/');
    }

    async acceptJob(jobId: number): Promise<{ message: string }> {
        return this.request(`/workspace/contractor/assignments/${jobId}/accept/`, {
            method: 'POST',
        });
    }

    async rejectJob(jobId: number): Promise<{ message: string }> {
        return this.request(`/workspace/contractor/assignments/${jobId}/reject/`, {
            method: 'POST',
        });
    }

    async getWallet(): Promise<WalletData> {
        return this.request('/workspace/payout/contractor-wallet/');
    }

    async getWalletTransactions(limit?: number): Promise<any[]> {
        const params = new URLSearchParams();
        if (limit) params.append('limit', limit.toString());
        return this.request(`/workspace/payout/wallet-transactions/?${params.toString()}`);
    }

    async requestPayout(amount: number): Promise<{ message: string }> {
        return this.request('/workspace/payout/request-payout/', {
            method: 'POST',
            body: JSON.stringify({ amount }),
        });
    }

    async submitJobCompletion(jobId: number, data: any): Promise<{ message: string }> {
        return this.request(`/workspace/contractor/jobs/${jobId}/complete/`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateChecklist(jobId: number, stepId: number, data: any): Promise<{ message: string }> {
        return this.request(`/workspace/contractor/checklist-step/${stepId}/update/`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    }

    async uploadStepMedia(stepId: number, formData: FormData): Promise<{ message: string }> {
        const token = localStorage.getItem('access_token');
        const headers: HeadersInit = token ? { Authorization: `Token ${token}` } : {};
        
        const response = await fetch(`${this.baseURL}/workspace/contractor/step-media/upload/`, {
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

    async getNotifications(): Promise<{ results: NotificationData[]; count: number }> {
        return this.request('/workspace/contractor/notifications/');
    }

    async markNotificationRead(notificationId: number): Promise<{ message: string }> {
        return this.request(`/workspace/contractor/notifications/${notificationId}/read/`, {
            method: 'POST',
        });
    }

    async getCompliance(): Promise<{ results: ComplianceDocument[]; count: number }> {
        return this.request('/workspace/compliance/contractor-compliance/');
    }

    async uploadCompliance(formData: FormData): Promise<{ message: string }> {
        const token = localStorage.getItem('access_token');
        const headers: HeadersInit = token ? { Authorization: `Token ${token}` } : {};
        
        const response = await fetch(`${this.baseURL}/workspace/compliance/contractor-upload/`, {
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
}

export const contractorApiService = new ContractorApiService(API_BASE_URL);
