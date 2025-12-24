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
import { getJobById, updateJobField, createEstimate } from '@/data/mockData';
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
    const [job, setJob] = useState<any>(undefined);
    const [activeTab, setActiveTab] = useState<TabType>('visit');
    const [signatureSaved, setSignatureSaved] = useState(false);

    // Visit Form State
    const [measurements, setMeasurements] = useState({ display: '', verified: false });
    const [scopeConfirmed, setScopeConfirmed] = useState(false);
    const [beforePhotosUploaded, setBeforePhotosUploaded] = useState(false);
    const [toolsRequired, setToolsRequired] = useState<string[]>([]);
    const [laborRequired, setLaborRequired] = useState(1);
    const [estimatedTime, setEstimatedTime] = useState(4);
    const [safetyConcerns, setSafetyConcerns] = useState('');
    const [materials, setMaterials] = useState<Material[]>(MOCK_AI_MATERIALS);
    const [showMaterialModal, setShowMaterialModal] = useState(false);

    // Quote State


    useEffect(() => {
        if (jobId) {
            const j = getJobById(Number(jobId));
            if (j) {
                setJob(j);
                if (j.materials && j.materials.length > 0) {
                    setMaterials(j.materials);
                }
            }
            setLoading(false);
        }
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

    const handleMaterialsSave = (updatedMaterials: Material[]) => {
        const verifiedMaterials = updatedMaterials.map(m => ({ ...m, status: 'FM Verified' as const }));
        setMaterials(verifiedMaterials);
        setShowMaterialModal(false);
        // Persist to mock data (in memory)
        updateJobField(Number(jobId), 'materials', verifiedMaterials);
        updateJobField(Number(jobId), 'materialStatus', 'FM Verified');
    };

    const handleSubmitVisit = () => {
        if (!isVisitComplete) return;

        updateJobField(Number(jobId), 'status', 'InProgress');
        updateJobField(Number(jobId), 'visitStatus', 'Completed');

        // Also save mandatory fields to job object for peristence
        updateJobField(Number(jobId), 'measurements', measurements);
        updateJobField(Number(jobId), 'toolsRequired', toolsRequired);
        updateJobField(Number(jobId), 'laborRequired', laborRequired);
        updateJobField(Number(jobId), 'estimatedTime', estimatedTime);
        updateJobField(Number(jobId), 'safetyConcerns', safetyConcerns);
        updateJobField(Number(jobId), 'scopeConfirmed', scopeConfirmed);
        updateJobField(Number(jobId), 'beforePhotosUploaded', beforePhotosUploaded);

        alert('Site visit submitted successfully through the new secure flow.');
        navigate('/fm/dashboard');
    };

    if (loading || !job) return <PortalLayout title="Loading..." navItems={[]}><div className="p-8">Loading...</div></PortalLayout>;

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
                            <h2 className="text-2xl font-bold">{job.customerName}'s Property</h2>
                            <p className="text-gray-400">{job.type} Job • {job.trade}</p>
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
                                    <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-xl p-6 text-center hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer transition-colors" onClick={() => setBeforePhotosUploaded(true)}>
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
                                    <Button className="mt-6" onClick={() => {
                                        // 1. Create/Update Estimate in the system
                                        // Create line items from verified materials and labor
                                        const materialLineItems = materials
                                            .filter(m => m.status === 'FM Verified')
                                            .map(m => ({
                                                description: m.name,
                                                category: 'Material',
                                                quantity: m.quantity,
                                                rate: 50, // Mock rate, should be dynamic
                                                total: m.quantity * 50
                                            }));

                                        const laborLineItems = [{
                                            description: `Labor (${estimatedTime} hours)`,
                                            category: 'Labor',
                                            quantity: estimatedTime,
                                            rate: 80, // Mock hourly rate
                                            total: estimatedTime * 80
                                        }];

                                        const newEstimate = createEstimate(job.id, [...materialLineItems, ...laborLineItems]);

                                        // 2. Generate Link
                                        const magicLink = `${window.location.origin}/quote/${job.magicToken || 'mock-token-123'}`;
                                        navigator.clipboard.writeText(magicLink);
                                        alert(`Estimate #${newEstimate.id} Created & Magic Link Copied!\n\n${magicLink}\n\nShare this with the customer to approve.`);
                                    }}>
                                        <div className="flex items-center">
                                            <Send className="w-4 h-4 mr-2" />
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
                                                <span className="font-bold text-lg">Signed by {job.customerName}</span>
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
                            disabled={!isVisitComplete}
                            onClick={handleSubmitVisit}
                        >
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
