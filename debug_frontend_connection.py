#!/usr/bin/env python3
"""
Debug Frontend Connection
This script tests the exact same connection method your frontend uses
"""

import requests
import json
import time

# Backend URL (same as your frontend)
BACKEND_URL = "https://casto-ai-bot.vercel.app"

def test_frontend_connection():
    """Test the exact connection method your frontend uses"""
    print("🔍 Debugging Frontend Connection")
    print("=" * 50)
    
    # Test 1: Test the exact endpoint your frontend hits
    print("\n1️⃣ Testing frontend endpoint...")
    try:
        # This is what your frontend does - test connectivity first
        response = requests.post(f"{BACKEND_URL}/chat", json={"message": "test"}, timeout=8)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Frontend endpoint working")
        elif response.status_code == 500:
            print("   ⚠️ Backend error (but connection works)")
            print(f"   Error: {response.text}")
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Connection Error: {e}")
    except requests.exceptions.Timeout as e:
        print(f"   ❌ Timeout Error: {e}")
    except Exception as e:
        print(f"   ❌ Other Error: {e}")
    
    # Test 2: Test with different timeout (your frontend uses 8 seconds)
    print("\n2️⃣ Testing with frontend timeout (8 seconds)...")
    try:
        response = requests.post(f"{BACKEND_URL}/chat", json={"message": "test"}, timeout=8)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Connection with 8s timeout works")
        else:
            print(f"   ❌ Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Test the exact request format your frontend sends
    print("\n3️⃣ Testing exact frontend request format...")
    try:
        # Mimic your frontend exactly
        payload = {"message": "test"}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(
            f"{BACKEND_URL}/chat", 
            json=payload, 
            headers=headers,
            timeout=8
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Exact frontend format works")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Check if it's a specific message issue
    print("\n4️⃣ Testing with Casto query (should work)...")
    try:
        payload = {"message": "Who is Maryles Casto?"}
        response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=8)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Casto query works")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_frontend_connection()
