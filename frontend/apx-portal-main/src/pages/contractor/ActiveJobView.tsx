import { useState, useEffect } from 'react';
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
import { contractorApiService } from '@/lib/contractorApi';

export default function ActiveJobView() {
    const { jobId } = useParams();
    const navigate = useNavigate();

    const [job, setJob] = useState<any>(null);
    const [jobChecklist, setJobChecklist] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [processing, setProcessing] = useState(false);

    useEffect(() => {
        const fetchJobDetails = async () => {
            if (!jobId) return;
            
            try {
                setLoading(true);
                setError(null);
                const jobData = await contractorApiService.getJobDetail(Number(jobId));
                setJob(jobData);
                setJobChecklist(jobData.checklist || []);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load job details');
            } finally {
                setLoading(false);
            }
        };

        fetchJobDetails();
    }, [jobId]);

    const navItems = [
        { label: 'Dashboard', path: '/contractor/dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
        { label: 'Job Board', path: '/contractor/jobs', icon: <Briefcase className="w-5 h-5" /> },
        { label: 'Compliance Hub', path: '/contractor/compliance', icon: <ShieldCheck className="w-5 h-5" /> },
        { label: 'Wallet', path: '/contractor/wallet', icon: <WalletIcon className="w-5 h-5" /> },
    ];

    if (loading) {
        return (
            <PortalLayout title="Loading Job..." navItems={navItems}>
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
                <Card>
                    <div className="text-center py-12">
                        <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
                        <h3 className="text-xl font-semibold text-white mb-2">Job Not Found</h3>
                        <p className="text-gray-400 mb-4">{error || "The job you're looking for doesn't exist."}</p>
                        <Button onClick={() => navigate('/contractor/jobs')}>
                            Back to Job Board
                        </Button>
                    </div>
                </Card>
            </PortalLayout>
        );
    }

    const handleChecklistToggle = async (itemId: string) => {
        try {
            const item = jobChecklist.find(i => i.id === itemId);
            if (!item) return;

            await contractorApiService.updateChecklist(job.id, item.id, { 
                completed: !item.completed 
            });
            
            // Refresh job data
            const updatedJob = await contractorApiService.getJobDetail(Number(jobId));
            setJob(updatedJob);
            setJobChecklist(updatedJob.checklist || []);
        } catch (err) {
            alert('Failed to update checklist item');
        }
    };

    const handlePhotoUpload = async (type: 'before' | 'after') => {
        try {
            // Create a mock file input for demo
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
                formData.append('job_id', job.id.toString());
                formData.append('photo_type', type);

                try {
                    setProcessing(true);
                    // Note: This would use a specific photo upload endpoint
                    // await contractorApiService.uploadStepMedia(stepId, formData);
                    alert(`${type === 'before' ? 'Before' : 'After'} photos uploaded successfully!`);
                    
                    // Refresh job data
                    const updatedJob = await contractorApiService.getJobDetail(Number(jobId));
                    setJob(updatedJob);
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

    const handleFlagConcern = async () => {
        const description = prompt('Describe the concern:');
        if (description && description.trim()) {
            try {
                // Note: This would need a flag concern/create dispute API endpoint
                alert('Concern flagged and sent to admin.');
            } catch (err) {
                alert('Failed to flag concern');
            }
        }
    };

    const handleMarkComplete = async () => {
        try {
            setProcessing(true);
            await contractorApiService.submitJobCompletion(job.id, {
                completion_notes: 'Job completed successfully',
                checklist_completed: true,
                photos_uploaded: true
            });
            
            alert('Job marked as complete! Admin will review for payout approval.');
            navigate('/contractor/jobs');
        } catch (err) {
            alert('Failed to mark job as complete');
        } finally {
            setProcessing(false);
        }
    };

    const canComplete =
        job.checklist_completed &&
        (job.before_photos_count || 0) > 0 &&
        (job.after_photos_count || 0) > 0 &&
        (!job.materials || job.materials.every((m: any) => m.delivery_status === 'Delivered' || m.delivery_status === 'Correct'));

    const hasMaterialIssues = job.materials?.some((m: any) =>
        m.delivery_status === 'Missing Items' ||
        m.delivery_status === 'Damaged' ||
        m.delivery_status === 'Wrong Items'
    );

    return (
        <PortalLayout title={`Job: ${job.address || job.location}`} navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                {/* Job Header */}
                <Card className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 border-purple-500/30">
                    <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                        <div>
                            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{job.address || job.location}</h2>
                            <div className="flex flex-wrap items-center gap-3 text-sm text-gray-300">
                                <span>Customer: {job.customer_name}</span>
                                <span>•</span>
                                <span>Title: {job.title}</span>
                                {job.estimated_hours && (
                                    <>
                                        <span>•</span>
                                        <span>Est. Hours: {job.estimated_hours}</span>
                                    </>
                                )}
                            </div>
                            {job.gate_code && (
                                <div className="mt-3 inline-flex items-center space-x-2 bg-blue-500/20 border border-blue-500/30 rounded-lg px-4 py-2">
                                    <span className="text-sm text-blue-300">Gate Code:</span>
                                    <span className="font-mono text-lg font-bold text-blue-200">{job.gate_code}</span>
                                </div>
                            )}
                        </div>
                        <div className="flex flex-col items-end gap-2">
                            <Badge variant={getStatusBadgeVariant(job.status)} className="text-base px-4 py-2">
                                {job.status}
                            </Badge>
                            {job.is_project && <Badge variant="info">PROJECT</Badge>}
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
                            {job.description || job.scope_of_work || 'Complete work as specified in the job requirements.'}
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
                                            {job.materials.map((material: any) => (
                                                <tr key={material.id} className="border-b border-gray-200 dark:border-white/5">
                                                    <td className="py-3 px-3 text-gray-900 dark:text-white">{material.name}</td>
                                                    <td className="py-3 px-3 text-gray-500 dark:text-gray-400 font-mono text-xs">{material.sku}</td>
                                                    <td className="py-3 px-3 text-gray-600 dark:text-gray-300">{material.quantity}</td>
                                                    <td className="py-3 px-3 text-gray-600 dark:text-gray-300">{material.supplier}</td>
                                                    <td className="py-3 px-3">
                                                        <Badge variant={getStatusBadgeVariant(material.delivery_status || 'default')}>
                                                            {material.delivery_status || 'N/A'}
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
                        <Badge variant={job.checklist_completed ? 'success' : 'warning'}>
                            {jobChecklist.filter((i: any) => i.completed).length}/{jobChecklist.length} Complete
                        </Badge>
                    </h3>
                    <div className="grid gap-3">
                        {jobChecklist.map((item: any) => (
                            <Card key={item.id} hover={false} className="cursor-pointer" onClick={() => handleChecklistToggle(item.id)}>
                                <div className="flex items-center space-x-3">
                                    <input
                                        type="checkbox"
                                        checked={item.completed}
                                        onChange={() => handleChecklistToggle(item.id)}
                                        className="w-5 h-5 rounded border-white/20 bg-white/5 text-purple-500 focus:ring-purple-400"
                                    />
                                    <span className={`text-gray-900 dark:text-white ${item.completed ? 'line-through text-gray-400' : ''}`}>
                                        {item.description || item.label}
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
                                <p className="text-3xl font-bold text-purple-400 mb-3">{job.before_photos_count || 0}</p>
                                <Button 
                                    variant={job.before_photos_count ? 'outline' : 'primary'} 
                                    size="sm" 
                                    onClick={() => handlePhotoUpload('before')} 
                                    className="w-full"
                                    disabled={processing}
                                >
                                    <Upload className="w-4 h-4 mr-2" />
                                    {job.before_photos_count ? 'Add More' : 'Upload Before Photos'}
                                </Button>
                            </div>
                        </Card>

                        {/* After Photos */}
                        <Card hover={false}>
                            <div className="text-center">
                                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">After Photos</h4>
                                <p className="text-3xl font-bold text-green-400 mb-3">{job.after_photos_count || 0}</p>
                                <Button 
                                    variant={job.after_photos_count ? 'outline' : 'primary'} 
                                    size="sm" 
                                    onClick={() => handlePhotoUpload('after')} 
                                    className="w-full"
                                    disabled={processing}
                                >
                                    <Upload className="w-4 h-4 mr-2" />
                                    {job.after_photos_count ? 'Add More' : 'Upload After Photos'}
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
                        disabled={!canComplete || processing}
                        className="flex-1"
                    >
                        {processing ? (
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        ) : null}
                        {canComplete ? 'Mark Job Complete ✓' : 'Complete Requirements First'}
                    </Button>
                </div>

                {/* Completion Requirements */}
                {!canComplete && (
                    <Card className="bg-blue-500/10 border-blue-500/30">
                        <h4 className="font-semibold text-blue-300 mb-2">Requirements to Complete Job:</h4>
                        <ul className="space-y-2 text-sm">
                            <li className={`flex items-center space-x-2 ${job.checklist_completed ? 'text-green-400' : 'text-gray-300'}`}>
                                {job.checklist_completed ? '✓' : '○'} All checklist items completed
                            </li>
                            <li className={`flex items-center space-x-2 ${(job.before_photos_count || 0) > 0 ? 'text-green-400' : 'text-gray-300'}`}>
                                {(job.before_photos_count || 0) > 0 ? '✓' : '○'} Before photos uploaded
                            </li>
                            <li className={`flex items-center space-x-2 ${(job.after_photos_count || 0) > 0 ? 'text-green-400' : 'text-gray-300'}`}>
                                {(job.after_photos_count || 0) > 0 ? '✓' : '○'} After photos uploaded
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
