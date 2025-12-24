import React, { createContext, useContext, useState, useEffect } from 'react';

export interface CompletedJob {
  id: string;
  jobName: string;
  customerName: string;
  address: string;
  completedDate: string;
  estimatedPay: string;
  description?: string;
}

interface ContractorJobsContextType {
  completedJobs: CompletedJob[];
  addCompletedJob: (job: CompletedJob) => void;
  completedJobsCount: number;
}

const ContractorJobsContext = createContext<ContractorJobsContextType | undefined>(undefined);

const STORAGE_KEY = 'contractor_completed_jobs';

export function ContractorJobsProvider({ children }: { children: React.ReactNode }) {
  const [completedJobs, setCompletedJobs] = useState<CompletedJob[]>([]);

  useEffect(() => {
    // Load from localStorage on mount
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        setCompletedJobs(JSON.parse(stored));
      } catch (e) {
        console.error('Failed to load completed jobs:', e);
      }
    }
  }, []);

  // Listen for storage events to sync across tabs/windows
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === STORAGE_KEY && e.newValue) {
        try {
          setCompletedJobs(JSON.parse(e.newValue));
        } catch (e) {
          console.error('Failed to sync completed jobs from storage event:', e);
        }
      }
    };

    // Also listen for custom storage events (for same-tab updates)
    const handleCustomStorage = () => {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        try {
          setCompletedJobs(JSON.parse(stored));
        } catch (e) {
          console.error('Failed to sync completed jobs from custom event:', e);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('localStorageUpdate', handleCustomStorage);
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('localStorageUpdate', handleCustomStorage);
    };
  }, []);

  const addCompletedJob = (job: CompletedJob) => {
    const updated = [job, ...completedJobs];
    setCompletedJobs(updated);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    // Dispatch custom event for same-tab updates
    window.dispatchEvent(new CustomEvent('localStorageUpdate'));
  };

  return (
    <ContractorJobsContext.Provider
      value={{
        completedJobs,
        addCompletedJob,
        completedJobsCount: completedJobs.length,
      }}
    >
      {children}
    </ContractorJobsContext.Provider>
  );
}

export function useContractorJobs() {
  const context = useContext(ContractorJobsContext);
  if (!context) {
    throw new Error('useContractorJobs must be used within ContractorJobsProvider');
  }
  return context;
}

