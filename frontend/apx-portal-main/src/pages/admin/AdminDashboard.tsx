
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { useState, useEffect } from 'react';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import {
    LayoutDashboard,
    ShieldCheck,
    AlertTriangle,
    DollarSign,
    Briefcase,
    Calendar,
    Users,
    FileText,
    Loader2
} from 'lucide-react';
import { adminApiService } from '@/lib/adminApi';
import { formatCurrency } from '@/lib/utils';
import {
    AreaChart,
    Area,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from 'recharts';

export default function AdminDashboard() {
    const navigate = useNavigate();
    const { user } = useAuth();
    
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [dashboardStats, setDashboardStats] = useState<any>(null);
    const [jobs, setJobs] = useState<any[]>([]);
    const [disputes, setDisputes] = useState<any[]>([]);
    const [payouts, setPayouts] = useState<any[]>([]);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                setLoading(true);
                setError(null);

                // Fetch dashboard stats
                const [statsData, jobsData, disputesData, payoutsData] = await Promise.all([
                    adminApiService.getDashboardStats(),
                    adminApiService.getJobs({ limit: 10 }),
                    adminApiService.getDisputes({ limit: 10 }),
                    adminApiService.getPayouts({ limit: 10 })
                ]);

                setDashboardStats(statsData);
                setJobs(jobsData.results || jobsData);
                setDisputes(disputesData.results || disputesData);
                setPayouts(payoutsData.results || payoutsData);
            } catch (err) {
                console.error('Failed to fetch dashboard data:', err);
                setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    if (loading) {
        return (
            <PortalLayout title="Admin Dashboard" navItems={navItems}>
                <div className="flex items-center justify-center h-64">
                    <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                    <span className="ml-2 text-gray-600">Loading dashboard...</span>
                </div>
            </PortalLayout>
        );
    }

    if (error) {
        return (
            <PortalLayout title="Admin Dashboard" navItems={navItems}>
                <div className="flex items-center justify-center h-64">
                    <div className="text-center">
                        <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                        <p className="text-red-600 mb-4">{error}</p>
                        <Button onClick={() => window.location.reload()}>Retry</Button>
                    </div>
                </div>
            </PortalLayout>
        );
    }

    const navItems = [
        { label: 'Dashboard', path: '/admin/dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
        { label: 'Jobs', path: '/admin/jobs', icon: <Briefcase className="w-5 h-5" /> },
        { label: 'Legal & Compliance', path: '/admin/legal-compliance', icon: <ShieldCheck className="w-5 h-5" /> },
        { label: 'Disputes', path: '/admin/disputes', icon: <AlertTriangle className="w-5 h-5" /> },
        { label: 'Ledger', path: '/admin/ledger', icon: <FileText className="w-5 h-5" /> },
        { label: 'Payouts', path: '/admin/payouts', icon: <DollarSign className="w-5 h-5" /> },
        { label: 'Meetings', path: '/admin/meetings', icon: <Calendar className="w-5 h-5" /> },
        { label: 'Leads', path: '/admin/leads', icon: <Users className="w-5 h-5" /> },
    ];

    // Calculate stats from API data
    const pendingDisputes = disputes.filter(d => d.status === 'Open' || d.status === 'open');
    const pendingPayouts = payouts.filter(p => p.status === 'Processing' || p.status === 'processing');
    const activeJobs = jobs.filter(j => j.status === 'InProgress' || j.status === 'Open' || j.status === 'in_progress' || j.status === 'open');
    
    const totalPendingPayouts = pendingPayouts.reduce((sum, p) => sum + (p.amount || 0), 0);

    // Use API stats if available, otherwise calculate from data
    const stats = {
        pendingDisputes: dashboardStats?.pending_disputes || pendingDisputes.length,
        pendingPayouts: dashboardStats?.pending_payouts || pendingPayouts.length,
        blockedContractors: dashboardStats?.blocked_contractors || 0,
        activeJobs: dashboardStats?.active_jobs || activeJobs.length,
        scheduledMeetings: dashboardStats?.scheduled_meetings || 3,
        activeLeads: dashboardStats?.active_leads || 5,
        totalPendingPayouts: dashboardStats?.total_pending_payouts || totalPendingPayouts
    };

    const revenueData = dashboardStats?.revenue_data || [
        { name: 'Jan', value: 4000 },
        { name: 'Feb', value: 3000 },
        { name: 'Mar', value: 2000 },
        { name: 'Apr', value: 2780 },
        { name: 'May', value: 1890 },
        { name: 'Jun', value: 2390 },
        { name: 'Jul', value: 3490 },
    ];

    const jobStatsData = dashboardStats?.job_stats || [
        { name: 'Open', count: jobs.filter(j => j.status === 'Open' || j.status === 'open').length },
        { name: 'In Progress', count: jobs.filter(j => j.status === 'InProgress' || j.status === 'in_progress').length },
        { name: 'Completed', count: jobs.filter(j => j.status === 'Complete' || j.status === 'completed').length },
        { name: 'Paid', count: jobs.filter(j => j.status === 'Paid' || j.status === 'paid').length },
    ];

    return (
        <PortalLayout title="Admin Dashboard" navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <Card
                        hover={true}
                        className="cursor-pointer bg-gradient-to-br from-red-500/10 to-red-600/10 dark:from-red-500/20 dark:to-red-600/20 border-red-200 dark:border-red-800"
                        onClick={() => navigate('/admin/disputes')}
                    >
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Pending Disputes</p>
                                <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.pendingDisputes}</p>
                            </div>
                            <div className="w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                                <AlertTriangle className="w-6 h-6 text-red-600 dark:text-red-400" />
                            </div>
                        </div>
                    </Card>

                    <Card
                        hover={true}
                        className="cursor-pointer bg-gradient-to-br from-yellow-500/10 to-yellow-600/10 dark:from-yellow-500/20 dark:to-yellow-600/20 border-yellow-200 dark:border-yellow-800"
                        onClick={() => navigate('/admin/payouts')}
                    >
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Pending Payouts</p>
                                <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.pendingPayouts}</p>
                                <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">{formatCurrency(stats.totalPendingPayouts)}</p>
                            </div>
                            <div className="w-12 h-12 rounded-full bg-yellow-100 dark:bg-yellow-900/30 flex items-center justify-center">
                                <DollarSign className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
                            </div>
                        </div>
                    </Card>

                    <Card
                        hover={true}
                        className="cursor-pointer bg-gradient-to-br from-orange-500/10 to-orange-600/10 dark:from-orange-500/20 dark:to-orange-600/20 border-orange-200 dark:border-orange-800"
                        onClick={() => navigate('/admin/legal-compliance')}
                    >
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Blocked Contractors</p>
                                <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.blockedContractors}</p>
                            </div>
                            <div className="w-12 h-12 rounded-full bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center">
                                <ShieldCheck className="w-6 h-6 text-orange-600 dark:text-orange-400" />
                            </div>
                        </div>
                    </Card>

                    <Card
                        hover={true}
                        className="cursor-pointer bg-gradient-to-br from-blue-500/10 to-blue-600/10 dark:from-blue-500/20 dark:to-blue-600/20 border-blue-200 dark:border-blue-800"
                        onClick={() => navigate('/admin/jobs', { state: { status: 'Active' } })}
                    >
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Active Jobs</p>
                                <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.activeJobs}</p>
                            </div>
                            <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                                <Briefcase className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                            </div>
                        </div>
                    </Card>

                    <Card
                        hover={true}
                        className="cursor-pointer bg-gradient-to-br from-purple-500/10 to-purple-600/10 dark:from-purple-500/20 dark:to-purple-600/20 border-purple-200 dark:border-purple-800"
                        onClick={() => navigate('/admin/meetings')}
                    >
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Scheduled Meetings</p>
                                <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.scheduledMeetings}</p>
                            </div>
                            <div className="w-12 h-12 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                                <Calendar className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                            </div>
                        </div>
                    </Card>

                    <Card
                        hover={true}
                        className="cursor-pointer bg-gradient-to-br from-indigo-500/10 to-indigo-600/10 dark:from-indigo-500/20 dark:to-indigo-600/20 border-indigo-200 dark:border-indigo-800"
                        onClick={() => navigate('/admin/leads')}
                    >
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Active Leads</p>
                                <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.activeLeads}</p>
                            </div>
                            <div className="w-12 h-12 rounded-full bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
                                <Users className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                            </div>
                        </div>
                    </Card>
                </div>

                {/* Charts Section */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <Card>
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Revenue Overview</h3>
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={revenueData}>
                                    <defs>
                                        <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                                            <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
                                    <XAxis dataKey="name" className="text-xs text-gray-400" />
                                    <YAxis className="text-xs text-gray-400" />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', color: '#fff' }}
                                        itemStyle={{ color: '#fff' }}
                                    />
                                    <Area type="monotone" dataKey="value" stroke="#8b5cf6" fillOpacity={1} fill="url(#colorRevenue)" />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </Card>

                    <Card>
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Job Status Distribution</h3>
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={jobStatsData}>
                                    <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
                                    <XAxis dataKey="name" className="text-xs text-gray-400" />
                                    <YAxis className="text-xs text-gray-400" />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', color: '#fff' }}
                                        cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                    />
                                    <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </Card>
                </div>

                {/* Lists Section */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Investors List */}
                    <Card>
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Active Investors</h3>
                            <Button variant="outline" size="sm" onClick={() => navigate('/admin/investors')}>View All</Button>
                        </div>
                        <div className="space-y-4">
                            {dashboardStats?.recent_investors?.slice(0, 5).map((investor: any) => (
                                <div key={investor.id} className="flex items-center justify-between p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800 smooth-transition">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center text-white font-bold overflow-hidden shadow-sm">
                                            {investor.avatar_url ? <img src={investor.avatar_url} alt={investor.name} className="w-full h-full object-cover" /> : (investor.name || investor.first_name || 'U').charAt(0)}
                                        </div>
                                        <div>
                                            <p className="font-semibold text-gray-900 dark:text-white">{investor.name || `${investor.first_name} ${investor.last_name}`}</p>
                                            <p className="text-xs text-gray-500 dark:text-gray-400">{investor.email}</p>
                                        </div>
                                    </div>
                                    <Badge variant="success">Active</Badge>
                                </div>
                            )) || (
                                <div className="text-center py-4 text-gray-500">
                                    No investor data available
                                </div>
                            )}
                        </div>
                    </Card>

                    {/* Contractors List */}
                    <Card>
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Recent Contractors</h3>
                            <Button variant="outline" size="sm" onClick={() => navigate('/admin/legal-compliance')}>View All</Button>
                        </div>
                        <div className="space-y-4">
                            {dashboardStats?.recent_contractors?.slice(0, 5).map((contractor: any) => (
                                <div key={contractor.id} className="flex items-center justify-between p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800 smooth-transition">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-indigo-600 flex items-center justify-center text-white font-bold overflow-hidden shadow-sm">
                                            {contractor.avatar_url ? <img src={contractor.avatar_url} alt={contractor.name} className="w-full h-full object-cover" /> : (contractor.name || contractor.first_name || 'U').charAt(0)}
                                        </div>
                                        <div>
                                            <p className="font-semibold text-gray-900 dark:text-white">{contractor.name || `${contractor.first_name} ${contractor.last_name}`}</p>
                                            <p className="text-xs text-gray-500 dark:text-gray-400">{contractor.trade || 'General'}</p>
                                        </div>
                                    </div>
                                    <Badge variant={contractor.compliance_status === 'active' || contractor.compliance_status === 'verified' ? 'success' : 'danger'}>
                                        {contractor.compliance_status === 'active' || contractor.compliance_status === 'verified' ? 'Verified' : 'Blocked'}
                                    </Badge>
                                </div>
                            )) || (
                                <div className="text-center py-4 text-gray-500">
                                    No contractor data available
                                </div>
                            )}
                        </div>
                    </Card>
                </div>
            </div>
        </PortalLayout>
    );
}
