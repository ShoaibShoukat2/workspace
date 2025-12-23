import { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import { formatCurrency } from '@/lib/utils';
import { Building, MapPin } from 'lucide-react';
import Badge from '@/components/ui/Badge';

export default function InvestorProperties() {
    const [properties, setProperties] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchProperties();
    }, []);

    const fetchProperties = async () => {
        try {
            const response = await fetch('/api/jobs/?is_project=true', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            if (response.ok) {
                const jobs = await response.json();
                
                // Group jobs by property
                const propertyGroups = jobs.reduce((acc: any, job: any) => {
                    if (!acc[job.property_address]) {
                        acc[job.property_address] = {
                            address: job.property_address,
                            city: job.city,
                            jobs: [],
                            totalRevenue: 0,
                            issues: 0
                        };
                    }
                    acc[job.property_address].jobs.push(job);
                    acc[job.property_address].totalRevenue += 5000; // Mock revenue
                    if (job.status === 'Open' || job.status === 'InProgress') {
                        // Mock logic for issues
                    }
                    return acc;
                }, {});

                setProperties(Object.values(propertyGroups));
            }
        } catch (error) {
            console.error('Error fetching properties:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="text-center py-8">Loading properties...</div>;
    }

    return (
        <div className="grid grid-cols-1 gap-6">
            {properties.map((property: any, index) => (
                <Card key={index} hover={false} className="border-l-4 border-l-blue-500">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                        <div className="flex-1">
                            <div className="flex items-start justify-between mb-2">
                                <div className="flex items-center space-x-2">
                                    <Building className="w-5 h-5 text-blue-500" />
                                    <h3 className="text-lg font-bold text-gray-900 dark:text-white">{property.address}</h3>
                                </div>
                                <Badge variant="default">{property.jobs.length} Active Jobs</Badge>
                            </div>

                            <div className="flex items-center text-gray-500 text-sm mb-4">
                                <MapPin className="w-4 h-4 mr-1" />
                                {property.city}
                            </div>

                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
                                    <p className="text-xs text-gray-500 mb-1">Total Jobs</p>
                                    <p className="font-bold text-gray-900 dark:text-white">{property.jobs.length}</p>
                                </div>
                                <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
                                    <p className="text-xs text-gray-500 mb-1">Total Revenue</p>
                                    <p className="font-bold text-green-600">{formatCurrency(property.totalRevenue)}</p>
                                </div>
                                <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
                                    <p className="text-xs text-gray-500 mb-1">Net Profit</p>
                                    <p className="font-bold text-purple-600">{formatCurrency(property.totalRevenue * 0.2)}</p>
                                </div>
                                <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
                                    <p className="text-xs text-gray-500 mb-1">Issues</p>
                                    <p className={`font-bold ${property.issues > 0 ? 'text-red-500' : 'text-gray-400'}`}>
                                        {property.issues}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="w-full md:w-1/3">
                            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Recent Activity</h4>
                            <div className="space-y-2 max-h-40 overflow-y-auto pr-2 custom-scrollbar">
                                {property.jobs.slice(0, 3).map((job: any) => (
                                    <div key={job.id} className="text-xs p-2 rounded bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800">
                                        <div className="flex justify-between mb-1">
                                            <span className="font-medium text-gray-900 dark:text-white capitalize">{job.trade}</span>
                                            <span className={`text-[10px] px-1.5 py-0.5 rounded ${job.status === 'Complete' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
                                                }`}>{job.status}</span>
                                        </div>
                                        <p className="text-gray-500 truncate">{job.customer_name}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </Card>
            ))}
        </div>
    );
}
