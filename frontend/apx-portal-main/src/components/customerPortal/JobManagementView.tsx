import { useState } from 'react';
import * as React from 'react';
import { useAuth } from '@/context/AuthContext';
import { useJobs } from '@/context/JobsContext';
import {
  Plus,
  MapPin,
  Calendar,
  DollarSign,
  Hammer,
  FileText,
  ChevronRight,
  X,
  Info,
} from 'lucide-react';

interface JobManagementViewProps {
  onJobSelect: (jobId: string) => void;
}

export default function JobManagementView({ onJobSelect }: JobManagementViewProps) {
  const { currentUser } = useAuth();
  const { jobs, createJob, getJobsByCustomer, loading, error, refreshJobs } = useJobs();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    jobName: '',
    propertyAddress: '',
    city: '',
    trade: '',
    estimatedPay: '',
    description: '',
    scheduledTime: '',
    squareFootage: '',
  });

  // Get customer jobs filtered by profileID (preferred) or email (fallback)
  const customerJobs = getJobsByCustomer(currentUser?.email || '', currentUser?.profileID);
  
  // Refresh jobs when component mounts
  React.useEffect(() => {
    refreshJobs();
  }, [refreshJobs]);

  // Check if user has profileID
  const hasProfileID = !!currentUser?.profileID;

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate user is logged in
    if (!currentUser) {
      alert('Please log in to create a job.');
      return;
    }

    // Validate profileID is required
    if (!currentUser.profileID) {
      alert('Profile ID is required. Please log in again to get your profile ID.');
      return;
    }

    try {
      const newJob = await createJob({
        jobName: formData.jobName,
        propertyAddress: formData.propertyAddress,
        city: formData.city,
        customerName: currentUser.name,
        customerEmail: currentUser.email,
        trade: formData.trade,
        estimatedPay: formData.estimatedPay,
        description: formData.description,
        scheduledTime: formData.scheduledTime || undefined,
        squareFootage: formData.squareFootage || undefined,
        profileID: currentUser.profileID, // Required - already validated above
      });

      setShowCreateModal(false);
      setFormData({
        jobName: '',
        propertyAddress: '',
        city: '',
        trade: '',
        estimatedPay: '',
        description: '',
        scheduledTime: '',
        squareFootage: '',
      });
      // Select the newly created job
      onJobSelect(newJob.id);
    } catch (error: any) {
      console.error('Failed to create job:', error);
      alert(`Failed to create job: ${error.message || 'Unknown error'}`);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      Open: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      InProgress: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      Complete: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
      Paid: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    };
    return styles[status as keyof typeof styles] || styles.Open;
  };

  return (
    <div className="min-h-full p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight text-white mb-2">Job Management</h1>
            <p className="text-slate-400 text-sm">Create and manage your service requests</p>
          </div>
          <button
            onClick={() => {
              if (!hasProfileID) {
                alert('Profile ID is required. Please log in again to get your profile ID.');
                return;
              }
              setShowCreateModal(true);
            }}
            disabled={!hasProfileID}
            className="px-6 py-3 rounded-xl bg-emerald-600 text-white font-semibold hover:bg-emerald-500 transition-all shadow-lg shadow-emerald-500/20 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Plus className="w-5 h-5" /> Create New Job
          </button>
        </div>

        {/* Profile ID Warning */}
        {!hasProfileID && (
          <div className="glass-panel p-6 rounded-2xl border border-amber-500/20 bg-amber-500/5 mb-6">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-amber-500/10">
                <Info className="w-5 h-5 text-amber-400" />
              </div>
              <div className="flex-1">
                <h3 className="text-sm font-medium text-amber-200 mb-1">Profile ID Required</h3>
                <p className="text-xs text-amber-200/80">
                  You need to log in with your profile ID to create and view jobs. Please log out and log in again.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="glass-panel p-6 rounded-2xl border border-red-500/20 bg-red-500/5 mb-6">
            <p className="text-sm text-red-400">Error loading jobs: {error}</p>
            <button
              onClick={() => refreshJobs()}
              className="mt-2 text-xs text-red-300 hover:text-red-200 underline"
            >
              Retry
            </button>
          </div>
        )}

        {/* Jobs Grid */}
        {loading ? (
          <div className="glass-panel p-12 rounded-2xl text-center border border-white/10">
            <p className="text-slate-400">Loading jobs...</p>
          </div>
        ) : customerJobs.length === 0 ? (
          <div className="glass-panel p-12 rounded-2xl text-center border border-white/10">
            <FileText className="w-16 h-16 text-slate-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">No Jobs Yet</h3>
            <p className="text-slate-400 mb-6">Create your first job to get started.</p>
            <button
              onClick={() => {
                if (!hasProfileID) {
                  alert('Profile ID is required. Please log in again to get your profile ID.');
                  return;
                }
                setShowCreateModal(true);
              }}
              disabled={!hasProfileID}
              className="px-6 py-3 rounded-xl bg-emerald-600 text-white font-semibold hover:bg-emerald-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Create Your First Job
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {customerJobs.map((job) => (
              <div
                key={job.id}
                onClick={() => onJobSelect(job.id)}
                className="glass-card p-6 rounded-2xl cursor-pointer hover:border-emerald-500/30 transition-all group"
              >
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white group-hover:text-emerald-400 transition-colors">
                    {job.jobName}
                  </h3>
                  <span className={`px-2 py-1 rounded-full text-[10px] font-semibold border ${getStatusBadge(job.status)}`}>
                    {job.status}
                  </span>
                </div>
                <div className="space-y-2 text-sm text-slate-400 mb-4">
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    <span>{job.propertyAddress}, {job.city}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Hammer className="w-4 h-4" />
                    <span className="capitalize">{job.trade}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <DollarSign className="w-4 h-4" />
                    <span className="text-white font-medium">{job.estimatedPay}</span>
                  </div>
                </div>
                <div className="flex items-center justify-between pt-4 border-t border-white/5">
                  <span className="text-xs text-slate-500">
                    {new Date(job.createdAt).toLocaleDateString()}
                  </span>
                  <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-emerald-400 transition-colors" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Job Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="glass-panel rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col border border-white/10">
            <div className="px-8 py-6 border-b border-white/5 flex items-center justify-between">
              <h2 className="text-2xl font-semibold tracking-tight text-white">Create New Job</h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="w-9 h-9 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center border border-white/10 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateJob} className="flex-1 overflow-y-auto p-8 space-y-6">
              <div>
                <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                  Job Name / Title
                </label>
                <input
                  type="text"
                  required
                  value={formData.jobName}
                  onChange={(e) => setFormData({ ...formData, jobName: e.target.value })}
                  className="w-full glass-input rounded-xl py-3 px-4 text-white text-sm"
                  placeholder="e.g., Master Bathroom Renovation"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                    Property Address
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.propertyAddress}
                    onChange={(e) => setFormData({ ...formData, propertyAddress: e.target.value })}
                    className="w-full glass-input rounded-xl py-3 px-4 text-white text-sm"
                    placeholder="123 Main St"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                    City
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                    className="w-full glass-input rounded-xl py-3 px-4 text-white text-sm"
                    placeholder="Los Angeles"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                    Trade Type
                  </label>
                  <select
                    required
                    value={formData.trade}
                    onChange={(e) => setFormData({ ...formData, trade: e.target.value })}
                    className="w-full glass-input rounded-xl py-3 px-4 text-white text-sm"
                  >
                    <option value="">Select trade...</option>
                    <option value="painting">Painting</option>
                    <option value="plumbing">Plumbing</option>
                    <option value="electrical">Electrical</option>
                    <option value="flooring">Flooring</option>
                    <option value="drywall">Drywall</option>
                    <option value="tiling">Tiling</option>
                    <option value="handyman">Handyman</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                    Estimated Pay
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.estimatedPay}
                    onChange={(e) => setFormData({ ...formData, estimatedPay: e.target.value })}
                    className="w-full glass-input rounded-xl py-3 px-4 text-white text-sm"
                    placeholder="$5,000.00"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                    Scheduled Start Date
                  </label>
                  <input
                    type="date"
                    value={formData.scheduledTime}
                    onChange={(e) => setFormData({ ...formData, scheduledTime: e.target.value })}
                    className="w-full glass-input rounded-xl py-3 px-4 text-white text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                    Square Footage (Optional)
                  </label>
                  <input
                    type="text"
                    value={formData.squareFootage}
                    onChange={(e) => setFormData({ ...formData, squareFootage: e.target.value })}
                    className="w-full glass-input rounded-xl py-3 px-4 text-white text-sm"
                    placeholder="350 sqft"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                  Description / Scope of Work
                </label>
                <textarea
                  required
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full glass-input rounded-xl py-3 px-4 text-white text-sm h-32 resize-none"
                  placeholder="Describe the work to be done in detail..."
                />
              </div>

              <div className="flex gap-4 pt-4 border-t border-white/5">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 py-3 rounded-xl border border-white/10 text-slate-300 text-sm font-medium hover:bg-white/5 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-3 rounded-xl bg-emerald-600 text-white text-sm font-semibold hover:bg-emerald-500 transition-colors"
                >
                  Create Job
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

