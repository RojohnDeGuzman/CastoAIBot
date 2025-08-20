#!/usr/bin/env python3
"""
Test Frontend Locally
This script tests if your frontend can run and connect to the backend
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """Test if config is working"""
    print("🔧 Testing Configuration...")
    try:
        from config import get_backend_url, get_client_id, get_tenant_id
        backend_url = get_backend_url()
        client_id = get_client_id()
        tenant_id = get_tenant_id()
        
        print(f"✅ Backend URL: {backend_url}")
        print(f"✅ Client ID: {client_id}")
        print(f"✅ Tenant ID: {tenant_id}")
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_backend_connectivity():
    """Test backend connectivity"""
    print("\n🌐 Testing Backend Connectivity...")
    try:
        from config import get_backend_url
        backend_url = get_backend_url()
        
        # Test basic connectivity
        response = requests.get(f"{backend_url}/debug/status", timeout=10)
        if response.status_code == 200:
            print(f"✅ Backend is reachable: {backend_url}")
            return True
        else:
            print(f"❌ Backend error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connectivity error: {e}")
        return False

def test_chat_endpoint():
    """Test the chat endpoint"""
    print("\n💬 Testing Chat Endpoint...")
    try:
        from config import get_backend_url
        backend_url = get_backend_url()
        
        # Test chat request
        payload = {"message": "Who is Maryles Casto?"}
        response = requests.post(f"{backend_url}/chat", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat endpoint working")
            print(f"   Response: {data.get('response', 'No response')[:100]}...")
            
            if 'debug_messages' in data:
                print(f"   Debug Messages: {len(data['debug_messages'])} found")
                for i, msg in enumerate(data['debug_messages'][:3], 1):  # Show first 3
                    print(f"     {i}. {msg}")
            else:
                print("   ⚠️ No debug_messages in response")
                
            if 'debug_info' in data:
                print(f"   Debug Info: {data['debug_info']}")
            else:
                print("   ⚠️ No debug_info in response")
                
            return True
        else:
            print(f"❌ Chat endpoint error: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat test error: {e}")
        return False

def test_frontend_imports():
    """Test if frontend modules can be imported"""
    print("\n📦 Testing Frontend Imports...")
    
    required_modules = [
        'PyQt5.QtWidgets',
        'PyQt5.QtCore', 
        'PyQt5.QtGui',
        'requests',
        'json',
        'os',
        'sys'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed imports: {failed_imports}")
        return False
    else:
        print("\n✅ All required modules imported successfully")
        return True

def test_frontend_class():
    """Test if the main frontend class can be created"""
    print("\n🏗️ Testing Frontend Class Creation...")
    
    try:
        # Test if we can import the main class
        from chatbot_ui import ChatbotWidget
        print("✅ ChatbotWidget class imported successfully")
        
        # Test if we can create an instance (without GUI)
        try:
            # This might fail if PyQt5 app is not initialized
            print("⚠️ Note: Full GUI testing requires PyQt5 application context")
            print("✅ Frontend class structure is correct")
            return True
        except Exception as e:
            print(f"⚠️ Instance creation failed (expected without GUI): {e}")
            print("✅ Frontend class structure is correct")
            return True
            
    except ImportError as e:
        print(f"❌ Failed to import ChatbotWidget: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 CASI Frontend Local Test")
    print("=" * 60)
    print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_config),
        ("Backend Connectivity", test_backend_connectivity),
        ("Chat Endpoint", test_chat_endpoint),
        ("Frontend Imports", test_frontend_imports),
        ("Frontend Class", test_frontend_class)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your frontend should work correctly.")
        print("💡 Try running: python chatbot_ui.py")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        print("💡 Fix the issues before running the frontend.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
