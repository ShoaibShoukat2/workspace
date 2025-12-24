"""
Utility functions and helpers
"""
import secrets
import string
from datetime import datetime
from typing import Optional
from fastapi import Request


def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    # Check for forwarded IP first (for reverse proxies)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to client host
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """Get user agent from request"""
    return request.headers.get("User-Agent", "unknown")


def generate_job_number() -> str:
    """Generate unique job number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = ''.join(secrets.choice(string.digits) for _ in range(4))
    return f"JOB-{timestamp}-{random_suffix}"


def generate_estimate_number() -> str:
    """Generate unique estimate number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = ''.join(secrets.choice(string.digits) for _ in range(4))
    return f"EST-{timestamp}-{random_suffix}"


def generate_payout_number() -> str:
    """Generate unique payout number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = ''.join(secrets.choice(string.digits) for _ in range(4))
    return f"PAY-{timestamp}-{random_suffix}"


def generate_dispute_reference() -> str:
    """Generate unique dispute reference number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    random_suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    return f"DISPUTE-{timestamp}-{random_suffix}"


def generate_magic_token() -> str:
    """Generate secure magic token for customer access"""
    return secrets.token_urlsafe(32)


def format_currency(amount: Optional[float]) -> str:
    """Format currency amount"""
    if amount is None:
        return "$0.00"
    return f"${amount:,.2f}"


def format_phone_number(phone: Optional[str]) -> Optional[str]:
    """Format phone number to standard format"""
    if not phone:
        return None
    
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # Format as (XXX) XXX-XXXX if 10 digits
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    
    return phone  # Return original if can't format


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in miles"""
    import math
    
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in miles
    r = 3956
    
    return c * r


def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
    return re.match(pattern, email) is not None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    import re
    # Remove or replace unsafe characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    return filename


def generate_file_path(job_id: int, file_type: str, filename: str) -> str:
    """Generate file path for uploads"""
    sanitized_filename = sanitize_filename(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"uploads/jobs/{job_id}/{file_type}/{timestamp}_{sanitized_filename}"


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return filename.split('.')[-1].lower() if '.' in filename else ''


def is_image_file(filename: str) -> bool:
    """Check if file is an image"""
    image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
    return get_file_extension(filename) in image_extensions


def is_document_file(filename: str) -> bool:
    """Check if file is a document"""
    document_extensions = {'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt'}
    return get_file_extension(filename) in document_extensions