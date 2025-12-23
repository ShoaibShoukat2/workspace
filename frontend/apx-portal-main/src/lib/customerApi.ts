const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export interface CustomerJob {
    id: number;
    job_number?: string;
    title: string;
    status: string;
    customer_email?: string;
    address?: string;
    created_at?: string;
    estimated_completion?: string;
    assigned_contractor?: {
        name: string;
        rating: number;
        specialization: string;
    };
    tracking?: {
        status: string;
        estimated_arrival?: string;
        actual_arrival?: string;
    };
}

export interface CustomerNotification {
    id: number;
    title: string;
    message: string;
    type?: string;
    created_at: string;
    is_read?: boolean;
    read?: boolean;
}

export interface CustomerDashboardData {
    active_job?: CustomerJob | null;
    recent_notifications?: CustomerNotification[];
    jobs?: CustomerJob[];
    stats?: {
        total_jobs: number;
        completed_jobs: number;
        active_jobs: number;
    };
}

export interface MaterialReference {
    id: number;
    item_name: string;
    quantity: number;
    supplier: string;
    supplier_logo?: string;
    sku?: string;
    price_low?: number;
    price_high?: number;
    purchase_url: string;
    description?: string;
}

class CustomerApiService {
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

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.baseURL}${endpoint}`;
        
        const config: RequestInit = {
            headers: {
                ...this.getHeaders(),
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || errorData.message || errorData.detail || 'An error occurred');
            }

            return await response.json();
        } catch (error) {
            if (error instanceof Error) {
                throw error;
            }
            throw new Error('Network error occurred');
        }
    }

    // Customer Dashboard
    async getDashboard(): Promise<CustomerDashboardData> {
        return await this.request('/workspace/customer/dashboard/');
    }

    // Customer Jobs
    async getJobs(): Promise<{ results: CustomerJob[]; count: number } | CustomerJob[]> {
        return await this.request('/workspace/customer/jobs/');
    }

    async getJobDetail(jobId: number): Promise<CustomerJob> {
        return await this.request(`/workspace/customer/jobs/${jobId}/`);
    }

    // Job Timeline
    async getJobTimeline(jobId: number): Promise<any[]> {
        return await this.request(`/workspace/customer/jobs/${jobId}/timeline/`);
    }

    // Live Tracking
    async getLiveTracking(jobId: number | string): Promise<any> {
        return await this.request(`/workspace/customer/tracking/${jobId}/`);
    }

    async getTrackingUpdates(jobId: number): Promise<any> {
        return await this.request(`/workspace/customer/tracking/${jobId}/updates/`);
    }

    // Notifications
    async getNotifications(): Promise<{ results: CustomerNotification[]; count: number } | CustomerNotification[]> {
        return await this.request('/workspace/customer/notifications/');
    }

    async markNotificationRead(notificationId: number): Promise<{ message: string }> {
        return await this.request(`/workspace/customer/notifications/${notificationId}/read/`, {
            method: 'POST',
        });
    }

    async markAllNotificationsRead(): Promise<{ message: string }> {
        return await this.request('/workspace/customer/notifications/mark-all-read/', {
            method: 'POST',
        });
    }

    // Checkpoints
    async getPreStartCheckpoint(jobId: number): Promise<any> {
        return await this.request(`/workspace/customer/jobs/${jobId}/pre-start-checkpoint/`);
    }

    async approvePreStartCheckpoint(jobId: number): Promise<{ message: string }> {
        return await this.request(`/workspace/customer/jobs/${jobId}/approve-pre-start/`, {
            method: 'POST',
        });
    }

    async rejectPreStartCheckpoint(jobId: number, reason: string): Promise<{ message: string }> {
        return await this.request(`/workspace/customer/jobs/${jobId}/reject-pre-start/`, {
            method: 'POST',
            body: JSON.stringify({ reason }),
        });
    }

    async getMidProjectCheckpoint(jobId: number): Promise<any> {
        return await this.request(`/workspace/customer/jobs/${jobId}/mid-project-checkpoint/`);
    }

    async approveMidProjectCheckpoint(jobId: number): Promise<{ message: string }> {
        return await this.request(`/workspace/customer/jobs/${jobId}/approve-mid-project/`, {
            method: 'POST',
        });
    }

    async rejectMidProjectCheckpoint(jobId: number, reason: string): Promise<{ message: string }> {
        return await this.request(`/workspace/customer/jobs/${jobId}/reject-mid-project/`, {
            method: 'POST',
            body: JSON.stringify({ reason }),
        });
    }

    async getFinalCheckpoint(jobId: number): Promise<any> {
        return await this.request(`/workspace/customer/jobs/${jobId}/final-checkpoint/`);
    }

    async approveFinalCheckpoint(jobId: number): Promise<{ message: string }> {
        return await this.request(`/workspace/customer/jobs/${jobId}/approve-final/`, {
            method: 'POST',
        });
    }

    async rejectFinalCheckpoint(jobId: number, reason: string): Promise<{ message: string }> {
        return await this.request(`/workspace/customer/jobs/${jobId}/reject-final/`, {
            method: 'POST',
            body: JSON.stringify({ reason }),
        });
    }

    // Materials
    async getJobMaterials(jobId: number): Promise<MaterialReference[]> {
        return await this.request(`/workspace/customer/jobs/${jobId}/materials/`);
    }

    async getMaterialDetail(materialId: number): Promise<MaterialReference> {
        return await this.request(`/workspace/customer/materials/${materialId}/`);
    }

    async confirmMaterialDelivery(jobId: number, materialIds: number[]): Promise<{ message: string }> {
        return await this.request(`/workspace/customer/jobs/${jobId}/materials/confirm-delivery/`, {
            method: 'POST',
            body: JSON.stringify({ material_ids: materialIds }),
        });
    }

    async uploadMaterialPhotos(jobId: number, formData: FormData): Promise<{ message: string }> {
        const token = localStorage.getItem('access_token');
        const headers: HeadersInit = token ? { Authorization: `Token ${token}` } : {};
        
        const response = await fetch(`${this.baseURL}/workspace/customer/jobs/${jobId}/materials/photos/`, {
            method: 'POST',
            headers,
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || errorData.message || 'Upload failed');
        }

        return response.json();
    }

    // Profile
    async getProfile(): Promise<any> {
        return await this.request('/workspace/customer/profile/');
    }

    async updateProfile(data: any): Promise<{ message: string }> {
        return await this.request('/workspace/customer/profile/', {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    }

    async updatePreferences(preferences: any): Promise<{ message: string }> {
        return await this.request('/workspace/customer/preferences/', {
            method: 'POST',
            body: JSON.stringify(preferences),
        });
    }

    // Issue Reporting
    async reportIssue(jobId: number, issueData: any): Promise<{ message: string }> {
        return await this.request('/workspace/customer/issues/report/', {
            method: 'POST',
            body: JSON.stringify({
                job_id: jobId,
                ...issueData,
            }),
        });
    }

    // Magic Token Access (Public endpoints)
    async getJobByToken(token: string): Promise<any> {
        return await this.request(`/workspace/customer/job/${token}/`);
    }

    async getTrackingByToken(token: string): Promise<any> {
        return await this.request(`/workspace/customer/tracking/${token}/`);
    }

    async validateQuoteToken(token: string): Promise<any> {
        return await this.request(`/workspace/customer/quote/${token}/validate/`);
    }

    async approveQuote(token: string, approvalData: any): Promise<any> {
        return await this.request(`/workspace/customer/quote/${token}/approve/`, {
            method: 'POST',
            body: JSON.stringify(approvalData),
        });
    }

    async confirmMaterialDeliveryByToken(token: string, formData: FormData): Promise<{ message: string }> {
        const response = await fetch(`${this.baseURL}/workspace/customer/materials/${token}/delivery/confirm/`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || errorData.message || 'Confirmation failed');
        }

        return response.json();
    }
}

export const customerApiService = new CustomerApiService(API_BASE_URL);
