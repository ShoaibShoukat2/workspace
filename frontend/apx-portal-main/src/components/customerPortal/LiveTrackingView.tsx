import { Hammer, Check, Loader, Circle, ChevronsLeftRight } from 'lucide-react';
import type { CustomerJob } from '@/types/customerPortal';

interface LiveTrackingViewProps {
    job: CustomerJob;
}

export default function LiveTrackingView({ job }: LiveTrackingViewProps) {
    const activePhase = job.progressPhases.find((p) => p.status === 'active');
    const progressPercent = 75; // This could be calculated from job data

    return (
        <div className="w-full h-full flex flex-col animate-enter bg-slate-950">
            {/* Map Hero Half */}
            <div className="h-2/5 relative w-full overflow-hidden border-b border-white/5 group">
                <div className="absolute inset-0 map-bg group-hover:scale-105 transition-transform duration-[2s]" />
                <div className="absolute inset-0 bg-gradient-to-b from-slate-950/10 via-slate-950/20 to-slate-950" />

                {/* Route Line SVG Animation */}
                <svg
                    className="absolute inset-0 w-full h-full pointer-events-none"
                    style={{ filter: 'drop-shadow(0 0 8px rgba(16, 185, 129, 0.4))' }}
                >
                    <path
                        d="M -100 200 Q 300 300 600 200 T 1400 150"
                        fill="none"
                        stroke="#10b981"
                        strokeWidth="2"
                        strokeDasharray="8 8"
                        className="animate-dash opacity-60"
                    />
                    <circle cx="600" cy="200" r="4" fill="#fff" className="pulse-marker" />
                </svg>

                {/* Live Status Card */}
                <div className="absolute bottom-8 left-8 glass-panel pl-6 pr-8 py-5 rounded-2xl flex items-center gap-6 border-l-4 border-l-emerald-500">
                    <div className="relative w-14 h-14">
                        <svg className="w-full h-full transform -rotate-90">
                            <circle cx="28" cy="28" r="22" stroke="#1e293b" strokeWidth="3" fill="none" />
                            <circle
                                cx="28"
                                cy="28"
                                r="22"
                                stroke="#10b981"
                                strokeWidth="3"
                                fill="none"
                                strokeDasharray="138"
                                strokeDashoffset={138 - (progressPercent / 100) * 138}
                                strokeLinecap="round"
                            />
                        </svg>
                        <span className="absolute inset-0 flex items-center justify-center text-xs font-bold text-white">
                            {progressPercent}%
                        </span>
                    </div>
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                            <span className="text-[10px] text-emerald-400 font-bold uppercase tracking-widest">
                                Live Status
                            </span>
                        </div>
                        <div className="text-xl text-white font-medium tracking-tight">
                            {activePhase?.title || 'Tiling Master Shower'}
                        </div>
                        <div className="text-xs text-slate-500 mt-1">Updated 24m ago by {job.contractor.name}</div>
                    </div>
                </div>
            </div>

            {/* Journey & Content Section */}
            <div className="flex-1 overflow-hidden flex flex-col lg:flex-row">
                {/* Timeline Left */}
                <div className="w-full lg:w-1/2 p-8 lg:p-12 overflow-y-auto space-y-10 relative bg-slate-950/50">
                    {/* Timeline Horizontal Flow Line */}
                    <div className="absolute left-[39px] top-12 bottom-12 w-0.5 bg-gradient-to-b from-emerald-500 via-emerald-500/50 to-slate-800" />

                    {job.progressPhases.map((phase, index) => {
                        const isCompleted = phase.status === 'completed';
                        const isActive = phase.status === 'active';
                        const isPending = phase.status === 'pending';

                        return (
                            <div
                                key={phase.id}
                                className={`relative flex gap-6 ${isPending ? 'opacity-40' : isCompleted ? 'opacity-60 hover:opacity-100' : ''} transition-opacity`}
                            >
                                {isActive ? (
                                    <div className="w-12 h-12 rounded-full bg-emerald-500/10 border border-emerald-500 flex items-center justify-center text-emerald-400 z-10 shrink-0 shadow-[0_0_20px_rgba(16,185,129,0.3)] pulse-marker">
                                        <Hammer className="w-5 h-5" />
                                    </div>
                                ) : (
                                    <div
                                        className={`w-6 h-6 rounded-full z-10 shrink-0 mt-1 ml-[11px] ${
                                            isCompleted
                                                ? 'bg-slate-950 border-2 border-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.4)]'
                                                : 'bg-slate-900 border border-slate-700'
                                        } flex items-center justify-center`}
                                    >
                                        {isCompleted && <div className="w-2 h-2 rounded-full bg-emerald-500" />}
                                    </div>
                                )}
                                <div className="flex-1 pt-1">
                                    <div className="flex justify-between items-start mb-2">
                                        <h4
                                            className={`font-medium tracking-tight ${
                                                isActive ? 'text-xl text-white' : 'text-white'
                                            }`}
                                        >
                                            {phase.title}
                                        </h4>
                                        {isActive && phase.dayProgress && (
                                            <span className="text-xs text-emerald-400 font-mono">
                                                {phase.dayProgress}
                                            </span>
                                        )}
                                        {isCompleted && (
                                            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                                                Completed
                                            </span>
                                        )}
                                    </div>

                                    {phase.contractorNote && (
                                        <div className="glass-panel p-4 rounded-xl border-l-2 border-l-emerald-500 bg-white/[0.02] mt-4 mb-4">
                                            <div className="flex items-center gap-3 mb-2">
                                                <img
                                                    src={phase.contractorNote.avatar}
                                                    alt={phase.contractorNote.author}
                                                    className="w-8 h-8 rounded-full border border-white/10"
                                                />
                                                <span className="text-xs text-slate-400 font-medium">
                                                    {phase.contractorNote.author} • Lead Contractor
                                                </span>
                                            </div>
                                            <p className="text-sm text-slate-300 italic">
                                                {phase.contractorNote.text}
                                            </p>
                                        </div>
                                    )}

                                    {phase.tasks && phase.tasks.length > 0 && (
                                        <div className="flex flex-wrap gap-2">
                                            {phase.tasks.map((task) => (
                                                <span
                                                    key={task.id}
                                                    className="px-3 py-1 rounded-md bg-white/5 border border-white/10 text-[10px] text-slate-300 font-medium uppercase tracking-wider flex items-center gap-1.5"
                                                >
                                                    {task.status === 'completed' && (
                                                        <Check className="w-3 h-3 text-emerald-500" />
                                                    )}
                                                    {task.status === 'in-progress' && (
                                                        <Loader className="w-3 h-3 text-amber-400 animate-spin" />
                                                    )}
                                                    {task.status === 'pending' && (
                                                        <Circle className="w-3 h-3 opacity-50" />
                                                    )}
                                                    {task.label}
                                                </span>
                                            ))}
                                        </div>
                                    )}

                                    {isPending && <p className="text-sm text-slate-500">Scheduled for {job.schedule.completionDate}</p>}
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Visual Right: Before/After Slider */}
                <div className="w-full lg:w-1/2 bg-black relative overflow-hidden group">
                    <div
                        className="absolute inset-0 bg-cover bg-center opacity-40 blur-sm scale-110"
                        style={{
                            backgroundImage: `url('https://images.unsplash.com/photo-1620626011761-996317b8d101?q=80&w=1600')`,
                        }}
                    />

                    <div className="absolute inset-0 flex items-center justify-center p-8">
                        <div className="relative w-full max-w-md aspect-[4/5] rounded-2xl overflow-hidden shadow-2xl border border-white/10">
                            {/* Before Image */}
                            {job.beforeImage && (
                                <img
                                    src={job.beforeImage}
                                    alt="Before"
                                    className="absolute inset-0 w-full h-full object-cover grayscale brightness-75"
                                />
                            )}
                            <div className="absolute top-4 left-4 bg-black/60 backdrop-blur text-white text-[10px] font-bold uppercase px-3 py-1 rounded border border-white/10">
                                Before
                            </div>

                            {/* After Image (Clipped) */}
                            {job.afterImage && (
                                <div className="absolute inset-0 w-[60%] overflow-hidden border-r border-white/80 shadow-[10px_0_50px_rgba(0,0,0,0.8)]">
                                    <img
                                        src={job.afterImage}
                                        alt="After"
                                        className="absolute inset-0 w-[100vw] max-w-md aspect-[4/5] h-full object-cover"
                                    />
                                    <div className="absolute top-4 right-4 bg-emerald-600/90 backdrop-blur text-white text-[10px] font-bold uppercase px-3 py-1 rounded shadow-lg">
                                        Current Progress
                                    </div>
                                </div>
                            )}

                            {/* Slider Handle Visual */}
                            <div className="absolute inset-y-0 left-[60%] w-0.5 bg-white shadow-[0_0_15px_rgba(255,255,255,0.8)] z-20 cursor-ew-resize">
                                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-lg">
                                    <ChevronsLeftRight className="w-4 h-4 text-slate-900" />
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="absolute bottom-8 inset-x-0 text-center">
                        <p className="text-xs text-slate-400 uppercase tracking-[0.2em]">Interactive Visualizer</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

