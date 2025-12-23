import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Badge, { getStatusBadgeVariant } from '@/components/ui/Badge';
import Button from '@/components/ui/Button';

import SupportWidget from '@/components/contractor/SupportWidget';
import {
    LayoutDashboard,
    ShieldCheck,
    Briefcase,
    Wallet as WalletIcon,
    TrendingUp,
    DollarSign,
    CheckCircle,
    AlertCircle,
    MapPin,
    Clock,
    ArrowRight,
    Loader2
} from 'lucide-react';
import { contractorApiService } from '@/lib/contractorApi';
import { formatCurrency } from '@/lib/utils';

export default function ContractorDashboard() {
    const navigate = useNavigate();
    const { user } = useAuth();

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [dashboardData, setDashboardData] = useState<any>(null);
    const [activeJobs, setActiveJobs] = useState<any[]>([]);
    const [walletData, setWalletData] = useState<any>(null);
    const [complianceData, setComplianceData] = useState<any>(null);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                setLoading(true);
                setError(null);

                const [dashboard, jobs, wallet, compliance] = await Promise.all([
                    contractorApiService.getDashboard(),
                    contractorApiService.getActiveJobs(),
                    contractorApiService.getWallet(),
                    contractorApiService.getCompliance()
                ]);

                setDashboardData(dashboard);
                setActiveJobs(jobs.results || jobs);
                setWalletData(wallet);
                setComplianceData(compliance);
            } catch (err) {
                console.error('Failed to fetch contractor dashboard data:', err);
                setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    if (loading) {
        return (
            <PortalLayout title="Contractor Dashboard" navItems={navItems}>
                <div className="flex items-center justify-center h-64">
                    <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
                    <span className="ml-2 text-gray-600">Loading dashboard...</span>
                </div>
            </PortalLayout>
        );
    }

    if (error) {
        return (
            <PortalLayout title="Contractor Dashboard" navItems={navItems}>
                <div className="flex items-center justify-center h-64">
                    <div className="text-center">
                        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                        <p className="text-red-600 mb-4">{error}</p>
                        <Button onClick={() => window.location.reload()}>Retry</Button>
                    </div>
                </div>
            </PortalLayout>
        );
    }

    const navItems = [
        { label: 'Dashboard', path: '/contractor/dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
        { label: 'Job Board', path: '/contractor/jobs', icon: <Briefcase className="w-5 h-5" /> },
        { label: 'Compliance Hub', path: '/contractor/compliance', icon: <ShieldCheck className="w-5 h-5" /> },
        { label: 'Wallet', path: '/contractor/wallet', icon: <WalletIcon className="w-5 h-5" /> },
    ];

    const complianceStatus = complianceData?.overall_status || user?.compliance_status || 'active';
    const stats = {
        completedJobsCount: dashboardData?.completed_jobs_count || 0,
        pendingPayoutTotal: walletData?.pending_balance || 0,
        totalEarnings: walletData?.total_earnings || 0,
        activeJobsCount: dashboardData?.active_jobs_count || activeJobs.length
    };

    return (
        <PortalLayout title="Contractor Dashboard" navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                {/* Compliance Banner */}
                <Card className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 border-purple-500/30">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <div className={`w-12 h-12 rounded-full flex items-center justify-center ${complianceStatus === 'active' ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
                                {complianceStatus === 'active' ? (
                                    <CheckCircle className="w-6 h-6 text-green-400" />
                                ) : (
                                    <AlertCircle className="w-6 h-6 text-red-400" />
                                )}
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Compliance Status</h3>
                                <Badge variant={getStatusBadgeVariant(complianceStatus)}>
                                    {complianceStatus.toUpperCase()}
                                </Badge>
                            </div>
                        </div>
                        <Button variant="outline" onClick={() => navigate('/contractor/compliance')}>
                            Manage Compliance
                        </Button>
                    </div>
                </Card>

                {/* Important Notice */}
                <Card className="bg-blue-500/10 border-blue-500/30">
                    <div className="flex items-start space-x-3">
                        <AlertCircle className="w-5 h-5 text-blue-400 mt-1" />
                        <div>
                            <h4 className="font-semibold text-blue-300">Important Reminder</h4>
                            <p className="text-sm text-blue-200 mt-1">
                                <strong>Use provided materials only.</strong> Do not purchase materials for jobs. All materials are supplied by customers or handled separately.
                            </p>
                        </div>
                    </div>
                </Card>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card hover={false}>
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400">Completed Jobs</p>
                                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">{stats.completedJobsCount}</p>
                                <div className="flex items-center space-x-2 mt-2">
                                    <TrendingUp className="w-4 h-4 text-green-400" />
                                    <span className="text-sm text-green-400">+12% this month</span>
                                </div>
                            </div>
                            <div className="w-16 h-16 rounded-full bg-gradient-to-r from-green-500/20 to-emerald-500/20 flex items-center justify-center">
                                <CheckCircle className="w-8 h-8 text-green-400" />
                            </div>
                        </div>
                    </Card>

                    <Card hover={false}>
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400">Pending Payouts</p>
                                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                                    {formatCurrency(stats.pendingPayoutTotal)}
                                </p>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    className="mt-2 p-0 h-auto"
                                    onClick={() => navigate('/contractor/wallet')}
                                >
                                    View Details →
                                </Button>
                            </div>
                            <div className="w-16 h-16 rounded-full bg-gradient-to-r from-purple-500/20 to-pink-500/20 flex items-center justify-center">
                                <DollarSign className="w-8 h-8 text-purple-400" />
                            </div>
                        </div>
                    </Card>
                </div>

                {/* Available Jobs Section */}
                <div>
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                                Hello, {user?.first_name || user?.name?.split(' ')[0] || 'Contractor'}
                            </h1>
                            <p className="text-gray-600 dark:text-gray-600 dark:text-gray-400 mt-1">
                                Use provided materials only. Do not purchase your own.
                            </p>
                        </div>

                        <div className="flex items-center space-x-2">
                            <span className="text-sm text-gray-700 dark:text-gray-500 dark:text-gray-600 dark:text-gray-400 mr-2">Status:</span>
                            <Badge variant={getStatusBadgeVariant(complianceStatus)}>
                                {complianceStatus.toUpperCase()}
                            </Badge>
                            <Button
                                variant="outline"
                                onClick={() => {
                                    if (complianceStatus === 'blocked') {
                                        alert('Fix compliance to accept jobs. Please visit the Compliance Hub to resolve issues.');
                                    } else {
                                        navigate('/contractor/jobs');
                                    }
                                }}
                            >
                                View All Jobs
                            </Button>
                        </div>
                    </div>

                    {/* Active Jobs Grid */}
                    <div>
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Active Jobs</h2>
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {activeJobs.length > 0 ? (
                                activeJobs.map((job) => (
                                    <Card key={job.id} className="hover:shadow-md transition-shadow cursor-pointer">
                                        <div className="flex justify-between items-start mb-4">
                                            <div className="flex items-start space-x-3">
                                                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                                                    <MapPin className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                                                </div>
                                                <div>
                                                    <div className="flex items-center space-x-2">
                                                        <h3 className="font-semibold text-gray-900 dark:text-white">{job.property_address || job.address}</h3>
                                                        {job.is_project && (
                                                            <Badge variant="info">Project</Badge>
                                                        )}
                                                    </div>
                                                    <p className="text-sm text-gray-600 dark:text-gray-400">{job.customer_name || job.customer?.name}</p>
                                                </div>
                                            </div>
                                            <Badge variant={job.status === 'in_progress' || job.status === 'InProgress' ? 'warning' : 'success'}>
                                                {job.status}
                                            </Badge>
                                        </div>

                                        <div className="space-y-3 mb-4">
                                            <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                                                <Clock className="w-4 h-4 mr-2 opacity-70" />
                                                Scheduled: {job.scheduled_time || job.scheduledTime ? new Date(job.scheduled_time || job.scheduledTime).toLocaleDateString() : 'TBD'}
                                            </div>
                                            <div className="flex items-center justify-between text-sm">
                                                <span className="text-gray-600 dark:text-gray-400">Estimated Pay:</span>
                                                <span className="font-semibold text-green-600 dark:text-green-400">{formatCurrency(job.estimated_pay || job.total_amount || 280)}</span>
                                            </div>
                                        </div>

                                        <div className="flex space-x-3 pt-4 border-t border-gray-100 dark:border-gray-800">
                                            <Button
                                                className="flex-1"
                                                size="sm"
                                                variant="outline"
                                                onClick={() => navigate(`/contractor/jobs/${job.id}`)}
                                            >
                                                View Details
                                            </Button>
                                            <Button
                                                className="flex-1"
                                                size="sm"
                                                onClick={() => navigate(`/contractor/jobs/${job.id}`)}
                                            >
                                                Start Job
                                            </Button>
                                        </div>
                                    </Card>
                                ))
                            ) : (
                                <Card hover={false}>
                                    <div className="text-center py-8">
                                        <Briefcase className="w-12 h-12 text-gray-700 dark:text-gray-500 mx-auto mb-4" />
                                        <p className="text-gray-600 dark:text-gray-400">No active jobs at the moment.</p>
                                        <Button variant="ghost" className="text-purple-500 mt-2">
                                            Browse Job Board
                                        </Button>
                                    </div>
                                </Card>
                            )}
                        </div>
                    </div>

                    {/* Available Jobs Preview */}
                    <div className="mt-8">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-xl font-bold text-gray-900 dark:text-white">New Opportunities</h2>
                            <Button variant="ghost" className="text-purple-500 hover:text-purple-600" onClick={() => navigate('/contractor/jobs')}>
                                View All
                                <ArrowRight className="w-4 h-4 ml-1" />
                            </Button>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {dashboardData?.available_jobs?.slice(0, 3).map((job: any) => (
                                <Card key={job.id} className="opacity-75 hover:opacity-100 transition-opacity">
                                    <div className="flex items-start justify-between">
                                        <div>
                                            <h3 className="font-semibold text-gray-900 dark:text-white">{job.property_address || job.address}</h3>
                                            <p className="text-sm text-gray-600 dark:text-gray-400">{job.customer_name || job.customer?.name}</p>
                                        </div>
                                        {job.is_project && (
                                            <Badge variant="info">Project</Badge>
                                        )}
                                    </div>

                                    <div className="flex items-center justify-between text-sm mt-4">
                                        <span className="text-gray-600 dark:text-gray-400">Estimated Pay:</span>
                                        <span className="font-semibold text-green-400">{formatCurrency(job.estimated_pay || job.total_amount || 280)}</span>
                                    </div>

                                    <Button className="w-full mt-4" size="sm" variant="outline" onClick={() => navigate('/contractor/jobs')}>
                                        View Details
                                    </Button>
                                </Card>
                            )) || (
                                <div className="col-span-3">
                                    <Card hover={false}>
                                        <div className="text-center py-8">
                                            <Briefcase className="w-12 h-12 text-gray-700 dark:text-gray-500 mx-auto mb-4" />
                                            <p className="text-gray-600 dark:text-gray-400">No available jobs matching your trade at the moment.</p>
                                            <p className="text-sm text-gray-700 dark:text-gray-500 mt-2">Check back later for new opportunities!</p>
                                        </div>
                                    </Card>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <button
                        onClick={() => navigate('/contractor/jobs')}
                        className="glass-card p-6 text-center hover:scale-[1.05] smooth-transition group"
                    >
                        <Briefcase className="w-8 h-8 text-purple-400 mx-auto mb-2 group-hover:scale-110 smooth-transition" />
                        <p className="text-sm font-medium text-gray-900 dark:text-white">Browse Jobs</p>
                    </button>

                    <button
                        onClick={() => navigate('/contractor/compliance')}
                        className="glass-card p-6 text-center hover:scale-[1.05] smooth-transition group"
                    >
                        <ShieldCheck className="w-8 h-8 text-blue-400 mx-auto mb-2 group-hover:scale-110 smooth-transition" />
                        <p className="text-sm font-medium text-gray-900 dark:text-white">Compliance</p>
                    </button>

                    <button
                        onClick={() => navigate('/contractor/wallet')}
                        className="glass-card p-6 text-center hover:scale-[1.05] smooth-transition group"
                    >
                        <WalletIcon className="w-8 h-8 text-green-400 mx-auto mb-2 group-hover:scale-110 smooth-transition" />
                        <p className="text-sm font-medium text-gray-900 dark:text-white">View Wallet</p>
                    </button>

                    <button
                        onClick={() => navigate('/contractor/jobs')}
                        className="glass-card p-6 text-center hover:scale-[1.05] smooth-transition group"
                    >
                        <TrendingUp className="w-8 h-8 text-pink-400 mx-auto mb-2 group-hover:scale-110 smooth-transition" />
                        <p className="text-sm font-medium text-gray-900 dark:text-white">My Activity</p>
                    </button>
                </div>
                <SupportWidget />
            </div>
        </PortalLayout>
    );
}
