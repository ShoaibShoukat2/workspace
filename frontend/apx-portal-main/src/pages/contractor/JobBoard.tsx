import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Badge, { getStatusBadgeVariant } from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import {
    LayoutDashboard,
    ShieldCheck,
    Briefcase,
    Wallet as WalletIcon,
    Filter,
    MapPin,
    Clock,
    DollarSign,
    Package,
    Loader2,
    AlertCircle
} from 'lucide-react';
import SupportFloatingButton from '@/components/contractor/SupportFloatingButton';
import { contractorApiService } from '@/lib/contractorApi';
import { formatCurrency } from '@/lib/utils';

export default function JobBoard() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [filterStatus, setFilterStatus] = useState<'all' | 'available' | 'inprogress' | 'completed'>('available');
    const [filterCity, setFilterCity] = useState('all');
    
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [assignments, setAssignments] = useState<any[]>([]);
    const [activeJobs, setActiveJobs] = useState<any[]>([]);
    const [processing, setProcessing] = useState<number | null>(null);

    useEffect(() => {
        const fetchJobs = async () => {
            try {
                setLoading(true);
                setError(null);

                const [assignmentsData, activeJobsData] = await Promise.all([
                    contractorApiService.getAssignments(),
                    contractorApiService.getActiveJobs()
                ]);

                setAssignments(assignmentsData.results || assignmentsData);
                setActiveJobs(activeJobsData.results || activeJobsData);
            } catch (err) {
                console.error('Failed to fetch job board data:', err);
                setError(err instanceof Error ? err.message : 'Failed to load jobs');
            } finally {
                setLoading(false);
            }
        };

        fetchJobs();
    }, []);

    if (loading) {
        return (
            <PortalLayout title="Job Board" navItems={navItems}>
                <div className="flex items-center justify-center h-64">
                    <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
                    <span className="ml-2 text-gray-600">Loading jobs...</span>
                </div>
            </PortalLayout>
        );
    }

    if (error) {
        return (
            <PortalLayout title="Job Board" navItems={navItems}>
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

    const availableJobs = assignments.filter((j: any) => 
        j.status === 'Open' || j.status === 'open' || j.status === 'available'
    );

    const myActiveJobs = activeJobs.filter((j: any) => 
        j.status === 'InProgress' || j.status === 'in_progress' || j.status === 'active'
    );

    const myCompletedJobs = activeJobs.filter((j: any) => 
        j.status === 'Complete' || j.status === 'completed' || j.status === 'Paid' || j.status === 'paid'
    );

    const getFilteredJobs = () => {
        let filtered = filterStatus === 'available' ? availableJobs :
            filterStatus === 'inprogress' ? myActiveJobs :
                filterStatus === 'completed' ? myCompletedJobs :
                    [...availableJobs, ...myActiveJobs, ...myCompletedJobs];

        if (filterCity !== 'all') {
            filtered = filtered.filter((j: any) => (j.city || j.location) === filterCity);
        }

        return filtered;
    };

    const allJobs = [...assignments, ...activeJobs];
    const cities = ['all', ...Array.from(new Set(allJobs.map((j: any) => j.city || j.location).filter(Boolean)))];

    const handleAcceptJob = async (jobId: number) => {
        if (user?.compliance_status === 'blocked') {
            alert('You must fix compliance issues before accepting jobs. Please visit the Compliance Hub.');
            navigate('/contractor/compliance');
            return;
        }

        try {
            setProcessing(jobId);
            await contractorApiService.acceptJob(jobId);
            
            // Refresh data
            const [assignmentsData, activeJobsData] = await Promise.all([
                contractorApiService.getAssignments(),
                contractorApiService.getActiveJobs()
            ]);
            
            setAssignments(assignmentsData.results || assignmentsData);
            setActiveJobs(activeJobsData.results || activeJobsData);
            
            alert('Job accepted! You can now view it in "My Active Jobs".');
            setFilterStatus('inprogress');
        } catch (err) {
            console.error('Failed to accept job:', err);
            alert('Failed to accept job. Please try again.');
        } finally {
            setProcessing(null);
        }
    };

    const handleRejectJob = async (jobId: number) => {
        try {
            setProcessing(jobId);
            await contractorApiService.rejectJob(jobId);
            
            // Refresh assignments
            const assignmentsData = await contractorApiService.getAssignments();
            setAssignments(assignmentsData.results || assignmentsData);
            
            alert('Job rejected.');
        } catch (err) {
            console.error('Failed to reject job:', err);
            alert('Failed to reject job. Please try again.');
        } finally {
            setProcessing(null);
        }
    };

    const filteredJobs = getFilteredJobs();

    return (
        <PortalLayout title="Job Board" navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                {/* Filters */}
                <Card hover={false}>
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                        <div className="flex items-center space-x-2">
                            <Filter className="w-5 h-5 text-purple-400" />
                            <span className="font-semibold text-gray-900 dark:text-white">Filters</span>
                        </div>
                        <div className="flex flex-col sm:flex-row gap-3">
                            {/* Status Filter */}
                            <div className="flex gap-2">
                                {['available', 'inprogress', 'completed'].map((status) => (
                                    <button
                                        key={status}
                                        onClick={() => setFilterStatus(status as any)}
                                        className={`px-4 py-2 rounded-lg text-sm font-medium smooth-transition ${filterStatus === status
                                            ? 'bg-purple-500 text-white'
                                            : 'bg-white/5 text-gray-300 hover:bg-white/10'
                                            }`}
                                    >
                                        {status === 'available' ? 'Available' :
                                            status === 'inprogress' ? 'In Progress' : 'Completed'}
                                    </button>
                                ))}
                            </div>

                            {/* City Filter */}
                            <select
                                value={filterCity}
                                onChange={(e) => setFilterCity(e.target.value)}
                                className="px-4 py-2 rounded-lg bg-gray-100 dark:bg-white/5 border border-gray-200 dark:border-white/20 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-400"
                            >
                                {cities.map((city) => (
                                    <option key={city} value={city} className="bg-gray-800">
                                        {city === 'all' ? 'All Cities' : city}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>
                </Card>

                {/* Stats Bar */}
                <div className="grid grid-cols-3 gap-4">
                    <Card hover={false} className="text-center">
                        <p className="text-2xl font-bold text-gray-900 dark:text-white">{availableJobs.length}</p>
                        <p className="text-sm text-gray-400 mt-1">Available</p>
                    </Card>
                    <Card hover={false} className="text-center">
                        <p className="text-2xl font-bold text-purple-400">{myActiveJobs.length}</p>
                        <p className="text-sm text-gray-400 mt-1">In Progress</p>
                    </Card>
                    <Card hover={false} className="text-center">
                        <p className="text-2xl font-bold text-green-400">{myCompletedJobs.length}</p>
                        <p className="text-sm text-gray-400 mt-1">Completed</p>
                    </Card>
                </div>

                {/* Jobs Grid */}
                <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                        {filterStatus === 'available' ? 'Available Jobs' :
                            filterStatus === 'inprogress' ? 'My Active Jobs' : 'Completed Jobs'}
                        <span className="text-gray-400 text-lg ml-2">({filteredJobs.length})</span>
                    </h2>

                    {filteredJobs.length > 0 ? (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                            {filteredJobs.map((job: any) => (
                                <Card key={job.id} className="hover:scale-[1.02]">
                                    <div className="space-y-4">
                                        {/* Header */}
                                        <div className="flex items-start justify-between">
                                            <div>
                                                <h3 className="font-semibold text-gray-900 dark:text-white text-lg">{job.property_address || job.propertyAddress}</h3>
                                                <p className="text-sm text-gray-400">{job.customer_name || job.customerName}</p>
                                            </div>
                                            <div className="flex flex-col items-end gap-2">
                                                <Badge variant={getStatusBadgeVariant(job.status)}>
                                                    {job.status}
                                                </Badge>
                                                {(job.is_project || job.isProject) && (
                                                    <Badge variant="info">PROJECT</Badge>
                                                )}
                                            </div>
                                        </div>

                                        {/* Details Grid */}
                                        <div className="grid grid-cols-2 gap-3 text-sm">
                                            <div className="flex items-center space-x-2 text-gray-300">
                                                <MapPin className="w-4 h-4 text-blue-400" />
                                                <span>{job.city || job.location}</span>
                                            </div>
                                            <div className="flex items-center space-x-2 text-gray-300">
                                                <Clock className="w-4 h-4 text-purple-400" />
                                                <span>{job.trade || job.category}</span>
                                            </div>
                                            <div className="flex items-center space-x-2 text-gray-300">
                                                <DollarSign className="w-4 h-4 text-green-400" />
                                                <span className="font-semibold text-green-400">{formatCurrency(job.estimated_pay || job.total_amount || 420)}</span>
                                            </div>
                                            <div className="flex items-center space-x-2">
                                                <Package className="w-4 h-4 text-cyan-400" />
                                                <Badge variant={getStatusBadgeVariant(job.material_status || job.materialStatus || 'default')} className="text-xs">
                                                    {job.material_status || job.materialStatus || 'Pending'}
                                                </Badge>
                                            </div>
                                        </div>

                                        {/* Gate Code (if active) */}
                                        {filterStatus === 'inprogress' && (job.gate_code || job.gateCode) && (
                                            <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
                                                <p className="text-xs text-blue-300 mb-1">Gate Code:</p>
                                                <p className="font-mono text-lg font-bold text-blue-200">{job.gate_code || job.gateCode}</p>
                                            </div>
                                        )}

                                        {/* Actions */}
                                        <div className="flex gap-2">
                                            {filterStatus === 'available' && (
                                                <>
                                                    <Button
                                                        variant="primary"
                                                        size="sm"
                                                        className="flex-1"
                                                        onClick={() => handleAcceptJob(job.id)}
                                                        disabled={processing === job.id || user?.compliance_status === 'blocked'}
                                                    >
                                                        {processing === job.id ? (
                                                            <Loader2 className="w-4 h-4 animate-spin mr-2" />
                                                        ) : null}
                                                        {user?.compliance_status === 'blocked' ? 'Fix Compliance' : 'Accept Job'}
                                                    </Button>
                                                    <Button
                                                        variant="outline"
                                                        size="sm"
                                                        onClick={() => handleRejectJob(job.id)}
                                                        disabled={processing === job.id}
                                                    >
                                                        Reject
                                                    </Button>
                                                </>
                                            )}
                                            {filterStatus === 'inprogress' && (
                                                <Button
                                                    variant="primary"
                                                    size="sm"
                                                    className="flex-1"
                                                    onClick={() => navigate(`/contractor/jobs/${job.id}`)}
                                                >
                                                    Work on Job →
                                                </Button>
                                            )}
                                            {filterStatus === 'completed' && (
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    className="flex-1"
                                                    onClick={() => navigate(`/contractor/jobs/${job.id}`)}
                                                >
                                                    View Details
                                                </Button>
                                            )}
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => alert('Job details: ' + JSON.stringify(job, null, 2))}
                                            >
                                                <Briefcase className="w-4 h-4" />
                                            </Button>
                                        </div>
                                    </div>
                                </Card>
                            ))}
                        </div>
                    ) : (
                        <Card hover={false}>
                            <div className="text-center py-12">
                                <Briefcase className="w-16 h-16 text-gray-500 mx-auto mb-4" />
                                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No Jobs Found</h3>
                                <p className="text-gray-400">
                                    {filterStatus === 'available' && 'No available jobs matching your trade and filters.'}
                                    {filterStatus === 'inprogress' && 'You have no active jobs. Check the Available tab.'}
                                    {filterStatus === 'completed' && 'You haven\'t completed any jobs yet.'}
                                </p>
                            </div>
                        </Card>
                    )}
                </div>
            </div>
        </PortalLayout>
    );
}
