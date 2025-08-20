#!/usr/bin/env python3
"""
Test script to check if the live Vercel deployment has the knowledge base fixes
"""

import requests
import json

def test_live_knowledge_base():
    """Test if the live deployment has the updated knowledge base"""
    print("Testing live Vercel deployment...")
    
    # Replace this with your actual Vercel URL
    vercel_url = input("Enter your Vercel URL (e.g., https://your-app.vercel.app): ").strip()
    
    if not vercel_url:
        print("❌ No Vercel URL provided")
        return False
    
    try:
        # Test the knowledge base test endpoint
        test_url = f"{vercel_url}/test/kb"
        print(f"Testing: {test_url}")
        
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test endpoint responded successfully")
            print(f"Knowledge base entries: {data.get('knowledge_base_test', {}).get('entries_count', 'Unknown')}")
            
            # Check if we have the expected number of entries (should be 41+)
            entries_count = data.get('knowledge_base_test', {}).get('entries_count', 0)
            if entries_count >= 41:
                print(f"✅ Knowledge base has {entries_count} entries (expected 41+)")
                return True
            else:
                print(f"❌ Knowledge base only has {entries_count} entries (expected 41+)")
                return False
        else:
            print(f"❌ Test endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing live deployment: {e}")
        return False

def test_live_chat():
    """Test the live chat endpoint with a Maryles Casto question"""
    print("\nTesting live chat endpoint...")
    
    vercel_url = input("Enter your Vercel URL (e.g., https://your-app.vercel.app): ").strip()
    
    if not vercel_url:
        print("❌ No Vercel URL provided")
        return False
    
    try:
        chat_url = f"{vercel_url}/chat"
        print(f"Testing: {chat_url}")
        
        # Test with the problematic query
        test_data = {
            "message": "who is Maryles Casto?",
            "access_token": "test"  # This might fail auth but let's see the response
        }
        
        response = requests.post(chat_url, json=test_data, timeout=15)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            
            # Check if it mentions Casto Travel Philippines (correct) vs fashion designer (incorrect)
            if 'casto travel philippines' in response_text.lower():
                print("✅ Response mentions Casto Travel Philippines (correct)")
                return True
            elif 'fashion' in response_text.lower() or 'designer' in response_text.lower():
                print("❌ Response mentions fashion designer (incorrect - using training data)")
                return False
            else:
                print("⚠️ Response doesn't clearly indicate source")
                return False
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing live chat: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("LIVE DEPLOYMENT TEST")
    print("=" * 60)
    
    kb_ok = test_live_knowledge_base()
    chat_ok = test_live_chat()
    
    print("\n" + "=" * 60)
    if kb_ok and chat_ok:
        print("🎉 DEPLOYMENT IS WORKING - Knowledge base fixes are live!")
    else:
        print("❌ DEPLOYMENT ISSUES - Knowledge base fixes are not active")
        print("\nNext steps:")
        print("1. Check Vercel dashboard for deployment status")
        print("2. Verify environment variables (GROQ_API_KEY)")
        print("3. Trigger a manual deployment")
    print("=" * 60)
