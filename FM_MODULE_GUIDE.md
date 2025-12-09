# Field Manager (FM) Module - Complete Guide

## Overview

Field Manager module facility management professionals ke liye design kiya gaya hai jo jobs create karte hain, estimates banate hain, aur customer signatures collect karte hain.

## Key Features

### 1. FM Dashboard
Real-time overview of all FM activities:
- Job statistics (Pending, Active, Completed, Cancelled)
- Financial tracking (Estimated vs Actual costs)
- Estimate analytics (Draft, Sent, Approved, Signed)
- Recent jobs list
- Upcoming deadlines
- Overdue jobs alert

### 2. Job Management
Complete job lifecycle management:
- Create jobs with full details
- Customer information (name, email, phone, address)
- Pricing (estimated and actual costs)
- Status workflow (Pending → In Progress → Completed)
- Priority levels (Low, Medium, High, Urgent)
- File attachments support
- Due date tracking

### 3. Estimate Creation
Professional estimate generation:
- Multiple line items support
- Automatic calculations (subtotal, tax, total)
- Configurable tax rate
- Discount support
- Draft and send workflow
- Unique estimate numbering

### 4. Digital Signature
Secure customer approval:
- Public signing links
- Canvas-based signature capture
- Base64 signature storage
- IP address tracking
- Timestamp recording
- Automatic status update on signing

## API Endpoints

### Dashboard

#### Get FM Dashboard
```
GET /api/workspaces/fm/dashboard/
Query Parameters:
  - workspace_id (optional): Filter by workspace

Response:
{
  "job_statistics": {
    "total_jobs": 25,
    "pending_jobs": 5,
    "active_jobs": 10,
    "completed_jobs": 10,
    "cancelled_jobs": 0,
    "high_priority": 3,
    "urgent_priority": 1,
    "overdue_jobs": 2
  },
  "financial_overview": {
    "total_estimated_cost": 50000.00,
    "total_actual_cost": 48500.00,
    "variance": 1500.00
  },
  "estimate_statistics": {
    "total_estimates": 15,
    "draft_estimates": 2,
    "sent_estimates": 5,
    "approved_estimates": 8,
    "signed_estimates": 7,
    "total_estimate_value": 75000.00,
    "approved_estimate_value": 60000.00
  },
  "recent_jobs": [...],
  "upcoming_deadlines": [...]
}
```

#### Get Jobs by Status
```
GET /api/workspaces/fm/jobs/status/{status}/
Parameters:
  - status: pending, in_progress, completed, cancelled

Query Parameters:
  - workspace_id (optional): Filter by workspace

Response:
{
  "status": "pending",
  "count": 5,
  "jobs": [...]
}
```

### Job Management

#### Create Job
```
POST /api/workspaces/fm/jobs/create/

Request Body:
{
  "workspace_id": "uuid",
  "title": "HVAC System Repair",
  "description": "Complete HVAC system inspection and repair",
  "status": "PENDING",
  "priority": "HIGH",
  "assigned_to": 2,
  "estimated_hours": 8,
  "estimated_cost": 1500.00,
  "start_date": "2025-12-10",
  "due_date": "2025-12-20",
  "location": "Building A, Floor 3",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+1-555-0123",
  "customer_address": "123 Main St, City, State",
  "notes": "Customer prefers morning appointments"
}

Response: 201 Created
{
  "id": 1,
  "job_number": "JOB-A1B2C3D4-00001",
  "title": "HVAC System Repair",
  ...
}
```

#### List FM's Jobs
```
GET /api/workspaces/fm/jobs/

Query Parameters:
  - workspace_id: Filter by workspace
  - status: Filter by status
  - priority: Filter by priority

Response: 200 OK
[
  {
    "id": 1,
    "job_number": "JOB-A1B2C3D4-00001",
    "title": "HVAC System Repair",
    "status": "PENDING",
    "priority": "HIGH",
    "customer_name": "John Doe",
    "attachment_count": 3,
    ...
  }
]
```

#### Update Job
```
PATCH /api/workspaces/fm/jobs/{id}/

Request Body:
{
  "status": "IN_PROGRESS",
  "actual_hours": 6.5,
  "actual_cost": 1350.00
}

Response: 200 OK
```

### Job Attachments

#### Upload Attachment
```
POST /api/workspaces/fm/jobs/attachments/

Request Body:
{
  "job": 1,
  "file_name": "blueprint.pdf",
  "file_path": "/uploads/jobs/blueprint.pdf",
  "file_type": "application/pdf",
  "file_size": 2048576,
  "description": "Building blueprint"
}

Response: 201 Created
```

#### List Job Attachments
```
GET /api/workspaces/fm/jobs/{job_id}/attachments/

Response: 200 OK
[
  {
    "id": 1,
    "file_name": "blueprint.pdf",
    "file_type": "application/pdf",
    "file_size": 2048576,
    "uploaded_by_email": "fm@example.com",
    "created_at": "2025-12-05T10:30:00Z"
  }
]
```

### Estimate Management

#### Create Estimate with Line Items
```
POST /api/workspaces/fm/estimates/create/

Request Body:
{
  "workspace_id": "uuid",
  "job": 1,
  "title": "HVAC Repair Estimate",
  "description": "Complete cost breakdown for HVAC repair",
  "tax_rate": 8.5,
  "discount_amount": 50.00,
  "valid_until": "2025-12-31",
  "line_items": [
    {
      "item_order": 1,
      "description": "HVAC System Inspection",
      "quantity": 1,
      "unit_price": 200.00
    },
    {
      "item_order": 2,
      "description": "Compressor Replacement",
      "quantity": 1,
      "unit_price": 800.00
    },
    {
      "item_order": 3,
      "description": "Labor (8 hours)",
      "quantity": 8,
      "unit_price": 75.00
    }
  ],
  "notes": "All parts include 1-year warranty"
}

Response: 201 Created
{
  "id": 1,
  "estimate_number": "EST-A1B2C3D4-00001",
  "title": "HVAC Repair Estimate",
  "subtotal": 1600.00,
  "tax_amount": 136.00,
  "total_amount": 1686.00,
  "line_items": [...],
  ...
}
```

#### List FM's Estimates
```
GET /api/workspaces/fm/estimates/

Query Parameters:
  - workspace_id: Filter by workspace
  - status: Filter by status

Response: 200 OK
[
  {
    "id": 1,
    "estimate_number": "EST-A1B2C3D4-00001",
    "title": "HVAC Repair Estimate",
    "status": "SENT",
    "total_amount": 1686.00,
    "is_signed": false,
    "line_item_count": 3,
    ...
  }
]
```

#### Update Estimate
```
PATCH /api/workspaces/fm/estimates/{id}/

Request Body:
{
  "tax_rate": 9.0,
  "discount_amount": 100.00
}

Response: 200 OK
```

### Estimate Line Items

#### Add Line Item
```
POST /api/workspaces/fm/estimates/line-items/

Request Body:
{
  "estimate": 1,
  "item_order": 4,
  "description": "Additional parts",
  "quantity": 2,
  "unit_price": 50.00,
  "notes": "Optional upgrade"
}

Response: 201 Created
{
  "id": 4,
  "description": "Additional parts",
  "quantity": 2,
  "unit_price": 50.00,
  "total": 100.00
}
```

#### Update Line Item
```
PATCH /api/workspaces/fm/estimates/line-items/{id}/

Request Body:
{
  "quantity": 3,
  "unit_price": 45.00
}

Response: 200 OK
```

#### Delete Line Item
```
DELETE /api/workspaces/fm/estimates/line-items/{id}/

Response: 204 No Content
```

### Estimate Actions

#### Send Estimate to Customer
```
POST /api/workspaces/fm/estimates/{id}/send/

Response: 200 OK
{
  "message": "Estimate sent successfully",
  "estimate_number": "EST-A1B2C3D4-00001",
  "status": "SENT"
}
```

#### Recalculate Estimate Totals
```
POST /api/workspaces/fm/estimates/{id}/recalculate/

Response: 200 OK
{
  "message": "Estimate totals recalculated",
  "subtotal": 1600.00,
  "tax_amount": 136.00,
  "total_amount": 1686.00
}
```

### Customer Signature (Public Endpoints)

#### Get Estimate for Signing
```
GET /api/workspaces/public/estimates/{estimate_number}/

Response: 200 OK
{
  "estimate_number": "EST-A1B2C3D4-00001",
  "title": "HVAC Repair Estimate",
  "description": "Complete cost breakdown",
  "status": "SENT",
  "line_items": [...],
  "subtotal": 1600.00,
  "tax_rate": 8.5,
  "tax_amount": 136.00,
  "discount_amount": 50.00,
  "total_amount": 1686.00,
  "valid_until": "2025-12-31",
  "is_signed": false,
  "created_at": "2025-12-05T10:30:00Z"
}
```

#### Sign Estimate
```
POST /api/workspaces/public/estimates/{id}/sign/

Request Body:
{
  "signature": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}

Response: 200 OK
{
  "message": "Estimate signed successfully",
  "estimate_number": "EST-A1B2C3D4-00001",
  "signed_at": "2025-12-05T14:30:00Z"
}
```

## Workflow Examples

### Complete Job Creation Workflow

1. **FM logs in**
```bash
POST /api/auth/login/
{
  "email": "fm@example.com",
  "password": "password"
}
```

2. **FM creates a job**
```bash
POST /api/workspaces/fm/jobs/create/
{
  "workspace_id": "uuid",
  "title": "HVAC Repair",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  ...
}
```

3. **FM uploads attachments**
```bash
POST /api/workspaces/fm/jobs/attachments/
{
  "job": 1,
  "file_name": "photo1.jpg",
  ...
}
```

4. **FM creates estimate**
```bash
POST /api/workspaces/fm/estimates/create/
{
  "job": 1,
  "line_items": [...]
}
```

5. **FM sends estimate to customer**
```bash
POST /api/workspaces/fm/estimates/1/send/
```

6. **Customer receives email with link**
```
https://yourapp.com/sign-estimate/EST-A1B2C3D4-00001
```

7. **Customer views and signs estimate**
```bash
GET /api/workspaces/public/estimates/EST-A1B2C3D4-00001/
POST /api/workspaces/public/estimates/1/sign/
```

8. **FM receives notification and updates job**
```bash
PATCH /api/workspaces/fm/jobs/1/
{
  "status": "IN_PROGRESS"
}
```

## Database Models

### Job Model
```python
- workspace (FK)
- job_number (unique)
- title
- description
- status (PENDING, IN_PROGRESS, COMPLETED, CANCELLED)
- priority (LOW, MEDIUM, HIGH, URGENT)
- assigned_to (FK to User)
- created_by (FK to User)
- estimated_hours, actual_hours
- estimated_cost, actual_cost
- start_date, due_date, completed_date
- location
- customer_name, customer_email, customer_phone, customer_address
- notes
```

### JobAttachment Model
```python
- job (FK)
- file_name
- file_path
- file_type
- file_size
- uploaded_by (FK to User)
- description
```

### Estimate Model
```python
- workspace (FK)
- job (FK)
- estimate_number (unique)
- title, description
- status (DRAFT, SENT, APPROVED, REJECTED, EXPIRED)
- subtotal, tax_rate, tax_amount, discount_amount, total_amount
- valid_until
- created_by (FK to User)
- approved_by (FK to User)
- customer_signature (Base64)
- customer_signed_at
- customer_ip_address
```

### EstimateLineItem Model
```python
- estimate (FK)
- item_order
- description
- quantity
- unit_price
- total (calculated)
- notes
```

## Frontend Integration

### Customer Signature Page
See `customer_signature_example.html` for complete implementation:
- Canvas-based signature capture
- Touch and mouse support
- Real-time estimate display
- Signature validation
- Success/error handling

### FM Dashboard Components
Recommended components:
1. Statistics cards (jobs, estimates, financials)
2. Recent jobs table
3. Upcoming deadlines list
4. Quick action buttons
5. Status filter tabs

## Security Considerations

1. **Authentication**
   - FM endpoints require IsAdminOrFM permission
   - JWT token authentication

2. **Authorization**
   - FMs can only access their own jobs/estimates
   - Workspace-level access control

3. **Public Endpoints**
   - Estimate signing is public but validated
   - IP address tracking for audit
   - Estimate number required (not ID)

4. **Data Validation**
   - All inputs validated
   - File size limits on attachments
   - Signature data validation

## Best Practices

1. **Job Creation**
   - Always include customer details
   - Set realistic due dates
   - Add relevant attachments
   - Assign appropriate priority

2. **Estimate Creation**
   - Use clear line item descriptions
   - Set reasonable valid_until dates
   - Include all costs in line items
   - Add notes for clarification

3. **Signature Collection**
   - Send estimate link via email
   - Include estimate details in email
   - Set expiry dates
   - Follow up on unsigned estimates

## Testing

### Test FM Dashboard
```bash
curl -X GET "http://localhost:8000/api/workspaces/fm/dashboard/" \
  -H "Authorization: Bearer <fm_token>"
```

### Test Job Creation
```bash
curl -X POST http://localhost:8000/api/workspaces/fm/jobs/create/ \
  -H "Authorization: Bearer <fm_token>" \
  -H "Content-Type: application/json" \
  -d @job_data.json
```

### Test Estimate with Line Items
```bash
curl -X POST http://localhost:8000/api/workspaces/fm/estimates/create/ \
  -H "Authorization: Bearer <fm_token>" \
  -H "Content-Type: application/json" \
  -d @estimate_data.json
```

## Troubleshooting

**Issue: Totals not calculating**
- Call `/recalculate/` endpoint after adding line items

**Issue: Signature not saving**
- Ensure signature data is valid Base64
- Check estimate status (must be SENT or DRAFT)

**Issue: FM can't see jobs**
- Verify user role is FM or ADMIN
- Check workspace membership

## Future Enhancements

1. Email notifications for estimate signing
2. PDF generation for estimates
3. Bulk job creation
4. Template estimates
5. Mobile app for FM
6. Real-time notifications
7. Advanced reporting
8. Integration with payment gateways

## Support

For issues or questions:
- Check API_DOCUMENTATION.md
- Review IMPLEMENTATION_GUIDE.md
- Test with POSTMAN_COLLECTION.json
- Contact: support@yourapp.com
