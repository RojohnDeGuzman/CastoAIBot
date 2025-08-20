#!/usr/bin/env python3
"""
Test script to verify knowledge base fixes
"""

import json
import os

def test_knowledge_base_file():
    """Test the knowledge base JSON file"""
    print("Testing knowledge_base.json...")
    
    if not os.path.exists('knowledge_base.json'):
        print("❌ knowledge_base.json not found!")
        return False
    
    try:
        with open('knowledge_base.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ knowledge_base.json loaded successfully - {len(data)} entries")
        
        # Check for Maryles Casto entries
        maryles_entries = [entry for entry in data if "maryles" in entry.get('question', '').lower() or "maryles" in entry.get('answer', '').lower()]
        print(f"✅ Found {len(maryles_entries)} entries about Maryles Casto")
        
        # Show sample Maryles entry
        if maryles_entries:
            print(f"Sample Maryles entry: {maryles_entries[0]['answer'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading knowledge_base.json: {e}")
        return False

def test_api_knowledge_base():
    """Test the embedded knowledge base in api/index.py"""
    print("\nTesting api/index.py embedded knowledge base...")
    
    try:
        # Import the function
        import sys
        sys.path.append('.')
        
        from api.index import get_cached_knowledge
        
        # Test the function
        knowledge_entries = get_cached_knowledge()
        print(f"✅ get_cached_knowledge() returned {len(knowledge_entries)} entries")
        
        # Check for Maryles Casto entries
        maryles_found = False
        for entry in knowledge_entries:
            if isinstance(entry, dict):
                if "maryles" in entry.get('question', '').lower() or "maryles" in entry.get('answer', '').lower():
                    maryles_found = True
                    print(f"✅ Found Maryles Casto entry: {entry['answer'][:100]}...")
                    break
            elif isinstance(entry, str):
                if "maryles" in entry.lower():
                    maryles_found = True
                    print(f"✅ Found Maryles Casto in string entry: {entry[:100]}...")
                    break
        
        if not maryles_found:
            print("❌ No Maryles Casto entries found in embedded knowledge base")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing api knowledge base: {e}")
        return False

def test_person_detection():
    """Test the person detection logic"""
    print("\nTesting person detection logic...")
    
    try:
        from api.index import check_knowledge_base_for_person, get_cached_knowledge
        
        knowledge_entries = get_cached_knowledge()
        
        # Test various name variations
        test_cases = [
            "who is Maryle Casto",  # Missing 's'
            "who is Maryles Casto",  # Correct
            "tell me about Maryles",  # Partial name
            "who is Marc Casto",     # Another person
        ]
        
        for test_case in test_cases:
            result = check_knowledge_base_for_person(test_case, knowledge_entries)
            if result:
                print(f"✅ '{test_case}' -> Found: {result[:100]}...")
            else:
                print(f"❌ '{test_case}' -> No result found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing person detection: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("KNOWLEDGE BASE FIX VERIFICATION")
    print("=" * 60)
    
    kb_file_ok = test_knowledge_base_file()
    api_kb_ok = test_api_knowledge_base()
    person_detection_ok = test_person_detection()
    
    print("\n" + "=" * 60)
    if kb_file_ok and api_kb_ok and person_detection_ok:
        print("🎉 ALL TESTS PASSED - Knowledge base should work correctly!")
    else:
        print("❌ SOME TESTS FAILED - Check the issues above")
    print("=" * 60)
