# Contractor Module - Complete Guide

## Overview

Contractor module contractors ke liye design kiya gaya hai jo jobs accept karte hain, step-by-step checklists follow karte hain, photos/videos upload karte hain, aur jobs complete karke verification ke liye submit karte hain.

## Key Features

### 1. Contractor Dashboard
Real-time overview of contractor activities:
- Assignment statistics (pending, accepted, rejected)
- Active jobs count
- Completed jobs count
- Jobs pending verification
- Average ratings (quality, timeliness, professionalism)
- Unread notifications
- Recent assignments list

### 2. Job Assignment System
Complete assignment workflow:
- View all job assignments
- Accept jobs with one click
- Reject jobs with reason
- Assignment status tracking
- Automatic notifications to FM/Admin

### 3. Step-by-Step Checklist
Structured job execution:
- Predefined checklist for each job
- Numbered steps with descriptions
- Required vs optional steps
- Mark steps as complete
- Add notes to each step
- Progress tracking (completion percentage)

### 4. Media Upload System
Photo/video documentation:
- Upload photos for each step
- Upload videos for documentation
- Add captions to media
- Thumbnail support
- File size tracking
- Delete uploaded media

### 5. Job Completion Workflow
Professional completion process:
- Submit job for verification
- Add completion notes
- Record actual hours worked
- Automatic validation (all required steps completed)
- Notification to FM/Admin
- Track verification status

### 6. Verification & Rating
Quality assurance:
- FM/Admin reviews completion
- Approve/Reject/Request Revision
- Quality rating (1-5)
- Timeliness rating (1-5)
- Professionalism rating (1-5)
- Overall rating calculation
- Contractor profile rating update

### 7. Notification System
Real-time updates:
- Job assigned notifications
- Job accepted/rejected confirmations
- Step completion alerts
- Job verification results
- Revision requests
- Read/unread status
- Bulk mark as read

## Database Models

### JobAssignment
```python
- job (FK to Job)
- contractor (FK to Contractor)
- assigned_by (FK to User)
- status (PENDING, ACCEPTED, REJECTED, CANCELLED)
- assigned_at, responded_at
- rejection_reason
- notes
```

### JobChecklist
```python
- job (FK to Job)
- title, description
- order
- created_by (FK to User)
- completion_percentage (calculated property)
```

### ChecklistStep
```python
- checklist (FK to JobChecklist)
- step_number
- title, description
- is_required, is_completed
- completed_by (FK to User)
- completed_at
- notes
```

### StepMedia
```python
- step (FK to ChecklistStep)
- media_type (PHOTO, VIDEO, DOCUMENT)
- file_name, file_path, file_size
- thumbnail_path
- uploaded_by (FK to User)
- caption
```

### JobCompletion
```python
- job (OneToOne to Job)
- contractor (FK to Contractor)
- submitted_at
- status (SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED, REVISION_REQUIRED)
- completion_notes
- actual_hours_worked
- verified_by (FK to User)
- verified_at, verification_notes
- quality_rating, timeliness_rating, professionalism_rating
- overall_rating (calculated)
```

### JobNotification
```python
- recipient (FK to User)
- job (FK to Job)
- notification_type (JOB_ASSIGNED, JOB_ACCEPTED, etc.)
- title, message
- is_read, read_at
```

## API Endpoints

### Contractor Dashboard

#### Get Dashboard
```
GET /api/workspaces/contractor/dashboard/

Response:
{
  "contractor_info": {
    "company_name": "ABC Contractors",
    "specialization": "HVAC Systems",
    "rating": 4.75,
    "total_jobs_completed": 25
  },
  "assignment_statistics": {
    "total_assignments": 30,
    "pending_assignments": 2,
    "accepted_assignments": 25,
    "rejected_assignments": 3,
    "active_jobs": 5,
    "completed_jobs": 20,
    "pending_verification": 2
  },
  "ratings": {
    "average_quality": 4.8,
    "average_timeliness": 4.7,
    "average_professionalism": 4.9,
    "average_overall": 4.8
  },
  "unread_notifications": 3,
  "recent_assignments": [...]
}
```

### Job Assignments

#### List Assignments
```
GET /api/workspaces/contractor/assignments/
Query Parameters:
  - status: pending, accepted, rejected

Response:
[
  {
    "id": 1,
    "job": 1,
    "job_title": "HVAC System Repair",
    "job_number": "JOB-A1B2C3D4-00001",
    "contractor": 1,
    "contractor_email": "contractor@example.com",
    "assigned_by_email": "fm@example.com",
    "status": "PENDING",
    "assigned_at": "2025-12-05T10:00:00Z",
    "responded_at": null,
    "rejection_reason": null,
    "notes": "Contractor has relevant experience"
  }
]
```

#### Accept Job
```
POST /api/workspaces/contractor/assignments/{id}/accept/

Response:
{
  "message": "Job accepted successfully",
  "assignment": {...}
}
```

#### Reject Job
```
POST /api/workspaces/contractor/assignments/{id}/reject/

Request Body:
{
  "rejection_reason": "Schedule conflict - unavailable during requested timeframe"
}

Response:
{
  "message": "Job rejected successfully",
  "assignment": {...}
}
```

### Active Jobs

#### List Active Jobs
```
GET /api/workspaces/contractor/jobs/active/

Response:
[
  {
    "id": 1,
    "job_number": "JOB-A1B2C3D4-00001",
    "title": "HVAC System Repair",
    "description": "Complete HVAC system repair",
    "status": "IN_PROGRESS",
    "priority": "HIGH",
    "due_date": "2025-12-20",
    "location": "Building A, Floor 3",
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "customer_phone": "+1-555-0123",
    "assignment": {...},
    "checklists": [
      {
        "id": 1,
        "title": "HVAC Repair Checklist",
        "completion_percentage": 60.0,
        "total_steps": 5,
        "completed_steps": 3,
        "steps": [...]
      }
    ],
    "completion": null,
    "attachments": [...]
  }
]
```

#### Get Job Details
```
GET /api/workspaces/contractor/jobs/{id}/

Response: (Same as active jobs detail)
```

### Checklist Management

#### Update Step
```
PATCH /api/workspaces/contractor/steps/{id}/

Request Body:
{
  "is_completed": true,
  "notes": "Step completed successfully. All equipment tested."
}

Response:
{
  "message": "Step updated successfully",
  "step": {
    "id": 1,
    "checklist": 1,
    "step_number": 1,
    "title": "Initial System Inspection",
    "description": "Inspect HVAC system",
    "is_required": true,
    "is_completed": true,
    "completed_by": 2,
    "completed_by_email": "contractor@example.com",
    "completed_at": "2025-12-05T14:30:00Z",
    "notes": "Step completed successfully. All equipment tested.",
    "media": [...],
    "media_count": 2
  }
}
```

#### Upload Step Media
```
POST /api/workspaces/contractor/steps/media/

Request Body:
{
  "step": 1,
  "media_type": "PHOTO",
  "file_name": "before_work.jpg",
  "file_path": "/uploads/steps/before_work.jpg",
  "file_size": 1024576,
  "caption": "Before starting the repair work"
}

Response:
{
  "id": 1,
  "step": 1,
  "media_type": "PHOTO",
  "file_name": "before_work.jpg",
  "file_path": "/uploads/steps/before_work.jpg",
  "file_size": 1024576,
  "thumbnail_path": null,
  "uploaded_by": 2,
  "uploaded_by_email": "contractor@example.com",
  "caption": "Before starting the repair work",
  "created_at": "2025-12-05T14:35:00Z"
}
```

#### List Step Media
```
GET /api/workspaces/contractor/steps/{step_id}/media/

Response:
[
  {
    "id": 1,
    "media_type": "PHOTO",
    "file_name": "before_work.jpg",
    "file_path": "/uploads/steps/before_work.jpg",
    "caption": "Before starting the repair work",
    "created_at": "2025-12-05T14:35:00Z"
  },
  {
    "id": 2,
    "media_type": "PHOTO",
    "file_name": "after_work.jpg",
    "file_path": "/uploads/steps/after_work.jpg",
    "caption": "After completing the repair",
    "created_at": "2025-12-05T16:45:00Z"
  }
]
```

#### Delete Media
```
DELETE /api/workspaces/contractor/steps/media/{id}/

Response: 204 No Content
```

### Job Completion

#### Submit Completion
```
POST /api/workspaces/contractor/jobs/{id}/complete/

Request Body:
{
  "completion_notes": "Job completed successfully. All checklist items verified. Customer satisfied.",
  "actual_hours_worked": 7.5
}

Response:
{
  "message": "Job submitted for verification successfully",
  "completion": {
    "id": 1,
    "job": 1,
    "job_title": "HVAC System Repair",
    "job_number": "JOB-A1B2C3D4-00001",
    "contractor": 1,
    "contractor_email": "contractor@example.com",
    "submitted_at": "2025-12-05T17:00:00Z",
    "status": "SUBMITTED",
    "completion_notes": "Job completed successfully...",
    "actual_hours_worked": 7.5,
    "verified_by": null,
    "verified_at": null,
    "verification_notes": null,
    "quality_rating": null,
    "timeliness_rating": null,
    "professionalism_rating": null,
    "overall_rating": null
  }
}
```

#### List Completed Jobs
```
GET /api/workspaces/contractor/completed-jobs/

Response:
[
  {
    "id": 1,
    "job_title": "HVAC System Repair",
    "job_number": "JOB-A1B2C3D4-00001",
    "status": "APPROVED",
    "submitted_at": "2025-12-05T17:00:00Z",
    "verified_at": "2025-12-06T10:00:00Z",
    "quality_rating": 5,
    "timeliness_rating": 5,
    "professionalism_rating": 5,
    "overall_rating": 5.0
  }
]
```

### Notifications

#### List Notifications
```
GET /api/workspaces/contractor/notifications/
Query Parameters:
  - is_read: true/false

Response:
[
  {
    "id": 1,
    "recipient_email": "contractor@example.com",
    "job": 1,
    "job_number": "JOB-A1B2C3D4-00001",
    "notification_type": "JOB_ASSIGNED",
    "title": "New Job Assignment: JOB-A1B2C3D4-00001",
    "message": "You have been assigned a new job: HVAC System Repair",
    "is_read": false,
    "read_at": null,
    "created_at": "2025-12-05T10:00:00Z"
  }
]
```

#### Mark as Read
```
POST /api/workspaces/contractor/notifications/{id}/read/

Response:
{
  "message": "Notification marked as read",
  "notification": {...}
}
```

#### Mark All as Read
```
POST /api/workspaces/contractor/notifications/read-all/

Response:
{
  "message": "All notifications marked as read"
}
```

### Admin/FM Endpoints

#### Assign Job to Contractor
```
POST /api/workspaces/admin/assign-job/

Request Body:
{
  "job_id": 1,
  "contractor_id": 2,
  "notes": "Contractor has relevant experience with HVAC systems"
}

Response:
{
  "message": "Job assigned successfully",
  "assignment": {...}
}
```

#### Verify Job Completion
```
POST /api/workspaces/admin/verify-completion/{id}/

Request Body:
{
  "action": "approve",  // or "reject", "request_revision"
  "verification_notes": "Excellent work. All requirements met.",
  "quality_rating": 5,
  "timeliness_rating": 5,
  "professionalism_rating": 5
}

Response:
{
  "message": "Job completion approved successfully",
  "completion": {...}
}
```

#### Create Job Checklist
```
POST /api/workspaces/admin/checklists/create/

Request Body:
{
  "job": 1,
  "title": "HVAC System Repair Checklist",
  "description": "Standard checklist for HVAC repairs",
  "order": 1
}

Response:
{
  "id": 1,
  "job": 1,
  "title": "HVAC System Repair Checklist",
  "completion_percentage": 0.0,
  "total_steps": 0,
  "completed_steps": 0,
  "steps": []
}
```

#### Create Checklist Step
```
POST /api/workspaces/admin/checklist-steps/create/

Request Body:
{
  "checklist": 1,
  "step_number": 1,
  "title": "Initial System Inspection",
  "description": "Inspect HVAC system and identify issues",
  "is_required": true
}

Response:
{
  "id": 1,
  "checklist": 1,
  "step_number": 1,
  "title": "Initial System Inspection",
  "description": "Inspect HVAC system and identify issues",
  "is_required": true,
  "is_completed": false,
  "media_count": 0
}
```

## Complete Workflow Example

### 1. FM Creates Job and Checklist
```bash
# Create job
POST /api/workspaces/fm/jobs/create/
{
  "workspace_id": "uuid",
  "title": "HVAC System Repair",
  ...
}

# Create checklist
POST /api/workspaces/admin/checklists/create/
{
  "job": 1,
  "title": "HVAC Repair Checklist"
}

# Add steps
POST /api/workspaces/admin/checklist-steps/create/
{
  "checklist": 1,
  "step_number": 1,
  "title": "Initial Inspection",
  "is_required": true
}
```

### 2. FM Assigns Job to Contractor
```bash
POST /api/workspaces/admin/assign-job/
{
  "job_id": 1,
  "contractor_id": 2
}
```

### 3. Contractor Receives Notification
```bash
GET /api/workspaces/contractor/notifications/
# Contractor sees "JOB_ASSIGNED" notification
```

### 4. Contractor Accepts Job
```bash
POST /api/workspaces/contractor/assignments/1/accept/
```

### 5. Contractor Works on Job
```bash
# View job details
GET /api/workspaces/contractor/jobs/1/

# Complete step 1
PATCH /api/workspaces/contractor/steps/1/
{
  "is_completed": true,
  "notes": "Inspection complete"
}

# Upload photo
POST /api/workspaces/contractor/steps/media/
{
  "step": 1,
  "media_type": "PHOTO",
  "file_name": "inspection.jpg",
  ...
}

# Complete remaining steps...
```

### 6. Contractor Submits Completion
```bash
POST /api/workspaces/contractor/jobs/1/complete/
{
  "completion_notes": "All work completed",
  "actual_hours_worked": 7.5
}
```

### 7. FM Receives Notification
```bash
# FM sees "JOB_COMPLETED" notification
```

### 8. FM Verifies and Rates
```bash
POST /api/workspaces/admin/verify-completion/1/
{
  "action": "approve",
  "verification_notes": "Excellent work",
  "quality_rating": 5,
  "timeliness_rating": 5,
  "professionalism_rating": 5
}
```

### 9. Contractor Receives Verification
```bash
# Contractor sees "JOB_VERIFIED" notification
# Contractor rating updated
```

## Frontend Integration

### Contractor Dashboard Components
1. Statistics cards (assignments, active jobs, ratings)
2. Recent assignments list
3. Notifications panel
4. Quick actions (accept/reject)

### Job Detail Page
1. Job information card
2. Customer details
3. Checklist with progress bar
4. Step list with completion status
5. Media gallery for each step
6. Complete job button

### Checklist Step Component
1. Step number and title
2. Description
3. Completion checkbox
4. Notes textarea
5. Media upload button
6. Media gallery
7. Mark complete button

### Notification Center
1. Notification list
2. Read/unread indicators
3. Mark as read buttons
4. Filter by type
5. Real-time updates

## Best Practices

### For Contractors
1. **Accept jobs promptly** - Review and respond quickly
2. **Follow checklist order** - Complete steps sequentially
3. **Upload quality photos** - Clear, well-lit images
4. **Add detailed notes** - Document work thoroughly
5. **Complete all required steps** - Before submitting
6. **Accurate time tracking** - Record actual hours

### For FM/Admin
1. **Create detailed checklists** - Clear step descriptions
2. **Mark critical steps as required** - Ensure quality
3. **Assign appropriate contractors** - Match skills
4. **Timely verification** - Review completions quickly
5. **Fair ratings** - Provide constructive feedback
6. **Handle revisions professionally** - Clear instructions

## Troubleshooting

**Issue: Cannot submit job completion**
- Ensure all required checklist steps are completed
- Check if job status is IN_PROGRESS

**Issue: Cannot upload media**
- Verify file size limits
- Check file type is supported
- Ensure step exists and contractor has access

**Issue: Notifications not appearing**
- Check notification permissions
- Verify user is recipient
- Refresh notification list

## Future Enhancements

1. Real-time notifications (WebSocket)
2. Offline mode for mobile app
3. Voice notes for steps
4. GPS location tracking
5. Time tracking per step
6. Contractor chat with FM
7. Push notifications
8. Barcode/QR code scanning
9. Equipment tracking
10. Automated reminders

## Support

For issues or questions:
- Check API_DOCUMENTATION.md
- Review IMPLEMENTATION_GUIDE.md
- Test with POSTMAN_COLLECTION.json
- Contact: support@yourapp.com
