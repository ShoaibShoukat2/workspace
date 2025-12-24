import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Badge, { getStatusBadgeVariant } from '@/components/ui/Badge';
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
    CheckCircle,
    Package
} from 'lucide-react';
import { disputes, resolveDispute, jobs, materialDeliveries } from '@/data/mockData';
import { formatDate } from '@/lib/utils';

export default function DisputeDetail() {
    const { disputeId } = useParams();
    const navigate = useNavigate();
    const [resolution, setResolution] = useState('');

    const dispute = disputes.find(d => d.id === Number(disputeId));

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

    if (!dispute) {
        return (
            <PortalLayout title="Dispute Not Found" navItems={navItems}>
                <Card className="text-center py-12">
                    <p className="text-gray-600 dark:text-gray-400">Dispute not found.</p>
                    <Button onClick={() => navigate('/admin/disputes')} className="mt-4">
                        Back to Disputes
                    </Button>
                </Card>
            </PortalLayout>
        );
    }

    const handleResolve = () => {
        if (!resolution.trim()) {
            alert('Please enter a resolution before marking as resolved.');
            return;
        }
        resolveDispute(dispute.id, resolution);
        alert('Dispute marked as resolved!');
        navigate('/admin/disputes');
    };

    return (
        <PortalLayout title={`Dispute #${dispute.id}`} navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                {/* Header */}
                <Card>
                    <div className="flex items-start justify-between mb-4">
                        <div>
                            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{dispute.title}</h2>
                            <div className="flex items-center space-x-3 text-sm text-gray-600 dark:text-gray-400">
                                <span>Job #{dispute.jobId}</span>
                                <span>•</span>
                                <span>Created by: {dispute.createdBy}</span>
                                <span>•</span>
                                <span>{formatDate(dispute.createdDate || '')}</span>
                            </div>
                        </div>
                        <Badge variant={getStatusBadgeVariant(dispute.status)}>{dispute.status}</Badge>
                    </div>
                </Card>

                {/* Description */}
                <Card>
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Description</h3>
                    <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{dispute.description}</p>
                </Card>

                {/* Material Context (if applicable) */}
                {jobs.find(j => j.id === dispute.jobId)?.materialStatus && (
                    <Card>
                        <h3 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                            <Package className="w-5 h-5 text-gray-500" />
                            Material Context
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <p className="text-sm font-medium text-gray-500 mb-1">Status</p>
                                <Badge variant={jobs.find(j => j.id === dispute.jobId)?.materialStatus === 'Issues Found' ? 'danger' : 'success'}>
                                    {jobs.find(j => j.id === dispute.jobId)?.materialStatus}
                                </Badge>
                                <p className="text-xs text-gray-400 mt-2">
                                    Delivery: {materialDeliveries.find(d => d.jobId === dispute.jobId)?.status || 'Pending'}
                                </p>
                            </div>
                            <div>
                                <p className="text-sm font-medium text-gray-500 mb-2">Delivery Proof</p>
                                <div className="flex gap-2">
                                    {materialDeliveries.find(d => d.jobId === dispute.jobId)?.photos?.map((_, i) => (
                                        <div key={i} className="w-20 h-20 bg-gray-100 rounded-lg border border-gray-200 flex items-center justify-center text-xs text-gray-400">
                                            Photo {i + 1}
                                        </div>
                                    )) || <p className="text-sm text-gray-400 italic">No photos uploaded.</p>}
                                </div>
                            </div>
                        </div>
                    </Card>
                )}

                {/* Resolution Section */}
                {dispute.status === 'Open' ? (
                    <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
                        <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Resolve Dispute</h3>
                        <textarea
                            value={resolution}
                            onChange={(e) => setResolution(e.target.value)}
                            rows={6}
                            className="w-full px-4 py-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent smooth-transition resize-none mb-4"
                            placeholder="Enter resolution details, actions taken, and outcome..."
                        />
                        <div className="flex space-x-3">
                            <Button variant="primary" onClick={handleResolve}>
                                <CheckCircle className="w-4 h-4 mr-2" />
                                Mark as Resolved
                            </Button>
                            <Button variant="outline" onClick={() => navigate('/admin/disputes')}>
                                Cancel
                            </Button>
                        </div>
                    </Card>
                ) : (
                    <Card className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
                        <h3 className="font-semibold text-green-800 dark:text-green-300 mb-3 flex items-center">
                            <CheckCircle className="w-5 h-5 mr-2" />
                            Resolved
                        </h3>
                        <p className="text-gray-700 dark:text-gray-300">{dispute.resolution}</p>
                    </Card>
                )}
            </div>
        </PortalLayout>
    );
}
