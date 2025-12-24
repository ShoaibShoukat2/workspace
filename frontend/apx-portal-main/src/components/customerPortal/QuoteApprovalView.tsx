import { Check } from 'lucide-react';
import type { CustomerJob } from '@/types/customerPortal';

interface QuoteApprovalViewProps {
    job: CustomerJob;
    onApprove?: () => void;
    onRequestChanges?: () => void;
}

export default function QuoteApprovalView({ job, onApprove, onRequestChanges }: QuoteApprovalViewProps) {
    const totalEstimate = job.scopeItems.reduce((sum, item) => sum + item.price, 0);

    return (
        <>
            <div className="p-8 lg:p-12 max-w-5xl mx-auto space-y-8 animate-enter pb-32">
                <div className="flex items-center justify-between">
                    <h2 className="text-3xl font-light text-white tracking-tight">Walkthrough Results</h2>
                    <span className="px-4 py-1.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 text-xs font-semibold uppercase tracking-wide">
                        Action Required
                    </span>
                </div>

                {/* Photo Gallery Strip */}
                {job.gallery && job.gallery.length > 0 && (
                    <div className="flex gap-4 overflow-x-auto pb-4 no-scrollbar snap-x">
                        {job.gallery.map((photo) => (
                            <div
                                key={photo.id}
                                className="min-w-[280px] h-48 rounded-2xl overflow-hidden relative border border-white/10 group snap-center"
                            >
                                <img
                                    src={photo.image}
                                    alt={photo.label}
                                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                                />
                                <div className="absolute bottom-0 inset-x-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
                                    <span className="text-xs font-medium text-white">{photo.label}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Measurements & Scope */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Measurements */}
                    {job.measurements && (
                        <div className="lg:col-span-1 glass-panel rounded-2xl p-6">
                            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-6">
                                Measurements
                            </h3>
                            <div className="space-y-4">
                                <div className="flex justify-between py-2 border-b border-white/5">
                                    <span className="text-slate-300">Total Area</span>
                                    <span className="text-white font-mono">{job.measurements.totalArea}</span>
                                </div>
                                <div className="flex justify-between py-2 border-b border-white/5">
                                    <span className="text-slate-300">Ceiling Height</span>
                                    <span className="text-white font-mono">{job.measurements.ceilingHeight}</span>
                                </div>
                                {job.measurements.linearCabinetry && (
                                    <div className="flex justify-between py-2 border-b border-white/5">
                                        <span className="text-slate-300">Linear Cabinetry</span>
                                        <span className="text-white font-mono">
                                            {job.measurements.linearCabinetry}
                                        </span>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Scope List */}
                    <div className="lg:col-span-2 glass-panel rounded-2xl p-6">
                        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-6">
                            Scope of Work
                        </h3>
                        <div className="space-y-3">
                            {job.scopeItems.map((item) => (
                                <div
                                    key={item.id}
                                    className="flex items-start gap-4 p-4 rounded-xl bg-white/5 border border-white/5"
                                >
                                    <div className="w-5 h-5 rounded-full bg-emerald-500/20 flex items-center justify-center mt-0.5 text-emerald-400">
                                        <Check className="w-3 h-3" />
                                    </div>
                                    <div className="flex-1">
                                        <h4 className="text-white font-medium text-sm">{item.title}</h4>
                                        <p className="text-slate-400 text-xs mt-1">{item.description}</p>
                                    </div>
                                    <span className="text-sm text-slate-300 font-medium">
                                        ${item.price.toLocaleString()}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Sticky Action Bar */}
            <div className="fixed bottom-6 left-1/2 -translate-x-1/2 w-[90%] max-w-2xl glass-panel rounded-full p-2 pl-6 pr-2 flex items-center justify-between border border-emerald-500/30 shadow-[0_0_40px_rgba(0,0,0,0.5)] z-40">
                <div className="flex flex-col">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider">Total Estimate</span>
                    <span className="text-lg font-semibold text-white">
                        ${totalEstimate.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </span>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={onRequestChanges}
                        className="px-6 py-2.5 rounded-full text-sm font-medium text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
                    >
                        Request Changes
                    </button>
                    <button
                        onClick={onApprove}
                        className="px-8 py-2.5 rounded-full text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-500 shadow-lg shadow-emerald-500/25 transition-all"
                    >
                        Approve Quote
                    </button>
                </div>
            </div>
        </>
    );
}

