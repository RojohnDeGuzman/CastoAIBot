#!/usr/bin/env python3
"""
Test script to check if CEO queries now work properly
"""

import requests
import json

def test_ceo_queries():
    """Test CEO queries to see if they now get proper CEO information"""
    print("🧪 Testing CEO Query Fix")
    print("=" * 50)
    
    backend_url = "https://casto-ai-bot.vercel.app"
    
    # Test CEO queries
    ceo_queries = [
        "Who is the CEO?",
        "WHO IS THE CEO?",
        "who is the ceo?",
        "Who Is The CEO?",
        "Tell me about the CEO",
        "Who is the current CEO?",
        "Who runs the company?"
    ]
    
    for i, query in enumerate(ceo_queries, 1):
        print(f"\n🔍 Test {i}: '{query}'")
        print("-" * 40)
        
        try:
            payload = {"message": query}
            response = requests.post(f"{backend_url}/chat", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "No response")
                debug_info = data.get("debug_info", {})
                source = debug_info.get('source', 'Unknown')
                
                print(f"✅ Status: {response.status_code}")
                print(f"🔍 Source: {source}")
                print(f"📝 Response: {response_text[:300]}...")
                
                # Check if CEO info is mentioned
                if "marc casto" in response_text.lower() and "ceo" in response_text.lower():
                    print(f"✅ CEO INFO: Correctly mentions Marc Casto as CEO!")
                elif "marc casto" in response_text.lower():
                    print(f"✅ CEO INFO: Mentions Marc Casto")
                elif "ceo" in response_text.lower():
                    print(f"⚠️  CEO INFO: Mentions CEO but not Marc Casto")
                else:
                    print(f"❌ CEO INFO: No CEO information found")
                
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print()

if __name__ == "__main__":
    test_ceo_queries()
