# Django Job Management System

A comprehensive job management system built with Django REST Framework, featuring modern security features and flexible user management.

## Features

### Core Authentication
- **Email-based Registration & Login** - Password-based authentication
- **Magic Link Authentication** - Passwordless login via email
- **JWT Token Management** - Secure access and refresh tokens
- **Email Verification** - Account verification through email
- **Password Reset** - Secure password recovery system

### Security Features
- **Account Lockout** - Automatic lock after 5 failed attempts (30 minutes)
- **Session Management** - Track and manage multiple device sessions
- **Login History** - Detailed audit trail of all login attempts
- **IP Tracking** - IP logging for login attempts and sessions
- **Token Expiry** - Configurable token lifetimes
- **Secure Password Validation** - Django's built-in validators

### User Management
- **Role-Based Access Control (RBAC)** - 5 user roles:
  - Admin
  - Facility Manager (FM)
  - Contractor
  - Customer
  - Investor
- **Profile Management** - User profile updates
- **User Statistics** - Analytics for admin dashboard
- **Soft Delete** - Deactivate users instead of permanent deletion

### Management Commands
- `cleanup_tokens` - Delete expired tokens
- `create_roles` - Setup default roles
- `unlock_accounts` - Unlock locked accounts

## Tech Stack

- **Django** 4.2+
- **Django REST Framework** 3.14+
- **Simple JWT** 5.3+ - JWT authentication
- **Django CORS Headers** - Cross-origin support
- **Celery** - Async task processing
- **Redis** - Caching and session storage
- **Cryptography** - Secure token generation
- **ReportLab** - PDF generation
- **Pillow** - Image processing

## Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd <project-directory>
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourapp.com

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

Server will run at `http://127.0.0.1:8000/`.

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | New user registration | No |
| POST | `/api/auth/login/` | Email/password login | No |
| POST | `/api/auth/logout/` | Logout current session | Yes |
| POST | `/api/auth/logout-all/` | Logout from all devices | Yes |
| POST | `/api/auth/token/refresh/` | Refresh access token | No |

### Magic Link

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/magic-link/request/` | Request magic link | No |
| POST | `/api/auth/magic-link/verify/` | Verify magic link | No |

### Email Verification

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/verify-email/` | Verify email address | No |
| POST | `/api/auth/resend-verification/` | Resend verification email | Yes |

### Password Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/password-reset/request/` | Request password reset | No |
| POST | `/api/auth/password-reset/confirm/` | Confirm password reset | No |
| POST | `/api/auth/change-password/` | Change password | Yes |

### User Profile

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/auth/me/` | Get current user | Yes |
| PATCH | `/api/auth/profile/` | Update profile | Yes |

### Session Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/auth/sessions/` | List active sessions | Yes |
| POST | `/api/auth/sessions/<id>/revoke/` | Revoke specific session | Yes |
| GET | `/api/auth/login-history/` | View login history | Yes |

### User Management (Admin Only)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/auth/users/` | List all users | Admin |
| GET | `/api/auth/users/<id>/` | Get user details | Admin/FM |
| PATCH | `/api/auth/users/<id>/` | Update user | Admin/FM |
| DELETE | `/api/auth/users/<id>/` | Deactivate user | Admin/FM |
| GET | `/api/auth/stats/` | User statistics | Admin |

## Management Commands

### Authentication Commands

#### Cleanup Expired Tokens
```bash
python manage.py cleanup_tokens
```

#### Create Default Roles
```bash
python manage.py create_roles
```

#### Unlock Locked Accounts
```bash
python manage.py unlock_accounts
```

### Workspace Commands

#### Update Compliance Status
Automatically update compliance document status based on expiry dates:
```bash
python manage.py update_compliance_status
```

#### Generate Workspace Report
Generate comprehensive CSV reports for a workspace:
```bash
python manage.py generate_workspace_report <workspace_id>

# With custom output directory
python manage.py generate_workspace_report <workspace_id> --output-dir=exports/
```

This command generates:
- Jobs report
- Estimates report
- Contractors report
- Payouts report
- Compliance report

### Cron Automation Commands

#### Daily Compliance Expiry Check
```bash
python manage.py check_compliance_expiry
```

#### Send Pending Jobs Reminder
```bash
python manage.py send_pending_jobs_reminder
```

#### Send Daily Summary
```bash
python manage.py send_daily_summary
```

#### Send Payout Reminders
```bash
python manage.py send_payout_reminders
```

#### Auto Close Stale Jobs
```bash
# Dry run (test without closing)
python manage.py auto_close_stale_jobs --dry-run

# Actual run (close jobs inactive for 90+ days)
python manage.py auto_close_stale_jobs --days=90
```

## Project Modules

### 1. Authentication Module
- User registration and login
- JWT token management
- Email verification
- Password reset
- Magic link authentication
- Role-based access control
- Session management
- Login history tracking

### 2. Workspace & Data Structure
- Unique workspace ID generation
- Job tracking
- Estimates with line items
- Contractors management
- Payouts tracking
- Reports generation
- Compliance data
- CSV export functionality

### 3. Field Manager (FM) Module
- FM dashboard with real-time stats
- Job creation with customer details
- Job attachments
- Estimate creation with line items
- Digital signature collection
- Public signing links
- Automatic calculations
- Status-based filtering

### 4. Contractor Module
- Contractor dashboard
- Job assignment acceptance/rejection
- Step-by-step checklist system
- Photo/video upload for steps
- Progress tracking
- Job completion submission
- Admin/FM verification
- Rating system
- Real-time notifications

### 5. Admin Payout & Financial Flow
- Ready for payout jobs view
- Single and bulk payout approval
- Contractor wallet system
- Balance tracking
- Transaction ledger
- Payout request system
- Admin approval/rejection workflow
- Downloadable CSV reports

### 6. Compliance & Disputes System
- Contractor compliance hub
- Document upload
- Expiry tracking
- Admin compliance center
- Document verification
- Dispute management
- Escalation flow
- Resolution tracking

### 7. Investor Module
- Investor dashboard
- Revenue statistics
- ROI analytics
- Job volume breakdown
- Payout analytics
- Monthly breakdown
- Performance comparison
- Downloadable reports

### 8. AI-Assisted Features
- AI job description generator
- AI checklist suggestions
- Pricing anomaly detection
- Missing items detection
- Smart recommendations
- Contractor matching
- At-risk job identification

### 9. PDF Generation
- Professional estimate PDFs
- Job report PDFs
- Payout slip PDFs
- Compliance certificate PDFs
- Investor report PDFs
- Automatic generation
- Professional formatting

### 10. Cron Automation System
- Daily compliance checks
- Pending jobs reminders
- Daily summary emails
- Payout reminders
- Auto close stale jobs
- Automated notifications

## Documentation Files

- **README.md** - Project overview and setup
- **API_DOCUMENTATION.md** - Complete API reference
- **IMPLEMENTATION_GUIDE.md** - Implementation details
- **FM_MODULE_GUIDE.md** - Field Manager guide
- **CONTRACTOR_MODULE_GUIDE.md** - Contractor guide
- **PAYOUT_MODULE_GUIDE.md** - Payout system guide
- **COMPLIANCE_MODULE_GUIDE.md** - Compliance guide
- **INVESTOR_MODULE_GUIDE.md** - Investor guide
- **AI_MODULE_GUIDE.md** - AI features guide
- **PDF_MODULE_GUIDE.md** - PDF generation guide
- **CRON_AUTOMATION_GUIDE.md** - Automation guide
- **DEPLOYMENT_SUMMARY.md** - Deployment checklist
- **PROJECT_SUMMARY.md** - Complete summary
- **TESTING_REPORT.md** - Testing results
- **QUICK_STATUS_REPORT.md** - Quick status
- **POSTMAN_COLLECTION.json** - API testing
- **crontab_config.txt** - Cron configuration
- **.env.example** - Environment template

## Security Best Practices

1. **Environment Variables** - Store sensitive data in `.env` file
2. **HTTPS** - Always use HTTPS in production
3. **Strong Passwords** - Password validation enabled
4. **Token Rotation** - Refresh tokens automatically rotate
5. **Account Lockout** - Protection against brute force attacks
6. **CORS Configuration** - Allow specific origins in production
7. **Rate Limiting** - Implement rate limiting on API endpoints

## Configuration

### JWT Settings
Customize in `config/settings.py`:
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

### Email Settings
Configure SMTP for production:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## Testing

Run tests:
```bash
python manage.py test authentication
python manage.py test workspace
```

## Deployment

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Setup database (PostgreSQL recommended)
- [ ] Configure Redis
- [ ] Setup email service
- [ ] Enable HTTPS
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser
- [ ] Setup cron jobs
- [ ] Configure monitoring

### Environment Variables
Set these in production:
- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- `DATABASE_URL`
- `REDIS_URL`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `FRONTEND_URL`

## Troubleshooting

### Common Issues

**Email not sending**
- Check email backend configuration
- Verify SMTP credentials
- Check firewall/port settings

**Token expired errors**
- Check token lifetime settings
- Verify system time sync

**Account locked**
- Run `unlock_accounts` command
- Or manually unlock via admin panel

## Testing with Postman

Postman collection file included for testing:
1. Import `POSTMAN_COLLECTION.json` into Postman
2. Set `base_url` variable to `http://localhost:8000/api`
3. Register/Login to get access token (automatically saved)
4. Test all endpoints with pre-configured requests

Collection includes:
- Authentication flows
- Workspace management
- All CRUD operations
- CSV export endpoints
- Automatic token management

## Support

For issues or questions:
- Create GitHub Issues
- Check documentation
- Email: support@yourapp.com

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## License

This project is licensed under the MIT License.

## Project Status

**Status:** ✅ Production Ready
**Version:** 1.0.0
**Modules:** 10/10 Complete
**API Endpoints:** 135+
**Documentation:** Complete
**Testing:** Passed

---

**Last Updated:** December 6, 2024
**Developed with:** Django REST Framework
**Database:** SQLite (Development) / PostgreSQL (Production)
