import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import { Package, CheckCircle, AlertTriangle, Download } from 'lucide-react';
import type { Material } from '@/types';

interface MaterialsProps {
    jobId?: number;
}

export default function Materials({ jobId: _ }: MaterialsProps) {
    const { currentUser } = useAuth();
    const navigate = useNavigate();

    // Mock materials data
    const [materials] = useState<Material[]>([
        {
            id: 'm1',
            name: 'Interior Paint - Eggshell',
            sku: 'PAI-INT-001',
            quantity: 5,
            supplier: 'Home Depot',
            priceRange: '$45-60/gal',
            status: 'FM Verified',
            deliveryStatus: 'Delivered'
        },
        {
            id: 'm2',
            name: 'Drywall Joint Compound',
            sku: 'DRY-JNT-002',
            quantity: 3,
            supplier: 'Ace Hardware',
            priceRange: '$15-20/bucket',
            status: 'AI Generated',
            deliveryStatus: 'Ordered'
        },
        {
            id: 'm3',
            name: 'Painter\'s Tape',
            sku: 'TAP-PAI-001',
            quantity: 10,
            supplier: '3M Distributor',
            priceRange: '$3-5/roll',
            status: 'FM Verified',
            deliveryStatus: 'Delivered'
        }
    ]);

    const navItems = [
        { label: 'Dashboard', path: '/fm/dashboard', icon: <Package className="w-5 h-5" /> },
        { label: 'Materials', path: '/materials', icon: <Package className="w-5 h-5" /> },
    ];

    const getMaterialStatusVariant = (status: string) => {
        switch (status) {
            case 'FM Verified': return 'success';
            case 'Issues Found': return 'danger';
            default: return 'warning';
        }
    };



    return (
        <PortalLayout title="Materials List" navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                {/* Header */}
                <Card hover={false}>
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Materials</h2>
                            <p className="text-gray-600 dark:text-gray-400 mt-2">
                                {currentUser?.role === 'fm' && 'Verify and manage AI-generated materials list'}
                                {currentUser?.role === 'customer' && 'Review materials for your job'}
                                {currentUser?.role === 'admin' && 'Audit materials across all jobs'}
                                {currentUser?.role === 'contractor' && 'View verified materials for your job'}
                            </p>
                        </div>
                        {currentUser?.role !== 'contractor' && (
                            <Button onClick={() => navigate('/materials/purchase')}>
                                <Download className="w-4 h-4 mr-2" />
                                Material Purchase
                            </Button>
                        )}
                    </div>
                </Card>

                {/* Materials Table */}
                <Card hover={false} className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-gray-200 dark:border-gray-700">
                                <th className="text-left px-4 py-3 font-semibold text-gray-900 dark:text-white">Item Name</th>
                                <th className="text-left px-4 py-3 font-semibold text-gray-900 dark:text-white">SKU</th>
                                <th className="text-left px-4 py-3 font-semibold text-gray-900 dark:text-white">Qty</th>
                                <th className="text-left px-4 py-3 font-semibold text-gray-900 dark:text-white">Supplier</th>
                                <th className="text-left px-4 py-3 font-semibold text-gray-900 dark:text-white">Price Range</th>
                                <th className="text-left px-4 py-3 font-semibold text-gray-900 dark:text-white">Status</th>
                                {currentUser?.role === 'fm' && (
                                    <>
                                        <th className="text-left px-4 py-3 font-semibold text-gray-900 dark:text-white">Verify</th>
                                        <th className="text-left px-4 py-3 font-semibold text-gray-900 dark:text-white">Edit</th>
                                    </>
                                )}
                            </tr>
                        </thead>
                        <tbody>
                            {materials.map((material) => (
                                <tr key={material.id} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                                    <td className="px-4 py-3 text-gray-900 dark:text-white font-medium">{material.name}</td>
                                    <td className="px-4 py-3 text-gray-600 dark:text-gray-400 text-sm">{material.sku}</td>
                                    <td className="px-4 py-3 text-gray-600 dark:text-gray-400">{material.quantity}</td>
                                    <td className="px-4 py-3 text-gray-600 dark:text-gray-400 text-sm">{material.supplier}</td>
                                    <td className="px-4 py-3 text-gray-600 dark:text-gray-400 text-sm">{material.priceRange}</td>
                                    <td className="px-4 py-3">
                                        <Badge variant={getMaterialStatusVariant(material.status)}>
                                            {material.status}
                                        </Badge>
                                    </td>
                                    {currentUser?.role === 'fm' && (
                                        <>
                                            <td className="px-4 py-3">
                                                {material.status !== 'FM Verified' && (
                                                    <Button size="sm" variant="outline">
                                                        <CheckCircle className="w-4 h-4" />
                                                    </Button>
                                                )}
                                            </td>
                                            <td className="px-4 py-3">
                                                <Button size="sm" variant="outline">Edit</Button>
                                            </td>
                                        </>
                                    )}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </Card>

                {/* Info Banner */}
                <Card className="bg-blue-50 dark:bg-blue-950/30 border-blue-200 dark:border-blue-800">
                    <div className="flex items-start space-x-3">
                        <AlertTriangle className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                        <div>
                            <h3 className="font-semibold text-blue-900 dark:text-blue-200">Material Information</h3>
                            <p className="text-sm text-blue-800 dark:text-blue-300 mt-1">
                                • <strong>AI Generated:</strong> Materials suggested by AI analysis
                            </p>
                            <p className="text-sm text-blue-800 dark:text-blue-300">
                                • <strong>FM Verified:</strong> Field Manager has verified and approved materials
                            </p>
                            <p className="text-sm text-blue-800 dark:text-blue-300">
                                • <strong>Issues Found:</strong> Problems with delivery or quality detected
                            </p>
                            <p className="text-sm text-blue-800 dark:text-blue-300 mt-2">
                                Customers purchase materials directly from suppliers. Apex does not handle material payments.
                            </p>
                        </div>
                    </div>
                </Card>
            </div>
        </PortalLayout>
    );
}
