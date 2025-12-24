import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { customerApi } from '@/services/customerApi';

import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { AlertTriangle, FileText, Clock } from 'lucide-react';
import CustomerTracker from './CustomerTracker';
import JobProgressTimeline from '@/components/customer/JobProgressTimeline';
import MaterialsReadOnlyList from '@/components/customer/MaterialsReadOnlyList';

export default function CustomerDashboard() {
    const { currentUser } = useAuth();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState<'status' | 'materials' | 'actions'>('status');
    const [dashboardData, setDashboardData] = useState<any>(null);
    const [activeJob, setActiveJob] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            setLoading(true);
            setError(null);
            
            const [dashboard, jobs] = await Promise.all([
                customerApi.getDashboard(),
                customerApi.getJobs({ status: 'active', limit: 1 })
            ]);
            
            setDashboardData(dashboard);
            setActiveJob(jobs.jobs?.[0] || null);
        } catch (err: any) {
            console.error('Failed to load dashboard data:', err);
            setError('Failed to load dashboard data. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center">
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 max-w-md">
                    <p className="text-red-700 dark:text-red-400">{error}</p>
                    <button 
                        onClick={loadDashboardData}
                        className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    // Use real data or fallbacks
    const activeJobId = activeJob?.id || 101;
    const magicToken = activeJob?.magic_token || 'mock-token-123';

    return (
        <div className="min-h-[calc(100vh-4rem)] flex flex-col lg:flex-row gap-6 animate-fade-in p-4 lg:p-6 max-w-[1600px] mx-auto">

            {/* LEFT COLUMN: Map & Tracking (Main Focus) */}
            <div className="lg:w-2/3 flex flex-col gap-6">
                {/* Header Widget */}
                <div className="bg-gradient-to-r from-gray-900 to-gray-800 dark:from-gray-800 dark:to-gray-900 rounded-2xl p-6 text-white shadow-lg flex justify-between items-center">
                    <div>
                        <h2 className="text-2xl font-bold mb-1">Hello, {currentUser?.name.split(' ')[0]}</h2>
                        <p className="text-gray-300 text-sm">You have an active service visit in progress.</p>
                    </div>
                    <div className="bg-white/10 p-2 rounded-lg">
                        <Clock className="w-6 h-6 text-blue-400" />
                    </div>
                </div>

                {/* Tracking Map */}
                <Card className="flex-1 overflow-hidden p-0 border-0 shadow-xl min-h-[500px] relative">
                    <div className="absolute top-0 left-0 right-0 z-10 bg-white/90 dark:bg-gray-900/90 backdrop-blur px-4 py-2 border-b border-gray-200 dark:border-gray-800 flex justify-between items-center text-xs font-semibold text-gray-500 uppercase tracking-widest">
                        <span>Live Tracking</span>
                        <span className="flex items-center gap-1 text-green-600"><div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" /> Live</span>
                    </div>
                    <div className="h-full pt-8">
                        <CustomerTracker jobId={activeJobId} embed={true} onlyMap={true} />
                    </div>
                </Card>
            </div>

            {/* RIGHT COLUMN: Controls & Details */}
            <div className="lg:w-1/3 flex flex-col gap-6">

                <Card className="flex-1 flex flex-col p-0 overflow-hidden">
                    {/* Tabs */}
                    <div className="flex border-b border-gray-100 dark:border-gray-800">
                        <button
                            onClick={() => setActiveTab('status')}
                            className={`flex-1 py-4 text-sm font-medium border-b-2 transition-colors ${activeTab === 'status' ? 'border-black dark:border-white text-black dark:text-white' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
                        >
                            Progress
                        </button>
                        <button
                            onClick={() => setActiveTab('materials')}
                            className={`flex-1 py-4 text-sm font-medium border-b-2 transition-colors ${activeTab === 'materials' ? 'border-black dark:border-white text-black dark:text-white' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
                        >
                            Materials
                        </button>
                        <button
                            onClick={() => setActiveTab('actions')}
                            className={`flex-1 py-4 text-sm font-medium border-b-2 transition-colors ${activeTab === 'actions' ? 'border-black dark:border-white text-black dark:text-white' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
                        >
                            Actions
                        </button>
                    </div>

                    {/* Tab Content */}
                    <div className="p-6 overflow-y-auto max-h-[600px]">
                        {activeTab === 'status' && (
                            <div className="animate-fade-in-right">
                                <h3 className="font-bold text-lg mb-6 text-gray-900 dark:text-white">Service Timeline</h3>
                                <JobProgressTimeline status={activeJob.status} />

                                <div className="mt-8 pt-6 border-t border-gray-100 dark:border-gray-800">
                                    <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Technician</h4>
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-full bg-gray-200 overflow-hidden">
                                            <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=technician`} alt="Tech" className="w-full h-full object-cover" />
                                        </div>
                                        <div>
                                            <p className="font-medium text-sm">Alex M.</p>
                                            <p className="text-xs text-gray-500">Painting Specialist • 4.9 ★</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {activeTab === 'materials' && (
                            <div className="animate-fade-in-right">
                                <h3 className="font-bold text-lg mb-6 text-gray-900 dark:text-white">Project Materials</h3>
                                <MaterialsReadOnlyList />
                            </div>
                        )}

                        {activeTab === 'actions' && (
                            <div className="space-y-3 animate-fade-in-right">
                                <h3 className="font-bold text-lg mb-6 text-gray-900 dark:text-white">Quick Actions</h3>
                                <Button
                                    variant="outline"
                                    className="w-full justify-start h-auto py-3"
                                    onClick={() => navigate(`/issue/${magicToken}`)}
                                >
                                    <AlertTriangle className="w-5 h-5 mr-3 text-red-500" />
                                    <div className="text-left">
                                        <div className="font-medium">Report an Issue</div>
                                        <div className="text-xs text-gray-500">Something wrong?</div>
                                    </div>
                                </Button>

                                <Button
                                    variant="outline"
                                    className="w-full justify-start h-auto py-3"
                                    onClick={() => navigate(`/quote/${magicToken}`)}
                                >
                                    <FileText className="w-5 h-5 mr-3 text-blue-500" />
                                    <div className="text-left">
                                        <div className="font-medium">View Original Quote</div>
                                        <div className="text-xs text-gray-500">See contract details</div>
                                    </div>
                                </Button>
                            </div>
                        )}
                    </div>
                </Card>
            </div>
        </div>
    );
}
