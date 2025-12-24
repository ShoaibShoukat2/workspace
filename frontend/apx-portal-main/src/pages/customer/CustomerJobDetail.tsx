import { useParams, useNavigate } from 'react-router-dom';
import { useJobs } from '@/context/JobsContext';
import {
  MapPin,
  Calendar,
  DollarSign,
  Hammer,
  Home,
  ArrowLeft,
  FileText,
} from 'lucide-react';
import '@/styles/customerPortal.css';

export default function CustomerJobDetail() {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const { getJobById } = useJobs();
  const job = jobId ? getJobById(jobId) : undefined;

  if (!job) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-semibold mb-2">Job Not Found</h2>
          <p className="text-slate-400 mb-4">The job you're looking for doesn't exist.</p>
          <button
            onClick={() => navigate('/customer/job-management')}
            className="px-6 py-3 rounded-xl bg-emerald-600 text-white font-semibold hover:bg-emerald-500"
          >
            Back to Jobs
          </button>
        </div>
      </div>
    );
  }

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
    <div className="min-h-screen bg-slate-950 text-white p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <button
          onClick={() => navigate('/customer/job-management')}
          className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors mb-4"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Jobs
        </button>

        <div className="glass-panel p-8 rounded-3xl border border-white/10">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-white mb-2">{job.jobName}</h1>
              <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusBadge(job.status)}`}>
                {job.status}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="flex items-center gap-3 text-sm">
              <MapPin className="w-5 h-5 text-emerald-400" />
              <div>
                <div className="text-slate-400 text-xs uppercase tracking-wider mb-1">Address</div>
                <div className="text-white">{job.propertyAddress}</div>
                <div className="text-slate-400">{job.city}</div>
              </div>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <Hammer className="w-5 h-5 text-emerald-400" />
              <div>
                <div className="text-slate-400 text-xs uppercase tracking-wider mb-1">Trade</div>
                <div className="text-white capitalize">{job.trade}</div>
              </div>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <DollarSign className="w-5 h-5 text-emerald-400" />
              <div>
                <div className="text-slate-400 text-xs uppercase tracking-wider mb-1">Estimated Pay</div>
                <div className="text-white font-semibold text-lg">{job.estimatedPay}</div>
              </div>
            </div>
            {job.scheduledTime && (
              <div className="flex items-center gap-3 text-sm">
                <Calendar className="w-5 h-5 text-emerald-400" />
                <div>
                  <div className="text-slate-400 text-xs uppercase tracking-wider mb-1">Scheduled</div>
                  <div className="text-white">{new Date(job.scheduledTime).toLocaleDateString()}</div>
                </div>
              </div>
            )}
            {job.squareFootage && (
              <div className="flex items-center gap-3 text-sm">
                <Home className="w-5 h-5 text-emerald-400" />
                <div>
                  <div className="text-slate-400 text-xs uppercase tracking-wider mb-1">Square Footage</div>
                  <div className="text-white">{job.squareFootage}</div>
                </div>
              </div>
            )}
          </div>

          <div className="pt-6 border-t border-white/5">
            <div className="flex items-center gap-2 mb-3">
              <FileText className="w-5 h-5 text-emerald-400" />
              <h3 className="text-lg font-semibold text-white">Scope of Work</h3>
            </div>
            <p className="text-slate-300 leading-relaxed">{job.description}</p>
          </div>

          {job.assignedContractorId && (
            <div className="mt-6 pt-6 border-t border-white/5">
              <div className="text-slate-400 text-xs uppercase tracking-wider mb-2">Assigned Contractor</div>
              <div className="text-white">Contractor ID: {job.assignedContractorId}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

