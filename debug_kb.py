#!/usr/bin/env python3
"""
Debug script to test knowledge base lookup step by step
"""

def test_knowledge_base_lookup():
    """Test the knowledge base lookup logic"""
    
    # Simulate the knowledge base entries
    knowledge_entries = [
        {
            "question": "Who is Maryles Casto?",
            "answer": "MARYLES CASTO - Founder & Chairperson. After 40+ years of traversing through the travel industry's ebbs and flows; and changes in Silicon Valley, Maryles sold Casto Travel to Flight Centre, one of the world's largest travel companies. She continues to own Casto Travel Philippines, providing knowledge, insight, and inspiration in several capacities, including client interactions, organizing exclusive journeys, and steering the company with her leadership and strategic vision."
        }
    ]
    
    # Test user input
    user_input = "who is Maryle Casto?"
    user_input_lower = user_input.lower()
    
    print(f"User input: '{user_input}'")
    print(f"User input lower: '{user_input_lower}'")
    
    # Test the name variations logic
    name_variations = {
        "maryle": "maryles casto",  # Missing 's'
        "maryles": "maryles casto", 
    }
    
    print(f"\nTesting name variations:")
    for variation, full_name in name_variations.items():
        if variation in user_input_lower:
            print(f"✅ MATCH: '{variation}' -> '{full_name}'")
            
            # Now test if we can find the knowledge base entry
            found = False
            for entry in knowledge_entries:
                if isinstance(entry, dict):
                    entry_question = entry.get('question', '').lower()
                    entry_answer = entry.get('answer', '').lower()
                    
                    if full_name in entry_question or full_name in entry_answer:
                        print(f"✅ Found KB entry: {entry.get('answer', '')[:100]}...")
                        found = True
                        break
            
            if not found:
                print(f"❌ No KB entry found for '{full_name}'")
        else:
            print(f"❌ NO MATCH: '{variation}' not in '{user_input_lower}'")
    
    # Test the casto_personnel logic
    casto_personnel = [
        "maryles casto", "marc casto"
    ]
    
    print(f"\nTesting casto_personnel:")
    for person in casto_personnel:
        if person in user_input_lower:
            print(f"✅ MATCH: '{person}' found in '{user_input_lower}'")
        else:
            print(f"❌ NO MATCH: '{person}' not in '{user_input_lower}'")

if __name__ == "__main__":
    test_knowledge_base_lookup()
