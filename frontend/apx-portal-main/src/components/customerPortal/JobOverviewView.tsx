import { ShieldCheck, CalendarClock } from 'lucide-react';
import type { CustomerJob } from '@/types/customerPortal';

interface JobOverviewViewProps {
    job: CustomerJob;
}

export default function JobOverviewView({ job }: JobOverviewViewProps) {
    return (
        <div className="p-8 lg:p-12 max-w-7xl mx-auto space-y-8 animate-enter">
            {/* Hero Status Section */}
            <div className="relative h-[400px] rounded-3xl overflow-hidden border border-white/10 shadow-2xl group">
                {/* Map Background */}
                <div className="absolute inset-0 map-bg transition-transform duration-1000 group-hover:scale-105" />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent" />

                {/* Floating Contractor Card */}
                <div className="absolute top-8 right-8 w-80 glass-panel rounded-2xl p-5 transform transition-transform hover:-translate-y-1">
                    <div className="flex items-start gap-4 mb-4">
                        <div className="relative">
                            <img
                                src={job.contractor.avatar}
                                alt={job.contractor.name}
                                className="w-14 h-14 rounded-xl object-cover border border-white/10"
                            />
                            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-emerald-500 border-2 border-slate-800 rounded-full" />
                        </div>
                        <div>
                            <h3 className="text-white font-semibold">{job.contractor.name}</h3>
                            <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">
                                {job.contractor.role}
                            </p>
                            <div className="flex items-center gap-1 text-amber-400 text-xs font-medium">
                                <span>★</span> {job.contractor.rating} ({job.contractor.jobsCount} Jobs)
                            </div>
                        </div>
                    </div>
                    <div className="flex gap-2">
                        <button className="flex-1 py-2 rounded-lg bg-white/5 text-xs font-medium text-white hover:bg-white/10 transition-colors border border-white/5">
                            View Profile
                        </button>
                        <button className="flex-1 py-2 rounded-lg bg-emerald-500 text-xs font-medium text-white hover:bg-emerald-400 transition-colors shadow-lg shadow-emerald-900/20">
                            Message
                        </button>
                    </div>
                </div>

                {/* Left Rail: Timeline Progress */}
                <div className="absolute bottom-8 left-8 flex items-end gap-12">
                    <div className="space-y-6 relative">
                        <div className="absolute left-[7px] top-2 bottom-2 w-px bg-white/10" />

                        {job.timelineSteps.map((step, index) => {
                            const isCompleted = step.status === 'completed';
                            const isActive = step.status === 'active';
                            return (
                                <div key={step.id} className="relative flex items-center gap-4">
                                    <div
                                        className={`w-3.5 h-3.5 rounded-full z-10 ${
                                            isCompleted
                                                ? 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]'
                                                : isActive
                                                  ? 'bg-slate-800 border border-emerald-500/50 animate-pulse'
                                                  : 'bg-slate-800 border border-white/20 opacity-40'
                                        }`}
                                    />
                                    <span
                                        className={`text-sm font-medium ${
                                            isActive
                                                ? 'text-emerald-400'
                                                : isCompleted
                                                  ? 'text-white'
                                                  : 'text-slate-400 opacity-40'
                                        }`}
                                    >
                                        {step.label}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>

            {/* Lower Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="glass-panel p-8 rounded-3xl relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-32 bg-emerald-500/5 rounded-full blur-3xl group-hover:bg-emerald-500/10 transition-colors" />
                    <div className="relative z-10">
                        <p className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">
                            Estimated Cost
                        </p>
                        <div className="text-4xl font-light text-white tracking-tight mb-1">
                            ${job.estimatedCost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </div>
                        <div className="flex items-center gap-2 mt-4 text-emerald-400 text-sm">
                            <ShieldCheck className="w-4 h-4" />
                            <span>Funds held in escrow</span>
                        </div>
                    </div>
                </div>

                <div className="glass-panel p-8 rounded-3xl relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-32 bg-indigo-500/5 rounded-full blur-3xl group-hover:bg-indigo-500/10 transition-colors" />
                    <div className="relative z-10">
                        <p className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">
                            Project Schedule
                        </p>
                        <div className="text-4xl font-light text-white tracking-tight mb-1">{job.schedule.duration}</div>
                        <div className="flex items-center gap-2 mt-4 text-indigo-400 text-sm">
                            <CalendarClock className="w-4 h-4" />
                            <span>Est. Completion: {job.schedule.completionDate}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

