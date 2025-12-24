import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { adminApi } from '@/services/adminApi';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Badge, { getStatusBadgeVariant } from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Search, Eye, LayoutDashboard, Briefcase, ShieldCheck, AlertTriangle, FileText, DollarSign, Calendar, Users } from 'lucide-react';

export default function AdminJobList() {
    const location = useLocation();
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState<string>('All');
    const [jobs, setJobs] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadJobs();
        // Set initial filter from navigation state if present
        if (location.state && location.state.status) {
            setStatusFilter(location.state.status);
        }
    }, [location]);

    const loadJobs = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await adminApi.getJobs();
            setJobs(data.jobs || []);
        } catch (err: any) {
            console.error('Failed to load jobs:', err);
            setError('Failed to load jobs. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const filteredJobs = jobs.filter(job => {
        const matchesSearch =
            (job.property_address || job.propertyAddress || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
            (job.customer_name || job.customerName || '').toLowerCase().includes(searchTerm.toLowerCase());

        let matchesStatus = true;
        if (statusFilter === 'All') {
            matchesStatus = true;
        } else if (statusFilter === 'Active') {
            matchesStatus = job.status === 'Open' || job.status === 'InProgress';
        } else {
            matchesStatus = job.status === statusFilter;
        }

        return matchesSearch && matchesStatus;
    });

    const categories = ['All', 'Active', 'Open', 'InProgress', 'Complete', 'Paid', 'Cancelled'];

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

    return (
        <PortalLayout title="All Jobs" navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                <div className="flex flex-col md:flex-row gap-4 justify-between items-center">
                    <div className="relative w-full md:w-96">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <Input
                            placeholder="Search jobs..."
                            className="pl-10"
                            value={searchTerm}
                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <div className="flex gap-2 overflow-x-auto pb-2 w-full md:w-auto">
                        {categories.map(cat => (
                            <Button
                                key={cat}
                                variant={statusFilter === cat ? 'primary' : 'outline'}
                                size="sm"
                                onClick={() => setStatusFilter(cat)}
                            >
                                {cat}
                            </Button>
                        ))}
                    </div>
                </div>

                {loading ? (
                    <div className="flex items-center justify-center h-64">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                    </div>
                ) : error ? (
                    <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                        <p className="text-red-700 dark:text-red-400">{error}</p>
                        <button 
                            onClick={loadJobs}
                            className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                        >
                            Retry
                        </button>
                    </div>
                ) : (
                    <Card>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left">
                            <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-800">
                                <tr>
                                    <th className="py-3 px-4 font-medium">Job ID</th>
                                    <th className="py-3 px-4 font-medium">Property</th>
                                    <th className="py-3 px-4 font-medium">Customer</th>
                                    <th className="py-3 px-4 font-medium">Type</th>
                                    <th className="py-3 px-4 font-medium">Status</th>
                                    <th className="py-3 px-4 font-medium">Assigned To</th>
                                    <th className="py-3 px-4 font-medium text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                                {filteredJobs.map(job => (
                                    <tr key={job.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                                        <td className="py-3 px-4 font-mono text-gray-600 dark:text-gray-400">#{job.id}</td>
                                        <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">
                                            {job.property_address || job.propertyAddress || 'N/A'}
                                        </td>
                                        <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                                            {job.customer_name || job.customerName || 'N/A'}
                                        </td>
                                        <td className="py-3 px-4 text-gray-600 dark:text-gray-400 capitalize">
                                            {job.job_type || job.type || 'N/A'}
                                        </td>
                                        <td className="py-3 px-4">
                                            <Badge variant={getStatusBadgeVariant(job.status)}>{job.status}</Badge>
                                        </td>
                                        <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                                            {job.assigned_contractor_id || job.assignedContractorId ? 
                                                `Contractor #${job.assigned_contractor_id || job.assignedContractorId}` : 
                                                'Unassigned'
                                            }
                                        </td>
                                        <td className="py-3 px-4 text-right">
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => {
                                                    alert(`Viewing Job #${job.id} details`);
                                                }}
                                            >
                                                <Eye className="w-4 h-4" />
                                            </Button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {filteredJobs.length === 0 && (
                            <div className="text-center py-12 text-gray-500">
                                No jobs found matching your filters.
                            </div>
                        )}
                    </div>
                </Card>
                )}
            </div>
        </PortalLayout>
    );
}
