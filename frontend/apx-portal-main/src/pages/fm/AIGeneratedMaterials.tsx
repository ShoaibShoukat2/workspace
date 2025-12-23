import { useState } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
// import Badge from '@/components/ui/Badge';
import { Material } from '@/types';
import { CheckCircle, Plus, Trash2, Sparkles } from 'lucide-react';

interface AIGeneratedMaterialsProps {
    materials: Material[];
    onSave: (materials: Material[]) => void;
    onCancel: () => void;
}

export default function AIGeneratedMaterials({ materials, onSave, onCancel }: AIGeneratedMaterialsProps) {
    const [editedMaterials, setEditedMaterials] = useState<Material[]>(
        materials.map(m => ({ ...m })) // Deep copy for editing
    );

    const handleQuantityChange = (index: number, qty: number) => {
        const updated = [...editedMaterials];
        updated[index].quantity = qty;
        setEditedMaterials(updated);
    };

    const handleRemove = (index: number) => {
        setEditedMaterials(editedMaterials.filter((_, i) => i !== index));
    };

    const handleAdd = () => {
        setEditedMaterials([
            ...editedMaterials,
            {
                id: `new-${Date.now()}`,
                name: '',
                sku: '',
                quantity: 1,
                supplier: '',
                priceRange: '',
                status: 'FM Verified'
            }
        ]);
    };

    const handleUpdateField = (index: number, field: keyof Material, value: string) => {
        const updated = [...editedMaterials];
        (updated[index] as any)[field] = value;
        setEditedMaterials(updated);
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-white dark:bg-gray-900 shadow-2xl">
                <div className="flex items-center justify-between mb-6 sticky top-0 bg-white dark:bg-gray-900 pb-4 border-b border-gray-100 dark:border-gray-800 z-10">
                    <div>
                        <div className="flex items-center gap-2">
                            <Sparkles className="w-5 h-5 text-purple-500" />
                            <h2 className="text-xl font-bold text-gray-900 dark:text-white">AI Material List Verification</h2>
                        </div>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                            Review and verify the AI-suggested materials. You are responsible for accuracy.
                        </p>
                    </div>
                </div>

                <div className="space-y-4">
                    {/* Read-only AI Suggestion Context (Mock) */}
                    <div className="p-4 bg-purple-50 dark:bg-purple-900/10 rounded-xl border border-purple-100 dark:border-purple-800/30 mb-6">
                        <div className="flex items-start gap-3">
                            <div className="p-2 bg-purple-100 dark:bg-purple-800/30 rounded-lg">
                                <Sparkles className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                            </div>
                            <div>
                                <h4 className="font-semibold text-purple-900 dark:text-purple-100 text-sm">AI Analysis</h4>
                                <p className="text-xs text-purple-800 dark:text-purple-300 mt-1 leading-relaxed">
                                    Based on the scope "Paint 2 bedrooms and hallway", I have suggested premium white paint (approx 3 gallons), rollers, and drop cloths. Please verify quantities based on actual measurements.
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Material List */}
                    <div className="space-y-3">
                        {editedMaterials.map((item, index) => (
                            <div key={item.id} className="grid grid-cols-12 gap-3 items-end p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700 hover:border-purple-200 dark:hover:border-purple-700 smooth-transition group">
                                <div className="col-span-12 md:col-span-4">
                                    <Input
                                        label="Item Name"
                                        value={item.name}
                                        onChange={(e) => handleUpdateField(index, 'name', e.target.value)}
                                        placeholder="Material Name"
                                        className="bg-white dark:bg-gray-800"
                                    />
                                </div>
                                <div className="col-span-6 md:col-span-2">
                                    <Input
                                        label="SKU / ID"
                                        value={item.sku}
                                        onChange={(e) => handleUpdateField(index, 'sku', e.target.value)}
                                        placeholder="Optional SKU"
                                        className="bg-white dark:bg-gray-800"
                                    />
                                </div>
                                <div className="col-span-6 md:col-span-2">
                                    <Input
                                        label="Quantity"
                                        type="number"
                                        value={item.quantity}
                                        onChange={(e) => handleQuantityChange(index, parseFloat(e.target.value))}
                                        className="bg-white dark:bg-gray-800"
                                    />
                                </div>
                                <div className="col-span-6 md:col-span-3">
                                    <Input
                                        label="Supplier"
                                        value={item.supplier}
                                        onChange={(e) => handleUpdateField(index, 'supplier', e.target.value)}
                                        placeholder="Preferred Supplier"
                                        className="bg-white dark:bg-gray-800"
                                    />
                                </div>
                                <div className="col-span-6 md:col-span-1 flex justify-end pb-2">
                                    <button
                                        onClick={() => handleRemove(index)}
                                        className="p-2 text-red-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg smooth-transition"
                                        title="Remove Item"
                                    >
                                        <Trash2 className="w-5 h-5" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>

                    <Button variant="outline" onClick={handleAdd} className="w-full border-dashed border-2 py-4 text-gray-500 hover:text-purple-600 hover:border-purple-300">
                        <Plus className="w-5 h-5 mr-2" />
                        Add New Material
                    </Button>
                </div>

                <div className="flex items-center justify-end gap-3 mt-8 pt-6 border-t border-gray-100 dark:border-gray-800 sticky bottom-0 bg-white dark:bg-gray-900">
                    <Button variant="ghost" onClick={onCancel}>
                        Cancel
                    </Button>
                    <Button variant="primary" onClick={() => onSave(editedMaterials)}>
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Verify & Save List
                    </Button>
                </div>
            </Card>
        </div>
    );
}
