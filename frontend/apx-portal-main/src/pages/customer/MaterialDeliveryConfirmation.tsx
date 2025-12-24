import { useState } from 'react';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import { Package, Camera, MapPin, CheckCircle, AlertTriangle, XCircle, Send } from 'lucide-react';
import { updateMaterialDeliveryStatus } from '@/data/mockData';
import { DeliveryStatus } from '@/types';


export default function MaterialDeliveryConfirmation() {
    // Mock Data
    const jobId = 101;
    const [status, setStatus] = useState<DeliveryStatus | ''>('');
    const [photos, setPhotos] = useState<string[]>([]);
    const [notes, setNotes] = useState('');
    const [locationCaptured, setLocationCaptured] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    const handlePhotoUpload = () => {
        // Simulate upload
        const newPhoto = `photo_${Date.now()}.jpg`;
        setPhotos([...photos, newPhoto]);
        alert("Photo uploaded successfully");
    };

    const handleSubmit = () => {
        if (!status) {
            alert("Please select a delivery status");
            return;
        }
        if (status !== 'Correct' && photos.length === 0) {
            alert("Please provide photos for issues");
            return;
        }

        setSubmitting(true);

        // Mock API call
        setTimeout(() => {
            updateMaterialDeliveryStatus(jobId, status as DeliveryStatus, photos, locationCaptured ? { latitude: 42.3314, longitude: -83.0458 } : undefined);
            setSubmitting(false);
            alert("Delivery confirmation submitted!");
            // Redirect or show success state
        }, 1500);
    };

    return (
        <div className="max-w-2xl mx-auto space-y-6 animate-fade-in pb-20">

            <div className="text-center mb-8">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-purple-100 dark:bg-purple-900/30 mb-4">
                    <Package className="w-8 h-8 text-purple-600 dark:text-purple-400" />
                </div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Verify Your Delivery</h1>
                <p className="text-gray-500">Please inspect the items delivered to your property.</p>
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
                            onClick={handlePhotoUpload}
                            className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-xl p-8 text-center hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer transition-colors"
                        >
                            <Camera className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                            <p className="font-medium text-gray-900 dark:text-white">Tap to take photo</p>
                            <p className="text-sm text-gray-500">or upload from gallery</p>
                        </div>

                        {photos.length > 0 && (
                            <div className="mt-4 grid grid-cols-3 gap-2">
                                {photos.map((_, i) => (
                                    <div key={i} className="aspect-square bg-gray-200 rounded-lg flex items-center justify-center text-xs text-gray-500 relative group">
                                        Photo {i + 1}
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
                        <Button size="sm" variant="outline" onClick={() => { setLocationCaptured(true); alert("Location captured"); }}>
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
                        {submitting ? 'Submitting...' : 'Confirm Delivery Status'}
                        <Send className="w-4 h-4 ml-2" />
                    </Button>
                </div>
            </div>

        </div>
    );
}
