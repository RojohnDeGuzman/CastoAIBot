#!/usr/bin/env python3
"""
Local test script to verify knowledge base logic
"""

def test_knowledge_base_logic():
    """Test the knowledge base logic locally"""
    
    print("🧪 Testing Knowledge Base Logic Locally")
    print("=" * 50)
    
    # Simulate the knowledge base entries
    knowledge_entries = [
        {
            "question": "Who is Maryles Casto?",
            "answer": "MARYLES CASTO - Founder & Chairperson. After 40+ years of traversing through the travel industry's ebbs and flows; and changes in Silicon Valley, Maryles sold Casto Travel to Flight Centre, one of the world's largest travel companies. She continues to own Casto Travel Philippines, providing knowledge, insight, and inspiration in several capacities, including client interactions, organizing exclusive journeys, and steering the company with her leadership and strategic vision."
        },
        {
            "question": "What is Casto Travel Philippines?",
            "answer": "Casto Travel Philippines is a leading travel and tourism company in the Philippines, part of the Casto Group. They offer domestic and international travel packages, hotel bookings, tour packages, travel insurance, corporate travel management, and group travel arrangements."
        }
    ]
    
    # Test the fuzzy matching logic
    def check_knowledge_base_for_person(user_input, knowledge_entries):
        """Local version of the knowledge base check"""
        user_input_lower = user_input.lower()
        
        print(f"🔍 Checking: '{user_input}'")
        
        # Name variations
        name_variations = {
            "maryle": "maryles casto",  # Missing 's'
            "maryles": "maryles casto", 
        }
        
        # Step 1: Check for exact matches
        casto_personnel = ["maryles casto", "marc casto"]
        for person in casto_personnel:
            if person in user_input_lower:
                print(f"✅ Exact match: '{person}'")
                for entry in knowledge_entries:
                    if person in entry.get('question', '').lower() or person in entry.get('answer', '').lower():
                        print(f"🎯 Found KB entry: {entry.get('answer', '')[:100]}...")
                        return entry.get('answer', '')
        
        # Step 2: Try fuzzy matching
        for variation, full_name in name_variations.items():
            if variation in user_input_lower:
                print(f"🔍 Fuzzy match: '{variation}' -> '{full_name}'")
                for entry in knowledge_entries:
                    if full_name in entry.get('question', '').lower() or full_name in entry.get('answer', '').lower():
                        print(f"🎯 Found KB entry via fuzzy match: {entry.get('answer', '')[:100]}...")
                        return entry.get('answer', '')
        
        print("❌ No KB entry found")
        return None
    
    # Test cases
    test_cases = [
        "who is Maryles Casto?",
        "who is Maryle Casto?",  # Missing 's'
        "tell me about Maryles Casto",
        "what is Casto Travel Philippines?"
    ]
    
    print(f"\n📊 Knowledge Base has {len(knowledge_entries)} entries")
    
    for test_case in test_cases:
        print(f"\n{'='*30}")
        result = check_knowledge_base_for_person(test_case, knowledge_entries)
        if result:
            print(f"✅ SUCCESS: Query '{test_case}' returned KB result")
        else:
            print(f"❌ FAILED: Query '{test_case}' returned no result")
    
    print(f"\n{'='*50}")
    print("🏁 Local Testing Complete!")

if __name__ == "__main__":
    test_knowledge_base_logic()
