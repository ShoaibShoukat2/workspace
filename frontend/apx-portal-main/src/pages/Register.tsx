import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Card from '@/components/ui/Card';
import { Home, CheckCircle } from 'lucide-react';

export default function Register() {
    const navigate = useNavigate();
    const { register, loading, error } = useAuth();
    const [formData, setFormData] = useState({
        email: '',
        username: '',
        password: '',
        confirmPassword: '',
        role: 'customer'
    });
    const [formError, setFormError] = useState('');
    const [success, setSuccess] = useState(false);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        setFormError('');
    };

    const validateForm = () => {
        if (!formData.email || !formData.username || !formData.password) {
            setFormError('All fields are required');
            return false;
        }

        if (formData.password !== formData.confirmPassword) {
            setFormError('Passwords do not match');
            return false;
        }

        if (formData.password.length < 8) {
            setFormError('Password must be at least 8 characters long');
            return false;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData.email)) {
            setFormError('Please enter a valid email address');
            return false;
        }

        return true;
    };

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setFormError('');

        if (!validateForm()) {
            return;
        }

        try {
            await register({
                email: formData.email,
                username: formData.username,
                password: formData.password,
                password2: formData.confirmPassword,
                role: formData.role
            });
            setSuccess(true);
        } catch (err) {
            setFormError(error || 'Registration failed. Please try again.');
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
                        <h1 className="text-4xl font-bold gradient-text">Registration Successful!</h1>
                        <p className="mt-2 text-gray-300">Please check your email to verify your account.</p>
                    </div>

                    <Card className="bg-white/10 dark:bg-white/5 backdrop-blur-xl border-white/20 dark:border-white/10">
                        <div className="text-center space-y-4">
                            <p className="text-white">
                                We've sent a verification email to <strong>{formData.email}</strong>
                            </p>
                            <p className="text-gray-300 text-sm">
                                Please click the verification link in your email to activate your account.
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
                    <h1 className="text-4xl font-bold gradient-text">Create Account</h1>
                    <p className="mt-2 text-gray-300">Join Apex Home Services today!</p>
                </div>

                {/* Registration Form */}
                <Card className="bg-white/10 dark:bg-white/5 backdrop-blur-xl border-white/20 dark:border-white/10">
                    <form onSubmit={handleRegister} className="space-y-6">
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
                            label="Username"
                            type="text"
                            name="username"
                            value={formData.username}
                            onChange={handleInputChange}
                            placeholder="Choose a username"
                            required
                        />

                        <div className="space-y-2">
                            <label className="block text-sm font-medium text-gray-200">
                                Role
                            </label>
                            <select
                                name="role"
                                value={formData.role}
                                onChange={handleInputChange}
                                className="w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                            >
                                <option value="customer" className="bg-gray-800">Customer</option>
                                <option value="contractor" className="bg-gray-800">Contractor</option>
                                <option value="fm" className="bg-gray-800">Field Manager</option>
                            </select>
                        </div>

                        <Input
                            label="Password"
                            type="password"
                            name="password"
                            value={formData.password}
                            onChange={handleInputChange}
                            placeholder="Create a password"
                            required
                        />

                        <Input
                            label="Confirm Password"
                            type="password"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleInputChange}
                            placeholder="Confirm your password"
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
                            {loading ? 'Creating Account...' : 'Create Account'}
                        </Button>

                        <div className="text-center">
                            <p className="text-gray-300 text-sm">
                                Already have an account?{' '}
                                <Link 
                                    to="/login" 
                                    className="text-purple-300 hover:text-purple-200 smooth-transition font-medium"
                                >
                                    Sign in here
                                </Link>
                            </p>
                        </div>
                    </form>
                </Card>

                {/* Terms and Privacy */}
                <div className="text-center">
                    <p className="text-gray-400 text-xs">
                        By creating an account, you agree to our{' '}
                        <a href="#" className="text-purple-300 hover:text-purple-200">Terms of Service</a>
                        {' '}and{' '}
                        <a href="#" className="text-purple-300 hover:text-purple-200">Privacy Policy</a>
                    </p>
                </div>
            </div>
        </div>
    );
}