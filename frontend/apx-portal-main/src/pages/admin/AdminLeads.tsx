import { useState, useEffect } from 'react';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import { UserPlus, LayoutDashboard, Briefcase, ShieldCheck, AlertTriangle, FileText, DollarSign, Calendar, Users, Plus, Download } from 'lucide-react';
import { leads as initialLeads } from '@/data/mockData';
import AddLeadModal from '@/components/leads/AddLeadModal';

export default function AdminLeads() {
    const [leads, setLeads] = useState(initialLeads);
    const [isModalOpen, setIsModalOpen] = useState(false);

    // Refresh function to reload data from the mutable store
    const refreshLeads = () => {
        // In a real app, this would be an API call.
        // For mock data, we simply force a re-read of the imported array.
        // Spreading to create a new reference to trigger React re-render.
        setLeads([...initialLeads]);
    };

    const getStageColor = (stage: string) => {
        switch (stage) {
            case 'New': return 'info';
            case 'Contacted': return 'warning';
            case 'Proposal Sent': return 'primary';
            case 'Won': return 'success';
            default: return 'default';
        }
    };

    const navItems = [
        { label: 'Dashboard', path: '/admin/dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
        { label: 'Jobs', path: '/admin/jobs', icon: <Briefcase className="w-5 h-5" /> },
        { label: 'Legal & Compliance', path: '/admin/legal-compliance', icon: <ShieldCheck className="w-5 h-5" /> },
        { label: 'Disputes', path: '/admin/disputes', icon: <AlertTriangle className="w-5 h-5" /> },
        { label: 'Ledger', path: '/admin/ledger', icon: <FileText className="w-5 h-5" /> },
        { label: 'Payouts', path: '/admin/payouts', icon: <DollarSign className="w-5 h-5" /> },
        { label: 'Meetings', path: '/admin/meetings', icon: <Calendar className="w-5 h-5" /> },
        { label: 'Leads', path: '/admin/leads', icon: <Users className="w-5 h-5" /> },
    ];

    return (
        <PortalLayout title="Lead Pipeline" navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                <div className="flex justify-between items-center">
                    <h2 className="text-lg font-medium text-gray-700 dark:text-gray-300">Active Opportunities</h2>
                    <div className="flex gap-3">
                        <Button variant="outline" onClick={() => alert('Mock: Syncing with Angi...')}>
                            <Download className="w-4 h-4 mr-2" />
                            Import Angi Leads
                        </Button>
                        <Button onClick={() => setIsModalOpen(true)}>
                            <Plus className="w-4 h-4 mr-2" />
                            Add Manual Lead
                        </Button>
                    </div>
                </div>

                <Card>
                    <table className="w-full text-sm text-left">
                        <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-800">
                            <tr>
                                <th className="py-3 px-4 font-medium">Lead Name</th>
                                <th className="py-3 px-4 font-medium">Property</th>
                                <th className="py-3 px-4 font-medium">Date Added</th>
                                <th className="py-3 px-4 font-medium">Source</th>
                                <th className="py-3 px-4 font-medium">Stage</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                            {leads.map((l) => (
                                <tr key={l.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                                    <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">
                                        <div className="flex items-center space-x-3">
                                            <div className="p-1.5 bg-purple-100 dark:bg-purple-900/30 rounded-full">
                                                <UserPlus className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                                            </div>
                                            <span>{l.name}</span>
                                        </div>
                                    </td>
                                    <td className="py-3 px-4 text-gray-600 dark:text-gray-400">{l.property}</td>
                                    <td className="py-3 px-4 text-gray-600 dark:text-gray-400">{l.date}</td>
                                    <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                                        <span className="text-xs border border-gray-200 dark:border-gray-700 px-2 py-0.5 rounded-full">
                                            {l.source}
                                        </span>
                                    </td>
                                    <td className="py-3 px-4">
                                        <Badge variant={getStageColor(l.stage) as any}>{l.stage}</Badge>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </Card>
            </div>

            <AddLeadModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSuccess={refreshLeads}
            />
        </PortalLayout>
    );
}
