import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import { investorApiService } from '@/lib/investorApi';
import { formatCurrency } from '@/lib/utils';
import {
    ArrowLeft,
    Building,
    DollarSign,
    TrendingUp,
    AlertTriangle,
    FileText,
    LayoutDashboard,
    Users,
    PieChart as PieChartIcon
} from 'lucide-react';

export default function PropertyDetailView() {
    const { address } = useParams<{ address: string }>();
    const navigate = useNavigate();
    const decodedAddress = decodeURIComponent(address || '');

    const [property, setProperty] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchPropertyData = async () => {
            try {
                setLoading(true);
                setError(null);
                
                // Get all properties and find the one matching the address
                const propertiesResponse = await investorApiService.getProperties();
                const matchingProperty = propertiesResponse.results.find(
                    (p: any) => p.address === decodedAddress
                );
                
                if (matchingProperty) {
                    // Get detailed property data including jobs
                    const propertyDetail = await investorApiService.getPropertyDetail(matchingProperty.id);
                    setProperty(propertyDetail);
                } else {
                    setError('Property not found');
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load property data');
            } finally {
                setLoading(false);
            }
        };

        if (decodedAddress) {
            fetchPropertyData();
        }
    }, [decodedAddress]);

    // Standard Investor Navigation
    const navItems = [
        { label: 'Dashboard', path: '/investor/dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
        { label: 'Work Orders', path: '/investor/orders', icon: <FileText className="w-5 h-5" /> },
        { label: 'Leads', path: '/investor/leads', icon: <Users className="w-5 h-5" /> },
        { label: 'Properties', path: '/investor/properties', icon: <Building className="w-5 h-5" /> },
        { label: 'Reports', path: '/investor/reports', icon: <PieChartIcon className="w-5 h-5" /> },
    ];

    if (loading) {
        return (
            <PortalLayout title="Loading Property..." navItems={navItems}>
                <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                    <span className="ml-3 text-gray-600 dark:text-gray-400">Loading property details...</span>
                </div>
            </PortalLayout>
        );
    }

    if (error || !property) {
        return (
            <PortalLayout title="Property Not Found" navItems={navItems}>
                <Card className="text-center py-12">
                    <p className="text-red-600 dark:text-red-400 mb-4">{error || "Property not found."}</p>
                    <Button onClick={() => navigate('/investor/dashboard')}>Back to Dashboard</Button>
                </Card>
            </PortalLayout>
        );
    }

    const issueCount = property.jobs?.filter((job: any) => job.status === 'disputed').length || 0;

    return (
        <PortalLayout title={`Property: ${decodedAddress}`} navItems={navItems}>
            <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">

                {/* Header */}
                <div className="flex items-center space-x-4 mb-6">
                    <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
                        <ArrowLeft className="w-5 h-5 mr-2" />
                        Back
                    </Button>
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
                            <Building className="w-6 h-6 mr-3 text-purple-600" />
                            {property.address}
                        </h1>
                        <p className="text-gray-500 dark:text-gray-400 ml-9">{property.city || 'Property Details'}</p>
                    </div>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card>
                        <div className="flex items-center justify-between mb-2">
                            <h3 className="text-sm font-medium text-gray-500">Total Investment</h3>
                            <DollarSign className="w-5 h-5 text-green-500" />
                        </div>
                        <p className="text-3xl font-bold text-gray-900 dark:text-white">{formatCurrency(property.total_investment || 0)}</p>
                    </Card>
                    <Card>
                        <div className="flex items-center justify-between mb-2">
                            <h3 className="text-sm font-medium text-gray-500">Current Revenue</h3>
                            <TrendingUp className="w-5 h-5 text-blue-500" />
                        </div>
                        <p className="text-3xl font-bold text-gray-900 dark:text-white">{formatCurrency(property.current_revenue || 0)}</p>
                    </Card>
                    <Card>
                        <div className="flex items-center justify-between mb-2">
                            <h3 className="text-sm font-medium text-gray-500">ROI</h3>
                            <FileText className="w-5 h-5 text-purple-500" />
                        </div>
                        <p className="text-3xl font-bold text-gray-900 dark:text-white">{property.roi_percentage || 0}%</p>
                    </Card>
                </div>

                {/* Issues Warning */}
                {issueCount > 0 && (
                    <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-center text-red-700 dark:text-red-400">
                        <AlertTriangle className="w-5 h-5 mr-2" />
                        <span className="font-medium">{issueCount} Flagged Issue(s) reported on this property. Check job details.</span>
                    </div>
                )}

                {/* Jobs List */}
                <Card>
                    <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-6">Work Orders History</h2>
                    {property.jobs && property.jobs.length > 0 ? (
                        <div className="space-y-4">
                            {property.jobs.map((job: any) => (
                                <div key={job.id} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 border border-gray-100 dark:border-gray-800 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                                    <div className="space-y-1 mb-4 sm:mb-0">
                                        <div className="flex items-center gap-2">
                                            <span className="font-semibold text-gray-900 dark:text-white">Job #{job.id}</span>
                                            <Badge variant={job.status === 'Complete' ? 'success' : job.status === 'InProgress' ? 'warning' : 'default'}>
                                                {job.status}
                                            </Badge>
                                        </div>
                                        <p className="text-sm text-gray-500">{job.created_at ? new Date(job.created_at).toLocaleDateString() : 'N/A'} - {job.title}</p>
                                    </div>

                                    <div className="flex items-center gap-6">
                                        <div className="text-right">
                                            <p className="text-xs text-gray-500">Estimated Cost</p>
                                            <p className="font-medium text-gray-900 dark:text-white">{formatCurrency(job.estimated_cost || 0)}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-xs text-gray-500">Actual Cost</p>
                                            <p className="font-bold text-green-600 dark:text-green-400">{formatCurrency(job.actual_cost || 0)}</p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8">
                            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No Work Orders</h3>
                            <p className="text-gray-500">No work orders found for this property.</p>
                        </div>
                    )}
                </Card>
            </div>
        </PortalLayout>
    );
}
