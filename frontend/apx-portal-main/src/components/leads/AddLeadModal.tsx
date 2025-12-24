import React, { useState } from 'react';
import { X, User, Home, Phone, Mail, FileText } from 'lucide-react';
import Button from '@/components/ui/Button';
import { addLead } from '@/data/mockData';

interface AddLeadModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

export default function AddLeadModal({ isOpen, onClose, onSuccess }: AddLeadModalProps) {
    const [formData, setFormData] = useState({
        name: '',
        property: '',
        phone: '',
        email: '',
        notes: ''
    });

    if (!isOpen) return null;

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        // Add to mock DB
        addLead({
            name: formData.name,
            property: formData.property,
            stage: 'New',
            phone: formData.phone,
            email: formData.email,
            source: 'Manual'
        });

        // Reset and close
        setFormData({ name: '', property: '', phone: '', email: '', notes: '' });
        onSuccess();
        onClose();
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fade-in">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-md mx-4 overflow-hidden border border-gray-100 dark:border-gray-700">

                {/* Header */}
                <div className="flex justify-between items-center p-4 border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
                    <h3 className="font-bold text-lg text-gray-900 dark:text-white">Add New Lead</h3>
                    <button onClick={onClose} className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors">
                        <X className="w-5 h-5 text-gray-500" />
                    </button>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="p-4 space-y-4">

                    {/* Name */}
                    <div className="space-y-1">
                        <label className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Client Name</label>
                        <div className="relative">
                            <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                            <input
                                required
                                type="text"
                                placeholder="e.g. John Smith"
                                className="w-full pl-9 pr-4 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all text-sm"
                                value={formData.name}
                                onChange={e => setFormData({ ...formData, name: e.target.value })}
                            />
                        </div>
                    </div>

                    {/* Property */}
                    <div className="space-y-1">
                        <label className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Property Address</label>
                        <div className="relative">
                            <Home className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                            <input
                                required
                                type="text"
                                placeholder="e.g. 123 Main St"
                                className="w-full pl-9 pr-4 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all text-sm"
                                value={formData.property}
                                onChange={e => setFormData({ ...formData, property: e.target.value })}
                            />
                        </div>
                    </div>

                    {/* Contact Info (Row) */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1">
                            <label className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Phone</label>
                            <div className="relative">
                                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                <input
                                    type="tel"
                                    placeholder="(555) 123-4567"
                                    className="w-full pl-9 pr-4 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all text-sm"
                                    value={formData.phone}
                                    onChange={e => setFormData({ ...formData, phone: e.target.value })}
                                />
                            </div>
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Email</label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                <input
                                    type="email"
                                    placeholder="john@example.com"
                                    className="w-full pl-9 pr-4 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all text-sm"
                                    value={formData.email}
                                    onChange={e => setFormData({ ...formData, email: e.target.value })}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Footer Actions */}
                    <div className="flex justify-end gap-3 pt-4 border-t border-gray-100 dark:border-gray-700 mt-2">
                        <Button type="button" variant="ghost" onClick={onClose}>
                            Cancel
                        </Button>
                        <Button type="submit">
                            Save Lead
                        </Button>
                    </div>

                </form>
            </div>
        </div>
    );
}
