import { useNavigate } from 'react-router-dom';
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
    FileText,
    Briefcase,
    Calendar,
    Users,
    ChevronRight
} from 'lucide-react';
import { adminApiService } from '@/lib/adminApi';
import { formatDate } from '@/lib/utils';

export default function DisputeList() {
    const navigate = useNavigate();
    const [disputes, setDisputes] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchDisputes = async () => {
            try {
                setLoading(true);
                setError(null);
                const response = await adminApiService.getDisputes({ limit: 100 });
                setDisputes(response.results);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load disputes');
            } finally {
                setLoading(false);
            }
        };

        fetchDisputes();
    }, []);

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

    const openDisputes = disputes.filter(d => d.status === 'Open' || d.status === 'open');
    const resolvedDisputes = disputes.filter(d => d.status === 'Resolved' || d.status === 'resolved');

    if (loading) {
        return (
            <PortalLayout title="Dispute Resolution" navItems={navItems}>
                <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                    <span className="ml-3 text-gray-600 dark:text-gray-400">Loading disputes...</span>
                </div>
            </PortalLayout>
        );
    }

    if (error) {
        return (
            <PortalLayout title="Dispute Resolution" navItems={navItems}>
                <Card className="text-center py-12">
                    <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
                    <Button onClick={() => window.location.reload()}>Retry</Button>
                </Card>
            </PortalLayout>
        );
    }

    return (
        <PortalLayout title="Dispute Resolution" navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                {/* Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card hover={false} className="bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
                        <div className="flex items-center space-x-3">
                            <AlertTriangle className="w-10 h-10 text-red-600 dark:text-red-400" />
                            <div>
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">{openDisputes.length}</p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">Open Disputes</p>
                            </div>
                        </div>
                    </Card>

                    <Card hover={false} className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
                        <div className="flex items-center space-x-3">
                            <AlertTriangle className="w-10 h-10 text-green-600 dark:text-green-400" />
                            <div>
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">{resolvedDisputes.length}</p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">Resolved</p>
                            </div>
                        </div>
                    </Card>

                    <Card hover={false} className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
                        <div className="flex items-center space-x-3">
                            <AlertTriangle className="w-10 h-10 text-blue-600 dark:text-blue-400" />
                            <div>
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">{disputes.length}</p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">Total</p>
                            </div>
                        </div>
                    </Card>
                </div>

                {/* Open Disputes */}
                {openDisputes.length > 0 && (
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Open Disputes</h2>
                        <div className="space-y-4">
                            {openDisputes.map((dispute) => (
                                <Card key={dispute.id} className="hover:scale-[1.01]">
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center space-x-2 mb-2">
                                                <Badge variant="danger">Open</Badge>
                                                <span className="text-sm text-gray-500 dark:text-gray-400">Job #{dispute.job_id}</span>
                                                <span className="text-sm text-gray-500 dark:text-gray-400">•</span>
                                                <span className="text-sm text-gray-500 dark:text-gray-400">
                                                    Messages: {dispute.messages_count || 0}
                                                </span>
                                            </div>
                                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">{dispute.description}</h3>
                                            <p className="text-xs text-gray-500 dark:text-gray-500">
                                                Created: {formatDate(dispute.created_at || '')}
                                            </p>
                                        </div>
                                        <Button
                                            variant="primary"
                                            onClick={() => navigate(`/admin/disputes/${dispute.id}`)}
                                        >
                                            Review
                                            <ChevronRight className="w-4 h-4 ml-1" />
                                        </Button>
                                    </div>
                                </Card>
                            ))}
                        </div>
                    </div>
                )}

                {/* Resolved Disputes */}
                {resolvedDisputes.length > 0 && (
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Resolved Disputes</h2>
                        <div className="space-y-4">
                            {resolvedDisputes.map((dispute) => (
                                <Card key={dispute.id}>
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center space-x-2 mb-2">
                                                <Badge variant="success">Resolved</Badge>
                                                <span className="text-sm text-gray-500 dark:text-gray-400">Job #{dispute.job_id}</span>
                                            </div>
                                            <h3 className="font-semibold text-gray-900 dark:text-white mb-1">{dispute.description}</h3>
                                        </div>
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() => navigate(`/admin/disputes/${dispute.id}`)}
                                        >
                                            View
                                        </Button>
                                    </div>
                                </Card>
                            ))}
                        </div>
                    </div>
                )}

                {disputes.length === 0 && (
                    <Card className="text-center py-12">
                        <AlertTriangle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No Disputes</h3>
                        <p className="text-gray-600 dark:text-gray-400">All disputes have been resolved.</p>
                    </Card>
                )}
            </div>
        </PortalLayout>
    );
}
