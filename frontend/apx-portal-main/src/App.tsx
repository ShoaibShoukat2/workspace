import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth, getDashboardRoute } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import AuthDebug from './components/AuthDebug';

// Pages - will be created next
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';

// Contractor Portal
import ContractorDashboard from './pages/contractor/ContractorDashboard';
import ComplianceHub from './pages/contractor/ComplianceHub';
import JobBoard from './pages/contractor/JobBoard';
import ActiveJobView from './pages/contractor/ActiveJobView';
import Wallet from './pages/contractor/Wallet';

// Field Manager Portal
import FMDashboard from './pages/fm/FMDashboard';
import FMJobVisit from './pages/fm/FMJobVisit';
import ChangeOrderForm from './pages/fm/ChangeOrderForm';

// Admin Portal
import AdminDashboard from './pages/admin/AdminDashboard';
import LegalCompliance from './pages/admin/LegalCompliance';
import DisputeList from './pages/admin/DisputeList';
import DisputeDetail from './pages/admin/DisputeDetail';
import Ledger from './pages/admin/Ledger';
import PayoutApproval from './pages/admin/PayoutApproval';
import InvestorAccounting from './pages/admin/InvestorAccounting';
import AdminJobList from './pages/admin/AdminJobList';
import AdminMeetings from './pages/admin/AdminMeetings';
import AdminLeads from './pages/admin/AdminLeads';

// Investor Portal
import InvestorDashboard from './pages/investor/InvestorDashboard';
import InvestorReports from './pages/investor/InvestorReports';
import PropertyDetailView from './pages/investor/PropertyDetailView';

// Customer Portal (Magic Links)
import QuoteApproval from './pages/customer/QuoteApproval';
import ReportIssue from './pages/customer/ReportIssue';
import MaterialPurchaseStatus from './pages/customer/MaterialPurchaseStatus';
import MaterialDeliveryConfirmation from './pages/customer/MaterialDeliveryConfirmation';
import CustomerTracker from './pages/customer/CustomerTracker';
import CustomerDashboard from './pages/customer/CustomerDashboard';
import CustomerCredentials from './pages/customer/CustomerCredentials';

function App() {
    const { isAuthenticated, currentUser } = useAuth();

    return (
        <div className="min-h-screen">
            <Routes>
                {/* Public Routes */}
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/forgot-password" element={<ForgotPassword />} />
                <Route path="/reset-password" element={<ResetPassword />} />
                <Route path="/track/:jobId" element={<CustomerTracker />} />

                {/* Contractor Portal */}
                <Route
                    path="/contractor/dashboard"
                    element={
                        <ProtectedRoute allowedRoles={['contractor']}>
                            <ContractorDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/contractor/compliance"
                    element={
                        <ProtectedRoute allowedRoles={['contractor']}>
                            <ComplianceHub />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/contractor/jobs"
                    element={
                        <ProtectedRoute allowedRoles={['contractor']}>
                            <JobBoard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/contractor/jobs/:jobId"
                    element={
                        <ProtectedRoute allowedRoles={['contractor']}>
                            <ActiveJobView />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/contractor/wallet"
                    element={
                        <ProtectedRoute allowedRoles={['contractor']}>
                            <Wallet />
                        </ProtectedRoute>
                    }
                />

                {/* Field Manager Portal */}
                <Route
                    path="/fm/dashboard"
                    element={
                        <ProtectedRoute allowedRoles={['fm']}>
                            <FMDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/fm/visits/:jobId"
                    element={
                        <ProtectedRoute allowedRoles={['fm']}>
                            <FMJobVisit />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/fm/visits/:jobId/change-order"
                    element={
                        <ProtectedRoute allowedRoles={['fm']}>
                            <ChangeOrderForm />
                        </ProtectedRoute>
                    }
                />

                {/* Admin Portal */}
                <Route
                    path="/admin/dashboard"
                    element={
                        <ProtectedRoute allowedRoles={['admin']}>
                            <AdminDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/legal-compliance"
                    element={
                        <ProtectedRoute allowedRoles={['admin']}>
                            <LegalCompliance />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/disputes"
                    element={
                        <ProtectedRoute allowedRoles={['admin']}>
                            <DisputeList />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/disputes/:disputeId"
                    element={
                        <ProtectedRoute allowedRoles={['admin']}>
                            <DisputeDetail />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/ledger"
                    element={
                        <ProtectedRoute allowedRoles={['admin']}>
                            <Ledger />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/payouts"
                    element={
                        <ProtectedRoute allowedRoles={['admin']}>
                            <PayoutApproval />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/investors"
                    element={
                        <ProtectedRoute allowedRoles={['admin']}>
                            <InvestorAccounting />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/jobs"
                    element={
                        <ProtectedRoute allowedRoles={['admin']}>
                            <AdminJobList />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/meetings"
                    element={
                        <ProtectedRoute allowedRoles={['admin']}>
                            <AdminMeetings />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/leads"
                    element={
                        <ProtectedRoute allowedRoles={['admin']}>
                            <AdminLeads />
                        </ProtectedRoute>
                    }
                />

                {/* Investor Portal */}
                <Route
                    path="/investor/dashboard"
                    element={
                        <ProtectedRoute allowedRoles={['investor']}>
                            <InvestorDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/investor/orders"
                    element={
                        <ProtectedRoute allowedRoles={['investor']}>
                            <InvestorDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/investor/properties"
                    element={
                        <ProtectedRoute allowedRoles={['investor']}>
                            <InvestorDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/investor/leads"
                    element={
                        <ProtectedRoute allowedRoles={['investor']}>
                            <InvestorDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/investor/reports"
                    element={
                        <ProtectedRoute allowedRoles={['investor']}>
                            <InvestorReports />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/investor/property/:address"
                    element={
                        <ProtectedRoute allowedRoles={['investor']}>
                            <PropertyDetailView />
                        </ProtectedRoute>
                    }
                />

                {/* Customer Portal */}
                <Route
                    path="/customer/dashboard"
                    element={
                        <ProtectedRoute allowedRoles={['customer']}>
                            <CustomerDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route path="/materials/:token" element={<MaterialPurchaseStatus />} />
                <Route path="/materials/:token/delivery" element={<MaterialDeliveryConfirmation />} />
                <Route path="/issue/:token" element={<ReportIssue />} />

                {/* Public Magic Links */}
                <Route path="/quote/:token" element={<QuoteApproval />} />
                <Route path="/customer/credentials" element={<CustomerCredentials />} />

                {/* Redirect root to login or dashboard based on auth */}
                <Route 
                    path="/" 
                    element={
                        isAuthenticated && currentUser ? 
                        <Navigate to={getDashboardRoute(currentUser.role)} replace /> : 
                        <Navigate to="/login" replace />
                    } 
                />
                <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
            <AuthDebug />
        </div >
    );
}

export default App;
