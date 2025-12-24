import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import {
    LayoutDashboard,
    ClipboardList,
    FileEdit,
    Plus,
    Trash2,
    Save,
    AlertCircle
} from 'lucide-react';
import { jobs, createDispute } from '@/data/mockData';
import { formatCurrency } from '@/lib/utils';

export default function ChangeOrderForm() {
    const { jobId } = useParams();
    const navigate = useNavigate();
    const { currentUser } = useAuth();

    const [reason, setReason] = useState('');
    const [lineItems, setLineItems] = useState<Array<{
        description: string;
        category: 'Labor' | 'Material';
        quantity: number;
        rate: number;
    }>>([
        { description: '', category: 'Labor', quantity: 1, rate: 0 }
    ]);

    const job = jobs.find(j => j.id === Number(jobId));

    const navItems = [
        { label: 'Dashboard', path: '/fm/dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
        { label: 'Site Visits', path: '/fm/dashboard', icon: <ClipboardList className="w-5 h-5" /> },
        { label: 'Change Orders', path: '/fm/dashboard', icon: <FileEdit className="w-5 h-5" /> },
    ];

    if (!job) {
        return (
            <PortalLayout title="Job Not Found" navItems={navItems}>
                <Card className="text-center py-12">
                    <p className="text-gray-600 dark:text-gray-400">Job not found.</p>
                    <Button onClick={() => navigate('/fm/dashboard')} className="mt-4">
                        Back to Dashboard
                    </Button>
                </Card>
            </PortalLayout>
        );
    }

    const addLineItem = () => {
        setLineItems([...lineItems, { description: '', category: 'Labor', quantity: 1, rate: 0 }]);
    };

    const removeLineItem = (index: number) => {
        setLineItems(lineItems.filter((_, i) => i !== index));
    };

    const updateLineItem = (index: number, field: string, value: any) => {
        const updated = [...lineItems];
        updated[index] = { ...updated[index], [field]: value };
        setLineItems(updated);
    };

    const calculateTotal = () => {
        return lineItems.reduce((sum, item) => sum + (item.quantity * item.rate), 0);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        const validLineItems = lineItems.filter(item => item.description && item.rate > 0);

        if (!reason.trim()) {
            alert('Please provide a reason for the change order.');
            return;
        }

        if (validLineItems.length === 0) {
            alert('Please add at least one line item.');
            return;
        }

        const changeOrderDetails = `Change Order Request:\nReason: ${reason}\n\nAdditional Costs:\n${validLineItems.map(item =>
            `- ${item.description}: ${item.quantity} x ${formatCurrency(item.rate)} = ${formatCurrency(item.quantity * item.rate)}`
        ).join('\n')}\n\nTotal Additional: ${formatCurrency(calculateTotal())}`;

        createDispute(job.id, 'fm', 'Change Order Request', changeOrderDetails);

        alert('Change order submitted for admin approval!');
        navigate('/fm/dashboard');
    };

    return (
        <PortalLayout title={`Change Order: ${job.propertyAddress}`} navItems={navItems}>
            <form onSubmit={handleSubmit} className="space-y-6 animate-fade-in">
                {/* Job Info */}
                <Card>
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Job Information</h3>
                    <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                        <p><span className="font-medium">Property:</span> {job.propertyAddress}</p>
                        <p><span className="font-medium">Customer:</span> {job.customerName}</p>
                        <p><span className="font-medium">Trade:</span> {job.trade}</p>
                    </div>
                </Card>

                {/* Warning */}
                <Card className="bg-yellow-50 dark:bg-yellow-900/10 border-yellow-200 dark:border-yellow-800">
                    <div className="flex items-start space-x-3">
                        <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5" />
                        <div>
                            <h4 className="font-semibold text-yellow-800 dark:text-yellow-300 mb-1">Change Order Notice</h4>
                            <p className="text-sm text-yellow-700 dark:text-yellow-400">
                                This will create a change order request requiring admin approval. The customer will be notified
                                of additional costs before work proceeds.
                            </p>
                        </div>
                    </div>
                </Card>

                {/* Reason */}
                <Card>
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Reason for Change Order</h3>
                    <textarea
                        value={reason}
                        onChange={(e) => setReason(e.target.value)}
                        rows={4}
                        className="w-full px-4 py-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent smooth-transition resize-none"
                        placeholder="Explain why additional work is needed (e.g., discovered damage, customer requested additions, unforeseen complications...)"
                        required
                    />
                </Card>

                {/* Additional Line Items */}
                <Card>
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="font-semibold text-gray-900 dark:text-white">Additional Work & Costs</h3>
                        <Button type="button" variant="outline" size="sm" onClick={addLineItem}>
                            <Plus className="w-4 h-4 mr-2" />
                            Add Item
                        </Button>
                    </div>

                    <div className="space-y-3">
                        {lineItems.map((item, index) => (
                            <Card key={index} hover={false} className="bg-gray-50 dark:bg-gray-800/50">
                                <div className="grid grid-cols-12 gap-3">
                                    <div className="col-span-12 md:col-span-4">
                                        <Input
                                            label="Description"
                                            value={item.description}
                                            onChange={(e) => updateLineItem(index, 'description', e.target.value)}
                                            placeholder="e.g., Repair water damage"
                                            required
                                        />
                                    </div>
                                    <div className="col-span-6 md:col-span-2">
                                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                            Category
                                        </label>
                                        <select
                                            value={item.category}
                                            onChange={(e) => updateLineItem(index, 'category', e.target.value)}
                                            className="w-full px-4 py-2 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-400"
                                        >
                                            <option value="Labor">Labor</option>
                                            <option value="Material">Material</option>
                                        </select>
                                    </div>
                                    <div className="col-span-6 md:col-span-2">
                                        <Input
                                            type="number"
                                            label="Qty"
                                            value={item.quantity}
                                            onChange={(e) => updateLineItem(index, 'quantity', parseFloat(e.target.value) || 0)}
                                            min="0"
                                            step="0.01"
                                            required
                                        />
                                    </div>
                                    <div className="col-span-8 md:col-span-2">
                                        <Input
                                            type="number"
                                            label="Rate"
                                            value={item.rate}
                                            onChange={(e) => updateLineItem(index, 'rate', parseFloat(e.target.value) || 0)}
                                            min="0"
                                            step="0.01"
                                            required
                                        />
                                    </div>
                                    <div className="col-span-8 md:col-span-2 flex items-end justify-between">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                                Total
                                            </label>
                                            <p className="font-semibold text-purple-600 dark:text-purple-400">
                                                {formatCurrency(item.quantity * item.rate)}
                                            </p>
                                        </div>
                                        {lineItems.length > 1 && (
                                            <button
                                                type="button"
                                                onClick={() => removeLineItem(index)}
                                                className="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg smooth-transition"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </Card>
                        ))}
                    </div>

                    <Card className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20 border-purple-200 dark:border-purple-800 mt-4">
                        <div className="flex items-center justify-between">
                            <span className="text-lg font-semibold text-gray-900 dark:text-white">Total Additional Cost:</span>
                            <span className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                                {formatCurrency(calculateTotal())}
                            </span>
                        </div>
                    </Card>
                </Card>

                {/* Actions */}
                <div className="flex space-x-4">
                    <Button type="submit" variant="primary" className="flex-1">
                        <Save className="w-4 h-4 mr-2" />
                        Submit Change Order
                    </Button>
                    <Button
                        type="button"
                        variant="outline"
                        onClick={() => navigate('/fm/dashboard')}
                    >
                        Cancel
                    </Button>
                </div>
            </form>
        </PortalLayout>
    );
}
