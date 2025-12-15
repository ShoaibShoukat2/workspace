# Complete API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication
All protected endpoints require JWT authentication. Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Table of Contents
1. [Authentication Module](#authentication-module)
2. [Workspace Management](#workspace-management)
3. [Field Manager (FM) Module](#field-manager-fm-module)
4. [Contractor Module](#contractor-module)
5. [Admin Payout & Financial Flow](#admin-payout--financial-flow)
6. [Compliance & Disputes](#compliance--disputes)
7. [Investor Module](#investor-module)
8. [AI-Assisted Features](#ai-assisted-features)
9. [PDF Generation](#pdf-generation)
10. [Error Responses](#error-responses)

---

## Authentication Module

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

### Logout
**POST** `/auth/logout/`
**Auth Required:** Yes

Logout from current session.

**Response:** `200 OK`
```json
{
  "message": "Logged out successfully"
}
```

### Logout All Devices
**POST** `/auth/logout-all/`
**Auth Required:** Yes

Logout from all devices.

**Response:** `200 OK`
```json
{
  "message": "Logged out from all devices"
}
```

### Refresh Token
**POST** `/auth/token/refresh/`

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

### Magic Link Request
**POST** `/auth/magic-link/request/`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:** `200 OK`
```json
{
  "message": "Magic link sent to your email"
}
```

### Magic Link Verify
**POST** `/auth/magic-link/verify/`

**Request Body:**
```json
{
  "token": "abc123def456..."
}
```

**Response:** `200 OK`
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

### Verify Email
**POST** `/auth/verify-email/`

**Request Body:**
```json
{
  "token": "verification_token_here"
}
```

**Response:** `200 OK`
```json
{
  "message": "Email verified successfully"
}
```

### Resend Verification Email
**POST** `/auth/resend-verification/`
**Auth Required:** Yes

**Response:** `200 OK`
```json
{
  "message": "Verification email sent"
}
```

### Password Reset Request
**POST** `/auth/password-reset/request/`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:** `200 OK`
```json
{
  "message": "Password reset email sent"
}
```

### Password Reset Confirm
**POST** `/auth/password-reset/confirm/`

**Request Body:**
```json
{
  "token": "reset_token_here",
  "password": "NewSecurePass123!",
  "password2": "NewSecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "message": "Password reset successful"
}
```

### Change Password
**POST** `/auth/change-password/`
**Auth Required:** Yes

**Request Body:**
```json
{
  "old_password": "OldPass123!",
  "new_password": "NewPass123!",
  "new_password2": "NewPass123!"
}
```

**Response:** `200 OK`
```json
{
  "message": "Password changed successfully"
}
```

### Get Current User
**GET** `/auth/me/`
**Auth Required:** Yes

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "role": "CUSTOMER",
  "is_verified": true,
  "is_active": true,
  "created_at": "2025-12-01T10:00:00Z"
}
```

### Update Profile
**PATCH** `/auth/profile/`
**Auth Required:** Yes

**Request Body:**
```json
{
  "username": "newusername",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "newusername",
  "first_name": "John",
  "last_name": "Doe"
}
```

### List Active Sessions
**GET** `/auth/sessions/`
**Auth Required:** Yes

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "device_info": "Chrome on Windows",
    "ip_address": "192.168.1.1",
    "is_current": true,
    "last_activity": "2025-12-05T10:30:00Z",
    "created_at": "2025-12-05T09:00:00Z"
  }
]
```

### Revoke Session
**POST** `/auth/sessions/<session_id>/revoke/`
**Auth Required:** Yes

**Response:** `200 OK`
```json
{
  "message": "Session revoked successfully"
}
```

### Login History
**GET** `/auth/login-history/`
**Auth Required:** Yes

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "ip_address": "192.168.1.1",
    "device_info": "Chrome on Windows",
    "success": true,
    "timestamp": "2025-12-05T09:00:00Z"
  }
]
```

### List All Users (Admin Only)
**GET** `/auth/users/`
**Auth Required:** Admin

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "role": "CUSTOMER",
    "is_active": true,
    "is_verified": true
  }
]
```

### Get User Details (Admin/FM)
**GET** `/auth/users/<user_id>/`
**Auth Required:** Admin/FM

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "role": "CUSTOMER",
  "is_active": true,
  "is_verified": true,
  "created_at": "2025-12-01T10:00:00Z"
}
```

### Update User (Admin/FM)
**PATCH** `/auth/users/<user_id>/`
**Auth Required:** Admin/FM

**Request Body:**
```json
{
  "is_active": false,
  "role": "CONTRACTOR"
}
```

**Response:** `200 OK`

### Deactivate User (Admin/FM)
**DELETE** `/auth/users/<user_id>/`
**Auth Required:** Admin/FM

**Response:** `204 No Content`

### User Statistics (Admin)
**GET** `/auth/stats/`
**Auth Required:** Admin

**Response:** `200 OK`
```json
{
  "total_users": 150,
  "active_users": 145,
  "verified_users": 140,
  "users_by_role": {
    "ADMIN": 2,
    "FM": 5,
    "CONTRACTOR": 50,
    "CUSTOMER": 80,
    "INVESTOR": 13
  }
}
```

---

## Workspace Management

### Create Workspace
**POST** `/workspaces/`
**Auth Required:** Yes

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
  "created_at": "2025-12-05T10:30:00Z"
}
```

### List Workspaces
**GET** `/workspaces/`
**Auth Required:** Yes

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
    "is_active": true
  }
]
```

### Get Workspace Details
**GET** `/workspaces/<workspace_id>/`
**Auth Required:** Yes

**Response:** `200 OK`

### Update Workspace
**PATCH** `/workspaces/<workspace_id>/`
**Auth Required:** Yes

**Request Body:**
```json
{
  "name": "Updated Project Name",
  "description": "Updated description"
}
```

**Response:** `200 OK`

### Delete Workspace
**DELETE** `/workspaces/<workspace_id>/`
**Auth Required:** Yes

**Response:** `204 No Content`

### Get Workspace Statistics
**GET** `/workspaces/<workspace_id>/stats/`
**Auth Required:** Yes

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

### Create Job
**POST** `/workspaces/<workspace_id>/jobs/`
**Auth Required:** Yes

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
  "job_number": "JOB-A1B2C3D4-00001",
  "title": "HVAC Maintenance",
  "status": "PENDING",
  "priority": "HIGH",
  "assigned_to_email": "contractor@example.com",
  "estimated_hours": 8.00,
  "due_date": "2025-12-15",
  "location": "Building A, Floor 3"
}
```

### List Jobs
**GET** `/workspaces/<workspace_id>/jobs/`
**Auth Required:** Yes

**Response:** `200 OK`

### Get Job Details
**GET** `/workspaces/jobs/<job_id>/`
**Auth Required:** Yes

**Response:** `200 OK`

### Update Job
**PATCH** `/workspaces/jobs/<job_id>/`
**Auth Required:** Yes

**Response:** `200 OK`

### Delete Job
**DELETE** `/workspaces/jobs/<job_id>/`
**Auth Required:** Yes

**Response:** `204 No Content`

### Export Jobs to CSV
**GET** `/workspaces/<workspace_id>/jobs/export/`
**Auth Required:** Yes

**Response:** `200 OK` (CSV file download)

### Create Estimate
**POST** `/workspaces/<workspace_id>/estimates/`
**Auth Required:** Yes

**Request Body:**
```json
{
  "job": 1,
  "title": "HVAC Maintenance Estimate",
  "description": "Cost estimate",
  "status": "DRAFT",
  "subtotal": 1000.00,
  "tax_amount": 80.00,
  "discount_amount": 50.00,
  "total_amount": 1030.00,
  "valid_until": "2025-12-31"
}
```

**Response:** `201 Created`

### List Estimates
**GET** `/workspaces/<workspace_id>/estimates/`
**Auth Required:** Yes

**Response:** `200 OK`

### Export Estimates to CSV
**GET** `/workspaces/<workspace_id>/estimates/export/`
**Auth Required:** Yes

**Response:** `200 OK` (CSV file download)

### Add Contractor
**POST** `/workspaces/<workspace_id>/contractors/`
**Auth Required:** Yes

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
  "address": "123 Main St"
}
```

**Response:** `201 Created`

### List Contractors
**GET** `/workspaces/<workspace_id>/contractors/`
**Auth Required:** Yes

**Response:** `200 OK`

### Export Contractors to CSV
**GET** `/workspaces/<workspace_id>/contractors/export/`
**Auth Required:** Yes

**Response:** `200 OK` (CSV file download)

### Create Payout
**POST** `/workspaces/<workspace_id>/payouts/`
**Auth Required:** Yes

**Request Body:**
```json
{
  "contractor": 1,
  "job": 1,
  "amount": 600.00,
  "status": "PENDING",
  "payment_method": "BANK_TRANSFER",
  "description": "Payment for job",
  "scheduled_date": "2025-12-20"
}
```

**Response:** `201 Created`

### List Payouts
**GET** `/workspaces/<workspace_id>/payouts/`
**Auth Required:** Yes

**Response:** `200 OK`

### Export Payouts to CSV
**GET** `/workspaces/<workspace_id>/payouts/export/`
**Auth Required:** Yes

**Response:** `200 OK` (CSV file download)

### Add Compliance Record
**POST** `/workspaces/<workspace_id>/compliance/`
**Auth Required:** Yes

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

### List Compliance Records
**GET** `/workspaces/<workspace_id>/compliance/`
**Auth Required:** Yes

**Response:** `200 OK`

### Get Expiring Compliance
**GET** `/workspaces/<workspace_id>/compliance/expiring/`
**Auth Required:** Yes

**Response:** `200 OK`
```json
{
  "expiring_soon": [
    {
      "id": 2,
      "contractor_email": "contractor@example.com",
      "compliance_type": "INSURANCE",
      "document_name": "Liability Insurance",
      "expiry_date": "2025-12-20"
    }
  ],
  "expired": []
}
```

### Export Compliance to CSV
**GET** `/workspaces/<workspace_id>/compliance/export/`
**Auth Required:** Yes

**Response:** `200 OK` (CSV file download)

---

## Field Manager (FM) Module

### FM Dashboard
**GET** `/workspaces/fm/dashboard/`
**Auth Required:** FM/Admin

**Response:** `200 OK`
```json
{
  "job_statistics": {
    "total_jobs": 50,
    "pending_jobs": 10,
    "active_jobs": 25,
    "completed_jobs": 15
  },
  "financial_overview": {
    "total_estimated_cost": 150000.00,
    "total_actual_cost": 145000.00,
    "variance": -5000.00,
    "variance_percentage": -3.33
  },
  "estimate_analytics": {
    "total_estimates": 40,
    "draft_estimates": 5,
    "sent_estimates": 10,
    "approved_estimates": 20,
    "signed_estimates": 15
  },
  "recent_jobs": [],
  "upcoming_deadlines": [],
  "overdue_jobs": []
}
```

### Get Jobs by Status
**GET** `/workspaces/fm/jobs/status/<status>/`
**Auth Required:** FM/Admin

**Response:** `200 OK`

### List FM Jobs
**GET** `/workspaces/fm/jobs/`
**Auth Required:** FM/Admin

**Response:** `200 OK`

### Create FM Job
**POST** `/workspaces/fm/jobs/create/`
**Auth Required:** FM/Admin

**Request Body:**
```json
{
  "workspace": 1,
  "title": "Plumbing Repair",
  "description": "Fix leaking pipes",
  "priority": "HIGH",
  "estimated_hours": 4,
  "start_date": "2025-12-10",
  "due_date": "2025-12-12",
  "location": "Building B",
  "customer_name": "John Smith",
  "customer_email": "john@example.com",
  "customer_phone": "+1-555-1234",
  "customer_address": "456 Oak St"
}
```

**Response:** `201 Created`

### Get FM Job Details
**GET** `/workspaces/fm/jobs/<job_id>/`
**Auth Required:** FM/Admin

**Response:** `200 OK`

### Update FM Job
**PATCH** `/workspaces/fm/jobs/<job_id>/`
**Auth Required:** FM/Admin

**Response:** `200 OK`

### Upload Job Attachment
**POST** `/workspaces/fm/jobs/attachments/`
**Auth Required:** FM/Admin

**Request Body:** (multipart/form-data)
```
job: 1
file: [file upload]
description: "Floor plan"
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "job": 1,
  "file": "/media/attachments/file.pdf",
  "file_name": "file.pdf",
  "file_size": 1024000,
  "description": "Floor plan",
  "uploaded_at": "2025-12-05T10:30:00Z"
}
```

### List Job Attachments
**GET** `/workspaces/fm/jobs/<job_id>/attachments/`
**Auth Required:** Yes

**Response:** `200 OK`

### Delete Job Attachment
**DELETE** `/workspaces/fm/jobs/attachments/<attachment_id>/`
**Auth Required:** FM/Admin

**Response:** `204 No Content`

### List FM Estimates
**GET** `/workspaces/fm/estimates/`
**Auth Required:** FM/Admin

**Response:** `200 OK`

### Create FM Estimate
**POST** `/workspaces/fm/estimates/create/`
**Auth Required:** FM/Admin

**Request Body:**
```json
{
  "workspace": 1,
  "job": 1,
  "title": "Plumbing Repair Estimate",
  "description": "Cost estimate for plumbing work",
  "tax_rate": 8.0,
  "discount_amount": 0,
  "valid_until": "2025-12-31",
  "line_items": [
    {
      "description": "Labor",
      "quantity": 4,
      "unit_price": 75.00,
      "total": 300.00
    },
    {
      "description": "Materials",
      "quantity": 1,
      "unit_price": 150.00,
      "total": 150.00
    }
  ]
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "estimate_number": "EST-A1B2C3D4-00001",
  "title": "Plumbing Repair Estimate",
  "status": "DRAFT",
  "subtotal": 450.00,
  "tax_amount": 36.00,
  "discount_amount": 0.00,
  "total_amount": 486.00,
  "line_items": [
    {
      "id": 1,
      "description": "Labor",
      "quantity": 4.00,
      "unit_price": 75.00,
      "total": 300.00
    }
  ]
}
```

### Get FM Estimate Details
**GET** `/workspaces/fm/estimates/<estimate_id>/`
**Auth Required:** FM/Admin

**Response:** `200 OK`

### Update FM Estimate
**PATCH** `/workspaces/fm/estimates/<estimate_id>/`
**Auth Required:** FM/Admin

**Response:** `200 OK`

### Add Estimate Line Item
**POST** `/workspaces/fm/estimates/line-items/`
**Auth Required:** FM/Admin

**Request Body:**
```json
{
  "estimate": 1,
  "description": "Additional materials",
  "quantity": 2,
  "unit_price": 50.00,
  "total": 100.00
}
```

**Response:** `201 Created`

### List Estimate Line Items
**GET** `/workspaces/fm/estimates/<estimate_id>/line-items/`
**Auth Required:** Yes

**Response:** `200 OK`

### Update Line Item
**PATCH** `/workspaces/fm/estimates/line-items/<item_id>/`
**Auth Required:** FM/Admin

**Response:** `200 OK`

### Delete Line Item
**DELETE** `/workspaces/fm/estimates/line-items/<item_id>/`
**Auth Required:** FM/Admin

**Response:** `204 No Content`

### Send Estimate to Customer
**POST** `/workspaces/fm/estimates/<estimate_id>/send/`
**Auth Required:** FM/Admin

**Response:** `200 OK`
```json
{
  "message": "Estimate sent to customer",
  "estimate_number": "EST-A1B2C3D4-00001",
  "status": "SENT"
}
```

### Recalculate Estimate Totals
**POST** `/workspaces/fm/estimates/<estimate_id>/recalculate/`
**Auth Required:** FM/Admin

**Response:** `200 OK`
```json
{
  "subtotal": 450.00,
  "tax_amount": 36.00,
  "discount_amount": 0.00,
  "total_amount": 486.00
}
```

### View Estimate for Signing (Public)
**GET** `/workspaces/public/estimates/<estimate_number>/`
**Auth Required:** No

**Response:** `200 OK`
```json
{
  "id": 1,
  "estimate_number": "EST-A1B2C3D4-00001",
  "title": "Plumbing Repair Estimate",
  "description": "Cost estimate",
  "subtotal": 450.00,
  "tax_amount": 36.00,
  "total_amount": 486.00,
  "status": "SENT",
  "line_items": [],
  "customer_name": "John Smith",
  "customer_email": "john@example.com"
}
```

### Sign Estimate (Public)
**POST** `/workspaces/public/estimates/<estimate_id>/sign/`
**Auth Required:** No

**Request Body:**
```json
{
  "customer_name": "John Smith",
  "customer_email": "john@example.com",
  "signature_data": "data:image/png;base64,iVBORw0KGgoAAAANS..."
}
```

**Response:** `200 OK`
```json
{
  "message": "Estimate signed successfully",
  "estimate_number": "EST-A1B2C3D4-00001",
  "status": "APPROVED",
  "signed_at": "2025-12-05T10:30:00Z"
}
```

---

## Contractor Module

### Contractor Dashboard
**GET** `/workspaces/contractor/dashboard/`
**Auth Required:** Contractor

**Response:** `200 OK`
```json
{
  "job_statistics": {
    "pending_assignments": 3,
    "accepted_jobs": 5,
    "active_jobs": 4,
    "completed_jobs": 25,
    "total_earnings": 15000.00
  },
  "performance_ratings": {
    "average_quality": 4.5,
    "average_timeliness": 4.3,
    "average_professionalism": 4.7,
    "total_ratings": 20
  },
  "recent_notifications": []
}
```

### List Job Assignments
**GET** `/workspaces/contractor/assignments/`
**Auth Required:** Contractor

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "job": {
      "id": 1,
      "job_number": "JOB-A1B2C3D4-00001",
      "title": "HVAC Maintenance",
      "priority": "HIGH"
    },
    "status": "PENDING",
    "assigned_at": "2025-12-05T10:00:00Z",
    "notes": "Please complete by Friday"
  }
]
```

### Accept Job Assignment
**POST** `/workspaces/contractor/assignments/<assignment_id>/accept/`
**Auth Required:** Contractor

**Request Body:**
```json
{
  "notes": "I will start tomorrow morning"
}
```

**Response:** `200 OK`
```json
{
  "message": "Job assignment accepted",
  "assignment_id": 1,
  "status": "ACCEPTED"
}
```

### Reject Job Assignment
**POST** `/workspaces/contractor/assignments/<assignment_id>/reject/`
**Auth Required:** Contractor

**Request Body:**
```json
{
  "reason": "Not available during this time period"
}
```

**Response:** `200 OK`
```json
{
  "message": "Job assignment rejected",
  "assignment_id": 1,
  "status": "REJECTED"
}
```

### List Active Jobs
**GET** `/workspaces/contractor/jobs/active/`
**Auth Required:** Contractor

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "job_number": "JOB-A1B2C3D4-00001",
    "title": "HVAC Maintenance",
    "status": "IN_PROGRESS",
    "priority": "HIGH",
    "due_date": "2025-12-15",
    "checklist": {
      "total_steps": 5,
      "completed_steps": 2,
      "progress_percentage": 40.0
    }
  }
]
```

### Get Contractor Job Details
**GET** `/workspaces/contractor/jobs/<job_id>/`
**Auth Required:** Contractor

**Response:** `200 OK`
```json
{
  "id": 1,
  "job_number": "JOB-A1B2C3D4-00001",
  "title": "HVAC Maintenance",
  "description": "Quarterly maintenance",
  "status": "IN_PROGRESS",
  "priority": "HIGH",
  "location": "Building A, Floor 3",
  "customer_name": "John Smith",
  "customer_phone": "+1-555-1234",
  "checklist": {
    "id": 1,
    "steps": []
  }
}
```

### Update Checklist Step
**PATCH** `/workspaces/contractor/steps/<step_id>/`
**Auth Required:** Contractor

**Request Body:**
```json
{
  "is_completed": true,
  "notes": "Completed successfully, all filters replaced"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "step_number": 1,
  "title": "Replace air filters",
  "description": "Replace all HVAC air filters",
  "is_required": true,
  "is_completed": true,
  "completed_at": "2025-12-05T10:30:00Z",
  "notes": "Completed successfully, all filters replaced"
}
```

### Upload Step Media
**POST** `/workspaces/contractor/steps/media/`
**Auth Required:** Contractor

**Request Body:** (multipart/form-data)
```
step: 1
file: [file upload]
media_type: PHOTO
caption: "Before photo"
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "step": 1,
  "file": "/media/step_media/photo.jpg",
  "media_type": "PHOTO",
  "caption": "Before photo",
  "file_size": 2048000,
  "uploaded_at": "2025-12-05T10:30:00Z"
}
```

### List Step Media
**GET** `/workspaces/contractor/steps/<step_id>/media/`
**Auth Required:** Contractor

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "media_type": "PHOTO",
    "file": "/media/step_media/photo.jpg",
    "caption": "Before photo",
    "uploaded_at": "2025-12-05T10:30:00Z"
  }
]
```

### Delete Step Media
**DELETE** `/workspaces/contractor/steps/media/<media_id>/`
**Auth Required:** Contractor

**Response:** `204 No Content`

### Submit Job Completion
**POST** `/workspaces/contractor/jobs/<job_id>/complete/`
**Auth Required:** Contractor

**Request Body:**
```json
{
  "actual_hours": 7.5,
  "completion_notes": "All tasks completed successfully. Customer satisfied with work."
}
```

**Response:** `200 OK`
```json
{
  "message": "Job completion submitted for review",
  "job_id": 1,
  "job_number": "JOB-A1B2C3D4-00001",
  "completion_id": 1,
  "status": "PENDING_VERIFICATION"
}
```

### List Completed Jobs
**GET** `/workspaces/contractor/completed-jobs/`
**Auth Required:** Contractor

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "job_number": "JOB-A1B2C3D4-00001",
    "title": "HVAC Maintenance",
    "completed_at": "2025-12-05T10:30:00Z",
    "verification_status": "APPROVED",
    "rating": 4.5
  }
]
```

### List Notifications
**GET** `/workspaces/contractor/notifications/`
**Auth Required:** Contractor

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "notification_type": "JOB_ASSIGNED",
    "title": "New Job Assignment",
    "message": "You have been assigned to job JOB-A1B2C3D4-00001",
    "is_read": false,
    "created_at": "2025-12-05T10:00:00Z"
  }
]
```

### Mark Notification as Read
**POST** `/workspaces/contractor/notifications/<notification_id>/read/`
**Auth Required:** Contractor

**Response:** `200 OK`
```json
{
  "message": "Notification marked as read"
}
```

### Mark All Notifications as Read
**POST** `/workspaces/contractor/notifications/read-all/`
**Auth Required:** Contractor

**Response:** `200 OK`
```json
{
  "message": "All notifications marked as read",
  "count": 5
}
```

### Assign Job to Contractor (Admin/FM)
**POST** `/workspaces/admin/assign-job/`
**Auth Required:** FM/Admin

**Request Body:**
```json
{
  "job": 1,
  "contractor": 2,
  "notes": "Please complete by Friday"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "job": 1,
  "contractor": 2,
  "status": "PENDING",
  "assigned_at": "2025-12-05T10:30:00Z",
  "notes": "Please complete by Friday"
}
```

### Verify Job Completion (Admin/FM)
**POST** `/workspaces/admin/verify-completion/<completion_id>/`
**Auth Required:** FM/Admin

**Request Body:**
```json
{
  "status": "APPROVED",
  "quality_rating": 5,
  "timeliness_rating": 4,
  "professionalism_rating": 5,
  "feedback": "Excellent work, completed ahead of schedule"
}
```

**Response:** `200 OK`
```json
{
  "message": "Job completion verified",
  "completion_id": 1,
  "status": "APPROVED",
  "payout_eligibility_created": true
}
```

### Create Job Checklist (Admin/FM)
**POST** `/workspaces/admin/checklists/create/`
**Auth Required:** FM/Admin

**Request Body:**
```json
{
  "job": 1,
  "title": "HVAC Maintenance Checklist",
  "description": "Standard quarterly maintenance steps"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "job": 1,
  "title": "HVAC Maintenance Checklist",
  "description": "Standard quarterly maintenance steps",
  "total_steps": 0,
  "completed_steps": 0,
  "progress_percentage": 0.0
}
```

### Create Checklist Step (Admin/FM)
**POST** `/workspaces/admin/checklist-steps/create/`
**Auth Required:** FM/Admin

**Request Body:**
```json
{
  "checklist": 1,
  "step_number": 1,
  "title": "Replace air filters",
  "description": "Replace all HVAC air filters with new ones",
  "is_required": true
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "checklist": 1,
  "step_number": 1,
  "title": "Replace air filters",
  "description": "Replace all HVAC air filters with new ones",
  "is_required": true,
  "is_completed": false
}
```

---

## Admin Payout & Financial Flow

### View Ready for Payout Jobs
**GET** `/workspaces/admin/payouts/ready/`
**Auth Required:** Admin

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "job_number": "JOB-A1B2C3D4-00001",
    "title": "HVAC Maintenance",
    "contractor_email": "contractor@example.com",
    "contractor_company": "ABC Contractors Inc.",
    "amount": 600.00,
    "completed_at": "2025-12-05T10:30:00Z",
    "verified_at": "2025-12-05T11:00:00Z"
  }
]
```

### Approve Job Payout
**POST** `/workspaces/admin/payouts/<eligibility_id>/approve/`
**Auth Required:** Admin

**Response:** `200 OK`
```json
{
  "message": "Payout approved and credited to contractor wallet",
  "eligibility_id": 1,
  "amount": 600.00,
  "contractor_email": "contractor@example.com",
  "wallet_balance": 1200.00
}
```

### Reject Job Payout
**POST** `/workspaces/admin/payouts/<eligibility_id>/reject/`
**Auth Required:** Admin

**Request Body:**
```json
{
  "reason": "Quality issues need to be addressed"
}
```

**Response:** `200 OK`
```json
{
  "message": "Payout rejected",
  "eligibility_id": 1,
  "reason": "Quality issues need to be addressed"
}
```

### Bulk Approve Payouts
**POST** `/workspaces/admin/payouts/bulk-approve/`
**Auth Required:** Admin

**Request Body:**
```json
{
  "eligibility_ids": [1, 2, 3, 4, 5]
}
```

**Response:** `200 OK`
```json
{
  "message": "Bulk payout approval completed",
  "approved_count": 5,
  "total_amount": 3000.00,
  "failed": []
}
```

### Get Payout Statistics
**GET** `/workspaces/admin/payouts/statistics/`
**Auth Required:** Admin

**Response:** `200 OK`
```json
{
  "ready_for_payout": {
    "count": 10,
    "total_amount": 6000.00
  },
  "processing": {
    "count": 5,
    "total_amount": 2500.00
  },
  "paid_this_month": {
    "count": 25,
    "total_amount": 15000.00
  },
  "total_paid": {
    "count": 150,
    "total_amount": 90000.00
  }
}
```

### List All Payout Requests (Admin)
**GET** `/workspaces/admin/payout-requests/`
**Auth Required:** Admin

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "contractor_email": "contractor@example.com",
    "contractor_company": "ABC Contractors Inc.",
    "amount": 500.00,
    "status": "PENDING",
    "payment_method": "BANK_TRANSFER",
    "bank_account_number": "****5678",
    "requested_at": "2025-12-05T10:00:00Z"
  }
]
```

### Approve Payout Request (Admin)
**POST** `/workspaces/admin/payout-requests/<request_id>/approve/`
**Auth Required:** Admin

**Request Body:**
```json
{
  "transaction_reference": "TXN-123456789"
}
```

**Response:** `200 OK`
```json
{
  "message": "Payout request approved",
  "request_id": 1,
  "amount": 500.00,
  "status": "APPROVED"
}
```

### Reject Payout Request (Admin)
**POST** `/workspaces/admin/payout-requests/<request_id>/reject/`
**Auth Required:** Admin

**Request Body:**
```json
{
  "reason": "Insufficient documentation provided"
}
```

**Response:** `200 OK`
```json
{
  "message": "Payout request rejected",
  "request_id": 1,
  "reason": "Insufficient documentation provided"
}
```

### Get Contractor Wallet
**GET** `/workspaces/contractor/wallet/`
**Auth Required:** Contractor

**Response:** `200 OK`
```json
{
  "balance": 1200.00,
  "total_earned": 15000.00,
  "total_withdrawn": 13800.00,
  "pending_amount": 300.00,
  "last_transaction_date": "2025-12-05T10:30:00Z"
}
```

### Get Wallet Transactions
**GET** `/workspaces/contractor/wallet/transactions/`
**Auth Required:** Contractor

**Query Parameters:**
- `transaction_type` - Filter by CREDIT or DEBIT
- `start_date` - Filter from date
- `end_date` - Filter to date

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "transaction_type": "CREDIT",
    "amount": 600.00,
    "balance_after": 1200.00,
    "description": "Payment for job JOB-A1B2C3D4-00001",
    "reference_number": "TXN-123456",
    "created_at": "2025-12-05T10:30:00Z"
  }
]
```

### Download Wallet Ledger CSV
**GET** `/workspaces/contractor/wallet/ledger/download/`
**Auth Required:** Contractor

**Query Parameters:**
- `start_date` - From date (YYYY-MM-DD)
- `end_date` - To date (YYYY-MM-DD)

**Response:** `200 OK` (CSV file download)

### Request Payout
**POST** `/workspaces/contractor/wallet/request-payout/`
**Auth Required:** Contractor

**Request Body:**
```json
{
  "amount": 500.00,
  "payment_method": "BANK_TRANSFER",
  "bank_account_number": "1234567890",
  "bank_routing_number": "987654321",
  "bank_name": "First National Bank",
  "notes": "Please process by end of week"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "amount": 500.00,
  "status": "PENDING",
  "payment_method": "BANK_TRANSFER",
  "requested_at": "2025-12-05T10:30:00Z",
  "message": "Payout request submitted successfully"
}
```

### List Contractor Payout Requests
**GET** `/workspaces/contractor/payout-requests/`
**Auth Required:** Contractor

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "amount": 500.00,
    "status": "PENDING",
    "payment_method": "BANK_TRANSFER",
    "requested_at": "2025-12-05T10:30:00Z",
    "processed_at": null
  }
]
```

### Download Payout Report (Admin)
**GET** `/workspaces/admin/payouts/report/download/`
**Auth Required:** Admin

**Query Parameters:**
- `start_date` - From date (YYYY-MM-DD)
- `end_date` - To date (YYYY-MM-DD)
- `status` - Filter by status (PENDING, APPROVED, PAID)

**Response:** `200 OK` (CSV file download)

---

## Compliance & Disputes

### Contractor Compliance Hub
**GET** `/workspaces/contractor/compliance/hub/`
**Auth Required:** Contractor

**Response:** `200 OK`
```json
{
  "compliance_summary": {
    "total_documents": 5,
    "valid_documents": 3,
    "expiring_soon": 1,
    "expired": 1
  },
  "documents": [
    {
      "id": 1,
      "compliance_type": "LICENSE",
      "document_name": "Contractor License",
      "status": "VALID",
      "expiry_date": "2026-01-01",
      "is_expiring_soon": false
    }
  ],
  "pending_uploads": ["INSURANCE", "CERTIFICATION"]
}
```

### Upload Compliance Document
**POST** `/workspaces/contractor/compliance/upload/`
**Auth Required:** Contractor

**Request Body:** (multipart/form-data)
```
compliance_type: LICENSE
document_name: Contractor License
document_number: LIC-12345
issue_date: 2024-01-01
expiry_date: 2026-01-01
file: [file upload]
notes: Valid contractor license
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "compliance_type": "LICENSE",
  "document_name": "Contractor License",
  "document_number": "LIC-12345",
  "status": "PENDING_VERIFICATION",
  "file_path": "/media/compliance/license.pdf",
  "file_size": 1024000,
  "uploaded_at": "2025-12-05T10:30:00Z"
}
```

### Admin Compliance Center
**GET** `/workspaces/admin/compliance/center/`
**Auth Required:** Admin

**Response:** `200 OK`
```json
{
  "pending_verification": [
    {
      "id": 1,
      "contractor_email": "contractor@example.com",
      "compliance_type": "LICENSE",
      "document_name": "Contractor License",
      "uploaded_at": "2025-12-05T10:00:00Z"
    }
  ],
  "expiring_soon": [],
  "expired": [],
  "statistics": {
    "total_documents": 50,
    "pending_verification": 5,
    "valid": 40,
    "expiring_soon": 3,
    "expired": 2
  }
}
```

### Approve Compliance Document (Admin)
**POST** `/workspaces/admin/compliance/<compliance_id>/approve/`
**Auth Required:** Admin

**Request Body:**
```json
{
  "notes": "Document verified and approved"
}
```

**Response:** `200 OK`
```json
{
  "message": "Compliance document approved",
  "compliance_id": 1,
  "status": "VALID"
}
```

### Reject Compliance Document (Admin)
**POST** `/workspaces/admin/compliance/<compliance_id>/reject/`
**Auth Required:** Admin

**Request Body:**
```json
{
  "reason": "Document is expired or illegible"
}
```

**Response:** `200 OK`
```json
{
  "message": "Compliance document rejected",
  "compliance_id": 1,
  "status": "REJECTED",
  "reason": "Document is expired or illegible"
}
```

### Create Dispute
**POST** `/workspaces/disputes/create/`
**Auth Required:** Yes

**Request Body:**
```json
{
  "job": 1,
  "dispute_type": "QUALITY",
  "title": "Work quality issue",
  "description": "The completed work does not meet specifications",
  "priority": "HIGH"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "dispute_number": "DISP-A1B2C3D4-00001",
  "job": 1,
  "dispute_type": "QUALITY",
  "title": "Work quality issue",
  "status": "OPEN",
  "priority": "HIGH",
  "raised_by": "user@example.com",
  "created_at": "2025-12-05T10:30:00Z"
}
```

### List Disputes
**GET** `/workspaces/disputes/`
**Auth Required:** Yes

**Query Parameters:**
- `status` - Filter by status (OPEN, IN_PROGRESS, RESOLVED, CLOSED)
- `dispute_type` - Filter by type

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "dispute_number": "DISP-A1B2C3D4-00001",
    "job_number": "JOB-A1B2C3D4-00001",
    "dispute_type": "QUALITY",
    "title": "Work quality issue",
    "status": "OPEN",
    "priority": "HIGH",
    "raised_by": "user@example.com",
    "created_at": "2025-12-05T10:30:00Z"
  }
]
```

### Get Dispute Details
**GET** `/workspaces/disputes/<dispute_id>/`
**Auth Required:** Yes

**Response:** `200 OK`
```json
{
  "id": 1,
  "dispute_number": "DISP-A1B2C3D4-00001",
  "job": {
    "id": 1,
    "job_number": "JOB-A1B2C3D4-00001",
    "title": "HVAC Maintenance"
  },
  "dispute_type": "QUALITY",
  "title": "Work quality issue",
  "description": "The completed work does not meet specifications",
  "status": "OPEN",
  "priority": "HIGH",
  "raised_by": "user@example.com",
  "assigned_to": null,
  "messages": [],
  "attachments": [],
  "created_at": "2025-12-05T10:30:00Z"
}
```

### Add Dispute Message
**POST** `/workspaces/disputes/<dispute_id>/messages/`
**Auth Required:** Yes

**Request Body:**
```json
{
  "message": "I have reviewed the issue and will address it tomorrow"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "dispute": 1,
  "sender": "contractor@example.com",
  "message": "I have reviewed the issue and will address it tomorrow",
  "created_at": "2025-12-05T11:00:00Z"
}
```

### Upload Dispute Attachment
**POST** `/workspaces/disputes/<dispute_id>/attachments/`
**Auth Required:** Yes

**Request Body:** (multipart/form-data)
```
file: [file upload]
description: "Photo of the issue"
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "dispute": 1,
  "file": "/media/disputes/photo.jpg",
  "description": "Photo of the issue",
  "uploaded_by": "user@example.com",
  "uploaded_at": "2025-12-05T11:00:00Z"
}
```

### Update Dispute Status
**PATCH** `/workspaces/disputes/<dispute_id>/`
**Auth Required:** Admin/FM

**Request Body:**
```json
{
  "status": "RESOLVED",
  "resolution_notes": "Issue has been addressed and customer is satisfied"
}
```

**Response:** `200 OK`
```json
{
  "message": "Dispute updated successfully",
  "dispute_id": 1,
  "status": "RESOLVED"
}
```

### Escalate Dispute
**POST** `/workspaces/disputes/<dispute_id>/escalate/`
**Auth Required:** Yes

**Request Body:**
```json
{
  "escalation_reason": "Issue not resolved after multiple attempts"
}
```

**Response:** `200 OK`
```json
{
  "message": "Dispute escalated successfully",
  "dispute_id": 1,
  "escalation_level": 2
}
```

---

## Investor Module

### Investor Dashboard
**GET** `/workspaces/investor/dashboard/`
**Auth Required:** Investor

**Response:** `200 OK`
```json
{
  "revenue_statistics": {
    "total_revenue": 250000.00,
    "revenue_this_month": 25000.00,
    "revenue_last_month": 22000.00,
    "growth_percentage": 13.64
  },
  "roi_analytics": {
    "total_investment": 500000.00,
    "total_returns": 250000.00,
    "roi_percentage": 50.0,
    "projected_annual_roi": 60.0
  },
  "job_volume": {
    "total_jobs": 150,
    "completed_jobs": 120,
    "active_jobs": 25,
    "pending_jobs": 5,
    "completion_rate": 80.0
  },
  "payout_analytics": {
    "total_payouts": 180000.00,
    "payouts_this_month": 18000.00,
    "average_payout": 1500.00,
    "pending_payouts": 5000.00
  }
}
```

### Get Monthly Revenue Breakdown
**GET** `/workspaces/investor/revenue/monthly/`
**Auth Required:** Investor

**Query Parameters:**
- `year` - Year (default: current year)

**Response:** `200 OK`
```json
{
  "year": 2025,
  "monthly_data": [
    {
      "month": 1,
      "month_name": "January",
      "revenue": 20000.00,
      "jobs_completed": 15,
      "average_job_value": 1333.33
    },
    {
      "month": 2,
      "month_name": "February",
      "revenue": 22000.00,
      "jobs_completed": 18,
      "average_job_value": 1222.22
    }
  ],
  "total_revenue": 250000.00,
  "average_monthly_revenue": 20833.33
}
```

### Get Workspace Performance Comparison
**GET** `/workspaces/investor/performance/comparison/`
**Auth Required:** Investor

**Response:** `200 OK`
```json
[
  {
    "workspace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "workspace_name": "Downtown Facility Project",
    "total_revenue": 150000.00,
    "total_jobs": 80,
    "completion_rate": 85.0,
    "average_job_value": 1875.00,
    "total_payouts": 100000.00
  },
  {
    "workspace_id": "b2c3d4e5-f6g7-8901-bcde-fg2345678901",
    "workspace_name": "Uptown Complex",
    "total_revenue": 100000.00,
    "total_jobs": 70,
    "completion_rate": 75.0,
    "average_job_value": 1428.57,
    "total_payouts": 80000.00
  }
]
```

### Get Top Contractors by Earnings
**GET** `/workspaces/investor/contractors/top-earners/`
**Auth Required:** Investor

**Query Parameters:**
- `limit` - Number of contractors (default: 10)

**Response:** `200 OK`
```json
[
  {
    "contractor_id": 1,
    "contractor_email": "contractor@example.com",
    "contractor_company": "ABC Contractors Inc.",
    "total_earnings": 25000.00,
    "jobs_completed": 35,
    "average_rating": 4.7,
    "completion_rate": 95.0
  }
]
```

### Download Investor Report CSV
**GET** `/workspaces/investor/reports/download/`
**Auth Required:** Investor

**Query Parameters:**
- `report_type` - Type: revenue, jobs, payouts, contractors
- `start_date` - From date (YYYY-MM-DD)
- `end_date` - To date (YYYY-MM-DD)

**Response:** `200 OK` (CSV file download)

### Get Recent Activity Feed
**GET** `/workspaces/investor/activity/recent/`
**Auth Required:** Investor

**Query Parameters:**
- `limit` - Number of activities (default: 20)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "activity_type": "JOB_COMPLETED",
    "description": "Job JOB-A1B2C3D4-00001 completed",
    "workspace_name": "Downtown Facility Project",
    "amount": 1500.00,
    "timestamp": "2025-12-05T10:30:00Z"
  },
  {
    "id": 2,
    "activity_type": "PAYOUT_PROCESSED",
    "description": "Payout of $600 processed",
    "workspace_name": "Downtown Facility Project",
    "amount": 600.00,
    "timestamp": "2025-12-05T09:00:00Z"
  }
]
```

---

## AI-Assisted Features

### Generate AI Job Description
**POST** `/workspaces/ai/generate-job-description/`
**Auth Required:** FM/Admin

**Request Body:**
```json
{
  "job_type": "HVAC_MAINTENANCE",
  "additional_details": "Quarterly maintenance for commercial building"
}
```

**Response:** `200 OK`
```json
{
  "job_type": "HVAC_MAINTENANCE",
  "generated_description": "Perform comprehensive HVAC system maintenance including filter replacement, coil cleaning, refrigerant level check, thermostat calibration, and system performance testing. Ensure all components are functioning optimally and identify any potential issues.",
  "estimated_hours": 6,
  "recommended_priority": "MEDIUM"
}
```

### Get AI Checklist Suggestions
**POST** `/workspaces/ai/suggest-checklist/`
**Auth Required:** FM/Admin

**Request Body:**
```json
{
  "job_type": "PLUMBING_REPAIR",
  "job_description": "Fix leaking pipes in bathroom"
}
```

**Response:** `200 OK`
```json
{
  "job_type": "PLUMBING_REPAIR",
  "suggested_steps": [
    {
      "step_number": 1,
      "title": "Inspect leak source",
      "description": "Identify the exact location and cause of the leak",
      "is_required": true,
      "estimated_time": 15
    },
    {
      "step_number": 2,
      "title": "Shut off water supply",
      "description": "Turn off water supply to the affected area",
      "is_required": true,
      "estimated_time": 5
    },
    {
      "step_number": 3,
      "title": "Remove damaged pipe section",
      "description": "Cut out and remove the damaged pipe section",
      "is_required": true,
      "estimated_time": 30
    }
  ],
  "total_estimated_time": 120
}
```

### Detect Pricing Anomalies
**POST** `/workspaces/ai/detect-pricing-anomalies/`
**Auth Required:** FM/Admin

**Request Body:**
```json
{
  "estimate_id": 1
}
```

**Response:** `200 OK`
```json
{
  "estimate_id": 1,
  "estimate_number": "EST-A1B2C3D4-00001",
  "has_anomalies": true,
  "anomalies": [
    {
      "line_item": "Labor",
      "issue": "PRICE_TOO_HIGH",
      "current_price": 150.00,
      "expected_range": "50.00 - 100.00",
      "severity": "HIGH",
      "recommendation": "Review labor rate - significantly higher than market average"
    }
  ],
  "overall_assessment": "REVIEW_RECOMMENDED",
  "confidence_score": 0.85
}
```

### Detect Missing Items
**POST** `/workspaces/ai/detect-missing-items/`
**Auth Required:** FM/Admin

**Request Body:**
```json
{
  "job_type": "HVAC_MAINTENANCE",
  "estimate_id": 1
}
```

**Response:** `200 OK`
```json
{
  "estimate_id": 1,
  "job_type": "HVAC_MAINTENANCE",
  "missing_items": [
    {
      "item": "Air filter replacement",
      "reason": "Standard component for HVAC maintenance",
      "priority": "HIGH",
      "estimated_cost": 50.00
    },
    {
      "item": "Refrigerant level check",
      "reason": "Essential for system efficiency",
      "priority": "MEDIUM",
      "estimated_cost": 75.00
    }
  ],
  "completeness_score": 0.65,
  "recommendation": "Consider adding missing items for comprehensive service"
}
```

### Get Smart Recommendations for FM
**GET** `/workspaces/ai/recommendations/fm/`
**Auth Required:** FM/Admin

**Response:** `200 OK`
```json
{
  "recommendations": [
    {
      "type": "OVERDUE_JOBS",
      "priority": "HIGH",
      "title": "5 jobs are overdue",
      "description": "Review and reassign or extend deadlines for overdue jobs",
      "action_url": "/workspaces/fm/jobs/status/OVERDUE",
      "affected_count": 5
    },
    {
      "type": "PENDING_ESTIMATES",
      "priority": "MEDIUM",
      "title": "8 estimates awaiting customer response",
      "description": "Follow up with customers on pending estimates",
      "action_url": "/workspaces/fm/estimates/?status=SENT",
      "affected_count": 8
    },
    {
      "type": "COMPLIANCE_EXPIRING",
      "priority": "HIGH",
      "title": "3 contractor compliance documents expiring soon",
      "description": "Request updated compliance documents from contractors",
      "action_url": "/workspaces/compliance/expiring",
      "affected_count": 3
    }
  ],
  "generated_at": "2025-12-05T10:30:00Z"
}
```

### Get Contractor Recommendations
**POST** `/workspaces/ai/recommend-contractors/`
**Auth Required:** FM/Admin

**Request Body:**
```json
{
  "job_id": 1,
  "job_type": "HVAC_MAINTENANCE",
  "priority": "HIGH",
  "location": "Building A, Floor 3"
}
```

**Response:** `200 OK`
```json
{
  "job_id": 1,
  "recommended_contractors": [
    {
      "contractor_id": 1,
      "contractor_email": "contractor@example.com",
      "contractor_company": "ABC Contractors Inc.",
      "match_score": 0.95,
      "reasons": [
        "Specializes in HVAC systems",
        "High rating (4.7/5.0)",
        "95% completion rate",
        "Available immediately"
      ],
      "average_rating": 4.7,
      "jobs_completed": 35,
      "hourly_rate": 75.00
    },
    {
      "contractor_id": 2,
      "contractor_email": "contractor2@example.com",
      "contractor_company": "XYZ Services",
      "match_score": 0.88,
      "reasons": [
        "HVAC experience",
        "Good rating (4.5/5.0)",
        "Located nearby"
      ],
      "average_rating": 4.5,
      "jobs_completed": 28,
      "hourly_rate": 70.00
    }
  ]
}
```

### Identify At-Risk Jobs
**GET** `/workspaces/ai/jobs/at-risk/`
**Auth Required:** FM/Admin

**Response:** `200 OK`
```json
{
  "at_risk_jobs": [
    {
      "job_id": 1,
      "job_number": "JOB-A1B2C3D4-00001",
      "title": "HVAC Maintenance",
      "risk_level": "HIGH",
      "risk_factors": [
        "Due date in 2 days",
        "Only 40% complete",
        "Contractor has not updated progress in 3 days"
      ],
      "recommendations": [
        "Contact contractor for status update",
        "Consider extending deadline or reassigning"
      ],
      "due_date": "2025-12-07",
      "progress_percentage": 40.0
    }
  ],
  "total_at_risk": 3
}
```

### Get Workflow Optimization Tips
**GET** `/workspaces/ai/optimization/tips/`
**Auth Required:** FM/Admin

**Response:** `200 OK`
```json
{
  "optimization_tips": [
    {
      "category": "EFFICIENCY",
      "title": "Batch similar jobs together",
      "description": "You have 5 HVAC maintenance jobs. Consider assigning them to the same contractor to reduce travel time and costs.",
      "potential_savings": "15% time reduction",
      "priority": "MEDIUM"
    },
    {
      "category": "COST",
      "title": "Review contractor rates",
      "description": "Contractor ABC's rates are 20% higher than market average. Consider negotiating or exploring alternatives.",
      "potential_savings": "$500/month",
      "priority": "LOW"
    },
    {
      "category": "QUALITY",
      "title": "Implement preventive maintenance schedule",
      "description": "70% of jobs are reactive repairs. A preventive maintenance schedule could reduce emergency repairs by 40%.",
      "potential_savings": "$2000/month",
      "priority": "HIGH"
    }
  ],
  "generated_at": "2025-12-05T10:30:00Z"
}
```

---

## PDF Generation

### Generate Estimate PDF
**GET** `/workspaces/pdf/estimate/<estimate_id>/`
**Auth Required:** FM/Admin

**Response:** `200 OK` (PDF file download)

### Generate Job Report PDF
**GET** `/workspaces/pdf/job-report/<job_id>/`
**Auth Required:** FM/Admin

**Response:** `200 OK` (PDF file download)

### Generate Payout Slip PDF
**GET** `/workspaces/pdf/payout-slip/<payout_request_id>/`
**Auth Required:** Admin/Contractor

**Response:** `200 OK` (PDF file download)

### Generate Compliance Certificate PDF
**GET** `/workspaces/pdf/compliance-certificate/<compliance_id>/`
**Auth Required:** Admin/Contractor

**Response:** `200 OK` (PDF file download)

### Generate Investor Report PDF
**GET** `/workspaces/pdf/investor-report/`
**Auth Required:** Investor

**Query Parameters:**
- `start_date` - From date (YYYY-MM-DD)
- `end_date` - To date (YYYY-MM-DD)
- `report_type` - Type: summary, detailed, financial

**Response:** `200 OK` (PDF file download)

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
  "error": "Permission denied",
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "error": "Resource not found",
  "detail": "The requested resource does not exist."
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "detail": "An unexpected error occurred. Please try again later."
}
```

---

## Pagination

List endpoints support pagination. Default page size is 20 items.

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (max: 100, default: 20)

**Response Format:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Filtering & Searching

Most list endpoints support filtering and searching:

**Common Query Parameters:**
- `search` - Search across multiple fields
- `ordering` - Sort by field (prefix with `-` for descending)
- `status` - Filter by status
- `created_at__gte` - Filter by date (greater than or equal)
- `created_at__lte` - Filter by date (less than or equal)

**Example:**
```
GET /api/workspaces/1/jobs/?search=HVAC&status=PENDING&ordering=-created_at
```

---

## Rate Limiting

Currently, no rate limiting is implemented. For production deployment, consider implementing rate limiting using:
- Django REST Framework throttling
- Redis-based rate limiting
- API Gateway rate limiting

**Recommended Limits:**
- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour
- Admin: 5000 requests/hour

---

## API Versioning

Current API version: **v1**

All endpoints are prefixed with `/api/` and currently use version 1.

Future versions will be accessible via:
- URL versioning: `/api/v2/endpoint/`
- Header versioning: `Accept: application/json; version=2`

---

## Authentication Flow

### Standard Login Flow
1. **POST** `/auth/login/` with email and password
2. Receive `access` and `refresh` tokens
3. Use `access` token in Authorization header for subsequent requests
4. When `access` token expires, use **POST** `/auth/token/refresh/` with `refresh` token
5. Receive new `access` token

### Magic Link Flow
1. **POST** `/auth/magic-link/request/` with email
2. User receives email with magic link
3. User clicks link, which redirects to frontend with token
4. Frontend calls **POST** `/auth/magic-link/verify/` with token
5. Receive `access` and `refresh` tokens

---

## File Upload Guidelines

### Supported File Types
- **Images:** JPG, PNG, GIF (max 5MB)
- **Documents:** PDF, DOC, DOCX (max 10MB)
- **Videos:** MP4, MOV (max 50MB)

### Upload Format
Use `multipart/form-data` content type for file uploads.

**Example:**
```bash
curl -X POST http://localhost:8000/api/workspaces/fm/jobs/attachments/ \
  -H "Authorization: Bearer <token>" \
  -F "job=1" \
  -F "file=@/path/to/file.pdf" \
  -F "description=Floor plan"
```

---

## Webhook Support (Future)

Planned webhook events:
- `job.created`
- `job.completed`
- `estimate.signed`
- `payout.approved`
- `compliance.expiring`
- `dispute.created`

---

## API Testing

### Using Postman
1. Import `POSTMAN_COLLECTION.json`
2. Set environment variable `base_url` to `http://localhost:8000/api`
3. Login to get access token (automatically saved)
4. Test all endpoints with pre-configured requests

### Using cURL
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Use token
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer <access_token>"
```

---

## Support & Documentation

- **API Documentation:** This file
- **Module Guides:** See individual module guide files
- **Testing Report:** `TESTING_REPORT.md`
- **Deployment Guide:** `DEPLOYMENT_SUMMARY.md`
- **GitHub Issues:** For bug reports and feature requests
- **Email Support:** support@yourapp.com

---

**Last Updated:** December 10, 2025
**API Version:** 1.0
**Total Endpoints:** 135+
