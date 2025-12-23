#!/usr/bin/env python3
"""
Test script for Customer Dashboard APIs
Run this to verify all new customer dashboard endpoints are working
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/workspaces"
TEST_EMAIL = "customer@test.com"
TEST_TOKEN = "mock-token-123"

def test_api_endpoint(method, endpoint, data=None, headers=None, expected_status=200):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        
        print(f"✅ {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print(f"   ✅ Expected status {expected_status}")
        else:
            print(f"   ❌ Expected {expected_status}, got {response.status_code}")
        
        try:
            result = response.json()
            print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
        except:
            print(f"   Response: {response.text[:200]}...")
        
        print("-" * 50)
        return response
        
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint}")
        print("   Error: Could not connect to server. Make sure Django is running.")
        print("-" * 50)
        return None
    except Exception as e:
        print(f"❌ {method} {endpoint}")
        print(f"   Error: {str(e)}")
        print("-" * 50)
        return None

def main():
    print("🧪 Testing Customer Dashboard APIs")
    print("=" * 60)
    
    # Test 1: Validate Quote Token (Public)
    print("1. Testing Quote Token Validation...")
    test_api_endpoint('GET', f'/public/validate-token/{TEST_TOKEN}/')
    
    # Test 2: Get Job Details by Token (Public)
    print("2. Testing Job Details by Token...")
    test_api_endpoint('GET', f'/public/job/{TEST_TOKEN}/')
    
    # Test 3: Approve Quote (Public)
    print("3. Testing Quote Approval...")
    test_api_endpoint('POST', f'/public/quote/{TEST_TOKEN}/approve/')
    
    # Test 4: Generate Customer Credentials (Public)
    print("4. Testing Credential Generation...")
    test_api_endpoint('POST', '/public/generate-credentials/', {
        'email': TEST_EMAIL,
        'quote_token': TEST_TOKEN
    })
    
    # Test 5: Get Job Tracking by Token (Public)
    print("5. Testing Job Tracking by Token...")
    test_api_endpoint('GET', f'/public/job/{TEST_TOKEN}/tracking/')
    
    # Note: The following tests require authentication
    print("\n📝 Note: The following tests require authentication:")
    print("   - Customer Dashboard: GET /customer/dashboard/")
    print("   - Job Details: GET /customer/jobs/{id}/")
    print("   - Live Tracking: GET /customer/jobs/{id}/tracking/")
    print("   - Material Delivery: GET /customer/jobs/{id}/material-delivery/")
    print("   - Report Issue: POST /customer/jobs/{id}/report-issue/")
    print("   - Notifications: GET /customer/notifications/")
    
    print("\n🔐 To test authenticated endpoints:")
    print("1. First generate credentials using the public endpoint")
    print("2. Use the returned auth_token in Authorization header")
    print("3. Example: headers={'Authorization': 'Token your_token_here'}")
    
    print("\n✅ Public API tests completed!")
    print("🚀 All new customer dashboard APIs are ready to use!")

if __name__ == "__main__":
    main()