import { Home, Briefcase, FileCheck, Package, Map, CheckCircle2 } from 'lucide-react';
import type { WorkflowStep } from '@/types/customerPortal';

interface CustomerSidebarProps {
    currentStep: WorkflowStep;
    onStepChange: (step: WorkflowStep) => void;
    customerName?: string;
    customerAvatar?: string;
    hasSelectedJob?: boolean; // Whether a job is currently selected
}

export default function CustomerSidebar({
    currentStep,
    onStepChange,
    customerName = 'Sarah Jenkins',
    customerAvatar = 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=100&h=100',
    hasSelectedJob = false,
}: CustomerSidebarProps) {
    // Always show Job Management
    const jobManagementStep = { id: 'job-management' as WorkflowStep, label: 'Job Management', icon: <Briefcase className="w-5 h-5" /> };
    
    // Only show workflow steps when a job is selected
    const workflowSteps: Array<{ id: WorkflowStep; label: string; icon: React.ReactNode }> = [
        { id: 'overview', label: 'Job Overview', icon: <Briefcase className="w-5 h-5" /> },
        { id: 'quote', label: 'Quote Approval', icon: <FileCheck className="w-5 h-5" /> },
        { id: 'materials', label: 'Material Sourcing', icon: <Package className="w-5 h-5" /> },
        { id: 'progress', label: 'Live Tracking', icon: <Map className="w-5 h-5" /> },
        { id: 'completion', label: 'Final Review', icon: <CheckCircle2 className="w-5 h-5" /> },
    ];

    // Combine steps: always show Job Management, show workflow steps only if job is selected
    const steps = hasSelectedJob 
        ? [jobManagementStep, ...workflowSteps]
        : [jobManagementStep];

    return (
        <aside className="w-20 lg:w-72 border-r border-white/5 flex flex-col bg-slate-950 z-20 shrink-0">
            <div className="h-24 flex items-center justify-center lg:justify-start lg:px-8 border-b border-white/5">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
                        <Home className="text-white w-4 h-4 stroke-[2.5]" />
                    </div>
                    <span className="hidden lg:block text-lg font-bold tracking-tight text-white">Apex</span>
                </div>
            </div>

            {/* Workflow Steps Navigation */}
            <nav className="flex-1 px-4 py-8 space-y-2">
                {hasSelectedJob && (
                    <div className="hidden lg:block px-4 mb-4 text-[10px] font-semibold text-slate-500 uppercase tracking-widest">
                        Renovation Workflow
                    </div>
                )}
                {!hasSelectedJob && (
                    <div className="hidden lg:block px-4 mb-4 text-[10px] font-semibold text-slate-500 uppercase tracking-widest">
                        Dashboard
                    </div>
                )}

                {steps.map((step) => {
                    const isActive = currentStep === step.id;
                    return (
                        <button
                            key={step.id}
                            onClick={() => onStepChange(step.id)}
                            className={`w-full flex items-center gap-4 px-4 py-3.5 rounded-xl text-left transition-all ${
                                isActive
                                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                    : 'text-slate-400 hover:text-white hover:bg-white/5 border border-transparent'
                            } group`}
                        >
                            {step.icon}
                            <span className="hidden lg:block font-medium text-sm">{step.label}</span>
                            {isActive && (
                                <div className="hidden lg:block ml-auto w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]" />
                            )}
                        </button>
                    );
                })}
            </nav>

            <div className="p-6 border-t border-white/5">
                <button className="flex items-center gap-3 w-full p-2 rounded-lg hover:bg-white/5 transition-colors">
                    <img
                        src={customerAvatar}
                        alt={customerName}
                        className="w-9 h-9 rounded-full border border-white/10"
                    />
                    <div className="hidden lg:block text-left">
                        <div className="text-sm font-medium text-white">{customerName}</div>
                        <div className="text-xs text-slate-500">Property Owner</div>
                    </div>
                </button>
            </div>
        </aside>
    );
}

