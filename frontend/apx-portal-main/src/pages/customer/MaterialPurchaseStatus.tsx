import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import { Package, ExternalLink, Truck, CheckCircle, Clock, AlertTriangle, Loader2 } from 'lucide-react';
import { customerApiService } from '@/lib/customerApi';

export default function MaterialPurchaseStatus() {
    const { token } = useParams<{ token: string }>();
    
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [materialsData, setMaterialsData] = useState<any>(null);

    useEffect(() => {
        const fetchMaterialsData = async () => {
            if (!token) {
                setError('No materials token provided');
                setLoading(false);
                return;
            }

            try {
                setLoading(true);
                setError(null);
                // For now, we'll use a mock response since this endpoint might not be implemented yet
                // const data = await customerApiService.getMaterialsByToken(token);
                const data = {
                    job_id: 101,
                    order_id: 'ORD-001',
                    materials: [
                        { 
                            id: 1, 
                            name: 'Paint - White', 
                            quantity: 2, 
                            supplier: 'Home Depot',
                            status: 'ordered',
                            tracking_number: 'HD123456789',
                            estimated_delivery: '2024-12-25',
                            price: 45.99
                        },
                        { 
                            id: 2, 
                            name: 'Brushes', 
                            quantity: 3, 
                            supplier: 'Lowes',
                            status: 'delivered',
                            tracking_number: 'LW987654321',
                            delivered_date: '2024-12-23',
                            price: 29.99
                        }
                    ],
                    total_cost: 75.98,
                    delivery_address: '123 Main St, Detroit, MI'
                };
                setMaterialsData(data);
            } catch (err) {
                console.error('Failed to fetch materials data:', err);
                setError(err instanceof Error ? err.message : 'Failed to load materials data');
            } finally {
                setLoading(false);
            }
        };

        fetchMaterialsData();
    }, [token]);

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'ordered':
                return <Clock className="w-4 h-4 text-yellow-500" />;
            case 'shipped':
                return <Truck className="w-4 h-4 text-blue-500" />;
            case 'delivered':
                return <CheckCircle className="w-4 h-4 text-green-500" />;
            default:
                return <Package className="w-4 h-4 text-gray-500" />;
        }
    };

    const getStatusVariant = (status: string) => {
        switch (status) {
            case 'ordered':
                return 'warning';
            case 'shipped':
                return 'info';
            case 'delivered':
                return 'success';
            default:
                return 'default';
        }
    };

    if (loading) {
        return (
            <div className="max-w-3xl mx-auto flex items-center justify-center h-64">
                <div className="text-center">
                    <Loader2 className="w-8 h-8 animate-spin text-purple-600 mx-auto mb-4" />
                    <p className="text-gray-600">Loading materials status...</p>
                </div>
            </div>
        );
    }

    if (error || !materialsData) {
        return (
            <div className="max-w-3xl mx-auto">
                <Card className="text-center p-8">
                    <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Unable to Load Materials</h2>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                        {error || 'The materials link is invalid or has expired.'}
                    </p>
                    <Button onClick={() => window.location.reload()}>
                        Retry
                    </Button>
                </Card>
            </div>
        );
    }

    return (
        <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
            <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-purple-100 dark:bg-purple-900/30 mb-4">
                    <Package className="w-8 h-8 text-purple-600 dark:text-purple-400" />
                </div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Project Materials Status</h1>
                <p className="text-gray-500">Track your material orders and deliveries</p>
                <p className="text-sm text-gray-400">Order ID: {materialsData.order_id}</p>
            </div>

            {/* Delivery Address */}
            <Card>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Delivery Address</h3>
                <p className="text-gray-600 dark:text-gray-400">{materialsData.delivery_address}</p>
            </Card>

            {/* Materials List */}
            <Card>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Materials</h3>
                <div className="space-y-4">
                    {materialsData.materials.map((material: any) => (
                        <div key={material.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                            <div className="flex items-start justify-between mb-3">
                                <div className="flex-1">
                                    <h4 className="font-medium text-gray-900 dark:text-white">{material.name}</h4>
                                    <p className="text-sm text-gray-500">Qty: {material.quantity}</p>
                                    <p className="text-sm text-gray-500">Supplier: {material.supplier}</p>
                                </div>
                                <div className="text-right">
                                    <Badge variant={getStatusVariant(material.status)} className="mb-2">
                                        {getStatusIcon(material.status)}
                                        <span className="ml-1 capitalize">{material.status}</span>
                                    </Badge>
                                    <p className="text-sm font-semibold text-gray-900 dark:text-white">
                                        ${material.price}
                                    </p>
                                </div>
                            </div>

                            {material.tracking_number && (
                                <div className="bg-gray-50 dark:bg-gray-800 rounded p-3 mt-3">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-xs text-gray-500 mb-1">Tracking Number</p>
                                            <p className="font-mono text-sm text-gray-900 dark:text-white">
                                                {material.tracking_number}
                                            </p>
                                        </div>
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() => {
                                                const trackingUrl = material.supplier === 'Home Depot' 
                                                    ? `https://www.homedepot.com/track-order/${material.tracking_number}`
                                                    : `https://www.lowes.com/track-order/${material.tracking_number}`;
                                                window.open(trackingUrl, '_blank');
                                            }}
                                        >
                                            <ExternalLink className="w-4 h-4 mr-1" />
                                            Track
                                        </Button>
                                    </div>
                                    
                                    {material.status === 'delivered' && material.delivered_date && (
                                        <p className="text-xs text-green-600 mt-2">
                                            Delivered on {new Date(material.delivered_date).toLocaleDateString()}
                                        </p>
                                    )}
                                    
                                    {material.status === 'ordered' && material.estimated_delivery && (
                                        <p className="text-xs text-blue-600 mt-2">
                                            Estimated delivery: {new Date(material.estimated_delivery).toLocaleDateString()}
                                        </p>
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                {/* Total Cost */}
                <div className="border-t border-gray-200 dark:border-gray-700 pt-4 mt-4">
                    <div className="flex justify-between items-center">
                        <span className="font-semibold text-gray-900 dark:text-white">Total Cost</span>
                        <span className="text-lg font-bold text-gray-900 dark:text-white">
                            ${materialsData.total_cost}
                        </span>
                    </div>
                </div>
            </Card>

            {/* Help Section */}
            <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
                <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">Need Help?</h3>
                <p className="text-sm text-blue-700 dark:text-blue-300 mb-3">
                    If you have questions about your material orders or deliveries, contact our support team.
                </p>
                <Button variant="outline" size="sm" className="border-blue-300 text-blue-700 hover:bg-blue-100">
                    Contact Support
                </Button>
            </Card>
        </div>
    );
}
