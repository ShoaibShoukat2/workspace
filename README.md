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

### Authentication Endpoints

```
POST /api/v1/auth/register          # User registration
POST /api/v1/auth/login             # Email/password login
POST /api/v1/auth/refresh           # Refresh access token
POST /api/v1/auth/magic-link/request # Request magic link
POST /api/v1/auth/magic-link/verify  # Verify magic link
POST /api/v1/auth/verify-email      # Verify email address
POST /api/v1/auth/password-reset/request # Request password reset
POST /api/v1/auth/password-reset/confirm # Confirm password reset
GET  /api/v1/auth/me                # Get current user
PATCH /api/v1/auth/profile          # Update profile
POST /api/v1/auth/logout            # Logout
```

### Core Business Endpoints

```
# Workspaces
GET    /api/v1/workspaces           # List workspaces
POST   /api/v1/workspaces           # Create workspace
GET    /api/v1/workspaces/{id}      # Get workspace
PATCH  /api/v1/workspaces/{id}      # Update workspace

# Jobs
GET    /api/v1/jobs                 # List jobs
POST   /api/v1/jobs                 # Create job
GET    /api/v1/jobs/{id}            # Get job
PATCH  /api/v1/jobs/{id}            # Update job

# Contractors
GET    /api/v1/contractors          # List contractors
POST   /api/v1/contractors          # Create contractor
GET    /api/v1/contractors/{id}     # Get contractor
```

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