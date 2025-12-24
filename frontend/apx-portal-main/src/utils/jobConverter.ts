import type { CustomerJob as JobsContextJob } from '@/context/JobsContext';
import type { CustomerJob as CustomerPortalJob } from '@/types/customerPortal';

/**
 * Converts a job from JobsContext format to CustomerPortal format
 */
export function convertJobToCustomerPortal(job: JobsContextJob): CustomerPortalJob {
  // Parse estimated pay to number
  const estimatedCost = parseFloat(job.estimatedPay.replace(/[^0-9.]/g, '')) || 0;

  // Determine status
  let status: 'active' | 'pending' | 'completed' = 'pending';
  if (job.status === 'InProgress') {
    status = 'active';
  } else if (job.status === 'Complete' || job.status === 'Paid') {
    status = 'completed';
  }

  // Create timeline steps based on contractor progress
  const timelineSteps = [];
  const currentStep = job.contractorProgress?.currentStep || 0;
  
  timelineSteps.push({ id: '1', label: 'Job Created', status: 'completed' });
  
  if (currentStep >= 2) {
    timelineSteps.push({ id: '2', label: 'Walkthrough Scheduled', status: 'completed' });
  } else {
    timelineSteps.push({ id: '2', label: 'Walkthrough Scheduled', status: 'pending' });
  }
  
  if (currentStep >= 3) {
    timelineSteps.push({ id: '3', label: 'Quote Pending Approval', status: 'active' });
  } else if (currentStep === 2) {
    timelineSteps.push({ id: '3', label: 'Quote Pending Approval', status: 'pending' });
  } else {
    timelineSteps.push({ id: '3', label: 'Quote Pending Approval', status: 'pending' });
  }
  
  if (currentStep >= 4) {
    timelineSteps.push({ id: '4', label: 'Work in Progress', status: 'active' });
  } else {
    timelineSteps.push({ id: '4', label: 'Work in Progress', status: 'pending' });
  }

  // Create scope items from description
  const scopeItems = [
    {
      id: '1',
      title: 'Project Overview',
      description: job.description || 'No description provided',
      price: estimatedCost * 0.3,
      completed: currentStep >= 2,
    },
    {
      id: '2',
      title: 'Initial Assessment',
      description: 'Site walkthrough and assessment',
      price: estimatedCost * 0.2,
      completed: currentStep >= 2,
    },
    {
      id: '3',
      title: 'Main Work',
      description: job.description || 'Main project work',
      price: estimatedCost * 0.5,
      completed: currentStep >= 4,
    },
  ];

  // Create progress phases based on contractor progress
  const progressPhases = [];
  if (currentStep >= 2) {
    progressPhases.push({
      id: '1',
      title: 'Demolition Phase',
      status: 'completed' as const,
    });
  } else {
    progressPhases.push({
      id: '1',
      title: 'Demolition Phase',
      status: 'pending' as const,
    });
  }

  if (currentStep >= 3) {
    progressPhases.push({
      id: '2',
      title: 'Installation & Finishes',
      status: currentStep >= 4 ? 'completed' : ('active' as const),
      dayProgress: currentStep >= 4 ? 'Day 5/5' : 'Day 3/5',
      contractorNote: currentStep >= 3 ? {
        author: 'Contractor',
        avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&q=80&w=150',
        text: 'Work is progressing well. All materials have been delivered and installation has begun.',
      } : undefined,
      tasks: [
        { id: '1', label: 'Waterproofing', status: currentStep >= 3 ? ('completed' as const) : ('pending' as const) },
        { id: '2', label: 'Installation', status: currentStep >= 4 ? ('in-progress' as const) : ('pending' as const) },
        { id: '3', label: 'Finishing', status: 'pending' as const },
      ],
    });
  } else {
    progressPhases.push({
      id: '2',
      title: 'Installation & Finishes',
      status: 'pending' as const,
    });
  }

  if (currentStep >= 5) {
    progressPhases.push({
      id: '3',
      title: 'Final Walkthrough',
      status: 'completed' as const,
    });
  } else {
    progressPhases.push({
      id: '3',
      title: 'Final Walkthrough',
      status: 'pending' as const,
    });
  }

  // Calculate schedule
  const startDate = job.scheduledTime ? new Date(job.scheduledTime) : new Date();
  const completionDate = new Date(startDate);
  completionDate.setDate(completionDate.getDate() + 21); // 3 weeks default

  return {
    id: job.id,
    title: job.jobName,
    address: `${job.propertyAddress}, ${job.city}`,
    status,
    estimatedCost,
    schedule: {
      duration: '3 Weeks',
      completionDate: completionDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    },
    contractor: {
      id: job.assignedContractorId?.toString() || '1',
      name: 'Contractor',
      avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&q=80&w=150&h=150',
      rating: 4.9,
      jobsCount: 128,
      role: 'Lead Contractor',
    },
    timelineSteps,
    measurements: job.squareFootage ? {
      totalArea: job.squareFootage,
      ceilingHeight: '9.5 ft',
    } : undefined,
    scopeItems,
    progressPhases,
    materials: [],
    gallery: [],
  };
}

