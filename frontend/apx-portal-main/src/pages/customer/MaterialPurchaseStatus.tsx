import MaterialsReadOnlyList from '@/components/customer/MaterialsReadOnlyList';

export default function MaterialPurchaseStatus() {
    return (
        <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Project Materials</h1>

            {/* Using the shared component to ensure it matches the dashboard widget exactly ("sinked") */}
            <MaterialsReadOnlyList />
        </div>
    );
}
