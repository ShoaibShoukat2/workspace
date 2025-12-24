import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, ArrowRight } from 'lucide-react';
import '@/styles/customerPortal.css';

interface CustomerLoginProps {
    onLogin?: () => void;
}

export default function CustomerLogin({ onLogin }: CustomerLoginProps) {
    const navigate = useNavigate();
    const [email, setEmail] = useState('sarah@apex.home');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (onLogin) {
            onLogin();
        } else {
            // Default: navigate to customer dashboard
            navigate('/customer/jobs/8291');
        }
    };

    return (
        <div className="min-h-screen w-full bg-slate-950 flex flex-col lg:flex-row transition-transform duration-700 ease-in-out">
            {/* Abstract Visual */}
            <div className="hidden lg:flex lg:w-3/5 relative overflow-hidden">
                <div
                    className="absolute inset-0 bg-cover bg-center opacity-60"
                    style={{
                        backgroundImage: `url('https://images.unsplash.com/photo-1600607686527-6fb886090705?q=80&w=2700&auto=format&fit=crop')`,
                    }}
                />
                <div className="absolute inset-0 bg-gradient-to-r from-slate-950 via-slate-950/80 to-transparent" />

                <div className="relative z-10 p-20 flex flex-col justify-between h-full">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-[0_0_30px_rgba(16,185,129,0.3)]">
                            <Home className="text-white w-6 h-6 stroke-[2]" />
                        </div>
                        <span className="text-3xl font-bold tracking-tight text-white">Apex</span>
                    </div>

                    <div className="max-w-2xl">
                        <h1 className="text-6xl font-medium text-white leading-[1.1] tracking-tight mb-8">
                            The operating system for <br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-300">
                                modern craftsmanship
                            </span>
                            .
                        </h1>
                        <div className="flex gap-8">
                            <div className="pl-4 border-l border-emerald-500/50">
                                <p className="text-sm text-emerald-400 font-semibold uppercase tracking-widest mb-1">
                                    Transparent
                                </p>
                                <p className="text-slate-400 font-light text-lg">Real-time visual tracking.</p>
                            </div>
                            <div className="pl-4 border-l border-emerald-500/50">
                                <p className="text-sm text-emerald-400 font-semibold uppercase tracking-widest mb-1">
                                    Secure
                                </p>
                                <p className="text-slate-400 font-light text-lg">Escrow-backed payments.</p>
                            </div>
                        </div>
                    </div>

                    <p className="text-xs text-slate-600 tracking-widest uppercase">
                        © 2025 APEX INC. • ENTERPRISE FIELD OPERATIONS
                    </p>
                </div>
            </div>

            {/* Login Form */}
            <div className="w-full lg:w-2/5 flex items-center justify-center relative bg-slate-950">
                <div className="pointer-events-none absolute inset-0 bg-grid-pattern opacity-[0.03]" />

                <div className="w-full max-w-sm p-8 z-10 animate-enter">
                    <div className="mb-12">
                        <h2 className="text-3xl font-semibold text-white tracking-tight mb-2">Welcome Home</h2>
                        <p className="text-slate-500 font-light">Sign in to track your renovation.</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                                Email Address
                            </label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full bg-slate-900 border border-white/10 rounded-xl py-4 px-4 text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 transition-all font-light"
                                placeholder="name@email.com"
                            />
                        </div>

                        <button
                            type="submit"
                            className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-4 rounded-xl transition-all shadow-[0_0_30px_rgba(16,185,129,0.2)] hover:shadow-[0_0_40px_rgba(16,185,129,0.4)] flex items-center justify-center gap-2 group"
                        >
                            <span>Access Dashboard</span>
                            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}

