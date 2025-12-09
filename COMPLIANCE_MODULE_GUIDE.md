# Compliance & Disputes System Module Guide

## Overview
Complete compliance tracking aur dispute management system with escalation flow.

---

## 🔐 Contractor Compliance Hub

### 1. View Compliance Documents
**Endpoint:** `GET /api/workspace/contractor/compliance/`
**Permission:** Authenticated Contractor

**Response:**
```json
[
  {
    "id": 1,
    "compliance_type": "ID",
    "document_name": "Driver License",
    "document_number": "DL123456",
    "status": "APPROVED",
    "issue_date": "2023-01-01",
    "expiry_date": "2028-01-01",
    "file_path": "/media/compliance/dl.pdf",
    "file_size": 245678,
    "is_expiring_soon": false,
    "is_expired": false,
    "verified_by_email": "admin@example.com",
    "verified_at": "2024-01-15T10:30:00Z"
  }
]
```

### 2. Upload Compliance Document
**Endpoint:** `POST /api/workspace/contractor/compliance/upload/`
**Permission:** Authenticated Contractor

**Request:**
```json
{
  "workspace_id": "uuid-here",
  "compliance_type": "INSURANCE",
  "document_name": "General Liability Insurance",
  "document_number": "INS-789456",
  "issue_date": "2024-01-01",
  "expiry_date": "2025-01-01",
  "file_path": "/media/compliance/insurance.pdf",
  "file_size": 512000,
  "notes": "Updated insurance policy"
}
```

**Compliance Types:**
- `ID` - ID Document
- `LICENSE` - License
- `INSURANCE` - Insurance
- `CERTIFICATION` - Certification
- `CONTRACT` - Contract
- `SAFETY` - Safety Training
- `OTHER` - Other

### 3. Compliance Statistics
**Endpoint:** `GET /api/workspace/contractor/compliance/stats/`
**Permission:** Authenticated Contractor

**Response:**
```json
{
  "total_documents": 8,
  "pending_verification": 2,
  "approved": 5,
  "rejected": 1,
  "expiring_soon": 1,
  "expired": 0
}
```

---

## 👨‍💼 Admin Compliance Center

### 1. View All Compliance Documents
**Endpoint:** `GET /api/workspace/admin/compliance/`
**Permission:** Admin Only

**Query Parameters:**
- `status` - Filter by status (PENDING, APPROVED, REJECTED, EXPIRED)
- `contractor_id` - Filter by contractor
- `compliance_type` - Filter by type

**Response:**
```json
[
  {
    "id": 1,
    "contractor_email": "contractor@example.com",
    "contractor_company": "ABC Construction",
    "compliance_type": "LICENSE",
    "document_name": "Contractor License",
    "status": "PENDING",
    "expiry_date": "2025-12-31",
    "is_expiring_soon": false,
    "is_expired": false,
    "created_at": "2024-01-10T09:00:00Z"
  }
]
```

### 2. Approve Compliance Document
**Endpoint:** `POST /api/workspace/admin/compliance/{compliance_id}/approve/`
**Permission:** Admin Only

**Response:**
```json
{
  "message": "Compliance document approved successfully",
  "compliance": {
    "id": 1,
    "status": "APPROVED",
    "verified_by_email": "admin@example.com",
    "verified_at": "2024-01-15T10:30:00Z"
  }
}
```

### 3. Reject Compliance Document
**Endpoint:** `POST /api/workspace/admin/compliance/{compliance_id}/reject/`
**Permission:** Admin Only

**Request:**
```json
{
  "rejection_reason": "Document is expired. Please upload current document."
}
```

**Response:**
```json
{
  "message": "Compliance document rejected",
  "compliance": {
    "id": 1,
    "status": "REJECTED",
    "rejection_reason": "Document is expired. Please upload current document.",
    "verified_by_email": "admin@example.com"
  }
}
```

### 4. Admin Compliance Statistics
**Endpoint:** `GET /api/workspace/admin/compliance/stats/`
**Permission:** Admin Only

**Response:**
```json
{
  "total_documents": 45,
  "pending_verification": 8,
  "approved": 32,
  "rejected": 5,
  "expiring_soon": 6,
  "expired": 2,
  "by_type": {
    "ID Document": 10,
    "License": 8,
    "Insurance": 12,
    "Certification": 7,
    "Contract": 5,
    "Safety Training": 3
  }
}
```

---

## ⚖️ Dispute Center

### Escalation Flow
```
Customer → FM → Admin
```

### 1. Create Dispute
**Endpoint:** `POST /api/workspace/disputes/create/`
**Permission:** Authenticated

**Request:**
```json
{
  "job_id": 123,
  "category": "QUALITY",
  "title": "Poor workmanship on bathroom tiles",
  "description": "The tiles are not aligned properly and there are visible gaps."
}
```

**Dispute Categories:**
- `QUALITY` - Quality Issue
- `PAYMENT` - Payment Issue
- `TIMELINE` - Timeline Issue
- `COMMUNICATION` - Communication Issue
- `SAFETY` - Safety Concern
- `OTHER` - Other

**Response:**
```json
{
  "id": 1,
  "dispute_number": "DISP-000001",
  "job_number": "JOB-000123",
  "job_title": "Bathroom Renovation",
  "raised_by_email": "customer@example.com",
  "contractor_email": "contractor@example.com",
  "category": "QUALITY",
  "title": "Poor workmanship on bathroom tiles",
  "status": "OPEN",
  "created_at": "2024-01-15T14:30:00Z"
}
```

### 2. List Disputes
**Endpoint:** `GET /api/workspace/disputes/`
**Permission:** Authenticated

**Query Parameters:**
- `status` - Filter by status

**Access Control:**
- Admin: Sees all disputes
- FM: Sees escalated disputes (ESCALATED_TO_FM, ESCALATED_TO_ADMIN)
- Contractor: Sees their disputes
- Customer: Sees disputes they raised

**Response:**
```json
[
  {
    "id": 1,
    "dispute_number": "DISP-000001",
    "job_number": "JOB-000123",
    "status": "ESCALATED_TO_FM",
    "category": "QUALITY",
    "title": "Poor workmanship",
    "message_count": 5,
    "created_at": "2024-01-15T14:30:00Z"
  }
]
```

### 3. View Dispute Details
**Endpoint:** `GET /api/workspace/disputes/{dispute_id}/`
**Permission:** Authenticated

**Response:**
```json
{
  "id": 1,
  "dispute_number": "DISP-000001",
  "job_number": "JOB-000123",
  "job_title": "Bathroom Renovation",
  "raised_by_email": "customer@example.com",
  "contractor_email": "contractor@example.com",
  "category": "QUALITY",
  "title": "Poor workmanship",
  "description": "Detailed description...",
  "status": "ESCALATED_TO_FM",
  "messages": [...],
  "attachments": [...],
  "created_at": "2024-01-15T14:30:00Z"
}
```

### 4. Escalate to FM
**Endpoint:** `POST /api/workspace/disputes/{dispute_id}/escalate-to-fm/`
**Permission:** Authenticated

**Response:**
```json
{
  "message": "Dispute escalated to FM successfully",
  "dispute": {
    "id": 1,
    "status": "ESCALATED_TO_FM"
  }
}
```

### 5. Escalate to Admin
**Endpoint:** `POST /api/workspace/disputes/{dispute_id}/escalate-to-admin/`
**Permission:** Admin or FM

**Response:**
```json
{
  "message": "Dispute escalated to Admin successfully",
  "dispute": {
    "id": 1,
    "status": "ESCALATED_TO_ADMIN"
  }
}
```

### 6. Resolve Dispute (Admin Only)
**Endpoint:** `POST /api/workspace/disputes/{dispute_id}/resolve/`
**Permission:** Admin Only

**Request:**
```json
{
  "resolution_notes": "Contractor agreed to redo the tiles. Work will be completed by next week."
}
```

**Response:**
```json
{
  "message": "Dispute resolved successfully",
  "dispute": {
    "id": 1,
    "status": "RESOLVED",
    "resolved_by_email": "admin@example.com",
    "resolved_at": "2024-01-20T16:00:00Z",
    "resolution_notes": "Contractor agreed to redo the tiles..."
  }
}
```

### 7. Add Message to Dispute
**Endpoint:** `POST /api/workspace/disputes/messages/`
**Permission:** Authenticated

**Request:**
```json
{
  "dispute": 1,
  "message": "I have reviewed the photos and will fix the issue tomorrow.",
  "is_internal": false
}
```

**Note:** `is_internal=true` messages are only visible to Admin/FM

### 8. View Dispute Messages
**Endpoint:** `GET /api/workspace/disputes/{dispute_id}/messages/`
**Permission:** Authenticated

**Response:**
```json
[
  {
    "id": 1,
    "sender_email": "contractor@example.com",
    "sender_name": "John Contractor",
    "message": "I will fix this issue.",
    "is_internal": false,
    "created_at": "2024-01-15T15:00:00Z"
  }
]
```

### 9. Add Attachment to Dispute
**Endpoint:** `POST /api/workspace/disputes/attachments/`
**Permission:** Authenticated

**Request:**
```json
{
  "dispute": 1,
  "file_name": "evidence.jpg",
  "file_path": "/media/disputes/evidence.jpg",
  "file_type": "image/jpeg",
  "file_size": 245678,
  "description": "Photo showing the issue"
}
```

### 10. View Dispute Attachments
**Endpoint:** `GET /api/workspace/disputes/{dispute_id}/attachments/`
**Permission:** Authenticated

### 11. Dispute Statistics (Admin)
**Endpoint:** `GET /api/workspace/admin/disputes/stats/`
**Permission:** Admin Only

**Response:**
```json
{
  "total_disputes": 25,
  "open": 5,
  "escalated_to_fm": 8,
  "escalated_to_admin": 4,
  "resolved": 7,
  "closed": 1,
  "by_category": {
    "Quality Issue": 10,
    "Payment Issue": 5,
    "Timeline Issue": 6,
    "Communication Issue": 3,
    "Safety Concern": 1
  }
}
```

---

## 📊 Compliance Status Tracking

### Document Status Flow
```
PENDING → APPROVED/REJECTED
APPROVED → EXPIRING_SOON → EXPIRED
```

### Auto-Status Updates
- Documents automatically marked as `EXPIRING_SOON` when 30 days or less until expiry
- Documents automatically marked as `EXPIRED` when past expiry date
- Run management command: `python manage.py update_compliance_status`

---

## 🔔 Notifications

### Compliance Notifications
- Document approved → Contractor notified
- Document rejected → Contractor notified with reason
- Document expiring soon → Contractor notified

### Dispute Notifications
- Dispute escalated to FM → FM notified
- Dispute resolved → All parties notified

---

## 🎯 Best Practices

### For Contractors
1. Upload all required documents before starting work
2. Keep documents up to date
3. Respond to rejection reasons promptly
4. Monitor expiry dates

### For Admins
1. Review compliance documents within 24-48 hours
2. Provide clear rejection reasons
3. Monitor expiring documents
4. Resolve disputes fairly and promptly

### For Dispute Management
1. Try to resolve at customer-contractor level first
2. Escalate to FM if no resolution
3. Admin makes final decision
4. Document all communications
5. Attach evidence (photos, documents)

---

## 🔒 Security & Permissions

### Contractor Compliance Hub
- Contractors can only view/upload their own documents
- Cannot approve/reject documents

### Admin Compliance Center
- Full access to all compliance documents
- Can approve/reject any document
- View comprehensive statistics

### Dispute Center
- Customers see disputes they raised
- Contractors see their disputes
- FM sees escalated disputes
- Admin sees all disputes
- Internal messages hidden from non-admin/FM users

---

## 📝 Notes

- All file uploads should be handled separately (use file upload endpoints)
- Store file paths in database after successful upload
- Implement file size limits (recommended: 10MB max)
- Support common formats: PDF, JPG, PNG, DOC, DOCX
- Auto-generate dispute numbers: DISP-XXXXXX
- Track all status changes with timestamps
- Send email notifications for important events
