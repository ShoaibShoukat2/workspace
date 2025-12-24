import Card from '@/components/ui/Card';
import { AlertCircle, ExternalLink } from 'lucide-react';
import Button from '@/components/ui/Button';

// Using local mock data to ensure exact match with the standalone page request
// In a real app, this would come from the API or props, but for this visual sync request we use consistent mock data.
export const MOCK_PROJECT_MATERIALS = [
    { id: '1', name: 'Premium White Paint', sku: 'PNT-101', quantity: 3, supplier: 'Home Depot', priceRange: '$45-55', status: 'FM Verified' },
    { id: '2', name: 'Drywall Compound', sku: 'DW-202', quantity: 2, supplier: 'Lowe\'s', priceRange: '$20-25', status: 'FM Verified' },
    { id: '3', name: 'Sanding Sponges (3-Pack)', sku: 'SND-303', quantity: 5, supplier: 'True Value', priceRange: '$12-15', status: 'FM Verified' },
    { id: '4', name: 'Painter\'s Tape (Blue)', sku: 'TPE-404', quantity: 10, supplier: 'Home Depot', priceRange: '$6-8', status: 'FM Verified' },
    { id: '5', name: 'Drop Cloths (Canvas)', sku: 'CLT-505', quantity: 4, supplier: 'Lowe\'s', priceRange: '$15-18', status: 'FM Verified' },
    { id: '6', name: 'Roller Frame 9"', sku: 'RLR-606', quantity: 2, supplier: 'Sherwin Williams', priceRange: '$8-10', status: 'FM Verified' },
    { id: '7', name: 'Roller Covers 3/8" Nap', sku: 'CVR-707', quantity: 6, supplier: 'Sherwin Williams', priceRange: '$5-7', status: 'FM Verified' },
    { id: '8', name: 'Paint Tray Liner 5-Pack', sku: 'TRY-808', quantity: 2, supplier: 'Home Depot', priceRange: '$4-6', status: 'FM Verified' },
    { id: '9', name: 'Spackling Paste', sku: 'SPK-909', quantity: 1, supplier: 'Ace Hardware', priceRange: '$8-12', status: 'FM Verified' },
    { id: '10', name: 'Caulk Gun', sku: 'CLK-010', quantity: 1, supplier: 'Lowe\'s', priceRange: '$12-16', status: 'FM Verified' },
    { id: '11', name: 'White Silicone Caulk', sku: 'CLK-011', quantity: 3, supplier: 'Lowe\'s', priceRange: '$6-8', status: 'FM Verified' },
    { id: '12', name: 'Utility Knife Blades', sku: 'BLD-012', quantity: 1, supplier: 'Home Depot', priceRange: '$5-7', status: 'FM Verified' },
];

export default function MaterialsReadOnlyList() {
    // Ignoring props to force the "sunk" (synced) state requested by user
    const materials = MOCK_PROJECT_MATERIALS;

    const getSupplierInitials = (supplier: string) => {
        if (!supplier) return '??';
        if (supplier.includes('Home Depot')) return 'HD';
        if (supplier.includes('Lowe')) return 'LO';
        if (supplier.includes('Sherwin')) return 'SW';
        if (supplier.includes('Ace')) return 'AH';
        if (supplier.includes('True')) return 'TV';
        return supplier.substring(0, 2).toUpperCase();
    };

    return (
        <div className="space-y-4">
            <div className="flex items-start gap-2 p-3 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 text-xs rounded-lg mb-4">
                <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <p>
                    Apex does not track or supply materials. Use the links below to purchase directly from suppliers.
                </p>
            </div>

            {materials.map((item) => (
                <Card key={item.id} className="p-0 overflow-hidden hover:shadow-md transition-shadow duration-200 border border-gray-100 dark:border-gray-800">
                    <div className="flex items-center p-3">
                        {/* Icon */}
                        <div className="w-10 h-10 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center text-gray-500 dark:text-gray-400 font-bold text-xs tracking-wide mr-3 flex-shrink-0">
                            {getSupplierInitials(item.supplier)}
                        </div>

                        {/* Details */}
                        <div className="flex-1 min-w-0">
                            <h3 className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                                {item.name}
                            </h3>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                                Qty: {item.quantity} • {item.supplier}
                            </p>
                        </div>

                        {/* Supplier & Price */}
                        <div className="flex flex-col items-end gap-1 ml-3">
                            <div className="text-right">
                                <p className="font-bold text-xs text-gray-900 dark:text-white">
                                    {item.priceRange}
                                </p>
                            </div>
                            <Button
                                size="sm"
                                variant="outline"
                                className="h-6 px-2 text-[10px] gap-1"
                                onClick={() => window.open('https://www.homedepot.com', '_blank')}
                            >
                                Buy <ExternalLink className="w-3 h-3" />
                            </Button>
                        </div>
                    </div>
                </Card>
            ))}
        </div>
    );
}
