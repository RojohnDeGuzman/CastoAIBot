#!/usr/bin/env python3
"""
Debug script to test why "maryle" is not matching "maryles casto"
"""

def test_maryle_matching():
    """Test the fuzzy matching logic"""
    
    # Simulate the user input
    user_input = "who is Maryle Casto?"
    user_input_lower = user_input.lower()
    
    print(f"User input: '{user_input}'")
    print(f"User input lower: '{user_input_lower}'")
    
    # Test the name variations logic
    name_variations = {
        "maryle": "maryles casto",  # Missing 's'
        "maryles": "maryles casto", 
        "marc": "marc casto",
    }
    
    print("\nTesting name variations:")
    for variation, full_name in name_variations.items():
        if variation in user_input_lower:
            print(f"✅ MATCH: '{variation}' -> '{full_name}'")
        else:
            print(f"❌ NO MATCH: '{variation}' not in '{user_input_lower}'")
    
    # Test the casto_personnel logic
    casto_personnel = [
        "maryles casto", "marc casto", "elaine randrup"
    ]
    
    print("\nTesting casto_personnel:")
    for person in casto_personnel:
        if person in user_input_lower:
            print(f"✅ MATCH: '{person}' found in '{user_input_lower}'")
        else:
            print(f"❌ NO MATCH: '{person}' not in '{user_input_lower}'")
    
    # Test the specific case
    print(f"\nSpecific test:")
    print(f"'maryle' in '{user_input_lower}': {'maryle' in user_input_lower}")
    print(f"'maryles casto' in '{user_input_lower}': {'maryles casto' in user_input_lower}")

if __name__ == "__main__":
    test_maryle_matching()
