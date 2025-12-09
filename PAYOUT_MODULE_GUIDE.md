# Admin Payout & Financial Flow Module - Complete Guide

## Overview

Payout & Financial Flow module admin aur contractors ke liye complete payment management system provide karta hai with automatic wallet credits, transaction tracking, aur downloadable reports.

## Key Features

### 1. Admin Payout Management
Complete payout control:
- View all jobs ready for payout
- Single job payout approval
- Bulk payout approval (multiple jobs at once)
- Reject payouts with reason
- Automatic wallet credit on approval
- Real-time payout statistics
- Track processing status

### 2. Contractor Wallet System
Digital wallet for contractors:
- Current balance tracking
- Total earned amount
- Total withdrawn amount
- Pending amount (requested but not processed)
- Automatic credit on job approval
- Debit on payout withdrawal
- Complete transaction history

### 3. Transaction Ledger
Detailed transaction tracking:
- Credit transactions (job payments)
- Debit transactions (withdrawals)
- Transaction status
- Balance after each transaction
- Reference numbers
- Descriptions
- Date and time stamps

### 4. Payout Request System
Contractor withdrawal system:
- Request payout from wallet balance
- Multiple payment methods
- Bank account details
- PayPal integration
- Admin approval workflow
- Status tracking
- Rejection with reason

### 5. Financial Reports
Comprehensive reporting:
- Downloadable payout reports (CSV)
- Wallet ledger export
- Date range filtering
- Contractor-wise reports
- Monthly summaries

## Database Models

### ContractorWallet
```python
- contractor (OneToOne to Contractor)
- balance (current wallet balance)
- total_earned (lifetime earnings)
- total_withdrawn (lifetime withdrawals)
- pending_amount (pending payout requests)
- created_at, updated_at
```

**Methods:**
- `credit(amount, description)` - Add money to wallet
- `debit(amount, description)` - Remove money from wallet
- `add_pending(amount)` - Add to pending amount
- `clear_pending(amount)` - Clear pending amount

### WalletTransaction
```python
- wallet (FK to ContractorWallet)
- transaction_type (CREDIT, DEBIT)
- amount
- balance_after
- status (PENDING, COMPLETED, FAILED, CANCELLED)
- description
- reference_number
- payout (FK to Payout, optional)
- created_at
```

### PayoutRequest
```python
- contractor (FK to Contractor)
- request_number (unique)
- amount
- status (PENDING, APPROVED, REJECTED, PROCESSING, COMPLETED)
- payment_method (BANK_TRANSFER, CHECK, CASH, PAYPAL, OTHER)
- bank_account_number, bank_name, bank_routing_number
- paypal_email
- notes
- reviewed_by (FK to User)
- reviewed_at
- rejection_reason
- payout (OneToOne to Payout)
- created_at, updated_at
```

### JobPayoutEligibility
```python
- job (OneToOne to Job)
- contractor (FK to Contractor)
- amount
- status (READY, PROCESSING, PAID, ON_HOLD)
- verified_at
- payout (FK to Payout)
- notes
- created_at, updated_at
```

**Methods:**
- `mark_as_paid(payout)` - Mark job as paid

## API Endpoints

### Admin Payout Management

#### View Ready for Payout Jobs
```
GET /api/workspaces/admin/payouts/ready/
Query Parameters:
  - contractor_id (optional): Filter by contractor

Response:
[
  {
    "id": 1,
    "job": 1,
    "job_number": "JOB-A1B2C3D4-00001",
    "job_title": "HVAC System Repair",
    "contractor": 1,
    "contractor_email": "contractor@example.com",
    "contractor_company": "ABC Contractors",
    "amount": 1500.00,
    "status": "READY",
    "verified_at": "2025-12-05T17:00:00Z",
    "payout": null,
    "payout_number": null,
    "notes": null,
    "created_at": "2025-12-05T17:00:00Z"
  }
]
```

#### Approve Job Payout
```
POST /api/workspaces/admin/payouts/{eligibility_id}/approve/

Response:
{
  "message": "Payout approved and wallet credited successfully",
  "payout": {
    "id": 1,
    "payout_number": "PAY-A1B2C3D4-00001",
    "amount": 1500.00,
    "status": "COMPLETED",
    "paid_date": "2025-12-06"
  },
  "wallet": {
    "balance": 1500.00,
    "total_earned": 1500.00,
    "total_withdrawn": 0.00,
    "pending_amount": 0.00
  }
}
```

#### Reject Job Payout
```
POST /api/workspaces/admin/payouts/{eligibility_id}/reject/

Request Body:
{
  "rejection_reason": "Documentation incomplete"
}

Response:
{
  "message": "Payout rejected and put on hold",
  "eligibility": {...}
}
```

#### Bulk Approve Payouts
```
POST /api/workspaces/admin/payouts/bulk-approve/

Request Body:
{
  "eligibility_ids": [1, 2, 3, 4, 5]
}

Response:
{
  "message": "Processed 5 payouts",
  "approved": 5,
  "failed": 0,
  "results": [
    {
      "eligibility_id": 1,
      "status": "approved",
      "payout_number": "PAY-A1B2C3D4-00001"
    },
    ...
  ]
}
```

#### Get Payout Statistics
```
GET /api/workspaces/admin/payouts/statistics/

Response:
{
  "ready_for_payout": {
    "count": 10,
    "total_amount": 15000.00
  },
  "processing": {
    "count": 2,
    "total_amount": 3000.00
  },
  "paid_this_month": {
    "count": 25,
    "total_amount": 37500.00
  },
  "on_hold": {
    "count": 3,
    "total_amount": 4500.00
  },
  "wallet_summary": {
    "total_balance": 50000.00,
    "total_pending": 5000.00
  }
}
```

### Contractor Wallet

#### Get Wallet Balance
```
GET /api/workspaces/contractor/wallet/

Response:
{
  "id": 1,
  "contractor": 1,
  "contractor_email": "contractor@example.com",
  "contractor_company": "ABC Contractors",
  "balance": 2500.00,
  "total_earned": 15000.00,
  "total_withdrawn": 12500.00,
  "pending_amount": 500.00,
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-12-06T14:30:00Z"
}
```

#### View Transaction History
```
GET /api/workspaces/contractor/wallet/transactions/
Query Parameters:
  - transaction_type: credit, debit
  - date_from: YYYY-MM-DD
  - date_to: YYYY-MM-DD

Response:
[
  {
    "id": 1,
    "wallet": 1,
    "contractor_email": "contractor@example.com",
    "transaction_type": "CREDIT",
    "amount": 1500.00,
    "balance_after": 2500.00,
    "status": "COMPLETED",
    "description": "Payment for job JOB-A1B2C3D4-00001",
    "reference_number": null,
    "payout": 1,
    "payout_number": "PAY-A1B2C3D4-00001",
    "created_at": "2025-12-06T10:00:00Z"
  },
  {
    "id": 2,
    "transaction_type": "DEBIT",
    "amount": 500.00,
    "balance_after": 2000.00,
    "status": "COMPLETED",
    "description": "Payout request PR-00001-00001",
    "created_at": "2025-12-05T15:00:00Z"
  }
]
```

#### Download Wallet Ledger
```
GET /api/workspaces/contractor/wallet/ledger/download/

Response: CSV file download
Filename: wallet_ledger_contractor@example.com_20251206.csv

CSV Content:
Date,Transaction Type,Amount,Balance After,Status,Description,Reference Number
2025-12-06 10:00:00,Credit,$1500.00,$2500.00,Completed,Payment for job JOB-A1B2C3D4-00001,
2025-12-05 15:00:00,Debit,$500.00,$2000.00,Completed,Payout request PR-00001-00001,
```

#### Request Payout
```
POST /api/workspaces/contractor/wallet/request-payout/

Request Body:
{
  "amount": 500.00,
  "payment_method": "BANK_TRANSFER",
  "bank_account_number": "1234567890",
  "bank_name": "Chase Bank",
  "bank_routing_number": "021000021",
  "notes": "Weekly payout request"
}

Response:
{
  "message": "Payout request submitted successfully",
  "payout_request": {
    "id": 1,
    "request_number": "PR-00001-00001",
    "amount": 500.00,
    "status": "PENDING",
    "payment_method": "BANK_TRANSFER",
    "bank_account_number": "1234567890",
    "bank_name": "Chase Bank",
    "created_at": "2025-12-06T14:00:00Z"
  }
}
```

#### View Payout Requests
```
GET /api/workspaces/contractor/payout-requests/

Response:
[
  {
    "id": 1,
    "request_number": "PR-00001-00001",
    "amount": 500.00,
    "status": "PENDING",
    "payment_method": "BANK_TRANSFER",
    "reviewed_by": null,
    "reviewed_at": null,
    "rejection_reason": null,
    "created_at": "2025-12-06T14:00:00Z"
  }
]
```

### Admin Payout Requests

#### List All Payout Requests
```
GET /api/workspaces/admin/payout-requests/
Query Parameters:
  - status: pending, approved, rejected

Response:
[
  {
    "id": 1,
    "contractor_email": "contractor@example.com",
    "contractor_company": "ABC Contractors",
    "request_number": "PR-00001-00001",
    "amount": 500.00,
    "status": "PENDING",
    "payment_method": "BANK_TRANSFER",
    "bank_account_number": "1234567890",
    "bank_name": "Chase Bank",
    "created_at": "2025-12-06T14:00:00Z"
  }
]
```

#### Approve Payout Request
```
POST /api/workspaces/admin/payout-requests/{request_id}/approve/

Response:
{
  "message": "Payout request approved successfully",
  "payout_request": {
    "id": 1,
    "status": "APPROVED",
    "reviewed_by": 1,
    "reviewed_by_email": "admin@example.com",
    "reviewed_at": "2025-12-06T15:00:00Z"
  }
}
```

#### Reject Payout Request
```
POST /api/workspaces/admin/payout-requests/{request_id}/reject/

Request Body:
{
  "rejection_reason": "Insufficient documentation provided"
}

Response:
{
  "message": "Payout request rejected",
  "payout_request": {
    "id": 1,
    "status": "REJECTED",
    "rejection_reason": "Insufficient documentation provided",
    "reviewed_by": 1,
    "reviewed_at": "2025-12-06T15:00:00Z"
  }
}
```

### Reports

#### Download Payout Report
```
GET /api/workspaces/admin/payouts/report/download/
Query Parameters:
  - date_from: YYYY-MM-DD
  - date_to: YYYY-MM-DD

Response: CSV file download
Filename: payout_report_20251206.csv

CSV Content:
Job Number,Job Title,Contractor Email,Contractor Company,Amount,Payout Number,Paid Date,Status
JOB-A1B2C3D4-00001,HVAC System Repair,contractor@example.com,ABC Contractors,$1500.00,PAY-A1B2C3D4-00001,2025-12-06,Paid
```

## Complete Workflow

### Automatic Payout Flow

1. **Job Completion Verified**
   - FM/Admin verifies job completion with "approve" action
   - System automatically creates `JobPayoutEligibility` record
   - Status set to "READY"
   - Amount calculated from job's actual_cost or estimated_cost

2. **Admin Views Ready Jobs**
   ```bash
   GET /api/workspaces/admin/payouts/ready/
   ```

3. **Admin Approves Payout**
   ```bash
   POST /api/workspaces/admin/payouts/1/approve/
   ```
   - Creates `Payout` record
   - Credits contractor wallet
   - Creates `WalletTransaction` (CREDIT)
   - Marks eligibility as "PAID"
   - Sends notification to contractor

4. **Contractor Sees Updated Balance**
   ```bash
   GET /api/workspaces/contractor/wallet/
   ```

### Manual Payout Request Flow

1. **Contractor Requests Payout**
   ```bash
   POST /api/workspaces/contractor/wallet/request-payout/
   {
     "amount": 500.00,
     "payment_method": "BANK_TRANSFER",
     "bank_account_number": "1234567890"
   }
   ```
   - Creates `PayoutRequest` record
   - Adds amount to wallet's pending_amount
   - Status set to "PENDING"

2. **Admin Reviews Request**
   ```bash
   GET /api/workspaces/admin/payout-requests/
   ```

3. **Admin Approves Request**
   ```bash
   POST /api/workspaces/admin/payout-requests/1/approve/
   ```
   - Debits wallet balance
   - Creates `WalletTransaction` (DEBIT)
   - Clears pending amount
   - Updates request status to "APPROVED"
   - Sends notification to contractor

## Best Practices

### For Admins
1. **Regular Review** - Check ready payouts daily
2. **Bulk Processing** - Use bulk approve for efficiency
3. **Verify Details** - Check job completion before approval
4. **Document Rejections** - Provide clear rejection reasons
5. **Monitor Statistics** - Track financial health
6. **Generate Reports** - Monthly payout reports

### For Contractors
1. **Check Balance** - Regularly monitor wallet
2. **Review Transactions** - Verify all credits/debits
3. **Request Timely** - Request payouts when needed
4. **Provide Details** - Complete bank information
5. **Download Ledger** - Keep records for taxes
6. **Track Requests** - Monitor payout request status

## Security Features

1. **Admin-Only Approval** - Only admins can approve payouts
2. **Balance Validation** - Check sufficient balance before debit
3. **Transaction Logging** - All transactions recorded
4. **Reference Numbers** - Unique identifiers for tracking
5. **Status Tracking** - Complete audit trail
6. **Notification System** - Real-time updates

## Financial Reports

### Payout Report Columns
- Job Number
- Job Title
- Contractor Email
- Contractor Company
- Amount
- Payout Number
- Paid Date
- Status

### Wallet Ledger Columns
- Date
- Transaction Type
- Amount
- Balance After
- Status
- Description
- Reference Number

## Troubleshooting

**Issue: Payout not appearing in ready list**
- Ensure job completion is approved
- Check if payout eligibility was created
- Verify job has actual_cost or estimated_cost

**Issue: Cannot approve payout**
- Check if status is "READY"
- Verify admin permissions
- Ensure job is not already paid

**Issue: Payout request rejected**
- Review rejection reason
- Update required information
- Resubmit new request

**Issue: Wallet balance incorrect**
- Review transaction history
- Check for pending amounts
- Contact admin for reconciliation

## Future Enhancements

1. Automated payout schedules (weekly/monthly)
2. Multiple currency support
3. Tax calculation and reporting
4. Payment gateway integration
5. Instant payout options
6. Contractor earnings forecast
7. Advanced financial analytics
8. Mobile wallet app
9. QR code payments
10. Cryptocurrency support

## Support

For issues or questions:
- Check API_DOCUMENTATION.md
- Review IMPLEMENTATION_GUIDE.md
- Test with POSTMAN_COLLECTION.json
- Contact: support@yourapp.com
