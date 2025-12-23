// User roles
export type UserRole = 'admin' | 'fm' | 'contractor' | 'investor' | 'customer';

// Job statuses
export type JobStatus = 'Estimate' | 'Open' | 'InProgress' | 'Complete' | 'ReadyForPayout' | 'Paid' | 'Declined';

// Job types
export type JobType = 'handyman' | 'investor' | 'moving';

// Visit statuses
export type VisitStatus = 'ToVisit' | 'InProgress' | 'Completed';

// Material statuses
export type MaterialStatus = 'AI Generated' | 'FM Verified' | 'Issues Found';

// Delivery statuses
export type DeliveryStatus = 'Ordered' | 'Delivered' | 'Missing Items' | 'Damaged' | 'Wrong Items' | 'Correct';

// Project statuses
export type ProjectStatus = 'Setup' | 'AdminApproved' | 'InProgress' | 'Completed';

// Subtask statuses
export type SubtaskStatus = 'NotStarted' | 'MaterialsVerified' | 'InProgress' | 'Blocked' | 'Completed';

// Compliance status
export type ComplianceStatus = 'active' | 'blocked';

// User interface
export interface User {
    id: number;
    name: string;
    email: string;
    role: UserRole;
    trade?: string; // for contractors
    complianceStatus?: ComplianceStatus;
    insuranceExpiryDate?: string;
    avatarUrl?: string;
}

// Material interface
export interface Material {
    id: string;
    name: string;
    sku: string;
    quantity: number;
    supplier: string;
    priceRange: string;
    status: MaterialStatus;
    deliveryStatus?: DeliveryStatus;
}

// Material Delivery interface
export interface MaterialDelivery {
    id: string;
    jobId: number;
    materials: Material[];
    status: DeliveryStatus;
    photos: string[];
    gpsLocation?: {
        latitude: number;
        longitude: number;
    };
    deliveredAt?: string;
    notes?: string;
}

// Estimate interface
export interface Estimate {
    id: number;
    jobId: number;
    trade: string;
    hours: number;
    materialEstimate: number;
    laborRate: number;
    scopeOfWork: string;
    price: number;
    status: 'Draft' | 'CustomerSigned';
    materials?: Material[];
}

// Change Order interface
export interface ChangeOrder {
    id: number;
    jobId: number;
    description: string;
    additionalCost: number;
    status: 'PendingSignature' | 'Signed';
    customerSignedAt?: string;
}

// Checklist Item interface
export interface ChecklistItem {
    id: string;
    jobId: number;
    label: string;
    done: boolean;
}

// Job interface
export interface Job {
    id: number;
    status: JobStatus;
    type: JobType;
    propertyAddress: string;
    city: string;
    customerName: string;
    customerEmail: string;
    fmId?: number;
    assignedContractorId?: number;
    estimateId?: number;
    customerSigned: boolean;
    hasChangeOrder: boolean;
    disputeId?: number;
    gateCode?: string;
    scheduledTime?: string;
    latitude?: number;
    longitude?: number;
    trade?: string;
    checklistCompleted: boolean;
    beforePhotos: number;
    afterPhotos: number;
    receiptsUploaded: number;
    magicToken?: string;
    materials?: Material[];
    materialStatus?: MaterialStatus;
    visitStatus?: VisitStatus;
    mandatorySiteVisit?: boolean;
    measurements?: {
        display: string; // Structured JSON string or verified text
        verified?: boolean;
    };
    toolsRequired?: string[];
    laborRequired?: number;
    estimatedTime?: number;
    safetyConcerns?: string;
    scopeConfirmed?: boolean;
    beforePhotosUploaded?: boolean;
    isProject?: boolean;
    projectId?: number;
    projectModeApproved?: boolean;
}

// FM Visit Note interface
export interface FMVisitNote {
    id: string;
    jobId: number;
    author: string;
    text: string;
    timestamp: string;
}

// Dispute interface
export interface Dispute {
    id: number;
    jobId: number;
    raisedByRole: 'customer' | 'fm' | 'contractor';
    title: string;
    description: string;
    severity: 'minor' | 'medium' | 'severe';
    status: 'Open' | 'Resolved' | 'Refunded';
    createdAt: string;
    resolution?: string;
    createdBy?: string;
    createdDate?: string;
    messages?: DisputeMessage[];
}

// Dispute Message interface
export interface DisputeMessage {
    id: string;
    disputeId: number;
    senderRole: UserRole | 'customer';
    text: string;
    timestamp: string;
}

// Contractor Payout interface
export interface ContractorPayout {
    id: number;
    contractorId: number;
    jobId: number;
    jobType: JobType;
    amount: number;
    materialReimbursed: number;
    status: 'Processing' | 'Paid' | 'Declined';
    paymentDate?: string;
}

// Contractor Compliance interface
export interface ContractorCompliance {
    contractorId: number;
    w9Uploaded: boolean;
    insuranceUploaded: boolean;
    insuranceExpiryDate: string;
    independentAgreementSigned: boolean;
    liabilityWaiverSigned: boolean;
    paymentTermsSigned: boolean;
    complianceStatus: ComplianceStatus;
}

// Ledger Entry interface
export interface LedgerEntry {
    id: number;
    date: string;
    jobId: number;
    city: string;
    jobType: JobType;
    deposit: number;
    laborPayout: number;
    materialCost: number;
    platformFees: number;
    refunds: number;
    chargebacks: number;
    netProfit: number;
    investorSplit: number;
}

// Investor interface
export interface Investor {
    id: number;
    name: string;
    splitPercent: number;
    totalRevenue: number;
    totalPayouts: number;
    balanceDue: number;
}

// Investor Job Breakdown
export interface InvestorJobBreakdown {
    investorId: number;
    jobId: number;
    revenue: number;
    expenses: number;
    platformFee: number;
    investorShare: number;
    roi?: number;
    profitSplit?: {
        apex: number;
        investor: number;
    };
}

// Contractor Stats
export interface ContractorStats {
    contractorId: number;
    completedJobsCount: number;
    pendingPayoutTotal: number;
}

// Deposit
export interface Deposit {
    id: number;
    jobId: number;
    amount: number;
    status: 'Pending' | 'Paid';
    paidAt?: string;
}

// Quote Line Item
export interface QuoteLineItem {
    id: string;
    jobId: number;
    label: string;
    qty: number;
    unitPrice: number;
    total: number;
}

// Project interface
export interface Project {
    id: number;
    name: string;
    description: string;
    propertyAddress: string;
    city: string;
    status: ProjectStatus;
    trades: string[];
    subtasks: ProjectSubtask[];
    adminApproved: boolean;
    createdAt: string;
}


// Project Subtask interface
export interface ProjectSubtask {
    id: string;
    projectId: number;
    trade: string;
    jobId?: number;
    status: SubtaskStatus;
    estimatedTime: number;
    materialsVerified: boolean;
}

// Lead interface
export interface Lead {
    id: number;
    name: string;
    stage: 'New' | 'Contacted' | 'Proposal Sent' | 'Won' | 'Lost';
    property: string;
    date: string;
    phone?: string;
    email?: string;
    source: 'Manual' | 'Angi' | 'Referral';
}
