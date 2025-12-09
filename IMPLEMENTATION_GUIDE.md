# Implementation Guide

## Overview

Yeh Django-based authentication aur workspace management system hai jo facility management, contractor management, aur compliance tracking ke liye design kiya gaya hai.

## Modules

### 1. Authentication Module (`authentication/`)

**Features:**
- Email-based registration aur login
- Magic link (passwordless) authentication
- JWT token management
- Email verification
- Password reset functionality
- Role-based access control (RBAC)
- Account lockout after failed attempts
- Session management
- Login history tracking

**Models:**
- `User` - Custom user model with roles
- `VerificationToken` - Email verification aur password reset tokens
- `RefreshTokenSession` - Active session tracking
- `LoginHistory` - Login attempt audit trail

**Roles:**
- ADMIN - Full system access
- FM (Facility Manager) - Facility management access
- CONTRACTOR - Contractor-specific access
- CUSTOMER - Customer access
- INVESTOR - Investor access

### 2. Workspace Module (`workspace/`)

**Features:**
- Unique workspace creation with UUID
- Multi-user workspace collaboration
- Job tracking aur management
- Estimate creation aur approval
- Contractor management
- Payout processing
- Compliance document tracking
- CSV export for all entities

**Models:**
- `Workspace` - Main workspace container
- `WorkspaceMember` - Workspace membership with roles
- `Job` - Job tracking with status workflow
- `Estimate` - Financial estimates
- `Contractor` - Contractor profiles
- `Payout` - Payment tracking
- `Report` - Generated reports
- `ComplianceData` - Compliance document tracking

## Database Schema

### Key Relationships

```
User (1) ----< (N) Workspace (owner)
User (N) ----< (N) WorkspaceMember >---- (1) Workspace
Workspace (1) ----< (N) Job
Workspace (1) ----< (N) Estimate
Workspace (1) ----< (N) Contractor
Workspace (1) ----< (N) Payout
Workspace (1) ----< (N) ComplianceData
Job (1) ----< (N) Estimate
Job (1) ----< (N) Payout
Contractor (1) ----< (N) Payout
Contractor (1) ----< (N) ComplianceData
```

## Setup Instructions

### 1. Initial Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env  # Edit with your settings
```

### 2. Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 3. Initial Data

```bash
# Create default roles (optional)
python manage.py create_roles
```

### 4. Run Server

```bash
python manage.py runserver
```

## API Workflow Examples

### Complete User Registration Flow

1. **Register User**
```bash
POST /api/auth/register/
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "username": "johndoe",
  "role": "FM"
}
```

2. **Verify Email**
```bash
POST /api/auth/verify-email/
{
  "token": "verification_token_from_email"
}
```

3. **Login**
```bash
POST /api/auth/login/
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

### Complete Workspace Workflow

1. **Create Workspace**
```bash
POST /api/workspaces/
{
  "name": "Downtown Facility",
  "workspace_type": "FACILITY",
  "description": "Main facility management"
}
```

2. **Add Contractor**
```bash
POST /api/workspaces/{workspace_id}/contractors/
{
  "user": 3,
  "company_name": "ABC Contractors",
  "license_number": "LIC-12345",
  "hourly_rate": 75.00
}
```

3. **Create Job**
```bash
POST /api/workspaces/{workspace_id}/jobs/
{
  "title": "HVAC Maintenance",
  "description": "Quarterly maintenance",
  "priority": "HIGH",
  "assigned_to": 3,
  "due_date": "2025-12-15"
}
```

4. **Create Estimate**
```bash
POST /api/workspaces/{workspace_id}/estimates/
{
  "job": 1,
  "title": "HVAC Maintenance Estimate",
  "total_amount": 1000.00
}
```

5. **Create Payout**
```bash
POST /api/workspaces/{workspace_id}/payouts/
{
  "contractor": 1,
  "job": 1,
  "amount": 600.00,
  "payment_method": "BANK_TRANSFER"
}
```

6. **Export Data**
```bash
GET /api/workspaces/{workspace_id}/jobs/export/
GET /api/workspaces/{workspace_id}/payouts/export/
```

## CSV Export Structure

### Jobs CSV
```
Job Number, Title, Status, Priority, Assigned To, Estimated Hours, Actual Hours, Start Date, Due Date, Completed Date, Location, Created At, Updated At
```

### Estimates CSV
```
Estimate Number, Title, Job Number, Status, Subtotal, Tax Amount, Discount Amount, Total Amount, Valid Until, Created By, Approved By, Approved At, Created At
```

### Contractors CSV
```
Email, Company Name, License Number, Specialization, Hourly Rate, Status, Rating, Total Jobs Completed, Phone, Address, Created At
```

### Payouts CSV
```
Payout Number, Contractor Email, Company Name, Job Number, Amount, Status, Payment Method, Scheduled Date, Paid Date, Processed By, Transaction Reference, Created At
```

### Compliance CSV
```
Contractor Email, Company Name, Compliance Type, Document Name, Document Number, Status, Issue Date, Expiry Date, Verified By, Verified At, Created At
```

## Security Considerations

### 1. Authentication Security
- JWT tokens with configurable expiry
- Refresh token rotation
- Account lockout after 5 failed attempts
- Password validation (length, complexity)
- Email verification required

### 2. Authorization
- Role-based access control
- Workspace-level permissions
- Owner/member checks on all operations

### 3. Data Protection
- HTTPS in production (configure in settings)
- CSRF protection enabled
- XSS protection headers
- Secure cookie settings

### 4. API Security
- Authentication required for all workspace operations
- Input validation on all endpoints
- SQL injection protection (Django ORM)

## Performance Optimization

### 1. Database Indexes
- Workspace ID indexed
- Job number indexed
- Email fields indexed
- Foreign keys indexed

### 2. Query Optimization
- Use `select_related()` for foreign keys
- Use `prefetch_related()` for reverse relations
- Pagination on list endpoints

### 3. Caching (Optional)
```python
# In settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

## Monitoring & Maintenance

### Regular Tasks

1. **Daily**
```bash
# Update compliance status
python manage.py update_compliance_status
```

2. **Weekly**
```bash
# Cleanup expired tokens
python manage.py cleanup_tokens

# Generate workspace reports
python manage.py generate_workspace_report <workspace_id>
```

3. **Monthly**
```bash
# Unlock accounts (if needed)
python manage.py unlock_accounts

# Database backup
python manage.py dumpdata > backup.json
```

## Testing

### Run Tests
```bash
# All tests
python manage.py test

# Specific app
python manage.py test authentication
python manage.py test workspace

# With coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## Deployment Checklist

### Pre-Deployment
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set strong `SECRET_KEY`
- [ ] Configure production database (PostgreSQL)
- [ ] Setup Redis for caching
- [ ] Configure email service (SMTP)
- [ ] Setup static files serving
- [ ] Configure HTTPS/SSL
- [ ] Setup backup strategy

### Post-Deployment
- [ ] Run migrations
- [ ] Collect static files
- [ ] Create superuser
- [ ] Test all endpoints
- [ ] Monitor logs
- [ ] Setup monitoring (Sentry, etc.)

## Troubleshooting

### Common Issues

**Issue: Migrations not applying**
```bash
python manage.py migrate --fake-initial
```

**Issue: Static files not loading**
```bash
python manage.py collectstatic --clear
```

**Issue: Token expired errors**
- Check system time synchronization
- Verify JWT settings in `settings.py`

**Issue: Email not sending**
- Verify SMTP credentials
- Check firewall/port settings
- Test with console backend first

## Future Enhancements

### Planned Features
1. Real-time notifications (WebSocket)
2. File upload for compliance documents
3. Advanced reporting with charts
4. Mobile app API optimization
5. Bulk operations for jobs/estimates
6. Automated compliance reminders
7. Integration with payment gateways
8. Advanced search and filtering
9. Activity timeline for workspaces
10. API rate limiting

## Support & Documentation

- **README.md** - Project overview aur setup
- **API_DOCUMENTATION.md** - Complete API reference
- **IMPLEMENTATION_GUIDE.md** - This file
- Django Admin - `/admin/` for data management
- API Browsable Interface - DRF browsable API

## Contributing

1. Create feature branch
2. Write tests for new features
3. Update documentation
4. Submit pull request
5. Code review process

## License

MIT License - See LICENSE file for details
