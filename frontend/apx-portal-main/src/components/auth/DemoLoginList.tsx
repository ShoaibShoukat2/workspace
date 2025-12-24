import React from 'react';
import type { User } from '@/types';
import { users } from '@/data/mockData';

interface DemoLoginListProps {
  onSelect: (user: User) => void;
}

const ROLE_LABELS: Record<User['role'], string> = {
  admin: 'Admin',
  fm: 'Field Manager',
  contractor: 'Contractor',
  investor: 'Investor',
  customer: 'Homeowner',
};

export default function DemoLoginList({ onSelect }: DemoLoginListProps) {
  return (
    <div className="mt-10 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white tracking-tight">Quick Demo Login</h3>
        <span className="text-[10px] uppercase tracking-wider text-slate-500">
          Tap a profile to auto-fill
        </span>
      </div>

      <div className="space-y-2">
        {users.filter((user) => user.role !== 'fm').map((user) => (
          <button
            key={user.id}
            type="button"
            onClick={() => onSelect(user)}
            className="w-full glass-panel glass-card-hover rounded-2xl px-4 py-3 text-left flex items-center justify-between"
          >
            <div>
              <p className="text-sm font-medium text-white">{user.name}</p>
              <p className="text-xs text-slate-400">{user.email}</p>
            </div>
            <span className="px-3 py-1 rounded-full border border-emerald-500/40 bg-emerald-500/10 text-[10px] font-semibold uppercase tracking-wider text-emerald-300">
              {ROLE_LABELS[user.role]}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}


