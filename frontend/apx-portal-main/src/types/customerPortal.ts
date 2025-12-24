export type WorkflowStep = 'job-management' | 'overview' | 'quote' | 'materials' | 'progress' | 'completion';

export interface Contractor {
    id: string;
    name: string;
    avatar: string;
    rating: number;
    jobsCount: number;
    role: string;
}

export interface TimelineStep {
    id: string;
    label: string;
    status: 'completed' | 'pending' | 'active';
    date?: string;
}

export interface ScopeItem {
    id: string;
    title: string;
    description: string;
    price: number;
    completed?: boolean;
}

export interface MaterialItem {
    id: string;
    name: string;
    description: string;
    image: string;
    price: number;
    unit: string;
    vendor: {
        name: string;
        logo: string;
        color: string;
    };
    inStock?: boolean;
}

export interface ProgressPhase {
    id: string;
    title: string;
    status: 'completed' | 'active' | 'pending';
    dayProgress?: string;
    contractorNote?: {
        author: string;
        avatar: string;
        text: string;
    };
    tasks?: Array<{
        id: string;
        label: string;
        status: 'completed' | 'in-progress' | 'pending';
    }>;
}

export interface CustomerJob {
    id: string;
    title: string;
    address: string;
    status: 'active' | 'pending' | 'completed';
    estimatedCost: number;
    schedule: {
        duration: string;
        completionDate: string;
    };
    contractor: Contractor;
    timelineSteps: TimelineStep[];
    measurements?: {
        totalArea: string;
        ceilingHeight: string;
        linearCabinetry?: string;
    };
    scopeItems: ScopeItem[];
    materials?: MaterialItem[];
    progressPhases: ProgressPhase[];
    gallery?: Array<{
        id: string;
        image: string;
        label: string;
    }>;
    beforeImage?: string;
    afterImage?: string;
    finalBalance?: number;
}

