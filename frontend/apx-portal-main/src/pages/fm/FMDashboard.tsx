import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Badge, { getStatusBadgeVariant } from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import {
    LayoutDashboard,
    ClipboardList,
    FileEdit,
    Map,
    List,
    MapPin,
    Calendar,
    Clock,
    ChevronRight,
    AlertCircle,
    Loader2
} from 'lucide-react';
import { fmApiService } from '@/lib/fmApi';

export default function FMDashboard() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [viewMode, setViewMode] = useState<'map' | 'list'>('list');
    
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [dashboardData, setDashboardData] = useState<any>(null);
    const [jobs, setJobs] = useState<any[]>([]);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                setLoading(true);
                setError(null);

                const [dashboard, jobsData] = await Promise.all([
                    fmApiService.getDashboard(),
                    fmApiService.getJobs({ limit: 20 })
                ]);

                setDashboardData(dashboard);
                setJobs(jobsData.results || jobsData);
            } catch (err) {
                console.error('Failed to fetch FM dashboard data:', err);
                setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    if (loading) {
        return (
            <PortalLayout title="Field Manager Dashboard" navItems={navItems}>
                <div className="flex items-center justify-center h-64">
                    <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
                    <span className="ml-2 text-gray-600">Loading dashboard...</span>
                </div>
            </PortalLayout>
        );
    }

    if (error) {
        return (
            <PortalLayout title="Field Manager Dashboard" navItems={navItems}>
                <div className="flex items-center justify-center h-64">
                    <div className="text-center">
                        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                        <p className="text-red-600 mb-4">{error}</p>
                        <Button onClick={() => window.location.reload()}>Retry</Button>
                    </div>
                </div>
            </PortalLayout>
        );
    }

    const navItems = [
        { label: 'Dashboard', path: '/fm/dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
        { label: 'Site Visits', path: '/fm/dashboard', icon: <ClipboardList className="w-5 h-5" /> },
        { label: 'Change Orders', path: '/fm/dashboard', icon: <FileEdit className="w-5 h-5" /> },
    ];

    // Get jobs for FM (all pending and assigned jobs)
    const myJobs = jobs.filter(j =>
        j.status === 'Open' || j.status === 'open' ||
        j.status === 'InProgress' || j.status === 'in_progress' ||
        j.status === 'Complete' || j.status === 'completed'
    );

    const pendingVisits = dashboardData?.pending_visits || myJobs.filter(j => j.status === 'Open' || j.status === 'open').length;
    const activeJobs = dashboardData?.active_jobs || myJobs.filter(j => j.status === 'InProgress' || j.status === 'in_progress').length;
    const completedToday = dashboardData?.completed_today || myJobs.filter(j => j.status === 'Complete' || j.status === 'completed').length;

    return (
        <PortalLayout title="Field Manager Dashboard" navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card hover={false} className="bg-gradient-to-br from-blue-500/10 to-blue-600/10 dark:from-blue-500/20 dark:to-blue-600/20 border-blue-200 dark:border-blue-800">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Pending Visits</p>
                                <p className="text-3xl font-bold text-gray-900 dark:text-white">{pendingVisits}</p>
                            </div>
                            <div className="w-14 h-14 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                                <Calendar className="w-7 h-7 text-blue-600 dark:text-blue-400" />
                            </div>
                        </div>
                    </Card>

                    <Card hover={false} className="bg-gradient-to-br from-purple-500/10 to-purple-600/10 dark:from-purple-500/20 dark:to-purple-600/20 border-purple-200 dark:border-purple-800">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Active Jobs</p>
                                <p className="text-3xl font-bold text-gray-900 dark:text-white">{activeJobs}</p>
                            </div>
                            <div className="w-14 h-14 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                                <Clock className="w-7 h-7 text-purple-600 dark:text-purple-400" />
                            </div>
                        </div>
                    </Card>

                    <Card hover={false} className="bg-gradient-to-br from-green-500/10 to-green-600/10 dark:from-green-500/20 dark:to-green-600/20 border-green-200 dark:border-green-800">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Completed Today</p>
                                <p className="text-3xl font-bold text-gray-900 dark:text-white">{completedToday}</p>
                            </div>
                            <div className="w-14 h-14 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                                <ClipboardList className="w-7 h-7 text-green-600 dark:text-green-400" />
                            </div>
                        </div>
                    </Card>
                </div>

                {/* View Toggle */}
                <Card hover={false}>
                    <div className="flex items-center justify-between">
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Site Visits</h2>
                        <div className="flex space-x-2">
                            <button
                                onClick={() => setViewMode('list')}
                                className={`px-4 py-2 rounded-lg flex items-center space-x-2 smooth-transition ${viewMode === 'list'
                                    ? 'bg-purple-500 text-white'
                                    : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                                    }`}
                            >
                                <List className="w-4 h-4" />
                                <span className="text-sm font-medium">List</span>
                            </button>
                            <button
                                onClick={() => setViewMode('map')}
                                className={`px-4 py-2 rounded-lg flex items-center space-x-2 smooth-transition ${viewMode === 'map'
                                    ? 'bg-purple-500 text-white'
                                    : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                                    }`}
                            >
                                <Map className="w-4 h-4" />
                                <span className="text-sm font-medium">Map</span>
                            </button>
                        </div>
                    </div>
                </Card>

                {/* Map View */}
                {viewMode === 'map' && (
                    <Card className="h-96">
                        <div className="relative w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900 rounded-xl flex items-center justify-center">
                            <div className="text-center">
                                <Map className="w-16 h-16 text-gray-400 dark:text-gray-600 mx-auto mb-4" />
                                <p className="text-gray-600 dark:text-gray-400 text-lg font-medium mb-2">Map View</p>
                                <p className="text-sm text-gray-500 dark:text-gray-500">
                                    Interactive map with job locations would appear here
                                </p>
                                <p className="text-xs text-gray-400 dark:text-gray-600 mt-2">
                                    (Leaflet map integration - {myJobs.length} jobs to display)
                                </p>
                            </div>
                        </div>
                    </Card>
                )}

                {/* List View */}
                {viewMode === 'list' && (
                    <div className="space-y-4">
                        {myJobs.length > 0 ? (
                            myJobs.map((job) => (
                                <Card key={job.id} className="hover:scale-[1.01]">
                                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                                        <div className="flex-1">
                                            <div className="flex items-start justify-between mb-2">
                                                <div>
                                                    <h3 className="font-semibold text-gray-900 dark:text-white text-lg">
                                                        {job.property_address || job.propertyAddress}
                                                    </h3>
                                                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                                        {job.customer_name || job.customerName} • {job.trade}
                                                    </p>
                                                </div>
                                                <Badge variant={getStatusBadgeVariant(job.status)}>
                                                    {job.status}
                                                </Badge>
                                            </div>

                                            <div className="flex flex-wrap items-center gap-2 mt-3 text-sm">
                                                <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                                                    <MapPin className="w-4 h-4 text-blue-500" />
                                                    <span>{job.city || job.location}</span>
                                                </div>

                                                {/* Mandatory Site Visit Badge */}
                                                {(job.mandatory_site_visit || job.mandatorySiteVisit) && (
                                                    <Badge variant="warning" className="text-xs bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-900/30 dark:text-amber-300 dark:border-amber-700">
                                                        MANDATORY VISIT
                                                    </Badge>
                                                )}

                                                {/* Visit Status Badge */}
                                                {(job.visit_status || job.visitStatus) && (
                                                    <Badge
                                                        variant={
                                                            (job.visit_status || job.visitStatus) === 'Completed' || (job.visit_status || job.visitStatus) === 'completed' ? 'success' :
                                                                (job.visit_status || job.visitStatus) === 'InProgress' || (job.visit_status || job.visitStatus) === 'in_progress' ? 'info' : 'default'
                                                        }
                                                        className="text-xs"
                                                    >
                                                        {job.visit_status || job.visitStatus}
                                                    </Badge>
                                                )}

                                                {/* Material Status Badge */}
                                                {(job.material_status || job.materialStatus) && (
                                                    <Badge
                                                        variant={
                                                            (job.material_status || job.materialStatus) === 'Issues Found' ? 'danger' :
                                                                (job.material_status || job.materialStatus) === 'FM Verified' ? 'success' :
                                                                    (job.material_status || job.materialStatus) === 'AI Generated' ? 'info' : 'warning'
                                                        }
                                                        className="text-xs flex items-center gap-1"
                                                    >
                                                        {(job.material_status || job.materialStatus) === 'Issues Found' && <AlertCircle className="w-3 h-3" />}
                                                        {job.material_status || job.materialStatus}
                                                    </Badge>
                                                )}

                                                {/* Material Alert */}
                                                {(job.material_status || job.materialStatus) === 'Issues Found' && (
                                                    <div className="flex items-center space-x-1 text-red-600 dark:text-red-400 text-xs">
                                                        <AlertCircle className="w-3 h-3" />
                                                        <span>Materials need attention</span>
                                                    </div>
                                                )}

                                                {(job.is_project || job.isProject) && (
                                                    <Badge variant="info" className="text-xs">
                                                        PROJECT
                                                    </Badge>
                                                )}
                                                {job.materials && job.materials.length > 0 && (
                                                    <Badge variant="default" className="text-xs">
                                                        {job.materials.length} Materials
                                                    </Badge>
                                                )}
                                            </div>
                                        </div>

                                        <div className="flex flex-col sm:flex-row gap-2">
                                            <Button
                                                variant="primary"
                                                size="sm"
                                                onClick={() => navigate(`/fm/visits/${job.id}`)}
                                            >
                                                <ClipboardList className="w-4 h-4 mr-2" />
                                                {job.status === 'Open' ? 'Start Visit' : 'View Visit'}
                                                <ChevronRight className="w-4 h-4 ml-1" />
                                            </Button>
                                            {job.status === 'InProgress' && (
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => navigate(`/fm/visits/${job.id}/change-order`)}
                                                >
                                                    <FileEdit className="w-4 h-4 mr-2" />
                                                    Change Order
                                                </Button>
                                            )}
                                        </div>
                                    </div>
                                </Card>
                            ))
                        ) : (
                            <Card className="text-center py-12">
                                <ClipboardList className="w-16 h-16 text-gray-400 dark:text-gray-600 mx-auto mb-4" />
                                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No Site Visits</h3>
                                <p className="text-gray-600 dark:text-gray-400">
                                    All site visits are complete. New jobs will appear here.
                                </p>
                            </Card>
                        )}
                    </div>
                )}
            </div>
        </PortalLayout>
    );
}
