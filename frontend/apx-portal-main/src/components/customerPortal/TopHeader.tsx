import { Phone, MessageSquare } from 'lucide-react';

interface TopHeaderProps {
    jobTitle: string;
    jobId: string;
    address: string;
    isActive?: boolean;
}

export default function TopHeader({ jobTitle, jobId, address, isActive = true }: TopHeaderProps) {
    return (
        <header className="h-24 shrink-0 flex items-center justify-between px-8 lg:px-12 border-b border-white/5 z-20 bg-slate-950/80 backdrop-blur-md">
            <div>
                <div className="flex items-center gap-2 text-xs text-emerald-500 font-medium uppercase tracking-widest mb-1">
                    {isActive && <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />}
                    Active Project
                </div>
                <h1 className="text-2xl font-semibold text-white tracking-tight">{jobTitle}</h1>
                <p className="text-sm text-slate-500">
                    Job ID: #{jobId} • {address}
                </p>
            </div>

            <div className="flex items-center gap-4">
                <button className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center text-slate-400 hover:text-white hover:bg-white/5 transition-colors">
                    <Phone className="w-4 h-4" />
                </button>
                <button className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center text-slate-400 hover:text-white hover:bg-white/5 transition-colors relative">
                    <MessageSquare className="w-4 h-4" />
                    <span className="absolute top-0 right-0 w-2.5 h-2.5 bg-rose-500 rounded-full border-2 border-slate-950" />
                </button>
            </div>
        </header>
    );
}

