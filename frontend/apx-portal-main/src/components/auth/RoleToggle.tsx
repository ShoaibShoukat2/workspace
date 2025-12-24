import React from 'react';
import type { UserRole } from '@/types';

export interface RoleOption {
  id: string;
  label: string;
  role: UserRole;
}

interface RoleToggleProps {
  options: RoleOption[];
  activeRole: UserRole;
  onChange: (role: UserRole) => void;
}

export default function RoleToggle({ options, activeRole, onChange }: RoleToggleProps) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mb-8 p-1 bg-white/5 rounded-xl border border-white/5">
      {options.map((opt) => {
        const isActive = opt.role === activeRole;
        return (
          <button
            key={opt.id}
            type="button"
            onClick={() => onChange(opt.role)}
            className={[
              'py-2.5 px-3 rounded-lg text-[11px] font-medium transition-all whitespace-nowrap',
              isActive
                ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-500/20'
                : 'text-slate-400 hover:text-white hover:bg-white/5',
            ].join(' ')}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}


