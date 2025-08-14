#!/usr/bin/env python3
"""
Simple test script to verify backend functionality
Run this to test if the backend is working after disabling authentication
"""

import requests
import json

# Backend URL
BACKEND_URL = "https://casto-ai-bot.vercel.app"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check successful!")
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            print(f"API Key configured: {data.get('api_key_configured')}")
            print(f"Authentication: {data.get('authentication')}")
            print(f"Available endpoints: {list(data.get('endpoints', {}).keys())}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_test_endpoint():
    """Test the simple test endpoint"""
    print("\nTesting test endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/test", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Test endpoint successful!")
            print(f"Message: {data.get('message')}")
            return True
        else:
            print(f"❌ Test endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Test endpoint error: {e}")
        return False

def test_chat_endpoint():
    """Test the chat endpoint without authentication"""
    print("\nTesting chat endpoint...")
    try:
        payload = {
            "message": "Hello, this is a test message"
        }
        response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat endpoint successful!")
            print(f"Response: {data.get('response', 'No response')[:100]}...")
            return True
        else:
            print(f"❌ Chat endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        return False

def test_knowledge_endpoints():
    """Test the knowledge endpoints"""
    print("\nTesting knowledge endpoints...")
    
    # Test GET knowledge
    try:
        response = requests.get(f"{BACKEND_URL}/knowledge", timeout=10)
        print(f"GET knowledge status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ GET knowledge successful!")
            print(f"Knowledge entries: {len(data)}")
        else:
            print(f"❌ GET knowledge failed: {response.text}")
    except Exception as e:
        print(f"❌ GET knowledge error: {e}")
    
    # Test POST knowledge
    try:
        payload = {
            "content": "This is a test knowledge entry"
        }
        response = requests.post(f"{BACKEND_URL}/knowledge", json=payload, timeout=10)
        print(f"POST knowledge status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ POST knowledge successful!")
            print(f"Message: {data.get('message')}")
        else:
            print(f"❌ POST knowledge failed: {response.text}")
    except Exception as e:
        print(f"❌ POST knowledge error: {e}")

def main():
    """Run all tests"""
    print("🧪 Testing CASI Backend API")
    print("=" * 50)
    
    # Test basic connectivity
    health_ok = test_health_check()
    test_ok = test_test_endpoint()
    
    if not health_ok or not test_ok:
        print("\n❌ Basic connectivity tests failed. Backend may not be reachable.")
        return
    
    # Test chat functionality
    chat_ok = test_chat_endpoint()
    
    # Test knowledge endpoints
    test_knowledge_endpoints()
    
    print("\n" + "=" * 50)
    if chat_ok:
        print("🎉 All tests passed! Backend is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
