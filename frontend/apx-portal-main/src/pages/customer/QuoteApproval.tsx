import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import { customerApiService } from '@/lib/customerApi';
import { Hammer, FileText, CheckCircle, AlertTriangle, Loader2 } from 'lucide-react';
import { formatCurrency } from '@/lib/utils';


export default function QuoteApproval() {
    const { token } = useParams<{ token: string }>();
    const navigate = useNavigate();
    
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [quoteData, setQuoteData] = useState<any>(null);
    const [processing, setProcessing] = useState(false);

    useEffect(() => {
        const fetchQuoteData = async () => {
            if (!token) {
                setError('No quote token provided');
                setLoading(false);
                return;
            }

            try {
                setLoading(true);
                setError(null);
                const data = await customerApiService.validateQuoteToken(token);
                setQuoteData(data);
            } catch (err) {
                console.error('Failed to fetch quote data:', err);
                setError(err instanceof Error ? err.message : 'Failed to load quote');
            } finally {
                setLoading(false);
            }
        };

        fetchQuoteData();
    }, [token]);

    const handleApprove = async () => {
        if (!token || !quoteData) return;

        try {
            setProcessing(true);
            await customerApiService.approveQuote(token, {
                approved: true,
                signature: 'Digital Signature',
                timestamp: new Date().toISOString()
            });
            
            navigate('/customer/credentials', {
                state: {
                    email: quoteData.customer_email,
                    message: 'Quote approved successfully! Your job will begin soon.'
                }
            });
        } catch (err) {
            console.error('Failed to approve quote:', err);
            alert('Failed to approve quote. Please try again.');
        } finally {
            setProcessing(false);
        }
    };

    const handleReject = async () => {
        const reason = prompt('Please provide a reason for rejecting this quote:');
        if (!reason || !token) return;

        try {
            setProcessing(true);
            await customerApiService.approveQuote(token, {
                approved: false,
                rejection_reason: reason,
                timestamp: new Date().toISOString()
            });
            
            alert('Quote rejected. Your Field Manager will contact you soon.');
            navigate('/');
        } catch (err) {
            console.error('Failed to reject quote:', err);
            alert('Failed to reject quote. Please try again.');
        } finally {
            setProcessing(false);
        }
    };

    const handlePurchaseMaterials = () => {
        // Mock purchase flow
        window.open('https://www.homedepot.com', '_blank');
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
                <div className="text-center">
                    <Loader2 className="w-8 h-8 animate-spin text-purple-600 mx-auto mb-4" />
                    <p className="text-gray-500">Loading quote...</p>
                </div>
            </div>
        );
    }

    if (error || !quoteData) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
                <Card className="text-center p-8 max-w-md">
                    <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Invalid Quote Link</h2>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                        {error || 'The quote link you used is invalid or has expired. Please contact your Field Manager.'}
                    </p>
                    <p className="text-xs text-gray-400 mt-4">Token: {token}</p>
                    <Button onClick={() => window.location.reload()} className="mt-4">
                        Retry
                    </Button>
                </Card>
            </div>
        );
    }

    // Extract data from API response
    const job = quoteData.job || quoteData;
    const estimate = quoteData.estimate || quoteData;
    const materialItems = job.materials || estimate.line_items || [];
    const laborHours = estimate.labor_hours || estimate.hours || 0;
    const totalMaterialsCost = estimate.material_cost || estimate.materialEstimate || 0;
    const totalLaborCost = estimate.labor_cost || ((estimate.labor_rate || 0) * laborHours);
    const totalPrice = estimate.total_price || estimate.price || 0;

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4 md:p-8">
            <div className="max-w-4xl mx-auto space-y-6">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">Review Quote</h1>
                        <p className="text-gray-600 dark:text-gray-400">
                            For {job.property_address || job.propertyAddress}
                        </p>
                    </div>
                    <Badge variant="info" className="self-start md:self-auto">
                        Estimate #{estimate.id || estimate.estimate_id}
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
                                {estimate.scope_of_work || estimate.scopeOfWork}
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
                                    {materialItems.map((item: any, idx: number) => (
                                        <div key={idx} className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-800 last:border-0">
                                            <div>
                                                <p className="font-medium text-gray-900 dark:text-white">{item.name || item.description}</p>
                                                <p className="text-xs text-gray-500">Qty: {item.quantity}</p>
                                            </div>
                                            <div className="text-right">
                                                <p className="font-medium text-gray-900 dark:text-white">{formatCurrency(item.cost || item.price || (50 * item.quantity))}</p>
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
                                    <span>{formatCurrency(totalPrice - totalMaterialsCost - totalLaborCost)}</span>
                                </div>
                                <div className="h-px bg-gray-200 dark:bg-gray-700 my-2" />
                                <div className="flex justify-between text-xl font-bold text-gray-900 dark:text-white">
                                    <span>Total</span>
                                    <span className="text-purple-600 dark:text-purple-400">{formatCurrency(totalPrice)}</span>
                                </div>
                            </div>

                            <div className="space-y-3">
                                <Button
                                    className="w-full text-lg py-6"
                                    variant="primary"
                                    onClick={handleApprove}
                                    disabled={processing}
                                >
                                    {processing ? (
                                        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                                    ) : (
                                        <CheckCircle className="w-5 h-5 mr-2" />
                                    )}
                                    Approve Quote
                                </Button>
                                <Button
                                    className="w-full"
                                    variant="outline"
                                    onClick={handleReject}
                                    disabled={processing}
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
