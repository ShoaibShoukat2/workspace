# Investor Dashboard Frontend Integration Guide

## 🎯 **Complete API Integration for Investor Dashboard**

This guide provides the complete API integration for all investor dashboard pages to replace mock data with real backend calls.

### 📋 **Available API Endpoints**

All endpoints are prefixed with `/api/v1/investors/` and require investor authentication.

#### **Core Dashboard APIs**
- `GET /dashboard` - Main dashboard overview with metrics
- `GET /job-breakdowns` - Job breakdown data with filters
- `GET /performance` - Performance metrics and analytics
- `GET /portfolio` - Portfolio overview and statistics
- `GET /roi-analysis` - ROI analysis with time grouping
- `GET /payouts` - Payout history and status
- `GET /reports` - Generated reports list
- `POST /reports/generate` - Generate new reports

#### **Additional APIs**
- `GET /properties` - Investor properties list
- `GET /properties/{id}` - Property details
- `GET /leads` - Investment leads pipeline
- `POST /leads` - Create new lead
- `GET /earnings-breakdown` - Detailed earnings breakdown
- `GET /allocation-data` - Portfolio allocation for charts
- `GET /market-insights` - Market analysis and insights

### 🔧 **Frontend Integration Steps**

#### **1. InvestorDashboard.tsx Integration**

Replace mock data imports with API calls:

```typescript
// Remove mock data imports
// import { jobs as allJobs, investorJobBreakdown, investors, leads as initialLeads } from '@/data/mockData';

// Add API service
import { investorApi } from '@/services/api';

// Add state for API data
const [dashboardData, setDashboardData] = useState(null);
const [jobBreakdowns, setJobBreakdowns] = useState([]);
const [portfolioAllocation, setPortfolioAllocation] = useState([]);
const [earningsBreakdown, setEarningsBreakdown] = useState(null);
const [roiData, setRoiData] = useState([]);
const [loading, setLoading] = useState(true);

// Load data on component mount
useEffect(() => {
    const loadDashboardData = async () => {
        try {
            setLoading(true);
            
            // Load all dashboard data
            const [dashboard, breakdowns, allocation, earnings, roi] = await Promise.all([
                investorApi.getDashboard(),
                investorApi.getJobBreakdowns(),
                investorApi.getAllocationData(),
                investorApi.getEarningsBreakdown(),
                investorApi.getRoiAnalysis({ group_by: 'month' })
            ]);
            
            setDashboardData(dashboard);
            setJobBreakdowns(breakdowns);
            setPortfolioAllocation(allocation);
            setEarningsBreakdown(earnings);
            setRoiData(roi.roi_trend || []);
            
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };
    
    loadDashboardData();
}, []);

// Update metrics calculations
const activeProjects = dashboardData?.active_jobs || 0;
const totalRevenue = dashboardData?.total_revenue || 0;
const netProfit = earningsBreakdown?.investor_earnings || 0;
const avgRoi = dashboardData?.roi_percentage || 0;
```

#### **2. InvestorReports.tsx Integration**

Replace mock reports with API data:

```typescript
// Add API integration
import { investorApi } from '@/services/api';

const [reports, setReports] = useState([]);
const [loading, setLoading] = useState(true);

useEffect(() => {
    const loadReports = async () => {
        try {
            const reportsData = await investorApi.getReports();
            setReports(reportsData);
        } catch (error) {
            console.error('Failed to load reports:', error);
        } finally {
            setLoading(false);
        }
    };
    
    loadReports();
}, []);

// Add report generation
const handleGenerateReport = async (reportType: string) => {
    try {
        await investorApi.generateReport({
            report_type: reportType,
            date_from: null,
            date_to: null
        });
        
        // Refresh reports list
        const updatedReports = await investorApi.getReports();
        setReports(updatedReports);
        
        alert('Report generation started!');
    } catch (error) {
        console.error('Failed to generate report:', error);
        alert('Failed to generate report');
    }
};
```

#### **3. PropertyDetailView.tsx Integration**

Replace mock property data with API calls:

```typescript
// Add API integration
import { investorApi } from '@/services/api';

const [propertyData, setPropertyData] = useState(null);
const [loading, setLoading] = useState(true);

useEffect(() => {
    const loadPropertyData = async () => {
        if (!address) return;
        
        try {
            // In real implementation, you'd need property ID
            // For now, we'll use the address to find the property
            const properties = await investorApi.getProperties();
            const property = properties.find(p => p.address === decodedAddress);
            
            if (property) {
                const propertyDetails = await investorApi.getPropertyDetails(property.id);
                setPropertyData(propertyDetails);
            }
        } catch (error) {
            console.error('Failed to load property data:', error);
        } finally {
            setLoading(false);
        }
    };
    
    loadPropertyData();
}, [address]);

// Update calculations with real data
const totalRevenue = propertyData?.total_revenue || 0;
const totalProfit = propertyData?.total_profit || 0;
const activeJobs = propertyData?.active_jobs || 0;
const propertyJobs = propertyData?.jobs || [];
```

### 🔌 **API Service Implementation**

Create `src/services/investorApi.ts`:

```typescript
import { apiClient } from './api';

export const investorApi = {
    // Dashboard APIs
    getDashboard: () => apiClient.get('/investors/dashboard'),
    getJobBreakdowns: (params = {}) => apiClient.get('/investors/job-breakdowns', { params }),
    getPerformance: (params = {}) => apiClient.get('/investors/performance', { params }),
    getPortfolio: () => apiClient.get('/investors/portfolio'),
    getRoiAnalysis: (params = {}) => apiClient.get('/investors/roi-analysis', { params }),
    getMarketInsights: () => apiClient.get('/investors/market-insights'),
    
    // Payouts and Reports
    getPayouts: (params = {}) => apiClient.get('/investors/payouts', { params }),
    getReports: (params = {}) => apiClient.get('/investors/reports', { params }),
    generateReport: (data) => apiClient.post('/investors/reports/generate', data),
    
    // Properties
    getProperties: (params = {}) => apiClient.get('/investors/properties', { params }),
    getPropertyDetails: (propertyId) => apiClient.get(`/investors/properties/${propertyId}`),
    
    // Leads
    getLeads: (params = {}) => apiClient.get('/investors/leads', { params }),
    createLead: (data) => apiClient.post('/investors/leads', data),
    
    // Additional Data
    getEarningsBreakdown: () => apiClient.get('/investors/earnings-breakdown'),
    getAllocationData: () => apiClient.get('/investors/allocation-data'),
};
```

### 📊 **Data Structure Examples**

#### **Dashboard Response**
```json
{
    "total_investment": 50000.0,
    "current_balance": 45000.0,
    "total_revenue": 12500.0,
    "total_payouts": 8500.0,
    "roi_percentage": 25.0,
    "active_jobs": 3,
    "completed_jobs": 12,
    "pending_payouts": 1500.0,
    "monthly_revenue": [
        {"month": "Jan", "revenue": 2000},
        {"month": "Feb", "revenue": 2500}
    ],
    "job_performance": {
        "completion_rate": 95.0,
        "average_profit_margin": 18.5,
        "customer_satisfaction": 4.7
    }
}
```

#### **Job Breakdowns Response**
```json
[
    {
        "job_id": 101,
        "job_number": "JOB-101",
        "property_address": "123 Main St",
        "job_type": "Painting",
        "status": "COMPLETED",
        "investment_amount": 5000.0,
        "investor_share": 1200.0,
        "profit_margin": 24.0,
        "roi_percentage": 24.0,
        "completed_date": "2024-01-15"
    }
]
```

#### **Portfolio Allocation Response**
```json
[
    {"name": "Flips", "value": 65, "color": "#8b5cf6"},
    {"name": "Rentals", "value": 25, "color": "#ec4899"},
    {"name": "Commercial", "value": 10, "color": "#3b82f6"}
]
```

### 🔐 **Authentication Integration**

Ensure all API calls include proper authentication:

```typescript
// In your API client setup
const apiClient = axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth interceptor
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});
```

### 🎨 **UI Integration Tips**

#### **Loading States**
```typescript
// Add loading states to all components
{loading ? (
    <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
    </div>
) : (
    // Your content here
)}
```

#### **Error Handling**
```typescript
// Add error states
const [error, setError] = useState(null);

// In your API calls
try {
    const data = await investorApi.getDashboard();
    setDashboardData(data);
    setError(null);
} catch (err) {
    setError('Failed to load dashboard data');
    console.error(err);
}

// In your JSX
{error && (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
        <p className="text-red-700">{error}</p>
    </div>
)}
```

#### **Real-time Updates**
```typescript
// Add periodic refresh for live data
useEffect(() => {
    const interval = setInterval(() => {
        // Refresh critical data every 30 seconds
        loadDashboardData();
    }, 30000);
    
    return () => clearInterval(interval);
}, []);
```

### 🚀 **Implementation Checklist**

- [ ] Replace all mock data imports with API calls
- [ ] Add loading states to all components
- [ ] Implement error handling for API failures
- [ ] Add authentication headers to all requests
- [ ] Test all dashboard tabs with real data
- [ ] Verify charts render correctly with API data
- [ ] Test property detail navigation
- [ ] Verify report generation workflow
- [ ] Test lead creation functionality
- [ ] Add real-time data refresh capabilities

### 📈 **Performance Optimization**

1. **Data Caching**: Cache dashboard data for 5 minutes
2. **Lazy Loading**: Load property details only when needed
3. **Pagination**: Implement pagination for large data sets
4. **Debouncing**: Debounce search and filter inputs
5. **Error Boundaries**: Add React error boundaries for graceful failures

### 🎯 **Final Result**

After integration, the investor dashboard will:

- ✅ Display real-time investment data
- ✅ Show actual job breakdowns and performance
- ✅ Generate and download real reports
- ✅ Manage actual investment leads
- ✅ Display live portfolio allocation
- ✅ Show real earnings and payout data
- ✅ Provide accurate ROI analysis
- ✅ Support property management workflow

The investor dashboard will be fully functional with complete backend integration, providing investors with real-time insights into their investment performance and portfolio management capabilities.