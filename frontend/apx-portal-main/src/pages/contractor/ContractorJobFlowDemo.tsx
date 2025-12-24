import { useMemo, useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useContractorJobs } from '@/context/ContractorJobsContext';
import { useJobs } from '@/context/JobsContext';
import '@/styles/customerPortal.css';
import {
  ArrowRight,
  AlertTriangle,
  Camera,
  Check,
  CheckCircle2,
  FileSignature,
  Flag,
  HelpCircle,
  Home as HomeIcon,
  ImagePlus,
  Info,
  MessageSquare,
  Phone,
  Shield,
  ShieldCheck,
} from 'lucide-react';

type RoleChoice = 'customer' | 'contractor';

export default function ContractorJobFlowDemo() {
  const location = useLocation();
  const navigate = useNavigate();
  const { addCompletedJob } = useContractorJobs();
  const { getJobById, updateContractorProgress, updateJob } = useJobs();
  const autoView = useMemo(() => new URLSearchParams(location.search).get('auto') === '1', [location.search]);
  const jobId = useMemo(() => new URLSearchParams(location.search).get('jobId'), [location.search]);
  const job = jobId ? getJobById(jobId) : null;

  const [currentRole, setCurrentRole] = useState<RoleChoice>('contractor');
  const [view, setView] = useState<'login' | 'customer' | 'contractor'>(autoView ? 'contractor' : 'login');
  const [acknowledged, setAcknowledged] = useState(false);
  const [step, setStep] = useState<1 | 2 | 3 | 4 | 5>(1);

  // Load saved progress on mount
  useEffect(() => {
    if (job?.contractorProgress) {
      setStep(job.contractorProgress.currentStep);
      setAcknowledged(job.contractorProgress.acknowledged);
    }
  }, [job]);

  // Save progress when step or acknowledged changes
  useEffect(() => {
    if (jobId && view === 'contractor' && step >= 1) {
      updateContractorProgress(jobId, {
        currentStep: step,
        acknowledged,
        lastUpdated: new Date().toISOString(),
      });
    }
  }, [step, acknowledged, jobId, view, updateContractorProgress]);

  const handleEnter = () => {
    if (currentRole === 'contractor') {
      setView('contractor');
      setStep(1);
    } else {
      setView('customer');
    }
  };

  const goToStep = (next: 1 | 2 | 3 | 4 | 5) => {
    setStep(next);
    if (jobId) {
      updateContractorProgress(jobId, {
        currentStep: next,
        acknowledged,
        lastUpdated: new Date().toISOString(),
      });
    }
  };

  const stepTitle = ['Acknowledgment', 'Walkthrough', 'Quote', 'Progress', 'Completion'][step - 1];

  return (
    <div className="min-h-screen w-full bg-slate-950 text-white flex flex-col">
      {/* LOGIN / ROLE SELECTION VIEW */}
      {view === 'login' && (
        <div className="flex flex-1 w-full bg-slate-950">
          {/* Left hero */}
          <div className="hidden lg:flex lg:w-3/5 relative overflow-hidden">
            <div
              className="absolute inset-0 bg-cover bg-center opacity-40"
              style={{
                backgroundImage:
                  "url('https://images.unsplash.com/photo-1600607686527-6fb886090705?q=80&w=2700&auto=format&fit=crop')",
              }}
            />
            <div className="absolute inset-0 bg-gradient-to-r from-slate-950 via-slate-950/80 to-transparent" />
            <div className="relative z-10 p-20 flex flex-col justify-between h-full">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-[0_0_30px_rgba(16,185,129,0.3)]">
                  <HomeIcon className="text-white w-6 h-6 stroke-[2]" />
                </div>
                <span className="text-3xl font-bold tracking-tight text-white">Apex</span>
              </div>
              <div className="max-w-2xl">
                <h1 className="text-6xl font-medium text-white leading-[1.1] tracking-tight mb-8">
                  The operating system for <br />
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-300">
                    modern craftsmanship
                  </span>
                  .
                </h1>
              </div>
              <p className="text-xs text-slate-600 tracking-widest uppercase">© 2025 APEX INC.</p>
            </div>
          </div>

          {/* Right auth panel */}
          <div className="w-full lg:w-2/5 flex items-center justify-center relative bg-slate-950">
            <div className="pointer-events-none absolute inset-0 bg-grid-pattern opacity-[0.03]" />
            <div className="w-full max-w-sm p-8 z-10 animate-enter">
              <div className="mb-10">
                <h2 className="text-3xl font-semibold text-white tracking-tight mb-2">Welcome Pro</h2>
                <p className="text-slate-500 font-light">Access your job cockpit.</p>
              </div>

              {/* Role toggle */}
              <div className="grid grid-cols-2 gap-2 mb-8 p-1 bg-white/5 rounded-xl border border-white/5">
                <button
                  type="button"
                  onClick={() => setCurrentRole('customer')}
                  className={
                    currentRole === 'customer'
                      ? 'py-3 px-4 rounded-lg text-xs font-medium transition-all bg-emerald-600 text-white shadow-lg shadow-emerald-500/20'
                      : 'py-3 px-4 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition-all hover:bg-white/5'
                  }
                >
                  Homeowner
                </button>
                <button
                  type="button"
                  onClick={() => setCurrentRole('contractor')}
                  className={
                    currentRole === 'contractor'
                      ? 'py-3 px-4 rounded-lg text-xs font-medium transition-all bg-emerald-600 text-white shadow-lg shadow-emerald-500/20'
                      : 'py-3 px-4 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition-all hover:bg-white/5'
                  }
                >
                  Contractor Pro
                </button>
              </div>

              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleEnter();
                }}
                className="space-y-6"
              >
                <div className="space-y-2">
                  <label className="text-[10px] font-medium text-slate-400 uppercase tracking-wider">
                    Email Address
                  </label>
                  <input
                    type="email"
                    defaultValue="pro@apex.inc"
                    className="w-full glass-input rounded-xl py-4 px-4 text-white placeholder-slate-600 focus:outline-none transition-all font-light"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full bg-slate-800 hover:bg-emerald-600 text-white font-medium py-4 rounded-xl transition-all border border-white/10 hover:border-emerald-500 flex items-center justify-center gap-2 group"
                >
                  <span>{currentRole === 'contractor' ? 'Enter Job Flow' : 'View Customer Placeholder'}</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* CUSTOMER PLACEHOLDER VIEW */}
      {view === 'customer' && (
        <div className="flex flex-1 h-screen w-full bg-slate-950 items-center justify-center text-slate-500">
          <div className="text-center px-6">
            <h2 className="text-2xl text-white mb-2">Customer View</h2>
            <p>Please reload and select &quot;Contractor Pro&quot; to view the requested design.</p>
          </div>
        </div>
      )}

      {/* CONTRACTOR JOB FLOW VIEW */}
      {view === 'contractor' && (
        <div className="flex flex-1 h-screen w-full relative bg-slate-950 text-white overflow-hidden">
          {/* Sidebar */}
          <aside className="w-72 border-r border-white/5 flex flex-col bg-[#050508] z-30 shrink-0">
            <div className="h-20 flex items-center px-8 border-b border-white/5">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-500/20">
                  <ShieldCheck className="text-white w-4 h-4" />
                </div>
                <span className="text-lg font-bold tracking-tight text-white">Apex Pro</span>
              </div>
            </div>

            <div className="p-6">
              <div className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest mb-4">
                Job Execution Sequence
              </div>

              <div className="space-y-1 relative">
                <div className="absolute left-[19px] top-6 bottom-6 w-px bg-white/10 -z-10" />

                {[1, 2, 3, 4, 5].map((i) => {
                  const isPast = i < step;
                  const isActive = i === step;
                  const titles = [
                    'Start Acknowledgment',
                    'Site Walkthrough',
                    'Quote Summary',
                    'Progress & Timeline',
                    'Completion & Delivery',
                  ];
                  if (isPast) {
                    return (
                      <div
                        key={i}
                        className="step-nav-item flex items-center gap-4 p-3 rounded-xl cursor-default"
                      >
                        <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-500 flex items-center justify-center relative z-10 border border-emerald-500/30">
                          <Check className="w-3.5 h-3.5" />
                        </div>
                        <div>
                          <div className="text-xs font-medium text-slate-300 opacity-60">Step {i}</div>
                          <div className="text-[10px] text-emerald-500">Completed</div>
                        </div>
                      </div>
                    );
                  }
                  if (isActive) {
                    return (
                      <div
                        key={i}
                        className="step-nav-item active flex items-center gap-4 p-3 rounded-xl bg-white/5 border border-white/10 shadow-lg cursor-default"
                      >
                        <div className="w-6 h-6 rounded-full bg-emerald-500 text-slate-950 flex items-center justify-center relative z-10 shadow-[0_0_10px_rgba(16,185,129,0.4)]">
                          <span className="font-bold text-[10px]">{i}</span>
                        </div>
                        <div>
                          <div className="text-xs font-semibold text-white">{titles[i - 1]}</div>
                          <div className="text-[10px] text-emerald-400">Current Step</div>
                        </div>
                      </div>
                    );
                  }
                  return (
                    <div
                      key={i}
                      className="step-nav-item flex items-center gap-4 p-3 rounded-xl opacity-40 grayscale cursor-default"
                    >
                      <div className="w-6 h-6 rounded-full bg-slate-800 border border-white/20 flex items-center justify-center relative z-10">
                        <span className="text-[10px] font-mono">{i}</span>
                      </div>
                      <div>
                        <div className="text-xs font-medium text-slate-300">Step {i}</div>
                        <div className="text-[10px] text-slate-500">Locked</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="mt-auto p-6 border-t border-white/5">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg border border-white/10 bg-slate-800" />
                <div className="overflow-hidden">
                  <div className="text-xs font-semibold text-white">Mike Ross</div>
                  <div className="text-[10px] text-slate-500">Apex Certified Pro</div>
                </div>
              </div>
            </div>
          </aside>

          {/* Main content */}
          <main className="flex-1 flex flex-col relative bg-grid-pattern h-full overflow-hidden">
            {/* Header */}
            <header className="h-20 shrink-0 flex items-center justify-between px-8 lg:px-12 border-b border-white/5 bg-slate-950/80 backdrop-blur-md z-20">
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-lg font-semibold tracking-tight text-white">Master Bath Renovation</h2>
                  <span className="px-2 py-0.5 rounded border border-white/10 bg-white/5 text-[10px] font-mono text-slate-400">
                    #BR-2847
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">Customer: Sarah Johnson • 1248 Highland Ave</p>
              </div>
              <div className="flex items-center gap-3">
                <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-white/10 bg-white/5 text-xs text-slate-300 hover:text-white transition-colors">
                  <Phone className="w-3.5 h-3.5" /> Contact
                </button>
                <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-white/10 bg-white/5 text-xs text-slate-300 hover:text-white transition-colors">
                  <HelpCircle className="w-3.5 h-3.5" /> Support
                </button>
              </div>
            </header>

            {/* Steps container */}
            <div className="flex-1 overflow-y-auto scroll-smooth p-8 lg:p-12 relative">
              {/* STEP 1 */}
              {step === 1 && (
                <div className="max-w-4xl mx-auto space-y-8 animate-enter">
                  <div className="text-center mb-10">
                    <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center shadow-[0_0_40px_rgba(79,70,229,0.3)] mb-6">
                      <FileSignature className="w-8 h-8 text-white" />
                    </div>
                    <h1 className="text-3xl font-semibold text-white tracking-tight mb-2">
                      Job Start Acknowledgment
                    </h1>
                    <p className="text-slate-400 max-w-lg mx-auto">
                      Before proceeding, you must review and agree to the platform standards for this specific job
                      type.
                    </p>
                  </div>

                  <div className="grid gap-4">
                    <div className="glass-panel p-6 rounded-2xl border-l-4 border-l-blue-500">
                      <h3 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
                        <MessageSquare className="w-4 h-4 text-blue-400" /> Professional Communication
                      </h3>
                      <ul className="space-y-2 ml-6 list-disc text-xs text-slate-400 marker:text-blue-500">
                        <li>Respond to customer messages within 2 hours during business hours.</li>
                        <li>Provide daily progress updates with at least 2 photos.</li>
                        <li>All scope changes must be documented in-app.</li>
                      </ul>
                    </div>

                    <div className="glass-panel p-6 rounded-2xl border-l-4 border-l-emerald-500">
                      <h3 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
                        <Shield className="w-4 h-4 text-emerald-400" /> Quality &amp; Safety Standards
                      </h3>
                      <ul className="space-y-2 ml-6 list-disc text-xs text-slate-400 marker:text-emerald-500">
                        <li>Follow all local building codes and safety regulations.</li>
                        <li>Maintain a clean and organized work site daily.</li>
                        <li>Use materials as specified in the approved quote only.</li>
                      </ul>
                    </div>

                    <div className="glass-panel p-6 rounded-2xl border-l-4 border-l-amber-500">
                      <h3 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
                        <Camera className="w-4 h-4 text-amber-400" /> Documentation Requirements
                      </h3>
                      <ul className="space-y-2 ml-6 list-disc text-xs text-slate-400 marker:text-amber-500">
                        <li>Mandatory walkthrough photos before touching tools.</li>
                        <li>Milestone photos at 25%, 50%, 75%, and 100%.</li>
                        <li>Final verification checklist required for payment release.</li>
                      </ul>
                    </div>
                  </div>

                  <div className="glass-panel p-6 rounded-2xl border border-white/10 mt-8 flex flex-col md:flex-row items-center gap-6 bg-emerald-900/10">
                    <label className="flex items-start gap-4 cursor-pointer group">
                      <div className="relative flex items-center">
                        <input
                          type="checkbox"
                          checked={acknowledged}
                          onChange={(e) => setAcknowledged(e.target.checked)}
                          className="peer h-6 w-6 cursor-pointer appearance-none rounded-lg border border-white/30 bg-white/5 checked:border-emerald-500 checked:bg-emerald-500 transition-all"
                        />
                        <Check className="pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 text-white opacity-0 peer-checked:opacity-100 transition-opacity" />
                      </div>
                      <div>
                        <div className="text-sm font-medium text-white group-hover:text-emerald-400 transition-colors">
                          I acknowledge and agree to all platform standards.
                        </div>
                        <div className="text-xs text-slate-500 mt-1">
                          By clicking, you accept liability for adherence to these terms.
                        </div>
                      </div>
                    </label>

                    <button
                      type="button"
                      disabled={!acknowledged}
                      onClick={() => goToStep(2)}
                      className="w-full md:w-auto md:ml-auto px-8 py-3 rounded-xl bg-slate-800 text-slate-500 font-semibold text-sm transition-all disabled:cursor-not-allowed disabled:opacity-50 hover:bg-emerald-600 hover:text-white hover:shadow-[0_0_20px_rgba(16,185,129,0.4)] flex items-center justify-center gap-2"
                    >
                      Begin Job <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}

              {/* STEP 2 (static layout demo) */}
              {step === 2 && (
                <div className="max-w-5xl mx-auto space-y-6 slide-enter">
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h2 className="text-2xl font-semibold text-white tracking-tight">Site Walkthrough</h2>
                      <p className="text-slate-400 text-xs mt-1">Document ground truth before starting work.</p>
                    </div>
                    <div className="text-right">
                      <div className="text-[10px] font-bold text-amber-500 uppercase tracking-widest animate-pulse">
                        Walkthrough In Progress
                      </div>
                      <div className="text-xs text-slate-500">Step 2 of 5</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
                    <div className="md:col-span-8 space-y-6">
                      <div className="glass-panel p-6 rounded-2xl">
                        <h3 className="text-sm font-semibold text-white mb-4 flex justify-between">
                          <span>A. Site Photos</span>
                          <span className="text-xs text-slate-500 font-normal">0/12 Uploaded</span>
                        </h3>
                        <div className="border-2 border-dashed border-white/10 rounded-xl bg-white/5 p-8 text-center hover:border-emerald-500/50 hover:bg-white/10 transition-all cursor-pointer group">
                          <div className="w-12 h-12 rounded-full bg-slate-800 mx-auto flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                            <Camera className="w-5 h-5 text-slate-400 group-hover:text-emerald-400 transition-colors" />
                          </div>
                          <div className="text-sm font-medium text-slate-300">Tap to upload site photos</div>
                          <div className="text-xs text-slate-600 mt-1">
                            Capture all angles, existing damage, and access routes
                          </div>
                        </div>
                        <div className="flex gap-3 mt-4 overflow-x-auto pb-2">
                          <div className="w-20 h-20 shrink-0 rounded-lg bg-slate-800 border border-white/5" />
                          <div className="w-20 h-20 shrink-0 rounded-lg bg-slate-800 border border-white/5" />
                          <div className="w-20 h-20 shrink-0 rounded-lg bg-slate-800 border border-white/5" />
                        </div>
                      </div>

                      <div className="glass-panel p-6 rounded-2xl">
                        <h3 className="text-sm font-semibold text-white mb-4">E. Scope of Work Summary</h3>
                        <textarea
                          className="w-full h-32 bg-slate-900/50 border border-white/10 rounded-xl p-4 text-slate-300 text-xs focus:border-emerald-500/50 focus:outline-none transition-colors resize-none"
                          placeholder="Describe the work to be done in detail..."
                        />
                      </div>
                    </div>

                    <div className="md:col-span-4 space-y-6">
                      <div className="glass-panel p-6 rounded-2xl">
                        <h3 className="text-sm font-semibold text-white mb-4">B. Measurements</h3>
                        <div className="space-y-3">
                          {['Room Width', 'Room Length', 'Ceiling Height'].map((label) => (
                            <div key={label}>
                              <label className="text-[10px] text-slate-500 uppercase tracking-wider mb-1 block">
                                {label}
                              </label>
                              <div className="relative">
                                <input
                                  type="text"
                                  className="w-full glass-input rounded-lg py-2 px-3 text-white text-sm"
                                  placeholder="0"
                                />
                                <span className="absolute right-3 top-2.5 text-xs text-slate-600">ft</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="glass-panel p-6 rounded-2xl">
                        <h3 className="text-sm font-semibold text-white mb-4">C. Observations</h3>
                        <div className="flex items-start gap-2 mb-3">
                          <input type="checkbox" className="mt-1 bg-white/5 border-white/20 rounded" />
                          <span className="text-xs text-slate-400">Pre-existing damage visible</span>
                        </div>
                        <div className="flex items-start gap-2 mb-3">
                          <input type="checkbox" className="mt-1 bg-white/5 border-white/20 rounded" />
                          <span className="text-xs text-slate-400">Plumbing access verified</span>
                        </div>
                        <div className="flex items-start gap-2">
                          <input type="checkbox" className="mt-1 bg-white/5 border-white/20 rounded" />
                          <span className="text-xs text-slate-400">Electrical panel accessible</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-end pt-4 border-t border-white/5">
                    <button
                      type="button"
                      onClick={() => goToStep(3)}
                      className="px-8 py-3 rounded-xl bg-emerald-600 text-white font-semibold text-sm hover:bg-emerald-500 transition-all shadow-lg shadow-emerald-900/20 flex items-center gap-2"
                    >
                      Continue to Quote <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}

              {/* STEP 3 */}
              {step === 3 && (
                <div className="max-w-2xl mx-auto space-y-8 slide-enter">
                  <div className="text-center mb-8">
                    <h2 className="text-2xl font-semibold text-white tracking-tight">System Quote Summary</h2>
                    <p className="text-slate-400 text-xs mt-1">Review the system-generated labor calculation.</p>
                  </div>

                  <div className="glass-panel border-t-4 border-t-indigo-500 rounded-2xl overflow-hidden shadow-2xl">
                    <div className="p-8 pb-4">
                      <div className="flex justify-between items-start mb-8">
                        <div>
                          <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">
                            Total Labor Estimate
                          </div>
                          <div className="text-5xl font-light text-white tracking-tighter">
                            $12,450
                            <span className="text-2xl text-slate-500 font-thin">.00</span>
                          </div>
                        </div>
                        <div className="px-3 py-1 bg-indigo-500/10 text-indigo-400 text-[10px] font-bold uppercase rounded border border-indigo-500/20">
                          Labor Only
                        </div>
                      </div>

                      <div className="space-y-4">
                        <div className="flex justify-between text-sm py-3 border-b border-white/5">
                          <span className="text-slate-400">Est. Duration</span>
                          <span className="text-white font-medium">14 Days</span>
                        </div>
                        <div className="flex justify-between text-sm py-3 border-b border-white/5">
                          <span className="text-slate-400">Scope Complexity</span>
                          <span className="text-white font-medium">High</span>
                        </div>
                        <div className="flex justify-between text-sm py-3 border-b border-white/5">
                          <span className="text-slate-400">Platform Fee (5%)</span>
                          <span className="text-slate-300 font-medium">-$622.50</span>
                        </div>
                      </div>
                    </div>
                    <div className="bg-amber-900/10 border-t border-amber-500/20 p-4 flex items-start gap-3">
                      <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0" />
                      <p className="text-xs text-amber-200/80 leading-relaxed">
                        <strong className="text-amber-500 block mb-1">Important: Materials Not Included</strong>
                        This quote covers labor only. You are responsible for sourcing materials based on the allowance
                        provided in the Material Schedule.
                      </p>
                    </div>
                    <div className="p-6 bg-white/5 flex gap-4">
                      <button className="flex-1 py-3 rounded-xl border border-white/10 text-slate-300 text-xs font-medium hover:bg-white/5">
                        Request Adjustment
                      </button>
                      <button
                        type="button"
                        onClick={() => goToStep(4)}
                        className="flex-1 py-3 rounded-xl bg-indigo-600 text-white text-xs font-bold uppercase tracking-wider hover:bg-indigo-500 shadow-lg shadow-indigo-500/20"
                      >
                        Proceed to Execution
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 4 */}
              {step === 4 && (
                <div className="max-w-5xl mx-auto space-y-8 slide-enter">
                  <div className="glass-panel p-8 rounded-3xl relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-r from-emerald-900/20 to-transparent" />
                    <div className="relative z-10">
                      <div className="flex justify-between items-end mb-6">
                        <div>
                          <div className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest mb-2">
                            Project Active
                          </div>
                          <h2 className="text-3xl font-light text-white tracking-tight">Progress Timeline</h2>
                        </div>
                        <div className="text-right">
                          <div className="text-3xl font-mono text-white">25%</div>
                          <div className="text-xs text-slate-500">Current Milestone</div>
                        </div>
                      </div>

                      <div className="relative mt-8 mb-4">
                        <div className="absolute top-1/2 left-0 w-full h-1 bg-white/10 -translate-y-1/2 rounded-full" />
                        <div className="absolute top-1/2 left-0 w-1/4 h-1 bg-emerald-500 -translate-y-1/2 rounded-full shadow-[0_0_15px_rgba(16,185,129,0.5)]" />

                        <div className="flex justify-between relative z-10">
                          <div className="flex flex-col items-center gap-2 group cursor-pointer">
                            <div className="w-8 h-8 rounded-full bg-emerald-500 border-4 border-slate-950 flex items-center justify-center text-slate-950 shadow-lg shadow-emerald-500/20">
                              <Check className="w-3 h-3" />
                            </div>
                            <span className="text-[10px] font-bold text-emerald-500 uppercase">Start</span>
                          </div>
                          <div className="flex flex-col items-center gap-2">
                            <div className="w-8 h-8 rounded-full bg-slate-900 border-2 border-emerald-500 flex items-center justify-center relative">
                              <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
                            </div>
                            <span className="text-[10px] font-bold text-white uppercase">Demolition</span>
                          </div>
                          <div className="flex flex-col items-center gap-2 opacity-40">
                            <div className="w-8 h-8 rounded-full bg-slate-900 border-2 border-slate-700 flex items-center justify-center" />
                            <span className="text-[10px] font-bold text-slate-400 uppercase">Rough-in</span>
                          </div>
                          <div className="flex flex-col items-center gap-2 opacity-40">
                            <div className="w-8 h-8 rounded-full bg-slate-900 border-2 border-slate-700 flex items-center justify-center" />
                            <span className="text-[10px] font-bold text-slate-400 uppercase">Install</span>
                          </div>
                          <div className="flex flex-col items-center gap-2 opacity-40">
                            <div className="w-8 h-8 rounded-full bg-slate-900 border-2 border-slate-700 flex items-center justify-center">
                              <Flag className="w-3 h-3 text-slate-500" />
                            </div>
                            <span className="text-[10px] font-bold text-slate-400 uppercase">Finish</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="glass-panel p-6 rounded-2xl">
                      <h3 className="text-sm font-semibold text-white mb-4">Milestone Tasks</h3>
                      <div className="space-y-3">
                        {[
                          'Remove existing vanity and tile',
                          'Dispose of debris',
                          'Verify subfloor integrity',
                        ].map((label) => (
                          <label
                            key={label}
                            className="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-white/5 hover:border-emerald-500/30 transition-all cursor-pointer"
                          >
                            <input
                              type="checkbox"
                              className="w-4 h-4 rounded border-white/20 bg-transparent text-emerald-500 focus:ring-0"
                            />
                            <span className="text-xs text-slate-300">{label}</span>
                          </label>
                        ))}
                      </div>
                    </div>

                    <div className="glass-panel p-6 rounded-2xl">
                      <h3 className="text-sm font-semibold text-white mb-4">Progress Documentation</h3>
                      <div className="h-32 border-2 border-dashed border-white/10 rounded-xl flex flex-col items-center justify-center text-center cursor-pointer hover:bg-white/5 transition-all">
                        <ImagePlus className="w-6 h-6 text-slate-500 mb-2" />
                        <span className="text-xs text-slate-400">Upload 4+ photos to unlock</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => goToStep(5)}
                        className="w-full mt-4 py-3 rounded-xl bg-emerald-600 text-white text-xs font-bold uppercase hover:bg-emerald-500 transition-colors"
                      >
                        Submit Milestone Review
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 5 */}
              {step === 5 && (
                <div className="max-w-3xl mx-auto space-y-8 slide-enter">
                  <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 mb-4">
                      <CheckCircle2 className="w-6 h-6" />
                    </div>
                    <h2 className="text-2xl font-semibold text-white tracking-tight">Project Completion</h2>
                    <p className="text-slate-400 text-xs mt-1">Final verification and handover.</p>
                  </div>

                  <div className="glass-panel p-8 rounded-3xl border border-emerald-500/30">
                    <h3 className="text-sm font-bold text-white uppercase tracking-widest mb-6 border-b border-white/5 pb-4">
                      Verification Checklist
                    </h3>

                    <div className="space-y-6">
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 mb-3">Installation Quality</h4>
                        <div className="space-y-2">
                          <label className="flex items-center gap-3 text-sm text-white">
                            <input
                              type="checkbox"
                              className="text-emerald-500 rounded bg-white/5 border-white/20"
                            />{' '}
                            All fixtures installed and tested
                          </label>
                          <label className="flex items-center gap-3 text-sm text-white">
                            <input
                              type="checkbox"
                              className="text-emerald-500 rounded bg-white/5 border-white/20"
                            />{' '}
                            Grout sealed and cured
                          </label>
                        </div>
                      </div>
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 mb-3">Site Cleanup</h4>
                        <div className="space-y-2">
                          <label className="flex items-center gap-3 text-sm text-white">
                            <input
                              type="checkbox"
                              className="text-emerald-500 rounded bg-white/5 border-white/20"
                            />{' '}
                            All debris removed from premises
                          </label>
                          <label className="flex items-center gap-3 text-sm text-white">
                            <input
                              type="checkbox"
                              className="text-emerald-500 rounded bg-white/5 border-white/20"
                            />{' '}
                            Surfaces dusted and wiped
                          </label>
                        </div>
                      </div>
                    </div>

                    <div className="mt-8 pt-6 border-t border-white/5">
                      <div className="flex items-start gap-3 bg-blue-900/10 p-4 rounded-xl mb-6">
                        <Info className="w-5 h-5 text-blue-400 shrink-0" />
                        <p className="text-xs text-blue-200/80">
                          Payment will be automatically released 24 hours after the customer confirms receipt of this
                          completion report and rates the project.
                        </p>
                      </div>

                      <button
                        type="button"
                        onClick={async () => {
                          if (job) {
                            try {
                              // Mark job as complete
                              await updateJob(job.id, { status: 'Complete' });
                              // Add to completed jobs
                              addCompletedJob({
                                id: job.id,
                                jobName: job.jobName,
                                customerName: job.customerName,
                                address: `${job.propertyAddress}, ${job.city}`,
                                completedDate: new Date().toLocaleDateString('en-US', {
                                  month: 'short',
                                  day: 'numeric',
                                  year: 'numeric',
                                }),
                                estimatedPay: job.estimatedPay,
                                description: job.description,
                              });
                              // Navigate back to contractor portal
                              navigate('/contractor/portal');
                            } catch (error: any) {
                              console.error('Failed to complete job:', error);
                              alert(`Failed to submit report: ${error.message || 'Unknown error'}`);
                            }
                          }
                        }}
                        className="w-full py-4 rounded-xl bg-white text-slate-950 font-bold hover:bg-slate-200 transition-colors flex items-center justify-center gap-2"
                      >
                        <ArrowRight className="w-4 h-4" /> Submit Final Report
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </main>
        </div>
      )}
    </div>
  );
}


