# Django Authentication System

Ek comprehensive authentication system Django REST Framework ke saath, jo modern security features aur flexible user management provide karta hai.

## Features

### Core Authentication
- **Email-based Registration & Login** - Password-based authentication
- **Magic Link Authentication** - Passwordless login via email
- **JWT Token Management** - Secure access aur refresh tokens
- **Email Verification** - Account verification through email
- **Password Reset** - Secure password recovery system

### Security Features
- **Account Lockout** - 5 failed attempts ke baad automatic lock (30 minutes)
- **Session Management** - Multiple device sessions ko track aur manage karo
- **Login History** - Detailed audit trail of all login attempts
- **IP Tracking** - Login attempts aur sessions ke liye IP logging
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
- **User Statistics** - Admin dashboard ke liye analytics
- **Soft Delete** - Users ko deactivate karo instead of permanent deletion

### Management Commands
- `cleanup_tokens` - Expired tokens ko delete karo
- `create_roles` - Default roles setup karo
- `unlock_accounts` - Locked accounts ko unlock karo

## Tech Stack

- **Django** 4.2+
- **Django REST Framework** 3.14+
- **Simple JWT** 5.3+ - JWT authentication
- **Django CORS Headers** - Cross-origin support
- **Celery** - Async task processing
- **Redis** - Caching aur session storage
- **Cryptography** - Secure token generation

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

Server `http://127.0.0.1:8000/` par run hoga.

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

## Usage Examples

### Registration
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "username": "johndoe",
    "role": "CUSTOMER"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### Magic Link Request
```bash
curl -X POST http://localhost:8000/api/auth/magic-link/request/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

### Get Current User
```bash
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer <access_token>"
```

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

## Project Structure

```
authentication/
├── management/
│   └── commands/
│       ├── cleanup_tokens.py
│       ├── create_roles.py
│       └── unlock_accounts.py
├── admin.py              # Django admin configuration
├── middleware.py         # Custom middleware
├── models.py            # User, Token, Session models
├── permissions.py       # Custom permissions
├── serializers.py       # DRF serializers
├── urls.py             # URL routing
├── utils.py            # Helper functions
└── views.py            # API views

config/
├── settings.py         # Django settings
├── urls.py            # Main URL configuration
└── wsgi.py            # WSGI configuration
```

## Security Best Practices

1. **Environment Variables** - Sensitive data ko `.env` file mein store karo
2. **HTTPS** - Production mein hamesha HTTPS use karo
3. **Strong Passwords** - Password validation enable hai
4. **Token Rotation** - Refresh tokens automatically rotate hote hain
5. **Account Lockout** - Brute force attacks se protection
6. **CORS Configuration** - Production mein specific origins allow karo
7. **Rate Limiting** - API endpoints par rate limiting implement karo (recommended)

## Configuration

### JWT Settings
`config/settings.py` mein customize karo:
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

### Email Settings
Production ke liye SMTP configure karo:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## Testing

Tests run karne ke liye:
```bash
python manage.py test authentication
```

## Deployment

### Production Checklist
- [ ] `DEBUG = False` set karo
- [ ] Strong `SECRET_KEY` generate karo
- [ ] `ALLOWED_HOSTS` configure karo
- [ ] Database setup (PostgreSQL recommended)
- [ ] Redis configure karo
- [ ] Email service setup karo
- [ ] HTTPS enable karo
- [ ] Static files collect karo: `python manage.py collectstatic`
- [ ] Migrations run karo: `python manage.py migrate`
- [ ] Superuser create karo

### Environment Variables
Production mein ye environment variables set karo:
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
- Email backend configuration check karo
- SMTP credentials verify karo
- Firewall/port settings check karo

**Token expired errors**
- Token lifetime settings check karo
- System time sync verify karo

**Account locked**
- `unlock_accounts` command run karo
- Ya admin panel se manually unlock karo

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## License

This project is licensed under the MIT License.

## Testing with Postman

Postman collection file included hai testing ke liye:
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

## Documentation Files

- **README.md** - Project overview, setup, aur quick start
- **API_DOCUMENTATION.md** - Complete API reference with examples
- **IMPLEMENTATION_GUIDE.md** - Detailed implementation guide
- **FM_MODULE_GUIDE.md** - Field Manager module complete guide
- **CONTRACTOR_MODULE_GUIDE.md** - Contractor module complete guide
- **PAYOUT_MODULE_GUIDE.md** ⭐ - Payout & Financial Flow complete guide
- **COMPLIANCE_MODULE_GUIDE.md** ⭐ - Compliance & Disputes System complete guide
- **INVESTOR_MODULE_GUIDE.md** ⭐ - Investor Module complete guide
- **AI_MODULE_GUIDE.md** ⭐ - AI-Assisted Features complete guide
- **PDF_MODULE_GUIDE.md** ⭐ - PDF Generation complete guide
- **CRON_AUTOMATION_GUIDE.md** ⭐ - Cron Automation System complete guide
- **DEPLOYMENT_SUMMARY.md** - Complete deployment summary
- **POSTMAN_COLLECTION.json** - Postman collection for API testing
- **customer_signature_example.html** - Customer signature page example
- **.env.example** - Environment variables template

## Support

Issues ya questions ke liye:
- GitHub Issues create karo
- Documentation check karo
- Email: support@yourapp.com

## Admin Payout & Financial Flow Module

### Admin Payout Management
- **Ready for Payout** - View all jobs ready for payment
- **Approve Payouts** - Single or bulk approval
- **Reject Payouts** - Put jobs on hold with reason
- **Auto-Credit Wallet** - Automatic wallet credit on approval
- **Payout Statistics** - Real-time financial overview
- **Payout Reports** - Downloadable CSV reports

### Contractor Wallet System
- **Balance Overview** - Current balance, total earned, withdrawn
- **Pending Amount** - Track pending payout requests
- **Wallet Ledger** - Complete transaction history
- **Credits** - Job payments credited to wallet
- **Debits** - Payout withdrawals
- **Transaction Details** - Reference numbers, descriptions

### Payout Request System
- **Request Withdrawal** - Contractors request payouts
- **Payment Methods** - Bank transfer, PayPal, check, cash
- **Bank Details** - Account number, routing number
- **Admin Approval** - Review and approve/reject requests
- **Status Tracking** - Pending, approved, rejected, completed

### Financial Reports
- **Payout Reports** - Downloadable CSV with date filters
- **Wallet Ledger** - Individual contractor transaction history
- **Statistics Dashboard** - Ready, processing, paid amounts
- **Monthly Summaries** - Track payments by period

## Contractor Module

### Contractor Dashboard
- **Job Statistics** - Pending, accepted, active, completed jobs
- **Assignment Overview** - View all job assignments
- **Performance Ratings** - Quality, timeliness, professionalism ratings
- **Earnings Tracking** - Completed jobs and payouts
- **Notifications** - Real-time job updates

### Job Assignment Workflow
- **View Assignments** - See all assigned jobs
- **Accept/Reject Jobs** - Accept or decline with reason
- **Job Details** - Complete job information
- **Customer Information** - Contact details and location

### Step-by-Step Checklist System
- **Structured Workflow** - Predefined steps for each job
- **Progress Tracking** - Visual completion percentage
- **Required vs Optional** - Mark critical steps
- **Step Completion** - Mark steps as done with notes
- **Media Upload** - Photos/videos for each step

### Photo/Video Upload
- **Step-Level Media** - Upload media for specific steps
- **Multiple Formats** - Photos, videos, documents
- **Captions** - Add descriptions to uploads
- **Thumbnail Support** - Preview images
- **File Management** - View and delete uploads

### Job Completion & Verification
- **Submit for Review** - Mark job as completed
- **Completion Notes** - Add final comments
- **Hours Tracking** - Record actual hours worked
- **Admin Verification** - FM/Admin reviews and approves
- **Rating System** - Receive quality ratings
- **Revision Requests** - Handle feedback and revisions

### Notification System
- **Real-time Alerts** - Job assignments, updates, completions
- **Read/Unread Status** - Track notification status
- **Notification Types** - Assigned, accepted, completed, verified
- **Mark as Read** - Individual or bulk actions

## Field Manager (FM) Module

### FM Dashboard
- **Real-time Statistics** - Job counts by status (Pending, Active, Completed)
- **Financial Overview** - Estimated vs actual costs, variance tracking
- **Estimate Analytics** - Draft, sent, approved, and signed estimates
- **Recent Jobs** - Quick access to latest jobs
- **Upcoming Deadlines** - Jobs approaching due dates
- **Overdue Tracking** - Identify delayed jobs

### FM Job Management
- **Create Jobs** - Full job details with customer information
- **Job Attachments** - Upload and manage multiple files per job
- **Pricing Details** - Estimated and actual costs tracking
- **Status Workflow** - Pending → In Progress → Completed
- **Priority Levels** - Low, Medium, High, Urgent
- **Customer Details** - Name, email, phone, address

### FM Estimate Creation
- **Editable Line Items** - Add/edit/delete line items dynamically
- **Automatic Calculations** - Subtotal, tax, discount, total
- **Tax Rate Configuration** - Flexible tax percentage
- **Draft & Send Workflow** - Create draft, review, then send
- **Estimate Numbering** - Auto-generated unique numbers

### Digital Signature Collection
- **Customer Signing** - Public link for customer signature
- **Base64 Signature Storage** - Secure signature data storage
- **IP Tracking** - Record customer IP on signing
- **Timestamp Recording** - Exact signing time
- **Status Auto-update** - Approved on signature
- **Signature Verification** - View signed estimates

## Workspace & Data Management Module

### Workspace Features
- **Unique Workspace ID** - Har customer/project ke liye unique UUID-based workspace
- **Workspace Types** - Project, Customer, Facility
- **Member Management** - Multiple users ko workspace mein add karo with roles
- **Workspace Statistics** - Real-time analytics aur insights

### Data Entities

#### Jobs
- Job tracking with unique job numbers
- Status management (Pending, In Progress, Completed, Cancelled)
- Priority levels (Low, Medium, High, Urgent)
- Time tracking (estimated vs actual hours)
- Assignment to contractors

#### Estimates
- Estimate creation with unique numbers
- Status workflow (Draft, Sent, Approved, Rejected, Expired)
- Financial calculations (subtotal, tax, discount, total)
- Job linking
- Approval tracking

#### Contractors
- Contractor profiles with company details
- License and specialization tracking
- Hourly rate management
- Rating system
- Job completion tracking

#### Payouts
- Payout management with unique numbers
- Multiple payment methods (Bank Transfer, Check, Cash, PayPal)
- Status tracking (Pending, Processing, Completed, Failed)
- Transaction reference tracking
- Job-based payouts

#### Compliance Data
- Document tracking (License, Insurance, Certification, Safety)
- Expiry date monitoring
- Automatic status updates (Valid, Expiring Soon, Expired)
- Verification workflow
- Document storage paths

### CSV Export Functionality

Har entity ke liye CSV export available hai:

#### Jobs Export
```bash
GET /api/workspaces/<workspace_id>/jobs/export/
```
Exports: Job Number, Title, Status, Priority, Assigned To, Hours, Dates, Location

#### Estimates Export
```bash
GET /api/workspaces/<workspace_id>/estimates/export/
```
Exports: Estimate Number, Title, Status, Financial Details, Approval Info

#### Contractors Export
```bash
GET /api/workspaces/<workspace_id>/contractors/export/
```
Exports: Email, Company, License, Specialization, Rate, Status, Rating

#### Payouts Export
```bash
GET /api/workspaces/<workspace_id>/payouts/export/
```
Exports: Payout Number, Contractor, Amount, Status, Payment Method, Dates

#### Compliance Export
```bash
GET /api/workspaces/<workspace_id>/compliance/export/
```
Exports: Contractor, Compliance Type, Document Details, Status, Dates

## Payout & Financial API Endpoints

### Admin Payout Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/workspaces/admin/payouts/ready/` | View ready for payout jobs | Admin |
| POST | `/api/workspaces/admin/payouts/<id>/approve/` | Approve job payout | Admin |
| POST | `/api/workspaces/admin/payouts/<id>/reject/` | Reject job payout | Admin |
| POST | `/api/workspaces/admin/payouts/bulk-approve/` | Bulk approve payouts | Admin |
| GET | `/api/workspaces/admin/payouts/statistics/` | Get payout statistics | Admin |

### Admin Payout Requests

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/workspaces/admin/payout-requests/` | List all payout requests | Admin |
| POST | `/api/workspaces/admin/payout-requests/<id>/approve/` | Approve request | Admin |
| POST | `/api/workspaces/admin/payout-requests/<id>/reject/` | Reject request | Admin |

### Contractor Wallet

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/workspaces/contractor/wallet/` | Get wallet balance | Contractor |
| GET | `/api/workspaces/contractor/wallet/transactions/` | View transaction history | Contractor |
| GET | `/api/workspaces/contractor/wallet/ledger/download/` | Download ledger CSV | Contractor |
| POST | `/api/workspaces/contractor/wallet/request-payout/` | Request payout | Contractor |
| GET | `/api/workspaces/contractor/payout-requests/` | View payout requests | Contractor |

### Reports

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/workspaces/admin/payouts/report/download/` | Download payout report | Admin |

## Contractor API Endpoints

### Contractor Dashboard

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/workspaces/contractor/dashboard/` | Get contractor dashboard | Contractor |

### Job Assignments

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/workspaces/contractor/assignments/` | List all assignments | Contractor |
| POST | `/api/workspaces/contractor/assignments/<id>/accept/` | Accept job | Contractor |
| POST | `/api/workspaces/contractor/assignments/<id>/reject/` | Reject job | Contractor |

### Active Jobs

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/workspaces/contractor/jobs/active/` | List active jobs | Contractor |
| GET | `/api/workspaces/contractor/jobs/<id>/` | Get job details | Contractor |

### Checklist Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| PATCH | `/api/workspaces/contractor/steps/<id>/` | Update step (mark complete) | Contractor |
| POST | `/api/workspaces/contractor/steps/media/` | Upload photo/video | Contractor |
| GET | `/api/workspaces/contractor/steps/<id>/media/` | List step media | Contractor |
| DELETE | `/api/workspaces/contractor/steps/media/<id>/` | Delete media | Contractor |

### Job Completion

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/workspaces/contractor/jobs/<id>/complete/` | Submit job completion | Contractor |
| GET | `/api/workspaces/contractor/completed-jobs/` | List completed jobs | Contractor |

### Notifications

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/workspaces/contractor/notifications/` | List notifications | Contractor |
| POST | `/api/workspaces/contractor/notifications/<id>/read/` | Mark as read | Contractor |
| POST | `/api/workspaces/contractor/notifications/read-all/` | Mark all as read | Contractor |

### Admin/FM - Contractor Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/workspaces/admin/assign-job/` | Assign job to contractor | FM/Admin |
| POST | `/api/workspaces/admin/verify-completion/<id>/` | Verify job completion | FM/Admin |
| POST | `/api/workspaces/admin/checklists/create/` | Create job checklist | FM/Admin |
| POST | `/api/workspaces/admin/checklist-steps/create/` | Create checklist step | FM/Admin |

## FM API Endpoints

### FM Dashboard

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/workspaces/fm/dashboard/` | Get FM dashboard data | FM/Admin |
| GET | `/api/workspaces/fm/jobs/status/<status>/` | Get jobs by status | FM/Admin |

### FM Job Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/workspaces/fm/jobs/` | List FM's jobs | FM/Admin |
| POST | `/api/workspaces/fm/jobs/create/` | Create new job | FM/Admin |
| GET | `/api/workspaces/fm/jobs/<id>/` | Get job details | FM/Admin |
| PATCH | `/api/workspaces/fm/jobs/<id>/` | Update job | FM/Admin |

### Job Attachments

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/workspaces/fm/jobs/attachments/` | Upload attachment | FM/Admin |
| GET | `/api/workspaces/fm/jobs/<job_id>/attachments/` | List attachments | Yes |
| DELETE | `/api/workspaces/fm/jobs/attachments/<id>/` | Delete attachment | FM/Admin |

### FM Estimate Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/workspaces/fm/estimates/` | List FM's estimates | FM/Admin |
| POST | `/api/workspaces/fm/estimates/create/` | Create estimate with line items | FM/Admin |
| GET | `/api/workspaces/fm/estimates/<id>/` | Get estimate details | FM/Admin |
| PATCH | `/api/workspaces/fm/estimates/<id>/` | Update estimate | FM/Admin |

### Estimate Line Items

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/workspaces/fm/estimates/line-items/` | Add line item | FM/Admin |
| GET | `/api/workspaces/fm/estimates/<id>/line-items/` | List line items | Yes |
| PATCH | `/api/workspaces/fm/estimates/line-items/<id>/` | Update line item | FM/Admin |
| DELETE | `/api/workspaces/fm/estimates/line-items/<id>/` | Delete line item | FM/Admin |

### Estimate Actions

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/workspaces/fm/estimates/<id>/send/` | Send estimate to customer | FM/Admin |
| POST | `/api/workspaces/fm/estimates/<id>/recalculate/` | Recalculate totals | FM/Admin |

### Customer Signature (Public)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/workspaces/public/estimates/<number>/` | View estimate for signing | No |
| POST | `/api/workspaces/public/estimates/<id>/sign/` | Sign estimate | No |

## Workspace API Endpoints

### Workspace Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/workspaces/` | List all workspaces | Yes |
| POST | `/api/workspaces/` | Create new workspace | Yes |
| GET | `/api/workspaces/<id>/` | Get workspace details | Yes |
| PATCH | `/api/workspaces/<id>/` | Update workspace | Yes |
| DELETE | `/api/workspaces/<id>/` | Delete workspace | Yes |
| GET | `/api/workspaces/<id>/stats/` | Get workspace statistics | Yes |

### Jobs

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/workspaces/<id>/jobs/` | List jobs | Yes |
| POST | `/api/workspaces/<id>/jobs/` | Create job | Yes |
| GET | `/api/workspaces/jobs/<job_id>/` | Get job details | Yes |
| PATCH | `/api/workspaces/jobs/<job_id>/` | Update job | Yes |
| DELETE | `/api/workspaces/jobs/<job_id>/` | Delete job | Yes |
| GET | `/api/workspaces/<id>/jobs/export/` | Export jobs to CSV | Yes |

### Estimates

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/workspaces/<id>/estimates/` | List estimates | Yes |
| POST | `/api/workspaces/<id>/estimates/` | Create estimate | Yes |
| GET | `/api/workspaces/estimates/<est_id>/` | Get estimate details | Yes |
| PATCH | `/api/workspaces/estimates/<est_id>/` | Update estimate | Yes |
| DELETE | `/api/workspaces/estimates/<est_id>/` | Delete estimate | Yes |
| GET | `/api/workspaces/<id>/estimates/export/` | Export estimates to CSV | Yes |

### Contractors

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/workspaces/<id>/contractors/` | List contractors | Yes |
| POST | `/api/workspaces/<id>/contractors/` | Add contractor | Yes |
| GET | `/api/workspaces/contractors/<c_id>/` | Get contractor details | Yes |
| PATCH | `/api/workspaces/contractors/<c_id>/` | Update contractor | Yes |
| DELETE | `/api/workspaces/contractors/<c_id>/` | Remove contractor | Yes |
| GET | `/api/workspaces/<id>/contractors/export/` | Export contractors to CSV | Yes |

### Payouts

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/workspaces/<id>/payouts/` | List payouts | Yes |
| POST | `/api/workspaces/<id>/payouts/` | Create payout | Yes |
| GET | `/api/workspaces/payouts/<p_id>/` | Get payout details | Yes |
| PATCH | `/api/workspaces/payouts/<p_id>/` | Update payout | Yes |
| DELETE | `/api/workspaces/payouts/<p_id>/` | Delete payout | Yes |
| GET | `/api/workspaces/<id>/payouts/export/` | Export payouts to CSV | Yes |

### Compliance

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/workspaces/<id>/compliance/` | List compliance data | Yes |
| POST | `/api/workspaces/<id>/compliance/` | Add compliance record | Yes |
| GET | `/api/workspaces/compliance/<c_id>/` | Get compliance details | Yes |
| PATCH | `/api/workspaces/compliance/<c_id>/` | Update compliance | Yes |
| DELETE | `/api/workspaces/compliance/<c_id>/` | Delete compliance | Yes |
| GET | `/api/workspaces/<id>/compliance/export/` | Export compliance to CSV | Yes |
| GET | `/api/workspaces/<id>/compliance/expiring/` | Get expiring documents | Yes |

## Usage Examples - Payout & Financial Module

### Admin Views Ready for Payout Jobs
```bash
curl -X GET http://localhost:8000/api/workspaces/admin/payouts/ready/ \
  -H "Authorization: Bearer <admin_token>"
```

### Admin Approves Job Payout
```bash
curl -X POST http://localhost:8000/api/workspaces/admin/payouts/1/approve/ \
  -H "Authorization: Bearer <admin_token>"
```

### Admin Bulk Approves Payouts
```bash
curl -X POST http://localhost:8000/api/workspaces/admin/payouts/bulk-approve/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "eligibility_ids": [1, 2, 3, 4, 5]
  }'
```

### Get Payout Statistics
```bash
curl -X GET http://localhost:8000/api/workspaces/admin/payouts/statistics/ \
  -H "Authorization: Bearer <admin_token>"
```

### Contractor Views Wallet
```bash
curl -X GET http://localhost:8000/api/workspaces/contractor/wallet/ \
  -H "Authorization: Bearer <contractor_token>"
```

### Contractor Views Transaction History
```bash
curl -X GET "http://localhost:8000/api/workspaces/contractor/wallet/transactions/?transaction_type=credit" \
  -H "Authorization: Bearer <contractor_token>"
```

### Contractor Downloads Wallet Ledger
```bash
curl -X GET http://localhost:8000/api/workspaces/contractor/wallet/ledger/download/ \
  -H "Authorization: Bearer <contractor_token>" \
  -o wallet_ledger.csv
```

### Contractor Requests Payout
```bash
curl -X POST http://localhost:8000/api/workspaces/contractor/wallet/request-payout/ \
  -H "Authorization: Bearer <contractor_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500.00,
    "payment_method": "BANK_TRANSFER",
    "bank_account_number": "1234567890",
    "bank_name": "Chase Bank",
    "bank_routing_number": "021000021",
    "notes": "Weekly payout request"
  }'
```

### Admin Approves Payout Request
```bash
curl -X POST http://localhost:8000/api/workspaces/admin/payout-requests/1/approve/ \
  -H "Authorization: Bearer <admin_token>"
```

### Admin Rejects Payout Request
```bash
curl -X POST http://localhost:8000/api/workspaces/admin/payout-requests/1/reject/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "rejection_reason": "Insufficient documentation provided"
  }'
```

### Download Payout Report
```bash
curl -X GET "http://localhost:8000/api/workspaces/admin/payouts/report/download/?date_from=2025-01-01&date_to=2025-12-31" \
  -H "Authorization: Bearer <admin_token>" \
  -o payout_report.csv
```

## Usage Examples - Contractor Module

### Get Contractor Dashboard
```bash
curl -X GET http://localhost:8000/api/workspaces/contractor/dashboard/ \
  -H "Authorization: Bearer <contractor_token>"
```

### View Job Assignments
```bash
curl -X GET "http://localhost:8000/api/workspaces/contractor/assignments/?status=pending" \
  -H "Authorization: Bearer <contractor_token>"
```

### Accept Job Assignment
```bash
curl -X POST http://localhost:8000/api/workspaces/contractor/assignments/1/accept/ \
  -H "Authorization: Bearer <contractor_token>"
```

### Reject Job Assignment
```bash
curl -X POST http://localhost:8000/api/workspaces/contractor/assignments/1/reject/ \
  -H "Authorization: Bearer <contractor_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "rejection_reason": "Schedule conflict - unavailable during requested timeframe"
  }'
```

### Get Active Jobs
```bash
curl -X GET http://localhost:8000/api/workspaces/contractor/jobs/active/ \
  -H "Authorization: Bearer <contractor_token>"
```

### Mark Checklist Step as Complete
```bash
curl -X PATCH http://localhost:8000/api/workspaces/contractor/steps/1/ \
  -H "Authorization: Bearer <contractor_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "is_completed": true,
    "notes": "Step completed successfully. All equipment tested and working."
  }'
```

### Upload Photo for Step
```bash
curl -X POST http://localhost:8000/api/workspaces/contractor/steps/media/ \
  -H "Authorization: Bearer <contractor_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "step": 1,
    "media_type": "PHOTO",
    "file_name": "before_work.jpg",
    "file_path": "/uploads/steps/before_work.jpg",
    "file_size": 1024576,
    "caption": "Before starting the repair work"
  }'
```

### Submit Job Completion
```bash
curl -X POST http://localhost:8000/api/workspaces/contractor/jobs/1/complete/ \
  -H "Authorization: Bearer <contractor_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "completion_notes": "Job completed successfully. All checklist items verified. Customer satisfied with work.",
    "actual_hours_worked": 7.5
  }'
```

### FM Assigns Job to Contractor
```bash
curl -X POST http://localhost:8000/api/workspaces/admin/assign-job/ \
  -H "Authorization: Bearer <fm_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 1,
    "contractor_id": 2,
    "notes": "Contractor has relevant experience with HVAC systems"
  }'
```

### FM Verifies Job Completion
```bash
curl -X POST http://localhost:8000/api/workspaces/admin/verify-completion/1/ \
  -H "Authorization: Bearer <fm_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "verification_notes": "Excellent work. All requirements met.",
    "quality_rating": 5,
    "timeliness_rating": 5,
    "professionalism_rating": 5
  }'
```

### FM Creates Job Checklist
```bash
curl -X POST http://localhost:8000/api/workspaces/admin/checklists/create/ \
  -H "Authorization: Bearer <fm_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "job": 1,
    "title": "HVAC System Repair Checklist",
    "description": "Standard checklist for HVAC repairs",
    "order": 1
  }'
```

### FM Creates Checklist Steps
```bash
curl -X POST http://localhost:8000/api/workspaces/admin/checklist-steps/create/ \
  -H "Authorization: Bearer <fm_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "checklist": 1,
    "step_number": 1,
    "title": "Initial System Inspection",
    "description": "Inspect HVAC system and identify issues",
    "is_required": true
  }'
```

## Usage Examples - FM Module

### Get FM Dashboard
```bash
curl -X GET "http://localhost:8000/api/workspaces/fm/dashboard/?workspace_id=<workspace_id>" \
  -H "Authorization: Bearer <access_token>"
```

### Create Job with Details
```bash
curl -X POST http://localhost:8000/api/workspaces/fm/jobs/create/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "<workspace_id>",
    "title": "HVAC System Repair",
    "description": "Complete HVAC system inspection and repair",
    "status": "PENDING",
    "priority": "HIGH",
    "estimated_hours": 8,
    "estimated_cost": 1500.00,
    "due_date": "2025-12-20",
    "location": "Building A, Floor 3",
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "customer_phone": "+1-555-0123",
    "customer_address": "123 Main St, City, State"
  }'
```

### Create Estimate with Line Items
```bash
curl -X POST http://localhost:8000/api/workspaces/fm/estimates/create/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "<workspace_id>",
    "job": 1,
    "title": "HVAC Repair Estimate",
    "description": "Complete cost breakdown",
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
    ]
  }'
```

### Send Estimate to Customer
```bash
curl -X POST http://localhost:8000/api/workspaces/fm/estimates/1/send/ \
  -H "Authorization: Bearer <access_token>"
```

### Customer Views Estimate (Public)
```bash
curl -X GET http://localhost:8000/api/workspaces/public/estimates/EST-A1B2C3D4-00001/
```

### Customer Signs Estimate (Public)
```bash
curl -X POST http://localhost:8000/api/workspaces/public/estimates/1/sign/ \
  -H "Content-Type: application/json" \
  -d '{
    "signature": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
  }'
```

### Get Jobs by Status
```bash
curl -X GET http://localhost:8000/api/workspaces/fm/jobs/status/pending/ \
  -H "Authorization: Bearer <access_token>"
```

### Upload Job Attachment
```bash
curl -X POST http://localhost:8000/api/workspaces/fm/jobs/attachments/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "job": 1,
    "file_name": "blueprint.pdf",
    "file_path": "/uploads/jobs/blueprint.pdf",
    "file_type": "application/pdf",
    "file_size": 2048576,
    "description": "Building blueprint"
  }'
```

## Usage Examples - Workspace Module

### Create Workspace
```bash
curl -X POST http://localhost:8000/api/workspaces/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Downtown Facility Project",
    "workspace_type": "PROJECT",
    "description": "Main facility management project"
  }'
```

### Create Job
```bash
curl -X POST http://localhost:8000/api/workspaces/<workspace_id>/jobs/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "HVAC Maintenance",
    "description": "Quarterly HVAC system maintenance",
    "status": "PENDING",
    "priority": "HIGH",
    "estimated_hours": 8,
    "due_date": "2025-12-15",
    "location": "Building A, Floor 3"
  }'
```

### Export Jobs to CSV
```bash
curl -X GET http://localhost:8000/api/workspaces/<workspace_id>/jobs/export/ \
  -H "Authorization: Bearer <access_token>" \
  -o jobs_export.csv
```

### Get Workspace Statistics
```bash
curl -X GET http://localhost:8000/api/workspaces/<workspace_id>/stats/ \
  -H "Authorization: Bearer <access_token>"
```

### Check Expiring Compliance Documents
```bash
curl -X GET http://localhost:8000/api/workspaces/<workspace_id>/compliance/expiring/ \
  -H "Authorization: Bearer <access_token>"
```

## Project Structure (Updated)

```
authentication/
├── management/commands/
│   ├── cleanup_tokens.py
│   ├── create_roles.py
│   └── unlock_accounts.py
├── models.py              # User, Token, Session models
├── serializers.py         # Authentication serializers
├── views.py              # Auth API views
├── urls.py               # Auth URL routing
├── permissions.py        # Custom permissions
└── utils.py              # Helper functions

workspace/
├── management/commands/
│   ├── update_compliance_status.py
│   └── generate_workspace_report.py
├── models.py              # Workspace, Job, JobAttachment, Estimate, 
│                          # EstimateLineItem, Contractor, Payout, 
│                          # Report, ComplianceData models
├── serializers.py         # DRF serializers for all models
├── views.py              # General workspace API views
├── fm_views.py           # Field Manager specific views
├── urls.py               # Complete URL routing
├── utils.py              # CSV export & number generators
├── admin.py              # Django admin configuration
└── tests.py              # Unit tests

config/
├── settings.py           # Django settings
├── urls.py              # Main URL configuration
└── wsgi.py              # WSGI configuration

Documentation/
├── README.md                    # Main documentation
├── API_DOCUMENTATION.md         # Complete API reference
├── IMPLEMENTATION_GUIDE.md      # Implementation details
├── POSTMAN_COLLECTION.json      # Postman test collection
└── .env.example                 # Environment variables template
```

## Changelog

### Version 1.0.0
- Initial release
- Email/password authentication
- Magic link authentication
- Role-based access control
- Session management
- Login history tracking
- Account lockout mechanism
- Workspace management with unique IDs
- Job tracking and management
- Estimate creation and approval
- Contractor management
- Payout processing
- Compliance tracking
- CSV export for all data entities
- **Field Manager (FM) Module**
  - FM Dashboard with real-time statistics
  - Job creation with customer details
  - Job attachments management
  - Estimate creation with editable line items
  - Automatic calculation (subtotal, tax, total)
  - Digital signature collection
  - Public estimate signing links
  - Status-based job filtering
  - Financial tracking (estimated vs actual)
- **Contractor Module** ✅
  - Contractor dashboard with job statistics
  - Job assignment acceptance/rejection
  - Active job workflow management
  - Step-by-step checklist system
  - Photo/video upload for each step
  - Progress tracking with completion percentage
  - Job completion submission
  - Admin/FM verification workflow
  - Rating system (quality, timeliness, professionalism)
  - Real-time notification system
  - Revision request handling
- **Admin Payout & Financial Flow** ⭐ NEW
  - Ready for payout jobs view
  - Single and bulk payout approval
  - Auto-credit contractor wallet
  - Contractor wallet system
  - Transaction ledger (credits/debits)
  - Payout request system
  - Admin approval/rejection workflow
  - Downloadable payout reports
  - Wallet ledger CSV export
  - Real-time financial statistics
- **Compliance & Disputes System** ⭐ NEW
  - Contractor compliance hub
  - Document upload (ID, insurance, certificates, contracts)
  - Expiry tracking & auto-status updates
  - Admin compliance center
  - Document verification (approve/reject)
  - Dispute management system
  - Customer → FM → Admin escalation flow
  - Dispute messaging & attachments
  - Resolution tracking
  - Comprehensive statistics
- **Investor Module** ⭐ NEW
  - Investor dashboard with revenue statistics
  - Overall revenue & profit tracking
  - ROI analytics & profitability analysis
  - Job volume breakdown
  - Payout analytics & trends
  - Monthly revenue breakdown
  - Workspace-wise performance comparison
  - Top contractor earnings
  - Downloadable reports (CSV)
  - Recent activity feed
- **AI-Assisted Features** ⭐ NEW
  - AI job description generator
  - AI checklist suggestions
  - Pricing anomaly detection
  - Missing items detection
  - Smart recommendations for FM
  - Contractor recommendation system
  - At-risk job identification
  - Workflow optimization tips
- **PDF Generation** ⭐ NEW
  - Professional estimate PDFs
  - Comprehensive job report PDFs
  - Official payout slip PDFs
  - Compliance certificate PDFs
  - Detailed investor report PDFs
  - Automatic PDF generation
  - Professional formatting & branding
  - One-click downloads
- **Cron Automation System** ⭐ NEW
  - Daily compliance expiry check
  - Pending jobs reminder
  - Daily summary email to FM/Admin
  - Payout reminders
  - Auto close stale jobs
  - Automated email notifications
  - Scheduled task management
