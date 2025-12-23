import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Badge, { getStatusBadgeVariant } from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { adminApiService, JobData } from '@/lib/adminApi';
import { Search, Eye, LayoutDashboard, Briefcase, ShieldCheck, AlertTriangle, FileText, DollarSign, Calendar, Users } from 'lucide-react';

export default function AdminJobList() {
    const location = useLocation();
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState<string>('All');
    const [jobs, setJobs] = useState<JobData[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Set initial filter from navigation state if present
    useEffect(() => {
        if (location.state && location.state.status) {
            setStatusFilter(location.state.status);
        }
    }, [location]);

    // Fetch jobs from API
    useEffect(() => {
        const fetchJobs = async () => {
            try {
                setLoading(true);
                setError(null);
                const response = await adminApiService.getJobs({ limit: 100 });
                setJobs(response.results);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load jobs');
            } finally {
                setLoading(false);
            }
        };

        fetchJobs();
    }, []);

    const filteredJobs = jobs.filter(job => {
        const matchesSearch =
            job.address.toLowerCase().includes(searchTerm.toLowerCase()) ||
            job.customer_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
            job.title.toLowerCase().includes(searchTerm.toLowerCase());

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

                <Card>
                    {loading ? (
                        <div className="flex items-center justify-center py-12">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                            <span className="ml-3 text-gray-600 dark:text-gray-400">Loading jobs...</span>
                        </div>
                    ) : error ? (
                        <div className="text-center py-12">
                            <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
                            <Button onClick={() => window.location.reload()}>Retry</Button>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left">
                                <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-800">
                                    <tr>
                                        <th className="py-3 px-4 font-medium">Job ID</th>
                                        <th className="py-3 px-4 font-medium">Title</th>
                                        <th className="py-3 px-4 font-medium">Property</th>
                                        <th className="py-3 px-4 font-medium">Customer</th>
                                        <th className="py-3 px-4 font-medium">Status</th>
                                        <th className="py-3 px-4 font-medium">Assigned To</th>
                                        <th className="py-3 px-4 font-medium text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                                    {filteredJobs.map(job => (
                                        <tr key={job.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                                            <td className="py-3 px-4 font-mono text-gray-600 dark:text-gray-400">#{job.id}</td>
                                            <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">{job.title}</td>
                                            <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">{job.address}</td>
                                            <td className="py-3 px-4 text-gray-600 dark:text-gray-400">{job.customer_email}</td>
                                            <td className="py-3 px-4">
                                                <Badge variant={getStatusBadgeVariant(job.status)}>{job.status}</Badge>
                                            </td>
                                            <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                                                {job.assigned_contractor || 'Unassigned'}
                                            </td>
                                            <td className="py-3 px-4 text-right">
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() => {
                                                        alert(`Viewing Job #${job.id} details - ${job.title}`);
                                                    }}
                                                >
                                                    <Eye className="w-4 h-4" />
                                                </Button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            {filteredJobs.length === 0 && !loading && (
                                <div className="text-center py-12 text-gray-500">
                                    No jobs found matching your filters.
                                </div>
                            )}
                        </div>
                    )}
                </Card>
            </div>
        </PortalLayout>
    );
}
