"""
CSV-based data layer for testing
Simple file-based storage instead of database
"""
import csv
import json
import os
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from pathlib import Path

# Create data directory
DATA_DIR = Path("app/data/csv_files")
DATA_DIR.mkdir(parents=True, exist_ok=True)

class CSVDataManager:
    """Manage CSV data files"""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self._ensure_csv_files()
    
    def _ensure_csv_files(self):
        """Create CSV files if they don't exist"""
        csv_files = {
            'users.csv': ['id', 'email', 'password_hash', 'full_name', 'role', 'is_active', 'created_at'],
            'jobs.csv': ['id', 'job_number', 'customer_name', 'property_address', 'status', 'trade', 'estimated_cost', 'actual_cost', 'assigned_contractor_id', 'created_at'],
            'contractors.csv': ['id', 'user_id', 'full_name', 'email', 'phone', 'trade', 'status', 'compliance_status', 'created_at'],
            'payouts.csv': ['id', 'contractor_id', 'amount', 'status', 'job_id', 'created_at', 'paid_date'],
            'compliance.csv': ['id', 'contractor_id', 'document_type', 'status', 'expiry_date', 'created_at'],
            'disputes.csv': ['id', 'job_id', 'contractor_id', 'customer_id', 'status', 'description', 'created_at'],
            'investors.csv': ['id', 'user_id', 'full_name', 'email', 'total_investment', 'total_returns', 'status', 'created_at'],
            'site_visits.csv': ['id', 'job_id', 'fm_id', 'visit_date', 'status', 'notes', 'created_at'],
            'notifications.csv': ['id', 'user_id', 'title', 'message', 'type', 'is_read', 'created_at']
        }
        
        for filename, headers in csv_files.items():
            filepath = self.data_dir / filename
            if not filepath.exists():
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    
                    # Add some sample data
                    if filename == 'users.csv':
                        sample_users = [
                            [1, 'admin@apex.inc', '$2b$12$hash1', 'Admin User', 'ADMIN', True, '2024-01-01'],
                            [2, 'contractor@apex.inc', '$2b$12$hash2', 'John Contractor', 'CONTRACTOR', True, '2024-01-01'],
                            [3, 'customer@apex.inc', '$2b$12$hash3', 'Jane Customer', 'CUSTOMER', True, '2024-01-01'],
                            [4, 'investor@apex.inc', '$2b$12$hash4', 'Bob Investor', 'INVESTOR', True, '2024-01-01'],
                            [5, 'fm@apex.inc', '$2b$12$hash5', 'Alice FM', 'FM', True, '2024-01-01']
                        ]
                        writer.writerows(sample_users)
                    
                    elif filename == 'jobs.csv':
                        sample_jobs = [
                            [101, 'JOB-20241201-001', 'John Smith', '123 Main St', 'InProgress', 'Painting', 5000, 4800, 2, '2024-12-01'],
                            [102, 'JOB-20241202-002', 'Jane Doe', '456 Oak Ave', 'Open', 'Plumbing', 3000, None, None, '2024-12-02'],
                            [103, 'JOB-20241203-003', 'Bob Wilson', '789 Pine St', 'Complete', 'Electrical', 4000, 3900, 2, '2024-12-03']
                        ]
                        writer.writerows(sample_jobs)
                    
                    elif filename == 'contractors.csv':
                        sample_contractors = [
                            [1, 2, 'John Contractor', 'contractor@apex.inc', '555-0101', 'Painting', 'ACTIVE', 'active', '2024-01-01'],
                            [2, 6, 'Mike Builder', 'mike@apex.inc', '555-0102', 'General', 'ACTIVE', 'active', '2024-01-01']
                        ]
                        writer.writerows(sample_contractors)
                    
                    elif filename == 'payouts.csv':
                        sample_payouts = [
                            [1, 1, 1200.00, 'COMPLETED', 101, '2024-12-01', '2024-12-05'],
                            [2, 1, 950.00, 'PENDING', 103, '2024-12-03', None]
                        ]
                        writer.writerows(sample_payouts)
    
    def read_csv(self, filename: str) -> List[Dict[str, Any]]:
        """Read CSV file and return as list of dictionaries"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            return []
        
        with open(filepath, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    def write_csv(self, filename: str, data: List[Dict[str, Any]]):
        """Write data to CSV file"""
        if not data:
            return
        
        filepath = self.data_dir / filename
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    
    def append_csv(self, filename: str, row: Dict[str, Any]):
        """Append a row to CSV file"""
        filepath = self.data_dir / filename
        with open(filepath, 'a', newline='', encoding='utf-8') as f:
            if filepath.stat().st_size == 0:
                # File is empty, write header
                writer = csv.DictWriter(f, fieldnames=row.keys())
                writer.writeheader()
            else:
                writer = csv.DictWriter(f, fieldnames=row.keys())
            writer.writerow(row)
    
    def get_next_id(self, filename: str) -> int:
        """Get next available ID for a CSV file"""
        data = self.read_csv(filename)
        if not data:
            return 1
        
        max_id = max(int(row.get('id', 0)) for row in data)
        return max_id + 1

# Global instance
csv_manager = CSVDataManager()

# Helper functions for common operations
def get_users() -> List[Dict[str, Any]]:
    """Get all users"""
    return csv_manager.read_csv('users.csv')

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    users = get_users()
    for user in users:
        if user['email'].lower() == email.lower():
            return user
    return None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    users = get_users()
    for user in users:
        if int(user['id']) == user_id:
            return user
    return None

def get_jobs(status: Optional[str] = None, contractor_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get jobs with optional filtering"""
    jobs = csv_manager.read_csv('jobs.csv')
    
    if status:
        jobs = [job for job in jobs if job['status'] == status]
    
    if contractor_id:
        jobs = [job for job in jobs if job['assigned_contractor_id'] and int(job['assigned_contractor_id']) == contractor_id]
    
    return jobs

def get_contractors(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get contractors with optional filtering"""
    contractors = csv_manager.read_csv('contractors.csv')
    
    if status:
        contractors = [c for c in contractors if c['status'] == status]
    
    return contractors

def get_payouts(status: Optional[str] = None, contractor_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get payouts with optional filtering"""
    payouts = csv_manager.read_csv('payouts.csv')
    
    if status:
        payouts = [p for p in payouts if p['status'] == status]
    
    if contractor_id:
        payouts = [p for p in payouts if int(p['contractor_id']) == contractor_id]
    
    return payouts

def get_disputes(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get disputes with optional filtering"""
    disputes = csv_manager.read_csv('disputes.csv')
    
    if status:
        disputes = [d for d in disputes if d['status'] == status]
    
    return disputes

def get_investors() -> List[Dict[str, Any]]:
    """Get all investors"""
    return csv_manager.read_csv('investors.csv')

def get_site_visits(fm_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get site visits with optional filtering"""
    visits = csv_manager.read_csv('site_visits.csv')
    
    if fm_id:
        visits = [v for v in visits if int(v['fm_id']) == fm_id]
    
    return visits

def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create new user"""
    user_data['id'] = csv_manager.get_next_id('users.csv')
    user_data['created_at'] = datetime.now().isoformat()
    csv_manager.append_csv('users.csv', user_data)
    return user_data

def update_payout_status(payout_id: int, status: str, paid_date: Optional[str] = None):
    """Update payout status"""
    payouts = csv_manager.read_csv('payouts.csv')
    
    for payout in payouts:
        if int(payout['id']) == payout_id:
            payout['status'] = status
            if paid_date:
                payout['paid_date'] = paid_date
            break
    
    csv_manager.write_csv('payouts.csv', payouts)

def get_dashboard_stats() -> Dict[str, Any]:
    """Get dashboard statistics"""
    jobs = get_jobs()
    contractors = get_contractors()
    payouts = get_payouts()
    disputes = get_disputes()
    
    return {
        'total_jobs': len(jobs),
        'active_jobs': len([j for j in jobs if j['status'] in ['Open', 'InProgress']]),
        'completed_jobs': len([j for j in jobs if j['status'] == 'Complete']),
        'total_contractors': len(contractors),
        'active_contractors': len([c for c in contractors if c['status'] == 'ACTIVE']),
        'pending_payouts': len([p for p in payouts if p['status'] == 'PENDING']),
        'pending_payouts_amount': sum(float(p['amount']) for p in payouts if p['status'] == 'PENDING'),
        'pending_disputes': len([d for d in disputes if d['status'] == 'Open']),
        'blocked_contractors': len([c for c in contractors if c['compliance_status'] == 'blocked'])
    }