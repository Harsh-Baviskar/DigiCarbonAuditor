#!/usr/bin/env python3
"""
Quick test script to verify Google Drive login endpoints
Run this after starting the Flask backend
"""

import requests
import json

API_BASE = "http://localhost:5000"

def test_login_endpoint():
    """Test GET /google-drive/login endpoint"""
    print("\n=== Testing Login Endpoint ===")
    try:
        response = requests.get(f"{API_BASE}/google-drive/login")
        print(f"Status: {response.status_code}")
        if response.ok:
            data = response.json()
            print(f"✓ Auth URL generated")
            print(f"URL: {data.get('auth_url', 'N/A')[:80]}...")
        else:
            print(f"✗ Error: {response.text}")
    except Exception as e:
        print(f"✗ Connection error: {e}")

def test_session_info():
    """Test GET /google-drive/session-info endpoint"""
    print("\n=== Testing Session Info Endpoint ===")
    try:
        response = requests.get(f"{API_BASE}/google-drive/session-info")
        print(f"Status: {response.status_code}")
        data = response.json()
        if data.get('authenticated'):
            print(f"✓ Authenticated: {data.get('user_info')}")
        else:
            print(f"✓ Not authenticated (expected): {data.get('message')}")
    except Exception as e:
        print(f"✗ Connection error: {e}")

def test_scan_without_auth():
    """Test POST /google-drive/scan (should fail without auth)"""
    print("\n=== Testing Scan Without Authentication ===")
    try:
        response = requests.post(
            f"{API_BASE}/google-drive/scan",
            json={"region": "IN-WE"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print(f"✓ Correctly requires authentication")
            data = response.json()
            print(f"Message: {data.get('error')}")
        else:
            print(f"✗ Unexpected response: {response.text}")
    except Exception as e:
        print(f"✗ Connection error: {e}")

def main():
    print("=" * 50)
    print("Google Drive Login System - Backend Tests")
    print("=" * 50)
    
    test_login_endpoint()
    test_session_info()
    test_scan_without_auth()
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("1. Login endpoint should return auth URL")
    print("2. Session info should show not authenticated")
    print("3. Scan should require authentication (401 error)")
    print("=" * 50)

if __name__ == "__main__":
    main()
