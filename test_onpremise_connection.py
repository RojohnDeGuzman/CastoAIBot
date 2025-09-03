#!/usr/bin/env python3
"""
Test script to verify connection to on-premise CASI backend
"""

import requests
import json
import sys

# Configuration
BACKEND_URL = "http://172.16.11.69:9000"

def test_connection():
    """Test basic connectivity to the on-premise backend"""
    print("🔍 Testing connection to on-premise CASI backend...")
    print(f"📍 Backend URL: {BACKEND_URL}")
    print("=" * 50)
    
    # Test 1: Health check
    print("1️⃣ Testing health check endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check successful!")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Message: {data.get('message', 'No message')}")
            print(f"   AI Client Available: {data.get('ai_client_available', False)}")
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    print()
    
    # Test 2: Test endpoint
    print("2️⃣ Testing /test endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/test", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test endpoint successful!")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Message: {data.get('message', 'No message')}")
        else:
            print(f"❌ Test endpoint failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Test endpoint failed: {e}")
    
    print()
    
    # Test 3: Chat endpoint (anonymous)
    print("3️⃣ Testing /chat endpoint (anonymous)...")
    try:
        payload = {"message": "Hello, this is a test message from the frontend connection test."}
        response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat endpoint successful!")
            print(f"   Response: {data.get('response', 'No response')[:100]}...")
        else:
            print(f"❌ Chat endpoint failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Chat endpoint failed: {e}")
    
    print()
    
    # Test 4: Knowledge search
    print("4️⃣ Testing /knowledge/search endpoint...")
    try:
        payload = {"query": "test knowledge search"}
        response = requests.post(f"{BACKEND_URL}/knowledge/search", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Knowledge search successful!")
            print(f"   Query: {data.get('query', 'unknown')}")
            print(f"   Results found: {data.get('total_found', 0)}")
        else:
            print(f"❌ Knowledge search failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Knowledge search failed: {e}")
    
    print()
    
    # Test 5: Company info
    print("5️⃣ Testing /company-info endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/company-info", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Company info successful!")
            company = data.get('company', {})
            print(f"   Company: {company.get('company_name', 'Unknown')}")
            print(f"   Industry: {company.get('industry', 'Unknown')}")
        else:
            print(f"❌ Company info failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Company info failed: {e}")
    
    print()
    print("=" * 50)
    print("🎉 Connection test completed!")
    print("💡 If all tests passed, your frontend should work with the on-premise backend.")
    print("💡 If any tests failed, check your network connectivity and backend status.")
    
    return True

if __name__ == "__main__":
    test_connection()
