#!/usr/bin/env python3
"""
Test script for the chat endpoint
"""

import requests
import json

def test_chat_endpoint():
    """Test the chat endpoint with Maryle Casto query"""
    
    # Your working domain
    base_url = "https://casto-ai-bot.vercel.app"
    
    print("🧪 Testing Chat Endpoint")
    print("=" * 50)
    
    # Test data
    test_data = {
        "message": "who is Maryle Casto?",  # Missing 's' - should trigger fuzzy matching
        "access_token": "test"  # This might fail auth but let's see
    }
    
    print(f"Testing: {base_url}/chat")
    print(f"Query: '{test_data['message']}'")
    
    try:
        # Make POST request to chat endpoint
        response = requests.post(f"{base_url}/chat", json=test_data, timeout=15)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            
            print(f"\n✅ SUCCESS! Response received:")
            print(f"Response: {response_text}")
            
            # Check if it mentions Casto Travel Philippines (correct) vs fashion designer (incorrect)
            if 'casto travel philippines' in response_text.lower():
                print("\n🎯 PERFECT! Response mentions Casto Travel Philippines (using KB!)")
                return True
            elif 'fashion' in response_text.lower() or 'designer' in response_text.lower():
                print("\n❌ PROBLEM! Response mentions fashion designer (still using AI training data)")
                return False
            else:
                print("\n⚠️ Response doesn't clearly indicate source")
                return False
                
        else:
            print(f"\n❌ Chat endpoint failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error testing chat endpoint: {e}")
        return False

if __name__ == "__main__":
    success = test_chat_endpoint()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS! Knowledge base first approach is working!")
    else:
        print("❌ ISSUE! Need to investigate further")
    print("=" * 50)
