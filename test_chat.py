#!/usr/bin/env python3
"""
Test script to test the chat endpoint with knowledge base
"""

import requests
import json

def test_chat_endpoint():
    """Test the chat endpoint with a Casto question"""
    url = "http://localhost:9000/chat"
    
    # Test data - asking about Marc Casto (should use knowledge base)
    test_data = {
        "message": "Who is Marc Casto?",
        "access_token": "test_token"  # This will fail auth, but let's see the response
    }
    
    try:
        print("Testing chat endpoint with question: 'Who is Marc Casto?'")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, timeout=10)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ Success! Response: {json.dumps(response_data, indent=2)}")
        else:
            print(f"❌ Error Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_chat_without_auth():
    """Test the chat endpoint without authentication to see the error"""
    url = "http://localhost:9000/chat"
    
    test_data = {
        "message": "Who is Marc Casto?"
    }
    
    try:
        print("\nTesting chat endpoint without authentication...")
        response = requests.post(url, json=test_data, timeout=10)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("CHAT ENDPOINT TEST")
    print("=" * 60)
    
    test_chat_without_auth()
    test_chat_endpoint()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
