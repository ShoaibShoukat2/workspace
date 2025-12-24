import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Badge, { getStatusBadgeVariant } from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import SupportWidget from '@/components/contractor/SupportWidget';
import {
    LayoutDashboard,
    ShieldCheck,
    Briefcase,
    Wallet as WalletIcon,
    CheckSquare,
    Upload,
    AlertCircle,
    Flag,
    Package
} from 'lucide-react';
import { jobs, checklistItems, updateChecklistItem, updateJobField, createDispute } from '@/data/mockData';

export default function ActiveJobView() {
    const { jobId } = useParams();
    const navigate = useNavigate();


    const [job, setJob] = useState(jobs.find(j => j.id === Number(jobId)));
    const [jobChecklist, setJobChecklist] = useState(
        checklistItems.filter(i => i.jobId === Number(jobId))
    );

    const navItems = [
        { label: 'Dashboard', path: '/contractor/dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
        { label: 'Job Board', path: '/contractor/jobs', icon: <Briefcase className="w-5 h-5" /> },
        { label: 'Compliance Hub', path: '/contractor/compliance', icon: <ShieldCheck className="w-5 h-5" /> },
        { label: 'Wallet', path: '/contractor/wallet', icon: <WalletIcon className="w-5 h-5" /> },
    ];

    if (!job) {
        return (
            <PortalLayout title="Job Not Found" navItems={navItems}>
                <Card>
                    <div className="text-center py-12">
                        <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
                        <h3 className="text-xl font-semibold text-white mb-2">Job Not Found</h3>
                        <p className="text-gray-400 mb-4">The job you're looking for doesn't exist.</p>
                        <Button onClick={() => navigate('/contractor/jobs')}>
                            Back to Job Board
                        </Button>
                    </div>
                </Card>
            </PortalLayout>
        );
    }

    const handleChecklistToggle = (itemId: string) => {
        updateChecklistItem(itemId, !jobChecklist.find(i => i.id === itemId)?.done);
        setJobChecklist(checklistItems.filter(i => i.jobId === Number(jobId)));
        setJob(jobs.find(j => j.id === Number(jobId)));
    };

    const handlePhotoUpload = (type: 'before' | 'after') => {
        const field = type === 'before' ? 'beforePhotos' : 'afterPhotos';
        const currentCount = job[field] || 0;
        updateJobField(job.id, field, currentCount + 1);
        setJob(jobs.find(j => j.id === Number(jobId)));
        alert(`${type === 'before' ? 'Before' : 'After'} photo uploaded (simulated)`);
    };

    const handleFlagConcern = () => {
        const description = prompt('Describe the concern:');
        if (description && description.trim()) {
            createDispute(job.id, 'contractor', 'Contractor flagged concern', description);
            alert('Concern flagged and sent to admin.');
        }
    };

    const handleMarkComplete = () => {
        updateJobField(job.id, 'status', 'Complete');
        setJob(jobs.find(j => j.id === Number(jobId)));
        alert('Job marked as complete! Admin will review for payout approval.');
        navigate('/contractor/jobs');
    };

    const canComplete =
        job.checklistCompleted &&
        (job.beforePhotos || 0) > 0 &&
        (job.afterPhotos || 0) > 0 &&
        (!job.materials || job.materials.every(m => m.deliveryStatus === 'Delivered' || m.deliveryStatus === 'Correct'));

    const hasMaterialIssues = job.materials?.some(m =>
        m.deliveryStatus === 'Missing Items' ||
        m.deliveryStatus === 'Damaged' ||
        m.deliveryStatus === 'Wrong Items'
    );

    return (
        <PortalLayout title={`Job: ${job.propertyAddress}`} navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                {/* Job Header */}
                <Card className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 border-purple-500/30">
                    <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                        <div>
                            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{job.propertyAddress}</h2>
                            <div className="flex flex-wrap items-center gap-3 text-sm text-gray-300">
                                <span>Customer: {job.customerName}</span>
                                <span>•</span>
                                <span>City: {job.city}</span>
                                <span>•</span>
                                <span>Trade: {job.trade}</span>
                            </div>
                            {job.gateCode && (
                                <div className="mt-3 inline-flex items-center space-x-2 bg-blue-500/20 border border-blue-500/30 rounded-lg px-4 py-2">
                                    <span className="text-sm text-blue-300">Gate Code:</span>
                                    <span className="font-mono text-lg font-bold text-blue-200">{job.gateCode}</span>
                                </div>
                            )}
                        </div>
                        <div className="flex flex-col items-end gap-2">
                            <Badge variant={getStatusBadgeVariant(job.status)} className="text-base px-4 py-2">
                                {job.status}
                            </Badge>
                            {job.isProject && <Badge variant="info">PROJECT</Badge>}
                        </div>
                    </div>
                </Card>

                {/* Important Notice for Materials */}
                <Card className="bg-yellow-50 dark:bg-yellow-500/10 border-yellow-200 dark:border-yellow-500/30">
                    <div className="flex items-start space-x-3">
                        <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-1" />
                        <div>
                            <h4 className="font-semibold text-yellow-800 dark:text-yellow-300">Material Policy Reminder</h4>
                            <p className="text-sm text-yellow-700 dark:text-yellow-200 mt-1">
                                <strong>DO NOT purchase materials for this job.</strong> All materials are supplied by the customer or handled separately.
                                You cannot upload material receipts. Use only the provided materials.
                            </p>
                        </div>
                    </div>
                </Card>

                {/* Scope of Work */}
                <div>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">Scope of Work</h3>
                    <Card hover={false}>
                        <p className="text-gray-300 leading-relaxed">
                            {job.trade === 'painting' ? 'Paint designated areas with provided materials. Ensure proper surface preparation and application of primer and finish coats.' :
                                job.trade === 'drywall' ? 'Patch and repair drywall as specified. Sand smooth and prepare for painting.' :
                                    'Complete work as specified in the job scope.'}
                        </p>
                    </Card>
                </div>

                {/* Materials Section */}
                {job.materials && job.materials.length > 0 && (
                    <div>
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3 flex items-center space-x-2">
                            <Package className="w-6 h-6 text-cyan-600 dark:text-cyan-400" />
                            <span>Materials (Read-Only)</span>
                        </h3>
                        <Card hover={false} className="bg-cyan-50 dark:bg-cyan-500/5 border-cyan-200 dark:border-cyan-500/20">
                            <div className="space-y-3">
                                <p className="text-sm text-cyan-800 dark:text-cyan-300 mb-3">
                                    Materials are verified and provided. You cannot edit, purchase, or upload receipts.
                                </p>
                                <div className="overflow-x-auto">
                                    <table className="w-full text-sm">
                                        <thead>
                                            <tr className="border-b border-white/10">
                                                <th className="text-left py-2 px-3 text-gray-400">Item</th>
                                                <th className="text-left py-2 px-3 text-gray-400">SKU</th>
                                                <th className="text-left py-2 px-3 text-gray-400">Qty</th>
                                                <th className="text-left py-2 px-3 text-gray-400">Supplier</th>
                                                <th className="text-left py-2 px-3 text-gray-400">Delivery Status</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {job.materials.map((material) => (
                                                <tr key={material.id} className="border-b border-gray-200 dark:border-white/5">
                                                    <td className="py-3 px-3 text-gray-900 dark:text-white">{material.name}</td>
                                                    <td className="py-3 px-3 text-gray-500 dark:text-gray-400 font-mono text-xs">{material.sku}</td>
                                                    <td className="py-3 px-3 text-gray-600 dark:text-gray-300">{material.quantity}</td>
                                                    <td className="py-3 px-3 text-gray-600 dark:text-gray-300">{material.supplier}</td>
                                                    <td className="py-3 px-3">
                                                        <Badge variant={getStatusBadgeVariant(material.deliveryStatus || 'default')}>
                                                            {material.deliveryStatus || 'N/A'}
                                                        </Badge>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                                {hasMaterialIssues && (
                                    <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mt-3">
                                        <div className="flex items-start space-x-2">
                                            <AlertCircle className="w-5 h-5 text-red-400 mt-0.5" />
                                            <div>
                                                <p className="text-sm font-semibold text-red-300">Material Delivery Issues Detected</p>
                                                <p className="text-xs text-red-200 mt-1">
                                                    You cannot mark this job complete until all material issues are resolved.
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </Card>
                    </div>
                )}

                {/* Checklist */}
                <div>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3 flex items-center space-x-2">
                        <CheckSquare className="w-6 h-6 text-purple-400" />
                        <span>Checklist</span>
                        <Badge variant={job.checklistCompleted ? 'success' : 'warning'}>
                            {jobChecklist.filter(i => i.done).length}/{jobChecklist.length} Complete
                        </Badge>
                    </h3>
                    <div className="grid gap-3">
                        {jobChecklist.map((item) => (
                            <Card key={item.id} hover={false} className="cursor-pointer" onClick={() => handleChecklistToggle(item.id)}>
                                <div className="flex items-center space-x-3">
                                    <input
                                        type="checkbox"
                                        checked={item.done}
                                        onChange={() => handleChecklistToggle(item.id)}
                                        className="w-5 h-5 rounded border-white/20 bg-white/5 text-purple-500 focus:ring-purple-400"
                                    />
                                    <span className={`text-gray-900 dark:text-white ${item.done ? 'line-through text-gray-400' : ''}`}>
                                        {item.label}
                                    </span>
                                </div>
                            </Card>
                        ))}
                    </div>
                </div>

                {/* Photo Uploads */}
                <div>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3 flex items-center space-x-2">
                        <Upload className="w-6 h-6 text-green-400" />
                        <span>Photo Documentation</span>
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Before Photos */}
                        <Card hover={false}>
                            <div className="text-center">
                                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Before Photos</h4>
                                <p className="text-3xl font-bold text-purple-400 mb-3">{job.beforePhotos || 0}</p>
                                <Button variant={job.beforePhotos ? 'outline' : 'primary'} size="sm" onClick={() => handlePhotoUpload('before')} className="w-full">
                                    <Upload className="w-4 h-4 mr-2" />
                                    {job.beforePhotos ? 'Add More' : 'Upload Before Photos'}
                                </Button>
                            </div>
                        </Card>

                        {/* After Photos */}
                        <Card hover={false}>
                            <div className="text-center">
                                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">After Photos</h4>
                                <p className="text-3xl font-bold text-green-400 mb-3">{job.afterPhotos || 0}</p>
                                <Button variant={job.afterPhotos ? 'outline' : 'primary'} size="sm" onClick={() => handlePhotoUpload('after')} className="w-full">
                                    <Upload className="w-4 h-4 mr-2" />
                                    {job.afterPhotos ? 'Add More' : 'Upload After Photos'}
                                </Button>
                            </div>
                        </Card>
                    </div>
                </div>

                {/* Actions */}
                <div className="flex flex-col sm:flex-row gap-4">
                    <Button
                        variant="danger"
                        onClick={handleFlagConcern}
                        className="flex-1"
                    >
                        <Flag className="w-4 h-4 mr-2" />
                        Flag Concern
                    </Button>
                    <Button
                        variant="primary"
                        onClick={handleMarkComplete}
                        disabled={!canComplete}
                        className="flex-1"
                    >
                        {canComplete ? 'Mark Job Complete ✓' : 'Complete Requirements First'}
                    </Button>
                </div>

                {/* Completion Requirements */}
                {!canComplete && (
                    <Card className="bg-blue-500/10 border-blue-500/30">
                        <h4 className="font-semibold text-blue-300 mb-2">Requirements to Complete Job:</h4>
                        <ul className="space-y-2 text-sm">
                            <li className={`flex items-center space-x-2 ${job.checklistCompleted ? 'text-green-400' : 'text-gray-300'}`}>
                                {job.checklistCompleted ? '✓' : '○'} All checklist items completed
                            </li>
                            <li className={`flex items-center space-x-2 ${(job.beforePhotos || 0) > 0 ? 'text-green-400' : 'text-gray-300'}`}>
                                {(job.beforePhotos || 0) > 0 ? '✓' : '○'} Before photos uploaded
                            </li>
                            <li className={`flex items-center space-x-2 ${(job.afterPhotos || 0) > 0 ? 'text-green-400' : 'text-gray-300'}`}>
                                {(job.afterPhotos || 0) > 0 ? '✓' : '○'} After photos uploaded
                            </li>
                            {job.materials && job.materials.length > 0 && (
                                <li className={`flex items-center space-x-2 ${!hasMaterialIssues ? 'text-green-400' : 'text-red-400'}`}>
                                    {!hasMaterialIssues ? '✓' : '✗'} No material delivery issues
                                </li>
                            )}
                        </ul>
                    </Card>
                )}
                <SupportWidget />
            </div>
        </PortalLayout>
    );
}
