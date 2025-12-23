import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import { Package, Camera, MapPin, CheckCircle, AlertTriangle, XCircle, Send, Loader2 } from 'lucide-react';
import { customerApiService } from '@/lib/customerApi';
import { DeliveryStatus } from '@/types';


export default function MaterialDeliveryConfirmation() {
    const { token } = useParams<{ token: string }>();
    
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [deliveryData, setDeliveryData] = useState<any>(null);
    const [status, setStatus] = useState<DeliveryStatus | ''>('');
    const [photos, setPhotos] = useState<File[]>([]);
    const [notes, setNotes] = useState('');
    const [locationCaptured, setLocationCaptured] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        const fetchDeliveryData = async () => {
            if (!token) {
                setError('No delivery token provided');
                setLoading(false);
                return;
            }

            try {
                setLoading(true);
                setError(null);
                // For now, we'll use a mock response since this endpoint might not be implemented yet
                // const data = await customerApiService.getDeliveryDetails(token);
                const data = {
                    job_id: 101,
                    delivery_id: 'DEL-001',
                    materials: [
                        { name: 'Paint - White', quantity: 2, status: 'delivered' },
                        { name: 'Brushes', quantity: 3, status: 'delivered' }
                    ],
                    delivery_address: '123 Main St, Detroit, MI',
                    expected_delivery: new Date().toISOString()
                };
                setDeliveryData(data);
            } catch (err) {
                console.error('Failed to fetch delivery data:', err);
                setError(err instanceof Error ? err.message : 'Failed to load delivery details');
            } finally {
                setLoading(false);
            }
        };

        fetchDeliveryData();
    }, [token]);

    const handlePhotoUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files;
        if (files) {
            setPhotos([...photos, ...Array.from(files)]);
        }
    };

    const handleSubmit = async () => {
        if (!status) {
            alert("Please select a delivery status");
            return;
        }
        if (status !== 'Correct' && photos.length === 0) {
            alert("Please provide photos for issues");
            return;
        }
        if (!token) {
            alert("Invalid delivery token");
            return;
        }

        try {
            setSubmitting(true);
            
            const formData = new FormData();
            formData.append('status', status);
            formData.append('notes', notes);
            formData.append('location_verified', locationCaptured.toString());
            
            photos.forEach((photo, index) => {
                formData.append(`photo_${index}`, photo);
            });

            await customerApiService.confirmMaterialDeliveryByToken(token, formData);
            
            alert("Delivery confirmation submitted successfully!");
            // Could redirect to a success page or dashboard
        } catch (err) {
            console.error('Failed to submit delivery confirmation:', err);
            alert('Failed to submit confirmation. Please try again.');
        } finally {
            setSubmitting(false);
        }
    };

    const captureLocation = () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    setLocationCaptured(true);
                    alert("Location captured successfully");
                },
                (error) => {
                    console.error('Error getting location:', error);
                    alert("Could not capture location. Please try again.");
                }
            );
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    };

    if (loading) {
        return (
            <div className="max-w-2xl mx-auto flex items-center justify-center h-64">
                <div className="text-center">
                    <Loader2 className="w-8 h-8 animate-spin text-purple-600 mx-auto mb-4" />
                    <p className="text-gray-600">Loading delivery details...</p>
                </div>
            </div>
        );
    }

    if (error || !deliveryData) {
        return (
            <div className="max-w-2xl mx-auto">
                <Card className="text-center p-8">
                    <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Invalid Delivery Link</h2>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                        {error || 'The delivery confirmation link is invalid or has expired.'}
                    </p>
                    <Button onClick={() => window.location.reload()}>
                        Retry
                    </Button>
                </Card>
            </div>
        );
    }

    return (
        <div className="max-w-2xl mx-auto space-y-6 animate-fade-in pb-20">

            <div className="text-center mb-8">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-purple-100 dark:bg-purple-900/30 mb-4">
                    <Package className="w-8 h-8 text-purple-600 dark:text-purple-400" />
                </div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Verify Your Delivery</h1>
                <p className="text-gray-500">Please inspect the items delivered to {deliveryData.delivery_address}</p>
                <p className="text-sm text-gray-400">Delivery ID: {deliveryData.delivery_id}</p>
            </div>

            {/* Materials List */}
            <Card>
                <div className="mb-4 font-bold text-lg border-b pb-2">Delivered Materials</div>
                <div className="space-y-2">
                    {deliveryData.materials?.map((material: any, index: number) => (
                        <div key={index} className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-800 rounded">
                            <span>{material.name}</span>
                            <span className="text-sm text-gray-500">Qty: {material.quantity}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* 1. Status Selection */}
            <Card>
                <div className="mb-4 font-bold text-lg border-b pb-2">1. Delivery Condition</div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {[
                        { id: 'Correct', label: 'All Items Correct', icon: <CheckCircle className="w-5 h-5" />, color: 'border-green-500 bg-green-50 text-green-700' },
                        { id: 'Missing Items', label: 'Missing Items', icon: <AlertTriangle className="w-5 h-5" />, color: 'border-amber-500 bg-amber-50 text-amber-700' },
                        { id: 'Damaged', label: 'Damaged Items', icon: <XCircle className="w-5 h-5" />, color: 'border-red-500 bg-red-50 text-red-700' },
                        { id: 'Wrong Items', label: 'Wrong Items', icon: <AlertTriangle className="w-5 h-5" />, color: 'border-orange-500 bg-orange-50 text-orange-700' },
                    ].map((option) => (
                        <button
                            key={option.id}
                            onClick={() => setStatus(option.id as DeliveryStatus)}
                            className={`p-4 rounded-xl border-2 flex items-center gap-3 transition-all ${status === option.id
                                ? option.color
                                : 'border-gray-200 hover:border-purple-200 hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800'
                                }`}
                        >
                            {option.icon}
                            <span className="font-medium">{option.label}</span>
                        </button>
                    ))}
                </div>
            </Card>

            {/* 2. Evidence Upload */}
            {(status && status !== 'Correct') && (
                <div className="animate-fade-in space-y-6">
                    <Card>
                        <div className="mb-4 font-bold text-lg border-b pb-2">2. Photo Evidence (Required)</div>
                        <div
                            className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-xl p-8 text-center hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer transition-colors"
                        >
                            <input
                                type="file"
                                multiple
                                accept="image/*"
                                onChange={handlePhotoUpload}
                                className="hidden"
                                id="photo-upload"
                            />
                            <label htmlFor="photo-upload" className="cursor-pointer">
                                <Camera className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                                <p className="font-medium text-gray-900 dark:text-white">Tap to take photo</p>
                                <p className="text-sm text-gray-500">or upload from gallery</p>
                            </label>
                        </div>

                        {photos.length > 0 && (
                            <div className="mt-4 grid grid-cols-3 gap-2">
                                {photos.map((photo, i) => (
                                    <div key={i} className="aspect-square bg-gray-200 rounded-lg flex items-center justify-center text-xs text-gray-500 relative group">
                                        {photo.name || `Photo ${i + 1}`}
                                        <button
                                            onClick={(e) => { e.stopPropagation(); setPhotos(photos.filter((_, idx) => idx !== i)); }}
                                            className="absolute top-1 right-1 bg-red-500 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                                        >
                                            <XCircle className="w-3 h-3" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </Card>

                    <Card>
                        <div className="mb-4 font-bold text-lg border-b pb-2">3. Additional Details</div>
                        <textarea
                            className="w-full rounded-xl border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 focus:ring-purple-500"
                            rows={4}
                            placeholder="Please describe exactly what is missing or damaged..."
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                        />
                    </Card>
                </div>
            )}

            {/* 4. GPS Verification */}
            <Card>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${locationCaptured ? 'bg-green-100 text-green-600' : 'bg-blue-100 text-blue-600'}`}>
                            <MapPin className="w-5 h-5" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-gray-900 dark:text-white">Location Verification</h3>
                            <p className="text-sm text-gray-500">
                                {locationCaptured ? "Location secured" : "We need to verify delivery location"}
                            </p>
                        </div>
                    </div>
                    {!locationCaptured && (
                        <Button size="sm" variant="outline" onClick={captureLocation}>
                            Allow GPS
                        </Button>
                    )}
                    {locationCaptured && (
                        <Badge variant="success">Verified</Badge>
                    )}
                </div>
            </Card>

            <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 p-4 border-t border-gray-100 dark:border-gray-800">
                <div className="max-w-2xl mx-auto">
                    <Button
                        className="w-full py-4 text-lg shadow-xl shadow-purple-500/20"
                        disabled={submitting || !status || (status !== 'Correct' && photos.length === 0)}
                        onClick={handleSubmit}
                    >
                        {submitting ? (
                            <>
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                Submitting...
                            </>
                        ) : (
                            <>
                                Confirm Delivery Status
                                <Send className="w-4 h-4 ml-2" />
                            </>
                        )}
                    </Button>
                </div>
            </div>

        </div>
    );
}
