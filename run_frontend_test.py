#!/usr/bin/env python3
"""
Simple Frontend Test Runner
This script tries to run your frontend to see if it works
"""

import sys
import os
import subprocess
import time

def test_frontend_run():
    """Test if the frontend can run"""
    print("🧪 Testing Frontend Execution")
    print("=" * 50)
    
    # Check if PyQt5 is available
    try:
        import PyQt5
        print("✅ PyQt5 is available")
    except ImportError:
        print("❌ PyQt5 not found. Install with: pip install PyQt5")
        return False
    
    # Check if the main file exists
    if not os.path.exists("chatbot_ui.py"):
        print("❌ chatbot_ui.py not found")
        return False
    
    print("✅ chatbot_ui.py found")
    
    # Try to run the frontend
    print("\n🚀 Attempting to run frontend...")
    print("💡 This will open the CASI application window")
    print("💡 Press Ctrl+C in this terminal to stop the test")
    print("💡 Or close the CASI window to stop")
    
    try:
        # Run the frontend
        process = subprocess.Popen([sys.executable, "chatbot_ui.py"])
        
        print(f"✅ Frontend started with PID: {process.pid}")
        print("💡 CASI application should now be running")
        print("💡 Try sending a message in the app")
        print("💡 Check if it connects to the backend")
        
        # Wait for user to test
        input("\n⏳ Press Enter when you're done testing, or Ctrl+C to stop...")
        
        # Terminate the process
        process.terminate()
        try:
            process.wait(timeout=5)
            print("✅ Frontend stopped cleanly")
        except subprocess.TimeoutExpired:
            process.kill()
            print("⚠️ Frontend force-killed")
        
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
        if 'process' in locals():
            process.terminate()
        return True
    except Exception as e:
        print(f"❌ Failed to run frontend: {e}")
        return False

def main():
    """Main function"""
    print("🎯 CASI Frontend Test Runner")
    print("=" * 50)
    
    success = test_frontend_run()
    
    if success:
        print("\n🎉 Frontend test completed!")
        print("💡 If the app opened and worked, your frontend is fine")
        print("💡 If there were issues, check the error messages above")
    else:
        print("\n❌ Frontend test failed!")
        print("💡 Check the error messages and fix the issues")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
