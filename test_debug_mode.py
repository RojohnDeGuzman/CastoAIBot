#!/usr/bin/env python3
"""
Test script for CASI Debug Mode
This script demonstrates the new enhanced debug functionality
"""

import requests
import json

# Base URL for your Vercel deployment
BASE_URL = "https://casto-ai-bot.vercel.app"  # Update this with your actual URL

def test_debug_status():
    """Test the debug status endpoint"""
    print("🔍 Testing Debug Status...")
    try:
        response = requests.get(f"{BASE_URL}/debug/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Debug Status: {data['message']}")
            print(f"🔧 Current Mode: {'🟢 ENABLED' if data['debug_mode'] else '🔴 DISABLED'}")
        else:
            print(f"❌ Failed to get debug status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing debug status: {e}")

def test_debug_format():
    """Test the debug format demo endpoint"""
    print("\n📋 Testing Debug Format Demo...")
    try:
        response = requests.get(f"{BASE_URL}/debug/format")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Debug Format Demo: {data['message']}")
            print(f"📊 Response Sources: {len(data['response_sources'])} available")
        else:
            print(f"❌ Failed to get debug format: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing debug format: {e}")

def test_chat_with_debug():
    """Test a chat request to see debug info in terminal"""
    print("\n💬 Testing Chat with Debug Mode...")
    print("📝 This will show debug info in your terminal if debug mode is enabled")
    
    chat_data = {
        "message": "Who is Maryle Casto?",
        "access_token": "test"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=chat_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat Response Received!")
            print(f"📝 Response: {data['response'][:100]}...")
            
            if 'debug_info' in data:
                debug = data['debug_info']
                print(f"\n🔍 DEBUG INFO RECEIVED:")
                print(f"   Source: {debug.get('source', 'N/A')}")
                print(f"   Confidence: {debug.get('confidence', 'N/A')}")
                print(f"   Response Type: {debug.get('response_type', 'N/A')}")
                print(f"   Processing Time: {debug.get('processing_time', 'N/A')}")
                print(f"   KB Entries Checked: {debug.get('knowledge_entries_checked', 'N/A')}")
                print(f"   Search Method: {debug.get('search_method', 'N/A')}")
                print(f"   AI Model Bypassed: {debug.get('ai_model_bypassed', 'N/A')}")
                print(f"   Response Quality: {debug.get('response_quality', 'N/A')}")
            else:
                print("❌ No debug info in response")
        else:
            print(f"❌ Chat request failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing chat: {e}")

def toggle_debug_mode(enable=True):
    """Toggle debug mode on/off"""
    print(f"\n🔧 {'Enabling' if enable else 'Disabling'} Debug Mode...")
    
    toggle_data = {
        "debug_mode": enable
    }
    
    try:
        response = requests.post(f"{BASE_URL}/debug/toggle", json=toggle_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
            print(f"🔧 Debug Mode: {'🟢 ENABLED' if data['debug_mode'] else '🔴 DISABLED'}")
        else:
            print(f"❌ Failed to toggle debug mode: {response.status_code}")
    except Exception as e:
        print(f"❌ Error toggling debug mode: {e}")

def main():
    """Main test function"""
    print("🎯 CASI Debug Mode Test Script")
    print("=" * 50)
    
    # Test current debug status
    test_debug_status()
    
    # Test debug format demo
    test_debug_format()
    
    # Test chat with debug mode enabled
    test_chat_with_debug()
    
    print("\n" + "=" * 50)
    print("📋 Debug Mode Instructions:")
    print("1. Set DEBUG_MODE = True in api/index.py to see terminal output")
    print("2. Use /debug/toggle endpoint to enable/disable via API")
    print("3. Use /debug/status to check current debug mode")
    print("4. Chat requests will show detailed debug info in terminal")
    print("5. JSON responses include comprehensive debug_info object")
    print("\n🔧 To disable terminal output, set DEBUG_MODE = False")

if __name__ == "__main__":
    main()
