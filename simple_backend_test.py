#!/usr/bin/env python3
"""
Simple Backend Test
This script tests the backend with minimal requests to identify the exact issue
"""

import requests
import json

# Backend URL
BACKEND_URL = "https://casto-ai-bot.vercel.app"

def test_simple_endpoints():
    """Test simple endpoints to see what's working"""
    print("🧪 Simple Backend Test")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    print("\n1️⃣ Testing basic connectivity...")
    try:
        response = requests.get(f"{BACKEND_URL}/debug/status", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ /debug/status working")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 2: Test KB endpoint
    print("\n2️⃣ Testing knowledge base endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/test/kb", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ /test/kb working")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 3: Test chat endpoint with minimal data
    print("\n3️⃣ Testing chat endpoint with minimal data...")
    try:
        payload = {"message": "test"}
        response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ /chat working")
            data = response.json()
            print(f"   Response: {data.get('response', 'No response')[:100]}...")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 4: Check if it's a deployment issue
    print("\n4️⃣ Checking deployment status...")
    try:
        # Try to get any response from the root
        response = requests.get(BACKEND_URL, timeout=10)
        print(f"   Root Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Root endpoint working")
        else:
            print(f"   Root Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Root failed: {e}")

if __name__ == "__main__":
    test_simple_endpoints()
