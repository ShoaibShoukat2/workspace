import { useParams, useNavigate } from 'react-router-dom';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import { jobs, investorJobBreakdown } from '@/data/mockData';
import { formatCurrency } from '@/lib/utils';
import {
    ArrowLeft,
    Building,
    DollarSign,
    TrendingUp,
    AlertTriangle,
    FileText,
    LayoutDashboard,
    Users,
    PieChart as PieChartIcon
} from 'lucide-react';

export default function PropertyDetailView() {
    const { address } = useParams<{ address: string }>();
    const navigate = useNavigate();
    const decodedAddress = decodeURIComponent(address || '');

    const propertyJobs = jobs.filter(j => j.propertyAddress === decodedAddress && j.type === 'investor');

    // Aggregates
    const totalRevenue = propertyJobs.reduce((sum, j) => {
        const bd = investorJobBreakdown.find(b => b.jobId === j.id);
        return sum + (bd?.revenue || 0);
    }, 0);

    const totalProfit = propertyJobs.reduce((sum, j) => {
        const bd = investorJobBreakdown.find(b => b.jobId === j.id);
        return sum + (bd?.investorShare || 0);
    }, 0);

    const issueCount = propertyJobs.filter(j => j.disputeId).length;

    // Standard Investor Navigation
    const navItems = [
        { label: 'Dashboard', path: '/investor/dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
        { label: 'Work Orders', path: '/investor/orders', icon: <FileText className="w-5 h-5" /> },
        { label: 'Leads', path: '/investor/leads', icon: <Users className="w-5 h-5" /> },
        { label: 'Properties', path: '/investor/properties', icon: <Building className="w-5 h-5" /> },
        { label: 'Reports', path: '/investor/reports', icon: <PieChartIcon className="w-5 h-5" /> },
    ];

    if (!decodedAddress || propertyJobs.length === 0) {
        return (
            <PortalLayout title="Property Not Found" navItems={navItems}>
                <div className="p-8 text-center">
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">Property Not Found</h2>
                    <Button className="mt-4" onClick={() => navigate('/investor/dashboard')}>Back to Dashboard</Button>
                </div>
            </PortalLayout>
        );
    }

    return (
        <PortalLayout title={`Property: ${decodedAddress}`} navItems={navItems}>
            <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">

                {/* Header */}
                <div className="flex items-center space-x-4 mb-6">
                    <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
                        <ArrowLeft className="w-5 h-5 mr-2" />
                        Back
                    </Button>
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
                            <Building className="w-6 h-6 mr-3 text-purple-600" />
                            {decodedAddress}
                        </h1>
                        <p className="text-gray-500 dark:text-gray-400 ml-9">{propertyJobs[0].city}</p>
                    </div>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card>
                        <div className="flex items-center justify-between mb-2">
                            <h3 className="text-sm font-medium text-gray-500">Total Profit</h3>
                            <DollarSign className="w-5 h-5 text-green-500" />
                        </div>
                        <p className="text-3xl font-bold text-gray-900 dark:text-white">{formatCurrency(totalProfit)}</p>
                    </Card>
                    <Card>
                        <div className="flex items-center justify-between mb-2">
                            <h3 className="text-sm font-medium text-gray-500">Revenue</h3>
                            <TrendingUp className="w-5 h-5 text-blue-500" />
                        </div>
                        <p className="text-3xl font-bold text-gray-900 dark:text-white">{formatCurrency(totalRevenue)}</p>
                    </Card>
                    <Card>
                        <div className="flex items-center justify-between mb-2">
                            <h3 className="text-sm font-medium text-gray-500">Active Jobs</h3>
                            <FileText className="w-5 h-5 text-purple-500" />
                        </div>
                        <p className="text-3xl font-bold text-gray-900 dark:text-white">{propertyJobs.filter(j => ['Open', 'InProgress'].includes(j.status)).length}</p>
                    </Card>
                </div>

                {/* Issues Warning */}
                {issueCount > 0 && (
                    <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-center text-red-700 dark:text-red-400">
                        <AlertTriangle className="w-5 h-5 mr-2" />
                        <span className="font-medium">{issueCount} Flagged Issue(s) reported on this property. Check job details.</span>
                    </div>
                )}

                {/* Jobs List */}
                <Card>
                    <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-6">Work Orders History</h2>
                    <div className="space-y-4">
                        {propertyJobs.map(job => {
                            const breakdown = investorJobBreakdown.find(b => b.jobId === job.id);
                            return (
                                <div key={job.id} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 border border-gray-100 dark:border-gray-800 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                                    <div className="space-y-1 mb-4 sm:mb-0">
                                        <div className="flex items-center gap-2">
                                            <span className="font-semibold text-gray-900 dark:text-white">Job #{job.id}</span>
                                            <Badge variant={job.status === 'Complete' ? 'success' : 'default'}>{job.status}</Badge>
                                        </div>
                                        <p className="text-sm text-gray-500">{new Date(job.scheduledTime || '').toLocaleDateString()} - {job.trade}</p>
                                    </div>

                                    <div className="flex items-center gap-6">
                                        <div className="text-right">
                                            <p className="text-xs text-gray-500">Revenue</p>
                                            <p className="font-medium text-gray-900 dark:text-white">{formatCurrency(breakdown?.revenue || 0)}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-xs text-gray-500">Profit Share</p>
                                            <p className="font-bold text-green-600 dark:text-green-400">{formatCurrency(breakdown?.investorShare || 0)}</p>
                                        </div>
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                </Card>
            </div>
        </PortalLayout>
    );
}
