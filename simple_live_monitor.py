#!/usr/bin/env python3
"""
Simple Live Debug Monitor for CASI Vercel Backend
Continuously shows live debug logs from the Vercel deployment
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
    print("🎯 CASI LIVE DEBUG MONITOR")
    print("=" * 60)
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Backend: {BASE_URL}")
    print("=" * 60)
    print("💡 Send chat requests to see live debug logs!")
    print("💡 Press Ctrl+C to stop")
    print("=" * 60)

def send_query_and_show_debug(query):
    """Send a query and show debug messages"""
    try:
        print(f"\n🔍 Sending: '{query}'")
        
        chat_data = {
            "message": query,
            "access_token": "test"
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=chat_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'debug_messages' in data and data['debug_messages']:
                print("📋 DEBUG LOGS:")
                print("-" * 40)
                for msg in data['debug_messages']:
                    print(msg)
                print("-" * 40)
                
                # Show response summary
                if 'debug_info' in data:
                    debug = data['debug_info']
                    print(f"✅ Response: {debug.get('source', 'N/A')} | {debug.get('confidence', 'N/A')}")
            else:
                print("⚠️ No debug messages received")
        else:
            print(f"❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def continuous_monitor():
    """Continuous monitoring with auto-refresh"""
    print("🚀 Starting continuous debug monitor...")
    print("This will refresh every 5 seconds to show new debug logs")
    
    try:
        while True:
            clear_screen()
            print_header()
            
            # Test backend connectivity
            try:
                response = requests.get(f"{BASE_URL}/debug/status", timeout=5)
                if response.status_code == 200:
                    print("✅ Backend connected")
                else:
                    print(f"❌ Backend error: {response.status_code}")
            except:
                print("❌ Backend not reachable")
            
            print("\n⏳ Waiting for debug logs...")
            print("Send a chat request from another terminal or your app!")
            print("\nExample:")
            print(f"curl -X POST '{BASE_URL}/chat' -H 'Content-Type: application/json' -d '{{\"message\": \"Who is Maryle Casto?\", \"access_token\": \"test\"}}'")
            
            # Wait and refresh
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped")

def interactive_monitor():
    """Interactive monitoring with manual queries"""
    print("🎮 Interactive Debug Monitor")
    print("Type your questions and see live debug logs!")
    
    try:
        while True:
            query = input("\n💬 CASI > ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            elif query.lower() in ['clear', 'cls']:
                clear_screen()
                print_header()
            elif query:
                send_query_and_show_debug(query)
                
    except KeyboardInterrupt:
        print("\n\n🛑 Interactive mode stopped")

def main():
    """Main function"""
    print("🎯 CASI Live Debug Monitor")
    print("=" * 40)
    print("Choose mode:")
    print("1. Continuous monitor (auto-refresh)")
    print("2. Interactive monitor (manual queries)")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nEnter choice (1-3): ").strip()
            
            if choice == "1":
                continuous_monitor()
                break
            elif choice == "2":
                interactive_monitor()
                break
            elif choice == "3":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
