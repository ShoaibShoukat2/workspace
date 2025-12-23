# API Integration Checklist

## ✅ Completed

### Authentication & Core
- [x] Login endpoint fixed (`/workspace/auth/login/`)
- [x] Register endpoint fixed (`/authentication/register/`)
- [x] Logout endpoint fixed (`/authentication/logout/`)
- [x] Current user endpoint fixed (`/workspace/auth/user/`)
- [x] Token management in AuthContext updated
- [x] User role mapping corrected (admin, fm, contractor, investor, customer)

### API Service Files
- [x] `src/lib/api.ts` - Authentication service
- [x] `src/lib/adminApi.ts` - Admin Dashboard API
- [x] `src/lib/contractorApi.ts` - Contractor Dashboard API
- [x] `src/lib/fmApi.ts` - Field Manager Dashboard API
- [x] `src/lib/investorApi.ts` - Investor Dashboard API
- [x] `src/lib/customerApi.ts` - Customer Dashboard API (enhanced)

### Documentation
- [x] `MISSING_APIS_INTEGRATION.md` - Comprehensive status report
- [x] `API_IMPLEMENTATION_GUIDE.md` - Code examples for each dashboard

---

## ⏳ To Do - Dashboard Integration

### Admin Portal

#### AdminDashboard
- [ ] Replace mock `disputes` with `adminApiService.getDisputes()`
- [ ] Replace mock `contractorPayouts` with `adminApiService.getPayouts()`
- [ ] Replace mock `jobs` with `adminApiService.getJobs()`
- [ ] Call `adminApiService.getDashboardStats()` for KPIs
- [ ] Update stat cards with API data
- [ ] Implement pagination for job/dispute lists

**Location**: `src/pages/admin/AdminDashboard.tsx`
**Required Methods**:
```typescript
- adminApiService.getDashboardStats()
- adminApiService.getJobs({ status?, limit, offset })
- adminApiService.getDisputes({ status?, limit, offset })
- adminApiService.getPayouts({ status?, limit, offset })
```

#### AdminJobList
- [ ] Implement job list with search/filter
- [ ] Add pagination
- [ ] Implement job detail view
- [ ] Add job action buttons (assign, close, etc.)

**Location**: `src/pages/admin/AdminJobList.tsx`
**Required Methods**:
```typescript
- adminApiService.getJobs()
- adminApiService.getJobDetail(jobId)
```

#### PayoutApproval
- [ ] Load pending payouts from API
- [ ] Implement approve/reject functionality
- [ ] Add batch approval feature
- [ ] Display payout history

**Location**: `src/pages/admin/PayoutApproval.tsx`
**Required Methods**:
```typescript
- adminApiService.getPayouts({ status: 'Processing' })
- adminApiService.approveJobPayout(jobId)
- adminApiService.rejectJobPayout(jobId, reason)
```

#### LegalCompliance
- [ ] Load compliance documents from API
- [ ] Implement approve/reject functionality
- [ ] Add expiring compliance alerts
- [ ] Display compliance analytics

**Location**: `src/pages/admin/LegalCompliance.tsx`
**Required Methods**:
```typescript
- adminApiService.getCompliance()
- adminApiService.approveCompliance(complianceId)
- adminApiService.rejectCompliance(complianceId, reason)
```

#### DisputeList & DisputeDetail
- [ ] Load disputes from API
- [ ] Implement dispute messaging
- [ ] Add escalation functionality
- [ ] Display resolution history

**Location**: `src/pages/admin/DisputeList.tsx`, `src/pages/admin/DisputeDetail.tsx`
**Required Methods**:
```typescript
- adminApiService.getDisputes()
- adminApiService.getDisputeDetail(disputeId)
```

#### AdminLeads
- [ ] Load leads from API
- [ ] Implement lead filtering and search
- [ ] Add conversion tracking
- [ ] Display lead analytics

**Location**: `src/pages/admin/AdminLeads.tsx`
**Required Methods**:
```typescript
- adminApiService.getLeads()
```

#### InvestorAccounting
- [ ] Load investor accounting data from API
- [ ] Display financial summaries
- [ ] Implement reporting

**Location**: `src/pages/admin/InvestorAccounting.tsx`

#### Ledger
- [ ] Load ledger transactions from API
- [ ] Implement transaction filtering
- [ ] Add export functionality

**Location**: `src/pages/admin/Ledger.tsx`

---

### Contractor Portal

#### ContractorDashboard
- [ ] Call `contractorApiService.getDashboard()`
- [ ] Call `contractorApiService.getActiveJobs()`
- [ ] Call `contractorApiService.getWallet()` for earnings
- [ ] Update compliance banner status from API
- [ ] Display available jobs count

**Location**: `src/pages/contractor/ContractorDashboard.tsx`
**Required Methods**:
```typescript
- contractorApiService.getDashboard()
- contractorApiService.getActiveJobs()
- contractorApiService.getWallet()
```

#### JobBoard
- [ ] Call `contractorApiService.getAssignments()`
- [ ] Implement accept/reject job functionality
- [ ] Add job filtering by category/location
- [ ] Show job details preview

**Location**: `src/pages/contractor/JobBoard.tsx`
**Required Methods**:
```typescript
- contractorApiService.getAssignments()
- contractorApiService.acceptJob(jobId)
- contractorApiService.rejectJob(jobId)
```

#### ActiveJobView
- [ ] Call `contractorApiService.getJobDetail(jobId)`
- [ ] Implement checklist updates
- [ ] Add media upload functionality
- [ ] Display job progress timeline
- [ ] Implement job completion submission

**Location**: `src/pages/contractor/ActiveJobView.tsx`
**Required Methods**:
```typescript
- contractorApiService.getJobDetail(jobId)
- contractorApiService.updateChecklist(jobId, stepId, data)
- contractorApiService.uploadStepMedia(stepId, formData)
- contractorApiService.submitJobCompletion(jobId, data)
```

#### Wallet
- [ ] Call `contractorApiService.getWallet()`
- [ ] Call `contractorApiService.getWalletTransactions()`
- [ ] Implement payout request feature
- [ ] Display transaction history with filters
- [ ] Add download ledger functionality

**Location**: `src/pages/contractor/Wallet.tsx`
**Required Methods**:
```typescript
- contractorApiService.getWallet()
- contractorApiService.getWalletTransactions(limit)
- contractorApiService.requestPayout(amount)
```

#### ComplianceHub
- [ ] Call `contractorApiService.getCompliance()`
- [ ] Implement document upload functionality
- [ ] Show compliance status and expiry dates
- [ ] Add renewal reminders
- [ ] Display compliance statistics

**Location**: `src/pages/contractor/ComplianceHub.tsx`
**Required Methods**:
```typescript
- contractorApiService.getCompliance()
- contractorApiService.uploadCompliance(formData)
```

---

### Field Manager Portal

#### FMDashboard
- [ ] Call `fmApiService.getDashboard()`
- [ ] Call `fmApiService.getJobs()`
- [ ] Display job status breakdown
- [ ] Show pending estimates count
- [ ] Display pending site visits count

**Location**: `src/pages/fm/FMDashboard.tsx`
**Required Methods**:
```typescript
- fmApiService.getDashboard()
- fmApiService.getJobs({ limit: 10 })
```

#### FMJobVisit
- [ ] Call `fmApiService.getJobDetail(jobId)`
- [ ] Call `fmApiService.getSiteVisit(jobId)`
- [ ] Implement start/update/complete site visit
- [ ] Add photo upload functionality
- [ ] Implement notes management
- [ ] Show job checklist if applicable

**Location**: `src/pages/fm/FMJobVisit.tsx`
**Required Methods**:
```typescript
- fmApiService.getJobDetail(jobId)
- fmApiService.getSiteVisit(jobId)
- fmApiService.startSiteVisit(jobId, data)
- fmApiService.updateSiteVisit(jobId, data)
- fmApiService.completeSiteVisit(jobId)
- fmApiService.uploadSiteVisitPhoto(jobId, formData)
```

#### ChangeOrderForm
- [ ] Call `fmApiService.createChangeOrder(jobId, data)`
- [ ] Implement form validation
- [ ] Add line items for change order
- [ ] Show cost impact
- [ ] Send to customer for approval

**Location**: `src/pages/fm/ChangeOrderForm.tsx`
**Required Methods**:
```typescript
- fmApiService.createChangeOrder(jobId, data)
```

#### FM Job Management (new page if needed)
- [ ] List all FM jobs
- [ ] Implement job creation
- [ ] Manage job assignments
- [ ] Track job status
- [ ] View job timeline

**Required Methods**:
```typescript
- fmApiService.getJobs()
- fmApiService.createJob(data)
- fmApiService.getJobDetail(jobId)
```

#### FM Estimate Management (new page if needed)
- [ ] List estimates
- [ ] Create new estimates
- [ ] Add/edit line items
- [ ] Send estimates to customers
- [ ] Track customer signatures

**Required Methods**:
```typescript
- fmApiService.getEstimates()
- fmApiService.getEstimateDetail(estimateId)
- fmApiService.createEstimate(jobId, data)
- fmApiService.addLineItem(estimateId, data)
- fmApiService.updateLineItem(itemId, data)
- fmApiService.deleteLineItem(itemId)
- fmApiService.sendEstimate(estimateId)
```

---

### Investor Portal

#### InvestorDashboard
- [ ] Call `investorApiService.getDashboard()`
- [ ] Call `investorApiService.getProperties()`
- [ ] Call `investorApiService.getRevenueStatistics()`
- [ ] Display KPI cards
- [ ] Show portfolio overview
- [ ] Display property grid

**Location**: `src/pages/investor/InvestorDashboard.tsx`
**Required Methods**:
```typescript
- investorApiService.getDashboard()
- investorApiService.getProperties()
- investorApiService.getRevenueStatistics('6m')
- investorApiService.getROIAnalytics()
- investorApiService.getJobCategoryBreakdown()
```

#### PropertyDetailView
- [ ] Call `investorApiService.getPropertyDetail(propertyId)`
- [ ] Display property metrics
- [ ] Show jobs associated with property
- [ ] Display performance analytics
- [ ] Show revenue breakdown by category

**Location**: `src/pages/investor/PropertyDetailView.tsx`
**Required Methods**:
```typescript
- investorApiService.getPropertyDetail(propertyId)
```

#### InvestorReports
- [ ] Call analytics methods
- [ ] Implement date range filtering
- [ ] Generate PDF reports
- [ ] Export CSV functionality
- [ ] Display charts and graphs

**Location**: `src/pages/investor/InvestorReports.tsx`
**Required Methods**:
```typescript
- investorApiService.getRevenueStatistics(period)
- investorApiService.getROIAnalytics()
- investorApiService.getEarningsBreakdown(period)
- investorApiService.downloadReportCSV()
- investorApiService.downloadDetailedJobReportCSV()
```

---

### Customer Portal

#### CustomerDashboard
- [ ] Fully integrate `customerApiService.getDashboard()`
- [ ] Display active job information
- [ ] Show live tracking map with real location data
- [ ] Display job timeline/progress
- [ ] Show notifications
- [ ] Handle checkpoints (pre-start, mid-project, final)

**Location**: `src/pages/customer/CustomerDashboard.tsx`
**Required Methods**:
```typescript
- customerApiService.getDashboard()
- customerApiService.getJobs()
- customerApiService.getLiveTracking(jobId)
```

#### QuoteApproval (Magic Link)
- [ ] Validate quote token
- [ ] Load estimate details
- [ ] Implement approve/reject functionality
- [ ] Handle digital signature if needed
- [ ] Redirect after approval

**Location**: `src/pages/customer/QuoteApproval.tsx`
**Required Methods**:
```typescript
- customerApiService.validateQuoteToken(token)
- customerApiService.approveQuote(token, data)
```

#### MaterialPurchaseStatus (Magic Link)
- [ ] Load material list for order
- [ ] Show delivery status
- [ ] Track material source/supplier
- [ ] Confirm receipt/delivery

**Location**: `src/pages/customer/MaterialPurchaseStatus.tsx`

#### MaterialDeliveryConfirmation (Magic Link)
- [ ] Load delivery details
- [ ] Implement photo upload for confirmation
- [ ] Confirm delivery with timestamps
- [ ] Show tracking history

**Location**: `src/pages/customer/MaterialDeliveryConfirmation.tsx`
**Required Methods**:
```typescript
- customerApiService.confirmMaterialDeliveryByToken(token, formData)
```

#### ReportIssue (Magic Link)
- [ ] Load job details
- [ ] Create issue report form
- [ ] Upload issue photos
- [ ] Track issue status

**Location**: `src/pages/customer/ReportIssue.tsx`
**Required Methods**:
```typescript
- customerApiService.reportIssue(jobId, data)
```

#### CustomerTracker (Magic Link)
- [ ] Load live contractor tracking
- [ ] Display real-time location on map
- [ ] Show ETA and progress
- [ ] Display job timeline

**Location**: `src/pages/customer/CustomerTracker.tsx`
**Required Methods**:
```typescript
- customerApiService.getLiveTracking(jobId)
- customerApiService.getTrackingUpdates(jobId)
```

#### CustomerCredentials
- [ ] Generate customer access credentials
- [ ] Display magic link
- [ ] Copy link functionality
- [ ] Set expiration/access levels

**Location**: `src/pages/customer/CustomerCredentials.tsx`

---

## Environment Configuration

### .env File
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_NODE_ENV=development
```

**Status**: ✅ Already configured

---

## Testing Checklist

### Authentication
- [ ] Login works with backend
- [ ] User role correctly determined
- [ ] Token stored in localStorage
- [ ] Redirect to correct dashboard after login
- [ ] Logout clears token and redirects

### Admin Dashboard
- [ ] Dashboard loads without errors
- [ ] Stats are from API, not mock data
- [ ] Jobs list shows API data
- [ ] Pagination works
- [ ] Filters work correctly

### Contractor
- [ ] Dashboard shows real job count
- [ ] Job board shows actual assignments
- [ ] Accept/reject jobs works
- [ ] Wallet shows real balance
- [ ] Payout request works

### FM
- [ ] Dashboard stats are accurate
- [ ] Job management works
- [ ] Site visit workflow complete
- [ ] Photo uploads work
- [ ] Estimate creation works

### Investor
- [ ] Dashboard shows property data
- [ ] ROI calculations correct
- [ ] Reports generate correctly
- [ ] CSV export works

### Customer
- [ ] Dashboard loads
- [ ] Live tracking shows location
- [ ] Checkpoints work
- [ ] Material confirmation works

---

## Priority Implementation Order

### Phase 1 (Critical - Week 1)
1. Admin Dashboard main page
2. Customer Dashboard full integration
3. Contractor Dashboard and Job Board
4. Login/Auth verification

### Phase 2 (High - Week 2)
1. FM Dashboard and Job Visit
2. Contractor Wallet
3. Admin Payouts
4. Admin Compliance

### Phase 3 (Medium - Week 3)
1. Investor Dashboard
2. FM Estimates
3. Customer Checkpoints
4. Material Management

### Phase 4 (Polish - Week 4)
1. Error handling improvements
2. Loading states optimization
3. Performance tweaks
4. Testing and QA

---

## Notes

- All API services use `Authorization: Token {access_token}` header
- Fallback to mock data can be temporary but should be removed before production
- Error boundaries recommended for each major page
- Consider adding toast notifications for user feedback
- Implement pagination for large datasets
- Add loading skeletons for better UX

---

Last Updated: 2025-12-23
