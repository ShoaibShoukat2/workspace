import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Badge, { getStatusBadgeVariant } from '@/components/ui/Badge';
import {
    LayoutDashboard,
    ShieldCheck,
    Briefcase,
    Wallet as WalletIcon,
    DollarSign,
    TrendingUp,
    Calendar,
    Package
} from 'lucide-react';
import { contractorApiService } from '@/lib/contractorApi';
import { formatCurrency, formatDate } from '@/lib/utils';
import Button from '@/components/ui/Button';
import Button from '@/components/ui/Button';

export default function Wallet() {
    const navigate = useNavigate();
    const { currentUser } = useAuth();

    const [walletData, setWalletData] = useState<any>(null);
    const [transactions, setTransactions] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchWalletData = async () => {
            try {
                setLoading(true);
                setError(null);
                
                const [wallet, transactionData] = await Promise.all([
                    contractorApiService.getWallet(),
                    contractorApiService.getWalletTransactions(50)
                ]);
                
                setWalletData(wallet);
                setTransactions(transactionData);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load wallet data');
            } finally {
                setLoading(false);
            }
        };

        fetchWalletData();
    }, []);

    const navItems = [
        { label: 'Dashboard', path: '/contractor/dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
        { label: 'Job Board', path: '/contractor/jobs', icon: <Briefcase className="w-5 h-5" /> },
        { label: 'Compliance Hub', path: '/contractor/compliance', icon: <ShieldCheck className="w-5 h-5" /> },
        { label: 'Wallet', path: '/contractor/wallet', icon: <WalletIcon className="w-5 h-5" /> },
    ];

    const myPayouts = transactions.filter((t: any) => t.type === 'payout');
    const totalPaid = walletData?.total_earned || 0;
    const pendingPayouts = walletData?.pending_payout || 0;

    if (loading) {
        return (
            <PortalLayout title="Wallet & Payouts" navItems={navItems}>
                <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                    <span className="ml-3 text-gray-600 dark:text-gray-400">Loading wallet data...</span>
                </div>
            </PortalLayout>
        );
    }

    if (error) {
        return (
            <PortalLayout title="Wallet & Payouts" navItems={navItems}>
                <Card className="text-center py-12">
                    <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
                    <Button onClick={() => window.location.reload()}>Retry</Button>
                </Card>
            </PortalLayout>
        );
    }

    return (
        <PortalLayout title="Wallet & Payouts" navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card hover={false} className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 border-green-500/30">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-300 mb-1">Total Paid</p>
                                <p className="text-4xl font-bold text-white">{formatCurrency(totalPaid)}</p>
                                <div className="flex items-center space-x-2 mt-3">
                                    <TrendingUp className="w-4 h-4 text-green-400" />
                                    <span className="text-sm text-green-400">All time earnings</span>
                                </div>
                            </div>
                            <div className="w-20 h-20 rounded-full bg-green-500/20 flex items-center justify-center">
                                <DollarSign className="w-10 h-10 text-green-400" />
                            </div>
                        </div>
                    </Card>

                    <Card hover={false} className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 border-purple-500/30">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-300 mb-1">Pending Payouts</p>
                                <p className="text-4xl font-bold text-white">{formatCurrency(pendingPayouts)}</p>
                                <div className="flex items-center space-x-2 mt-3">
                                    <Calendar className="w-4 h-4 text-purple-400" />
                                    <span className="text-sm text-purple-400">Awaiting approval</span>
                                </div>
                            </div>
                            <div className="w-20 h-20 rounded-full bg-purple-500/20 flex items-center justify-center">
                                <WalletIcon className="w-10 h-10 text-purple-400" />
                            </div>
                        </div>
                    </Card>
                </div>

                {/* Payouts Table */}
                <div>
                    <h2 className="text-2xl font-bold text-white mb-4">Payout History</h2>
                    {myPayouts.length > 0 ? (
                        <Card hover={false}>
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead>
                                        <tr className="border-b border-white/10">
                                            <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Transaction ID</th>
                                            <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Type</th>
                                            <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Amount</th>
                                            <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Status</th>
                                            <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Date</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {myPayouts.map((transaction: any) => (
                                            <tr key={transaction.id} className="border-b border-white/5 hover:bg-white/5 smooth-transition">
                                                <td className="py-4 px-4">
                                                    <span className="font-mono text-purple-400">#{transaction.id}</span>
                                                </td>
                                                <td className="py-4 px-4">
                                                    <Badge variant={transaction.job_type === 'investor' ? 'info' : 'default'}>
                                                        {transaction.type || 'payout'}
                                                    </Badge>
                                                </td>
                                                <td className="py-4 px-4">
                                                    <span className="font-semibold text-green-400 text-lg">
                                                        {formatCurrency(transaction.amount)}
                                                    </span>
                                                </td>
                                                <td className="py-4 px-4">
                                                    <Badge variant={getStatusBadgeVariant(transaction.status)}>
                                                        {transaction.status}
                                                    </Badge>
                                                </td>
                                                <td className="py-4 px-4 text-gray-300">
                                                    {transaction.created_at ? formatDate(transaction.created_at) : '-'}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </Card>
                    ) : (
                        <Card hover={false}>
                            <div className="text-center py-12">
                                <WalletIcon className="w-16 h-16 text-gray-500 mx-auto mb-4" />
                                <h3 className="text-xl font-semibold text-white mb-2">No Transactions Yet</h3>
                                <p className="text-gray-400">Complete jobs to start earning. Transactions appear here once processed.</p>
                            </div>
                        </Card>
                    )}
                </div>

                {/* Important Info */}
                <Card className="bg-blue-500/10 border-blue-500/30">
                    <h4 className="font-semibold text-blue-300 mb-2">Payment Information</h4>
                    <ul className="space-y-2 text-sm text-blue-200">
                        <li>• Payouts are processed after admin approval</li>
                        <li>• Material reimbursements (if applicable) are included separately</li>
                        <li>• Payment typically takes 3-5 business days after approval</li>
                        <li>• All payouts follow the agreed payment terms from your contractor agreement</li>
                    </ul>
                </Card>
            </div>
        </PortalLayout>
    );
}
