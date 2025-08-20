#!/usr/bin/env python3
"""
Test script to check George Anzures query specifically
"""

import requests
import json

def test_george_anzures():
    """Test the George Anzures query"""
    print("🧪 Testing George Anzures Query")
    print("=" * 50)
    
    backend_url = "https://casto-ai-bot.vercel.app"
    
    # Test George Anzures query
    payload = {"message": "Who is George Anzures?"}
    
    try:
        print(f"📤 Sending query: '{payload['message']}'")
        print(f"🌐 Backend: {backend_url}")
        print()
        
        response = requests.post(f"{backend_url}/chat", json=payload, timeout=30)
        
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response", "No response")
            debug_info = data.get("debug_info", {})
            
            print(f"✅ Response received")
            print(f"🔍 Source: {debug_info.get('source', 'Unknown')}")
            print(f"📝 Response: {response_text[:200]}...")
            print()
            
            # Show debug info
            if debug_info:
                print("🔍 Debug Info:")
                for key, value in debug_info.items():
                    print(f"   {key}: {value}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_george_anzures()
