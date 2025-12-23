import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
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
    Loader2
} from 'lucide-react';
import { adminApiService } from '@/lib/adminApi';
import { formatCurrency, formatDate } from '@/lib/utils';

export default function PayoutApproval() {
    const navigate = useNavigate();
    const { user } = useAuth();
    
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [payouts, setPayouts] = useState<any[]>([]);
    const [processing, setProcessing] = useState<number | null>(null);

    useEffect(() => {
        const fetchPayouts = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = await adminApiService.getPayouts();
                setPayouts(data.results || data);
            } catch (err) {
                console.error('Failed to fetch payouts:', err);
                setError(err instanceof Error ? err.message : 'Failed to load payouts');
            } finally {
                setLoading(false);
            }
        };

        fetchPayouts();
    }, []);

    const handleApprove = async (jobId: number) => {
        try {
            setProcessing(jobId);
            await adminApiService.approveJobPayout(jobId);
            
            // Refresh payouts
            const data = await adminApiService.getPayouts();
            setPayouts(data.results || data);
            
            alert('Payout approved and processed!');
        } catch (err) {
            console.error('Failed to approve payout:', err);
            alert('Failed to approve payout. Please try again.');
        } finally {
            setProcessing(null);
        }
    };

    const handleDecline = async (jobId: number) => {
        const reason = prompt('Please enter reason for declining:');
        if (!reason) return;

        try {
            setProcessing(jobId);
            await adminApiService.rejectJobPayout(jobId, reason);
            
            // Refresh payouts
            const data = await adminApiService.getPayouts();
            setPayouts(data.results || data);
            
            alert('Payout declined.');
        } catch (err) {
            console.error('Failed to decline payout:', err);
            alert('Failed to decline payout. Please try again.');
        } finally {
            setProcessing(null);
        }
    };

    if (loading) {
        return (
            <PortalLayout title="Payout Approval" navItems={navItems}>
                <div className="flex items-center justify-center h-64">
                    <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                    <span className="ml-2 text-gray-600">Loading payouts...</span>
                </div>
            </PortalLayout>
        );
    }

    if (error) {
        return (
            <PortalLayout title="Payout Approval" navItems={navItems}>
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

    const pendingPayouts = payouts.filter(p => p.status === 'Processing' || p.status === 'processing' || p.status === 'pending');
    const approvedPayouts = payouts.filter(p => p.status === 'Paid' || p.status === 'paid' || p.status === 'approved');

    return (
        <PortalLayout title="Payout Approval" navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                {/* Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card hover={false} className="bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800">
                        <div className="flex items-center space-x-3">
                            <DollarSign className="w-10 h-10 text-yellow-600 dark:text-yellow-400" />
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Pending</p>
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">{pendingPayouts.length}</p>
                                <p className="text-xs text-gray-500 dark:text-gray-500">
                                    {formatCurrency(pendingPayouts.reduce((sum, p) => sum + (p.amount || p.total_amount || 0), 0))}
                                </p>
                            </div>
                        </div>
                    </Card>

                    <Card hover={false} className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
                        <div className="flex items-center space-x-3">
                            <CheckCircle className="w-10 h-10 text-green-600 dark:text-green-400" />
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Approved</p>
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">{approvedPayouts.length}</p>
                                <p className="text-xs text-gray-500 dark:text-gray-500">
                                    {formatCurrency(approvedPayouts.reduce((sum, p) => sum + (p.amount || p.total_amount || 0), 0))}
                                </p>
                            </div>
                        </div>
                    </Card>

                    <Card hover={false} className="bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800">
                        <div className="flex items-center space-x-3">
                            <DollarSign className="w-10 h-10 text-purple-600 dark:text-purple-400" />
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total</p>
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">{payouts.length}</p>
                                <p className="text-xs text-gray-500 dark:text-gray-500">
                                    {formatCurrency(payouts.reduce((sum, p) => sum + (p.amount || p.total_amount || 0), 0))}
                                </p>
                            </div>
                        </div>
                    </Card>
                </div>

                {/* Pending Payouts */}
                {pendingPayouts.length > 0 && (
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Pending Approvals</h2>
                        <div className="space-y-4">
                            {pendingPayouts.map((payout) => {
                                return (
                                    <Card key={payout.id}>
                                        <div className="flex items-start justify-between gap-4">
                                            <div className="flex-1">
                                                <div className="flex items-center space-x-2 mb-2">
                                                    <Badge variant="warning">Pending</Badge>
                                                    <span className="text-sm text-gray-500 dark:text-gray-400">Job #{payout.job_id || payout.jobId}</span>

                                                    {payout.has_dispute && (
                                                        <Badge variant="danger" className=" animate-pulse">Open Dispute</Badge>
                                                    )}
                                                    {payout.material_issues && (
                                                        <Badge variant="danger">Material Issue</Badge>
                                                    )}
                                                </div>
                                                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                                                    {payout.contractor_name || payout.contractor?.name || 'Unknown Contractor'}
                                                </h3>
                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                                    <div>
                                                        <span className="text-gray-500 dark:text-gray-400">Job Type:</span>
                                                        <p className="font-medium text-gray-900 dark:text-white capitalize">{payout.job_type || payout.jobType}</p>
                                                    </div>
                                                    <div>
                                                        <span className="text-gray-500 dark:text-gray-400">Labor:</span>
                                                        <p className="font-medium text-gray-900 dark:text-white">{formatCurrency(payout.labor_amount || payout.amount || 0)}</p>
                                                    </div>
                                                    <div>
                                                        <span className="text-gray-500 dark:text-gray-400">Materials:</span>
                                                        <p className="font-medium text-gray-900 dark:text-white">
                                                            {(payout.material_reimbursed || payout.materialReimbursed || 0) > 0 ? formatCurrency(payout.material_reimbursed || payout.materialReimbursed) : 'N/A'}
                                                        </p>
                                                    </div>
                                                    <div>
                                                        <span className="text-gray-500 dark:text-gray-400">Total:</span>
                                                        <p className="font-semibold text-purple-600 dark:text-purple-400 text-lg">
                                                            {formatCurrency((payout.labor_amount || payout.amount || 0) + (payout.material_reimbursed || payout.materialReimbursed || 0))}
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="flex flex-col gap-2">
                                                <Button
                                                    variant="primary"
                                                    size="sm"
                                                    onClick={() => handleApprove(payout.job_id || payout.jobId)}
                                                    disabled={
                                                        processing === (payout.job_id || payout.jobId) ||
                                                        payout.has_dispute ||
                                                        payout.material_issues ||
                                                        (payout.mandatory_site_visit && payout.visit_status !== 'Completed')
                                                    }
                                                    title={
                                                        payout.has_dispute ? "Cannot approve: Open Dispute" :
                                                            payout.material_issues ? "Cannot approve: Material Issues" :
                                                                (payout.mandatory_site_visit && payout.visit_status !== 'Completed') ? "Cannot approve: Incomplete FM Visit" :
                                                                    "Approve Payout"
                                                    }
                                                >
                                                    {processing === (payout.job_id || payout.jobId) ? (
                                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                                    ) : (
                                                        <CheckCircle className="w-4 h-4 mr-2" />
                                                    )}
                                                    Approve
                                                </Button>
                                                <Button 
                                                    variant="danger" 
                                                    size="sm" 
                                                    onClick={() => handleDecline(payout.job_id || payout.jobId)}
                                                    disabled={processing === (payout.job_id || payout.jobId)}
                                                >
                                                    <XCircle className="w-4 h-4 mr-2" />
                                                    Decline
                                                </Button>
                                            </div>
                                        </div>
                                    </Card>
                                );
                            })}
                        </div>
                    </div>
                )}

                {/* Approved Payouts */}
                {approvedPayouts.length > 0 && (
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Approved Payouts</h2>
                        <Card>
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead>
                                        <tr className="border-b border-gray-200 dark:border-gray-700">
                                            <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Contractor</th>
                                            <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Job</th>
                                            <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Amount</th>
                                            <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Payment Date</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {approvedPayouts.map((payout) => (
                                            <tr key={payout.id} className="border-b border-gray-100 dark:border-gray-800">
                                                <td className="py-3 px-4 text-gray-900 dark:text-white">
                                                    {payout.contractor_name || payout.contractor?.name || 'Unknown'}
                                                </td>
                                                <td className="py-3 px-4 text-gray-700 dark:text-gray-300">#{payout.job_id || payout.jobId}</td>
                                                <td className="py-3 px-4 text-right font-semibold text-green-600 dark:text-green-400">
                                                    {formatCurrency((payout.labor_amount || payout.amount || 0) + (payout.material_reimbursed || payout.materialReimbursed || 0))}
                                                </td>
                                                <td className="py-3 px-4 text-gray-700 dark:text-gray-300">
                                                    {(payout.payment_date || payout.paymentDate) ? formatDate(payout.payment_date || payout.paymentDate) : '-'}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </Card>
                    </div>
                )}

                {payouts.length === 0 && (
                    <Card className="text-center py-12">
                        <DollarSign className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No Payouts</h3>
                        <p className="text-gray-600 dark:text-gray-400">All payouts have been processed.</p>
                    </Card>
                )}
            </div>
        </PortalLayout>
    );
}
