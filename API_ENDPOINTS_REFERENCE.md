# Job Workflow API Endpoints Reference

## Base URL
```
/api/workspaces/
```

## Authentication
All endpoints require authentication via Token header:
```
Authorization: Token <your_token_here>
```

## Authentication Endpoints

### Login
```http
POST /auth/login/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}
```

### Get Current User
```http
GET /auth/user/
Authorization: Token <token>
```

## Contractor Endpoints (B1-B13, B29)

### B1: Job List
```http
GET /contractor/jobs/
Authorization: Token <contractor_token>
```

### B2: Job Detail
```http
GET /contractor/jobs/{job_id}/
Authorization: Token <contractor_token>
```

### B3: Upload Photos
```http
POST /contractor/jobs/{job_id}/photos/upload/
Authorization: Token <contractor_token>
Content-Type: multipart/form-data

{
  "type": "before|evaluation|progress|after",
  "file": <file>,
  "caption": "Optional caption"
}
```

### B4: Update Evaluation
```http
PUT /contractor/jobs/{job_id}/evaluation/
Authorization: Token <contractor_token>
Content-Type: application/json

{
  "measurements": {
    "roomCount": 2,
    "squareFeet": 450
  },
  "scope": "Paint living room walls",
  "toolsRequired": ["brushes", "rollers"],
  "laborRequired": 2,
  "estimatedHours": 8,
  "safetyConcerns": "High ceilings"
}
```

### B5: Submit Evaluation
```http
POST /contractor/jobs/{job_id}/evaluation/submit/
Authorization: Token <contractor_token>
```

### B6: Get Materials
```http
GET /contractor/jobs/{job_id}/materials/
Authorization: Token <contractor_token>
```

### B7: Verify Materials
```http
PUT /contractor/jobs/{job_id}/materials/verify/
Authorization: Token <contractor_token>
Content-Type: application/json

{
  "items": [
    {
      "id": 123,
      "confirmedQty": 4,
      "status": "confirmed"
    }
  ]
}
```

### B8: Upload Progress Photos
```http
POST /contractor/jobs/{job_id}/progress/photos/
Authorization: Token <contractor_token>
Content-Type: multipart/form-data

{
  "file": <file>,
  "caption": "Progress update"
}
```

### B9: Add Progress Note
```http
POST /contractor/jobs/{job_id}/progress/notes/
Authorization: Token <contractor_token>
Content-Type: application/json

{
  "note": "Completed first coat on all walls"
}
```

### B10: Get Checklist
```http
GET /contractor/jobs/{job_id}/checklist/
Authorization: Token <contractor_token>
```

### B11: Update Checklist
```http
PUT /contractor/jobs/{job_id}/checklist/update/
Authorization: Token <contractor_token>
Content-Type: application/json

{
  "items": [
    {
      "id": "c1",
      "label": "All walls painted",
      "done": true
    }
  ]
}
```

### B13: Complete Work
```http
POST /contractor/jobs/{job_id}/complete/
Authorization: Token <contractor_token>
```

### B29: Verify Customer Materials
```http
POST /contractor/jobs/{job_id}/materials/verify-customer/
Authorization: Token <contractor_token>
Content-Type: application/json

{
  "status": "verified|issue",
  "note": "Materials look good"
}
```

## Customer Endpoints (C1-C14)

### C1: Job Timeline
```http
GET /customer/jobs/{job_id}/timeline/
Authorization: Token <customer_token>
```

### C2: Pre-Start Checkpoint
```http
GET /customer/jobs/{job_id}/pre-start/
Authorization: Token <customer_token>
```

### C3: Approve Pre-Start
```http
POST /customer/jobs/{job_id}/pre-start/approve/
Authorization: Token <customer_token>
Content-Type: application/json

{
  "note": "Looks good, proceed"
}
```

### C4: Reject Pre-Start
```http
POST /customer/jobs/{job_id}/pre-start/reject/
Authorization: Token <customer_token>
Content-Type: application/json

{
  "reason": "Need clarification on scope"
}
```

### C5: Mid-Project Checkpoint
```http
GET /customer/jobs/{job_id}/mid-project/
Authorization: Token <customer_token>
```

### C6: Approve Mid-Project
```http
POST /customer/jobs/{job_id}/mid-project/approve/
Authorization: Token <customer_token>
Content-Type: application/json

{
  "note": "Progress looks great"
}
```

### C7: Reject Mid-Project
```http
POST /customer/jobs/{job_id}/mid-project/reject/
Authorization: Token <customer_token>
Content-Type: application/json

{
  "reason": "Quality concerns with paint coverage"
}
```

### C8: Final Checkpoint
```http
GET /customer/jobs/{job_id}/final/
Authorization: Token <customer_token>
```

### C9: Approve Final
```http
POST /customer/jobs/{job_id}/final/approve/
Authorization: Token <customer_token>
Content-Type: application/json

{
  "note": "Excellent work!",
  "rating": 5,
  "review": "Very professional"
}
```

### C10: Reject Final
```http
POST /customer/jobs/{job_id}/final/reject/
Authorization: Token <customer_token>
Content-Type: application/json

{
  "reason": "Touch-ups needed in corners"
}
```

### C11: Job Materials
```http
GET /customer/jobs/{job_id}/materials/
Authorization: Token <customer_token>
```

### C12: Choose Material Source
```http
POST /customer/jobs/{job_id}/materials/source/
Authorization: Token <customer_token>
Content-Type: application/json

{
  "materialSource": "links|customer_supplied"
}
```

### C13: Upload Material Photos
```http
POST /customer/jobs/{job_id}/materials/photos/
Authorization: Token <customer_token>
Content-Type: multipart/form-data

{
  "file": <file>,
  "caption": "Materials purchased"
}
```

### C14: Confirm Liability
```http
POST /customer/jobs/{job_id}/materials/liability/
Authorization: Token <customer_token>
Content-Type: application/json

{
  "accepted": true
}
```

## Service Endpoints (30-31)

### 30: RAG Pricing Service
```http
POST /services/rag-pricing/{job_id}/
Authorization: Token <admin_token>
```

### 31: Material Scraper Service
```http
POST /services/material-scraper/{job_id}/
Authorization: Token <admin_token>
```

### RAG Pricing Analytics
```http
GET /services/rag-pricing/analytics/
Authorization: Token <admin_token>
```

### Material Scraper Status
```http
GET /services/material-scraper/status/
Authorization: Token <admin_token>
```

### Trigger Material Scrape
```http
POST /services/material-scraper/trigger/
Authorization: Token <admin_token>
Content-Type: application/json

{
  "vendor": "all|Home Depot|Lowes|Sherwin Williams|Amazon"
}
```

## Response Formats

### Success Response
```json
{
  "success": true,
  "data": { ... }
}
```

### Error Response
```json
{
  "error": "Error message",
  "details": { ... }
}
```

## Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Job Status Values
- `LEAD`
- `EVALUATION_SCHEDULED`
- `EVALUATION_COMPLETED`
- `AWAITING_PRE_START_APPROVAL`
- `IN_PROGRESS`
- `MID_CHECKPOINT_PENDING`
- `AWAITING_FINAL_APPROVAL`
- `COMPLETED`
- `CANCELLED`

## Checkpoint Types
- `PRE_START`
- `MID_PROJECT`
- `FINAL`

## Checkpoint Status Values
- `PENDING`
- `APPROVED`
- `REJECTED`
- `ISSUE`

## Photo Types
- `BEFORE`
- `EVALUATION`
- `PROGRESS`
- `AFTER`
- `CUSTOMER_MATERIALS`