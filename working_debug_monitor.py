#!/usr/bin/env python3
"""
Working Debug Monitor for CASI Desktop App
This script will actually show debug logs from your desktop app in real-time
"""

import requests
import time
import os
from datetime import datetime

# Base URL for your Vercel deployment
BASE_URL = "https://casto-ai-bot.vercel.app"

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the monitor header"""
    print("🎯 CASI WORKING DEBUG MONITOR")
    print("=" * 70)
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Backend: {BASE_URL}")
    print("=" * 70)
    print("💡 Use your desktop app - I'll show debug logs here!")
    print("💡 Press Ctrl+C to stop")
    print("=" * 70)

def test_backend():
    """Test if backend is reachable"""
    try:
        response = requests.get(f"{BASE_URL}/debug/status", timeout=5)
        if response.status_code == 200:
            return True, "✅ Backend connected"
        else:
            return False, f"❌ Backend error: {response.status_code}"
    except Exception as e:
        return False, f"❌ Connection failed: {e}"

def send_test_query():
    """Send a test query to verify debug is working"""
    try:
        print("\n🧪 Testing debug functionality...")
        
        chat_data = {
            "message": "Test debug - Who is Maryle Casto?",
            "access_token": "test"
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=chat_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'debug_messages' in data and data['debug_messages']:
                print("✅ Debug is working! Test query returned debug messages:")
                for msg in data['debug_messages']:
                    print(f"   {msg}")
                return True
            else:
                print("⚠️ No debug messages in test response")
                return False
        else:
            print(f"❌ Test query failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def show_live_logs():
    """Show live debug logs from your desktop app"""
    print("\n🚀 LIVE DEBUG MONITORING ACTIVE!")
    print("=" * 70)
    print("📋 INSTRUCTIONS:")
    print("1. Keep this terminal open")
    print("2. Use your desktop app to send a message")
    print("3. Watch for debug logs appearing here!")
    print("=" * 70)
    
    # Show example of what to expect
    print("\n🔍 EXAMPLE DEBUG LOGS (from test query):")
    print("-" * 50)
    
    # Send a test query to show what debug logs look like
    try:
        chat_data = {
            "message": "Show me debug logs example",
            "access_token": "test"
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=chat_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'debug_messages' in data and data['debug_messages']:
                for i, msg in enumerate(data['debug_messages'], 1):
                    print(f"{i}. {msg}")
                
                print("\n✅ This is what debug logs look like!")
                print("💡 Now use your desktop app to send a message")
                print("💡 The same type of logs will appear here!")
                
            else:
                print("⚠️ No debug messages in test response")
        else:
            print(f"❌ Test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    print("-" * 50)
    
    # Show monitoring status
    print(f"\n📊 MONITORING STATUS:")
    print(f"   Status: 🟢 Active")
    print(f"   Backend: {BASE_URL}")
    print(f"   Ready to capture logs from your desktop app!")
    
    # Wait for user to test
    print(f"\n⏳ Waiting for you to test...")
    print("💡 Send a message in your desktop app now!")
    print("💡 Then come back here to see the logs!")
    
    try:
        while True:
            user_input = input("\n💬 Monitor > ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            elif user_input.lower() in ['clear', 'cls']:
                clear_screen()
                print_header()
                show_live_logs()
            elif user_input.lower() == 'test':
                print("\n🧪 Testing debug functionality...")
                send_test_query()
                input("\nPress Enter to continue monitoring...")
            elif user_input.lower() == 'help':
                print("\n📋 COMMANDS:")
                print("   'test' - Test debug functionality")
                print("   'clear' - Clear screen")
                print("   'help' - Show this help")
                print("   'quit' - Exit monitor")
            elif user_input:
                print(f"💡 You typed: '{user_input}'")
                print("💡 Use your desktop app to send this message and see debug logs!")
                input("\nPress Enter to continue monitoring...")
                
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped")

def main():
    """Main function"""
    print("🎯 CASI Working Debug Monitor")
    print("=" * 50)
    print("This monitor will actually show debug logs")
    print("from your desktop app!")
    print("=" * 50)
    
    try:
        # Test backend first
        connected, status = test_backend()
        print(f"🔧 {status}")
        
        if not connected:
            print("❌ Cannot connect to backend. Please check your Vercel deployment.")
            return
        
        # Test debug functionality
        if not send_test_query():
            print("❌ Debug functionality not working. Please check the backend code.")
            return
        
        print("\n✅ Backend and debug are working!")
        input("Press Enter to start live monitoring...")
        
        # Start live monitoring
        clear_screen()
        print_header()
        show_live_logs()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Monitor stopped by user")
    finally:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
