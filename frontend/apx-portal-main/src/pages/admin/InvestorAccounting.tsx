import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import {
    LayoutDashboard,
    ShieldCheck,
    AlertTriangle,
    DollarSign,
    FileText,
    Briefcase,
    Calendar,
    Users,
    TrendingUp
} from 'lucide-react';
import { jobs, contractorPayouts, materialOrders } from '@/data/mockData';
import { formatCurrency } from '@/lib/utils';

export default function InvestorAccounting() {
    useNavigate();
    useAuth();

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

    const investorJobs = jobs.filter(j => j.isProject);
    const totalRevenue = investorJobs.length * 5000; // Simulated revenue
    const totalCosts = contractorPayouts.filter(p => p.jobType === 'investor').reduce((sum, p) => sum + p.amount, 0) +
        materialOrders.filter(m => investorJobs.some(j => j.id === m.jobId)).reduce((sum, m) => sum + m.totalCost, 0);
    const netProfit = totalRevenue - totalCosts;
    const profitMargin = totalRevenue > 0 ? ((netProfit / totalRevenue) * 100).toFixed(1) : 0;

    return (
        <PortalLayout title="Investor Accounting" navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <Card hover={false} className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
                        <div className="flex items-center space-x-3">
                            <Briefcase className="w-10 h-10 text-blue-600 dark:text-blue-400" />
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Investor Jobs</p>
                                <p className="text-3xl font-bold text-gray-900 dark:text-white">{investorJobs.length}</p>
                            </div>
                        </div>
                    </Card>

                    <Card hover={false} className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
                        <div className="flex items-center space-x-3">
                            <TrendingUp className="w-10 h-10 text-green-600 dark:text-green-400" />
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Revenue</p>
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">{formatCurrency(totalRevenue)}</p>
                            </div>
                        </div>
                    </Card>

                    <Card hover={false} className="bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
                        <div className="flex items-center space-x-3">
                            <DollarSign className="w-10 h-10 text-red-600 dark:text-red-400" />
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Costs</p>
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">{formatCurrency(totalCosts)}</p>
                            </div>
                        </div>
                    </Card>

                    <Card hover={false} className="bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800">
                        <div className="flex items-center space-x-3">
                            <TrendingUp className="w-10 h-10 text-purple-600 dark:text-purple-400" />
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Net Profit</p>
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">{formatCurrency(netProfit)}</p>
                                <p className="text-xs text-gray-500 dark:text-gray-500">{profitMargin}% margin</p>
                            </div>
                        </div>
                    </Card>
                </div>

                {/* Financial Breakdown */}
                <Card>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Financial Breakdown</h2>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                            <div>
                                <p className="font-semibold text-gray-900 dark:text-white">Revenue</p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">{investorJobs.length} investor-backed jobs</p>
                            </div>
                            <p className="text-2xl font-bold text-green-600 dark:text-green-400">+{formatCurrency(totalRevenue)}</p>
                        </div>

                        <div className="flex items-center justify-between p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                            <div>
                                <p className="font-semibold text-gray-900 dark:text-white">Contractor Payouts</p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    {contractorPayouts.filter(p => p.jobType === 'investor').length} payouts
                                </p>
                            </div>
                            <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                                -{formatCurrency(contractorPayouts.filter(p => p.jobType === 'investor').reduce((s, p) => s + p.amount, 0))}
                            </p>
                        </div>

                        <div className="flex items-center justify-between p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                            <div>
                                <p className="font-semibold text-gray-900 dark:text-white">Material Costs</p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    {materialOrders.filter(m => investorJobs.some(j => j.id === m.jobId)).length} orders
                                </p>
                            </div>
                            <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                                -{formatCurrency(materialOrders.filter(m => investorJobs.some(j => j.id === m.jobId)).reduce((s, m) => s + m.totalCost, 0))}
                            </p>
                        </div>

                        <div className="border-t-2 border-gray-200 dark:border-gray-700 pt-4 mt-4">
                            <div className="flex items-center justify-between p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                                <div>
                                    <p className="text-lg font-bold text-gray-900 dark:text-white">Net Profit</p>
                                    <p className="text-sm text-gray-600 dark:text-gray-400">Profit Margin: {profitMargin}%</p>
                                </div>
                                <p className="text-3xl font-bold text-purple-600 dark:text-purple-400">{formatCurrency(netProfit)}</p>
                            </div>
                        </div>
                    </div>
                </Card>

                {/* Investment Portfolio */}
                <Card>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Investment Portfolio</h2>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-gray-200 dark:border-gray-700">
                                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Job ID</th>
                                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Property</th>
                                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Status</th>
                                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Est. Revenue</th>
                                </tr>
                            </thead>
                            <tbody>
                                {investorJobs.map((job) => (
                                    <tr key={job.id} className="border-b border-gray-100 dark:border-gray-800">
                                        <td className="py-3 px-4 font-mono text-purple-600 dark:text-purple-400">#{job.id}</td>
                                        <td className="py-3 px-4 text-gray-900 dark:text-white">{job.propertyAddress}</td>
                                        <td className="py-3 px-4 text-gray-700 dark:text-gray-300">{job.status}</td>
                                        <td className="py-3 px-4 text-right font-semibold text-green-600 dark:text-green-400">
                                            {formatCurrency(5000)}
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
