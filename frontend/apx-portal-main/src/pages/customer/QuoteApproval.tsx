import { useNavigate, useParams } from 'react-router-dom';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import { getJobByToken, estimates, updateJobStatus } from '@/data/mockData';
import { Hammer, FileText, CheckCircle, AlertTriangle } from 'lucide-react';
import { formatCurrency } from '@/lib/utils';


export default function QuoteApproval() {
    const { token } = useParams<{ token: string }>();
    const navigate = useNavigate();

    // Default to 'mock-token-123' if the token from URL is invalid/missing during testing
    // This fallback ensures the demo always works even with a bad link
    const effectiveToken = token || 'mock-token-123';

    // We can lookup synchronously from mockData for this demo
    const job = getJobByToken(effectiveToken) || getJobByToken('mock-token-123');
    const estimate = job ? estimates.find(e => e.jobId === job.id) : undefined;
    const loading = false;

    // Derived state for line items (mock logic)
    // In a real app, these would come from the estimate.lineItems
    const materialItems = job?.materials || [];
    const laborMatches = estimate?.scopeOfWork.match(/Labor \((.*?) hours\)/);
    const laborHours = laborMatches ? parseFloat(laborMatches[1]) : (estimate?.hours || 0);

    const totalMaterialsCost = estimate?.materialEstimate || 0;
    const totalLaborCost = (estimate?.laborRate || 0) * (estimate?.hours || 0);

    const handleApprove = () => {
        if (job) {
            updateJobStatus(job.id, 'InProgress');
            navigate('/customer/credentials', {
                state: {
                    email: job.customerEmail,
                    password: 'temp-password-123'
                }
            });
        }
    };

    const handlePurchaseMaterials = () => {
        // Mock purchase flow
        window.open('https://www.homedepot.com', '_blank');
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
                <p className="text-gray-500">Loading quote...</p>
            </div>
        );
    }

    if (!job || !estimate) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
                <Card className="text-center p-8 max-w-md">
                    <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Invalid Quote Link</h2>
                    <p className="text-gray-600 dark:text-gray-400">
                        The quote link you used is invalid or has expired. Please contact your Field Manager.
                    </p>
                    <p className="text-xs text-gray-400 mt-4">Token: {token}</p>
                </Card>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4 md:p-8">
            <div className="max-w-4xl mx-auto space-y-6">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">Review Quote</h1>
                        <p className="text-gray-600 dark:text-gray-400">
                            For {job.propertyAddress}
                        </p>
                    </div>
                    <Badge variant="info" className="self-start md:self-auto">
                        Estimate #{estimate.id}
                    </Badge>
                </div>

                {/* Main Content */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Left Column: Scope & Line Items */}
                    <div className="md:col-span-2 space-y-6">
                        {/* Scope of Work */}
                        <Card>
                            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                                <FileText className="w-5 h-5 mr-2 text-purple-500" />
                                Scope of Work
                            </h2>
                            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-line">
                                {estimate.scopeOfWork}
                                {laborHours > 0 && `\n\nLabor: ~${laborHours} hours estimated.`}
                            </p>
                        </Card>

                        {/* Materials List */}
                        <Card>
                            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                                <Hammer className="w-5 h-5 mr-2 text-blue-500" />
                                Materials Breakdown
                            </h2>
                            {materialItems.length > 0 ? (
                                <div className="space-y-3">
                                    {materialItems.map((item, idx) => (
                                        <div key={idx} className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-800 last:border-0">
                                            <div>
                                                <p className="font-medium text-gray-900 dark:text-white">{item.name}</p>
                                                <p className="text-xs text-gray-500">Qty: {item.quantity}</p>
                                            </div>
                                            <div className="text-right">
                                                {/* Mock price per item calculation for display */}
                                                <p className="font-medium text-gray-900 dark:text-white">{formatCurrency(50 * item.quantity)}</p>
                                            </div>
                                        </div>
                                    ))}
                                    <div className="pt-2 flex justify-between font-bold text-gray-900 dark:text-white">
                                        <span>Total Materials</span>
                                        <span>{formatCurrency(totalMaterialsCost)}</span>
                                    </div>
                                </div>
                            ) : (
                                <p className="text-gray-500 italic">No specific materials listed.</p>
                            )}

                            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-100 dark:border-blue-800">
                                <h4 className="font-semibold text-blue-700 dark:text-blue-300 text-sm mb-1">
                                    Want to buy materials yourself?
                                </h4>
                                <p className="text-xs text-blue-600 dark:text-blue-400 mb-3">
                                    You can purchase these items directly from our partners to save on markup.
                                </p>
                                <Button
                                    size="sm"
                                    variant="outline"
                                    className="w-full bg-white dark:bg-gray-800"
                                    onClick={handlePurchaseMaterials}
                                >
                                    Purchase Materials Directly
                                </Button>
                            </div>
                        </Card>
                    </div>

                    {/* Right Column: Pricing & Approval */}
                    <div className="space-y-6">
                        <Card className="bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900 border-2 border-purple-100 dark:border-purple-900/50 shadow-lg">
                            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Quote Summary</h3>

                            <div className="space-y-3 mb-6">
                                <div className="flex justify-between text-gray-600 dark:text-gray-400">
                                    <span>Materials</span>
                                    <span>{formatCurrency(totalMaterialsCost)}</span>
                                </div>
                                <div className="flex justify-between text-gray-600 dark:text-gray-400">
                                    <span>Labor</span>
                                    <span>{formatCurrency(totalLaborCost)}</span>
                                </div>
                                <div className="flex justify-between text-gray-600 dark:text-gray-400">
                                    <span>Platform Fee</span>
                                    <span>{formatCurrency(estimate.price - totalMaterialsCost - totalLaborCost)}</span>
                                </div>
                                <div className="h-px bg-gray-200 dark:bg-gray-700 my-2" />
                                <div className="flex justify-between text-xl font-bold text-gray-900 dark:text-white">
                                    <span>Total</span>
                                    <span className="text-purple-600 dark:text-purple-400">{formatCurrency(estimate.price)}</span>
                                </div>
                            </div>

                            <div className="space-y-3">
                                <Button
                                    className="w-full text-lg py-6"
                                    variant="primary"
                                    onClick={handleApprove}
                                >
                                    <CheckCircle className="w-5 h-5 mr-2" />
                                    Approve Quote
                                </Button>
                                <Button
                                    className="w-full"
                                    variant="outline"
                                    onClick={() => alert('Please contact your Field Manager to discuss changes.')}
                                >
                                    Request Changes
                                </Button>
                            </div>

                            <p className="text-xs text-center text-gray-400 mt-4">
                                By approving, you agree to the Terms of Service and authorize the work to begin.
                            </p>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
}
