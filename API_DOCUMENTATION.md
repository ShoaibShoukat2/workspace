# API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication
All protected endpoints require JWT authentication. Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

## Authentication Endpoints

### Register
**POST** `/auth/register/`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "username": "johndoe",
  "role": "CUSTOMER"
}
```

**Response:** `201 Created`
```json
{
  "message": "Registration successful. Please check your email to verify your account.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "role": "CUSTOMER",
    "is_verified": false
  }
}
```

### Login
**POST** `/auth/login/`

Login with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "role": "CUSTOMER"
  }
}
```

### Refresh Token
**POST** `/auth/token/refresh/`

Get a new access token using refresh token.

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Workspace Endpoints

### Create Workspace
**POST** `/workspaces/`

Create a new workspace.

**Request Body:**
```json
{
  "name": "Downtown Facility Project",
  "workspace_type": "PROJECT",
  "description": "Main facility management project"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "workspace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Downtown Facility Project",
  "workspace_type": "PROJECT",
  "owner": 1,
  "owner_email": "user@example.com",
  "description": "Main facility management project",
  "is_active": true,
  "member_count": 1,
  "created_at": "2025-12-05T10:30:00Z",
  "updated_at": "2025-12-05T10:30:00Z"
}
```

### List Workspaces
**GET** `/workspaces/`

Get all workspaces accessible to the user.

**Query Parameters:**
- `search` - Search by name or type
- `ordering` - Sort by field (e.g., `-created_at`)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "workspace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Downtown Facility Project",
    "workspace_type": "PROJECT",
    "owner_email": "user@example.com",
    "member_count": 3,
    "is_active": true,
    "created_at": "2025-12-05T10:30:00Z"
  }
]
```

### Get Workspace Statistics
**GET** `/workspaces/<workspace_id>/stats/`

Get statistics for a specific workspace.

**Response:** `200 OK`
```json
{
  "total_jobs": 25,
  "pending_jobs": 5,
  "in_progress_jobs": 10,
  "completed_jobs": 10,
  "total_estimates": 15,
  "approved_estimates": 12,
  "total_contractors": 8,
  "active_contractors": 7,
  "total_payouts": 45000.00,
  "pending_payouts": 3,
  "compliance_expired": 2,
  "compliance_expiring_soon": 4
}
```

---

## Job Endpoints

### Create Job
**POST** `/workspaces/<workspace_id>/jobs/`

Create a new job in the workspace.

**Request Body:**
```json
{
  "title": "HVAC Maintenance",
  "description": "Quarterly HVAC system maintenance",
  "status": "PENDING",
  "priority": "HIGH",
  "assigned_to": 2,
  "estimated_hours": 8,
  "start_date": "2025-12-10",
  "due_date": "2025-12-15",
  "location": "Building A, Floor 3"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "workspace": 1,
  "workspace_name": "Downtown Facility Project",
  "job_number": "JOB-A1B2C3D4-00001",
  "title": "HVAC Maintenance",
  "description": "Quarterly HVAC system maintenance",
  "status": "PENDING",
  "priority": "HIGH",
  "assigned_to": 2,
  "assigned_to_email": "contractor@example.com",
  "created_by": 1,
  "created_by_email": "user@example.com",
  "estimated_hours": 8.00,
  "actual_hours": null,
  "start_date": "2025-12-10",
  "due_date": "2025-12-15",
  "completed_date": null,
  "location": "Building A, Floor 3",
  "notes": null,
  "created_at": "2025-12-05T10:30:00Z",
  "updated_at": "2025-12-05T10:30:00Z"
}
```

### List Jobs
**GET** `/workspaces/<workspace_id>/jobs/`

Get all jobs in the workspace.

**Query Parameters:**
- `search` - Search by job number, title, or status
- `ordering` - Sort by field (e.g., `-due_date`, `priority`)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "job_number": "JOB-A1B2C3D4-00001",
    "title": "HVAC Maintenance",
    "status": "PENDING",
    "priority": "HIGH",
    "assigned_to_email": "contractor@example.com",
    "due_date": "2025-12-15"
  }
]
```

### Export Jobs to CSV
**GET** `/workspaces/<workspace_id>/jobs/export/`

Export all jobs to CSV format.

**Response:** `200 OK` (CSV file download)

---

## Estimate Endpoints

### Create Estimate
**POST** `/workspaces/<workspace_id>/estimates/`

Create a new estimate.

**Request Body:**
```json
{
  "job": 1,
  "title": "HVAC Maintenance Estimate",
  "description": "Cost estimate for quarterly maintenance",
  "status": "DRAFT",
  "subtotal": 1000.00,
  "tax_amount": 80.00,
  "discount_amount": 50.00,
  "total_amount": 1030.00,
  "valid_until": "2025-12-31"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "workspace": 1,
  "workspace_name": "Downtown Facility Project",
  "job": 1,
  "job_title": "HVAC Maintenance",
  "estimate_number": "EST-A1B2C3D4-00001",
  "title": "HVAC Maintenance Estimate",
  "description": "Cost estimate for quarterly maintenance",
  "status": "DRAFT",
  "subtotal": 1000.00,
  "tax_amount": 80.00,
  "discount_amount": 50.00,
  "total_amount": 1030.00,
  "valid_until": "2025-12-31",
  "created_by": 1,
  "created_by_email": "user@example.com",
  "approved_by": null,
  "approved_by_email": null,
  "approved_at": null,
  "notes": null,
  "created_at": "2025-12-05T10:30:00Z",
  "updated_at": "2025-12-05T10:30:00Z"
}
```

### Export Estimates to CSV
**GET** `/workspaces/<workspace_id>/estimates/export/`

Export all estimates to CSV format.

**Response:** `200 OK` (CSV file download)

---

## Contractor Endpoints

### Add Contractor
**POST** `/workspaces/<workspace_id>/contractors/`

Add a contractor to the workspace.

**Request Body:**
```json
{
  "user": 3,
  "company_name": "ABC Contractors Inc.",
  "license_number": "LIC-12345",
  "specialization": "HVAC Systems",
  "hourly_rate": 75.00,
  "status": "ACTIVE",
  "phone": "+1-555-0123",
  "address": "123 Main St, City, State 12345"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "workspace": 1,
  "workspace_name": "Downtown Facility Project",
  "user": 3,
  "user_email": "contractor@example.com",
  "user_name": "johncontractor",
  "company_name": "ABC Contractors Inc.",
  "license_number": "LIC-12345",
  "specialization": "HVAC Systems",
  "hourly_rate": 75.00,
  "status": "ACTIVE",
  "rating": null,
  "total_jobs_completed": 0,
  "phone": "+1-555-0123",
  "address": "123 Main St, City, State 12345",
  "notes": null,
  "created_at": "2025-12-05T10:30:00Z",
  "updated_at": "2025-12-05T10:30:00Z"
}
```

### Export Contractors to CSV
**GET** `/workspaces/<workspace_id>/contractors/export/`

Export all contractors to CSV format.

**Response:** `200 OK` (CSV file download)

---

## Payout Endpoints

### Create Payout
**POST** `/workspaces/<workspace_id>/payouts/`

Create a new payout for a contractor.

**Request Body:**
```json
{
  "contractor": 1,
  "job": 1,
  "amount": 600.00,
  "status": "PENDING",
  "payment_method": "BANK_TRANSFER",
  "description": "Payment for HVAC maintenance job",
  "scheduled_date": "2025-12-20"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "workspace": 1,
  "workspace_name": "Downtown Facility Project",
  "contractor": 1,
  "contractor_email": "contractor@example.com",
  "contractor_company": "ABC Contractors Inc.",
  "job": 1,
  "job_title": "HVAC Maintenance",
  "payout_number": "PAY-A1B2C3D4-00001",
  "amount": 600.00,
  "status": "PENDING",
  "payment_method": "BANK_TRANSFER",
  "description": "Payment for HVAC maintenance job",
  "scheduled_date": "2025-12-20",
  "paid_date": null,
  "processed_by": null,
  "processed_by_email": null,
  "transaction_reference": null,
  "notes": null,
  "created_at": "2025-12-05T10:30:00Z",
  "updated_at": "2025-12-05T10:30:00Z"
}
```

### Export Payouts to CSV
**GET** `/workspaces/<workspace_id>/payouts/export/`

Export all payouts to CSV format.

**Response:** `200 OK` (CSV file download)

---

## Compliance Endpoints

### Add Compliance Record
**POST** `/workspaces/<workspace_id>/compliance/`

Add a compliance document for a contractor.

**Request Body:**
```json
{
  "contractor": 1,
  "compliance_type": "LICENSE",
  "document_name": "Contractor License",
  "document_number": "LIC-12345",
  "status": "VALID",
  "issue_date": "2024-01-01",
  "expiry_date": "2026-01-01",
  "notes": "Valid contractor license"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "workspace": 1,
  "workspace_name": "Downtown Facility Project",
  "contractor": 1,
  "contractor_email": "contractor@example.com",
  "contractor_company": "ABC Contractors Inc.",
  "compliance_type": "LICENSE",
  "document_name": "Contractor License",
  "document_number": "LIC-12345",
  "status": "VALID",
  "issue_date": "2024-01-01",
  "expiry_date": "2026-01-01",
  "verified_by": null,
  "verified_by_email": null,
  "verified_at": null,
  "file_path": null,
  "notes": "Valid contractor license",
  "is_expiring_soon": false,
  "is_expired": false,
  "created_at": "2025-12-05T10:30:00Z",
  "updated_at": "2025-12-05T10:30:00Z"
}
```

### Get Expiring Compliance Documents
**GET** `/workspaces/<workspace_id>/compliance/expiring/`

Get all expiring or expired compliance documents.

**Response:** `200 OK`
```json
{
  "expiring_soon": [
    {
      "id": 2,
      "contractor_email": "contractor@example.com",
      "compliance_type": "INSURANCE",
      "document_name": "Liability Insurance",
      "expiry_date": "2025-12-20",
      "is_expiring_soon": true
    }
  ],
  "expired": [
    {
      "id": 3,
      "contractor_email": "contractor2@example.com",
      "compliance_type": "CERTIFICATION",
      "document_name": "Safety Certification",
      "expiry_date": "2025-11-30",
      "is_expired": true
    }
  ]
}
```

### Export Compliance to CSV
**GET** `/workspaces/<workspace_id>/compliance/export/`

Export all compliance data to CSV format.

**Response:** `200 OK` (CSV file download)

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid data provided",
  "details": {
    "field_name": ["Error message"]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "error": "Permission denied"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented. For production, consider implementing rate limiting using Django REST Framework throttling or a third-party package.

## Pagination

List endpoints support pagination. Default page size is 20 items.

**Query Parameters:**
- `page` - Page number
- `page_size` - Items per page (max 100)

**Response:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/workspaces/?page=2",
  "previous": null,
  "results": [...]
}
```
