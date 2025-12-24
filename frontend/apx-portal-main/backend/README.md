# Apex Portal Backend API

Simple Flask API with CSV-based storage for MVP.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

The server will run on `http://localhost:5000`

## API Endpoints

### User Management

#### Sign Up
```bash
curl -X POST http://localhost:5000/api/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "password123",
    "user_role": "customer"
  }'
```

#### Login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@demo.com",
    "password": "demo123"
  }'
```

#### Get All Profiles
```bash
curl http://localhost:5000/api/profiles
```

#### Get Profile by ID
```bash
curl http://localhost:5000/api/profiles/customer-001
```

### Job Management

#### Create Job
```bash
curl -X POST http://localhost:5000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "profileID": "customer-001",
    "jobName": "Kitchen Renovation",
    "propertyAddress": "123 Main St",
    "city": "Los Angeles",
    "customerName": "John Doe",
    "customerEmail": "customer@demo.com",
    "trade": "painting",
    "estimatedPay": "$5,000.00",
    "description": "Complete kitchen renovation",
    "scheduledTime": "2024-12-01",
    "squareFootage": "350 sqft"
  }'
```

#### Get All Jobs
```bash
curl http://localhost:5000/api/jobs
```

#### Get Jobs by Profile ID
```bash
curl http://localhost:5000/api/jobs?profileID=customer-001
```

#### Get Jobs by Status
```bash
curl http://localhost:5000/api/jobs?status=Open
```

#### Get Jobs by Assigned Contractor
```bash
curl http://localhost:5000/api/jobs?assignedContractorId=contractor-001
```

#### Get Job by ID
```bash
curl http://localhost:5000/api/jobs/{job_id}
```

#### Update Job
```bash
curl -X PUT http://localhost:5000/api/jobs/{job_id} \
  -H "Content-Type: application/json" \
  -d '{
    "status": "InProgress",
    "assignedContractorId": "contractor-001"
  }'
```

#### Assign Job to Contractor
```bash
curl -X POST http://localhost:5000/api/jobs/{job_id}/assign \
  -H "Content-Type: application/json" \
  -d '{
    "contractorId": "contractor-001"
  }'
```

#### Update Job Progress
```bash
curl -X PUT http://localhost:5000/api/jobs/{job_id} \
  -H "Content-Type: application/json" \
  -d '{
    "contractorProgress": {
      "currentStep": 3,
      "acknowledged": true,
      "lastUpdated": "2024-12-23T10:00:00"
    }
  }'
```

### Health Check
```bash
curl http://localhost:5000/api/health
```

## Demo Accounts

The following accounts are automatically created on first run:

- **Customer**: customer@demo.com / demo123
- **Contractor 1**: contractor@demo.com / demo123
- **Contractor 2**: contractor2@demo.com / demo123
- **Admin**: admin@demo.com / demo123

## CSV Files

- `profiles.csv` - Stores user profiles
- `jobs.csv` - Stores job data

