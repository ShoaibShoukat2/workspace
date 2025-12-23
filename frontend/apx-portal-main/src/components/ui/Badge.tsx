import React from 'react';
import { cn } from '@/lib/utils';

interface BadgeProps {
    children: React.ReactNode;
    variant?: 'success' | 'warning' | 'danger' | 'info' | 'default';
    className?: string;
}

export default function Badge({ children, variant = 'default', className }: BadgeProps) {
    const variants = {
        success: 'bg-green-500/20 text-green-300 border-green-500/30',
        warning: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
        danger: 'bg-red-500/20 text-red-300 border-red-500/30',
        info: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
        default: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
    };

    return (
        <span
            className={cn(
                'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border backdrop-blur-sm',
                variants[variant],
                className
            )}
        >
            {children}
        </span>
    );
}

// Helper function to get status badge variant
export function getStatusBadgeVariant(status: string): BadgeProps['variant'] {
    const statusMap: Record<string, BadgeProps['variant']> = {
        active: 'success',
        completed: 'success',
        paid: 'success',
        delivered: 'success',
        blocked: 'danger',
        declined: 'danger',
        open: 'warning',
        pending: 'warning',
        processing: 'info',
        inprogress: 'info',
        estimate: 'default',
    };

    return statusMap[status.toLowerCase()] || 'default';
}
