import React from 'react';
import { cn } from '@/lib/utils';

interface PrimaryButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean;
}

export default function PrimaryButton({
  children,
  className,
  loading,
  disabled,
  ...props
}: PrimaryButtonProps) {
  const isDisabled = disabled || loading;

  return (
    <button
      className={cn(
        'w-full bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-4 rounded-xl',
        'transition-all shadow-[0_0_24px_rgba(16,185,129,0.25)] hover:shadow-[0_0_32px_rgba(16,185,129,0.45)]',
        'flex items-center justify-center gap-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/60 focus:ring-offset-0',
        isDisabled && 'opacity-60 cursor-not-allowed hover:bg-emerald-600 hover:shadow-none',
        className,
      )}
      disabled={isDisabled}
      {...props}
    >
      {loading ? 'Loading...' : children}
    </button>
  );
}


