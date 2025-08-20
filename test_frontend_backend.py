#!/usr/bin/env python3
"""
Test Frontend-Backend Communication
This script tests the exact same request format that your frontend uses
"""

import requests
import json
from datetime import datetime

# Backend URL (same as your frontend)
BACKEND_URL = "https://casto-ai-bot.vercel.app"

def test_frontend_request():
    """Test the exact request format your frontend uses"""
    print("🧪 Testing Frontend-Backend Communication")
    print("=" * 60)
    print(f"🌐 Backend: {BACKEND_URL}")
    print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test 1: Request without access token (anonymous mode)
    print("\n📤 Test 1: Anonymous Request (no access token)")
    print("-" * 40)
    
    payload1 = {"message": "Who is Maryle Casto?"}
    print(f"📤 Sending: {json.dumps(payload1, indent=2)}")
    
    try:
        response1 = requests.post(f"{BACKEND_URL}/chat", json=payload1, timeout=30)
        print(f"📥 Response Status: {response1.status_code}")
        print(f"📥 Response Headers: {dict(response1.headers)}")
        
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"✅ Success! Response:")
            print(f"   Response: {data1.get('response', 'No response')[:100]}...")
            
            if 'debug_messages' in data1:
                print(f"   Debug Messages: {len(data1['debug_messages'])} found")
                for i, msg in enumerate(data1['debug_messages'], 1):
                    print(f"     {i}. {msg}")
            else:
                print("   ⚠️ No debug_messages in response")
                
            if 'debug_info' in data1:
                print(f"   Debug Info: {data1['debug_info']}")
            else:
                print("   ⚠️ No debug_info in response")
        else:
            print(f"❌ Error Response: {response1.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 2: Request with fake access token
    print("\n📤 Test 2: Request with access token")
    print("-" * 40)
    
    payload2 = {
        "message": "Test debug - Who is Maryle Casto?",
        "access_token": "test_token_123"
    }
    print(f"📤 Sending: {json.dumps(payload2, indent=2)}")
    
    try:
        response2 = requests.post(f"{BACKEND_URL}/chat", json=payload2, timeout=30)
        print(f"📥 Response Status: {response2.status_code}")
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"✅ Success! Response:")
            print(f"   Response: {data2.get('response', 'No response')[:100]}...")
            
            if 'debug_messages' in data2:
                print(f"   Debug Messages: {len(data2['debug_messages'])} found")
                for i, msg in enumerate(data2['debug_messages'], 1):
                    print(f"     {i}. {msg}")
            else:
                print("   ⚠️ No debug_messages in response")
                
            if 'debug_info' in data2:
                print(f"   Debug Info: {data2['debug_info']}")
            else:
                print("   ⚠️ No debug_info in response")
        else:
            print(f"❌ Error Response: {response2.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 3: Check debug endpoints
    print("\n📤 Test 3: Debug Endpoints")
    print("-" * 40)
    
    debug_endpoints = [
        "/debug/status",
        "/debug/format", 
        "/test/kb"
    ]
    
    for endpoint in debug_endpoints:
        try:
            print(f"🔍 Testing {endpoint}...")
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        print()
    
    print("=" * 60)
    print("🎯 Test Complete!")
    print("💡 If you see debug messages above, the backend is working!")
    print("💡 If not, there might be an issue with the backend code.")

if __name__ == "__main__":
    test_frontend_request()
