import { Sparkles, PackageOpen, Plus, Camera, CheckCircle } from 'lucide-react';
import type { CustomerJob } from '@/types/customerPortal';

interface MaterialSourcingViewProps {
    job: CustomerJob;
    onMaterialAdd?: (materialId: string) => void;
    onSelfSourcing?: () => void;
}

export default function MaterialSourcingView({
    job,
    onMaterialAdd,
    onSelfSourcing,
}: MaterialSourcingViewProps) {
    const getVendorColorClass = (color: string) => {
        const colorMap: Record<string, string> = {
            orange: 'bg-orange-500/20 text-orange-500',
            blue: 'bg-blue-500/20 text-blue-500',
            purple: 'bg-purple-500/20 text-purple-500',
        };
        return colorMap[color] || 'bg-slate-500/20 text-slate-500';
    };

    return (
        <div className="p-8 lg:p-12 max-w-7xl mx-auto min-h-full flex flex-col animate-enter">
            <div className="flex items-end justify-between mb-10">
                <div>
                    <h2 className="text-3xl font-light text-white tracking-tight mb-2">Material Sourcing</h2>
                    <p className="text-slate-400 max-w-xl">
                        Curated recommendations from trusted vendors based on your quote specifications.
                    </p>
                </div>
                <div className="hidden md:flex gap-3">
                    <span className="px-3 py-1 rounded-full border border-white/10 text-xs text-slate-300 bg-white/5">
                        Plumbing
                    </span>
                    <span className="px-3 py-1 rounded-full border border-white/10 text-xs text-slate-300 bg-white/5">
                        Tiling
                    </span>
                    <span className="px-3 py-1 rounded-full border border-white/10 text-xs text-slate-300 bg-white/5">
                        Cabinetry
                    </span>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 h-full">
                {/* Left: Marketplace Grid */}
                <div className="lg:col-span-8 space-y-6">
                    <div className="flex items-center gap-2 mb-2">
                        <Sparkles className="w-4 h-4 text-emerald-400" />
                        <span className="text-xs font-semibold text-emerald-400 uppercase tracking-widest">
                            Recommended For You
                        </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {job.materials?.map((material) => (
                            <div
                                key={material.id}
                                className="glass-panel p-4 rounded-2xl group cursor-pointer glass-card-hover relative overflow-hidden"
                            >
                                {material.inStock && (
                                    <div className="absolute top-3 right-3 z-10 bg-black/60 backdrop-blur-md px-2 py-1 rounded text-[10px] text-white font-medium border border-white/10">
                                        In Stock
                                    </div>
                                )}
                                <div className="aspect-[4/3] rounded-xl overflow-hidden mb-4 bg-white/5 relative">
                                    <img
                                        src={material.image}
                                        alt={material.name}
                                        className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                                    />
                                </div>
                                <div className="space-y-3">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h4 className="text-white font-medium">{material.name}</h4>
                                            <p className="text-xs text-slate-500 mt-1">{material.description}</p>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-white font-semibold">${material.price}</div>
                                            <div className="text-[10px] text-slate-500">{material.unit}</div>
                                        </div>
                                    </div>
                                    <div className="flex items-center justify-between pt-3 border-t border-white/5">
                                        <div className="flex items-center gap-2">
                                            <div
                                                className={`w-5 h-5 rounded-full ${getVendorColorClass(
                                                    material.vendor.color,
                                                )} flex items-center justify-center text-[10px] font-bold`}
                                            >
                                                {material.vendor.logo}
                                            </div>
                                            <span className="text-xs text-slate-400">{material.vendor.name}</span>
                                        </div>
                                        <button
                                            onClick={() => onMaterialAdd?.(material.id)}
                                            className="w-8 h-8 rounded-full bg-emerald-500/10 hover:bg-emerald-500 text-emerald-500 hover:text-white flex items-center justify-center transition-all"
                                        >
                                            <Plus className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Right: I Have Materials */}
                <div className="lg:col-span-4 flex flex-col">
                    <div className="flex items-center gap-2 mb-2">
                        <PackageOpen className="w-4 h-4 text-slate-400" />
                        <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
                            Self Sourcing
                        </span>
                    </div>

                    <div
                        onClick={onSelfSourcing}
                        className="flex-1 glass-panel rounded-2xl p-8 relative overflow-hidden group hover:border-white/20 transition-all cursor-pointer flex flex-col items-center justify-center text-center"
                    >
                        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-slate-900/50" />
                        <div className="absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity bg-[url('https://www.transparenttextures.com/patterns/cubes.png')]" />

                        <div className="w-20 h-20 rounded-full bg-slate-800/50 border border-white/5 flex items-center justify-center mb-8 group-hover:scale-110 transition-transform duration-500 shadow-[0_0_40px_rgba(0,0,0,0.3)]">
                            <Camera className="w-8 h-8 text-slate-300 stroke-[1.5]" />
                        </div>

                        <h3 className="text-xl font-medium text-white mb-3">I Have My Materials</h3>
                        <p className="text-sm text-slate-400 leading-relaxed mb-8 max-w-xs">
                            Upload photos or receipts of materials you've already purchased. You assume
                            responsibility for dimensions and delivery.
                        </p>

                        <button className="px-6 py-3 rounded-full bg-white/5 hover:bg-white/10 text-white text-xs font-semibold uppercase tracking-wider border border-white/10 transition-all flex items-center gap-2">
                            <Camera className="w-4 h-4" />
                            Upload Proof
                        </button>

                        <div className="mt-auto pt-8 flex items-center gap-2 text-[10px] text-emerald-500 uppercase tracking-wider font-semibold">
                            <CheckCircle className="w-3 h-3" />
                            Zero Platform Fee
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

