#!/usr/bin/env python3
"""
Test script to verify registration API endpoint
"""
import requests
import json

# Test data
test_data = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpassword123",
    "password2": "testpassword123",
    "role": "customer"
}

# API endpoint
url = "http://localhost:8000/api/auth/register/"

try:
    print("Testing registration endpoint...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    
    response = requests.post(url, json=test_data, headers={
        'Content-Type': 'application/json'
    })
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    try:
        response_data = response.json()
        print(f"Response Data: {json.dumps(response_data, indent=2)}")
    except:
        print(f"Response Text: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("Error: Could not connect to the server. Make sure Django is running on localhost:8000")
except Exception as e:
    print(f"Error: {e}")