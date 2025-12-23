import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Badge, { getStatusBadgeVariant } from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import {
    LayoutDashboard,
    ClipboardList,
    FileEdit,
    Calculator,
    PenTool,
    Send,
    Camera,
    Ruler,
    AlertTriangle,
    Package,
    CheckCircle
} from 'lucide-react';
import { fmApiService } from '@/lib/fmApi';
import { formatCurrency } from '@/lib/utils';
import { Material } from '@/types';
import AIGeneratedMaterials from './AIGeneratedMaterials';

type TabType = 'visit' | 'quote' | 'signature';

// Mock AI Materials (in a real app, this would come from the backend based on trade/scope)
const MOCK_AI_MATERIALS: Material[] = [
    { id: 'm1', name: 'Premium Paint (Eggshell)', sku: 'PP-001', quantity: 5, supplier: 'Sherwin Williams', priceRange: '$45-50', status: 'AI Generated' },
    { id: 'm2', name: 'Roller Kit (9")', sku: 'RK-9', quantity: 2, supplier: 'Home Depot', priceRange: '$15-20', status: 'AI Generated' },
    { id: 'm3', name: 'Painters Tape (Blue)', sku: 'PT-2', quantity: 4, supplier: '3M', priceRange: '$5-8', status: 'AI Generated' },
];

export default function FMJobVisit() {
    const { jobId } = useParams();
    const navigate = useNavigate();
    useAuth();

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [job, setJob] = useState<any>(null);
    const [siteVisit, setSiteVisit] = useState<any>(null);
    const [activeTab, setActiveTab] = useState<TabType>('visit');
    const [signatureSaved, setSignatureSaved] = useState(false);
    const [processing, setProcessing] = useState(false);

    // Visit Form State
    const [measurements, setMeasurements] = useState({ display: '', verified: false });
    const [scopeConfirmed, setScopeConfirmed] = useState(false);
    const [beforePhotosUploaded, setBeforePhotosUploaded] = useState(false);
    const [toolsRequired, setToolsRequired] = useState<string[]>([]);
    const [laborRequired, setLaborRequired] = useState(1);
    const [estimatedTime, setEstimatedTime] = useState(4);
    const [safetyConcerns, setSafetyConcerns] = useState('');
    const [materials, setMaterials] = useState<Material[]>([]);
    const [showMaterialModal, setShowMaterialModal] = useState(false);

    useEffect(() => {
        const fetchJobData = async () => {
            if (!jobId) return;
            
            try {
                setLoading(true);
                setError(null);
                
                const [jobData, visitData] = await Promise.all([
                    fmApiService.getJobDetail(Number(jobId)),
                    fmApiService.getSiteVisit(Number(jobId)).catch(() => null) // Visit might not exist yet
                ]);
                
                setJob(jobData);
                setSiteVisit(visitData);
                
                // Load existing visit data if available
                if (visitData) {
                    setMeasurements(visitData.measurements || { display: '', verified: false });
                    setScopeConfirmed(visitData.scope_confirmed || false);
                    setBeforePhotosUploaded(visitData.photos_count > 0);
                    setToolsRequired(visitData.tools_required || []);
                    setLaborRequired(visitData.labor_required || 1);
                    setEstimatedTime(visitData.estimated_time || 4);
                    setSafetyConcerns(visitData.safety_concerns || '');
                    setSignatureSaved(visitData.customer_signed || false);
                }
                
                // Generate AI materials if not already done
                if (!materials.length) {
                    try {
                        const materialsResponse = await fmApiService.generateMaterials(Number(jobId));
                        setMaterials(materialsResponse.materials || []);
                    } catch (err) {
                        console.log('No AI materials available');
                    }
                }
                
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load job data');
            } finally {
                setLoading(false);
            }
        };

        fetchJobData();
    }, [jobId]);

    const calculateProgress = () => {
        let completed = 0;
        let total = 8; // Total steps

        if (beforePhotosUploaded) completed++;
        if (measurements.verified) completed++;
        if (scopeConfirmed) completed++;
        if (materials.some(m => m.status === 'FM Verified')) completed++;
        if (toolsRequired.length > 0) completed++;
        if (laborRequired > 0) completed++;
        if (estimatedTime > 0) completed++;
        if (signatureSaved) completed++;

        return { completed, total, percentage: (completed / total) * 100 };
    };

    const progress = calculateProgress();
    const isVisitComplete = progress.completed === progress.total;

    const handleMaterialsSave = async (updatedMaterials: Material[]) => {
        try {
            setProcessing(true);
            const verifiedMaterials = updatedMaterials.map(m => ({ ...m, status: 'FM Verified' as const }));
            
            await fmApiService.verifyMaterials(Number(jobId), verifiedMaterials);
            setMaterials(verifiedMaterials);
            setShowMaterialModal(false);
        } catch (err) {
            alert('Failed to save materials');
        } finally {
            setProcessing(false);
        }
    };

    const handlePhotoUpload = async () => {
        try {
            // Create a file input for upload
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            input.multiple = true;
            
            input.onchange = async (e) => {
                const files = (e.target as HTMLInputElement).files;
                if (!files || files.length === 0) return;

                const formData = new FormData();
                Array.from(files).forEach((file, index) => {
                    formData.append(`photo_${index}`, file);
                });

                try {
                    setProcessing(true);
                    await fmApiService.uploadSiteVisitPhoto(Number(jobId), formData);
                    setBeforePhotosUploaded(true);
                    alert('Photos uploaded successfully!');
                } catch (err) {
                    alert('Failed to upload photos');
                } finally {
                    setProcessing(false);
                }
            };
            
            input.click();
        } catch (err) {
            alert('Failed to upload photos');
        }
    };

    const handleSubmitVisit = async () => {
        if (!isVisitComplete) return;

        try {
            setProcessing(true);
            
            const visitData = {
                measurements,
                scope_confirmed: scopeConfirmed,
                tools_required: toolsRequired,
                labor_required: laborRequired,
                estimated_time: estimatedTime,
                safety_concerns: safetyConcerns,
                customer_signed: signatureSaved,
                photos_uploaded: beforePhotosUploaded
            };

            if (siteVisit) {
                await fmApiService.updateSiteVisit(Number(jobId), visitData);
                await fmApiService.completeSiteVisit(Number(jobId));
            } else {
                await fmApiService.startSiteVisit(Number(jobId), visitData);
                await fmApiService.completeSiteVisit(Number(jobId));
            }

            alert('Site visit submitted successfully!');
            navigate('/fm/dashboard');
        } catch (err) {
            alert('Failed to submit site visit');
        } finally {
            setProcessing(false);
        }
    };

    if (loading) {
        return (
            <PortalLayout title="Loading..." navItems={navItems}>
                <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                    <span className="ml-3 text-gray-600 dark:text-gray-400">Loading job details...</span>
                </div>
            </PortalLayout>
        );
    }

    if (error || !job) {
        return (
            <PortalLayout title="Job Not Found" navItems={navItems}>
                <Card className="text-center py-12">
                    <p className="text-red-600 dark:text-red-400 mb-4">{error || "Job not found."}</p>
                    <Button onClick={() => navigate('/fm/dashboard')}>Back to Dashboard</Button>
                </Card>
            </PortalLayout>
        );
    }

    const navItems = [
        { label: 'Dashboard', path: '/fm/dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
        { label: 'Site Visits', path: '/fm/dashboard', icon: <ClipboardList className="w-5 h-5" /> },
        { label: 'Change Orders', path: '/fm/dashboard', icon: <FileEdit className="w-5 h-5" /> },
    ];

    return (
        <PortalLayout title={`Site Visit: ${job.propertyAddress}`} navItems={navItems}>
            <div className="space-y-6 max-w-5xl mx-auto animate-fade-in pb-24">
                {/* Progress Header */}
                <Card className="bg-gradient-to-r from-gray-900 to-gray-800 text-white border-0">
                    <div className="flex items-center justify-between mb-2">
                        <div>
                            <h2 className="text-2xl font-bold">{job.customer_name}'s Property</h2>
                            <p className="text-gray-400">{job.title} • {job.location}</p>
                        </div>
                        <Badge variant={getStatusBadgeVariant(job.status)}>{job.status}</Badge>
                    </div>
                    <div className="mt-4">
                        <div className="flex justify-between text-sm mb-1">
                            <span className="font-medium text-gray-300">Mandatory Visit Completion</span>
                            <span className="font-bold text-purple-400">{progress.completed}/{progress.total} Steps</span>
                        </div>
                        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
                                style={{ width: `${progress.percentage}%` }}
                            />
                        </div>
                    </div>
                </Card>

                {/* Tabs */}
                <div className="flex space-x-2 border-b border-gray-200 dark:border-gray-700 overflow-x-auto">
                    {[
                        { id: 'visit', label: '1. Site Inspection', icon: <ClipboardList className="w-4 h-4" /> },
                        { id: 'quote', label: '2. Quote', icon: <Calculator className="w-4 h-4" /> },
                        { id: 'signature', label: '3. Sign-off', icon: <PenTool className="w-4 h-4" /> },
                    ].map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id as TabType)}
                            className={`px-6 py-3 flex items-center space-x-2 border-b-2 font-medium bg-transparent smooth-transition whitespace-nowrap ${activeTab === tab.id
                                ? 'border-purple-600 text-purple-600 dark:text-purple-400'
                                : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                                }`}
                        >
                            {tab.icon}
                            <span>{tab.label}</span>
                        </button>
                    ))}
                </div>

                {/* Content */}
                <div className="min-h-[400px]">
                    {/* STEP 1: SITE INSPECTION */}
                    {activeTab === 'visit' && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* 1. Photos */}
                            <Card className={beforePhotosUploaded ? "border-green-500/50 bg-green-50/10" : ""}>
                                <div className="flex items-center gap-3 mb-4">
                                    <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg text-blue-600">
                                        <Camera className="w-5 h-5" />
                                    </div>
                                    <h3 className="font-semibold text-lg dark:text-white">Before Photos</h3>
                                </div>
                                <div className="space-y-3">
                                    <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-xl p-6 text-center hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer transition-colors" onClick={handlePhotoUpload}>
                                        <Camera className="w-8 h-8 mx-auto text-gray-400 mb-2" />
                                        <p className="text-sm text-gray-500">Tap to upload photos</p>
                                    </div>
                                    {beforePhotosUploaded && (
                                        <div className="flex items-center text-green-600 dark:text-green-400 text-sm font-medium">
                                            <CheckCircle className="w-4 h-4 mr-1" /> Photos Uploaded
                                        </div>
                                    )}
                                </div>
                            </Card>

                            {/* 2. Measurements */}
                            <Card>
                                <div className="flex items-center gap-3 mb-4">
                                    <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg text-purple-600">
                                        <Ruler className="w-5 h-5" />
                                    </div>
                                    <h3 className="font-semibold text-lg dark:text-white">Measurements</h3>
                                </div>
                                <div className="space-y-3">
                                    <Input
                                        label="Room Dimensions / Area"
                                        placeholder="e.g., 12x14 Master Bed, 600 sqft total"
                                        value={measurements.display}
                                        onChange={(e) => setMeasurements({ ...measurements, display: e.target.value })}
                                    />
                                    <label className="flex items-center space-x-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={measurements.verified}
                                            onChange={(e) => setMeasurements({ ...measurements, verified: e.target.checked })}
                                            className="form-checkbox h-5 w-5 text-purple-600 rounded bg-gray-100 border-gray-300 focus:ring-purple-500"
                                        />
                                        <span className="text-gray-700 dark:text-gray-300">I verify these measurements are accurate</span>
                                    </label>
                                </div>
                            </Card>

                            {/* 3. Materials */}
                            <Card className="md:col-span-2">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-lg text-amber-600">
                                            <Package className="w-5 h-5" />
                                        </div>
                                        <h3 className="font-semibold text-lg dark:text-white">Materials Required</h3>
                                    </div>
                                    <Button size="sm" onClick={() => setShowMaterialModal(true)}>
                                        Review AI List
                                    </Button>
                                </div>
                                <div className="bg-gray-50 dark:bg-gray-800/10 rounded-xl p-4">
                                    {materials.some(m => m.status === 'FM Verified') ? (
                                        <div className="space-y-2">
                                            {materials.map((m) => (
                                                <div key={m.id} className="flex justify-between text-sm py-1 border-b border-gray-100 dark:border-gray-700 last:border-0">
                                                    <span className="text-gray-700 dark:text-gray-300">{m.name}</span>
                                                    <span className="font-medium text-gray-900 dark:text-white">x{m.quantity}</span>
                                                </div>
                                            ))}
                                            <div className="pt-2 text-green-600 text-sm flex items-center">
                                                <CheckCircle className="w-4 h-4 mr-1" /> Materials Verified
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="text-center text-gray-500 py-4">
                                            <p>AI has generated a suggestion list.</p>
                                            <p className="text-sm">Please review and verify to continue.</p>
                                        </div>
                                    )}
                                </div>
                            </Card>

                            {/* 4. Scope & Safety */}
                            <Card className="md:col-span-2">
                                <div className="flex items-center gap-3 mb-4">
                                    <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg text-red-600">
                                        <AlertTriangle className="w-5 h-5" />
                                    </div>
                                    <h3 className="font-semibold text-lg dark:text-white">Scope & Safety</h3>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <Input
                                        type="number"
                                        label="Labor Required (People)"
                                        value={laborRequired}
                                        onChange={(e) => setLaborRequired(Number(e.target.value))}
                                    />
                                    <Input
                                        type="number"
                                        label="Est. Time (Hours)"
                                        value={estimatedTime}
                                        onChange={(e) => setEstimatedTime(Number(e.target.value))}
                                    />
                                    <div className="md:col-span-2">
                                        <Input
                                            label="Tools Required (Comma separated)"
                                            placeholder="Ladder, Drill, Saw..."
                                            value={toolsRequired.join(', ')}
                                            onChange={(e) => setToolsRequired(e.target.value.split(',').map(s => s.trim()))}
                                        />
                                    </div>
                                    <div className="md:col-span-2">
                                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                            Safety Concerns
                                        </label>
                                        <textarea
                                            className="w-full rounded-xl border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 focus:ring-purple-500"
                                            rows={3}
                                            placeholder="None..."
                                            value={safetyConcerns}
                                            onChange={(e) => setSafetyConcerns(e.target.value)}
                                        />
                                    </div>
                                    <div className="md:col-span-2 pt-2">
                                        <label className="flex items-center space-x-2 cursor-pointer p-3 bg-gray-50 dark:bg-gray-800 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                                            <input
                                                type="checkbox"
                                                checked={scopeConfirmed}
                                                onChange={(e) => setScopeConfirmed(e.target.checked)}
                                                className="form-checkbox h-5 w-5 text-purple-600 rounded bg-white border-gray-300 focus:ring-purple-500"
                                            />
                                            <span className="font-medium text-gray-900 dark:text-white">I confirm the scope of work is accurate and site is ready.</span>
                                        </label>
                                    </div>
                                </div>
                            </Card>
                        </div>
                    )}

                    {/* STEP 2: QUOTE */}
                    {activeTab === 'quote' && (
                        <Card>
                            <div className="text-center py-12">
                                <Calculator className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                                <h3 className="text-xl font-semibold mb-2">Quote Generator</h3>
                                <p className="text-gray-500">Based on your verified materials and labor.</p>
                                <div className="mt-6 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg max-w-md mx-auto text-left">
                                    <h4 className="font-medium mb-2">Auto-Calculated Estimate:</h4>
                                    <div className="flex justify-between mb-1">
                                        <span>Materials ({materials.length} verified items)</span>
                                        <span>$450.00</span>
                                    </div>
                                    <div className="flex justify-between mb-1">
                                        <span>Labor ({laborRequired} people x {estimatedTime} hrs)</span>
                                        <span>$320.00</span>
                                    </div>
                                    <div className="border-t border-gray-300 dark:border-gray-600 mt-2 pt-2 flex justify-between font-bold">
                                        <span>Total</span>
                                        <span className="text-purple-600">$770.00</span>
                                    </div>
                                    <Button className="mt-6" onClick={async () => {
                                        try {
                                            setProcessing(true);
                                            
                                            // Create line items from verified materials and labor
                                            const materialLineItems = materials
                                                .filter(m => m.status === 'FM Verified')
                                                .map(m => ({
                                                    description: m.name,
                                                    quantity: m.quantity,
                                                    unit_price: 50, // Mock rate, should be dynamic
                                                }));

                                            const laborLineItems = [{
                                                description: `Labor (${estimatedTime} hours)`,
                                                quantity: estimatedTime,
                                                unit_price: 80, // Mock hourly rate
                                            }];

                                            const estimateData = {
                                                line_items: [...materialLineItems, ...laborLineItems],
                                                notes: 'Auto-generated from site visit'
                                            };

                                            const newEstimate = await fmApiService.createEstimate(Number(jobId), estimateData);
                                            
                                            // Generate magic link
                                            const magicLink = `${window.location.origin}/quote/${job.magic_token || 'mock-token-123'}`;
                                            navigator.clipboard.writeText(magicLink);
                                            
                                            alert(`Estimate #${newEstimate.id} Created & Magic Link Copied!\n\n${magicLink}\n\nShare this with the customer to approve.`);
                                        } catch (err) {
                                            alert('Failed to create estimate');
                                        } finally {
                                            setProcessing(false);
                                        }
                                    }} disabled={processing}>
                                        <div className="flex items-center">
                                            {processing ? (
                                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                            ) : (
                                                <Send className="w-4 h-4 mr-2" />
                                            )}
                                            Generate Quote & Copy Link
                                        </div>
                                    </Button>
                                    <p className="text-xs text-gray-400 mt-2">
                                        Generates a secure magic link for customer approval.
                                    </p>
                                </div>
                            </div>
                        </Card>
                    )}

                    {/* STEP 3: SIGN OFF */}
                    {activeTab === 'signature' && (
                        <Card>
                            <div className="text-center py-12">
                                <div className="max-w-md mx-auto">
                                    <h3 className="text-xl font-bold mb-4">Customer Authorization</h3>
                                    <p className="text-gray-600 mb-8">
                                        By signing, the customer agrees to the scope of work and estimated pricing verified in the previous steps.
                                    </p>

                                    <div
                                        onClick={() => setSignatureSaved(!signatureSaved)}
                                        className={`h-40 border-2 rounded-xl flex items-center justify-center cursor-pointer transition-all ${signatureSaved
                                            ? 'border-green-500 bg-green-50 text-green-600'
                                            : 'border-dashed border-gray-300 hover:border-purple-400 hover:bg-gray-50'
                                            }`}
                                    >
                                        {signatureSaved ? (
                                            <div className="text-center">
                                                <CheckCircle className="w-10 h-10 mx-auto mb-2" />
                                                <span className="font-bold text-lg">Signed by {job.customer_name}</span>
                                            </div>
                                        ) : (
                                            <div className="text-center text-gray-400">
                                                <PenTool className="w-8 h-8 mx-auto mb-2" />
                                                <span>Tap to Sign (Mock)</span>
                                            </div>
                                        )}
                                    </div>
                                    <p className="text-xs text-gray-400 mt-2">I certify that I am the property owner or authorized agent.</p>
                                </div>
                            </div>
                        </Card>
                    )}
                </div>
            </div>

            {/* Bottom Action Bar */}
            <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 p-4 md:pl-72 z-40">
                <div className="max-w-5xl mx-auto flex items-center justify-between">
                    <div className="hidden sm:block text-sm text-gray-500">
                        {isVisitComplete ? (
                            <span className="text-green-600 font-medium flex items-center">
                                <CheckCircle className="w-4 h-4 mr-1" /> All mandatory steps complete
                            </span>
                        ) : (
                            <span>Complete all {progress.total} steps to submit</span>
                        )}
                    </div>
                    <div className="flex space-x-3 w-full sm:w-auto">
                        <Button
                            variant="outline"
                            className="flex-1 sm:flex-none"
                            onClick={() => navigate('/fm/dashboard')}
                        >
                            Save Draft
                        </Button>
                        <Button
                            variant="primary"
                            className="flex-1 sm:flex-none"
                            disabled={!isVisitComplete || processing}
                            onClick={handleSubmitVisit}
                        >
                            {processing ? (
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                            ) : null}
                            Submit Visit
                            <Send className="w-4 h-4 ml-2" />
                        </Button>
                    </div>
                </div>
            </div>

            {/* AI Materials Modal */}
            {showMaterialModal && (
                <AIGeneratedMaterials
                    materials={materials}
                    onSave={handleMaterialsSave}
                    onCancel={() => setShowMaterialModal(false)}
                />
            )}
        </PortalLayout>
    );
}
