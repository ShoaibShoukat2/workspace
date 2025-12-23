import { Outlet, useParams } from 'react-router-dom';
import PortalLayout from '@/components/PortalLayout';
import { MapPin, Package, AlertTriangle, FileText, CheckCircle, Layers } from 'lucide-react';

export default function CustomerPortalLayout() {
    // In a real app, this would come from the active job context or auth
    // For this demo, we use the hardcoded token or get it from params if possible, 
    // but deeper links might need it. We'll default to the demo one for navigation consistency.
    const magicToken = 'demo-token-101';

    const navItems = [
        { label: 'Dashboard', path: '/customer/dashboard', icon: <MapPin className="w-5 h-5" /> },
        { label: 'Materials', path: `/materials/${magicToken}`, icon: <Layers className="w-5 h-5" /> },
        { label: 'Delivery', path: `/materials/${magicToken}/delivery`, icon: <CheckCircle className="w-5 h-5" /> },
        { label: 'Support', path: `/issue/${magicToken}`, icon: <AlertTriangle className="w-5 h-5" /> },
        { label: 'Quote', path: `/quote/${magicToken}`, icon: <FileText className="w-5 h-5" /> },
    ];

    return (
        <PortalLayout title="My Home Project" navItems={navItems}>
            <Outlet />
        </PortalLayout>
    );
}
