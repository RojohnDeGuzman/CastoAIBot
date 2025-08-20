#!/usr/bin/env python3
"""
Test script for CASI Local Debug Mode
This script shows debug messages from the Vercel deployment in your local terminal
"""

import requests
import json
import time

# Base URL for your Vercel deployment
BASE_URL = "https://casto-ai-bot.vercel.app"  # Update this with your actual URL

def test_chat_with_local_debug():
    """Test a chat request and show debug messages in local terminal"""
    print("🎯 CASI Local Debug Mode Test")
    print("=" * 60)
    print("📝 This will show debug messages from Vercel in your local terminal")
    print("=" * 60)
    
    # Test queries to see different debug paths
    test_queries = [
        "Who is Maryle Casto?",
        "What services does Casto Travel offer?",
        "How do I reset my password?",
        "Tell me a joke"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 TEST {i}: '{query}'")
        print("-" * 40)
        
        chat_data = {
            "message": query,
            "access_token": "test"
        }
        
        try:
            print(f"[DEBUG] Sending request to: {BASE_URL}/chat")
            start_time = time.time()
            
            response = requests.post(f"{BASE_URL}/chat", json=chat_data)
            processing_time = time.time() - start_time
            
            print(f"[DEBUG] Response received in {processing_time:.2f}s")
            print(f"[DEBUG] Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response received successfully!")
                print(f"📝 Response: {data['response'][:100]}...")
                
                # Show debug info
                if 'debug_info' in data:
                    debug = data['debug_info']
                    print(f"\n🔍 DEBUG INFO:")
                    print(f"   Source: {debug.get('source', 'N/A')}")
                    print(f"   Confidence: {debug.get('confidence', 'N/A')}")
                    print(f"   Response Type: {debug.get('response_type', 'N/A')}")
                    print(f"   Processing Time: {debug.get('processing_time', 'N/A')}")
                    print(f"   KB Entries Checked: {debug.get('knowledge_entries_checked', 'N/A')}")
                    print(f"   AI Model Bypassed: {debug.get('ai_model_bypassed', 'N/A')}")
                    print(f"   Response Quality: {debug.get('response_quality', 'N/A')}")
                
                # Show debug messages (this is what you'll see in your terminal!)
                if 'debug_messages' in data and data['debug_messages']:
                    print(f"\n📋 DEBUG MESSAGES FROM VERCEL:")
                    print("-" * 30)
                    for msg in data['debug_messages']:
                        print(msg)
                    print("-" * 30)
                else:
                    print("❌ No debug messages received")
                
            else:
                print(f"❌ Chat request failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing chat: {e}")
        
        print("\n" + "=" * 60)
        time.sleep(1)  # Small delay between tests

def test_debug_endpoints():
    """Test the debug endpoints"""
    print("\n🔧 Testing Debug Endpoints")
    print("=" * 40)
    
    # Test debug status
    try:
        response = requests.get(f"{BASE_URL}/debug/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Debug Status: {data['message']}")
            print(f"🔧 Debug Mode: {'🟢 ENABLED' if data['debug_mode'] else '🔴 DISABLED'}")
        else:
            print(f"❌ Debug status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing debug status: {e}")
    
    # Test debug format
    try:
        response = requests.get(f"{BASE_URL}/debug/format")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Debug Format: {data['message']}")
        else:
            print(f"❌ Debug format failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing debug format: {e}")

def main():
    """Main test function"""
    print("🚀 CASI Local Debug Mode - Live Terminal Debugging")
    print("=" * 70)
    print("This script will show you debug messages from the Vercel deployment")
    print("in your local terminal, giving you the live debugging experience!")
    print("=" * 70)
    
    # Test debug endpoints first
    test_debug_endpoints()
    
    # Test chat with local debug
    test_chat_with_local_debug()
    
    print("\n" + "=" * 70)
    print("🎯 What You Just Saw:")
    print("1. Debug messages from Vercel deployment in your local terminal")
    print("2. Real-time processing flow of each request")
    print("3. Where each response came from (KB, Website, AI, etc.)")
    print("4. Processing times and confidence levels")
    print("5. Complete debug trail of each request")
    print("\n🔧 To see this in your app, check the 'debug_messages' field")
    print("   in the API response and display them in your UI!")

if __name__ == "__main__":
    main()
