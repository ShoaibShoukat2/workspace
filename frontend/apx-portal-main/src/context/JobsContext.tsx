import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const API_BASE_URL = 'http://192.168.100.58:5001/api';

export interface CustomerJob {
  id: string;
  jobName: string;
  propertyAddress: string;
  city: string;
  customerName: string;
  customerEmail: string;
  trade: string;
  estimatedPay: string;
  description: string;
  scheduledTime?: string;
  squareFootage?: string;
  status: 'Open' | 'InProgress' | 'Complete' | 'Paid';
  assignedContractorId?: string | number;
  materialStatus?: 'AI Generated' | 'FM Verified' | 'Issues Found';
  createdAt: string;
  profileID?: string;
  // Contractor progress tracking
  contractorProgress?: {
    currentStep: 1 | 2 | 3 | 4 | 5;
    acknowledged: boolean;
    lastUpdated: string;
  };
}

interface JobsContextType {
  jobs: CustomerJob[];
  loading: boolean;
  error: string | null;
  refreshJobs: () => Promise<void>;
  createJob: (job: Omit<CustomerJob, 'id' | 'createdAt' | 'status'>) => Promise<CustomerJob>;
  updateJob: (jobId: string, updates: Partial<CustomerJob>) => Promise<void>;
  getJobById: (jobId: string) => CustomerJob | undefined;
  getJobsByCustomer: (customerEmail: string, profileID?: string) => CustomerJob[];
  getAvailableJobs: (trade?: string) => CustomerJob[];
  getJobsByContractor: (contractorId: string | number) => CustomerJob[];
  assignContractor: (jobId: string, contractorId: string | number) => Promise<void>;
  updateContractorProgress: (jobId: string, progress: CustomerJob['contractorProgress']) => Promise<void>;
}

const JobsContext = createContext<JobsContextType | undefined>(undefined);

// Helper to convert API job format to CustomerJob format
function convertApiJobToCustomerJob(apiJob: any): CustomerJob {
  return {
    id: apiJob.jobID || apiJob.id,
    jobName: apiJob.jobName,
    propertyAddress: apiJob.propertyAddress,
    city: apiJob.city,
    customerName: apiJob.customerName,
    customerEmail: apiJob.customerEmail,
    trade: apiJob.trade,
    estimatedPay: apiJob.estimatedPay,
    description: apiJob.description,
    scheduledTime: apiJob.scheduledTime || undefined,
    squareFootage: apiJob.squareFootage || undefined,
    status: apiJob.status || 'Open',
    assignedContractorId: apiJob.assignedContractorId || undefined,
    materialStatus: apiJob.materialStatus || undefined,
    createdAt: apiJob.createdAt || new Date().toISOString(),
    profileID: apiJob.profileID,
    contractorProgress: apiJob.contractorProgress_currentStep ? {
      currentStep: parseInt(apiJob.contractorProgress_currentStep) as 1 | 2 | 3 | 4 | 5,
      acknowledged: apiJob.contractorProgress_acknowledged === 'true' || apiJob.contractorProgress_acknowledged === true,
      lastUpdated: apiJob.contractorProgress_lastUpdated || new Date().toISOString(),
    } : undefined,
  };
}

// Helper to convert CustomerJob to API format
function convertCustomerJobToApi(job: Partial<CustomerJob>): any {
  return {
    jobID: job.id,
    profileID: job.profileID,
    jobName: job.jobName,
    propertyAddress: job.propertyAddress,
    city: job.city,
    customerName: job.customerName,
    customerEmail: job.customerEmail,
    trade: job.trade,
    estimatedPay: job.estimatedPay,
    description: job.description,
    scheduledTime: job.scheduledTime || '',
    squareFootage: job.squareFootage || '',
    status: job.status || 'Open',
    assignedContractorId: job.assignedContractorId?.toString() || '',
    materialStatus: job.materialStatus || '',
    contractorProgress_currentStep: job.contractorProgress?.currentStep?.toString() || '',
    contractorProgress_acknowledged: job.contractorProgress?.acknowledged?.toString() || '',
    contractorProgress_lastUpdated: job.contractorProgress?.lastUpdated || '',
  };
}

export function JobsProvider({ children }: { children: React.ReactNode }) {
  const [jobs, setJobs] = useState<CustomerJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch jobs from API
  const refreshJobs = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE_URL}/jobs`);
      if (!response.ok) {
        throw new Error(`Failed to fetch jobs: ${response.statusText}`);
      }
      const apiJobs = await response.json();
      const convertedJobs = apiJobs.map(convertApiJobToCustomerJob);
      setJobs(convertedJobs);
    } catch (err: any) {
      console.error('Error fetching jobs:', err);
      setError(err.message || 'Failed to fetch jobs');
      // Keep existing jobs on error
    } finally {
      setLoading(false);
    }
  }, []);

  // Load jobs on mount
  useEffect(() => {
    refreshJobs();
  }, [refreshJobs]);

  const createJob = async (jobData: Omit<CustomerJob, 'id' | 'createdAt' | 'status'>): Promise<CustomerJob> => {
    try {
      const apiPayload = {
        profileID: jobData.profileID || '',
        jobName: jobData.jobName,
        propertyAddress: jobData.propertyAddress,
        city: jobData.city,
        customerName: jobData.customerName,
        customerEmail: jobData.customerEmail,
        trade: jobData.trade,
        estimatedPay: jobData.estimatedPay,
        description: jobData.description,
        scheduledTime: jobData.scheduledTime || '',
        squareFootage: jobData.squareFootage || '',
      };

      const response = await fetch(`${API_BASE_URL}/jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(apiPayload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create job');
      }

      const result = await response.json();
      const newJob = convertApiJobToCustomerJob(result.job);
      
      // Refresh jobs list
      await refreshJobs();
      
      return newJob;
    } catch (err: any) {
      console.error('Error creating job:', err);
      throw err;
    }
  };

  const updateJob = async (jobId: string, updates: Partial<CustomerJob>) => {
    try {
      const existingJob = jobs.find(j => j.id === jobId);
      if (!existingJob) {
        throw new Error('Job not found');
      }

      const updatedJob = { ...existingJob, ...updates };
      const apiPayload = convertCustomerJobToApi(updatedJob);

      const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(apiPayload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to update job');
      }

      // Refresh jobs list
      await refreshJobs();
    } catch (err: any) {
      console.error('Error updating job:', err);
      throw err;
    }
  };

  const getJobById = (jobId: string) => jobs.find(j => j.id === jobId);

  const getJobsByCustomer = (customerEmail: string, profileID?: string) => {
    if (profileID) {
      // Filter by profileID if available (more reliable)
      return jobs.filter(j => j.profileID === profileID);
    }
    // Fallback to email filtering
    return jobs.filter(j => j.customerEmail === customerEmail);
  };

  const getAvailableJobs = (trade?: string) => 
    jobs.filter(j => 
      j.status === 'Open' && 
      !j.assignedContractorId && 
      (!trade || j.trade === trade)
    );

  const getJobsByContractor = (contractorId: string | number) =>
    jobs.filter(j => j.assignedContractorId?.toString() === contractorId.toString());

  const assignContractor = async (jobId: string, contractorId: string | number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/assign`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contractorId: contractorId.toString() }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to assign contractor');
      }

      // Update local state immediately for better UX
      await updateJob(jobId, { 
        assignedContractorId: contractorId, 
        status: 'InProgress',
        contractorProgress: {
          currentStep: 1,
          acknowledged: false,
          lastUpdated: new Date().toISOString(),
        },
      });
    } catch (err: any) {
      console.error('Error assigning contractor:', err);
      throw err;
    }
  };

  const updateContractorProgress = async (jobId: string, progress: CustomerJob['contractorProgress']) => {
    await updateJob(jobId, { contractorProgress: progress });
  };

  return (
    <JobsContext.Provider
      value={{
        jobs,
        loading,
        error,
        refreshJobs,
        createJob,
        updateJob,
        getJobById,
        getJobsByCustomer,
        getAvailableJobs,
        getJobsByContractor,
        assignContractor,
        updateContractorProgress,
      }}
    >
      {children}
    </JobsContext.Provider>
  );
}

export function useJobs() {
  const context = useContext(JobsContext);
  if (!context) {
    throw new Error('useJobs must be used within JobsProvider');
  }
  return context;
}

