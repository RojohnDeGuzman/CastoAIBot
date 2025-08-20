#!/usr/bin/env python3
"""
Live Debug Monitor for CASI Vercel Backend
This script continuously monitors and displays live debug logs from the Vercel deployment
"""

import requests
import json
import time
import threading
from datetime import datetime
import os

# Base URL for your Vercel deployment
BASE_URL = "https://casto-ai-bot.vercel.app"  # Update this with your actual URL

class LiveDebugMonitor:
    def __init__(self):
        self.is_running = False
        self.debug_history = []
        self.max_history = 100
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print the monitor header"""
        print("🎯 CASI LIVE DEBUG MONITOR - Vercel Backend")
        print("=" * 80)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Backend: {BASE_URL}")
        print(f"📊 Debug Messages: {len(self.debug_history)}")
        print("=" * 80)
        print("💡 Send a chat request to see live debug logs!")
        print("💡 Press Ctrl+C to stop monitoring")
        print("=" * 80)
    
    def add_debug_message(self, message):
        """Add a debug message to history"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_msg = f"[{timestamp}] {message}"
        self.debug_history.append(formatted_msg)
        
        # Keep only recent messages
        if len(self.debug_history) > self.max_history:
            self.debug_history = self.debug_history[-self.max_history:]
    
    def display_debug_history(self):
        """Display the debug history"""
        if not self.debug_history:
            print("⏳ Waiting for debug messages...")
            print("   Send a chat request to see live logs!")
            return
        
        print("📋 LIVE DEBUG LOGS:")
        print("-" * 80)
        
        # Show recent messages (last 20)
        recent_messages = self.debug_history[-20:]
        for msg in recent_messages:
            print(msg)
        
        if len(self.debug_history) > 20:
            print(f"... and {len(self.debug_history) - 20} more messages")
    
    def test_backend_connectivity(self):
        """Test if backend is reachable"""
        try:
            response = requests.get(f"{BASE_URL}/debug/status", timeout=5)
            if response.status_code == 200:
                return True, "✅ Backend connected"
            else:
                return False, f"❌ Backend error: {response.status_code}"
        except Exception as e:
            return False, f"❌ Connection failed: {e}"
    
    def send_test_query(self, query):
        """Send a test query and capture debug messages"""
        try:
            print(f"\n🔍 Sending test query: '{query}'")
            
            chat_data = {
                "message": query,
                "access_token": "test"
            }
            
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/chat", json=chat_data, timeout=30)
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Add debug messages to history
                if 'debug_messages' in data and data['debug_messages']:
                    for msg in data['debug_messages']:
                        self.add_debug_message(msg)
                    
                    print(f"✅ Query completed in {processing_time:.2f}s")
                    print(f"📊 Captured {len(data['debug_messages'])} debug messages")
                else:
                    print("⚠️ No debug messages in response")
                
                # Show response summary
                if 'debug_info' in data:
                    debug = data['debug_info']
                    summary = f"Source: {debug.get('source', 'N/A')} | Confidence: {debug.get('confidence', 'N/A')}"
                    self.add_debug_message(f"RESPONSE: {summary}")
                
            else:
                error_msg = f"Query failed: {response.status_code}"
                self.add_debug_message(error_msg)
                print(f"❌ {error_msg}")
                
        except Exception as e:
            error_msg = f"Query error: {e}"
            self.add_debug_message(error_msg)
            print(f"❌ {error_msg}")
    
    def interactive_mode(self):
        """Interactive mode for manual queries"""
        print("\n🎮 INTERACTIVE MODE")
        print("Type your questions and see live debug logs!")
        print("Commands: 'quit', 'clear', 'status', 'test'")
        print("-" * 40)
        
        while self.is_running:
            try:
                user_input = input("💬 CASI > ").strip()
                
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'clear':
                    self.debug_history.clear()
                    self.clear_screen()
                    self.print_header()
                elif user_input.lower() == 'status':
                    connected, status = self.test_backend_connectivity()
                    print(f"🔧 {status}")
                elif user_input.lower() == 'test':
                    # Send a test query
                    self.send_test_query("Who is Maryle Casto?")
                elif user_input:
                    # Send user's query
                    self.send_test_query(user_input)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def auto_test_mode(self):
        """Auto test mode with predefined queries"""
        test_queries = [
            "Who is Maryle Casto?",
            "What services does Casto Travel offer?",
            "How do I reset my password?",
            "Tell me a joke"
        ]
        
        print("\n🤖 AUTO TEST MODE")
        print("Sending test queries automatically...")
        print("-" * 40)
        
        for i, query in enumerate(test_queries, 1):
            if not self.is_running:
                break
                
            print(f"\n🔍 Auto Test {i}/{len(test_queries)}: '{query}'")
            self.send_test_query(query)
            
            # Wait between tests
            if i < len(test_queries):
                print("⏳ Waiting 3 seconds...")
                time.sleep(3)
    
    def start_monitoring(self, mode="interactive"):
        """Start the live debug monitoring"""
        self.is_running = True
        
        try:
            while self.is_running:
                self.clear_screen()
                self.print_header()
                
                # Test backend connectivity
                connected, status = self.test_backend_connectivity()
                print(f"🔧 {status}")
                
                # Display debug history
                self.display_debug_history()
                
                if mode == "interactive":
                    self.interactive_mode()
                elif mode == "auto":
                    self.auto_test_mode()
                    break
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
        finally:
            self.is_running = False

def main():
    """Main function"""
    print("🚀 CASI Live Debug Monitor")
    print("=" * 50)
    print("Choose monitoring mode:")
    print("1. Interactive mode (manual queries)")
    print("2. Auto test mode (predefined queries)")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nEnter choice (1-3): ").strip()
            
            if choice == "1":
                monitor = LiveDebugMonitor()
                monitor.start_monitoring("interactive")
                break
            elif choice == "2":
                monitor = LiveDebugMonitor()
                monitor.start_monitoring("auto")
                break
            elif choice == "3":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
