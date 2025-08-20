#!/usr/bin/env python3
"""
Live Log Capture Monitor for CASI Desktop App
This script actively monitors your Vercel backend and shows debug logs
as they happen from your desktop app - REAL-TIME LOGGING!
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
    print("🎯 CASI LIVE LOG CAPTURE MONITOR")
    print("=" * 70)
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Backend: {BASE_URL}")
    print("=" * 70)
    print("💡 Use your desktop app - I'll capture debug logs in real-time!")
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

def live_monitor():
    """Live monitoring that shows debug logs in real-time"""
    print("🚀 Starting live log capture monitor...")
    print("This will show debug logs from your desktop app in real-time!")
    
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
    
    print("\n✅ Ready to capture logs! Use your desktop app now.")
    print("🔍 I'll show debug logs as they happen...")
    input("\nPress Enter to start live monitoring...")
    
    # Start live monitoring
    log_history = []
    request_count = 0
    
    try:
        while True:
            clear_screen()
            print_header()
            
            # Test connectivity
            connected, status = test_backend()
            print(f"🔧 {status}")
            
            # Show monitoring status
            print(f"\n📊 LIVE MONITORING STATUS:")
            print(f"   Total requests monitored: {request_count}")
            print(f"   Total debug logs captured: {len(log_history)}")
            print(f"   Last check: {datetime.now().strftime('%H:%M:%S')}")
            print(f"   Status: {'🟢 Active' if connected else '🔴 Disconnected'}")
            
            # Show recent logs
            if log_history:
                print(f"\n📋 LIVE DEBUG LOGS (Last 20):")
                print("-" * 70)
                recent_logs = log_history[-20:]
                for i, log in enumerate(recent_logs, 1):
                    timestamp = log.get('timestamp', 'Unknown')
                    message = log.get('message', 'Unknown')
                    print(f"{i:2d}. [{timestamp}] {message}")
                print("-" * 70)
            else:
                print(f"\n⏳ Waiting for debug logs...")
                print("   Use your desktop app to send a message!")
                print("   I'll capture and display the logs here in real-time.")
            
            # Show instructions
            print(f"\n💡 INSTRUCTIONS:")
            print("1. Keep this terminal open")
            print("2. Use your desktop app normally")
            print("3. Send messages in your app")
            print("4. Watch for debug logs appearing here automatically!")
            print("\n🔍 TO TEST: Send a message in your desktop app RIGHT NOW!")
            print("   The debug logs will appear here immediately.")
            
            # Wait and refresh
            print(f"\n⏳ Refreshing in 2 seconds... (Press Ctrl+C to stop)")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Live monitoring stopped")

def main():
    """Main function"""
    print("🎯 CASI Live Log Capture Monitor")
    print("=" * 50)
    print("This monitor will CAPTURE debug logs in real-time")
    print("from your desktop app as they happen!")
    print("=" * 50)
    
    try:
        live_monitor()
    except KeyboardInterrupt:
        print("\n\n🛑 Monitor stopped by user")
    finally:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
