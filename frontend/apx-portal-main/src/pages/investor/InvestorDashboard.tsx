import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { investorApi } from '@/services/investorApi';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import {
    DollarSign,
    TrendingUp,
    Briefcase,
    Calendar,
    LayoutDashboard,
    FileText,
    Building,
    PieChart as PieChartIcon,
    Users,
    Plus,
    UserPlus,
    Download
} from 'lucide-react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip as RechartsTooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell
} from 'recharts';
import { Job, JobStatus } from '@/types';
import AddLeadModal from '@/components/leads/AddLeadModal';
import { investorJobBreakdown } from '@/data/mockData';

// Helper to format currency
const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
    }).format(amount);
};

const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
    });
};

export default function InvestorDashboard() {
    const navigate = useNavigate();
    const location = useLocation();
    
    const [dashboardData, setDashboardData] = useState<any>(null);
    const [jobBreakdowns, setJobBreakdowns] = useState<any[]>([]);
    const [properties, setProperties] = useState<any[]>([]);
    const [leads, setLeads] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const [activeTab, setActiveTab] = useState<'overview' | 'orders' | 'leads' | 'properties'>('overview');
    const [ordersFilter, setOrdersFilter] = useState<'active' | 'closed' | 'pending' | 'history'>('active');
    const [isLeadModalOpen, setIsLeadModalOpen] = useState(false);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            setLoading(true);
            setError(null);
            
            const [dashboard, breakdowns, propertiesData, leadsData] = await Promise.all([
                investorApi.getDashboard(),
                investorApi.getJobBreakdowns(),
                investorApi.getProperties(),
                investorApi.getLeads()
            ]);
            
            setDashboardData(dashboard);
            setJobBreakdowns(breakdowns.breakdowns || []);
            setProperties(propertiesData.properties || []);
            setLeads(leadsData.leads || []);
        } catch (err: any) {
            console.error('Failed to load dashboard data:', err);
            setError('Failed to load dashboard data. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    // Refresh Leads
    const refreshLeads = () => {
        loadDashboardData();
    };

    if (loading) {
        return (
            <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center">
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 max-w-md">
                    <p className="text-red-700 dark:text-red-400">{error}</p>
                    <button 
                        onClick={loadDashboardData}
                        className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    // Extract data from API response with fallbacks
    const investor = dashboardData?.investor || { name: 'Investor', email: 'investor@apex.inc' };
    const activeProjects = dashboardData?.active_projects || 0;
    const totalRevenue = dashboardData?.total_revenue || 0;
    const netProfit = dashboardData?.net_profit || 0;
    const avgRoi = dashboardData?.avg_roi || 0;

    // Graph Data from API or fallbacks
    const roiData = dashboardData?.roi_data || [
        { month: 'Jan', value: 12 },
        { month: 'Feb', value: 19 },
        { month: 'Mar', value: 15 },
        { month: 'Apr', value: 22 },
        { month: 'May', value: 28 },
        { month: 'Jun', value: 25 },
        { month: 'Jul', value: 32 },
    ];

    const allocationData = dashboardData?.allocation_data || [
        { name: 'Flips', value: 65, color: '#8b5cf6' },
        { name: 'Rentals', value: 25, color: '#ec4899' },
        { name: 'Commercial', value: 10, color: '#3b82f6' },
    ];

    // Sync tab with URL path
    useEffect(() => {
        const path = location.pathname;
        if (path.includes('/investor/orders')) {
            setActiveTab('orders');
        } else if (path.includes('/investor/properties')) {
            setActiveTab('properties');
        } else if (path.includes('/investor/leads')) {
            setActiveTab('leads');
        } else {
            setActiveTab('overview');
        }
    }, [location.pathname]);

    const getFilteredJobs = () => {
        switch (ordersFilter) {
            case 'active':
                return investorJobs.filter(j => ['Open', 'InProgress'].includes(j.status));
            case 'closed':
                return investorJobs.filter(j => ['Complete', 'Paid'].includes(j.status));
            case 'pending':
                return investorJobs.filter(j => j.status === 'Complete');
            case 'history':
                return investorJobs.filter(j => j.status === 'Paid');
            default:
                return investorJobs;
        }
    };

    // Navigation Items for Sidebar
    const navItems = [
        { label: 'Dashboard', path: '/investor/dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
        { label: 'Work Orders', path: '/investor/orders', icon: <FileText className="w-5 h-5" /> },
        { label: 'Leads', path: '/investor/leads', icon: <Users className="w-5 h-5" /> },
        { label: 'Properties', path: '/investor/properties', icon: <Building className="w-5 h-5" /> },
        { label: 'Reports', path: '/investor/reports', icon: <PieChartIcon className="w-5 h-5" /> },
    ];

    const filteredJobs = getFilteredJobs();

    return (
        <PortalLayout title="Investor Dashboard" navItems={navItems}>
            <div className="space-y-8 animate-fade-in pb-10">

                {/* 1. Gradient Welcome Header */}
                <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-fuchsia-600 to-purple-800 p-8 shadow-2xl">
                    <div className="relative z-10 text-white">
                        <h1 className="text-3xl font-bold mb-2">Welcome, {investor?.name || 'Investor'}!</h1>
                        <p className="text-purple-100 opacity-90">Investment Portfolio Overview</p>
                    </div>
                    <div className="absolute right-0 top-0 h-full w-1/3 opacity-10">
                        <PieChartIcon className="w-full h-full text-white" />
                    </div>
                </div>

                {/* 2. Floating Navigation Bar (Tabs) */}
                <div className="flex justify-center mb-6">
                    <div className="inline-flex bg-white dark:bg-gray-800/80 backdrop-blur-md rounded-full p-1.5 shadow-lg border border-gray-100 dark:border-gray-700/50">
                        {[
                            { id: 'overview', label: 'Overview', icon: LayoutDashboard },
                            { id: 'orders', label: 'Work Orders', icon: FileText },
                            { id: 'leads', label: 'Leads', icon: Users },
                            { id: 'properties', label: 'Properties', icon: Building },
                        ].map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => {
                                    setActiveTab(tab.id as any);
                                    if (tab.id === 'overview') navigate('/investor/dashboard');
                                    if (tab.id === 'orders') navigate('/investor/orders');
                                    if (tab.id === 'properties') navigate('/investor/properties');
                                }}
                                className={`flex items-center gap-2 px-5 py-2.5 text-sm font-bold transition-all duration-200 rounded-full ${activeTab === tab.id
                                        ? 'bg-purple-600 text-white shadow-md transform scale-105'
                                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-700/50'
                                    }`}
                            >
                                <tab.icon className={`w-4 h-4 ${activeTab === tab.id ? 'text-white' : 'text-gray-500 dark:text-gray-400'}`} />
                                {tab.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* 3. Overview Content */}
                {activeTab === 'overview' && (
                    <div className="space-y-8">
                        {/* Metrics Row */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            {/* Card 1: Active Projects (Blue theme) */}
                            <div className="p-6 rounded-2xl bg-white dark:bg-[#1e293b] border border-gray-200 dark:border-gray-700/50 shadow-lg relative overflow-hidden group hover:-translate-y-1 transition-transform cursor-default">
                                <div className="absolute top-0 right-0 p-4 opacity-20 dark:opacity-10 group-hover:opacity-30 dark:group-hover:opacity-20 transition-opacity">
                                    <Briefcase className="w-16 h-16 text-blue-500 dark:text-white" />
                                </div>
                                <p className="text-gray-500 dark:text-gray-400 text-sm font-medium mb-1">Active Projects</p>
                                <h3 className="text-3xl font-bold text-gray-900 dark:text-white">{activeProjects}</h3>
                                <div className="w-12 h-1 bg-blue-500 rounded-full mt-4" />
                            </div>

                            {/* Card 2: Total Revenue (Green theme) */}
                            <div className="p-6 rounded-2xl bg-white dark:bg-[#064e3b] dark:bg-gradient-to-br dark:from-green-900 dark:to-green-950 border border-gray-200 dark:border-green-800/50 shadow-lg relative overflow-hidden group hover:-translate-y-1 transition-transform cursor-default">
                                <div className="absolute top-0 right-0 p-4 opacity-20 dark:opacity-10 group-hover:opacity-30 dark:group-hover:opacity-20 transition-opacity">
                                    <TrendingUp className="w-16 h-16 text-green-500 dark:text-white" />
                                </div>
                                <p className="text-gray-500 dark:text-green-200 text-sm font-medium mb-1">Total Revenue</p>
                                <h3 className="text-3xl font-bold text-green-600 dark:text-white">{formatCurrency(totalRevenue)}</h3>
                                <div className="w-12 h-1 bg-green-500 rounded-full mt-4" />
                            </div>

                            {/* Card 3: Net Profit (Purple theme) */}
                            <div className="p-6 rounded-2xl bg-white dark:bg-[#4c1d95] dark:bg-gradient-to-br dark:from-purple-900 dark:to-purple-950 border border-gray-200 dark:border-purple-800/50 shadow-lg relative overflow-hidden group hover:-translate-y-1 transition-transform cursor-default">
                                <div className="absolute top-0 right-0 p-4 opacity-20 dark:opacity-10 group-hover:opacity-30 dark:group-hover:opacity-20 transition-opacity">
                                    <DollarSign className="w-16 h-16 text-purple-500 dark:text-white" />
                                </div>
                                <p className="text-gray-500 dark:text-purple-200 text-sm font-medium mb-1">Net Profit</p>
                                <h3 className="text-3xl font-bold text-purple-600 dark:text-white">{formatCurrency(netProfit)}</h3>
                                <div className="w-12 h-1 bg-purple-500 rounded-full mt-4" />
                            </div>

                            {/* Card 4: ROI (Orange theme) */}
                            <div className="p-6 rounded-2xl bg-white dark:bg-[#431407] dark:bg-gradient-to-br dark:from-orange-900 dark:to-orange-950 border border-gray-200 dark:border-orange-800/50 shadow-lg relative overflow-hidden group hover:-translate-y-1 transition-transform cursor-default">
                                <div className="absolute top-0 right-0 p-4 opacity-20 dark:opacity-10 group-hover:opacity-30 dark:group-hover:opacity-20 transition-opacity">
                                    <TrendingUp className="w-16 h-16 text-orange-500 dark:text-white" />
                                </div>
                                <p className="text-gray-500 dark:text-orange-200 text-sm font-medium mb-1">ROI</p>
                                <h3 className="text-3xl font-bold text-orange-600 dark:text-white">{avgRoi}%</h3>
                                <div className="w-12 h-1 bg-orange-500 rounded-full mt-4" />
                            </div>
                        </div>

                        {/* Earnings Breakdown */}
                        <Card className="bg-white dark:bg-[#111827] border-gray-200 dark:border-gray-800">
                            <h3 className="font-bold mb-6 text-gray-900 dark:text-gray-100">Earnings Breakdown</h3>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4 border border-gray-100 dark:border-gray-700/50 text-center">
                                    <p className="text-gray-500 dark:text-gray-400 text-xs uppercase font-bold tracking-wider mb-2">Apex Earnings (Platform)</p>
                                    <p className="text-2xl font-bold text-gray-900 dark:text-white">$750.00</p>
                                    <p className="text-xs text-gray-500 mt-1">15% Service Fee</p>
                                </div>
                                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4 border border-gray-100 dark:border-gray-700/50 text-center">
                                    <p className="text-gray-500 dark:text-gray-400 text-xs uppercase font-bold tracking-wider mb-2">Investor Earnings (Net)</p>
                                    <p className="text-2xl font-bold text-green-600 dark:text-green-400">{formatCurrency(netProfit)}</p>
                                    <p className="text-xs text-gray-500 mt-1">After Labor & Materials</p>
                                </div>
                                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4 border border-gray-100 dark:border-gray-700/50 text-center">
                                    <p className="text-gray-500 dark:text-gray-400 text-xs uppercase font-bold tracking-wider mb-2">Total Payouts Received</p>
                                    <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">$3,584.00</p>
                                    <p className="text-xs text-gray-500 mt-1">Cash Distributed</p>
                                </div>
                            </div>
                        </Card>

                        {/* Charts Section */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* ROI Chart */}
                            <Card className="bg-white dark:bg-[#111827] border-gray-200 dark:border-gray-800 min-h-[350px]">
                                <h3 className="font-bold mb-6 text-gray-900 dark:text-gray-100">Investment Performance (ROI)</h3>
                                <div className="h-[250px] w-full">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <LineChart data={roiData}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} className="dark:stroke-gray-700" />
                                            <XAxis dataKey="month" stroke="#9ca3af" tickLine={false} axisLine={false} />
                                            <YAxis stroke="#9ca3af" tickLine={false} axisLine={false} />
                                            <RechartsTooltip
                                                contentStyle={{ backgroundColor: '#fff', borderColor: '#e5e7eb', borderRadius: '8px', color: '#111827' }}
                                                itemStyle={{ color: '#111827' }}
                                            />
                                            <Line
                                                type="monotone"
                                                dataKey="value"
                                                stroke="#2dd4bf"
                                                strokeWidth={3}
                                                dot={{ fill: '#2dd4bf', strokeWidth: 2, r: 4 }}
                                            />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                            </Card>

                            {/* Portfolio Allocation */}
                            <Card className="bg-white dark:bg-[#111827] border-gray-200 dark:border-gray-800 min-h-[350px]">
                                <h3 className="font-bold mb-6 text-gray-900 dark:text-gray-100">Portfolio Allocation</h3>
                                <div className="h-[250px] w-full flex items-center justify-center relative">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <PieChart>
                                            <Pie
                                                data={allocationData}
                                                cx="50%"
                                                cy="50%"
                                                innerRadius={60}
                                                outerRadius={80}
                                                paddingAngle={5}
                                                dataKey="value"
                                            >
                                                {allocationData.map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                                ))}
                                            </Pie>
                                            <RechartsTooltip contentStyle={{ backgroundColor: '#fff', borderColor: '#e5e7eb', borderRadius: '8px', color: '#111827' }} />
                                        </PieChart>
                                    </ResponsiveContainer>
                                    {/* Legend */}
                                    <div className="absolute bottom-0 w-full flex justify-center gap-4 text-xs">
                                        {allocationData.map((item, idx) => (
                                            <div key={idx} className="flex items-center gap-1.5">
                                                <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: item.color }} />
                                                <span className="text-gray-600 dark:text-gray-300">{item.name}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </Card>
                        </div>
                    </div>
                )}

                {/* 4. ORDERS TAB (Existing List) */}
                {activeTab === 'orders' && (
                    <div className="space-y-6">
                        <div className="flex gap-2 border-b border-gray-200 dark:border-gray-800 pb-1">
                            {[
                                { id: 'active', label: 'Active Jobs', count: investorJobs.filter(j => ['Open', 'InProgress'].includes(j.status)).length },
                                { id: 'closed', label: 'Closed Jobs', count: investorJobs.filter(j => ['Complete', 'Paid'].includes(j.status)).length },
                                { id: 'pending', label: 'Pending Payouts', count: investorJobs.filter(j => j.status === 'Complete').length },
                                { id: 'history', label: 'Payout History', count: investorJobs.filter(j => j.status === 'Paid').length },
                            ].map((tab) => (
                                <button
                                    key={tab.id}
                                    onClick={() => setOrdersFilter(tab.id as any)}
                                    className={`px-4 py-2 text-sm font-medium transition-colors relative ${ordersFilter === tab.id
                                            ? 'text-purple-600 dark:text-purple-400'
                                            : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                                        }`}
                                >
                                    {tab.label}
                                    <span className="ml-2 bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded-full text-xs">
                                        {tab.count}
                                    </span>
                                    {ordersFilter === tab.id && (
                                        <div className="absolute bottom-0 left-0 w-full h-0.5 bg-purple-600 dark:bg-purple-400" />
                                    )}
                                </button>
                            ))}
                        </div>

                        <div className="space-y-4">
                            {filteredJobs.length > 0 ? (
                                filteredJobs.map((job: Job) => {
                                    const breakdown = investorJobBreakdown.find(b => b.jobId === job.id);
                                    return (
                                        <Card key={job.id} className="hover:shadow-md transition-shadow group cursor-pointer" onClick={() => navigate(`/investor/property/${job.id}`)}>
                                            <div className="flex justify-between items-start">
                                                <div className="flex gap-4">
                                                    <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center text-purple-600 dark:text-purple-400">
                                                        <Briefcase className="w-6 h-6" />
                                                    </div>
                                                    <div>
                                                        <h3 className="font-semibold text-gray-900 dark:text-white text-lg">{job.propertyAddress}</h3>
                                                        <p className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-2 mt-1">
                                                            <span>{job.city} • #{job.id}</span>
                                                            {job.scheduledTime && (
                                                                <span className="flex items-center gap-1 text-xs bg-gray-50 dark:bg-gray-800 px-2 py-0.5 rounded text-gray-500">
                                                                    <Calendar className="w-3 h-3" />
                                                                    {formatDate(job.scheduledTime)}
                                                                </span>
                                                            )}
                                                        </p>

                                                        {breakdown && (
                                                            <div className="flex items-center gap-4 mt-2 text-xs">
                                                                <span className="text-gray-600 dark:text-gray-400 font-medium bg-gray-50 dark:bg-gray-800 px-2 py-1 rounded">
                                                                    ROI: <span className="text-green-600 dark:text-green-400">
                                                                        {breakdown.expenses > 0
                                                                            ? ((breakdown.investorShare / breakdown.expenses) * 100).toFixed(1)
                                                                            : breakdown.roi}%
                                                                    </span>
                                                                </span>
                                                                <span className="text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 px-2 py-1 rounded">
                                                                    Share: {breakdown.profitSplit?.investor}%
                                                                </span>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                                <div className="text-right">
                                                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Status</p>
                                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${job.status === 'Paid' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' :
                                                            job.status === 'Complete' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400' :
                                                                'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400'
                                                        }`}>
                                                        {job.status === 'Complete' ? 'Pending Payout' : job.status}
                                                    </span>
                                                    {breakdown && (
                                                        <div className="mt-2 text-right">
                                                            <p className="text-xs text-gray-500 dark:text-gray-400">My Profit</p>
                                                            <p className="font-bold text-gray-900 dark:text-white">
                                                                {formatCurrency(breakdown.investorShare)}
                                                            </p>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </Card>
                                    );
                                })
                            ) : (
                                <Card className="py-12 flex flex-col items-center justify-center text-center border-dashed border-gray-700">
                                    <div className="w-16 h-16 bg-gray-800 rounded-full flex items-center justify-center mb-4 text-gray-500">
                                        <Briefcase className="w-8 h-8" />
                                    </div>
                                    <h3 className="text-lg font-medium text-white">No jobs found</h3>
                                    <p className="text-gray-500 max-w-sm mt-2">
                                        No jobs in this category yet.
                                    </p>
                                </Card>
                            )}
                        </div>
                    </div>
                )}

                {/* Leads Tab */}
                {activeTab === 'leads' && (
                    <div className="space-y-6 animate-fade-in">
                        <div className="flex justify-between items-center">
                            <div>
                                <h2 className="text-xl font-bold text-gray-900 dark:text-white">Deal Flow</h2>
                                <p className="text-sm text-gray-500 dark:text-gray-400">Manage your potential investment opportunities.</p>
                            </div>
                            <div className="flex gap-3">
                                <Button variant="outline" onClick={() => alert('Mock: Syncing with Angi...')}>
                                    <Download className="w-4 h-4 mr-2" />
                                    Import Angi Leads
                                </Button>
                                <Button onClick={() => setIsLeadModalOpen(true)}>
                                    <Plus className="w-4 h-4 mr-2" />
                                    Add Manual Lead
                                </Button>
                            </div>
                        </div>

                        <Card>
                            <table className="w-full text-sm text-left">
                                <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-800">
                                    <tr>
                                        <th className="py-3 px-4 font-medium">Lead Name</th>
                                        <th className="py-3 px-4 font-medium">Property</th>
                                        <th className="py-3 px-4 font-medium">Date Added</th>
                                        <th className="py-3 px-4 font-medium">Source</th>
                                        <th className="py-3 px-4 font-medium">Stage</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                                    {leads.map((l) => (
                                        <tr key={l.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                                            <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">
                                                <div className="flex items-center space-x-3">
                                                    <div className="p-1.5 bg-purple-100 dark:bg-purple-900/30 rounded-full">
                                                        <UserPlus className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                                                    </div>
                                                    <span>{l.name}</span>
                                                </div>
                                            </td>
                                            <td className="py-3 px-4 text-gray-600 dark:text-gray-400">{l.property}</td>
                                            <td className="py-3 px-4 text-gray-600 dark:text-gray-400">{l.date}</td>
                                            <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                                                <span className="text-xs border border-gray-200 dark:border-gray-700 px-2 py-0.5 rounded-full">
                                                    {l.source}
                                                </span>
                                            </td>
                                            <td className="py-3 px-4">
                                                <Badge variant={l.stage === 'New' ? 'info' : l.stage === 'Won' ? 'success' : 'default'}>{l.stage}</Badge>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </Card>
                    </div>
                )}

                {/* 6. PROPERTIES TAB */}
                {activeTab === 'properties' && (
                    <Card>
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="font-bold text-gray-900 dark:text-white">My Properties</h3>
                            <Button size="sm">Add Property</Button>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {/* Mock Property Cards */}
                            {[1, 2, 3].map((_, idx) => (
                                <div key={idx} className="border border-gray-200 dark:border-gray-700 rounded-xl p-4 hover:shadow-lg transition-shadow bg-white dark:bg-gray-800">
                                    <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded-lg mb-4 flex items-center justify-center">
                                        <Building className="w-10 h-10 text-gray-400" />
                                    </div>
                                    <h4 className="font-bold text-gray-900 dark:text-white">Property #{idx + 1}</h4>
                                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">123 Investment Lane</p>
                                    <div className="flex justify-between text-xs text-gray-500 border-t border-gray-100 dark:border-gray-700 pt-3">
                                        <span>Active Jobs: 1</span>
                                        <span className="text-green-500 font-medium">ROI: 12%</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </Card>
                )}

            </div>

            <AddLeadModal
                isOpen={isLeadModalOpen}
                onClose={() => setIsLeadModalOpen(false)}
                onSuccess={refreshLeads}
            />
        </PortalLayout>
    );
}
