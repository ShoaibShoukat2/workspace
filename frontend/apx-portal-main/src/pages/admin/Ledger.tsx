import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import {
    LayoutDashboard,
    ShieldCheck,
    AlertTriangle,
    DollarSign,
    FileText,
    Briefcase,
    Calendar,
    Users,
    TrendingUp,
    TrendingDown
} from 'lucide-react';
import { contractorPayouts, materialOrders } from '@/data/mockData';
import { formatCurrency, formatDate } from '@/lib/utils';

export default function Ledger() {
    const navigate = useNavigate();
    const { currentUser } = useAuth();

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

    const totalPayouts = contractorPayouts.reduce((sum, p) => sum + p.amount, 0);
    const totalMaterials = materialOrders.reduce((sum, m) => sum + m.totalCost, 0);
    const netBalance = totalPayouts + totalMaterials;

    return (
        <PortalLayout title="Accounting Ledger" navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card hover={false} className="bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
                        <div className="flex items-center space-x-3">
                            <TrendingDown className="w-10 h-10 text-red-600 dark:text-red-400" />
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Contractor Payouts</p>
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">{formatCurrency(totalPayouts)}</p>
                            </div>
                        </div>
                    </Card>

                    <Card hover={false} className="bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800">
                        <div className="flex items-center space-x-3">
                            <TrendingDown className="w-10 h-10 text-orange-600 dark:text-orange-400" />
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Material Purchases</p>
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">{formatCurrency(totalMaterials)}</p>
                            </div>
                        </div>
                    </Card>

                    <Card hover={false} className="bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800">
                        <div className="flex items-center space-x-3">
                            <TrendingUp className="w-10 h-10 text-purple-600 dark:text-purple-400" />
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Expenses</p>
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">{formatCurrency(netBalance)}</p>
                            </div>
                        </div>
                    </Card>
                </div>

                {/* All Transactions */}
                <Card>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">All Transactions</h2>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-gray-200 dark:border-gray-700">
                                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Date</th>
                                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Type</th>
                                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Description</th>
                                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Amount</th>
                                    <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {contractorPayouts.map((payout) => (
                                    <tr key={`payout-${payout.id}`} className="border-b border-gray-100 dark:border-gray-800">
                                        <td className="py-3 px-4 text-gray-600 dark:text-gray-400 text-sm">
                                            {payout.paymentDate ? formatDate(payout.paymentDate) : 'Pending'}
                                        </td>
                                        <td className="py-3 px-4">
                                            <Badge variant="info" className="text-xs">Payout</Badge>
                                        </td>
                                        <td className="py-3 px-4 text-gray-900 dark:text-white">
                                            Contractor Payment - Job #{payout.jobId}
                                        </td>
                                        <td className="py-3 px-4 text-right font-semibold text-red-600 dark:text-red-400">
                                            -{formatCurrency(payout.amount)}
                                        </td>
                                        <td className="py-3 px-4 text-center">
                                            <Badge variant={payout.status === 'Paid' ? 'success' : 'warning'} className="text-xs">
                                                {payout.status}
                                            </Badge>
                                        </td>
                                    </tr>
                                ))}
                                {materialOrders.map((order) => (
                                    <tr key={`material-${order.id}`} className="border-b border-gray-100 dark:border-gray-800">
                                        <td className="py-3 px-4 text-gray-600 dark:text-gray-400 text-sm">
                                            {formatDate(order.orderDate)}
                                        </td>
                                        <td className="py-3 px-4">
                                            <Badge variant="default" className="text-xs">Materials</Badge>
                                        </td>
                                        <td className="py-3 px-4 text-gray-900 dark:text-white">
                                            Material Order - Job #{order.jobId}
                                        </td>
                                        <td className="py-3 px-4 text-right font-semibold text-red-600 dark:text-red-400">
                                            -{formatCurrency(order.totalCost)}
                                        </td>
                                        <td className="py-3 px-4 text-center">
                                            <Badge variant={order.status === 'Delivered' ? 'success' : 'warning'} className="text-xs">
                                                {order.status}
                                            </Badge>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </Card>
            </div>
        </PortalLayout>
    );
}
