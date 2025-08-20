#!/usr/bin/env python3
"""
Test script to check CASI's identity and creation queries
"""

import requests
import json

def test_casi_identity():
    """Test CASI's identity and creation queries"""
    print("🧪 Testing CASI Identity & Creation Queries")
    print("=" * 60)
    
    backend_url = "https://casto-ai-bot.vercel.app"
    
    # Test CASI identity queries
    identity_queries = [
        # Name queries
        "What is your name?",
        "WHAT IS YOUR NAME?",
        "what is your name?",
        "Who are you?",
        "WHO ARE YOU?",
        "who are you?",
        
        # What CASI stands for
        "What does CASI stand for?",
        "WHAT DOES CASI STAND FOR?",
        "what does casi stand for?",
        "What does your name mean?",
        "WHAT DOES YOUR NAME MEAN?",
        "what does your name mean?",
        "What is the meaning of CASI?",
        "WHAT IS THE MEANING OF CASI?",
        "what is the meaning of casi?",
        
        # Creation queries
        "Who built you?",
        "WHO BUILT YOU?",
        "who built you?",
        "Who created you?",
        "WHO CREATED YOU?",
        "who created you?",
        "Who made you?",
        "WHO MADE YOU?",
        "who made you?",
        "Who developed you?",
        "WHO DEVELOPED YOU?",
        "who developed you?",
        
        # Identity questions
        "What are you?",
        "WHAT ARE YOU?",
        "what are you?",
        "Tell me about yourself",
        "TELL ME ABOUT YOURSELF",
        "tell me about yourself"
    ]
    
    successful_tests = 0
    total_tests = len(identity_queries)
    
    # Track responses by category
    name_responses = []
    meaning_responses = []
    creation_responses = []
    identity_responses = []
    
    for i, query in enumerate(identity_queries, 1):
        print(f"\n🔍 Test {i}/{total_tests}: '{query}'")
        print("-" * 50)
        
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
                
                # Check if we got a meaningful response
                if len(response_text) > 20 and "error" not in response_text.lower():
                    successful_tests += 1
                    print(f"🎯 SUCCESS: Got meaningful response from {source}")
                    
                    # Categorize and analyze responses
                    if any(word in query.lower() for word in ["name", "who are you"]):
                        name_responses.append((query, response_text))
                        if "casi" in response_text.lower():
                            print(f"✅ NAME INFO: Correctly mentions CASI")
                        else:
                            print(f"⚠️  NAME INFO: Doesn't mention CASI")
                    
                    elif any(word in query.lower() for word in ["stand for", "meaning", "mean"]):
                        meaning_responses.append((query, response_text))
                        if any(word in response_text.lower() for word in ["casto", "travel", "philippines", "assistant"]):
                            print(f"✅ MEANING INFO: Explains what CASI stands for")
                        else:
                            print(f"⚠️  MEANING INFO: Doesn't explain CASI meaning")
                    
                    elif any(word in query.lower() for word in ["built", "created", "made", "developed"]):
                        creation_responses.append((query, response_text))
                        if any(word in response_text.lower() for word in ["rojohn", "deguzman", "casto", "team"]):
                            print(f"✅ CREATION INFO: Mentions who built CASI")
                        else:
                            print(f"⚠️  CREATION INFO: Doesn't mention who built CASI")
                    
                    else:
                        identity_responses.append((query, response_text))
                        if "casi" in response_text.lower():
                            print(f"✅ IDENTITY INFO: Mentions CASI")
                        else:
                            print(f"⚠️  IDENTITY INFO: Doesn't mention CASI")
                    
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
    print(f"📊 CASI IDENTITY TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Successful tests: {successful_tests}/{total_tests}")
    print(f"❌ Failed tests: {total_tests - successful_tests}/{total_tests}")
    print(f"📈 Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    # Analyze responses by category
    print(f"\n🎯 RESPONSE ANALYSIS:")
    print(f"   📝 Name queries: {len(name_responses)} responses")
    print(f"   🔍 Meaning queries: {len(meaning_responses)} responses")
    print(f"   🛠️  Creation queries: {len(creation_responses)} responses")
    print(f"   🆔 Identity queries: {len(identity_responses)} responses")
    
    if successful_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! CASI identity working perfectly!")
    elif successful_tests >= total_tests * 0.8:
        print("\n👍 Most identity queries working well.")
    else:
        print("\n⚠️  Many identity queries need attention.")

if __name__ == "__main__":
    test_casi_identity()
