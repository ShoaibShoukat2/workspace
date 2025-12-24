import LayoutShell from '@/components/customerPortal/LayoutShell';
import { useAuth } from '@/context/AuthContext';
import '@/styles/customerPortal.css';

// This is the main Customer Dashboard (Single Job Page)
export default function CustomerJobView() {
    const { currentUser } = useAuth();

    return (
        <div className="customer-portal antialiased selection:bg-emerald-500/30 selection:text-emerald-100 h-screen flex flex-col overflow-hidden bg-slate-950">
            <LayoutShell customerName={currentUser?.name} />
        </div>
    );
}

