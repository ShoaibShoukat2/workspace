import { useState } from 'react';

import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import {
    LayoutDashboard,
    ShieldCheck,
    AlertTriangle,
    DollarSign,
    FileText,
    Briefcase,
    Calendar,
    Users,
    CheckCircle,
    XCircle,
    AlertCircle
} from 'lucide-react';
import { contractors, updateContractorCompliance } from '@/data/mockData';
import { formatDate } from '@/lib/utils';

export default function LegalCompliance() {
    const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'blocked'>('all');

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

    const filteredContractors = contractors.filter(c =>
        filterStatus === 'all' ? true : c.complianceStatus === filterStatus
    );

    const handleApprove = (contractorId: number) => {
        updateContractorCompliance(contractorId, { complianceStatus: 'active' });
        alert('Contractor approved and unblocked!');
    };

    const handleBlock = (contractorId: number) => {
        updateContractorCompliance(contractorId, { complianceStatus: 'blocked' });
        alert('Contractor blocked from accepting jobs.');
    };

    return (
        <PortalLayout title="Legal & Compliance" navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                {/* Filters */}
                <Card hover={false}>
                    <div className="flex items-center justify-between">
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Contractor Compliance</h2>
                        <div className="flex space-x-2">
                            {['all', 'active', 'blocked'].map((status) => (
                                <button
                                    key={status}
                                    onClick={() => setFilterStatus(status as any)}
                                    className={`px-4 py-2 rounded-lg text-sm font-medium smooth-transition ${filterStatus === status
                                        ? 'bg-purple-500 text-white'
                                        : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                                        }`}
                                >
                                    {status === 'all' ? 'All' : status === 'active' ? 'Active' : 'Blocked'}
                                </button>
                            ))}
                        </div>
                    </div>
                </Card>

                {/* Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card hover={false} className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
                        <div className="flex items-center space-x-3">
                            <CheckCircle className="w-10 h-10 text-green-600 dark:text-green-400" />
                            <div>
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                                    {contractors.filter(c => c.complianceStatus === 'active').length}
                                </p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">Active</p>
                            </div>
                        </div>
                    </Card>

                    <Card hover={false} className="bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
                        <div className="flex items-center space-x-3">
                            <XCircle className="w-10 h-10 text-red-600 dark:text-red-400" />
                            <div>
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                                    {contractors.filter(c => c.complianceStatus === 'blocked').length}
                                </p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">Blocked</p>
                            </div>
                        </div>
                    </Card>

                    <Card hover={false} className="bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800">
                        <div className="flex items-center space-x-3">
                            <AlertCircle className="w-10 h-10 text-yellow-600 dark:text-yellow-400" />
                            <div>
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                                    {contractors.filter(c => c.insuranceExpiry && new Date(c.insuranceExpiry) < new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)).length}
                                </p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">Expiring Soon</p>
                            </div>
                        </div>
                    </Card>
                </div>

                {/* Contractors List */}
                <div className="space-y-4">
                    {filteredContractors.map((contractor) => (
                        <Card key={contractor.id}>
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center space-x-3 mb-2">
                                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{contractor.name}</h3>
                                        <Badge variant={contractor.complianceStatus === 'active' ? 'success' : 'danger'}>
                                            {contractor.complianceStatus}
                                        </Badge>
                                    </div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                                        Trade: {contractor.trade} • Email: {contractor.email}
                                    </p>

                                    {/* Compliance Items */}
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                                        <div className={`flex items-center space-x-2 ${contractor.hasW9 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                                            {contractor.hasW9 ? <CheckCircle className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                                            <span>W-9 Form</span>
                                        </div>
                                        <div className={`flex items-center space-x-2 ${contractor.insuranceCert ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                                            {contractor.insuranceCert ? <CheckCircle className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                                            <span>Insurance Certificate</span>
                                        </div>
                                        <div className={`flex items-center space-x-2 ${contractor.signedAgreement ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                                            {contractor.signedAgreement ? <CheckCircle className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                                            <span>Signed Agreement</span>
                                        </div>
                                    </div>

                                    {contractor.insuranceExpiry && (
                                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                                            Insurance expires: {formatDate(contractor.insuranceExpiry)}
                                        </p>
                                    )}
                                </div>

                                <div className="flex space-x-2">
                                    {contractor.complianceStatus === 'blocked' ? (
                                        <Button variant="primary" size="sm" onClick={() => handleApprove(contractor.id)}>
                                            <CheckCircle className="w-4 h-4 mr-2" />
                                            Approve
                                        </Button>
                                    ) : (
                                        <Button variant="danger" size="sm" onClick={() => handleBlock(contractor.id)}>
                                            <XCircle className="w-4 h-4 mr-2" />
                                            Block
                                        </Button>
                                    )}
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>
            </div>
        </PortalLayout>
    );
}
