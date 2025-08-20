#!/usr/bin/env python3
"""
Test script to check case variations for knowledge base queries
"""

import requests
import json

def test_case_variations():
    """Test various case variations for knowledge base queries"""
    print("🧪 Testing Case Variations for Knowledge Base")
    print("=" * 60)
    
    backend_url = "https://casto-ai-bot.vercel.app"
    
    # Test cases with different case variations
    test_cases = [
        # George Anzures variations
        "Who is George Anzures?",
        "WHO IS GEORGE ANZURES?",
        "who is george anzures?",
        "Who Is George Anzures?",
        "WHO IS george ANZURES?",
        "who IS GEORGE anzures?",
        
        # Maryles Casto variations
        "Who is Maryles Casto?",
        "WHO IS MARYLES CASTO?",
        "who is maryles casto?",
        "Who Is Maryles Casto?",
        "WHO IS maryles CASTO?",
        "who IS MARYLES casto?",
        
        # Marc Casto variations
        "Who is Marc Casto?",
        "WHO IS MARC CASTO?",
        "who is marc casto?",
        "Who Is Marc Casto?",
        "WHO IS marc CASTO?",
        "who IS MARC casto?",
        
        # Partial name variations
        "Who is George?",
        "WHO IS GEORGE?",
        "who is george?",
        "Tell me about George",
        "TELL ME ABOUT GEORGE",
        "tell me about george",
        
        # Mixed case variations
        "Who Is The CEO?",
        "WHO IS THE ceo?",
        "who IS THE CEO?",
        "What Is Casto Travel?",
        "WHAT IS CASTO travel?",
        "what IS CASTO TRAVEL?"
    ]
    
    successful_tests = 0
    total_tests = len(test_cases)
    
    for i, test_query in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}/{total_tests}: '{test_query}'")
        print("-" * 50)
        
        try:
            payload = {"message": test_query}
            response = requests.post(f"{backend_url}/chat", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "No response")
                debug_info = data.get("debug_info", {})
                source = debug_info.get('source', 'Unknown')
                
                print(f"✅ Status: {response.status_code}")
                print(f"🔍 Source: {source}")
                print(f"📝 Response: {response_text[:150]}...")
                
                # Check if we got a meaningful response
                if len(response_text) > 20 and "error" not in response_text.lower():
                    successful_tests += 1
                    print(f"🎯 SUCCESS: Got meaningful response from {source}")
                else:
                    print(f"⚠️  WARNING: Response seems too short or contains error")
                
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print()
    
    # Summary
    print("=" * 60)
    print(f"📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Successful tests: {successful_tests}/{total_tests}")
    print(f"❌ Failed tests: {total_tests - successful_tests}/{total_tests}")
    print(f"📈 Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Case variations working perfectly!")
    elif successful_tests >= total_tests * 0.8:
        print("👍 Most tests passed! Case variations mostly working.")
    else:
        print("⚠️  Many tests failed. Case variations need improvement.")

if __name__ == "__main__":
    test_case_variations()
