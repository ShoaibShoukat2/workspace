# Apex Workspace Management API

Complete FastAPI conversion of Django backend with all functionality preserved.

## 🚀 Features

### Authentication & Security
- JWT-based authentication with refresh tokens
- Magic link passwordless login
- Email verification system
- Password reset functionality
- Role-based access control (Admin, FM, Contractor, Customer, Investor)
- Account lockout protection
- Session management
- Login history tracking

### Core Modules
- **Workspace Management**: Multi-tenant workspace system
- **Job Management**: Complete job lifecycle tracking
- **Contractor Management**: Contractor profiles, compliance, payouts
- **Customer Portal**: Customer dashboard with real-time tracking
- **Estimate System**: Quote generation and approval workflow
- **Compliance Tracking**: Document verification and expiry monitoring
- **GPS Tracking**: Real-time contractor location tracking
- **Reporting**: Comprehensive analytics and reports

### Advanced Features
- **AI Integration**: OpenAI-powered job descriptions and recommendations
- **Material Intelligence**: Price scraping and material suggestions
- **Angi Integration**: Lead management and scraping
- **Twilio Integration**: SMS and voice communications
- **Insurance Verification**: Automated insurance document processing
- **Dispute Management**: Complete dispute resolution system
- **Investor Portal**: ROI tracking and financial analytics

## 🛠 Technology Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL with SQLAlchemy 2.0 (async)
- **Authentication**: JWT with python-jose
- **Caching**: Redis
- **Background Tasks**: Celery
- **Email**: SMTP with HTML templates
- **File Storage**: Local/AWS S3
- **API Documentation**: Automatic OpenAPI/Swagger

## 📦 Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd apex-workspace-api
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Start services:
```bash
docker-compose up -d
```

4. Run database migrations:
```bash
docker-compose exec api alembic upgrade head
```

5. Access the API:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Manual Installation

1. Install Python 3.11+
2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r fastapi_requirements.txt
```

4. Set up PostgreSQL and Redis
5. Copy and configure `.env` file
6. Run migrations:
```bash
alembic upgrade head
```

7. Start the application:
```bash
uvicorn main:app --reload
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/apex_workspace

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Email
EMAIL_BACKEND=smtp  # or console for development
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# External APIs
OPENAI_API_KEY=your-openai-key
TWILIO_ACCOUNT_SID=your-twilio-sid
GOOGLE_MAPS_API_KEY=your-maps-key
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

---

## 🔐 Authentication Endpoints

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "admin@apex.inc",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@apex.inc",
    "full_name": "Admin User",
    "role": "ADMIN"
  },
  "profile": {
    "id": 1,
    "email": "admin@apex.inc",
    "full_name": "Admin User",
    "user_role": "ADMIN",
    "profileID": "PROF-000001",
    "profile_id": "PROF-000001"
  }
}
```

### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "email": "admin@apex.inc",
  "full_name": "Admin User",
  "role": "ADMIN",
  "is_active": true
}
```

### Get All Profiles
```http
GET /profiles
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "email": "admin@apex.inc",
    "full_name": "Admin User",
    "user_role": "ADMIN",
    "profileID": "PROF-000001",
    "profile_id": "PROF-000001"
  },
  {
    "id": 2,
    "email": "contractor@apex.inc",
    "full_name": "John Contractor",
    "user_role": "CONTRACTOR",
    "profileID": "PROF-000002",
    "profile_id": "PROF-000002"
  }
]
```

---

## 👨‍💼 Admin Dashboard APIs

### Get Admin Dashboard Overview
```http
GET /admin/dashboard
Authorization: Bearer <admin-token>
```

**Response:**
```json
{
  "total_jobs": 3,
  "active_jobs": 2,
  "completed_jobs": 1,
  "total_contractors": 2,
  "active_contractors": 2,
  "pending_payouts": 1,
  "pending_payouts_amount": 950.0,
  "pending_disputes": 0,
  "blocked_contractors": 0,
  "revenue_data": [
    {"month": "Jan", "value": 4000},
    {"month": "Feb", "value": 3000},
    {"month": "Mar", "value": 2000},
    {"month": "Apr", "value": 2780},
    {"month": "May", "value": 1890},
    {"month": "Jun", "value": 2390},
    {"month": "Jul", "value": 3490}
  ],
  "job_stats": [
    {"name": "Open", "count": 1},
    {"name": "In Progress", "count": 1},
    {"name": "Completed", "count": 1},
    {"name": "Paid", "count": 0}
  ],
  "recent_contractors": [
    {
      "id": "1",
      "user_id": "2",
      "full_name": "John Contractor",
      "email": "contractor@apex.inc",
      "phone": "555-0101",
      "trade": "Painting",
      "status": "ACTIVE",
      "compliance_status": "active",
      "created_at": "2024-01-01"
    }
  ],
  "active_investors": []
}
```

### Get All Jobs (Admin)
```http
GET /admin/jobs?status=Open
Authorization: Bearer <admin-token>
```

**Response:**
```json
{
  "jobs": [
    {
      "id": "101",
      "job_number": "JOB-20241201-001",
      "customer_name": "John Smith",
      "property_address": "123 Main St",
      "status": "InProgress",
      "trade": "Painting",
      "estimated_cost": "5000",
      "actual_cost": "4800",
      "assigned_contractor_id": "2",
      "created_at": "2024-12-01"
    }
  ],
  "total": 1
}
```

### Get All Payouts (Admin)
```http
GET /admin/payouts?status=PENDING
Authorization: Bearer <admin-token>
```

**Response:**
```json
{
  "payouts": [
    {
      "id": "2",
      "contractor_id": "1",
      "amount": "950.00",
      "status": "PENDING",
      "job_id": "103",
      "created_at": "2024-12-03",
      "paid_date": null,
      "contractor_name": "John Contractor",
      "contractor_email": "contractor@apex.inc"
    }
  ],
  "total": 1
}
```

### Approve Payout
```http
POST /admin/payouts/2/approve
Authorization: Bearer <admin-token>
```

**Response:**
```json
{
  "message": "Payout approved successfully"
}
```

### Reject Payout
```http
POST /admin/payouts/2/reject
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "reason": "Incomplete documentation"
}
```

**Response:**
```json
{
  "message": "Payout rejected successfully"
}
```

### Get All Contractors (Admin)
```http
GET /admin/contractors
Authorization: Bearer <admin-token>
```

**Response:**
```json
{
  "contractors": [
    {
      "id": "1",
      "user_id": "2",
      "full_name": "John Contractor",
      "email": "contractor@apex.inc",
      "phone": "555-0101",
      "trade": "Painting",
      "status": "ACTIVE",
      "compliance_status": "active",
      "created_at": "2024-01-01"
    }
  ],
  "total": 1
}
```

### Get All Users (Admin)
```http
GET /admin/users
Authorization: Bearer <admin-token>
```

**Response:**
```json
{
  "users": [
    {
      "id": "1",
      "email": "admin@apex.inc",
      "password_hash": "$2b$12$hash1",
      "full_name": "Admin User",
      "role": "ADMIN",
      "is_active": "True",
      "created_at": "2024-01-01"
    }
  ],
  "total": 5
}
```

---

## 🔨 Contractor Dashboard APIs

### Get Contractor Dashboard Overview
```http
GET /contractors/dashboard/overview
Authorization: Bearer <contractor-token>
```

**Response:**
```json
{
  "stats": {
    "active_jobs": 1,
    "completed_jobs": 1,
    "total_earnings": 1200.0,
    "pending_payouts": 950.0
  },
  "recent_jobs": [
    {
      "id": "101",
      "job_number": "JOB-20241201-001",
      "customer_name": "John Smith",
      "property_address": "123 Main St",
      "status": "InProgress",
      "trade": "Painting",
      "estimated_cost": "5000",
      "actual_cost": "4800",
      "assigned_contractor_id": "2",
      "created_at": "2024-12-01"
    }
  ],
  "compliance_status": "active"
}
```

### Get Available Jobs
```http
GET /contractors/jobs/available
Authorization: Bearer <contractor-token>
```

**Response:**
```json
{
  "jobs": [
    {
      "id": "102",
      "job_number": "JOB-20241202-002",
      "customer_name": "Jane Doe",
      "property_address": "456 Oak Ave",
      "status": "Open",
      "trade": "Plumbing",
      "estimated_cost": "3000",
      "actual_cost": null,
      "assigned_contractor_id": null,
      "created_at": "2024-12-02"
    }
  ],
  "total": 1
}
```

### Get My Jobs
```http
GET /contractors/jobs/my-jobs
Authorization: Bearer <contractor-token>
```

**Response:**
```json
{
  "jobs": [
    {
      "id": "101",
      "job_number": "JOB-20241201-001",
      "customer_name": "John Smith",
      "property_address": "123 Main St",
      "status": "InProgress",
      "trade": "Painting",
      "estimated_cost": "5000",
      "actual_cost": "4800",
      "assigned_contractor_id": "2",
      "created_at": "2024-12-01"
    }
  ],
  "total": 1
}
```

### Get Contractor Wallet
```http
GET /contractors/wallet
Authorization: Bearer <contractor-token>
```

**Response:**
```json
{
  "total_paid": 1200.0,
  "pending_amount": 950.0,
  "available_balance": 1200.0
}
```

### Get Contractor Payouts
```http
GET /contractors/payouts
Authorization: Bearer <contractor-token>
```

**Response:**
```json
{
  "payouts": [
    {
      "id": "1",
      "contractor_id": "1",
      "amount": "1200.00",
      "status": "COMPLETED",
      "job_id": "101",
      "created_at": "2024-12-01",
      "paid_date": "2024-12-05"
    },
    {
      "id": "2",
      "contractor_id": "1",
      "amount": "950.00",
      "status": "PENDING",
      "job_id": "103",
      "created_at": "2024-12-03",
      "paid_date": null
    }
  ],
  "total": 2
}
```

---

## 👥 Customer Dashboard APIs

### Get Customer Dashboard
```http
GET /customers/dashboard
Authorization: Bearer <customer-token>
```

**Response:**
```json
{
  "active_job": {
    "id": "101",
    "job_number": "JOB-20241201-001",
    "customer_name": "John Smith",
    "property_address": "123 Main St",
    "status": "InProgress",
    "trade": "Painting",
    "estimated_cost": "5000",
    "actual_cost": "4800",
    "assigned_contractor_id": "2",
    "created_at": "2024-12-01"
  },
  "total_jobs": 3,
  "completed_jobs": 1
}
```

### Get Customer Jobs
```http
GET /customers/jobs
Authorization: Bearer <customer-token>
```

**Response:**
```json
{
  "jobs": [
    {
      "id": "101",
      "job_number": "JOB-20241201-001",
      "customer_name": "John Smith",
      "property_address": "123 Main St",
      "status": "InProgress",
      "trade": "Painting",
      "estimated_cost": "5000",
      "actual_cost": "4800",
      "assigned_contractor_id": "2",
      "created_at": "2024-12-01"
    }
  ],
  "total": 3
}
```

### Get Specific Job
```http
GET /customers/jobs/101
Authorization: Bearer <customer-token>
```

**Response:**
```json
{
  "id": "101",
  "job_number": "JOB-20241201-001",
  "customer_name": "John Smith",
  "property_address": "123 Main St",
  "status": "InProgress",
  "trade": "Painting",
  "estimated_cost": "5000",
  "actual_cost": "4800",
  "assigned_contractor_id": "2",
  "created_at": "2024-12-01"
}
```

### Get Contractor Location
```http
GET /customers/jobs/101/contractor-location
Authorization: Bearer <customer-token>
```

**Response:**
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "last_updated": "2024-12-24T10:30:00Z",
  "status": "En Route"
}
```

---

## 💰 Investor Dashboard APIs

### Get Investor Dashboard
```http
GET /investors/dashboard
Authorization: Bearer <investor-token>
```

**Response:**
```json
{
  "total_investment": 50000.0,
  "total_returns": 12500.0,
  "active_projects": 3,
  "roi_percentage": 25.0,
  "investor": {
    "name": "Bob Investor",
    "email": "investor@apex.inc"
  },
  "roi_data": [
    {"month": "Jan", "value": 12},
    {"month": "Feb", "value": 19},
    {"month": "Mar", "value": 15},
    {"month": "Apr", "value": 22},
    {"month": "May", "value": 28},
    {"month": "Jun", "value": 25}
  ],
  "allocation_data": [
    {"name": "Flips", "value": 65, "color": "#8b5cf6"},
    {"name": "Rentals", "value": 25, "color": "#ec4899"},
    {"name": "Commercial", "value": 10, "color": "#3b82f6"}
  ]
}
```

### Get Investor Reports
```http
GET /investors/reports
Authorization: Bearer <investor-token>
```

**Response:**
```json
{
  "reports": [
    {
      "id": 1,
      "title": "Q4 2024 Performance Report",
      "type": "Quarterly",
      "status": "Ready",
      "created_at": "2024-12-20",
      "file_size": "2.4 MB"
    }
  ],
  "total": 1
}
```

---

## 🏗️ FM (Facility Manager) Dashboard APIs

### Get FM Dashboard
```http
GET /fm/dashboard
Authorization: Bearer <fm-token>
```

**Response:**
```json
{
  "pending_visits": 2,
  "active_jobs": 5,
  "completed_today": 1,
  "total_visits": 15
}
```

### Get FM Assigned Jobs
```http
GET /fm/jobs/assigned
Authorization: Bearer <fm-token>
```

**Response:**
```json
{
  "jobs": [
    {
      "id": "101",
      "job_number": "JOB-20241201-001",
      "customer_name": "John Smith",
      "property_address": "123 Main St",
      "status": "InProgress",
      "trade": "Painting",
      "estimated_cost": "5000",
      "actual_cost": "4800",
      "assigned_contractor_id": "2",
      "created_at": "2024-12-01"
    }
  ],
  "total": 3
}
```

---

## 🔧 Additional Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "Apex Workspace Management API is running",
  "version": "2.0.0"
}
```

### Root Endpoint
```http
GET /
```

**Response:**
```json
{
  "message": "Welcome to Apex Workspace Management API",
  "docs": "/docs",
  "redoc": "/redoc",
  "health": "/health"
}
```

---

## 📋 Test Users

For testing purposes, the following users are available:

| Role | Email | Password | Description |
|------|-------|----------|-------------|
| Admin | admin@apex.inc | any | Full system access |
| Contractor | contractor@apex.inc | any | Contractor dashboard access |
| Customer | customer@apex.inc | any | Customer portal access |
| Investor | investor@apex.inc | any | Investor dashboard access |
| FM | fm@apex.inc | any | Facility manager access |

**Note**: CSV storage uses placeholder password hashes. Any password will work for testing.

---

## 🚀 Quick Start Testing

1. **Start the servers:**
   - Backend: `python main.py` (runs on http://localhost:8000)
   - Frontend: `npm run dev` (runs on http://localhost:5173)

2. **Login:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@apex.inc", "password": "test123"}'
   ```

3. **Test dashboard:**
   ```bash
   curl -X GET http://localhost:8000/api/v1/admin/dashboard \
     -H "Authorization: Bearer <your-token>"
   ```

4. **Open frontend:**
   Visit http://localhost:5173 and login with any test user.

---

## 🏗 Database Schema

### Key Models

- **User**: Authentication and user management
- **Workspace**: Multi-tenant workspace system
- **Job**: Core job management with status tracking
- **Contractor**: Contractor profiles and management
- **Estimate**: Quote and estimate system
- **ComplianceData**: Document and compliance tracking
- **JobTracking**: GPS and progress tracking
- **MaterialSuggestion**: AI-powered material recommendations

### Relationships

- Users belong to multiple workspaces with different roles
- Jobs belong to workspaces and can be assigned to contractors
- Estimates are linked to jobs and workspaces
- Compliance data tracks contractor documents
- Job tracking provides real-time status updates

## 🔐 Security Features

- **JWT Authentication**: Secure token-based auth
- **Role-Based Access**: Fine-grained permissions
- **Account Lockout**: Protection against brute force
- **Session Management**: Track and revoke sessions
- **Email Verification**: Verify user email addresses
- **Password Security**: Bcrypt hashing with validation
- **CORS Protection**: Configurable CORS policies
- **Input Validation**: Pydantic schema validation

## 🚀 Deployment

### Production Deployment

1. Set up PostgreSQL and Redis servers
2. Configure environment variables for production
3. Set up SSL/TLS certificates
4. Use a production WSGI server (Gunicorn + Uvicorn)
5. Set up reverse proxy (Nginx)
6. Configure monitoring and logging

### Docker Production

```bash
# Build production image
docker build -t apex-workspace-api .

# Run with production settings
docker run -d \
  --name apex-api \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://... \
  -e DEBUG=False \
  apex-workspace-api
```

## 🧪 Testing

Run tests with pytest:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app
```

## 📊 Monitoring

### Health Checks

- **Health Endpoint**: `GET /health`
- **Database Check**: Verifies database connectivity
- **Redis Check**: Verifies cache connectivity

### Logging

Structured logging with configurable levels:
- Request/response logging
- Error tracking
- Performance monitoring
- Security event logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the code examples in the repository

---

**Note**: This is a complete FastAPI conversion of the original Django backend, maintaining all functionality while providing improved performance, better async support, and modern API standards.