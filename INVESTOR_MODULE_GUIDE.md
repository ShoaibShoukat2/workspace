# Investor Module - Complete Guide

## Overview
Complete investor dashboard with revenue statistics, ROI analytics, job volume breakdown, aur downloadable reports (CSV).

---

## 🎯 Key Features

- **Overall Revenue Statistics** - Total revenue, payouts, net profit tracking
- **ROI Analytics** - Return on investment calculations aur profitability analysis
- **Job Volume Breakdown** - Job statistics by status, priority, workspace
- **Payout Analytics** - Contractor payout trends aur analysis
- **Monthly Breakdown** - Month-wise revenue aur profit tracking
- **Downloadable Reports** - CSV format mein comprehensive reports
- **Recent Activity Feed** - Latest completed jobs aur payouts

---

## 📊 Investor Dashboard

### 1. Main Dashboard
**Endpoint:** `GET /api/workspace/investor/dashboard/`
**Permission:** Admin/Investor Only

**Query Parameters:**
- `date_from` - Start date (YYYY-MM-DD) - Default: Last 12 months
- `date_to` - End date (YYYY-MM-DD) - Default: Today

**Response:**
```json
{
  "date_range": {
    "from": "2023-01-01",
    "to": "2024-01-01"
  },
  "revenue": {
    "total_revenue": 500000.00,
    "total_payouts": 300000.00,
    "net_profit": 200000.00,
    "roi_percentage": 66.67,
    "pending_payouts": 25000.00
  },
  "jobs": {
    "total_jobs": 150,
    "completed_jobs": 120,
    "active_jobs": 20,
    "pending_jobs": 10,
    "completion_rate": 80.00,
    "average_job_value": 4166.67
  },
  "contractors": {
    "total_active_contractors": 25,
    "total_contractor_earnings": 300000.00
  },
  "monthly_breakdown": [
    {
      "month": "2023-01",
      "month_name": "January 2023",
      "revenue": 45000.00,
      "payouts": 27000.00,
      "profit": 18000.00,
      "jobs_count": 12
    }
  ]
}
```

**Usage Example:**
```bash
# Last 12 months (default)
GET /api/workspace/investor/dashboard/

# Custom date range
GET /api/workspace/investor/dashboard/?date_from=2023-06-01&date_to=2023-12-31
```

---

## 💰 Revenue Statistics

### 2. Detailed Revenue Statistics
**Endpoint:** `GET /api/workspace/investor/revenue-statistics/`
**Permission:** Admin/Investor Only

**Response:**
```json
{
  "revenue_by_workspace": [
    {
      "workspace__name": "Downtown Project",
      "workspace__workspace_id": "uuid-here",
      "total_revenue": 150000.00,
      "job_count": 45,
      "avg_revenue": 3333.33
    }
  ],
  "revenue_by_priority": [
    {
      "priority": "HIGH",
      "total_revenue": 200000.00,
      "job_count": 50
    },
    {
      "priority": "MEDIUM",
      "total_revenue": 180000.00,
      "job_count": 60
    }
  ],
  "top_contractors": [
    {
      "contractor_email": "contractor@example.com",
      "contractor_company": "ABC Construction",
      "total_earned": 75000.00,
      "jobs_completed": 25,
      "rating": 4.8
    }
  ]
}
```

**Key Insights:**
- Revenue breakdown by workspace
- Revenue distribution by job priority
- Top 10 performing contractors
- Average revenue per job

---

## 📈 Job Volume Breakdown

### 3. Job Volume Analysis
**Endpoint:** `GET /api/workspace/investor/job-volume/`
**Permission:** Admin/Investor Only

**Query Parameters:**
- `date_from` - Start date (YYYY-MM-DD)
- `date_to` - End date (YYYY-MM-DD)

**Response:**
```json
{
  "date_range": {
    "from": "2023-01-01",
    "to": "2024-01-01"
  },
  "by_status": [
    {
      "status": "COMPLETED",
      "count": 120,
      "total_value": 480000.00
    },
    {
      "status": "IN_PROGRESS",
      "count": 20,
      "total_value": 80000.00
    },
    {
      "status": "PENDING",
      "count": 10,
      "total_value": 40000.00
    }
  ],
  "by_priority": [
    {
      "priority": "HIGH",
      "count": 50,
      "total_value": 200000.00
    },
    {
      "priority": "MEDIUM",
      "count": 60,
      "total_value": 240000.00
    },
    {
      "priority": "LOW",
      "count": 40,
      "total_value": 160000.00
    }
  ],
  "by_workspace": [
    {
      "workspace__name": "Downtown Project",
      "workspace__workspace_id": "uuid-here",
      "count": 45,
      "total_value": 180000.00
    }
  ],
  "average_completion_days": 12.5
}
```

**Metrics:**
- Job distribution by status
- Job distribution by priority
- Job distribution by workspace
- Average completion time in days

---

## 💹 ROI Analytics

### 4. ROI & Profitability Analysis
**Endpoint:** `GET /api/workspace/investor/roi-analytics/`
**Permission:** Admin/Investor Only

**Query Parameters:**
- `date_from` - Start date (YYYY-MM-DD)
- `date_to` - End date (YYYY-MM-DD)

**Response:**
```json
{
  "date_range": {
    "from": "2023-01-01",
    "to": "2024-01-01"
  },
  "overall": {
    "total_investment": 300000.00,
    "total_returns": 500000.00,
    "net_profit": 200000.00,
    "roi_percentage": 66.67,
    "profit_margin": 40.00
  },
  "by_workspace": [
    {
      "workspace_name": "Downtown Project",
      "workspace_id": "uuid-here",
      "revenue": 180000.00,
      "investment": 108000.00,
      "profit": 72000.00,
      "roi_percentage": 66.67
    },
    {
      "workspace_name": "Uptown Facility",
      "workspace_id": "uuid-here",
      "revenue": 150000.00,
      "investment": 90000.00,
      "profit": 60000.00,
      "roi_percentage": 66.67
    }
  ]
}
```

**ROI Calculation:**
```
ROI % = (Net Profit / Total Investment) × 100
Profit Margin % = (Net Profit / Total Revenue) × 100
```

**Key Metrics:**
- Total investment (payouts)
- Total returns (revenue)
- Net profit
- ROI percentage
- Profit margin
- Workspace-wise ROI comparison

---

## 💸 Payout Analytics

### 5. Payout Trends & Analysis
**Endpoint:** `GET /api/workspace/investor/payout-analytics/`
**Permission:** Admin/Investor Only

**Query Parameters:**
- `date_from` - Start date (YYYY-MM-DD)
- `date_to` - End date (YYYY-MM-DD)

**Response:**
```json
{
  "date_range": {
    "from": "2023-01-01",
    "to": "2024-01-01"
  },
  "summary": {
    "total_payouts": 300000.00,
    "average_payout": 2500.00,
    "payout_count": 120
  },
  "by_status": [
    {
      "status": "COMPLETED",
      "count": 120,
      "total_amount": 300000.00
    },
    {
      "status": "PENDING",
      "count": 5,
      "total_amount": 12500.00
    }
  ],
  "by_payment_method": [
    {
      "payment_method": "BANK_TRANSFER",
      "count": 100,
      "total_amount": 250000.00
    },
    {
      "payment_method": "CHECK",
      "count": 20,
      "total_amount": 50000.00
    }
  ],
  "top_earners": [
    {
      "contractor__user__email": "contractor1@example.com",
      "contractor__company_name": "ABC Construction",
      "total_earned": 75000.00,
      "payout_count": 30
    }
  ]
}
```

**Insights:**
- Total payout amount
- Average payout per transaction
- Payout distribution by status
- Payment method preferences
- Top 10 earning contractors

---

## 📥 Downloadable Reports

### 6. Download Investor Report (CSV)
**Endpoint:** `GET /api/workspace/investor/reports/download/`
**Permission:** Admin/Investor Only

**Query Parameters:**
- `date_from` - Start date (YYYY-MM-DD)
- `date_to` - End date (YYYY-MM-DD)

**Response:** CSV file download

**CSV Contents:**
```csv
INVESTOR REPORT
Period: 2023-01-01 to 2024-01-01
Generated: 2024-01-15 10:30:00

REVENUE SUMMARY
Metric,Value
Total Revenue,$500000.00
Total Payouts,$300000.00
Net Profit,$200000.00
ROI,66.67%

JOB STATISTICS
Status,Count,Total Value
COMPLETED,120,$480000.00
IN_PROGRESS,20,$80000.00
PENDING,10,$40000.00

WORKSPACE PERFORMANCE
Workspace,Jobs,Revenue,Payouts,Profit,ROI %
Downtown Project,45,$180000.00,$108000.00,$72000.00,66.67%
Uptown Facility,38,$150000.00,$90000.00,$60000.00,66.67%
```

**Usage:**
```bash
# Download report for last 12 months
GET /api/workspace/investor/reports/download/

# Download report for specific period
GET /api/workspace/investor/reports/download/?date_from=2023-06-01&date_to=2023-12-31
```

### 7. Download Detailed Job Report (CSV)
**Endpoint:** `GET /api/workspace/investor/reports/jobs/download/`
**Permission:** Admin/Investor Only

**Query Parameters:**
- `date_from` - Start date (YYYY-MM-DD)
- `date_to` - End date (YYYY-MM-DD)

**Response:** CSV file download

**CSV Contents:**
```csv
Job Number,Title,Workspace,Status,Priority,Assigned To,Customer Name,Estimated Cost,Actual Cost,Start Date,Due Date,Completed Date,Created At
JOB-000001,Bathroom Renovation,Downtown Project,COMPLETED,HIGH,contractor@example.com,John Doe,$5000.00,$4800.00,2023-01-15,2023-01-30,2023-01-28,2023-01-10 09:00:00
JOB-000002,Kitchen Remodel,Uptown Facility,IN_PROGRESS,MEDIUM,contractor2@example.com,Jane Smith,$8000.00,$0.00,2023-02-01,2023-02-28,N/A,2023-01-25 14:30:00
```

---

## 📰 Recent Activity Feed

### 8. Recent Activity
**Endpoint:** `GET /api/workspace/investor/recent-activity/`
**Permission:** Admin/Investor Only

**Query Parameters:**
- `limit` - Number of activities to return (default: 20)

**Response:**
```json
{
  "activities": [
    {
      "type": "JOB_COMPLETED",
      "date": "2024-01-15",
      "description": "Job JOB-000123 completed",
      "amount": 4800.00,
      "details": {
        "job_number": "JOB-000123",
        "title": "Bathroom Renovation",
        "workspace": "Downtown Project"
      }
    },
    {
      "type": "PAYOUT_COMPLETED",
      "date": "2024-01-14",
      "description": "Payout PAY-000045 processed",
      "amount": 2500.00,
      "details": {
        "payout_number": "PAY-000045",
        "contractor": "contractor@example.com",
        "payment_method": "BANK_TRANSFER"
      }
    }
  ]
}
```

**Activity Types:**
- `JOB_COMPLETED` - Job completion events
- `PAYOUT_COMPLETED` - Payout processing events

---

## 📊 Dashboard Metrics Explained

### Revenue Metrics
- **Total Revenue**: Sum of all completed job costs
- **Total Payouts**: Sum of all completed contractor payouts
- **Net Profit**: Total Revenue - Total Payouts
- **ROI Percentage**: (Net Profit / Total Payouts) × 100
- **Pending Payouts**: Amount ready for payout but not yet processed

### Job Metrics
- **Total Jobs**: All jobs in date range
- **Completed Jobs**: Jobs with COMPLETED status
- **Active Jobs**: Jobs with IN_PROGRESS status
- **Pending Jobs**: Jobs with PENDING status
- **Completion Rate**: (Completed Jobs / Total Jobs) × 100
- **Average Job Value**: Total Revenue / Completed Jobs

### Contractor Metrics
- **Total Active Contractors**: Contractors with ACTIVE status
- **Total Contractor Earnings**: Sum of all contractor wallet earnings

---

## 🎯 Use Cases

### 1. Monthly Performance Review
```bash
# Get current month data
GET /api/workspace/investor/dashboard/?date_from=2024-01-01&date_to=2024-01-31
```

### 2. Quarterly ROI Analysis
```bash
# Q1 2024 ROI
GET /api/workspace/investor/roi-analytics/?date_from=2024-01-01&date_to=2024-03-31
```

### 3. Year-End Report
```bash
# Download full year report
GET /api/workspace/investor/reports/download/?date_from=2023-01-01&date_to=2023-12-31
```

### 4. Contractor Performance Review
```bash
# Get revenue statistics with top contractors
GET /api/workspace/investor/revenue-statistics/
```

### 5. Job Volume Trends
```bash
# Analyze job volume for last 6 months
GET /api/workspace/investor/job-volume/?date_from=2023-07-01&date_to=2023-12-31
```

---

## 📈 Best Practices

### For Investors
1. **Regular Monitoring**: Check dashboard weekly for trends
2. **ROI Tracking**: Monitor ROI by workspace to identify best performers
3. **Payout Analysis**: Review payout trends to manage cash flow
4. **Monthly Reports**: Download monthly reports for record keeping
5. **Contractor Performance**: Track top contractors for future projects

### For Admins
1. **Data Accuracy**: Ensure all job costs are accurately recorded
2. **Timely Updates**: Update job statuses promptly
3. **Payout Processing**: Process payouts on time to maintain accurate metrics
4. **Workspace Management**: Keep workspace data organized

---

## 🔒 Security & Permissions

### Access Control
- **Investor Dashboard**: Admin/Investor role only
- **All Analytics**: Admin/Investor role only
- **Reports Download**: Admin/Investor role only
- **Recent Activity**: Admin/Investor role only

### Data Privacy
- Sensitive contractor information protected
- Financial data encrypted
- Audit trail maintained for all transactions

---

## 📝 Notes

### Date Ranges
- Default date range: Last 12 months
- All dates in YYYY-MM-DD format
- Timezone: Server timezone (UTC recommended)

### Performance
- Large date ranges may take longer to process
- Consider using pagination for large datasets
- Reports are generated on-demand

### Calculations
- All amounts in USD (or configured currency)
- ROI calculated based on completed transactions only
- Monthly breakdown starts from first day of month

### CSV Reports
- UTF-8 encoding
- Comma-separated values
- Headers included
- Suitable for Excel/Google Sheets

---

## 🚀 Quick Start

### 1. View Dashboard
```bash
curl -X GET "http://localhost:8000/api/workspace/investor/dashboard/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Get ROI Analytics
```bash
curl -X GET "http://localhost:8000/api/workspace/investor/roi-analytics/?date_from=2023-01-01&date_to=2023-12-31" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Download Report
```bash
curl -X GET "http://localhost:8000/api/workspace/investor/reports/download/?date_from=2023-01-01&date_to=2023-12-31" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o investor_report.csv
```

---

## 📞 Support

Issues ya questions ke liye:
- Check API documentation
- Review error messages
- Contact system administrator
