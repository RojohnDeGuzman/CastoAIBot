#!/usr/bin/env python3
"""
Test script to verify knowledge base loading
"""

import json
import os

def test_knowledge_base():
    """Test if knowledge base can be loaded"""
    print("Testing knowledge base loading...")
    
    # Check if file exists
    if not os.path.exists('knowledge_base.json'):
        print("❌ knowledge_base.json file not found!")
        return False
    
    print(f"✅ knowledge_base.json found (size: {os.path.getsize('knowledge_base.json')} bytes)")
    
    # Try to load the JSON
    try:
        with open('knowledge_base.json', 'r', encoding='utf-8') as f:
            knowledge_data = json.load(f)
        
        print(f"✅ JSON loaded successfully - {len(knowledge_data)} entries")
        
        # Show sample entries
        print("\nSample entries:")
        for i, entry in enumerate(knowledge_data[:3]):
            print(f"  {i+1}. Q: {entry['question'][:50]}...")
            print(f"     A: {entry['answer'][:50]}...")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_backend_import():
    """Test if backend can import and load knowledge base"""
    print("\nTesting backend import...")
    
    try:
        # Import the backend module
        import sys
        sys.path.append('.')
        
        from backend import get_cached_knowledge
        
        # Test the function
        knowledge_entries = get_cached_knowledge()
        print(f"✅ Backend function loaded {len(knowledge_entries)} knowledge entries")
        
        if knowledge_entries:
            print("✅ Knowledge base is working in backend!")
            return True
        else:
            print("❌ Knowledge base returned empty results")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("KNOWLEDGE BASE TEST")
    print("=" * 50)
    
    kb_ok = test_knowledge_base()
    backend_ok = test_backend_import()
    
    print("\n" + "=" * 50)
    if kb_ok and backend_ok:
        print("🎉 ALL TESTS PASSED - Knowledge base is working!")
    else:
        print("❌ SOME TESTS FAILED - Check the issues above")
    print("=" * 50)
