import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth, getDashboardRoute } from '@/context/AuthContext';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Card from '@/components/ui/Card';
import { Home } from 'lucide-react';

export default function Login() {
    const navigate = useNavigate();
    const { login, loginWithAPI, loading, error, isAuthenticated, currentUser } = useAuth();
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [formError, setFormError] = useState('');
    const [useAPI, setUseAPI] = useState(true); // Default to API mode

    // Redirect if already authenticated
    useEffect(() => {
        if (isAuthenticated && currentUser) {
            console.log('User already authenticated, redirecting to:', getDashboardRoute(currentUser.role));
            navigate(getDashboardRoute(currentUser.role), { replace: true });
        }
    }, [isAuthenticated, currentUser, navigate]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        setFormError('');
    };

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setFormError('');

        if (!formData.email || !formData.password) {
            setFormError('Please enter both email and password');
            return;
        }

        try {
            if (useAPI) {
                // Use real API
                const user = await loginWithAPI({
                    email: formData.email,
                    password: formData.password
                });
                
                // Navigate based on user role from API response
                console.log('API Login successful, user:', user);
                navigate(getDashboardRoute(user.role), { replace: true });
            } else {
                // Use demo login
                await login(formData.email);
                const user = users.find((u) => u.email === formData.email);
                if (user) {
                    console.log('Demo Login successful, user:', user);
                    navigate(getDashboardRoute(user.role), { replace: true });
                }
            }
        } catch (err) {
            if (useAPI) {
                setFormError(error || 'Login failed. Please check your credentials.');
            } else {
                setFormError('User not found. Please select a demo user or enter a valid email.');
            }
        }
    };

    const handleDemoUser = async (userEmail: string) => {
        setFormData({ email: userEmail, password: 'demo' });
        setUseAPI(false); // Switch to demo mode
        try {
            await login(userEmail);
            const user = users.find((u) => u.email === userEmail);
            if (user) {
                console.log('Demo user login successful, user:', user);
                navigate(getDashboardRoute(user.role), { replace: true });
            }
        } catch (err) {
            setFormError('Error logging in');
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center px-4 py-12 relative overflow-hidden">
            {/* Background Image */}
            <div
                className="absolute inset-0 bg-cover bg-center bg-no-repeat"
                style={{
                    backgroundImage: `url('/src/assets/login-bg.png')`,
                }}
            />

            {/* Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-gray-900/80 via-purple-900/70 to-violet-900/80" />

            {/* Content */}
            <div className="w-full max-w-md space-y-8 animate-fade-in relative z-10">
                {/* Logo and Title */}
                <div className="text-center">
                    <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 mb-4 shadow-lg shadow-purple-500/50">
                        <Home className="w-10 h-10 text-white" />
                    </div>
                    <h1 className="text-4xl font-bold gradient-text">Apex Home Services</h1>
                    <p className="mt-2 text-gray-300">Welcome back! Please login to your account.</p>
                </div>

                {/* Login Form */}
                <Card className="bg-white/10 dark:bg-white/5 backdrop-blur-xl border-white/20 dark:border-white/10">
                    {/* API Toggle */}
                    <div className="mb-4 flex items-center justify-center space-x-4">
                        <label className="flex items-center space-x-2 text-sm text-gray-300">
                            <input
                                type="checkbox"
                                checked={useAPI}
                                onChange={(e) => setUseAPI(e.target.checked)}
                                className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                            />
                            <span>Use Real API</span>
                        </label>
                        {useAPI && (
                            <span className="text-xs text-green-300 bg-green-500/20 px-2 py-1 rounded">
                                API Mode Active
                            </span>
                        )}
                    </div>

                    <form onSubmit={handleLogin} className="space-y-6">
                        <Input
                            label="Email"
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleInputChange}
                            placeholder="Enter your email"
                            required
                        />

                        <Input
                            label="Password"
                            type="password"
                            name="password"
                            value={formData.password}
                            onChange={handleInputChange}
                            placeholder="Enter your password"
                            required
                        />

                        {(formError || error) && (
                            <div className="text-red-300 text-sm bg-red-500/20 border border-red-400/30 rounded-lg p-3">
                                {formError || error}
                            </div>
                        )}

                        <Button
                            type="submit"
                            variant="primary"
                            className="w-full"
                            disabled={loading}
                        >
                            {loading ? 'Logging in...' : 'Login'}
                        </Button>

                        <Link to="/forgot-password">
                            <button
                                type="button"
                                className="w-full text-sm text-purple-300 hover:text-purple-200 smooth-transition"
                            >
                                Forgot password?
                            </button>
                        </Link>
                    </form>
                </Card>

                {/* Registration Link */}
                <div className="text-center">
                    <p className="text-gray-300 text-sm">
                        Don't have an account?{' '}
                        <Link 
                            to="/register" 
                            className="text-purple-300 hover:text-purple-200 smooth-transition font-medium"
                        >
                            Create one here
                        </Link>
                    </p>
                </div>

                {/* Customer Access Info */}
                <div className="text-center">
                    <p className="text-gray-300 text-sm">
                        Are you a customer?
                        <br />
                        <span className="text-purple-300">Access your portal via the link in your quote/invoice email.</span>
                    </p>
                    {/* Debug: Manual redirect button */}
                    {isAuthenticated && currentUser && (
                        <button
                            onClick={() => {
                                console.log('Manual redirect clicked, user:', currentUser);
                                navigate('/customer/dashboard', { replace: true });
                            }}
                            className="mt-2 px-4 py-2 bg-red-500 text-white rounded text-xs"
                        >
                            DEBUG: Go to Customer Dashboard
                        </button>
                    )}
                </div>

                {/* Demo User Picker */}
                <Card className="bg-white/10 dark:bg-white/5 backdrop-blur-xl border-white/20 dark:border-white/10">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-white">Quick Demo Login</h3>
                        {!useAPI && (
                            <span className="text-xs text-blue-300 bg-blue-500/20 px-2 py-1 rounded">
                                Demo Mode
                            </span>
                        )}
                    </div>
                    <p className="text-sm text-gray-400 mb-4">
                        Click any user below to login instantly (demo mode)
                    </p>
                    <div className="space-y-2">
                        {users.map((user) => (
                            <button
                                key={user.id}
                                onClick={() => handleDemoUser(user.email)}
                                className="w-full px-4 py-3 rounded-lg bg-white/10 hover:bg-white/20 border border-white/20 hover:border-white/30 smooth-transition text-left group"
                            >
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="font-medium text-white group-hover:text-purple-200 smooth-transition">{user.name}</p>
                                        <p className="text-sm text-gray-300 group-hover:text-gray-200">{user.email}</p>
                                    </div>
                                    <span className="text-xs px-3 py-1 rounded-full bg-purple-500/30 text-purple-200 border border-purple-400/40 group-hover:bg-purple-500/40 smooth-transition">
                                        {user.role.toUpperCase()}
                                    </span>
                                </div>
                            </button>
                        ))}
                    </div>

                    {/* Customer Magic Link Demos */}
                    <div className="pt-4 border-t border-white/10 mt-4">
                        <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Customer Access (Public Links)</h4>
                        <div className="grid grid-cols-2 gap-3">
                            <button
                                onClick={() => navigate('/track/101')}
                                className="px-3 py-2 rounded-lg bg-blue-500/10 hover:bg-blue-500/20 border border-blue-400/20 text-blue-200 text-xs font-medium smooth-transition flex items-center justify-center gap-2"
                            >
                                <span>📍</span> Tracker
                            </button>
                            <button
                                onClick={() => navigate('/materials/demo-token-101')}
                                className="px-3 py-2 rounded-lg bg-green-500/10 hover:bg-green-500/20 border border-green-400/20 text-green-200 text-xs font-medium smooth-transition flex items-center justify-center gap-2"
                            >
                                <span>📦</span> Materials
                            </button>
                        </div>
                    </div>
                </Card>
            </div>
        </div>
    );
}
