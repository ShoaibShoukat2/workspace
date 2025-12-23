# API Integration Implementation Guide

## Quick Start Checklist

- [x] Authentication API integrated
- [x] All API service files created
- [ ] Admin Dashboard integrated
- [ ] Contractor Dashboard integrated
- [ ] FM Dashboard integrated
- [ ] Investor Dashboard integrated
- [ ] Customer Dashboard integrated

---

## Admin Dashboard Integration

**File**: `src/pages/admin/AdminDashboard.tsx`

### Current Status
Uses mock data from `@/data/mockData`. Replace with API calls.

### Implementation Example

```typescript
import { useState, useEffect } from 'react';
import { adminApiService } from '@/lib/adminApi';

export default function AdminDashboard() {
    const [stats, setStats] = useState<AdminDashboardStats | null>(null);
    const [jobs, setJobs] = useState<JobData[]>([]);
    const [disputes, setDisputes] = useState<DisputeData[]>([]);
    const [payouts, setPayouts] = useState<PayoutData[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const [statsData, jobsData, disputesData, payoutsData] = await Promise.all([
                    adminApiService.getDashboardStats(),
                    adminApiService.getJobs({ limit: 5 }),
                    adminApiService.getDisputes({ status: 'Open' }),
                    adminApiService.getPayouts({ status: 'Processing' }),
                ]);

                setStats(statsData);
                setJobs(jobsData.results);
                setDisputes(disputesData.results);
                setPayouts(payoutsData.results);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load dashboard');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) return <div>Loading...</div>;
    if (error) return <div className="text-red-500">{error}</div>;

    return (
        <PortalLayout title="Admin Dashboard" navItems={navItems}>
            <div className="space-y-6">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <StatCard 
                        title="Active Jobs" 
                        value={stats?.total_active_jobs || 0}
                        icon={<Briefcase />}
                    />
                    <StatCard 
                        title="Pending Disputes" 
                        value={stats?.pending_disputes || 0}
                        icon={<AlertTriangle />}
                    />
                    <StatCard 
                        title="Pending Payouts" 
                        value={stats?.pending_payouts || 0}
                        icon={<DollarSign />}
                    />
                    <StatCard 
                        title="Total Revenue" 
                        value={formatCurrency(stats?.total_revenue || 0)}
                        icon={<TrendingUp />}
                    />
                </div>

                {/* Recent Jobs Table */}
                <Card>
                    <h3 className="text-lg font-semibold mb-4">Recent Jobs</h3>
                    <JobsTable jobs={jobs} />
                </Card>

                {/* Recent Disputes Table */}
                <Card>
                    <h3 className="text-lg font-semibold mb-4">Open Disputes</h3>
                    <DisputesTable disputes={disputes} />
                </Card>
            </div>
        </PortalLayout>
    );
}
```

### Key Methods to Use
- `adminApiService.getDashboardStats()` - Get dashboard overview
- `adminApiService.getJobs()` - Get job list with filtering
- `adminApiService.getDisputes()` - Get disputes
- `adminApiService.getPayouts()` - Get payouts for approval

---

## Contractor Dashboard Integration

**File**: `src/pages/contractor/ContractorDashboard.tsx`

### Current Status
Partially uses mock data. Needs API integration for real-time stats.

### Implementation Example

```typescript
import { useState, useEffect } from 'react';
import { contractorApiService } from '@/lib/contractorApi';

export default function ContractorDashboard() {
    const { currentUser } = useAuth();
    const [dashboard, setDashboard] = useState<ContractorDashboardData | null>(null);
    const [activeJobs, setActiveJobs] = useState<ContractorJob[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const [dashData, jobsData] = await Promise.all([
                    contractorApiService.getDashboard(),
                    contractorApiService.getActiveJobs(),
                ]);

                setDashboard(dashData);
                setActiveJobs(Array.isArray(jobsData) ? jobsData : jobsData.results);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load dashboard');
            } finally {
                setLoading(false);
            }
        };

        if (currentUser) {
            fetchData();
        }
    }, [currentUser]);

    if (loading) return <LoadingSpinner />;
    if (error) return <ErrorAlert message={error} />;

    return (
        <PortalLayout title="Contractor Dashboard" navItems={navItems}>
            <div className="space-y-6">
                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <StatCard 
                        title="Active Jobs" 
                        value={dashboard?.active_jobs_count || 0}
                    />
                    <StatCard 
                        title="Completed Jobs" 
                        value={dashboard?.completed_jobs_count || 0}
                    />
                    <StatCard 
                        title="Total Earnings" 
                        value={formatCurrency(dashboard?.total_earnings || 0)}
                    />
                </div>

                {/* Active Jobs */}
                <Card>
                    <h3 className="text-lg font-semibold mb-4">Active Jobs</h3>
                    {activeJobs.length > 0 ? (
                        <ActiveJobsList jobs={activeJobs} />
                    ) : (
                        <p className="text-gray-500">No active jobs</p>
                    )}
                </Card>
            </div>
        </PortalLayout>
    );
}
```

### Key Methods
- `contractorApiService.getDashboard()` - Dashboard stats
- `contractorApiService.getActiveJobs()` - List active jobs
- `contractorApiService.getAssignments()` - Get available jobs
- `contractorApiService.acceptJob(jobId)` - Accept assignment
- `contractorApiService.rejectJob(jobId)` - Reject assignment

---

## Contractor Job Board Integration

**File**: `src/pages/contractor/JobBoard.tsx`

### Implementation Example

```typescript
import { useState, useEffect } from 'react';
import { contractorApiService } from '@/lib/contractorApi';

export default function JobBoard() {
    const [assignments, setAssignments] = useState<JobAssignment[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchAssignments = async () => {
            try {
                setLoading(true);
                const data = await contractorApiService.getAssignments();
                setAssignments(Array.isArray(data) ? data : data.results);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load jobs');
            } finally {
                setLoading(false);
            }
        };

        fetchAssignments();
    }, []);

    const handleAcceptJob = async (jobId: number) => {
        try {
            await contractorApiService.acceptJob(jobId);
            setAssignments(assignments.filter(a => a.id !== jobId));
            // Show success toast
        } catch (err) {
            // Show error toast
        }
    };

    const handleRejectJob = async (jobId: number) => {
        try {
            await contractorApiService.rejectJob(jobId);
            setAssignments(assignments.filter(a => a.id !== jobId));
            // Show success toast
        } catch (err) {
            // Show error toast
        }
    };

    return (
        <PortalLayout title="Available Jobs" navItems={navItems}>
            {loading ? (
                <LoadingSpinner />
            ) : error ? (
                <ErrorAlert message={error} />
            ) : (
                <div className="space-y-4">
                    {assignments.map(assignment => (
                        <JobCard
                            key={assignment.id}
                            assignment={assignment}
                            onAccept={() => handleAcceptJob(assignment.id)}
                            onReject={() => handleRejectJob(assignment.id)}
                        />
                    ))}
                </div>
            )}
        </PortalLayout>
    );
}
```

---

## Contractor Wallet Integration

**File**: `src/pages/contractor/Wallet.tsx`

### Implementation Example

```typescript
import { useState, useEffect } from 'react';
import { contractorApiService } from '@/lib/contractorApi';

export default function Wallet() {
    const [wallet, setWallet] = useState<WalletData | null>(null);
    const [transactions, setTransactions] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [payoutAmount, setPayoutAmount] = useState('');

    useEffect(() => {
        const fetchWalletData = async () => {
            try {
                setLoading(true);
                const [walletData, transactionData] = await Promise.all([
                    contractorApiService.getWallet(),
                    contractorApiService.getWalletTransactions(20),
                ]);

                setWallet(walletData);
                setTransactions(transactionData);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load wallet');
            } finally {
                setLoading(false);
            }
        };

        fetchWalletData();
    }, []);

    const handleRequestPayout = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const amount = parseFloat(payoutAmount);
            if (!amount || amount <= 0) {
                throw new Error('Invalid amount');
            }
            if (amount > (wallet?.balance || 0)) {
                throw new Error('Insufficient balance');
            }

            await contractorApiService.requestPayout(amount);
            setPayoutAmount('');
            // Refresh wallet data
            const updatedWallet = await contractorApiService.getWallet();
            setWallet(updatedWallet);
            // Show success toast
        } catch (err) {
            // Show error toast
        }
    };

    return (
        <PortalLayout title="Wallet" navItems={navItems}>
            {loading ? <LoadingSpinner /> : error ? <ErrorAlert message={error} /> : (
                <div className="space-y-6">
                    {/* Balance Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <BalanceCard
                            title="Available Balance"
                            amount={wallet?.balance || 0}
                        />
                        <BalanceCard
                            title="Total Earned"
                            amount={wallet?.total_earned || 0}
                        />
                        <BalanceCard
                            title="Pending Payout"
                            amount={wallet?.pending_payout || 0}
                        />
                    </div>

                    {/* Request Payout Form */}
                    <Card>
                        <h3 className="text-lg font-semibold mb-4">Request Payout</h3>
                        <form onSubmit={handleRequestPayout} className="space-y-4">
                            <input
                                type="number"
                                value={payoutAmount}
                                onChange={(e) => setPayoutAmount(e.target.value)}
                                placeholder="Enter amount"
                                className="w-full px-4 py-2 border rounded-lg"
                            />
                            <button
                                type="submit"
                                className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
                            >
                                Request Payout
                            </button>
                        </form>
                    </Card>

                    {/* Transactions Table */}
                    <Card>
                        <h3 className="text-lg font-semibold mb-4">Transaction History</h3>
                        <TransactionsTable transactions={transactions} />
                    </Card>
                </div>
            )}
        </PortalLayout>
    );
}
```

---

## FM Dashboard Integration

**File**: `src/pages/fm/FMDashboard.tsx`

### Implementation Example

```typescript
import { useState, useEffect } from 'react';
import { fmApiService } from '@/lib/fmApi';

export default function FMDashboard() {
    const [dashboard, setDashboard] = useState<FMDashboardData | null>(null);
    const [jobs, setJobs] = useState<FMJob[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const [dashData, jobsData] = await Promise.all([
                    fmApiService.getDashboard(),
                    fmApiService.getJobs({ limit: 10 }),
                ]);

                setDashboard(dashData);
                setJobs(jobsData.results);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load dashboard');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    return (
        <PortalLayout title="FM Dashboard" navItems={navItems}>
            {loading ? <LoadingSpinner /> : error ? <ErrorAlert message={error} /> : (
                <div className="space-y-6">
                    {/* Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                        <StatCard title="Total Jobs" value={dashboard?.total_jobs || 0} />
                        <StatCard title="Open Jobs" value={dashboard?.jobs_open || 0} />
                        <StatCard title="In Progress" value={dashboard?.jobs_in_progress || 0} />
                        <StatCard title="Completed" value={dashboard?.jobs_completed || 0} />
                    </div>

                    {/* Recent Jobs */}
                    <Card>
                        <h3 className="text-lg font-semibold mb-4">Recent Jobs</h3>
                        <FMJobsList jobs={jobs} />
                    </Card>
                </div>
            )}
        </PortalLayout>
    );
}
```

---

## FM Job Visit Integration

**File**: `src/pages/fm/FMJobVisit.tsx`

### Implementation Example

```typescript
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { fmApiService } from '@/lib/fmApi';

export default function FMJobVisit() {
    const { jobId } = useParams<{ jobId: string }>();
    const [job, setJob] = useState<FMJob | null>(null);
    const [siteVisit, setSiteVisit] = useState<SiteVisitData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [notes, setNotes] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            if (!jobId) return;
            try {
                setLoading(true);
                const [jobData, visitData] = await Promise.all([
                    fmApiService.getJobDetail(parseInt(jobId)),
                    fmApiService.getSiteVisit(parseInt(jobId)),
                ]);

                setJob(jobData);
                setSiteVisit(visitData);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load job');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [jobId]);

    const handleStartVisit = async () => {
        if (!jobId) return;
        try {
            const visitData = await fmApiService.startSiteVisit(parseInt(jobId), {
                notes: notes,
            });
            setSiteVisit(visitData);
            // Show success toast
        } catch (err) {
            // Show error toast
        }
    };

    const handleUpdateVisit = async () => {
        if (!jobId) return;
        try {
            const visitData = await fmApiService.updateSiteVisit(parseInt(jobId), {
                notes: notes,
            });
            setSiteVisit(visitData);
            // Show success toast
        } catch (err) {
            // Show error toast
        }
    };

    const handleCompleteVisit = async () => {
        if (!jobId) return;
        try {
            await fmApiService.completeSiteVisit(parseInt(jobId));
            setSiteVisit({ ...siteVisit!, status: 'completed' } as SiteVisitData);
            // Show success toast
        } catch (err) {
            // Show error toast
        }
    };

    const handlePhotoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!jobId || !e.target.files?.[0]) return;
        try {
            const formData = new FormData();
            formData.append('photo', e.target.files[0]);

            await fmApiService.uploadSiteVisitPhoto(parseInt(jobId), formData);
            // Show success toast and refresh
        } catch (err) {
            // Show error toast
        }
    };

    return (
        <PortalLayout title={`Site Visit - ${job?.title}`} navItems={navItems}>
            {loading ? <LoadingSpinner /> : error ? <ErrorAlert message={error} /> : (
                <div className="space-y-6">
                    {/* Job Info */}
                    <Card>
                        <h2 className="text-2xl font-bold mb-4">{job?.title}</h2>
                        <p className="text-gray-600">{job?.location}</p>
                        <p className="text-gray-600">Customer: {job?.customer_name}</p>
                    </Card>

                    {/* Site Visit Controls */}
                    <Card>
                        <h3 className="text-lg font-semibold mb-4">Site Visit</h3>
                        {!siteVisit ? (
                            <button
                                onClick={handleStartVisit}
                                className="bg-blue-600 text-white px-4 py-2 rounded-lg"
                            >
                                Start Site Visit
                            </button>
                        ) : (
                            <div className="space-y-4">
                                <textarea
                                    value={notes}
                                    onChange={(e) => setNotes(e.target.value)}
                                    placeholder="Visit notes..."
                                    className="w-full px-4 py-2 border rounded-lg"
                                />
                                <div className="flex gap-2">
                                    <button
                                        onClick={handleUpdateVisit}
                                        className="bg-yellow-600 text-white px-4 py-2 rounded-lg"
                                    >
                                        Update Visit
                                    </button>
                                    <button
                                        onClick={handleCompleteVisit}
                                        className="bg-green-600 text-white px-4 py-2 rounded-lg"
                                    >
                                        Complete Visit
                                    </button>
                                </div>
                            </div>
                        )}
                    </Card>

                    {/* Photo Upload */}
                    <Card>
                        <h3 className="text-lg font-semibold mb-4">Upload Photos</h3>
                        <input
                            type="file"
                            accept="image/*"
                            onChange={handlePhotoUpload}
                            className="block mb-4"
                        />
                    </Card>
                </div>
            )}
        </PortalLayout>
    );
}
```

---

## Investor Dashboard Integration

**File**: `src/pages/investor/InvestorDashboard.tsx`

### Implementation Example

```typescript
import { useState, useEffect } from 'react';
import { investorApiService } from '@/lib/investorApi';

export default function InvestorDashboard() {
    const [dashboard, setDashboard] = useState<InvestorDashboardData | null>(null);
    const [properties, setProperties] = useState<PropertyData[]>([]);
    const [revenueData, setRevenueData] = useState<RevenueData[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const [dashData, propsData, revData] = await Promise.all([
                    investorApiService.getDashboard(),
                    investorApiService.getProperties(),
                    investorApiService.getRevenueStatistics('6m'),
                ]);

                setDashboard(dashData);
                setProperties(propsData.results);
                setRevenueData(revData);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load dashboard');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    return (
        <PortalLayout title="Investor Dashboard" navItems={navItems}>
            {loading ? <LoadingSpinner /> : error ? <ErrorAlert message={error} /> : (
                <div className="space-y-6">
                    {/* Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                        <StatCard 
                            title="Properties" 
                            value={dashboard?.total_properties || 0}
                        />
                        <StatCard 
                            title="Active Orders" 
                            value={dashboard?.active_work_orders || 0}
                        />
                        <StatCard 
                            title="Total Revenue" 
                            value={formatCurrency(dashboard?.total_revenue || 0)}
                        />
                        <StatCard 
                            title="ROI" 
                            value={`${dashboard?.roi_percentage || 0}%`}
                        />
                    </div>

                    {/* Revenue Chart */}
                    <Card>
                        <h3 className="text-lg font-semibold mb-4">Revenue Trend</h3>
                        <RevenueChart data={revenueData} />
                    </Card>

                    {/* Properties Grid */}
                    <Card>
                        <h3 className="text-lg font-semibold mb-4">Properties</h3>
                        <PropertiesGrid properties={properties} />
                    </Card>
                </div>
            )}
        </PortalLayout>
    );
}
```

---

## Customer Dashboard (Partial Integration)

**File**: `src/pages/customer/CustomerDashboard.tsx`

### Current Implementation
Already has partial integration. To complete:

```typescript
// Replace the mock data fallback with full API integration
useEffect(() => {
    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            const data = await customerApiService.getDashboard();
            setDashboardData(data);
            
            // Fetch jobs if dashboard doesn't include them
            if (!data.jobs) {
                const jobsData = await customerApiService.getJobs();
                const jobsArray = Array.isArray(jobsData) ? jobsData : jobsData.results;
                setDashboardData(prev => prev ? { ...prev, jobs: jobsArray } : null);
            }
        } catch (err) {
            console.error('Failed to fetch dashboard data:', err);
            setError('Failed to load dashboard');
        } finally {
            setLoading(false);
        }
    };

    if (currentUser) {
        fetchDashboardData();
    }
}, [currentUser]);
```

---

## Common Patterns

### Error Handling
```typescript
const handleApiCall = async (apiFunction: () => Promise<any>) => {
    try {
        const result = await apiFunction();
        // Success handling
    } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An error occurred';
        // Show error toast or message
    }
};
```

### Loading States
```typescript
if (loading) return <LoadingSpinner />;
if (error) return <ErrorAlert message={error} />;
```

### Token Handling
Tokens are automatically managed. No additional code needed unless implementing token refresh logic.

---

## Testing API Integration

### Using Browser DevTools
1. Open Network tab
2. Make a request through the UI
3. Check the request headers include: `Authorization: Token {token}`
4. Verify response status is 200 (or expected status code)

### Common Issues
- **401 Unauthorized**: Token expired or invalid
- **404 Not Found**: Endpoint path mismatch
- **500 Internal Server Error**: Backend issue
- **CORS Error**: Frontend URL not allowed in backend CORS settings

---

## Performance Tips

1. **Pagination**: Use `limit` and `offset` parameters for large datasets
2. **Caching**: Consider storing frequently accessed data in state or Context
3. **Debouncing**: For search/filter operations, debounce API calls
4. **Parallel Requests**: Use `Promise.all()` for independent requests

---

## Next Steps

1. Start with Admin Dashboard integration
2. Move to critical pages (Customer, Contractor)
3. Complete FM and Investor integrations
4. Add error boundaries and loading states
5. Implement real-time updates if needed

---

Last Updated: 2025-12-23
