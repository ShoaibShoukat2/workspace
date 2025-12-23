import { useState } from 'react';
import { Link } from 'react-router-dom';
import { apiService } from '@/lib/api';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Card from '@/components/ui/Card';
import { Home, Mail, CheckCircle } from 'lucide-react';

export default function ForgotPassword() {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        if (!email) {
            setError('Please enter your email address');
            setLoading(false);
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            setError('Please enter a valid email address');
            setLoading(false);
            return;
        }

        try {
            await apiService.requestPasswordReset(email);
            setSuccess(true);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to send reset email');
        } finally {
            setLoading(false);
        }
    };

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
                        <h1 className="text-4xl font-bold gradient-text">Email Sent!</h1>
                        <p className="mt-2 text-gray-300">Check your inbox for password reset instructions.</p>
                    </div>

                    <Card className="bg-white/10 dark:bg-white/5 backdrop-blur-xl border-white/20 dark:border-white/10">
                        <div className="text-center space-y-4">
                            <Mail className="w-12 h-12 text-purple-300 mx-auto" />
                            <p className="text-white">
                                We've sent a password reset link to <strong>{email}</strong>
                            </p>
                            <p className="text-gray-300 text-sm">
                                Please check your email and click the reset link to create a new password.
                            </p>
                            <div className="pt-4">
                                <Link to="/login">
                                    <Button variant="primary" className="w-full">
                                        Back to Login
                                    </Button>
                                </Link>
                            </div>
                        </div>
                    </Card>

                    <div className="text-center">
                        <p className="text-gray-400 text-sm">
                            Didn't receive the email? Check your spam folder or{' '}
                            <button 
                                onClick={() => setSuccess(false)}
                                className="text-purple-300 hover:text-purple-200 smooth-transition"
                            >
                                try again
                            </button>
                        </p>
                    </div>
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
                    <h1 className="text-4xl font-bold gradient-text">Reset Password</h1>
                    <p className="mt-2 text-gray-300">Enter your email to receive reset instructions.</p>
                </div>

                {/* Reset Form */}
                <Card className="bg-white/10 dark:bg-white/5 backdrop-blur-xl border-white/20 dark:border-white/10">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <Input
                            label="Email Address"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Enter your email address"
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
                            {loading ? 'Sending...' : 'Send Reset Link'}
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