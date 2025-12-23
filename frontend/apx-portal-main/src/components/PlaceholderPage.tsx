export default function PlaceholderPage({ title }: { title: string }) {
    return (
        <div className="min-h-screen p-8">
            <div className="max-w-7xl mx-auto">
                <h1 className="text-4xl font-bold gradient-text mb-4">{title}</h1>
                <div className="glass-card p-8 text-center">
                    <p className="text-gray-300 text-lg">This page is under construction.</p>
                    <p className="text-gray-400 mt-2">Coming soon!</p>
                </div>
            </div>
        </div>
    );
}
