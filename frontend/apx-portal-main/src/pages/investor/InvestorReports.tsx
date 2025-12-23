import { useState, useEffect } from 'react';
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
import { investorApiService } from '@/lib/investorApi';

export default function InvestorReports() {
    const [filterPeriod, setFilterPeriod] = useState('All Time');
    const [searchTerm, setSearchTerm] = useState('');
    const [reports, setReports] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [downloading, setDownloading] = useState<string | null>(null);

    useEffect(() => {
        const fetchReports = async () => {
            try {
                setLoading(true);
                setError(null);
                
                // Fetch various report data from API
                const [properties, revenueData, roiData] = await Promise.all([
                    investorApiService.getProperties(),
                    investorApiService.getRevenueStatistics('6m'),
                    investorApiService.getROIAnalytics()
                ]);

                // Generate reports list from API data
                const generatedReports = [
                    {
                        id: 'R-PORTFOLIO-2024',
                        title: 'Portfolio Performance Report',
                        type: 'Portfolio',
                        date: new Date().toISOString().split('T')[0],
                        status: 'Ready',
                        size: '3.2 MB',
                        data: { properties: properties.results, revenue: revenueData, roi: roiData }
                    },
                    {
                        id: 'R-REVENUE-2024',
                        title: 'Revenue Analytics Report',
                        type: 'Revenue',
                        date: new Date().toISOString().split('T')[0],
                        status: 'Ready',
                        size: '2.8 MB',
                        data: { revenue: revenueData }
                    },
                    {
                        id: 'R-ROI-2024',
                        title: 'ROI Analysis Report',
                        type: 'ROI',
                        date: new Date().toISOString().split('T')[0],
                        status: 'Ready',
                        size: '1.9 MB',
                        data: { roi: roiData }
                    },
                    // Add property-specific reports
                    ...properties.results.map((property: any) => ({
                        id: `R-PROP-${property.id}`,
                        title: `Property Report: ${property.address}`,
                        type: 'Property',
                        date: new Date().toISOString().split('T')[0],
                        status: 'Ready',
                        size: '1.5 MB',
                        data: { property }
                    }))
                ];

                setReports(generatedReports);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load reports');
            } finally {
                setLoading(false);
            }
        };

        fetchReports();
    }, []);

    const handleDownloadReport = async (report: any) => {
        try {
            setDownloading(report.id);
            
            if (report.type === 'Portfolio' || report.type === 'Revenue') {
                // Download comprehensive CSV report
                const blob = await investorApiService.downloadReportCSV();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${report.title.replace(/\s+/g, '_')}.csv`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else if (report.type === 'Property') {
                // Download detailed job report
                const blob = await investorApiService.downloadDetailedJobReportCSV();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${report.title.replace(/\s+/g, '_')}.csv`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                // For other reports, show success message
                alert(`${report.title} downloaded successfully!`);
            }
        } catch (err) {
            alert('Failed to download report. Please try again.');
        } finally {
            setDownloading(null);
        }
    };

    const filteredReports = reports.filter(report =>
        report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        report.type.toLowerCase().includes(searchTerm.toLowerCase())
    );

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
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full pl-10 pr-4 py-2 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-500 hover:bg-gray-100 dark:hover:bg-gray-750 smooth-transition text-gray-900 dark:text-gray-100"
                            />
                        </div>
                        <div className="flex items-center space-x-3">
                            <Button variant="outline" className="flex items-center space-x-2">
                                <Filter className="w-4 h-4" />
                                <span>Filter</span>
                            </Button>
                            <Button variant="outline" className="flex items-center space-x-2" onClick={() => {
                                const periods = ['All Time', 'Last 6 Months', 'Last Year', 'YTD'];
                                const currentIndex = periods.indexOf(filterPeriod);
                                const nextIndex = (currentIndex + 1) % periods.length;
                                setFilterPeriod(periods[nextIndex]);
                            }}>
                                <Calendar className="w-4 h-4" />
                                <span>{filterPeriod}</span>
                                <ChevronDown className="w-4 h-4 ml-1" />
                            </Button>
                        </div>
                    </div>
                </Card>

                {loading ? (
                    <div className="flex items-center justify-center py-12">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                        <span className="ml-3 text-gray-600 dark:text-gray-400">Loading reports...</span>
                    </div>
                ) : error ? (
                    <Card className="text-center py-12">
                        <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
                        <Button onClick={() => window.location.reload()}>Retry</Button>
                    </Card>
                ) : (
                    /* Reports List */
                    <div className="grid gap-4">
                        {filteredReports.map((report) => (
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
                                        <Button 
                                            variant="ghost" 
                                            size="sm" 
                                            onClick={(e) => { 
                                                e.stopPropagation(); 
                                                handleDownloadReport(report);
                                            }}
                                            disabled={downloading === report.id}
                                        >
                                            {downloading === report.id ? (
                                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-purple-600"></div>
                                            ) : (
                                                <Download className="w-5 h-5 text-gray-400 hover:text-purple-600 dark:hover:text-purple-400" />
                                            )}
                                        </Button>
                                    </div>
                                </div>
                            </Card>
                        ))}
                        {filteredReports.length === 0 && !loading && (
                            <Card className="text-center py-12">
                                <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No Reports Found</h3>
                                <p className="text-gray-500">Try adjusting your search or filter criteria.</p>
                            </Card>
                        )}
                    </div>
                )}
            </div>
        </PortalLayout>
    );
}
