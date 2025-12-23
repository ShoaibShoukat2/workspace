import React from 'react';
import { CheckCircle, Circle, Clock } from 'lucide-react';
import { Job } from '@/types';

interface JobProgressTimelineProps {
    status: Job['status'];
    visitStatus?: Job['visitStatus'];
}

const STEPS = [
    { id: 'Scheduled', label: 'Scheduled' },
    { id: 'EnRoute', label: 'En Route' },
    { id: 'OnSite', label: 'On Site' },
    { id: 'InProgress', label: 'In Progress' },
    { id: 'Completed', label: 'Completed' },
];

export default function JobProgressTimeline({ status, visitStatus }: JobProgressTimelineProps) {
    // Determine current step index
    let currentStepIndex = 0;

    // Map job status/visitStatus to step index
    if (status === 'Estimate') currentStepIndex = -1; // Before scheduled
    if (status === 'Open') currentStepIndex = 0; // Scheduled

    // Check visit status for finer granularity
    if (visitStatus === 'EnRoute') currentStepIndex = 1;
    if (visitStatus === 'Arrived' || visitStatus === 'OnSite') currentStepIndex = 2;

    if (status === 'InProgress') currentStepIndex = 3;

    if (status === 'Complete' || status === 'ReadyForPayout' || status === 'Paid') {
        currentStepIndex = 4;
    }

    // Special check for "En Route" if we could detect it (e.g. from a prop or complex logic)
    // For now, if InProgress, we assume they arrived. If Open, maybe they are en route?
    // Let's rely on the passed status. 

    return (
        <div className="relative">
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700" />

            <div className="space-y-8 relative">
                {STEPS.map((step, index) => {
                    const isCompleted = index <= currentStepIndex;
                    const isCurrent = index === currentStepIndex;

                    return (
                        <div key={step.id} className="flex items-start gap-4">
                            <div className={`relative z-10 flex items-center justify-center w-8 h-8 rounded-full border-2 transition-colors ${isCompleted
                                ? 'bg-green-500 border-green-500 text-white'
                                : isCurrent
                                    ? 'bg-blue-600 border-blue-600 text-white animate-pulse'
                                    : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-300'
                                }`}>
                                {isCompleted ? (
                                    <CheckCircle className="w-5 h-5" />
                                ) : isCurrent ? (
                                    <Clock className="w-5 h-5" />
                                ) : (
                                    <Circle className="w-5 h-5" />
                                )}
                            </div>
                            <div className="pt-1">
                                <h4 className={`text-sm font-bold ${isCompleted || isCurrent ? 'text-gray-900 dark:text-white' : 'text-gray-400'
                                    }`}>
                                    {step.label}
                                </h4>
                                {isCurrent && (
                                    <p className="text-xs text-blue-600 dark:text-blue-400 font-medium mt-1">
                                        Current Status
                                    </p>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
