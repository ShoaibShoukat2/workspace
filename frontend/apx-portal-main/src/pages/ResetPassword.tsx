import { useState, useEffect } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { apiService } from '@/lib/api';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Card from '@/components/ui/Card';
import { Home, CheckCircle, AlertCircle } from 'lucide-react';

export default function ResetPassword() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const token = searchParams.get('token');
    
    const [formData, setFormData] = useState({
        password: '',
        confirmPassword: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        if (!token) {
            setError('Invalid reset link. Please request a new password reset.');
        }
    }, [token]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        setError('');
    };

    const validateForm = () => {
        if (!formData.password || !formData.confirmPassword) {
            setError('Please fill in all fields');
            return false;
        }

        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return false;
        }

        if (formData.password.length < 8) {
            setError('Password must be at least 8 characters long');
            return false;
        }

        return true;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (!token) {
            setError('Invalid reset link');
            return;
        }

        if (!validateForm()) {
            return;
        }

        setLoading(true);

        try {
            await apiService.resetPassword(token, formData.password);
            setSuccess(true);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to reset password');
        } finally {
            setLoading(false);
        }
    };

    if (!token) {
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

                {/* Error Content */}
                <div className="w-full max-w-md space-y-8 animate-fade-in relative z-10">
                    <div className="text-center">
                        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-r from-red-500 to-pink-500 mb-4 shadow-lg shadow-red-500/50">
                            <AlertCircle className="w-10 h-10 text-white" />
                        </div>
                        <h1 className="text-4xl font-bold gradient-text">Invalid Link</h1>
                        <p className="mt-2 text-gray-300">This password reset link is invalid or has expired.</p>
                    </div>

                    <Card className="bg-white/10 dark:bg-white/5 backdrop-blur-xl border-white/20 dark:border-white/10">
                        <div className="text-center space-y-4">
                            <p className="text-white">
                                Please request a new password reset link.
                            </p>
                            <div className="space-y-3">
                                <Link to="/forgot-password">
                                    <Button variant="primary" className="w-full">
                                        Request New Reset Link
                                    </Button>
                                </Link>
                                <Link to="/login">
                                    <Button variant="secondary" className="w-full">
                                        Back to Login
                                    </Button>
                                </Link>
                            </div>
                        </div>
                    </Card>
                </div>
            </div>
        );
    }

    if (success) {
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

                {/* Success Content */}
                <div className="w-full max-w-md space-y-8 animate-fade-in relative z-10">
                    <div className="text-center">
                        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-r from-green-500 to-emerald-500 mb-4 shadow-lg shadow-green-500/50">
                            <CheckCircle className="w-10 h-10 text-white" />
                        </div>
                        <h1 className="text-4xl font-bold gradient-text">Password Reset!</h1>
                        <p className="mt-2 text-gray-300">Your password has been successfully reset.</p>
                    </div>

                    <Card className="bg-white/10 dark:bg-white/5 backdrop-blur-xl border-white/20 dark:border-white/10">
                        <div className="text-center space-y-4">
                            <p className="text-white">
                                You can now login with your new password.
                            </p>
                            <div className="pt-4">
                                <Button 
                                    variant="primary" 
                                    className="w-full"
                                    onClick={() => navigate('/login')}
                                >
                                    Go to Login
                                </Button>
                            </div>
                        </div>
                    </Card>
                </div>
            </div>
        );
    }

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
                    <h1 className="text-4xl font-bold gradient-text">Set New Password</h1>
                    <p className="mt-2 text-gray-300">Enter your new password below.</p>
                </div>

                {/* Reset Form */}
                <Card className="bg-white/10 dark:bg-white/5 backdrop-blur-xl border-white/20 dark:border-white/10">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <Input
                            label="New Password"
                            type="password"
                            name="password"
                            value={formData.password}
                            onChange={handleInputChange}
                            placeholder="Enter your new password"
                            required
                        />

                        <Input
                            label="Confirm New Password"
                            type="password"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleInputChange}
                            placeholder="Confirm your new password"
                            required
                        />

                        {error && (
                            <div className="text-red-300 text-sm bg-red-500/20 border border-red-400/30 rounded-lg p-3">
                                {error}
                            </div>
                        )}

                        <Button
                            type="submit"
                            variant="primary"
                            className="w-full"
                            disabled={loading}
                        >
                            {loading ? 'Resetting...' : 'Reset Password'}
                        </Button>
                    </form>
                </Card>

                {/* Back to Login */}
                <div className="text-center">
                    <p className="text-gray-300 text-sm">
                        Remember your password?{' '}
                        <Link 
                            to="/login" 
                            className="text-purple-300 hover:text-purple-200 smooth-transition font-medium"
                        >
                            Back to Login
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}