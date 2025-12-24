import { Check, Star, CalendarCheck, Coins, ShieldCheck, Lock } from 'lucide-react';
import type { CustomerJob } from '@/types/customerPortal';

interface CompletionViewProps {
    job: CustomerJob;
    onReleaseFunds?: () => void;
}

export default function CompletionView({ job, onReleaseFunds }: CompletionViewProps) {
    return (
        <div className="p-8 lg:p-12 max-w-5xl mx-auto space-y-10 animate-enter pb-32">
            {/* Celebration Banner */}
            <div className="relative py-12 text-center rounded-3xl overflow-hidden border border-white/10 group">
                <div className="absolute inset-0 bg-gradient-to-r from-emerald-900/20 via-slate-900 to-emerald-900/20" />
                <div
                    className="absolute inset-0 opacity-10"
                    style={{
                        backgroundImage: `url('https://www.transparenttextures.com/patterns/stardust.png')`,
                    }}
                />

                <div className="relative z-10 flex flex-col items-center">
                    <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-emerald-400 to-teal-300 flex items-center justify-center shadow-[0_0_40px_rgba(16,185,129,0.5)] mb-6 animate-bounce">
                        <Check className="w-8 h-8 text-slate-900 stroke-[3]" />
                    </div>
                    <h1 className="text-5xl font-light text-white tracking-tight mb-2">Masterpiece Delivered</h1>
                    <p className="text-lg text-slate-400 font-light">Your renovation is officially complete.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Left: Review Experience */}
                <div className="lg:col-span-7 space-y-6">
                    <div className="glass-panel p-8 rounded-3xl relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/5 blur-3xl rounded-full" />
                        <h3 className="text-xl font-medium text-white mb-6">Rate Your Experience</h3>

                        {/* Stars */}
                        <div className="flex items-center gap-2 mb-8">
                            {[1, 2, 3, 4, 5].map((star) => (
                                <Star
                                    key={star}
                                    className={`w-8 h-8 ${
                                        star <= 4
                                            ? 'text-amber-400 fill-amber-400'
                                            : 'text-slate-700 hover:text-amber-400'
                                    } cursor-pointer hover:scale-110 transition-transform`}
                                />
                            ))}
                        </div>

                        {/* Sliders */}
                        <div className="space-y-5 mb-8">
                            <div className="space-y-2">
                                <div className="flex justify-between text-xs font-medium text-slate-400 uppercase tracking-wider">
                                    <span>Communication</span>
                                    <span className="text-emerald-400">Excellent</span>
                                </div>
                                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                                    <div className="h-full w-[90%] bg-gradient-to-r from-emerald-600 to-emerald-400 rounded-full" />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <div className="flex justify-between text-xs font-medium text-slate-400 uppercase tracking-wider">
                                    <span>Quality of Finish</span>
                                    <span className="text-emerald-400">Perfect</span>
                                </div>
                                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                                    <div className="h-full w-[98%] bg-gradient-to-r from-emerald-600 to-emerald-400 rounded-full" />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <div className="flex justify-between text-xs font-medium text-slate-400 uppercase tracking-wider">
                                    <span>Timeliness</span>
                                    <span className="text-slate-300">On Time</span>
                                </div>
                                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                                    <div className="h-full w-[85%] bg-slate-500 rounded-full" />
                                </div>
                            </div>
                        </div>

                        <textarea
                            className="w-full h-32 bg-slate-900/50 border border-white/10 rounded-xl p-4 text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500/50 transition-all text-sm resize-none"
                            placeholder="Share your thoughts about the craftsmanship..."
                        />
                    </div>

                    {/* Final Photos */}
                    {job.gallery && job.gallery.length > 0 && (
                        <div className="grid grid-cols-2 gap-4 h-48">
                            {job.gallery.slice(0, 2).map((photo) => (
                                <div
                                    key={photo.id}
                                    className="relative rounded-2xl overflow-hidden group cursor-pointer border border-white/5"
                                >
                                    <div className="absolute inset-0 bg-black/20 group-hover:bg-transparent transition-colors z-10" />
                                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent z-10" />
                                    <img
                                        src={photo.image}
                                        alt={photo.label}
                                        className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                                    />
                                    <div className="absolute bottom-3 left-4 z-20 text-white text-xs font-medium">
                                        {photo.label}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Right: Project Stats & Payment */}
                <div className="lg:col-span-5 space-y-6">
                    {/* Stats Card */}
                    <div className="glass-panel p-6 rounded-3xl">
                        <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-6">
                            Project Summary
                        </h3>
                        <div className="grid grid-cols-2 gap-4 mb-6">
                            <div className="p-4 rounded-2xl bg-white/5 border border-white/5 flex flex-col items-center text-center">
                                <CalendarCheck className="w-5 h-5 text-indigo-400 mb-2" />
                                <span className="text-xl font-light text-white">21</span>
                                <span className="text-[10px] text-slate-500 uppercase">Days Duration</span>
                            </div>
                            <div className="p-4 rounded-2xl bg-white/5 border border-white/5 flex flex-col items-center text-center">
                                <Coins className="w-5 h-5 text-emerald-400 mb-2" />
                                <span className="text-xl font-light text-white">
                                    {(job.estimatedCost / 1000).toFixed(1)}k
                                </span>
                                <span className="text-[10px] text-slate-500 uppercase">Total Value</span>
                            </div>
                        </div>
                        <div className="flex items-center gap-3 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                            <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center">
                                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                            </div>
                            <div>
                                <div className="text-white text-xs font-medium">Apex Warranty Active</div>
                                <div className="text-[10px] text-emerald-400/80">Coverage until Nov 2028</div>
                            </div>
                        </div>
                    </div>

                    {/* Payment Action */}
                    {job.finalBalance && (
                        <div className="glass-panel p-8 rounded-3xl border-t-4 border-t-emerald-500">
                            <div className="flex justify-between items-end mb-6">
                                <span className="text-slate-400 text-sm">Final Balance</span>
                                <span className="text-2xl font-semibold text-white">
                                    ${job.finalBalance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                </span>
                            </div>
                            <button
                                onClick={onReleaseFunds}
                                className="w-full py-4 rounded-xl bg-white text-slate-950 font-bold text-sm uppercase tracking-wide hover:bg-slate-200 transition-colors shadow-[0_0_30px_rgba(255,255,255,0.1)] flex items-center justify-center gap-2"
                            >
                                <Lock className="w-4 h-4" />
                                Release & Close Project
                            </button>
                            <p className="text-center text-[10px] text-slate-500 mt-4">
                                By releasing funds, you certify the work is complete.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

