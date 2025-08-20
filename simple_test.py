# Simple test
user_input = "who is Maryle Casto?"
user_input_lower = user_input.lower()

print(f"Input: '{user_input}'")
print(f"Lower: '{user_input_lower}'")
print(f"'maryle' in input: {'maryle' in user_input_lower}")
print(f"'maryles casto' in input: {'maryles casto' in user_input_lower}")

# Test the variation
if "maryle" in user_input_lower:
    print("✅ 'maryle' found!")
else:
    print("❌ 'maryle' NOT found!")
