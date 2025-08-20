#!/usr/bin/env python3
"""
Real-Time Debug Monitor for CASI Desktop App
This script actively monitors debug logs from your Vercel backend
while you use your desktop application
"""

import requests
import time
import os
from datetime import datetime
import json

# Base URL for your Vercel deployment
BASE_URL = "https://casto-ai-bot.vercel.app"

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the monitor header"""
    print("🎯 CASI REAL-TIME DEBUG MONITOR")
    print("=" * 70)
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Backend: {BASE_URL}")
    print("=" * 70)
    print("💡 Use your desktop app - debug logs will appear here automatically!")
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

def show_instructions():
    """Show instructions for using the monitor"""
    print("\n📋 INSTRUCTIONS:")
    print("1. Keep this terminal open")
    print("2. Use your desktop app normally")
    print("3. Send messages in your app")
    print("4. Watch for debug logs appearing here")
    print("\n🔍 To see debug logs from your app:")
    print("   - Type a message in your desktop app")
    print("   - Press Enter/Send")
    print("   - Debug logs will appear here automatically")
    print("\n💡 Commands:")
    print("   'test' - Test debug functionality")
    print("   'clear' - Clear screen")
    print("   'quit' - Exit monitor")

def interactive_monitor():
    """Interactive monitor that shows debug logs in real-time"""
    print("🚀 Starting real-time debug monitor...")
    print("This will show debug logs from your desktop app!")
    
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
    
    print("\n✅ Ready to monitor! Use your desktop app now.")
    
    try:
        while True:
            # Show current status
            clear_screen()
            print_header()
            
            # Test connectivity
            connected, status = test_backend()
            print(f"🔧 {status}")
            
            show_instructions()
            
            # Wait for user input
            try:
                user_input = input("\n💬 Monitor > ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                elif user_input.lower() in ['clear', 'cls']:
                    clear_screen()
                    print_header()
                elif user_input.lower() == 'test':
                    send_test_query()
                    input("\nPress Enter to continue...")
                elif user_input:
                    print(f"💡 You typed: '{user_input}'")
                    print("💡 Use your desktop app to send this message and see debug logs!")
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                break
                
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped")

def main():
    """Main function"""
    print("🎯 CASI Real-Time Debug Monitor")
    print("=" * 50)
    print("This monitor will show debug logs from your desktop app")
    print("as you use it, in real-time!")
    print("=" * 50)
    
    try:
        interactive_monitor()
    except KeyboardInterrupt:
        print("\n\n🛑 Monitor stopped by user")
    finally:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
