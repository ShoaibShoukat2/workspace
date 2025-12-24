import { useState, useEffect } from 'react';
import { investorApi } from '@/services/investorApi';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import {
    FileText,
    Download,
    Filter,
    Calendar,
    ChevronDown,
    Search,
    LayoutDashboard,
    Building,
    PieChart as PieChartIcon,
    Users
} from 'lucide-react';

export default function InvestorReports() {
    const [filterPeriod] = useState('All Time');
    const [reports, setReports] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadReports();
    }, []);

    const loadReports = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await investorApi.getReports();
            setReports(data.reports || []);
        } catch (err: any) {
            console.error('Failed to load reports:', err);
            setError('Failed to load reports. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const navItems = [
        { label: 'Dashboard', path: '/investor/dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
        { label: 'Work Orders', path: '/investor/orders', icon: <FileText className="w-5 h-5" /> },
        { label: 'Leads', path: '/investor/leads', icon: <Users className="w-5 h-5" /> },
        { label: 'Properties', path: '/investor/properties', icon: <Building className="w-5 h-5" /> },
        { label: 'Reports', path: '/investor/reports', icon: <PieChartIcon className="w-5 h-5" /> },
    ];

    return (
        <PortalLayout title="Financial Reports" navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                {/* Header Controls */}
                <Card>
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div className="relative flex-1 max-w-md">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Search reports..."
                                className="w-full pl-10 pr-4 py-2 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-500 hover:bg-gray-100 dark:hover:bg-gray-750 smooth-transition text-gray-900 dark:text-gray-100"
                            />
                        </div>
                        <div className="flex items-center space-x-3">
                            <Button variant="outline" className="flex items-center space-x-2">
                                <Filter className="w-4 h-4" />
                                <span>Filter</span>
                            </Button>
                            <Button variant="outline" className="flex items-center space-x-2">
                                <Calendar className="w-4 h-4" />
                                <span>{filterPeriod}</span>
                                <ChevronDown className="w-4 h-4 ml-1" />
                            </Button>
                        </div>
                    </div>
                </Card>

                {/* Reports List */}
                <div className="grid gap-4">
                    {reports.map((report) => (
                        <Card key={report.id} className="hover:scale-[1.01] cursor-pointer group">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-4">
                                    <div className="w-12 h-12 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center group-hover:bg-purple-200 dark:group-hover:bg-purple-800/40 smooth-transition">
                                        <FileText className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-400 smooth-transition">{report.title}</h3>
                                        <div className="flex items-center space-x-3 mt-1">
                                            <span className="text-sm text-gray-500 dark:text-gray-400">{report.id}</span>
                                            <span className="text-gray-300 dark:text-gray-600">•</span>
                                            <span className="text-sm text-gray-500 dark:text-gray-400">{report.date}</span>
                                            <span className="text-gray-300 dark:text-gray-600">•</span>
                                            <span className="text-sm text-gray-500 dark:text-gray-400">{report.size}</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center space-x-4">
                                    <Badge variant={report.status === 'Ready' ? 'success' : 'info'}>
                                        {report.status}
                                    </Badge>
                                    <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); alert(`Downloading ${report.title}...`); }}>
                                        <Download className="w-5 h-5 text-gray-400 hover:text-purple-600 dark:hover:text-purple-400" />
                                    </Button>
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>
            </div>
        </PortalLayout>
    );
}
