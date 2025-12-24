import { useState } from 'react';
import { CheckCircle, XCircle, Loader, Send, User, Briefcase, List } from 'lucide-react';
import '@/styles/customerPortal.css';

const API_BASE_URL = 'http://192.168.100.58:5001/api';

interface ApiResponse {
  success: boolean;
  data?: any;
  error?: string;
  status?: number;
}

export default function TestAPI() {
  const [responses, setResponses] = useState<Array<{ endpoint: string; response: ApiResponse; timestamp: string }>>([]);
  const [loading, setLoading] = useState<string | null>(null);

  const makeRequest = async (endpoint: string, method: string = 'GET', body?: any) => {
    setLoading(endpoint);
    try {
      const options: RequestInit = {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
      };

      if (body && method !== 'GET') {
        options.body = JSON.stringify(body);
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
      const data = await response.json();

      const apiResponse: ApiResponse = {
        success: response.ok,
        data,
        status: response.status,
        error: response.ok ? undefined : data.error || 'Request failed',
      };

      setResponses((prev) => [{ endpoint, response: apiResponse, timestamp: new Date().toLocaleTimeString() }, ...prev]);
      return apiResponse;
    } catch (error: any) {
      const apiResponse: ApiResponse = {
        success: false,
        error: error.message || 'Network error',
      };
      setResponses((prev) => [{ endpoint, response: apiResponse, timestamp: new Date().toLocaleTimeString() }, ...prev]);
      return apiResponse;
    } finally {
      setLoading(null);
    }
  };

  // User Management Tests
  const testSignup = () => {
    makeRequest('/signup', 'POST', {
      email: `test${Date.now()}@example.com`,
      password: 'test123',
      user_role: 'customer',
    });
  };

  const testLogin = () => {
    makeRequest('/login', 'POST', {
      email: 'customer@demo.com',
      password: 'demo123',
    });
  };

  const testGetProfiles = () => {
    makeRequest('/profiles');
  };

  const testGetProfile = () => {
    makeRequest('/profiles/customer-001');
  };

  // Job Management Tests
  const testCreateJob = () => {
    makeRequest('/jobs', 'POST', {
      profileID: 'customer-001',
      jobName: `Test Job ${Date.now()}`,
      propertyAddress: '123 Test Street',
      city: 'Los Angeles',
      customerName: 'Test Customer',
      customerEmail: 'customer@demo.com',
      trade: 'painting',
      estimatedPay: '$1,500.00',
      description: 'This is a test job created from the API test page',
      scheduledTime: '2024-12-25',
      squareFootage: '500 sqft',
    });
  };

  const testGetJobs = () => {
    makeRequest('/jobs');
  };

  const testGetJobsByStatus = () => {
    makeRequest('/jobs?status=Open');
  };

  const testGetJobsByProfile = () => {
    makeRequest('/jobs?profileID=customer-001');
  };

  const testAssignJob = async () => {
    // First get jobs to find a job ID
    const jobsResponse = await makeRequest('/jobs?status=Open');
    if (jobsResponse.success && jobsResponse.data && jobsResponse.data.length > 0) {
      const jobId = jobsResponse.data[0].jobID;
      makeRequest(`/jobs/${jobId}/assign`, 'POST', {
        contractorId: 'contractor-001',
      });
    } else {
      alert('No open jobs found. Create a job first.');
    }
  };

  const testUpdateJobProgress = async () => {
    // First get jobs to find a job ID
    const jobsResponse = await makeRequest('/jobs?assignedContractorId=contractor-001');
    if (jobsResponse.success && jobsResponse.data && jobsResponse.data.length > 0) {
      const jobId = jobsResponse.data[0].jobID;
      makeRequest(`/jobs/${jobId}`, 'PUT', {
        contractorProgress: {
          currentStep: 3,
          acknowledged: true,
          lastUpdated: new Date().toISOString(),
        },
      });
    } else {
      alert('No assigned jobs found. Assign a job first.');
    }
  };

  const testHealth = () => {
    makeRequest('/health');
  };

  const clearResponses = () => {
    setResponses([]);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white p-8" style={{ fontFamily: 'system-ui, -apple-system, sans-serif', minHeight: '100vh' }}>
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight text-white mb-2">API Test Page</h1>
            <p className="text-slate-400 text-sm">Test endpoints at {API_BASE_URL}</p>
          </div>
          <button
            onClick={clearResponses}
            className="px-4 py-2 rounded-xl border border-white/10 text-slate-300 text-sm hover:bg-white/5 transition-colors"
          >
            Clear Responses
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Test Buttons */}
          <div className="lg:col-span-1 space-y-6">
            {/* Health Check */}
            <div className="p-6 rounded-2xl border border-white/10" style={{ background: 'rgba(18, 20, 28, 0.6)', backdropFilter: 'blur(12px)' }}>
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-emerald-400" /> Health Check
              </h2>
              <button
                onClick={testHealth}
                disabled={loading === '/health'}
                className="w-full px-4 py-3 rounded-xl bg-emerald-600 text-white font-semibold hover:bg-emerald-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading === '/health' ? <Loader className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                Test Health
              </button>
            </div>

            {/* User Management */}
            <div className="p-6 rounded-2xl border border-white/10" style={{ background: 'rgba(18, 20, 28, 0.6)', backdropFilter: 'blur(12px)' }}>
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <User className="w-5 h-5 text-blue-400" /> User Management
              </h2>
              <div className="space-y-3">
                <button
                  onClick={testSignup}
                  disabled={loading === '/signup'}
                  className="w-full px-4 py-2 rounded-xl bg-blue-600 text-white text-sm font-medium hover:bg-blue-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading === '/signup' ? <Loader className="w-4 h-4 animate-spin" /> : 'Sign Up'}
                </button>
                <button
                  onClick={testLogin}
                  disabled={loading === '/login'}
                  className="w-full px-4 py-2 rounded-xl bg-blue-600 text-white text-sm font-medium hover:bg-blue-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading === '/login' ? <Loader className="w-4 h-4 animate-spin" /> : 'Login'}
                </button>
                <button
                  onClick={testGetProfiles}
                  disabled={loading === '/profiles'}
                  className="w-full px-4 py-2 rounded-xl bg-blue-600 text-white text-sm font-medium hover:bg-blue-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading === '/profiles' ? <Loader className="w-4 h-4 animate-spin" /> : 'Get All Profiles'}
                </button>
                <button
                  onClick={testGetProfile}
                  disabled={loading === '/profiles/customer-001'}
                  className="w-full px-4 py-2 rounded-xl bg-blue-600 text-white text-sm font-medium hover:bg-blue-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading === '/profiles/customer-001' ? <Loader className="w-4 h-4 animate-spin" /> : 'Get Profile'}
                </button>
              </div>
            </div>

            {/* Job Management */}
            <div className="p-6 rounded-2xl border border-white/10" style={{ background: 'rgba(18, 20, 28, 0.6)', backdropFilter: 'blur(12px)' }}>
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-emerald-400" /> Job Management
              </h2>
              <div className="space-y-3">
                <button
                  onClick={testCreateJob}
                  disabled={loading === '/jobs'}
                  className="w-full px-4 py-2 rounded-xl bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading === '/jobs' ? <Loader className="w-4 h-4 animate-spin" /> : 'Create Job'}
                </button>
                <button
                  onClick={testGetJobs}
                  disabled={loading === '/jobs'}
                  className="w-full px-4 py-2 rounded-xl bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading === '/jobs' ? <Loader className="w-4 h-4 animate-spin" /> : 'Get All Jobs'}
                </button>
                <button
                  onClick={testGetJobsByStatus}
                  disabled={loading === '/jobs?status=Open'}
                  className="w-full px-4 py-2 rounded-xl bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading === '/jobs?status=Open' ? <Loader className="w-4 h-4 animate-spin" /> : 'Get Open Jobs'}
                </button>
                <button
                  onClick={testGetJobsByProfile}
                  disabled={loading === '/jobs?profileID=customer-001'}
                  className="w-full px-4 py-2 rounded-xl bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading === '/jobs?profileID=customer-001' ? <Loader className="w-4 h-4 animate-spin" /> : 'Get Jobs by Profile'}
                </button>
                <button
                  onClick={testAssignJob}
                  disabled={loading?.includes('/jobs')}
                  className="w-full px-4 py-2 rounded-xl bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading?.includes('/jobs') ? <Loader className="w-4 h-4 animate-spin" /> : 'Assign Job'}
                </button>
                <button
                  onClick={testUpdateJobProgress}
                  disabled={loading?.includes('/jobs')}
                  className="w-full px-4 py-2 rounded-xl bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading?.includes('/jobs') ? <Loader className="w-4 h-4 animate-spin" /> : 'Update Progress'}
                </button>
              </div>
            </div>
          </div>

          {/* Right: Responses */}
          <div className="lg:col-span-2">
            <div className="p-6 rounded-2xl border border-white/10" style={{ background: 'rgba(18, 20, 28, 0.6)', backdropFilter: 'blur(12px)' }}>
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <List className="w-5 h-5 text-slate-400" /> API Responses
              </h2>
              {responses.length === 0 ? (
                <div className="text-center py-12 text-slate-500">
                  <p>No responses yet. Click a button to test an endpoint.</p>
                </div>
              ) : (
                <div className="space-y-4 max-h-[800px] overflow-y-auto">
                  {responses.map((item, index) => (
                    <div
                      key={index}
                      className={`p-4 rounded-xl border ${
                        item.response.success
                          ? 'bg-emerald-500/5 border-emerald-500/20'
                          : 'bg-red-500/5 border-red-500/20'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {item.response.success ? (
                            <CheckCircle className="w-4 h-4 text-emerald-400" />
                          ) : (
                            <XCircle className="w-4 h-4 text-red-400" />
                          )}
                          <span className="font-mono text-xs text-slate-300">{item.endpoint}</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-slate-500">
                          <span>{item.timestamp}</span>
                          {item.response.status && (
                            <span
                              className={`px-2 py-0.5 rounded ${
                                item.response.status < 300
                                  ? 'bg-emerald-500/10 text-emerald-400'
                                  : item.response.status < 400
                                  ? 'bg-yellow-500/10 text-yellow-400'
                                  : 'bg-red-500/10 text-red-400'
                              }`}
                            >
                              {item.response.status}
                            </span>
                          )}
                        </div>
                      </div>
                      {item.response.error && (
                        <div className="mb-2 text-sm text-red-400 font-medium">{item.response.error}</div>
                      )}
                      <pre className="text-xs bg-slate-900/50 p-3 rounded-lg overflow-x-auto text-slate-300">
                        {JSON.stringify(item.response.data || item.response.error, null, 2)}
                      </pre>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

