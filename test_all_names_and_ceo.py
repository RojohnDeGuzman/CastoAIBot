#!/usr/bin/env python3
"""
Test script to check ALL names in KB and CEO queries
"""

import requests
import json

def test_all_names_and_ceo():
    """Test all names in KB and CEO queries"""
    print("🧪 Testing ALL Names in KB + CEO Queries")
    print("=" * 70)
    
    backend_url = "https://casto-ai-bot.vercel.app"
    
    # Test ALL names from your knowledge base with case variations
    test_cases = [
        # Core Casto Family
        "Who is Maryles Casto?",
        "WHO IS MARYLES CASTO?",
        "who is maryles casto?",
        "Who Is Maryles Casto?",
        
        "Who is Marc Casto?",
        "WHO IS MARC CASTO?",
        "who is marc casto?",
        "Who Is Marc Casto?",
        
        # Executive Team
        "Who is Luz Bagtas?",
        "WHO IS LUZ BAGTAS?",
        "who is luz bagtas?",
        "Who Is Luz Bagtas?",
        
        "Who is Elaine Randrup?",
        "WHO IS ELAINE RANDRUP?",
        "who is elaine randrup?",
        "Who Is Elaine Randrup?",
        
        "Who is Alwin Benedicto?",
        "WHO IS ALWIN BENEDICTO?",
        "who is alwin benedicto?",
        "Who Is Alwin Benedicto?",
        
        "Who is George Anzures?",
        "WHO IS GEORGE ANZURES?",
        "who is george anzures?",
        "Who Is George Anzures?",
        
        "Who is Ma. Berdandina Galvez?",
        "WHO IS MA. BERDANDINA GALVEZ?",
        "who is ma. berdandina galvez?",
        "Who Is Ma. Berdandina Galvez?",
        
        "Who is Berlin Torres?",
        "WHO IS BERLIN TORRES?",
        "who is berlin torres?",
        "Who Is Berlin Torres?",
        
        "Who is Voltaire Villaflores?",
        "WHO IS VOLTAIRE VILLAFLORES?",
        "who is voltaire villaflores?",
        "Who Is Voltaire Villaflores?",
        
        "Who is Victor Villaflores?",
        "WHO IS VICTOR VILLAFLORES?",
        "who is victor villaflores?",
        "Who Is Victor Villaflores?",
        
        # CEO Specific Queries (should get current info)
        "Who is the CEO?",
        "WHO IS THE CEO?",
        "who is the ceo?",
        "Who Is The CEO?",
        "WHO IS THE ceo?",
        "who IS THE CEO?",
        
        "Who is the current CEO?",
        "WHO IS THE CURRENT CEO?",
        "who is the current ceo?",
        "Who Is The Current CEO?",
        
        "Tell me about the CEO",
        "TELL ME ABOUT THE CEO",
        "tell me about the ceo",
        "Tell Me About The CEO",
        
        # Company Leadership Queries
        "Who are the leaders?",
        "WHO ARE THE LEADERS?",
        "who are the leaders?",
        "Who Are The Leaders?",
        
        "Who is in charge?",
        "WHO IS IN CHARGE?",
        "who is in charge?",
        "Who Is In Charge?",
        
        "Who runs Casto Travel?",
        "WHO RUNS CASTO TRAVEL?",
        "who runs casto travel?",
        "Who Runs Casto Travel?"
    ]
    
    successful_tests = 0
    total_tests = len(test_cases)
    
    # Track which names work and which don't
    working_names = []
    failed_names = []
    
    for i, test_query in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}/{total_tests}: '{test_query}'")
        print("-" * 60)
        
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
                print(f"📝 Response: {response_text[:200]}...")
                
                # Check if we got a meaningful response
                if len(response_text) > 20 and "error" not in response_text.lower():
                    successful_tests += 1
                    working_names.append(test_query)
                    print(f"🎯 SUCCESS: Got meaningful response from {source}")
                    
                    # Special check for CEO queries
                    if "ceo" in test_query.lower():
                        if "marc casto" in response_text.lower():
                            print(f"✅ CEO INFO: Correctly identified Marc Casto as CEO")
                        else:
                            print(f"⚠️  CEO INFO: Response doesn't mention Marc Casto as CEO")
                    
                else:
                    failed_names.append(test_query)
                    print(f"⚠️  WARNING: Response seems too short or contains error")
                
            else:
                failed_names.append(test_query)
                print(f"❌ Status: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            failed_names.append(test_query)
            print(f"❌ Exception: {e}")
        
        print()
    
    # Summary
    print("=" * 70)
    print(f"📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Successful tests: {successful_tests}/{total_tests}")
    print(f"❌ Failed tests: {total_tests - successful_tests}/{total_tests}")
    print(f"📈 Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    print(f"\n🎯 WORKING NAMES ({len(working_names)}):")
    for name in working_names[:10]:  # Show first 10
        print(f"   ✅ {name}")
    if len(working_names) > 10:
        print(f"   ... and {len(working_names) - 10} more")
    
    if failed_names:
        print(f"\n❌ FAILED NAMES ({len(failed_names)}):")
        for name in failed_names[:5]:  # Show first 5
            print(f"   ❌ {name}")
        if len(failed_names) > 5:
            print(f"   ... and {len(failed_names) - 5} more")
    
    if successful_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! All names working perfectly!")
    elif successful_tests >= total_tests * 0.9:
        print("\n👍 Excellent! Almost all names working.")
    elif successful_tests >= total_tests * 0.8:
        print("\n👍 Most names working well.")
    else:
        print("\n⚠️  Many names need attention.")

if __name__ == "__main__":
    test_all_names_and_ceo()
