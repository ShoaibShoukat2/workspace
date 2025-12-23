import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import {
    LayoutDashboard,
    ShieldCheck,
    Briefcase,
    Wallet as WalletIcon,
    Upload,
    FileText,
    AlertCircle,
    CheckCircle,
    Calendar
} from 'lucide-react';
import { contractorApiService } from '@/lib/contractorApi';
import { formatDate } from '@/lib/utils';

export default function ComplianceHub() {
    const { currentUser } = useAuth();
    const navigate = useNavigate();

    const [compliance, setCompliance] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [uploading, setUploading] = useState<string | null>(null);

    useEffect(() => {
        const fetchCompliance = async () => {
            try {
                setLoading(true);
                setError(null);
                const response = await contractorApiService.getCompliance();
                setCompliance(response.results);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load compliance data');
            } finally {
                setLoading(false);
            }
        };

        fetchCompliance();
    }, []);

    const navItems = [
        { label: 'Dashboard', path: '/contractor/dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
        { label: 'Job Board', path: '/contractor/jobs', icon: <Briefcase className="w-5 h-5" /> },
        { label: 'Compliance Hub', path: '/contractor/compliance', icon: <ShieldCheck className="w-5 h-5" /> },
        { label: 'Wallet', path: '/contractor/wallet', icon: <WalletIcon className="w-5 h-5" /> },
    ];

    const handleFileUpload = async (type: 'w9' | 'insurance') => {
        try {
            // Create a file input for upload
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.pdf,.jpg,.jpeg,.png';
            
            input.onchange = async (e) => {
                const file = (e.target as HTMLInputElement).files?.[0];
                if (!file) return;

                const formData = new FormData();
                formData.append('document', file);
                formData.append('document_type', type === 'w9' ? 'W9' : 'INSURANCE');

                try {
                    setUploading(type);
                    await contractorApiService.uploadCompliance(formData);
                    
                    // Refresh compliance data
                    const response = await contractorApiService.getCompliance();
                    setCompliance(response.results);
                    
                    alert(`${type === 'w9' ? 'W-9' : 'Insurance Certificate'} uploaded successfully!`);
                } catch (err) {
                    alert('Failed to upload document. Please try again.');
                } finally {
                    setUploading(null);
                }
            };
            
            input.click();
        } catch (err) {
            alert('Failed to upload document');
        }
    };

    const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        // Note: This would need an API endpoint to update insurance expiry date
        // For now, we'll just update locally
        console.log('Insurance expiry date updated:', e.target.value);
    };

    const handleAgreementToggle = (agreement: 'independent' | 'liability' | 'payment') => {
        // Note: This would need an API endpoint to update agreement status
        // For now, we'll just show a message
        alert(`${agreement} agreement status updated (would be saved via API)`);
    };

    const getDocumentStatus = (docType: string) => {
        return compliance.find(doc => doc.document_type === docType);
    };

    const w9Doc = getDocumentStatus('W9');
    const insuranceDoc = getDocumentStatus('INSURANCE');

    const isExpiringWithin30Days = () => {
        if (!insuranceDoc?.expiry_date) return false;
        const expiry = new Date(insuranceDoc.expiry_date);
        const now = new Date();
        const thirtyDaysFromNow = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);
        return expiry < thirtyDaysFromNow && expiry > now;
    };

    const allCompliant = w9Doc?.status === 'approved' && 
                        insuranceDoc?.status === 'approved' && 
                        insuranceDoc?.expiry_date && 
                        new Date(insuranceDoc.expiry_date) > new Date();

    if (loading) {
        return (
            <PortalLayout title="Compliance Hub" navItems={navItems}>
                <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                    <span className="ml-3 text-gray-600 dark:text-gray-400">Loading compliance data...</span>
                </div>
            </PortalLayout>
        );
    }

    if (error) {
        return (
            <PortalLayout title="Compliance Hub" navItems={navItems}>
                <Card className="text-center py-12">
                    <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
                    <Button onClick={() => window.location.reload()}>Retry</Button>
                </Card>
            </PortalLayout>
        );
    }

    return (
        <PortalLayout title="Compliance Hub" navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                {/* Current Status */}
                <Card className={`${allCompliant ? 'bg-green-500/10 border-green-500/30' : 'bg-red-500/10 border-red-500/30'}`}>
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <div className={`w-16 h-16 rounded-full flex items-center justify-center ${allCompliant ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
                                {allCompliant ? (
                                    <CheckCircle className="w-8 h-8 text-green-400" />
                                ) : (
                                    <AlertCircle className="w-8 h-8 text-red-400" />
                                )}
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-gray-900 dark:text-white">Compliance Status</h3>
                                <Badge variant={allCompliant ? 'success' : 'danger'}>
                                    {allCompliant ? 'ACTIVE - All Clear' : 'BLOCKED - Action Required'}
                                </Badge>
                                {!allCompliant && (
                                    <p className="text-sm text-red-300 mt-2">
                                        Complete all requirements below to accept jobs
                                    </p>
                                )}
                            </div>
                        </div>
                    </div>
                </Card>

                {/* Expiring Soon Warning */}
                {isExpiringWithin30Days() && (
                    <Card className="bg-yellow-500/10 border-yellow-500/30">
                        <div className="flex items-start space-x-3">
                            <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-1" />
                            <div>
                                <h4 className="font-semibold text-yellow-800 dark:text-yellow-300">Insurance Expiring Soon!</h4>
                                <p className="text-sm text-yellow-700 dark:text-yellow-200 mt-1">
                                    Your insurance expires on {formatDate(insuranceDoc?.expiry_date || '')}. Please renew soon to avoid service interruption.
                                </p>
                            </div>
                        </div>
                    </Card>
                )}

                {/* Document Uploads */}
                <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Document Uploads</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* W-9 Upload */}
                        <Card hover={false}>
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center space-x-3">
                                    <FileText className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                                    <div>
                                        <h3 className="font-semibold text-gray-900 dark:text-white">W-9 Form</h3>
                                        <p className="text-sm text-gray-600 dark:text-gray-400">Tax documentation</p>
                                    </div>
                                </div>
                                {w9Doc?.status === 'approved' && (
                                    <CheckCircle className="w-5 h-5 text-green-500 dark:text-green-400" />
                                )}
                            </div>
                            <Button
                                variant={w9Doc ? 'outline' : 'primary'}
                                size="sm"
                                className="w-full"
                                onClick={() => handleFileUpload('w9')}
                                disabled={uploading === 'w9'}
                            >
                                {uploading === 'w9' ? (
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                                ) : (
                                    <Upload className="w-4 h-4 mr-2" />
                                )}
                                {w9Doc ? 'Re-upload W-9' : 'Upload W-9'}
                            </Button>
                            {w9Doc && (
                                <div className="mt-2 text-xs">
                                    <Badge variant={w9Doc.status === 'approved' ? 'success' : w9Doc.status === 'rejected' ? 'danger' : 'warning'}>
                                        {w9Doc.status}
                                    </Badge>
                                    <p className="text-gray-500 mt-1">Uploaded: {formatDate(w9Doc.uploaded_date)}</p>
                                </div>
                            )}
                        </Card>

                        {/* Insurance Certificate */}
                        <Card hover={false}>
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center space-x-3">
                                    <ShieldCheck className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                                    <div>
                                        <h3 className="font-semibold text-gray-900 dark:text-white">Insurance Certificate</h3>
                                        <p className="text-sm text-gray-600 dark:text-gray-400">Liability insurance</p>
                                    </div>
                                </div>
                                {insuranceDoc?.status === 'approved' && (
                                    <CheckCircle className="w-5 h-5 text-green-500 dark:text-green-400" />
                                )}
                            </div>
                            <Button
                                variant={insuranceDoc ? 'outline' : 'primary'}
                                size="sm"
                                className="w-full"
                                onClick={() => handleFileUpload('insurance')}
                                disabled={uploading === 'insurance'}
                            >
                                {uploading === 'insurance' ? (
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                                ) : (
                                    <Upload className="w-4 h-4 mr-2" />
                                )}
                                {insuranceDoc ? 'Re-upload Certificate' : 'Upload Certificate'}
                            </Button>
                            {insuranceDoc && (
                                <div className="mt-2 text-xs">
                                    <Badge variant={insuranceDoc.status === 'approved' ? 'success' : insuranceDoc.status === 'rejected' ? 'danger' : 'warning'}>
                                        {insuranceDoc.status}
                                    </Badge>
                                    <p className="text-gray-500 mt-1">Uploaded: {formatDate(insuranceDoc.uploaded_date)}</p>
                                </div>
                            )}
                        </Card>
                    </div>

                    {/* Insurance Expiry Date */}
                    <Card hover={false} className="mt-6">
                        <div className="flex items-center space-x-3 mb-4">
                            <Calendar className="w-6 h-6 text-cyan-600 dark:text-cyan-400" />
                            <div>
                                <h3 className="font-semibold text-gray-900 dark:text-white">Insurance Expiration Date</h3>
                                <p className="text-sm text-gray-600 dark:text-gray-400">When does your insurance expire?</p>
                            </div>
                        </div>
                        <Input
                            type="date"
                            value={insuranceDoc?.expiry_date || ''}
                            onChange={handleDateChange}
                            className="max-w-md border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        />
                        {insuranceDoc?.expiry_date && (
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                                Expires: {formatDate(insuranceDoc.expiry_date)}
                            </p>
                        )}
                    </Card>
                </div>

                {/* Agreements */}
                <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Required Agreements</h2>
                    <div className="space-y-4">
                        {/* Independent Contractor Agreement */}
                        <Card hover={false}>
                            <div className="flex items-start justify-between">
                                <div className="flex items-start space-x-4">
                                    <input
                                        type="checkbox"
                                        checked={compliance.independentAgreementSigned}
                                        onChange={() => handleAgreementToggle('independent')}
                                        className="mt-1 w-5 h-5 rounded border-gray-300 dark:border-white/20 bg-white dark:bg-white/5 text-purple-600 focus:ring-purple-500"
                                    />
                                    <div>
                                        <h3 className="font-semibold text-gray-900 dark:text-white">Independent Contractor Agreement</h3>
                                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                            I acknowledge that I am an independent contractor and not an employee of Apex Home Services.
                                        </p>
                                        <button className="text-sm text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 mt-2">
                                            View PDF →
                                        </button>
                                    </div>
                                </div>
                                {compliance.independentAgreementSigned && (
                                    <CheckCircle className="w-5 h-5 text-green-500 dark:text-green-400" />
                                )}
                            </div>
                        </Card>

                        {/* Liability Waiver */}
                        <Card hover={false}>
                            <div className="flex items-start justify-between">
                                <div className="flex items-start space-x-4">
                                    <input
                                        type="checkbox"
                                        checked={compliance.liabilityWaiverSigned}
                                        onChange={() => handleAgreementToggle('liability')}
                                        className="mt-1 w-5 h-5 rounded border-gray-300 dark:border-white/20 bg-white dark:bg-white/5 text-purple-600 focus:ring-purple-500"
                                    />
                                    <div>
                                        <h3 className="font-semibold text-gray-900 dark:text-white">Liability Waiver</h3>
                                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                            I carry adequate liability insurance and agree to hold Apex harmless for any claims arising from my work.
                                        </p>
                                        <button className="text-sm text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 mt-2">
                                            View PDF →
                                        </button>
                                    </div>
                                </div>
                                {compliance.liabilityWaiverSigned && (
                                    <CheckCircle className="w-5 h-5 text-green-500 dark:text-green-400" />
                                )}
                            </div>
                        </Card>

                        {/* Payment Terms */}
                        <Card hover={false}>
                            <div className="flex items-start justify-between">
                                <div className="flex items-start space-x-4">
                                    <input
                                        type="checkbox"
                                        checked={compliance.paymentTermsSigned}
                                        onChange={() => handleAgreementToggle('payment')}
                                        className="mt-1 w-5 h-5 rounded border-gray-300 dark:border-white/20 bg-white dark:bg-white/5 text-purple-600 focus:ring-purple-500"
                                    />
                                    <div>
                                        <h3 className="font-semibold text-gray-900 dark:text-white">Payment Terms</h3>
                                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                            I understand and agree to the payment terms, including payout schedules and material reimbursement policies.
                                        </p>
                                        <button className="text-sm text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 mt-2">
                                            View Terms →
                                        </button>
                                    </div>
                                </div>
                                {compliance.paymentTermsSigned && (
                                    <CheckCircle className="w-5 h-5 text-green-500 dark:text-green-400" />
                                )}
                            </div>
                        </Card>
                    </div>
                </div>

                {/* Summary */}
                <Card className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 border-purple-500/30">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Compliance Summary</h3>
                    <div className="space-y-3">
                        <div className="flex items-center justify-between">
                            <span className="text-gray-700 dark:text-gray-300">W-9 Uploaded</span>
                            {compliance.w9Uploaded ? (
                                <CheckCircle className="w-5 h-5 text-green-400" />
                            ) : (
                                <AlertCircle className="w-5 h-5 text-red-400" />
                            )}
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-gray-700 dark:text-gray-300">Insurance Certificate</span>
                            {compliance.insuranceUploaded ? (
                                <CheckCircle className="w-5 h-5 text-green-400" />
                            ) : (
                                <AlertCircle className="w-5 h-5 text-red-400" />
                            )}
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-gray-700 dark:text-gray-300">Insurance Valid</span>
                            {compliance.insuranceExpiryDate && new Date(compliance.insuranceExpiryDate) > new Date() ? (
                                <CheckCircle className="w-5 h-5 text-green-400" />
                            ) : (
                                <AlertCircle className="w-5 h-5 text-red-400" />
                            )}
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-gray-700 dark:text-gray-300">All Agreements Signed</span>
                            {compliance.independentAgreementSigned && compliance.liabilityWaiverSigned && compliance.paymentTermsSigned ? (
                                <CheckCircle className="w-5 h-5 text-green-400" />
                            ) : (
                                <AlertCircle className="w-5 h-5 text-red-400" />
                            )}
                        </div>
                    </div>
                </Card>

                {allCompliant && (
                    <div className="text-center">
                        <Button variant="primary" size="lg" onClick={() => navigate('/contractor/dashboard')}>
                            ✓ All Set! Return to Dashboard
                        </Button>
                    </div>
                )}
            </div>
        </PortalLayout>
    );
}
