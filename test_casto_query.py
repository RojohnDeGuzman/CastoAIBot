#!/usr/bin/env python3
"""
Test Casto Query
This script tests if the knowledge base lookup is working for Casto-related queries
"""

import requests
import json

# Backend URL
BACKEND_URL = "https://casto-ai-bot.vercel.app"

def test_casto_queries():
    """Test Casto-related queries to see if knowledge base is working"""
    print("🧪 Testing Casto Queries")
    print("=" * 50)
    
    # Test 1: Simple test message (should fall back to AI)
    print("\n1️⃣ Testing simple message: 'test'")
    try:
        payload = {"message": "test"}
        response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Response received")
            data = response.json()
            print(f"   Source: {data.get('debug_info', {}).get('source', 'Unknown')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 2: Casto-related query (should use knowledge base)
    print("\n2️⃣ Testing Casto query: 'Who is Maryles Casto?'")
    try:
        payload = {"message": "Who is Maryles Casto?"}
        response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Response received")
            data = response.json()
            print(f"   Source: {data.get('debug_info', {}).get('source', 'Unknown')}")
            print(f"   Response: {data.get('response', 'No response')[:100]}...")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 3: Another Casto query
    print("\n3️⃣ Testing Casto query: 'What is Casto Travel?'")
    try:
        payload = {"message": "What is Casto Travel?"}
        response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Response received")
            data = response.json()
            print(f"   Source: {data.get('debug_info', {}).get('source', 'Unknown')}")
            print(f"   Response: {data.get('response', 'No response')[:100]}...")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

if __name__ == "__main__":
    test_casto_queries()
