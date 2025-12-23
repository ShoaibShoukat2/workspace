import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps {
    children: React.ReactNode;
    className?: string;
    onClick?: () => void;
    hover?: boolean;
}

export default function Card({ children, className, onClick, hover = true }: CardProps) {
    return (
        <div
            className={cn(
                'glass-card p-6',
                hover && 'hover:scale-[1.02] cursor-pointer',
                'smooth-transition',
                className
            )}
            onClick={onClick}
        >
            {children}
        </div>
    );
}
