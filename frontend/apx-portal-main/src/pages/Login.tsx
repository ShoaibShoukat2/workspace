import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth, getDashboardRoute } from '@/context/AuthContext';
import type { UserRole } from '@/types';
import '@/styles/customerPortal.css';
import AuthLayoutSplit from '@/components/auth/AuthLayoutSplit';
import RoleToggle, { RoleOption } from '@/components/auth/RoleToggle';
import GlassInput from '@/components/auth/GlassInput';
import PrimaryButton from '@/components/auth/PrimaryButton';

const ROLE_OPTIONS: RoleOption[] = [
    { id: 'admin', label: 'Admin', role: 'admin' },
    { id: 'contractor', label: 'Contractor Pro', role: 'contractor' },
    { id: 'investor', label: 'Investor', role: 'investor' },
    { id: 'customer', label: 'Homeowner', role: 'customer' },
];

const CTA_LABELS: Record<UserRole, string> = {
    admin: 'Enter Admin Console',
    fm: 'Enter FM Dashboard',
    contractor: 'Enter Contractor Cockpit',
    investor: 'Enter Investor Portal',
    customer: 'Access Customer Portal',
};

// Demo credentials for development
const DEMO_CREDENTIALS = {
    admin: { email: 'admin@apex.inc', password: 'admin123' },
    contractor: { email: 'contractor@apex.inc', password: 'contractor123' },
    investor: { email: 'investor@apex.inc', password: 'investor123' },
    customer: { email: 'customer@apex.inc', password: 'customer123' },
    fm: { email: 'fm@apex.inc', password: 'fm123' },
};

export default function Login() {
    const navigate = useNavigate();
    const { login, loading } = useAuth();

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [selectedRole, setSelectedRole] = useState<UserRole>('contractor');
    const [error, setError] = useState('');

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (!email || !password) {
            setError('Please enter both email and password');
            return;
        }

        try {
            await login(email, password);
            // Navigation will be handled after successful login
            const user = await login(email, password);
            navigate(getDashboardRoute(selectedRole));
        } catch (err: any) {
            setError(err.message || 'Login failed. Please check your credentials.');
        }
    };

    const handleDemoLogin = async (role: UserRole) => {
        const creds = DEMO_CREDENTIALS[role];
        if (!creds) {
            setError('Demo credentials not available for this role');
            return;
        }

        setEmail(creds.email);
        setPassword(creds.password);
        setSelectedRole(role);

        try {
            await login(creds.email, creds.password);
            // Navigate based on role
            if (role === 'contractor') {
                navigate('/contractor/portal');
            } else {
                navigate(getDashboardRoute(role));
            }
        } catch (err: any) {
            setError(err.message || 'Demo login failed');
        }
    };

    return (
        <AuthLayoutSplit>
            {/* Role Switcher */}
            <RoleToggle
                options={ROLE_OPTIONS}
                activeRole={selectedRole}
                onChange={(role) => setSelectedRole(role)}
            />

            {/* Auth Form */}
            <form onSubmit={handleLogin} className="space-y-6">
                <GlassInput
                    label="Email Address"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="user@apex.inc"
                    required
                />

                <GlassInput
                    label="Password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    required
                />

                {error && (
                    <div className="text-rose-300 text-xs bg-rose-500/10 border border-rose-400/30 rounded-xl px-3 py-2">
                        {error}
                    </div>
                )}

                <PrimaryButton type="submit" loading={loading}>
                    {CTA_LABELS[selectedRole]}
                </PrimaryButton>

                <button
                    type="button"
                    className="w-full text-[11px] text-slate-500 hover:text-slate-300 text-left underline-offset-4 hover:underline"
                    onClick={() => alert('Password reset functionality will be implemented with backend integration.')}
                >
                    Forgot password?
                </button>
            </form>

            {/* Demo Login Section */}
            <div className="mt-6 space-y-4">
                <div className="text-[11px] text-slate-500 leading-relaxed">
                    <p className="font-semibold text-slate-400 mb-2">Demo Logins Available:</p>
                    <p>Use the buttons below to quickly access different user roles with backend authentication.</p>
                </div>

                {/* Demo Login Buttons */}
                <div className="grid grid-cols-2 gap-2">
                    {ROLE_OPTIONS.map((option) => (
                        <button
                            key={option.id}
                            type="button"
                            onClick={() => handleDemoLogin(option.role)}
                            disabled={loading}
                            className="px-3 py-2 text-xs bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-slate-300 transition-colors"
                        >
                            {option.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Customer helper text */}
            <div className="mt-6 text-[11px] text-slate-500 leading-relaxed">
                Are you a customer?
                <br />
                <span className="text-slate-400">
                    Access your portal via the secure link in your quote or invoice email.
                </span>
            </div>

            {/* Customer magic link demos */}
            <div className="mt-6 glass-panel rounded-2xl p-4 border border-white/10 space-y-3">
                <h4 className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">
                    Customer Magic Link Demos
                </h4>
                <button
                    type="button"
                    onClick={() => handleDemoLogin('customer')}
                    disabled={loading}
                    className="w-full px-4 py-3 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 disabled:opacity-50 border border-emerald-400/25 text-emerald-200 text-xs font-medium transition-colors flex items-center justify-center gap-2"
                >
                    <span>🏠</span> Customer Portal Demo
                </button>
                <div className="grid grid-cols-2 gap-3">
                    <button
                        type="button"
                        onClick={() => navigate('/track/101')}
                        className="px-3 py-2 rounded-xl bg-slate-900/60 hover:bg-slate-800 border border-white/10 text-slate-200 text-[11px] font-medium transition-colors flex items-center justify-center gap-2"
                    >
                        <span>📍</span> Tracker
                    </button>
                    <button
                        type="button"
                        onClick={() => navigate('/materials/demo-token-101')}
                        className="px-3 py-2 rounded-xl bg-slate-900/60 hover:bg-slate-800 border border-white/10 text-slate-200 text-[11px] font-medium transition-colors flex items-center justify-center gap-2"
                    >
                        <span>📦</span> Materials
                    </button>
                </div>
            </div>
        </AuthLayoutSplit>
    );
}

