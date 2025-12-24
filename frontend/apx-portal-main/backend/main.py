from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# CSV file paths
PROFILES_CSV = 'profiles.csv'
JOBS_CSV = 'jobs.csv'

# Ensure CSV files exist with headers
def init_csv_files():
    """Initialize CSV files with headers if they don't exist"""
    
    # Profiles CSV
    if not os.path.exists(PROFILES_CSV):
        with open(PROFILES_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['profileID', 'email', 'password', 'user_role'])
    
    # Jobs CSV
    if not os.path.exists(JOBS_CSV):
        with open(JOBS_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'jobID', 'profileID', 'jobName', 'propertyAddress', 'city', 
                'customerName', 'customerEmail', 'trade', 'estimatedPay', 
                'description', 'scheduledTime', 'squareFootage', 'status',
                'assignedContractorId', 'materialStatus', 'createdAt',
                'contractorProgress_currentStep', 'contractorProgress_acknowledged', 
                'contractorProgress_lastUpdated'
            ])

def read_profiles() -> List[Dict]:
    """Read all profiles from CSV"""
    profiles = []
    if os.path.exists(PROFILES_CSV):
        with open(PROFILES_CSV, 'r', newline='') as f:
            reader = csv.DictReader(f)
            profiles = list(reader)
    return profiles

def write_profiles(profiles: List[Dict]):
    """Write profiles to CSV"""
    if not profiles:
        return
    with open(PROFILES_CSV, 'w', newline='') as f:
        fieldnames = ['profileID', 'email', 'password', 'user_role']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(profiles)

def read_jobs() -> List[Dict]:
    """Read all jobs from CSV"""
    jobs = []
    if os.path.exists(JOBS_CSV):
        with open(JOBS_CSV, 'r', newline='') as f:
            reader = csv.DictReader(f)
            jobs = list(reader)
    return jobs

def write_jobs(jobs: List[Dict]):
    """Write jobs to CSV"""
    if not jobs:
        return
    fieldnames = [
        'jobID', 'profileID', 'jobName', 'propertyAddress', 'city', 
        'customerName', 'customerEmail', 'trade', 'estimatedPay', 
        'description', 'scheduledTime', 'squareFootage', 'status',
        'assignedContractorId', 'materialStatus', 'createdAt',
        'contractorProgress_currentStep', 'contractorProgress_acknowledged', 
        'contractorProgress_lastUpdated'
    ]
    with open(JOBS_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(jobs)

# Initialize CSV files on startup
init_csv_files()

# ==================== USER MANAGEMENT ====================

@app.route('/api/signup', methods=['POST'])
def signup():
    """Create a new user profile"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('email') or not data.get('password') or not data.get('user_role'):
            return jsonify({'error': 'Missing required fields: email, password, user_role'}), 400
        
        # Check if email already exists
        profiles = read_profiles()
        if any(p['email'] == data['email'] for p in profiles):
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new profile
        new_profile = {
            'profileID': str(uuid.uuid4()),
            'email': data['email'],
            'password': data['password'],  # No hashing for MVP
            'user_role': data['user_role']
        }
        
        profiles.append(new_profile)
        write_profiles(profiles)
        
        return jsonify({
            'message': 'User created successfully',
            'profileID': new_profile['profileID'],
            'email': new_profile['email'],
            'user_role': new_profile['user_role']
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    """Get all profiles"""
    try:
        profiles = read_profiles()
        # Don't return passwords in response
        for profile in profiles:
            profile.pop('password', None)
        return jsonify(profiles), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles/<profile_id>', methods=['GET'])
def get_profile(profile_id):
    """Get a specific profile by ID"""
    try:
        profiles = read_profiles()
        profile = next((p for p in profiles if p['profileID'] == profile_id), None)
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        profile.pop('password', None)
        return jsonify(profile), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Simple login - just verify credentials (no security for MVP)"""
    try:
        data = request.json
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing email or password'}), 400
        
        profiles = read_profiles()
        profile = next((p for p in profiles if p['email'] == data['email'] and p['password'] == data['password']), None)
        
        if not profile:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        profile.pop('password', None)
        return jsonify({
            'message': 'Login successful',
            'profile': profile
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== JOB MANAGEMENT ====================

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get all jobs, optionally filtered by profileID or status"""
    try:
        jobs = read_jobs()
        profile_id = request.args.get('profileID')
        status = request.args.get('status')
        assigned_contractor = request.args.get('assignedContractorId')
        
        # Filter jobs
        if profile_id:
            jobs = [j for j in jobs if j.get('profileID') == profile_id]
        if status:
            jobs = [j for j in jobs if j.get('status') == status]
        if assigned_contractor:
            jobs = [j for j in jobs if j.get('assignedContractorId') == assigned_contractor]
        
        return jsonify(jobs), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs', methods=['POST'])
def create_job():
    """Create a new job"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['profileID', 'jobName', 'propertyAddress', 'city', 
                          'customerName', 'customerEmail', 'trade', 'estimatedPay', 'description']
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
        
        # Create new job
        new_job = {
            'jobID': str(uuid.uuid4()),
            'profileID': data['profileID'],
            'jobName': data['jobName'],
            'propertyAddress': data['propertyAddress'],
            'city': data['city'],
            'customerName': data['customerName'],
            'customerEmail': data['customerEmail'],
            'trade': data['trade'],
            'estimatedPay': data['estimatedPay'],
            'description': data['description'],
            'scheduledTime': data.get('scheduledTime', ''),
            'squareFootage': data.get('squareFootage', ''),
            'status': 'Open',
            'assignedContractorId': data.get('assignedContractorId', ''),
            'materialStatus': data.get('materialStatus', ''),
            'createdAt': datetime.now().isoformat(),
            'contractorProgress_currentStep': '',
            'contractorProgress_acknowledged': '',
            'contractorProgress_lastUpdated': ''
        }
        
        jobs = read_jobs()
        jobs.append(new_job)
        write_jobs(jobs)
        
        return jsonify({
            'message': 'Job created successfully',
            'job': new_job
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get a specific job by ID"""
    try:
        jobs = read_jobs()
        job = next((j for j in jobs if j['jobID'] == job_id), None)
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify(job), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_id>', methods=['PUT'])
def update_job(job_id):
    """Update a job"""
    try:
        data = request.json
        jobs = read_jobs()
        
        job_index = next((i for i, j in enumerate(jobs) if j['jobID'] == job_id), None)
        if job_index is None:
            return jsonify({'error': 'Job not found'}), 404
        
        # Update job fields
        for key, value in data.items():
            if key == 'contractorProgress':
                # Handle nested contractorProgress object
                if isinstance(value, dict):
                    jobs[job_index][f'contractorProgress_currentStep'] = str(value.get('currentStep', ''))
                    jobs[job_index][f'contractorProgress_acknowledged'] = str(value.get('acknowledged', ''))
                    jobs[job_index][f'contractorProgress_lastUpdated'] = value.get('lastUpdated', '')
            else:
                jobs[job_index][key] = value
        
        write_jobs(jobs)
        
        return jsonify({
            'message': 'Job updated successfully',
            'job': jobs[job_index]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_id>/assign', methods=['POST'])
def assign_job(job_id):
    """Assign a job to a contractor"""
    try:
        data = request.json
        contractor_id = data.get('contractorId')
        
        if not contractor_id:
            return jsonify({'error': 'Missing contractorId'}), 400
        
        jobs = read_jobs()
        job_index = next((i for i, j in enumerate(jobs) if j['jobID'] == job_id), None)
        
        if job_index is None:
            return jsonify({'error': 'Job not found'}), 404
        
        jobs[job_index]['assignedContractorId'] = str(contractor_id)
        jobs[job_index]['status'] = 'InProgress'
        jobs[job_index]['contractorProgress_currentStep'] = '1'
        jobs[job_index]['contractorProgress_acknowledged'] = 'False'
        jobs[job_index]['contractorProgress_lastUpdated'] = datetime.now().isoformat()
        
        write_jobs(jobs)
        
        return jsonify({
            'message': 'Job assigned successfully',
            'job': jobs[job_index]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'API is running'}), 200

if __name__ == '__main__':
    # Seed demo data on first run
    profiles = read_profiles()
    if len(profiles) == 0:
        print("Seeding demo profiles...")
        demo_profiles = [
            {
                'profileID': 'customer-001',
                'email': 'customer@demo.com',
                'password': 'demo123',
                'user_role': 'customer'
            },
            {
                'profileID': 'contractor-001',
                'email': 'contractor@demo.com',
                'password': 'demo123',
                'user_role': 'contractor'
            },
            {
                'profileID': 'contractor-002',
                'email': 'contractor2@demo.com',
                'password': 'demo123',
                'user_role': 'contractor'
            },
            {
                'profileID': 'admin-001',
                'email': 'admin@demo.com',
                'password': 'demo123',
                'user_role': 'admin'
            }
        ]
        write_profiles(demo_profiles)
        print("Demo profiles created!")
    
    app.run(debug=True, host='0.0.0.0', port=5001)

