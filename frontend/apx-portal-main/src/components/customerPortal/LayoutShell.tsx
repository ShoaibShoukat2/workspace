import { useState } from 'react';
import CustomerSidebar from './CustomerSidebar';
import TopHeader from './TopHeader';
import JobOverviewView from './JobOverviewView';
import QuoteApprovalView from './QuoteApprovalView';
import MaterialSourcingView from './MaterialSourcingView';
import LiveTrackingView from './LiveTrackingView';
import CompletionView from './CompletionView';
import JobManagementView from './JobManagementView';
import { useJobs } from '@/context/JobsContext';
import { convertJobToCustomerPortal } from '@/utils/jobConverter';
import { mockCustomerJob } from '@/data/customerPortalMockData';
import type { CustomerJob, WorkflowStep } from '@/types/customerPortal';

interface LayoutShellProps {
    job?: CustomerJob;
    customerName?: string;
    customerAvatar?: string;
}

export default function LayoutShell({ job: initialJob, customerName, customerAvatar }: LayoutShellProps) {
    const { getJobById } = useJobs();
    const [currentStep, setCurrentStep] = useState<WorkflowStep>('job-management');
    const [selectedJob, setSelectedJob] = useState<CustomerJob | null>(initialJob || null);

    const handleStepChange = (step: WorkflowStep) => {
        // If clicking on job-management, deselect the job and go back to job management
        if (step === 'job-management') {
            setSelectedJob(null);
            setCurrentStep('job-management');
        } else {
            // For other steps, ensure a job is selected
            if (!selectedJob && step !== 'job-management') {
                // Don't allow navigation to workflow steps without a selected job
                return;
            }
            setCurrentStep(step);
        }
    };

    const handleJobSelect = (jobId: string) => {
        // Get real job data from JobsContext
        const realJob = getJobById(jobId);
        if (realJob) {
            // Convert to CustomerPortal format
            const convertedJob = convertJobToCustomerPortal(realJob);
            setSelectedJob(convertedJob);
            setCurrentStep('overview');
        } else {
            // Fallback to mock if job not found
            setSelectedJob(mockCustomerJob);
            setCurrentStep('overview');
        }
    };

    const handleQuoteApprove = () => {
        setCurrentStep('materials');
    };

    const handleMaterialSelfSourcing = () => {
        setCurrentStep('progress');
    };

    const renderCurrentView = () => {
        switch (currentStep) {
            case 'job-management':
                return <JobManagementView onJobSelect={handleJobSelect} />;
            case 'overview':
                if (!selectedJob) {
                    // If no job selected, go back to job management
                    setCurrentStep('job-management');
                    return <JobManagementView onJobSelect={handleJobSelect} />;
                }
                return <JobOverviewView job={selectedJob} />;
            case 'quote':
                if (!selectedJob) {
                    setCurrentStep('job-management');
                    return <JobManagementView onJobSelect={handleJobSelect} />;
                }
                return <QuoteApprovalView job={selectedJob} onApprove={handleQuoteApprove} />;
            case 'materials':
                if (!selectedJob) {
                    setCurrentStep('job-management');
                    return <JobManagementView onJobSelect={handleJobSelect} />;
                }
                return <MaterialSourcingView job={selectedJob} onSelfSourcing={handleMaterialSelfSourcing} />;
            case 'progress':
                if (!selectedJob) {
                    setCurrentStep('job-management');
                    return <JobManagementView onJobSelect={handleJobSelect} />;
                }
                return <LiveTrackingView job={selectedJob} />;
            case 'completion':
                if (!selectedJob) {
                    setCurrentStep('job-management');
                    return <JobManagementView onJobSelect={handleJobSelect} />;
                }
                return <CompletionView job={selectedJob} />;
            default:
                return <JobManagementView onJobSelect={handleJobSelect} />;
        }
    };

    // Show header only when a job is selected and not on job-management view
    const displayJob = selectedJob || initialJob;

    return (
        <div className="flex h-screen w-full relative">
            <CustomerSidebar
                currentStep={currentStep}
                onStepChange={handleStepChange}
                customerName={customerName}
                customerAvatar={customerAvatar}
                hasSelectedJob={!!selectedJob}
            />

            <main className="flex-1 flex flex-col h-screen overflow-hidden bg-slate-950 relative">
                {selectedJob && currentStep !== 'job-management' && (
                    <TopHeader 
                        jobTitle={selectedJob.title} 
                        jobId={selectedJob.id} 
                        address={selectedJob.address} 
                        isActive={selectedJob.status === 'active'} 
                    />
                )}

                <div className="flex-1 overflow-y-auto relative scroll-smooth bg-grid-pattern">
                    {renderCurrentView()}
                </div>
            </main>
        </div>
    );
}

