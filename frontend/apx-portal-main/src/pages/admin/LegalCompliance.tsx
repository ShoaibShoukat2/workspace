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
    CheckCircle,
    XCircle,
    AlertCircle
} from 'lucide-react';
import { adminApiService } from '@/lib/adminApi';
import { formatDate } from '@/lib/utils';

export default function LegalCompliance() {
    const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'blocked'>('all');
    const [compliance, setCompliance] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [processing, setProcessing] = useState<number | null>(null);

    useEffect(() => {
        const fetchCompliance = async () => {
            try {
                setLoading(true);
                setError(null);
                const response = await adminApiService.getCompliance({ limit: 100 });
                setCompliance(response.results);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load compliance data');
            } finally {
                setLoading(false);
            }
        };

        fetchCompliance();
    }, []);

    const filteredCompliance = compliance.filter(c =>
        filterStatus === 'all' ? true : c.status === filterStatus
    );

    const handleApprove = async (complianceId: number) => {
        try {
            setProcessing(complianceId);
            await adminApiService.approveCompliance(complianceId);
            // Refresh data
            const response = await adminApiService.getCompliance({ limit: 100 });
            setCompliance(response.results);
            alert('Compliance approved successfully!');
        } catch (err) {
            alert('Failed to approve compliance. Please try again.');
        } finally {
            setProcessing(null);
        }
    };

    const handleReject = async (complianceId: number) => {
        const reason = prompt('Please enter rejection reason:');
        if (!reason) return;

        try {
            setProcessing(complianceId);
            await adminApiService.rejectCompliance(complianceId, reason);
            // Refresh data
            const response = await adminApiService.getCompliance({ limit: 100 });
            setCompliance(response.results);
            alert('Compliance rejected successfully!');
        } catch (err) {
            alert('Failed to reject compliance. Please try again.');
        } finally {
            setProcessing(null);
        }
    };

    return (
        <PortalLayout title="Legal & Compliance" navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                {/* Filters */}
                <Card hover={false}>
                    <div className="flex items-center justify-between">
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Contractor Compliance</h2>
                        <div className="flex space-x-2">
                            {['all', 'active', 'blocked'].map((status) => (
                                <button
                                    key={status}
                                    onClick={() => setFilterStatus(status as any)}
                                    className={`px-4 py-2 rounded-lg text-sm font-medium smooth-transition ${filterStatus === status
                                        ? 'bg-purple-500 text-white'
                                        : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                                        }`}
                                >
                                    {status === 'all' ? 'All' : status === 'active' ? 'Active' : 'Blocked'}
                                </button>
                            ))}
                        </div>
                    </div>
                </Card>

                {/* Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card hover={false} className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
                        <div className="flex items-center space-x-3">
                            <CheckCircle className="w-10 h-10 text-green-600 dark:text-green-400" />
                            <div>
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                                    {compliance.filter(c => c.status === 'approved').length}
                                </p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">Approved</p>
                            </div>
                        </div>
                    </Card>

                    <Card hover={false} className="bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
                        <div className="flex items-center space-x-3">
                            <XCircle className="w-10 h-10 text-red-600 dark:text-red-400" />
                            <div>
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                                    {compliance.filter(c => c.status === 'rejected').length}
                                </p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">Rejected</p>
                            </div>
                        </div>
                    </Card>

                    <Card hover={false} className="bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800">
                        <div className="flex items-center space-x-3">
                            <AlertCircle className="w-10 h-10 text-yellow-600 dark:text-yellow-400" />
                            <div>
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                                    {compliance.filter(c => c.status === 'pending').length}
                                </p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">Pending</p>
                            </div>
                        </div>
                    </Card>
                </div>

                {/* Contractors List */}
                <div className="space-y-4">
                    {filteredCompliance.map((item) => (
                        <Card key={item.id}>
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center space-x-3 mb-2">
                                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{item.contractor_name}</h3>
                                        <Badge variant={item.status === 'approved' ? 'success' : item.status === 'rejected' ? 'danger' : 'warning'}>
                                            {item.status}
                                        </Badge>
                                    </div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                                        Document: {item.document_type} • Contractor ID: {item.contractor_id}
                                    </p>

                                    <div className="text-sm">
                                        <p className="text-gray-600 dark:text-gray-400">
                                            Expiry: {formatDate(item.expiry_date)}
                                        </p>
                                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                                            Submitted: {formatDate(item.created_at)}
                                        </p>
                                    </div>
                                </div>

                                <div className="flex space-x-2">
                                    {item.status === 'pending' && (
                                        <>
                                            <Button 
                                                variant="primary" 
                                                size="sm" 
                                                onClick={() => handleApprove(item.id)}
                                                disabled={processing === item.id}
                                            >
                                                {processing === item.id ? (
                                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                                ) : (
                                                    <>
                                                        <CheckCircle className="w-4 h-4 mr-2" />
                                                        Approve
                                                    </>
                                                )}
                                            </Button>
                                            <Button 
                                                variant="danger" 
                                                size="sm" 
                                                onClick={() => handleReject(item.id)}
                                                disabled={processing === item.id}
                                            >
                                                <XCircle className="w-4 h-4 mr-2" />
                                                Reject
                                            </Button>
                                        </>
                                    )}
                                </div>
                            </div>
                        </Card>
                    ))}
                    {filteredCompliance.length === 0 && (
                        <Card className="text-center py-12">
                            <p className="text-gray-500">No compliance documents found for the selected filter.</p>
                        </Card>
                    )}
                </div>
            </div>
        </PortalLayout>
    );
}
