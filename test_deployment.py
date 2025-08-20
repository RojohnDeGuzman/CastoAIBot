#!/usr/bin/env python3
"""
Test script for the new Vercel deployment
"""

import requests
import json

def test_new_deployment():
    """Test the new deployment with the knowledge base first approach"""
    
    # Your new Vercel URL
    base_url = "https://casto-ai-nj67nc4kx-rojohn-michael-de-guzmans-projects-07181284.vercel.app"
    
    print("🧪 Testing New Vercel Deployment")
    print("=" * 50)
    
    # Test 1: Knowledge Base Endpoint
    print("\n1️⃣ Testing Knowledge Base Endpoint...")
    try:
        response = requests.get(f"{base_url}/test/kb", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Knowledge Base Test Successful!")
            print(f"Entries Count: {data.get('knowledge_base_test', {}).get('entries_count', 'Unknown')}")
            print(f"Test Query: {data.get('knowledge_base_test', {}).get('test_query', 'Unknown')}")
            print(f"Test Result Found: {data.get('knowledge_base_test', {}).get('test_result_found', 'Unknown')}")
            
            if data.get('knowledge_base_test', {}).get('test_result_found'):
                print("🎯 Maryles Casto query found in knowledge base!")
            else:
                print("❌ Maryles Casto query NOT found in knowledge base")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing KB endpoint: {e}")
    
    # Test 2: Chat Endpoint (without auth for now)
    print("\n2️⃣ Testing Chat Endpoint...")
    try:
        test_data = {
            "message": "who is Maryle Casto?",
            "access_token": "test"  # This might fail auth but let's see
        }
        
        response = requests.post(f"{base_url}/chat", json=test_data, timeout=15)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:300]}...")
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            
            # Check if it mentions Casto Travel Philippines (correct) vs fashion designer (incorrect)
            if 'casto travel philippines' in response_text.lower():
                print("✅ Response mentions Casto Travel Philippines (correct - using KB!)")
            elif 'fashion' in response_text.lower() or 'designer' in response_text.lower():
                print("❌ Response mentions fashion designer (incorrect - still using training data)")
            else:
                print("⚠️ Response doesn't clearly indicate source")
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing chat endpoint: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Testing Complete!")

if __name__ == "__main__":
    test_new_deployment()
