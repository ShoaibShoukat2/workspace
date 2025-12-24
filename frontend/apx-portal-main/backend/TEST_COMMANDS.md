# API Test Commands

## Setup
Make sure the Flask server is running:
```bash
cd backend
python main.py
```

## User Management Tests

### 1. Health Check
```bash
curl http://localhost:5000/api/health
```

### 2. Sign Up - Create New Customer
```bash
curl -X POST http://localhost:5000/api/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newcustomer@example.com",
    "password": "password123",
    "user_role": "customer"
  }'
```

### 3. Sign Up - Create New Contractor
```bash
curl -X POST http://localhost:5000/api/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newcontractor@example.com",
    "password": "password123",
    "user_role": "contractor"
  }'
```

### 4. Login - Customer
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@demo.com",
    "password": "demo123"
  }'
```

### 5. Login - Contractor
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "contractor@demo.com",
    "password": "demo123"
  }'
```

### 6. Get All Profiles
```bash
curl http://localhost:5000/api/profiles
```

### 7. Get Profile by ID
```bash
curl http://localhost:5000/api/profiles/customer-001
```

## Job Management Tests

### 8. Create Job (Customer creates a job)
```bash
curl -X POST http://localhost:5000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "profileID": "customer-001",
    "jobName": "Exterior House Painting",
    "propertyAddress": "892 Willow Creek Rd",
    "city": "Los Angeles",
    "customerName": "Sarah Jenkins",
    "customerEmail": "customer@demo.com",
    "trade": "painting",
    "estimatedPay": "$2,100.00",
    "description": "Paint entire exterior of house including trim and doors",
    "scheduledTime": "2024-12-25",
    "squareFootage": "2500 sqft"
  }'
```

### 9. Get All Jobs
```bash
curl http://localhost:5000/api/jobs
```

### 10. Get Jobs by Customer Profile ID
```bash
curl "http://localhost:5000/api/jobs?profileID=customer-001"
```

### 11. Get Available Jobs (Status = Open)
```bash
curl "http://localhost:5000/api/jobs?status=Open"
```

### 12. Get Job by ID (replace {job_id} with actual job ID from step 8)
```bash
curl http://localhost:5000/api/jobs/job-001
```

### 13. Assign Job to Contractor
```bash
curl -X POST http://localhost:5000/api/jobs/job-001/assign \
  -H "Content-Type: application/json" \
  -d '{
    "contractorId": "contractor-001"
  }'
```

### 14. Get Jobs Assigned to Contractor
```bash
curl "http://localhost:5000/api/jobs?assignedContractorId=contractor-001"
```

### 15. Update Job Progress
```bash
curl -X PUT http://localhost:5000/api/jobs/job-001 \
  -H "Content-Type: application/json" \
  -d '{
    "contractorProgress": {
      "currentStep": 3,
      "acknowledged": true,
      "lastUpdated": "2024-12-23T14:30:00"
    }
  }'
```

### 16. Update Job Status
```bash
curl -X PUT http://localhost:5000/api/jobs/job-001 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "InProgress",
    "materialStatus": "FM Verified"
  }'
```

### 17. Complete Job
```bash
curl -X PUT http://localhost:5000/api/jobs/job-001 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Complete"
  }'
```

## Complete Workflow Test

### Step 1: Customer creates a job
```bash
curl -X POST http://localhost:5000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "profileID": "customer-001",
    "jobName": "Bathroom Leak Repair",
    "propertyAddress": "4402 Sunset Blvd",
    "city": "Los Angeles",
    "customerName": "Sarah Jenkins",
    "customerEmail": "customer@demo.com",
    "trade": "plumbing",
    "estimatedPay": "$450.00",
    "description": "Fix leaky faucet and replace damaged pipes",
    "scheduledTime": "2024-12-24"
  }'
```

### Step 2: Contractor views available jobs
```bash
curl "http://localhost:5000/api/jobs?status=Open"
```

### Step 3: Contractor accepts/assigns job
```bash
curl -X POST http://localhost:5000/api/jobs/{job_id_from_step1}/assign \
  -H "Content-Type: application/json" \
  -d '{
    "contractorId": "contractor-001"
  }'
```

### Step 4: Contractor updates progress
```bash
curl -X PUT http://localhost:5000/api/jobs/{job_id_from_step1} \
  -H "Content-Type: application/json" \
  -d '{
    "contractorProgress": {
      "currentStep": 2,
      "acknowledged": true,
      "lastUpdated": "2024-12-23T15:00:00"
    }
  }'
```

### Step 5: View contractor's active jobs
```bash
curl "http://localhost:5000/api/jobs?assignedContractorId=contractor-001&status=InProgress"
```

