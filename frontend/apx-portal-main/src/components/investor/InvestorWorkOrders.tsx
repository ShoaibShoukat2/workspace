import { useState } from 'react';
import Card from '@/components/ui/Card';
import Badge, { getStatusBadgeVariant } from '@/components/ui/Badge';
import { jobs } from '@/data/mockData';
import { formatCurrency } from '@/lib/utils';
import { Search } from 'lucide-react';

export default function InvestorWorkOrders() {
    const [filter, setFilter] = useState<'all' | 'active' | 'completed' | 'pending'>('all');
    const [searchTerm, setSearchTerm] = useState('');

    const allWorkOrders = jobs.filter(j => j.isProject);

    const filteredOrders = allWorkOrders.filter(job => {
        const matchesSearch = job.propertyAddress.toLowerCase().includes(searchTerm.toLowerCase()) ||
            job.city.toLowerCase().includes(searchTerm.toLowerCase());

        if (!matchesSearch) return false;

        if (filter === 'all') return true;
        if (filter === 'active') return job.status === 'InProgress' || job.status === 'Open';
        if (filter === 'completed') return job.status === 'Complete';
        // Mock logic for pending payout - strictly existing logic implies 'Complete' might still be pending, 
        // but for now let's just use status. 
        if (filter === 'pending') return job.status === 'Complete';

        return true;
    });

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
                <div className="flex bg-white dark:bg-gray-800 rounded-lg p-1 shadow-sm border border-gray-200 dark:border-gray-700 overflow-x-auto">
                    <button
                        onClick={() => setFilter('all')}
                        className={`whitespace-nowrap px-4 py-2 rounded-md text-sm font-medium transition ${filter === 'all' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'}`}
                    >
                        All Orders
                    </button>
                    <button
                        onClick={() => setFilter('active')}
                        className={`whitespace-nowrap px-4 py-2 rounded-md text-sm font-medium transition ${filter === 'active' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'}`}
                    >
                        Active
                    </button>
                    <button
                        onClick={() => setFilter('pending')}
                        className={`whitespace-nowrap px-4 py-2 rounded-md text-sm font-medium transition ${filter === 'pending' ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'}`}
                    >
                        Pending Payout
                    </button>
                    <button
                        onClick={() => setFilter('completed')}
                        className={`whitespace-nowrap px-4 py-2 rounded-md text-sm font-medium transition ${filter === 'completed' ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'}`}
                    >
                        Past History
                    </button>
                </div>

                <div className="relative w-full md:w-64">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <input
                        type="text"
                        placeholder="Search property or city..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-9 pr-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                </div>
            </div>

            <Card>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-gray-200 dark:border-gray-700 text-left">
                                <th className="py-3 px-4 text-sm font-semibold text-gray-600 dark:text-gray-400">Order ID</th>
                                <th className="py-3 px-4 text-sm font-semibold text-gray-600 dark:text-gray-400">Property</th>
                                <th className="py-3 px-4 text-sm font-semibold text-gray-600 dark:text-gray-400">Trade</th>
                                <th className="py-3 px-4 text-sm font-semibold text-gray-600 dark:text-gray-400">Status</th>
                                <th className="py-3 px-4 text-sm font-semibold text-gray-600 dark:text-gray-400 text-right">Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredOrders.length > 0 ? (
                                filteredOrders.map((job) => (
                                    <tr key={job.id} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                                        <td className="py-3 px-4 font-mono text-xs text-gray-500">#{job.id}</td>
                                        <td className="py-3 px-4">
                                            <p className="font-medium text-gray-900 dark:text-white">{job.propertyAddress}</p>
                                            <p className="text-xs text-gray-500">{job.city}</p>
                                        </td>
                                        <td className="py-3 px-4 text-gray-700 dark:text-gray-300 capitalize">{job.trade}</td>
                                        <td className="py-3 px-4">
                                            <Badge variant={getStatusBadgeVariant(job.status)} className="text-xs">
                                                {job.status}
                                            </Badge>
                                        </td>
                                        <td className="py-3 px-4 text-right font-medium text-gray-900 dark:text-white">
                                            {formatCurrency(5000)} {/* Mock amount */}
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={5} className="py-8 text-center text-gray-500">
                                        No work orders found matching filters.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    );
}
