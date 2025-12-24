
import { useNavigate, useLocation } from 'react-router-dom';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { CheckCircle, Copy, Lock, ArrowRight, ShieldCheck } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { getUserByEmail } from '@/data/mockData';

export default function CustomerCredentials() {
    const navigate = useNavigate();
    const location = useLocation();
    const { login } = useAuth();

    // Determine valid email: use passed email if valid user exists, otherwise default to demo customer
    const passedEmail = location.state?.email;
    const isValidUser = passedEmail && getUserByEmail(passedEmail);
    const emailToUse = isValidUser ? passedEmail : 'customer@apex.com';

    // In a real app, these would come from the backend response after approval
    const tempCredentials = {
        email: emailToUse,
        password: 'apex-temp-pass',
        portalLink: window.location.origin + '/customer/dashboard'
    };

    const handleCopy = (text: string) => {
        navigator.clipboard.writeText(text);
        alert('Copied to clipboard!');
    };

    const handleDirectAccess = async () => {
        try {
            // Mock auto-login for the smooth flow
            await login(tempCredentials.email);
            navigate('/customer/dashboard');
        } catch (error) {
            console.error(error);
            alert("Login failed: User mismatch. Please ensure the quote email matches a registered user.");
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4">
            <div className="max-w-md w-full animate-fade-in">
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 text-green-600 mb-4 shadow-lg shadow-green-500/20 animate-scale-in">
                        <CheckCircle className="w-8 h-8" />
                    </div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Quote Approved!</h1>
                    <p className="text-gray-600 dark:text-gray-400">
                        Your project has been officially started. We've created a secure portal for you to track progress.
                    </p>
                </div>

                <Card className="border-t-4 border-t-purple-500 shadow-2xl">
                    <div className="p-6 space-y-6">
                        <div className="flex items-center gap-3 text-purple-700 dark:text-purple-300 bg-purple-50 dark:bg-purple-900/20 p-4 rounded-xl">
                            <ShieldCheck className="w-6 h-6 flex-shrink-0" />
                            <div className="text-sm">
                                <span className="font-bold block">Secure Access Created</span>
                                Use these credentials to access your dashboard anytime.
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Username / Email</label>
                                <div className="mt-1 flex gap-2">
                                    <code className="flex-1 bg-gray-100 dark:bg-gray-800 p-3 rounded-lg text-gray-800 dark:text-gray-200 font-mono">
                                        {tempCredentials.email}
                                    </code>
                                    <Button variant="outline" size="sm" onClick={() => handleCopy(tempCredentials.email)}>
                                        <Copy className="w-4 h-4" />
                                    </Button>
                                </div>
                            </div>

                            <div>
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Temporary Password</label>
                                <div className="mt-1 flex gap-2">
                                    <code className="flex-1 bg-gray-100 dark:bg-gray-800 p-3 rounded-lg text-gray-800 dark:text-gray-200 font-mono">
                                        {tempCredentials.password}
                                    </code>
                                    <Button variant="outline" size="sm" onClick={() => handleCopy(tempCredentials.password)}>
                                        <Copy className="w-4 h-4" />
                                    </Button>
                                </div>
                            </div>
                        </div>

                        <div className="pt-4 border-t border-gray-100 dark:border-gray-800">
                            <Button
                                className="w-full h-12 text-lg shadow-xl shadow-purple-500/20"
                                onClick={handleDirectAccess}
                            >
                                <Lock className="w-4 h-4 mr-2" />
                                Access Portal Now
                                <ArrowRight className="w-4 h-4 ml-2" />
                            </Button>
                            <p className="text-xs text-center text-gray-400 mt-4">
                                You can change your password in the Settings tab later.
                            </p>
                        </div>
                    </div>
                </Card>
            </div>
        </div>
    );
}
