import React from 'react';
import { Home } from 'lucide-react';

interface AuthLayoutSplitProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
}

export default function AuthLayoutSplit({
  children,
  title = 'Welcome Pro',
  subtitle = 'Access your job cockpit.',
}: AuthLayoutSplitProps) {
  return (
    <div className="min-h-screen w-full bg-slate-950 text-white flex flex-col lg:flex-row overflow-hidden">
      {/* Hero / Left */}
      <div className="hidden lg:flex lg:w-3/5 relative overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center opacity-40"
          style={{
            backgroundImage:
              "url('https://images.unsplash.com/photo-1600607686527-6fb886090705?q=80&w=2700&auto=format&fit=crop')",
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
          </div>

          <p className="text-xs text-slate-600 tracking-widest uppercase">© 2025 APEX INC.</p>
        </div>
      </div>

      {/* Auth Panel / Right */}
      <div className="w-full lg:w-2/5 relative bg-slate-950 flex items-center justify-center">
        <div className="pointer-events-none absolute inset-0 bg-grid-pattern opacity-[0.03]" />
        <div className="w-full max-w-sm p-8 z-10 animate-enter font-[Manrope,sans-serif] space-y-6 relative">
          <div className="sticky top-0 z-20 -mx-8 px-8 py-4 bg-slate-950/95 backdrop-blur-xl border-b border-white/5">
            <h2 className="text-3xl font-semibold text-white tracking-tight mb-2">{title}</h2>
            <p className="text-slate-500 font-light">{subtitle}</p>
          </div>
          <div className="space-y-6">{children}</div>
        </div>
      </div>
    </div>
  );
}


