import { useState } from 'react';
import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LayoutGrid,
  Briefcase,
  ShieldCheck,
  Wallet,
  Search,
  Bell,
  HelpCircle,
  CheckCircle,
  DollarSign,
  TrendingUp,
  Info,
  MapPin,
  User,
  Calendar,
  Home,
  SlidersHorizontal,
  ChevronRight,
  ChevronDown,
  Download,
  MessageSquare,
  Triangle,
  FileText,
  Shield,
  Clock,
  CreditCard,
  X,
} from 'lucide-react';
import { useContractorJobs } from '@/context/ContractorJobsContext';
import { useJobs } from '@/context/JobsContext';
import { useAuth } from '@/context/AuthContext';
import '@/styles/customerPortal.css';

type TabId = 'dashboard' | 'compliance' | 'jobs' | 'wallet';

export default function ContractorPortal() {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const { completedJobs, completedJobsCount } = useContractorJobs();
  const { getAvailableJobs, getJobsByContractor, assignContractor, refreshJobs } = useJobs();
  const [activeTab, setActiveTab] = useState<TabId>('dashboard');
  const [showCompletedJobs, setShowCompletedJobs] = useState(false);

  // Refresh jobs when component mounts or when switching tabs
  React.useEffect(() => {
    refreshJobs();
  }, [refreshJobs]);

  const switchTab = (tabId: TabId) => {
    setActiveTab(tabId);
    refreshJobs(); // Refresh jobs when switching tabs
  };

  // Get jobs - using jobs array directly ensures reactivity to API changes
  const availableJobs = getAvailableJobs(currentUser?.trade);
  // Active Projects only shows jobs that have been started (status = 'InProgress')
  // Use profileID or id for contractor lookup
  const contractorId = (currentUser as any)?.profileID || (currentUser as any)?.id || currentUser?.id;
  const activeJobs = contractorId ? getJobsByContractor(contractorId).filter(j => j.status === 'InProgress') : [];

  const handleAcceptJob = async (jobId: string) => {
    const contractorId = (currentUser as any)?.profileID || (currentUser as any)?.id || currentUser?.id;
    if (contractorId) {
      try {
        await assignContractor(jobId, contractorId);
        navigate(`/contractor/job-flow-demo?auto=1&jobId=${jobId}`);
      } catch (error: any) {
        console.error('Failed to assign job:', error);
        alert(`Failed to accept job: ${error.message || 'Unknown error'}`);
      }
    }
  };

  const handleResumeJob = (jobId: string) => {
    navigate(`/contractor/job-flow-demo?auto=1&jobId=${jobId}`);
  };

  const pageTitles: Record<TabId, string> = {
    dashboard: 'Dashboard',
    compliance: 'Compliance Hub',
    jobs: 'Job Board',
    wallet: 'Wallet & Payouts',
  };

  return (
    <div className="min-h-screen flex text-sm antialiased font-sans selection:bg-emerald-500/30 selection:text-emerald-200 bg-[#05060A] text-[#E2E8F0]">
      {/* Background Grid Effect */}
      <div className="fixed inset-0 bg-grid pointer-events-none z-0" />
      <div className="fixed inset-0 bg-gradient-to-b from-transparent via-[#05060A]/80 to-[#05060A] pointer-events-none z-0" />

      {/* SIDEBAR */}
      <aside className="w-64 fixed h-screen z-50 border-r border-white/5 bg-[#08090F]/90 backdrop-blur-xl flex flex-col justify-between">
        <div>
          {/* Logo */}
          <div className="h-16 flex items-center px-6 border-b border-white/5">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center shadow-[0_0_20px_-5px_rgba(16,185,129,0.4)]">
                <Triangle className="text-white fill-current w-4 h-4 transform rotate-180" />
              </div>
              <span className="text-lg font-semibold tracking-tight text-white">Apex</span>
            </div>
          </div>

          {/* Workflow Nav */}
          <div className="p-4 space-y-1">
            <div className="px-3 py-2 text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">
              Workspace
            </div>

            <button
              onClick={() => switchTab('dashboard')}
              className={`nav-item w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all group ${
                activeTab === 'dashboard'
                  ? 'active bg-emerald-500/10 text-emerald-400 border-l-2 border-emerald-500'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <LayoutGrid className="w-4 h-4 transition-colors" />
              <span>Dashboard</span>
            </button>

            <button
              onClick={() => switchTab('jobs')}
              className={`nav-item w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all group ${
                activeTab === 'jobs'
                  ? 'active bg-emerald-500/10 text-emerald-400 border-l-2 border-emerald-500'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Briefcase className="w-4 h-4 transition-colors" />
              <span>Job Board</span>
              <span className="ml-auto bg-emerald-500/10 text-emerald-400 text-xs px-2 py-0.5 rounded-full border border-emerald-500/20">
                3 New
              </span>
            </button>

            <button
              onClick={() => switchTab('compliance')}
              className={`nav-item w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all group ${
                activeTab === 'compliance'
                  ? 'active bg-emerald-500/10 text-emerald-400 border-l-2 border-emerald-500'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <ShieldCheck className="w-4 h-4 transition-colors" />
              <span>Compliance Hub</span>
              <div className="ml-auto w-1.5 h-1.5 rounded-full bg-amber-500 shadow-[0_0_10px_-2px_rgba(16,185,129,0.3)]" />
            </button>

            <button
              onClick={() => switchTab('wallet')}
              className={`nav-item w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all group ${
                activeTab === 'wallet'
                  ? 'active bg-emerald-500/10 text-emerald-400 border-l-2 border-emerald-500'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Wallet className="w-4 h-4 transition-colors" />
              <span>Wallet & Payouts</span>
            </button>
          </div>

          <div className="px-4 py-4">
            <div className="border-t border-white/5 pt-4 space-y-1">
              <div className="px-3 py-2 text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">
                Projects
              </div>
              <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-all text-xs">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_10px_-2px_rgba(16,185,129,0.3)]" />
                Highland Kitchen
              </button>
              <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-all text-xs">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                Venice Bath Remodel
              </button>
            </div>
          </div>
        </div>

        {/* User Profile */}
        <div className="p-4 border-t border-white/5">
          <button className="flex items-center gap-3 w-full p-2 rounded-xl hover:bg-white/5 transition-colors">
            <img
              src="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
              alt="User"
              className="w-9 h-9 rounded-full border border-white/10"
            />
            <div className="text-left">
              <div className="text-xs font-medium text-white">Cory Anderson</div>
              <div className="text-[10px] text-emerald-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" /> Available
              </div>
            </div>
            <ChevronRight className="w-4 h-4 ml-auto text-slate-500" />
          </button>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="ml-64 flex-1 relative z-10 flex flex-col h-screen">
        {/* TOP HEADER */}
        <header className="h-16 border-b border-white/5 glass-panel sticky top-0 z-40 flex items-center justify-between px-8 backdrop-blur-md">
          {/* Left: Breadcrumbs / Context */}
          <div className="flex items-center gap-4">
            <div className="flex items-center text-slate-400 text-xs">
              <span className="hover:text-white cursor-pointer transition-colors">Contractor Portal</span>
              <ChevronRight className="w-3 h-3 mx-2 text-slate-600" />
              <span className="text-white font-medium">{pageTitles[activeTab]}</span>
            </div>
          </div>

          {/* Center: Search */}
          <div className="relative w-96 hidden md:block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search for jobs, reports, or settings..."
              className="w-full pl-10 pr-4 py-2 rounded-full glass-input text-xs placeholder:text-slate-600"
            />
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-3">
            <button className="w-9 h-9 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center border border-white/5 transition-all text-slate-400 hover:text-white">
              <Bell className="w-4 h-4" />
            </button>
            <button className="w-9 h-9 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center border border-white/5 transition-all text-slate-400 hover:text-white">
              <HelpCircle className="w-4 h-4" />
            </button>
            <div className="h-6 w-[1px] bg-white/10 mx-1" />
            <button className="px-3 py-1.5 rounded-full bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 text-xs font-medium border border-emerald-500/20 transition-all">
              Pro Member
            </button>
          </div>
        </header>

        {/* SCROLLABLE CONTENT */}
        <div className="flex-1 overflow-y-auto p-8 relative">
          {/* SECTION A: DASHBOARD */}
          {activeTab === 'dashboard' && (
            <div className="fade-in max-w-6xl mx-auto space-y-8">
              {/* Welcome & KPI Row */}
              <div className="flex flex-col md:flex-row gap-6">
                <div className="flex-1">
                  <h1 className="text-2xl font-semibold tracking-tight text-white mb-1">Good morning, Cory</h1>
                  <p className="text-slate-400 text-sm mb-6">Here is an overview of your projects today.</p>

                  {/* KPI Cards Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Completed Jobs KPI */}
                    <button
                      onClick={() => setShowCompletedJobs(true)}
                      className="glass-card p-5 rounded-2xl relative overflow-hidden group hover:bg-white/[0.02] transition-colors w-full text-left cursor-pointer"
                    >
                      <div className="flex justify-between items-start mb-4">
                        <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                          <CheckCircle className="w-4 h-4 text-emerald-400" />
                        </div>
                        <span className="text-xs font-medium text-emerald-400 bg-emerald-500/5 px-2 py-1 rounded-full">
                          {completedJobsCount > 0 ? `+${completedJobsCount} this session` : 'No jobs yet'}
                        </span>
                      </div>
                      <div className="text-3xl font-semibold text-white tracking-tight mb-1">
                        {completedJobsCount || 0}
                      </div>
                      <div className="text-xs text-slate-400 flex items-center justify-between">
                        <span>Completed Jobs</span>
                        {completedJobsCount > 0 && (
                          <ChevronRight className="w-3 h-3 text-slate-500 group-hover:text-emerald-400 transition-colors" />
                        )}
                      </div>
                    </button>

                    {/* Pending Payouts KPI */}
                    <div className="glass-card p-5 rounded-2xl relative overflow-hidden group hover:bg-white/[0.02] transition-colors">
                      <div className="flex justify-between items-start mb-4">
                        <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20">
                          <DollarSign className="w-4 h-4 text-blue-400" />
                        </div>
                        <button className="text-xs font-medium text-slate-300 hover:text-white flex items-center gap-1 transition-colors">
                          Details <ChevronRight className="w-3 h-3" />
                        </button>
                      </div>
                      <div className="text-3xl font-semibold text-white tracking-tight mb-1">$3,450.00</div>
                      <div className="text-xs text-slate-400">Pending Payouts</div>
                    </div>
                  </div>
                </div>

                {/* Compliance Banner (Right Side) */}
                <div className="w-full md:w-96 glass-panel rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between border-l-4 border-l-emerald-500">
                  <div className="absolute right-0 top-0 w-32 h-32 bg-emerald-500/10 blur-[50px] rounded-full pointer-events-none" />
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-medium text-white">Compliance Status</h3>
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-semibold tracking-wide">
                        ACTIVE
                      </span>
                    </div>
                    <p className="text-slate-400 text-xs leading-relaxed mb-4">
                      Your licenses and insurance are up to date. You are fully cleared to accept new jobs on the Apex
                      network.
                    </p>
                  </div>
                  <button
                    onClick={() => switchTab('compliance')}
                    className="w-full py-2.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-white transition-all flex items-center justify-center gap-2"
                  >
                    Manage Documents
                  </button>
                </div>
              </div>

              {/* Info Banner */}
              <div className="glass-panel p-4 rounded-xl border-l-4 border-l-blue-500/50 flex items-start gap-3 bg-blue-500/[0.03]">
                <Info className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                <div>
                  <h4 className="text-xs font-medium text-blue-100 mb-0.5">Seasonal Bonus Program</h4>
                  <p className="text-[11px] text-blue-200/60">
                    Complete 5 jobs before Friday to unlock a 5% bonus on all payouts.
                  </p>
                </div>
                <button className="ml-auto text-xs text-blue-400 hover:text-blue-300">Dismiss</button>
              </div>

              {/* Active Project Section */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-white tracking-tight">Active Projects</h2>
                  <button className="text-xs text-slate-500 hover:text-white transition-colors">View All</button>
                </div>

                {activeJobs.length === 0 ? (
                  <div className="glass-panel p-8 rounded-2xl border border-white/5 text-center">
                    <Briefcase className="w-12 h-12 text-slate-500 mx-auto mb-3" />
                    <p className="text-sm text-slate-400">No active projects at the moment.</p>
                    <p className="text-xs text-slate-500 mt-1">Accept a job from the Job Board to get started.</p>
                  </div>
                ) : (
                  activeJobs.map((job) => {
                    // Calculate progress: step 1 = 0%, step 2 = 25%, step 3 = 50%, step 4 = 75%, step 5 = 100%
                    const currentStep = job.contractorProgress?.currentStep || 1;
                    const progress = currentStep > 1 ? ((currentStep - 1) / 4) * 100 : 0;
                    const stepLabels = ['', 'Acknowledgment', 'Walkthrough', 'Quote', 'Progress', 'Completion'];
                    return (
                      <div
                        key={job.id}
                        className="glass-panel p-0 rounded-2xl overflow-hidden group border border-emerald-500/20 shadow-[0_0_10px_-2px_rgba(16,185,129,0.3)] transition-all hover:border-emerald-500/40"
                      >
                        <div className="flex flex-col md:flex-row">
                          {/* Map visual placeholder */}
                          <div className="h-32 md:h-auto md:w-48 bg-slate-800 relative overflow-hidden">
                            <div className="absolute inset-0 opacity-30 bg-[url('https://api.mapbox.com/styles/v1/mapbox/dark-v10/static/-118.4,34.0,12,0/400x400?access_token=pk.eyJ1IjoiZXhhbXBsZSIsImEiOiJjbGZ4...')] bg-cover bg-center mix-blend-overlay" />
                            <div className="absolute inset-0 bg-emerald-900/20 mix-blend-overlay" />
                            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center border border-emerald-500/50 shadow-[0_0_20px_-5px_rgba(16,185,129,0.4)]">
                              <div className="w-2.5 h-2.5 bg-emerald-400 rounded-full animate-pulse" />
                            </div>
                          </div>

                          {/* Content */}
                          <div className="p-6 flex-1 flex flex-col md:flex-row gap-6 items-center">
                            <div className="flex-1 space-y-2 text-center md:text-left">
                              <div className="flex items-center justify-center md:justify-start gap-2">
                                <h3 className="text-base font-semibold text-white">{job.jobName}</h3>
                                <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-semibold">
                                  IN PROGRESS
                                </span>
                              </div>
                              <div className="flex items-center justify-center md:justify-start gap-4 text-xs text-slate-400">
                                <span className="flex items-center gap-1.5">
                                  <MapPin className="w-3 h-3" /> {job.propertyAddress}
                                </span>
                                <span className="flex items-center gap-1.5">
                                  <User className="w-3 h-3" /> {job.customerName}
                                </span>
                              </div>
                              <div className="flex items-center justify-center md:justify-start gap-4 pt-2">
                                <div className="text-xs">
                                  <span className="block text-slate-500 uppercase text-[10px] tracking-wider mb-0.5">
                                    Current Step
                                  </span>
                                  <span className="text-slate-200">
                                    Step {job.contractorProgress?.currentStep || 1}: {stepLabels[job.contractorProgress?.currentStep || 1]}
                                  </span>
                                </div>
                                <div className="w-[1px] h-6 bg-white/10" />
                                <div className="text-xs">
                                  <span className="block text-slate-500 uppercase text-[10px] tracking-wider mb-0.5">
                                    Est. Pay
                                  </span>
                                  <span className="text-white font-medium">{job.estimatedPay}</span>
                                </div>
                              </div>
                            </div>

                            <div className="flex gap-3">
                              <button className="px-4 py-2 rounded-full bg-white/5 border border-white/10 text-white text-xs hover:bg-white/10 transition-colors">
                                Details
                              </button>
                              <button
                                onClick={() => handleResumeJob(job.id)}
                                className="px-5 py-2 rounded-full bg-emerald-500 text-slate-900 text-xs font-semibold hover:bg-emerald-400 shadow-[0_0_20px_-5px_rgba(16,185,129,0.4)] transition-all flex items-center gap-2"
                              >
                                Resume Job <ChevronRight className="w-3 h-3" />
                              </button>
                            </div>
                          </div>
                        </div>
                        {/* Progress Bar Bottom */}
                        <div className="h-1 w-full bg-slate-800">
                          <div
                            className="h-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)] transition-all"
                            style={{ width: `${progress}%` }}
                          />
                        </div>
                      </div>
                    );
                  })
                )}
              </div>

              {/* New Opportunities - Show available jobs preview */}
              {availableJobs.length > 0 && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h2 className="text-sm font-semibold text-white tracking-tight">New Opportunities</h2>
                    <button
                      onClick={() => switchTab('jobs')}
                      className="text-xs text-slate-500 hover:text-white transition-colors"
                    >
                      View All
                    </button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {availableJobs.slice(0, 3).map((job) => (
                      <div
                        key={job.id}
                        onClick={() => switchTab('jobs')}
                        className="glass-card p-5 rounded-2xl group hover:border-white/20 transition-all cursor-pointer"
                      >
                        <div className="flex justify-between items-start mb-3">
                          <div className="px-2 py-1 rounded bg-slate-800 border border-white/5 text-[10px] text-slate-400 capitalize">
                            {job.trade}
                          </div>
                          <span className="px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[10px] font-medium">
                            OPEN
                          </span>
                        </div>
                        <h4 className="text-sm font-medium text-white mb-1 group-hover:text-emerald-400 transition-colors">
                          {job.jobName}
                        </h4>
                        <div className="text-xs text-slate-500 mb-4 flex items-center gap-1">
                          <MapPin className="w-3 h-3" /> {job.propertyAddress}
                        </div>
                        <div className="flex items-center justify-between pt-3 border-t border-white/5">
                          <span className="text-sm font-semibold text-white">{job.estimatedPay}</span>
                          <button className="text-xs text-slate-400 group-hover:text-white transition-colors flex items-center gap-1">
                            View <ChevronRight className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* SECTION B: COMPLIANCE HUB */}
          {activeTab === 'compliance' && (
            <div className="fade-in max-w-5xl mx-auto space-y-8">
              {/* Header */}
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-semibold tracking-tight text-white mb-1">Compliance Hub</h1>
                  <p className="text-slate-400 text-sm">Manage your licenses, insurance, and tax documents.</p>
                </div>
                <div className="px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_20px_-5px_rgba(16,185,129,0.4)]" />
                  <span className="text-xs font-semibold text-emerald-400 tracking-wide uppercase">Active Status</span>
                </div>
              </div>

              {/* Warning Banner */}
              <div className="glass-panel p-5 rounded-xl border border-amber-500/20 bg-amber-500/[0.03] flex items-center gap-4">
                <div className="p-2 rounded-full bg-amber-500/10 text-amber-500">
                  <Info className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-medium text-white">Insurance Expiring Soon</h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Your General Liability insurance expires in <span className="text-white font-medium">14 days</span>.
                    Please upload a renewal certificate.
                  </p>
                </div>
                <button className="ml-auto px-4 py-2 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 text-xs font-medium border border-amber-500/20 transition-all">
                  Update Now
                </button>
              </div>

              {/* Uploads Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Card 1: W9 */}
                <div className="glass-card p-6 rounded-2xl flex flex-col gap-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2.5 rounded-lg bg-slate-800 border border-white/5">
                        <FileText className="w-5 h-5 text-emerald-400" />
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-white">W-9 Tax Form</h4>
                        <p className="text-xs text-slate-500">IRS Verification</p>
                      </div>
                    </div>
                    <CheckCircle className="w-5 h-5 text-emerald-500 fill-emerald-500/20" />
                  </div>
                  <div className="mt-2 p-3 rounded-lg bg-slate-950/50 border border-white/5 flex items-center justify-between">
                    <span className="text-xs text-slate-400">W9_Anderson_2024.pdf</span>
                    <span className="text-[10px] text-slate-600">3.2 MB</span>
                  </div>
                  <button className="mt-auto w-full py-2 rounded-lg border border-white/10 hover:bg-white/5 text-xs text-slate-300 transition-colors">
                    Re-upload
                  </button>
                </div>

                {/* Card 2: Insurance */}
                <div className="glass-card p-6 rounded-2xl flex flex-col gap-4 relative overflow-hidden">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2.5 rounded-lg bg-slate-800 border border-white/5">
                        <Shield className="w-5 h-5 text-amber-400" />
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-white">Liability Insurance</h4>
                        <p className="text-xs text-slate-500">Expiring Jan 10, 2026</p>
                      </div>
                    </div>
                    <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
                  </div>

                  {/* Form inside card */}
                  <div className="mt-2 space-y-3">
                    <div>
                      <label className="block text-[10px] uppercase tracking-wider text-slate-500 mb-1.5">
                        Expiration Date
                      </label>
                      <div className="relative">
                        <input
                          type="text"
                          defaultValue="Jan 10, 2026"
                          className="w-full pl-9 pr-3 py-2 rounded-lg glass-input text-xs"
                        />
                        <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500" />
                      </div>
                    </div>
                  </div>

                  <button className="mt-auto w-full py-2 rounded-lg bg-emerald-500 text-slate-900 font-semibold hover:bg-emerald-400 shadow-[0_0_20px_-5px_rgba(16,185,129,0.4)] text-xs transition-colors">
                    Update Certificate
                  </button>
                </div>
              </div>

              {/* Agreements List */}
              <div className="glass-panel rounded-2xl overflow-hidden">
                <div className="px-6 py-4 border-b border-white/5">
                  <h3 className="text-sm font-medium text-white">Signed Agreements</h3>
                </div>
                <div className="divide-y divide-white/5">
                  {[
                    'Independent Contractor Agreement',
                    'Liability Waiver 2024',
                    'Apex Platform Payment Terms',
                  ].map((agreement) => (
                    <div
                      key={agreement}
                      className="px-6 py-4 flex items-center justify-between hover:bg-white/[0.01] transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <CheckCircle className="w-4 h-4 text-emerald-500" />
                        <span className="text-sm text-slate-300">{agreement}</span>
                      </div>
                      <button className="text-xs text-emerald-400 hover:text-emerald-300">
                        {agreement.includes('Terms') ? 'View Terms' : 'View PDF'}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* SECTION C: JOB BOARD */}
          {activeTab === 'jobs' && (
            <div className="fade-in max-w-6xl mx-auto space-y-6">
              {/* Filters Bar */}
              <div className="glass-panel p-2 rounded-xl flex flex-col md:flex-row items-center justify-between gap-4 sticky top-0 z-30 backdrop-blur-xl">
                <div className="flex items-center gap-2 px-2">
                  <div className="p-2 bg-white/5 rounded-lg border border-white/5">
                    <SlidersHorizontal className="w-4 h-4 text-slate-400" />
                  </div>
                  <div className="h-6 w-[1px] bg-white/10 mx-1" />

                  {/* Tabs */}
                  <div className="flex bg-slate-900/50 p-1 rounded-lg border border-white/5">
                    <button className="px-4 py-1.5 rounded-md bg-white/10 text-white text-xs font-medium shadow-sm">
                      Available
                    </button>
                    <button className="px-4 py-1.5 rounded-md text-slate-400 hover:text-white text-xs transition-colors">
                      In Progress
                    </button>
                    <button className="px-4 py-1.5 rounded-md text-slate-400 hover:text-white text-xs transition-colors">
                      Completed
                    </button>
                  </div>
                </div>

                <div className="flex items-center gap-3 px-2 w-full md:w-auto">
                  <div className="relative w-40">
                    <select className="w-full appearance-none bg-slate-900/50 border border-white/10 text-white text-xs rounded-lg py-2 pl-3 pr-8 focus:border-emerald-500 focus:outline-none">
                      <option>All Cities</option>
                      <option>Los Angeles</option>
                      <option>San Diego</option>
                    </select>
                    <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500 pointer-events-none" />
                  </div>
                </div>
              </div>

              {/* Stats Row */}
              <div className="grid grid-cols-3 gap-4">
                <div className="glass-card p-4 rounded-xl flex items-center justify-between">
                  <span className="text-xs text-slate-400">Available Jobs</span>
                  <span className="text-lg font-semibold text-white">{availableJobs.length}</span>
                </div>
                <div className="glass-card p-4 rounded-xl flex items-center justify-between border-emerald-500/20 bg-emerald-500/[0.02]">
                  <span className="text-xs text-emerald-400">Active Jobs</span>
                  <span className="text-lg font-semibold text-emerald-400">{activeJobs.length}</span>
                </div>
                <div className="glass-card p-4 rounded-xl flex items-center justify-between">
                  <span className="text-xs text-slate-400">Completed</span>
                  <span className="text-lg font-semibold text-white">{completedJobsCount}</span>
                </div>
              </div>

              {/* Job List */}
              <div className="space-y-4">
                {availableJobs.length === 0 ? (
                  <div className="glass-panel p-12 rounded-2xl text-center border border-white/10">
                    <Briefcase className="w-16 h-16 text-slate-500 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-white mb-2">No Available Jobs</h3>
                    <p className="text-slate-400">There are no jobs matching your trade at the moment.</p>
                  </div>
                ) : (
                  availableJobs.map((job) => (
                    <div key={job.id} className="glass-panel p-5 rounded-xl hover:border-emerald-500/30 transition-all group">
                      <div className="flex flex-col md:flex-row gap-6">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-base font-semibold text-white">{job.jobName}</h3>
                            <span className="px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[10px] font-medium">
                              OPEN
                            </span>
                            {job.materialStatus && (
                              <span className="px-2 py-0.5 rounded-full bg-slate-800 border border-white/10 text-slate-400 text-[10px]">
                                {job.materialStatus}
                              </span>
                            )}
                          </div>
                          <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 mb-3">
                            <span className="flex items-center gap-1.5">
                              <MapPin className="w-3.5 h-3.5" /> {job.propertyAddress}, {job.city}
                            </span>
                            {job.scheduledTime && (
                              <span className="flex items-center gap-1.5">
                                <Calendar className="w-3.5 h-3.5" /> Start: {new Date(job.scheduledTime).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                              </span>
                            )}
                            {job.squareFootage && (
                              <span className="flex items-center gap-1.5">
                                <Home className="w-3.5 h-3.5" /> {job.squareFootage}
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-slate-500 line-clamp-2 max-w-2xl">
                            {job.description}
                          </p>
                        </div>

                        <div className="flex flex-col items-end justify-center min-w-[140px] border-l border-white/5 pl-6">
                          <span className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Estimated Pay</span>
                          <span className="text-xl font-bold text-white mb-3">{job.estimatedPay}</span>
                          <button
                            onClick={() => handleAcceptJob(job.id)}
                            className="w-full py-2 rounded-full bg-emerald-500 text-slate-900 text-xs font-semibold hover:bg-emerald-400 shadow-[0_0_20px_-5px_rgba(16,185,129,0.4)] transition-all"
                          >
                            Accept Job
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* SECTION D: WALLET */}
          {activeTab === 'wallet' && (
            <div className="fade-in max-w-5xl mx-auto space-y-8">
              {/* Header */}
              <div>
                <h1 className="text-2xl font-semibold tracking-tight text-white mb-1">Wallet & Payouts</h1>
                <p className="text-slate-400 text-sm">Track your earnings and payout history.</p>
              </div>

              {/* Money Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="glass-panel p-6 rounded-2xl relative overflow-hidden">
                  <div className="absolute right-0 top-0 w-48 h-48 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
                      <CreditCard className="w-5 h-5 text-emerald-400" />
                    </div>
                    <span className="text-sm font-medium text-slate-300">Total Earnings</span>
                  </div>
                  <div className="text-4xl font-semibold text-white tracking-tight mb-2">$84,320.50</div>
                  <div className="text-xs text-emerald-400 flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" /> +$12k this month
                  </div>
                </div>

                <div className="glass-panel p-6 rounded-2xl relative overflow-hidden">
                  <div className="absolute right-0 top-0 w-48 h-48 bg-blue-500/5 rounded-full blur-3xl pointer-events-none" />
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/20">
                      <Clock className="w-5 h-5 text-blue-400" />
                    </div>
                    <span className="text-sm font-medium text-slate-300">Pending Payouts</span>
                  </div>
                  <div className="text-4xl font-semibold text-white tracking-tight mb-2">$3,450.00</div>
                  <div className="text-xs text-slate-400">Estimates to hit bank by Nov 24</div>
                </div>
              </div>

              {/* Ledger Table */}
              <div className="glass-panel rounded-2xl overflow-hidden border border-white/5">
                <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between">
                  <h3 className="text-sm font-medium text-white">Recent Transactions</h3>
                  <button className="text-xs text-slate-400 hover:text-white flex items-center gap-1">
                    Download CSV <Download className="w-3 h-3" />
                  </button>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead>
                      <tr className="bg-white/[0.02] border-b border-white/5">
                        <th className="px-6 py-3 text-[10px] uppercase tracking-wider text-slate-500 font-medium">
                          Job ID
                        </th>
                        <th className="px-6 py-3 text-[10px] uppercase tracking-wider text-slate-500 font-medium">
                          Type
                        </th>
                        <th className="px-6 py-3 text-[10px] uppercase tracking-wider text-slate-500 font-medium">
                          Date
                        </th>
                        <th className="px-6 py-3 text-[10px] uppercase tracking-wider text-slate-500 font-medium">
                          Status
                        </th>
                        <th className="px-6 py-3 text-[10px] uppercase tracking-wider text-slate-500 font-medium text-right">
                          Amount
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5 text-xs text-slate-300">
                      {[
                        { id: '#8291', type: 'Kitchen Remodel (50%)', date: 'Nov 20, 2024', status: 'PROCESSING', amount: '$2,125.00' },
                        { id: '#8104', type: 'Electrical Repair', date: 'Nov 15, 2024', status: 'PAID', amount: '$450.00' },
                        { id: '#7992', type: 'Deck Stain Materials', date: 'Nov 10, 2024', status: 'PAID', amount: '$320.00' },
                      ].map((tx, idx) => (
                        <tr key={idx} className="hover:bg-white/[0.02] transition-colors">
                          <td className="px-6 py-4 font-mono text-slate-400">{tx.id}</td>
                          <td className="px-6 py-4">{tx.type}</td>
                          <td className="px-6 py-4">{tx.date}</td>
                          <td className="px-6 py-4">
                            <span
                              className={`px-2 py-0.5 rounded-full text-[10px] font-medium border ${
                                tx.status === 'PAID'
                                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                                  : 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                              }`}
                            >
                              {tx.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-right font-medium text-white">{tx.amount}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Info Panel */}
              <div className="p-4 rounded-xl border border-dashed border-white/10 text-center">
                <p className="text-xs text-slate-500">
                  Payments are processed every Friday. Please allow 2-3 business days for bank transfers to appear.
                </p>
              </div>
            </div>
          )}

          {/* FOOTER SPACER */}
          <div className="h-20" />

          {/* Floating Chat Button */}
          <button className="fixed bottom-8 right-8 w-14 h-14 rounded-full bg-slate-900 border border-white/10 shadow-[0_4px_30px_rgba(0,0,0,0.1)] flex items-center justify-center text-white hover:scale-105 transition-all group z-50">
            <div className="absolute inset-0 rounded-full bg-emerald-500/20 animate-ping opacity-20" />
            <MessageSquare className="w-6 h-6 group-hover:text-emerald-400 transition-colors" />
            <div className="absolute top-3 right-3 w-2.5 h-2.5 bg-red-500 rounded-full border border-slate-900" />
          </button>
        </div>
      </main>

      {/* Completed Jobs Modal */}
      {showCompletedJobs && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="glass-panel rounded-3xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col border border-white/10 shadow-2xl">
            {/* Header */}
            <div className="px-8 py-6 border-b border-white/5 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-semibold tracking-tight text-white mb-1">Completed Jobs</h2>
                <p className="text-slate-400 text-sm">Your successfully completed projects</p>
              </div>
              <button
                onClick={() => setShowCompletedJobs(false)}
                className="w-9 h-9 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center border border-white/10 transition-colors text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Jobs List */}
            <div className="flex-1 overflow-y-auto p-8">
              {completedJobs.length === 0 ? (
                <div className="text-center py-16">
                  <div className="w-16 h-16 mx-auto rounded-full bg-slate-800 border border-white/10 flex items-center justify-center mb-4">
                    <Briefcase className="w-8 h-8 text-slate-500" />
                  </div>
                  <h3 className="text-lg font-medium text-white mb-2">No Completed Jobs Yet</h3>
                  <p className="text-sm text-slate-400">Complete your first job to see it here.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {completedJobs.map((job) => (
                    <div
                      key={job.id}
                      className="glass-card p-6 rounded-2xl border border-white/5 hover:border-emerald-500/30 transition-all group"
                    >
                      <div className="flex flex-col md:flex-row gap-6">
                        {/* Left: Job Info */}
                        <div className="flex-1 space-y-3">
                          <div className="flex items-start justify-between">
                            <div>
                              <h3 className="text-base font-semibold text-white mb-1 group-hover:text-emerald-400 transition-colors">
                                {job.jobName}
                              </h3>
                              <div className="flex items-center gap-4 text-xs text-slate-400">
                                <span className="flex items-center gap-1.5">
                                  <User className="w-3.5 h-3.5" /> {job.customerName}
                                </span>
                                <span className="flex items-center gap-1.5">
                                  <MapPin className="w-3.5 h-3.5" /> {job.address}
                                </span>
                              </div>
                            </div>
                            <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-semibold tracking-wide">
                              COMPLETED
                            </span>
                          </div>

                          {job.description && (
                            <p className="text-xs text-slate-500 leading-relaxed">{job.description}</p>
                          )}

                          <div className="flex items-center gap-4 pt-2">
                            <div className="text-xs">
                              <span className="block text-slate-500 uppercase text-[10px] tracking-wider mb-0.5">
                                Completed
                              </span>
                              <span className="text-slate-200 flex items-center gap-1.5">
                                <Calendar className="w-3 h-3" /> {job.completedDate}
                              </span>
                            </div>
                            <div className="w-[1px] h-6 bg-white/10" />
                            <div className="text-xs">
                              <span className="block text-slate-500 uppercase text-[10px] tracking-wider mb-0.5">
                                Est. Pay
                              </span>
                              <span className="text-white font-semibold">{job.estimatedPay}</span>
                            </div>
                          </div>
                        </div>

                        {/* Right: Actions */}
                        <div className="flex items-center gap-3 md:flex-col md:justify-center">
                          <button className="px-4 py-2 rounded-full bg-white/5 border border-white/10 text-white text-xs hover:bg-white/10 transition-colors">
                            View Details
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            {completedJobs.length > 0 && (
              <div className="px-8 py-4 border-t border-white/5 flex items-center justify-between bg-white/[0.01]">
                <p className="text-xs text-slate-400">
                  Total: <span className="text-white font-medium">{completedJobs.length} job{completedJobs.length !== 1 ? 's' : ''}</span>
                </p>
                <button
                  onClick={() => setShowCompletedJobs(false)}
                  className="px-4 py-2 rounded-full bg-emerald-500 text-slate-900 text-xs font-semibold hover:bg-emerald-400 transition-colors"
                >
                  Close
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

