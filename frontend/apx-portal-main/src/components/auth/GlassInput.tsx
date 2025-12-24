import React from 'react';
import { cn } from '@/lib/utils';

interface GlassInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

export default function GlassInput({ label, id, className, ...props }: GlassInputProps) {
  const inputId = id || props.name || label.toLowerCase().replace(/\s+/g, '-');

  return (
    <div className="space-y-2">
      <label
        htmlFor={inputId}
        className="text-[10px] font-medium text-slate-400 uppercase tracking-wider"
      >
        {label}
      </label>
      <input
        id={inputId}
        className={cn(
          'w-full glass-input rounded-xl py-4 px-4 text-white placeholder-slate-600',
          'focus:outline-none transition-all font-light text-sm',
          className,
        )}
        {...props}
      />
    </div>
  );
}


