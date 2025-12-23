import { useAuth } from '@/context/AuthContext';

export default function AuthDebug() {
    const { currentUser, isAuthenticated, loading, error } = useAuth();

    if (process.env.NODE_ENV !== 'development') {
        return null;
    }

    return (
        <div className="fixed bottom-4 right-4 bg-black/80 text-white p-4 rounded-lg text-xs max-w-sm">
            <h4 className="font-bold mb-2">Auth Debug</h4>
            <div>Loading: {loading ? 'true' : 'false'}</div>
            <div>Authenticated: {isAuthenticated ? 'true' : 'false'}</div>
            <div>User: {currentUser ? currentUser.email : 'null'}</div>
            <div>Role: {currentUser ? `"${currentUser.role}"` : 'null'}</div>
            <div>Role Type: {currentUser ? typeof currentUser.role : 'null'}</div>
            <div>Error: {error || 'none'}</div>
        </div>
    );
}