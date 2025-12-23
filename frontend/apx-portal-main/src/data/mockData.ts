import type {
    User,
    Job,
    Estimate,
    ChangeOrder,
    FMVisitNote,
    Dispute,
    DisputeMessage,
    ContractorPayout,
    ContractorCompliance,
    LedgerEntry,
    Investor,
    InvestorJobBreakdown,
    ContractorStats,
    Deposit,
    QuoteLineItem,
    ChecklistItem,
    Material,
    MaterialDelivery,
    Project,
    Lead,
} from '@/types';

// ==================== MUTABLE DATA STORES ====================
console.log('mockData module evaluating...');

// Projects
export const projects: Project[] = [
    {
        id: 1,
        name: 'Cleveland Multi-Unit Renovation',
        description: 'Full renovation of 3 units at Pine Rd complex.',
        propertyAddress: '789 Pine Rd, Cleveland OH',
        city: 'Cleveland',
        status: 'Setup',
        trades: ['painting', 'flooring', 'electrical'],
        subtasks: [
            {
                id: 'pt1',
                projectId: 1,
                trade: 'painting',
                jobId: 102,
                status: 'NotStarted',
                estimatedTime: 12,
                materialsVerified: false,
            },
            {
                id: 'pt2',
                projectId: 1,
                trade: 'flooring',
                jobId: 105,
                status: 'Blocked', // Waiting on materials
                estimatedTime: 16,
                materialsVerified: false,
            }
        ],
        adminApproved: false,
        createdAt: '2025-12-01T09:00:00',
    }
];

// Users
export const users: User[] = [
    {
        id: 1,
        name: 'Alice Admin',
        email: 'alice@apex.com',
        role: 'admin',
        complianceStatus: 'active',
        avatarUrl: 'https://i.pravatar.cc/150?u=alice',
    },
    {
        id: 2,
        name: 'Frank FM',
        email: 'frank@apex.com',
        role: 'fm',
        complianceStatus: 'active',
        avatarUrl: 'https://i.pravatar.cc/150?u=frank',
    },
    {
        id: 3,
        name: 'Cory Contractor',
        email: 'cory@apex.com',
        role: 'contractor',
        trade: 'painting',
        complianceStatus: 'active',
        avatarUrl: 'https://i.pravatar.cc/150?u=cory',
        insuranceExpiryDate: '2026-01-10',
    },
    {
        id: 4,
        name: 'Dave Drywaller',
        email: 'dave@apex.com',
        role: 'contractor',
        trade: 'drywall',
        complianceStatus: 'blocked',
        avatarUrl: 'https://i.pravatar.cc/150?u=dave',
        insuranceExpiryDate: '2025-11-01',
    },
    {
        id: 5,
        name: 'Irene Investor',
        email: 'irene@apex.com',
        role: 'investor',
        complianceStatus: 'active',
        avatarUrl: 'https://i.pravatar.cc/150?u=irene',
    },
    {
        id: 6,
        name: 'John Doe (Customer)',
        email: 'customer@apex.com',
        role: 'customer',
        complianceStatus: 'active',
        avatarUrl: 'https://i.pravatar.cc/150?u=john',
    }
];

// Jobs
export const jobs: Job[] = [
    {
        id: 101,
        status: 'Estimate',
        type: 'handyman',
        propertyAddress: '123 Elm St, Detroit MI',
        city: 'Detroit',
        customerName: 'John Doe',
        customerEmail: 'customer@apex.com',
        fmId: 2,
        assignedContractorId: undefined,
        estimateId: 201,
        customerSigned: false,
        hasChangeOrder: false,
        disputeId: undefined,
        gateCode: '#1234',
        scheduledTime: '2025-12-10T10:00:00',
        latitude: 42.3314,
        longitude: -83.0458,
        trade: 'handyman',
        checklistCompleted: false,
        beforePhotos: 0,
        afterPhotos: 0,
        receiptsUploaded: 0,
        magicToken: 'mock-token-123',
        materialStatus: 'AI Generated',
        visitStatus: 'ToVisit',
        mandatorySiteVisit: true,
        isProject: false,
    },
    {
        id: 102,
        status: 'Open',
        type: 'handyman',
        propertyAddress: '789 Pine Rd, Cleveland OH',
        city: 'Cleveland',
        customerName: 'Mike Ross',
        customerEmail: 'mike@example.com',
        fmId: 2,
        assignedContractorId: undefined,
        estimateId: 202,
        customerSigned: true,
        hasChangeOrder: false,
        disputeId: undefined,
        scheduledTime: '2025-12-10T14:00:00',
        latitude: 41.4993,
        longitude: -81.6944,
        trade: 'painting',
        checklistCompleted: false,
        beforePhotos: 0,
        afterPhotos: 0,
        receiptsUploaded: 0,
        magicToken: 'demo-token-102',
        materialStatus: 'FM Verified',
        visitStatus: 'Completed',
        mandatorySiteVisit: true,
        isProject: false,
    },
    {
        id: 103,
        status: 'InProgress',
        type: 'handyman',
        propertyAddress: '456 Oak Ave, Detroit MI',
        city: 'Detroit',
        customerName: 'Sarah Smith',
        customerEmail: 'sarah@example.com',
        fmId: 2,
        assignedContractorId: 3,
        estimateId: 203,
        customerSigned: true,
        hasChangeOrder: false,
        disputeId: undefined,
        gateCode: '#5678',
        scheduledTime: '2025-12-09T09:00:00',
        latitude: 42.3500,
        longitude: -83.0500,
        trade: 'painting',
        checklistCompleted: false,
        beforePhotos: 2,
        afterPhotos: 0,
        receiptsUploaded: 1,
        magicToken: 'demo-token-103',
        materialStatus: 'FM Verified',
        visitStatus: 'Completed',
        mandatorySiteVisit: false,
        isProject: false,
    },
    {
        id: 104,
        status: 'Complete',
        type: 'investor',
        propertyAddress: '321 Maple Dr, Cleveland OH',
        city: 'Cleveland',
        customerName: 'Investor Property',
        customerEmail: 'investor@example.com',
        fmId: 2,
        assignedContractorId: 3,
        estimateId: 204,
        customerSigned: true,
        hasChangeOrder: true,
        disputeId: undefined,
        scheduledTime: '2025-12-08T11:00:00',
        latitude: 41.5000,
        longitude: -81.7000,
        trade: 'painting',
        checklistCompleted: true,
        beforePhotos: 3,
        afterPhotos: 3,
        receiptsUploaded: 2,
        magicToken: 'demo-token-104',
        materialStatus: 'FM Verified',
        visitStatus: 'Completed',
        mandatorySiteVisit: true,
        isProject: true,
    },
    // --- NEW MOCK DATA START ---
    // Active Jobs (Open/InProgress)
    {
        id: 110,
        status: 'Open',
        type: 'investor',
        propertyAddress: '5501 Broadway Ave, Cleveland OH',
        city: 'Cleveland',
        customerName: 'Inv. LLC',
        customerEmail: 'inv.llc@example.com',
        fmId: 2,
        magicToken: 't-110',
        trade: 'flooring',
        isProject: true,
        scheduledTime: '2025-12-20T09:00:00',
        mandatorySiteVisit: true,
        materialStatus: 'AI Generated',
        customerSigned: true,
        hasChangeOrder: false,
        checklistCompleted: false,
        beforePhotos: 0,
        afterPhotos: 0,
        receiptsUploaded: 0
    },
    {
        id: 111,
        status: 'InProgress',
        type: 'investor',
        propertyAddress: '1290 W 117th St, Cleveland OH',
        city: 'Cleveland',
        customerName: 'Inv. LLC',
        customerEmail: 'inv.llc@example.com',
        fmId: 2,
        magicToken: 't-111',
        trade: 'drywall',
        isProject: true,
        scheduledTime: '2025-12-18T08:00:00',
        mandatorySiteVisit: true,
        materialStatus: 'FM Verified',
        customerSigned: true,
        hasChangeOrder: false,
        checklistCompleted: false,
        beforePhotos: 2,
        afterPhotos: 0,
        receiptsUploaded: 0
    },
    {
        id: 112,
        status: 'InProgress',
        type: 'investor',
        propertyAddress: '880 E 185th St, Cleveland OH',
        city: 'Cleveland',
        customerName: 'Inv. LLC',
        customerEmail: 'inv.llc@example.com',
        fmId: 2,
        magicToken: 't-112',
        trade: 'painting',
        isProject: true,
        scheduledTime: '2025-12-19T10:00:00',
        mandatorySiteVisit: true,
        materialStatus: 'FM Verified',
        customerSigned: true,
        hasChangeOrder: false,
        checklistCompleted: false,
        beforePhotos: 1,
        afterPhotos: 0,
        receiptsUploaded: 0
    },
    {
        id: 113,
        status: 'Open',
        type: 'investor',
        propertyAddress: '3300 Warren Rd, Cleveland OH',
        city: 'Cleveland',
        customerName: 'Inv. LLC',
        customerEmail: 'inv.llc@example.com',
        fmId: 2,
        magicToken: 't-113',
        trade: 'plumbing',
        isProject: true,
        scheduledTime: '2025-12-21T13:00:00',
        mandatorySiteVisit: true,
        materialStatus: 'AI Generated',
        customerSigned: true,
        hasChangeOrder: false,
        checklistCompleted: false,
        beforePhotos: 0,
        afterPhotos: 0,
        receiptsUploaded: 0
    },
    {
        id: 114,
        status: 'InProgress',
        type: 'investor',
        propertyAddress: '2100 Superior Ave, Cleveland OH',
        city: 'Cleveland',
        customerName: 'Inv. LLC',
        customerEmail: 'inv.llc@example.com',
        fmId: 2,
        magicToken: 't-114',
        trade: 'electrical',
        isProject: true,
        scheduledTime: '2025-12-17T11:00:00',
        mandatorySiteVisit: true,
        materialStatus: 'FM Verified',
        customerSigned: true,
        hasChangeOrder: false,
        checklistCompleted: false,
        beforePhotos: 3,
        afterPhotos: 0,
        receiptsUploaded: 1
    },

    // Closed Jobs (Complete/Paid)
    {
        id: 115,
        status: 'Complete',
        type: 'investor',
        propertyAddress: '1500 Detroit Ave, Cleveland OH',
        city: 'Cleveland',
        customerName: 'Inv. LLC',
        customerEmail: 'inv.llc@example.com',
        fmId: 2,
        magicToken: 't-115',
        trade: 'roofing',
        isProject: true,
        scheduledTime: '2025-11-15T09:00:00',
        mandatorySiteVisit: true,
        materialStatus: 'FM Verified',
        customerSigned: true,
        hasChangeOrder: false,
        checklistCompleted: true,
        beforePhotos: 5,
        afterPhotos: 5,
        receiptsUploaded: 2
    },
    {
        id: 116,
        status: 'Paid',
        type: 'investor',
        propertyAddress: '4400 Pearl Rd, Cleveland OH',
        city: 'Cleveland',
        customerName: 'Inv. LLC',
        customerEmail: 'inv.llc@example.com',
        fmId: 2,
        magicToken: 't-116',
        trade: 'hvac',
        isProject: true,
        scheduledTime: '2025-10-10T09:00:00',
        mandatorySiteVisit: true,
        materialStatus: 'FM Verified',
        customerSigned: true,
        hasChangeOrder: false,
        checklistCompleted: true,
        beforePhotos: 4,
        afterPhotos: 4,
        receiptsUploaded: 3
    },
    {
        id: 117,
        status: 'Paid',
        type: 'investor',
        propertyAddress: '7800 Carnegie Ave, Cleveland OH',
        city: 'Cleveland',
        customerName: 'Inv. LLC',
        customerEmail: 'inv.llc@example.com',
        fmId: 2,
        magicToken: 't-117',
        trade: 'landscaping',
        isProject: true,
        scheduledTime: '2025-09-05T09:00:00',
        mandatorySiteVisit: true,
        materialStatus: 'FM Verified',
        customerSigned: true,
        hasChangeOrder: false,
        checklistCompleted: true,
        beforePhotos: 2,
        afterPhotos: 2,
        receiptsUploaded: 1
    },
    {
        id: 118,
        status: 'Paid',
        type: 'investor',
        propertyAddress: '2200 Euclid Ave, Cleveland OH',
        city: 'Cleveland',
        customerName: 'Inv. LLC',
        customerEmail: 'inv.llc@example.com',
        fmId: 2,
        magicToken: 't-118',
        trade: 'painting',
        isProject: true,
        scheduledTime: '2025-08-20T09:00:00',
        mandatorySiteVisit: true,
        materialStatus: 'FM Verified',
        customerSigned: true,
        hasChangeOrder: false,
        checklistCompleted: true,
        beforePhotos: 3,
        afterPhotos: 3,
        receiptsUploaded: 2
    },
    {
        id: 119,
        status: 'Complete',
        type: 'investor',
        propertyAddress: '5000 Lorain Ave, Cleveland OH',
        city: 'Cleveland',
        customerName: 'Inv. LLC',
        customerEmail: 'inv.llc@example.com',
        fmId: 2,
        magicToken: 't-119',
        trade: 'canpentry',
        isProject: true,
        scheduledTime: '2025-11-25T09:00:00',
        mandatorySiteVisit: true,
        materialStatus: 'FM Verified',
        customerSigned: true,
        hasChangeOrder: true,
        checklistCompleted: true,
        beforePhotos: 4,
        afterPhotos: 4,
        receiptsUploaded: 2
    },

    // More Active
    {
        id: 120,
        status: 'Open',
        type: 'investor',
        propertyAddress: '9900 St Clair Ave, Cleveland OH',
        city: 'Cleveland',
        customerName: 'Inv. LLC',
        customerEmail: 'inv.llc@example.com',
        fmId: 2,
        magicToken: 't-120',
        trade: 'flooring',
        isProject: true,
        scheduledTime: '2025-12-22T09:00:00',
        mandatorySiteVisit: true,
        materialStatus: 'AI Generated',
        customerSigned: true,
        hasChangeOrder: false,
        checklistCompleted: false,
        beforePhotos: 0,
        afterPhotos: 0,
        receiptsUploaded: 0
    },
    {
        id: 121,
        status: 'InProgress',
        type: 'investor',
        propertyAddress: '1501 W 25th St, Cleveland OH',
        city: 'Cleveland',
        customerName: 'Inv. LLC',
        customerEmail: 'inv.llc@example.com',
        fmId: 2,
        magicToken: 't-121',
        trade: 'drywall',
        isProject: true,
        scheduledTime: '2025-12-16T15:00:00',
        mandatorySiteVisit: true,
        materialStatus: 'FM Verified',
        customerSigned: true,
        hasChangeOrder: false,
        checklistCompleted: false,
        beforePhotos: 1,
        afterPhotos: 0,
        receiptsUploaded: 0
    },

    // More history
    {
        id: 122,
        status: 'Paid',
        type: 'investor',
        propertyAddress: '3000 W 14th St, Cleveland OH',
        city: 'Cleveland',
        customerName: 'Inv. LLC',
        customerEmail: 'inv.llc@example.com',
        fmId: 2,
        magicToken: 't-122',
        trade: 'painting',
        isProject: true,
        scheduledTime: '2025-07-15T09:00:00',
        mandatorySiteVisit: true,
        materialStatus: 'FM Verified',
        customerSigned: true,
        hasChangeOrder: false,
        checklistCompleted: true,
        beforePhotos: 5,
        afterPhotos: 5,
        receiptsUploaded: 3
    },
    {
        id: 123,
        status: 'Paid',
        type: 'investor',
        propertyAddress: '2500 E 9th St, Cleveland OH',
        city: 'Cleveland',
        customerName: 'Inv. LLC',
        customerEmail: 'inv.llc@example.com',
        fmId: 2,
        magicToken: 't-123',
        trade: 'electrical',
        isProject: true,
        scheduledTime: '2025-06-10T09:00:00',
        mandatorySiteVisit: true,
        materialStatus: 'FM Verified',
        customerSigned: true,
        hasChangeOrder: false,
        checklistCompleted: true,
        beforePhotos: 4,
        afterPhotos: 4,
        receiptsUploaded: 2
    },
];

// Estimates
export const estimates: Estimate[] = [
    {
        id: 201,
        jobId: 101,
        trade: 'drywall',
        hours: 4,
        materialEstimate: 120,
        laborRate: 75,
        scopeOfWork: 'Patch and paint hallway walls.',
        price: 420,
        status: 'Draft',
    },
    {
        id: 202,
        jobId: 102,
        trade: 'painting',
        hours: 6,
        materialEstimate: 200,
        laborRate: 65,
        scopeOfWork: 'Paint two bedrooms and living room.',
        price: 590,
        status: 'CustomerSigned',
    },
    {
        id: 203,
        jobId: 103,
        trade: 'painting',
        hours: 5,
        materialEstimate: 150,
        laborRate: 65,
        scopeOfWork: 'Paint kitchen and dining area.',
        price: 475,
        status: 'CustomerSigned',
    },
    {
        id: 204,
        jobId: 104,
        trade: 'painting',
        hours: 8,
        materialEstimate: 300,
        laborRate: 65,
        scopeOfWork: 'Full interior repaint of 3-bedroom property.',
        price: 820,
        status: 'CustomerSigned',
    },
];

// Change Orders
export const changeOrders: ChangeOrder[] = [
    {
        id: 301,
        jobId: 104,
        description: 'Added ceiling repaint in hallway.',
        additionalCost: 150,
        status: 'Signed',
        customerSignedAt: '2025-12-08T15:30:00',
    },
];

// FM Visit Notes
export const fmVisitNotes: FMVisitNote[] = [
    {
        id: 'n1',
        jobId: 101,
        author: 'Frank FM',
        text: 'Found minor drywall cracks in hallway.',
        timestamp: '2025-12-09T09:15:00',
    },
    {
        id: 'n2',
        jobId: 102,
        author: 'Frank FM',
        text: 'Customer wants premium paint finish.',
        timestamp: '2025-12-09T14:20:00',
    },
];

// Disputes
export const disputes: Dispute[] = [
    {
        id: 501,
        jobId: 103,
        raisedByRole: 'contractor',
        title: 'Found unexpected mold behind wall',
        description: 'Discovered mold; need new scope.',
        severity: 'severe',
        status: 'Open',
        createdAt: '2025-12-09T16:00:00',
    },
];

// Dispute Messages
export const disputeMessages: DisputeMessage[] = [
    {
        id: 'm1',
        disputeId: 501,
        senderRole: 'contractor',
        text: 'Paint color does not match the approved sample.',
        timestamp: '2025-12-09T12:30:00',
    },
];

// Contractor Payouts
export const contractorPayouts: ContractorPayout[] = [
    {
        id: 601,
        contractorId: 3,
        jobId: 104,
        jobType: 'investor',
        amount: 520,
        materialReimbursed: 120,
        status: 'Processing',
        paymentDate: undefined,
    },
];

// Contractor Compliance
export const contractorCompliance: ContractorCompliance[] = [
    {
        contractorId: 3,
        w9Uploaded: true,
        insuranceUploaded: true,
        insuranceExpiryDate: '2026-01-10',
        independentAgreementSigned: true,
        liabilityWaiverSigned: true,
        paymentTermsSigned: true,
        complianceStatus: 'active',
    },
    {
        contractorId: 4,
        w9Uploaded: true,
        insuranceUploaded: true,
        insuranceExpiryDate: '2025-11-01',
        independentAgreementSigned: true,
        liabilityWaiverSigned: true,
        paymentTermsSigned: false,
        complianceStatus: 'blocked',
    },
];

// Ledger Entries
export const ledgerEntries: LedgerEntry[] = [
    {
        id: 801,
        date: '2025-12-01',
        jobId: 104,
        city: 'Cleveland',
        jobType: 'investor',
        deposit: 200,
        laborPayout: 520,
        materialCost: 120,
        platformFees: 80,
        refunds: 0,
        chargebacks: 0,
        netProfit: -520,
        investorSplit: 150,
    },
];

// Investors
export const investors: Investor[] = [
    {
        id: 901,
        name: 'Irene Investor',
        splitPercent: 25,
        totalRevenue: 20000,
        totalPayouts: 5000,
        balanceDue: 1000,
    },
];

// Investor Job Breakdown
export const investorJobBreakdown: InvestorJobBreakdown[] = [
    {
        investorId: 901,
        jobId: 104,
        revenue: 820,
        expenses: 620,
        platformFee: 80,
        investorShare: 50,
        roi: 8.5, // 8.5%
        profitSplit: { apex: 30, investor: 70 }
    },
    {
        investorId: 901,
        jobId: 101, // Linking another job for demo
        revenue: 1200,
        expenses: 800,
        platformFee: 120,
        investorShare: 200,
        roi: 12.0,
        profitSplit: { apex: 30, investor: 70 }
    },
    // --- NEW BREAKDOWNS ---
    { investorId: 901, jobId: 110, revenue: 2500, expenses: 1800, platformFee: 250, investorShare: 450, roi: 25.0, profitSplit: { apex: 30, investor: 70 } },
    { investorId: 901, jobId: 111, revenue: 1500, expenses: 900, platformFee: 150, investorShare: 450, roi: 50.0, profitSplit: { apex: 30, investor: 70 } },
    { investorId: 901, jobId: 112, revenue: 3200, expenses: 2200, platformFee: 320, investorShare: 680, roi: 30.9, profitSplit: { apex: 30, investor: 70 } },
    { investorId: 901, jobId: 113, revenue: 950, expenses: 500, platformFee: 95, investorShare: 355, roi: 71.0, profitSplit: { apex: 30, investor: 70 } },
    { investorId: 901, jobId: 114, revenue: 4100, expenses: 3100, platformFee: 410, investorShare: 590, roi: 19.0, profitSplit: { apex: 30, investor: 70 } },
    { investorId: 901, jobId: 115, revenue: 5600, expenses: 4000, platformFee: 560, investorShare: 1040, roi: 26.0, profitSplit: { apex: 30, investor: 70 } },
    { investorId: 901, jobId: 116, revenue: 2800, expenses: 1900, platformFee: 280, investorShare: 620, roi: 32.6, profitSplit: { apex: 30, investor: 70 } },
    { investorId: 901, jobId: 117, revenue: 1200, expenses: 700, platformFee: 120, investorShare: 380, roi: 54.2, profitSplit: { apex: 30, investor: 70 } },
    { investorId: 901, jobId: 118, revenue: 1850, expenses: 1200, platformFee: 185, investorShare: 465, roi: 38.7, profitSplit: { apex: 30, investor: 70 } },
    { investorId: 901, jobId: 119, revenue: 3300, expenses: 2400, platformFee: 330, investorShare: 570, roi: 23.7, profitSplit: { apex: 30, investor: 70 } },
    { investorId: 901, jobId: 120, revenue: 2100, expenses: 1500, platformFee: 210, investorShare: 390, roi: 26.0, profitSplit: { apex: 30, investor: 70 } },
    { investorId: 901, jobId: 121, revenue: 1400, expenses: 950, platformFee: 140, investorShare: 310, roi: 32.6, profitSplit: { apex: 30, investor: 70 } },
    { investorId: 901, jobId: 122, revenue: 4500, expenses: 3200, platformFee: 450, investorShare: 850, roi: 26.5, profitSplit: { apex: 30, investor: 70 } },
    { investorId: 901, jobId: 123, revenue: 2900, expenses: 2000, platformFee: 290, investorShare: 610, roi: 30.5, profitSplit: { apex: 30, investor: 70 } },
];

// Platform Stats
export const stats = [
    { label: 'Total Revenue', value: '$45,231.89', change: '+20.1%', icon: 'DollarSign' },
    { label: 'Active Jobs', value: '12', change: '+2', icon: 'Briefcase' },
    { label: 'Pending Payouts', value: '$12,234', change: '+15%', icon: 'TrendingUp' },
    { label: 'Contractors', value: '8', change: '+1', icon: 'Users' }
];

// Contractor Stats
export const contractorStats: ContractorStats[] = [
    {
        contractorId: 3,
        completedJobsCount: 12,
        pendingPayoutTotal: 1850,
    },
];

// Deposits
export const deposits: Deposit[] = [
    {
        id: 401,
        jobId: 101,
        amount: 150,
        status: 'Pending',
        paidAt: undefined,
    },
    {
        id: 402,
        jobId: 102,
        amount: 200,
        status: 'Paid',
        paidAt: '2025-12-09T10:00:00',
    },
];

// Quote Line Items
export const quoteLineItems: QuoteLineItem[] = [
    {
        id: 'li1',
        jobId: 101,
        label: 'Drywall Patch',
        qty: 1,
        unitPrice: 300,
        total: 300,
    },
];

// Leads (Mutable)
export const leads: Lead[] = [
    { id: 1, name: 'Alice Johnson', stage: 'New', property: '456 Elm St', date: '2025-12-15', source: 'Manual' },
    { id: 2, name: 'Bob Williams', stage: 'Contacted', property: '789 Oak Ave', date: '2025-12-14', source: 'Angi' },
    { id: 3, name: 'Charlie Brown', stage: 'Proposal Sent', property: '321 Pine Ln', date: '2025-12-10', source: 'Referral' },
];

export const addLead = (lead: Omit<Lead, 'id' | 'date'>) => {
    const newLead: Lead = {
        ...lead,
        id: Math.max(...leads.map(l => l.id), 0) + 1,
        date: new Date().toISOString().split('T')[0],
    };
    leads.unshift(newLead);
    return newLead;
};



// Materials
export const materials: Material[] = [
    {
        id: 'mat1',
        name: 'Premium White Paint',
        sku: 'PWP-2024',
        quantity: 3,
        supplier: 'Home Depot',
        priceRange: '$45-55',
        status: 'AI Generated',
        deliveryStatus: 'Ordered',
    },
    {
        id: 'mat2',
        name: 'Drywall Compound',
        sku: 'DWC-500',
        quantity: 2,
        supplier: "Lowe's",
        priceRange: '$20-25',
        status: 'FM Verified',
        deliveryStatus: 'Delivered',
    },
];

// Material Deliveries
export const materialDeliveries: MaterialDelivery[] = [
    {
        id: 'md1',
        jobId: 101,
        materials: materials.slice(0, 2),
        status: 'Delivered',
        photos: ['/demo-delivery-photo.jpg'],
        gpsLocation: {
            latitude: 42.3314,
            longitude: -83.0458,
        },
        deliveredAt: '2025-12-09T08:00:00',
    },
];

// Checklist Items
export const checklistItems: ChecklistItem[] = [
    {
        id: 'c1',
        jobId: 103,
        label: 'Inspect walls',
        done: true,
    },
    {
        id: 'c2',
        jobId: 103,
        label: 'Prep surfaces',
        done: true,
    },
    {
        id: 'c3',
        jobId: 103,
        label: 'Apply primer',
        done: false,
    },
    {
        id: 'c4',
        jobId: 103,
        label: 'Apply finish coat',
        done: false,
    },
];

// Contractors (alias for contractor users)
export const contractors = users.filter(u => u.role === 'contractor').map(u => ({
    id: u.id,
    name: u.name,
    email: u.email,
    trade: u.trade || '',
    complianceStatus: u.complianceStatus || 'blocked',
    hasW9: true,
    insuranceCert: true,
    signedAgreement: true,
    insuranceExpiry: u.insuranceExpiryDate,
}));

// Material Orders (for ledger/accounting)
export const materialOrders = [
    {
        id: 1,
        jobId: 103,
        orderDate: '2025-12-08',
        totalCost: 150,
        status: 'Delivered',
    },
    {
        id: 2,
        jobId: 104,
        orderDate: '2025-12-07',
        totalCost: 300,
        status: 'Delivered',
    },
];

// ==================== MUTATION FUNCTIONS ====================

export function updateJobStatus(jobId: number, newStatus: Job['status']) {
    const job = jobs.find((j) => j.id === jobId);
    if (job) {
        job.status = newStatus;
    }
}

export function assignContractorToJob(jobId: number, contractorId: number) {
    const job = jobs.find((j) => j.id === jobId);
    if (job) {
        job.assignedContractorId = contractorId;
        job.status = 'InProgress';
    }
}

export function updateJobMaterialStatus(
    jobId: number,
    materialStatus: Job['materialStatus']
) {
    const job = jobs.find((j) => j.id === jobId);
    if (job) {
        job.materialStatus = materialStatus;
    }
}

export function createDispute(
    jobId: number,
    raisedByRole: 'customer' | 'fm' | 'contractor',
    title: string,
    description: string
): Dispute {
    // Simple severity calculation
    let severity: 'minor' | 'medium' | 'severe' = 'minor';
    if (description.toLowerCase().includes('mold') || description.toLowerCase().includes('refund')) {
        severity = 'severe';
    } else if (description.toLowerCase().includes('damage') || description.toLowerCase().includes('wrong')) {
        severity = 'medium';
    }

    const newDispute: Dispute = {
        id: disputes.length + 501,
        jobId,
        raisedByRole,
        title,
        description,
        severity,
        status: 'Open',
        createdAt: new Date().toISOString(),
    };

    disputes.push(newDispute);

    // Link dispute to job
    const job = jobs.find((j) => j.id === jobId);
    if (job) {
        job.disputeId = newDispute.id;
    }

    return newDispute;
}

export function processPayout(payoutId: number) {
    const payout = contractorPayouts.find((p) => p.id === payoutId);
    if (payout) {
        payout.status = 'Paid';
        payout.paymentDate = new Date().toISOString();

        // Update job status to Paid
        const job = jobs.find((j) => j.id === payout.jobId);
        if (job) {
            job.status = 'Paid';
        }

        // Add ledger entry if it doesn't exist
        const existingLedgerEntry = ledgerEntries.find((l) => l.jobId === payout.jobId);
        if (!existingLedgerEntry) {
            ledgerEntries.push({
                id: ledgerEntries.length + 801,
                date: new Date().toISOString().split('T')[0],
                jobId: payout.jobId,
                city: jobs.find((j) => j.id === payout.jobId)?.city || '',
                jobType: payout.jobType,
                deposit: 0,
                laborPayout: payout.amount,
                materialCost: payout.materialReimbursed,
                platformFees: 0,
                refunds: 0,
                chargebacks: 0,
                netProfit: -(payout.amount + payout.materialReimbursed),
                investorSplit: 0,
            });
        }
    }
}

export function updateContractorCompliance(
    contractorId: number,
    updates: Partial<ContractorCompliance>
) {
    const compliance = contractorCompliance.find((c) => c.contractorId === contractorId);
    if (compliance) {
        Object.assign(compliance, updates);

        // Auto-calculate compliance status
        const today = new Date();
        const expiryDate = new Date(compliance.insuranceExpiryDate);

        if (
            expiryDate < today ||
            !compliance.independentAgreementSigned ||
            !compliance.liabilityWaiverSigned ||
            !compliance.paymentTermsSigned
        ) {
            compliance.complianceStatus = 'blocked';
        } else {
            compliance.complianceStatus = 'active';
        }

        // Update user compliance status
        const user = users.find((u) => u.id === contractorId);
        if (user) {
            user.complianceStatus = compliance.complianceStatus;
        }
    }
}

export function updateDepositStatus(jobId: number, status: 'Pending' | 'Paid') {
    const deposit = deposits.find((d) => d.jobId === jobId);
    if (deposit) {
        deposit.status = status;
        if (status === 'Paid') {
            deposit.paidAt = new Date().toISOString();

            // Update job status to Open
            const job = jobs.find((j) => j.id === jobId);
            if (job) {
                job.status = 'Open';
            }
        }
    }
}

export function addFMNote(jobId: number, author: string, text: string) {
    const newNote: FMVisitNote = {
        id: `n${fmVisitNotes.length + 1}`,
        jobId,
        author,
        text,
        timestamp: new Date().toISOString(),
    };
    fmVisitNotes.push(newNote);
}

export function updateMaterialDeliveryStatus(
    jobId: number,
    status: MaterialDelivery['status'],
    photos: string[] = [],
    gpsLocation?: { latitude: number; longitude: number }
) {
    const delivery = materialDeliveries.find((d) => d.jobId === jobId);
    if (delivery) {
        delivery.status = status;
        delivery.photos = [...delivery.photos, ...photos];
        if (gpsLocation) {
            delivery.gpsLocation = gpsLocation;
        }
        delivery.deliveredAt = new Date().toISOString();
    }
}

export function updateChecklistItem(itemId: string, done: boolean) {
    const item = checklistItems.find((i) => i.id === itemId);
    if (item) {
        item.done = done;

        // Check if all items for this job are complete
        const jobItems = checklistItems.filter((i) => i.jobId === item.jobId);
        const allDone = jobItems.every((i) => i.done);

        // Update job checklistCompleted
        const job = jobs.find((j) => j.id === item.jobId);
        if (job) {
            job.checklistCompleted = allDone;
        }
    }
}

export function updateJobField(jobId: number, field: keyof Job, value: any) {
    const job = jobs.find((j) => j.id === jobId);
    if (job) {
        (job as any)[field] = value;
    }
}

export function getJobByToken(token: string): Job | undefined {
    return jobs.find((j) => j.magicToken === token);
}

export function getJobs(): Job[] {
    return jobs;
}

export function getUserByEmail(email: string): User | undefined {
    return users.find((u) => u.email === email);
}

export function getJobById(id: number): Job | undefined {
    return jobs.find((j) => j.id === id);
}

export function approvePayout(payoutId: number) {
    const payout = contractorPayouts.find((p) => p.id === payoutId);
    if (payout) {
        payout.status = 'Paid';
        payout.paymentDate = new Date().toISOString();
    }
}

export function declinePayout(payoutId: number) {
    const payout = contractorPayouts.find((p) => p.id === payoutId);
    if (payout) {
        payout.status = 'Declined';
    }
}

export function resolveDispute(disputeId: number, resolution: string) {
    const dispute = disputes.find((d) => d.id === disputeId);
    if (dispute) {
        dispute.status = 'Resolved';
        dispute.resolution = resolution;
    }
}

export function createEstimate(jobId: number, lineItems: Array<{
    description: string;
    category: string;
    quantity: number;
    rate: number;
    total: number;
}>) {
    // Calculate totals
    const materialEstimate = lineItems
        .filter(item => item.category === 'Material')
        .reduce((sum, item) => sum + item.total, 0);

    const laborHours = lineItems
        .filter(item => item.category === 'Labor')
        .reduce((sum, item) => sum + item.quantity, 0);

    const laborRate = laborHours > 0
        ? lineItems.filter(item => item.category === 'Labor')
            .reduce((sum, item) => sum + item.total, 0) / laborHours
        : 65;

    const totalPrice = lineItems.reduce((sum, item) => sum + item.total, 0);

    const job = jobs.find(j => j.id === jobId);
    const newEstimate = {
        id: estimates.length + 201,
        jobId,
        trade: job?.trade || 'handyman',
        hours: laborHours,
        materialEstimate,
        laborRate,
        scopeOfWork: lineItems.map(item => `${item.description} (${item.quantity} x ${item.rate})`).join('\n'),
        price: totalPrice,
        status: 'Draft' as const,
    };

    estimates.push(newEstimate);

    // Update job with estimate
    if (job) {
        job.estimateId = newEstimate.id;
    }

    return newEstimate;
}
