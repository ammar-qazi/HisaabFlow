#!/usr/bin/env python3

import sys
import os
sys.path.append('transformation')

from universal_transformer import UniversalTransformer

def debug_rule_matching():
    """Debug why specific rule conditions aren't matching"""
    print("🔍 Debugging Rule Condition Matching")
    
    # Manually check the conditions
    test_data = {
        'Date': '2025-02-07', 
        'Amount': -500.0,
        'Title': 'Outgoing fund transfer to Muhammad Ali - ride driver',
        'Note': 'Raast Out'
    }
    
    print(f"\\n📋 Test data:")
    for key, value in test_data.items():
        print(f"   {key}: '{value}' (type: {type(value)})")
    
    # Check the ride-hailing rule conditions manually
    print(f"\\n🧪 Manual condition checking:")
    
    # Condition 1: Note equals "Raast Out"
    note_match = str(test_data['Note']).lower() == "raast out"
    print(f"   Note equals 'Raast Out': {note_match}")
    
    # Condition 2: Amount range -2000 to -100
    amount = float(test_data['Amount'])
    amount_match = -2000 <= amount <= -100
    print(f"   Amount in range [-2000, -100]: {amount_match} (amount: {amount})")
    
    # Condition 3: Title contains "driver"
    title = str(test_data['Title']).lower()
    driver_match = "driver" in title
    print(f"   Title contains 'driver': {driver_match}")
    print(f"   Title: '{title}'")
    
    # All conditions should be True
    all_match = note_match and amount_match and driver_match
    print(f"\\n🎯 ALL CONDITIONS MATCH: {all_match}")
    
    if all_match:
        print("✅ The ride-hailing rule SHOULD trigger!")
        print("❓ There might be an issue with rule processing order or logic.")
    else:
        print("❌ Some conditions don't match - this explains why the rule doesn't trigger.")
    
    # Now let's check what the Default rule conditions are
    print(f"\\n🔍 Default rule conditions:")
    # Default rule: Note equals "Raast Out" AND Amount < 0
    default_note_match = str(test_data['Note']).lower() == "raast out"
    default_amount_match = float(test_data['Amount']) < 0
    default_all_match = default_note_match and default_amount_match
    
    print(f"   Note equals 'Raast Out': {default_note_match}")
    print(f"   Amount < 0: {default_amount_match}")
    print(f"   Default rule matches: {default_all_match}")
    
    print(f"\\n💡 Conclusion:")
    if all_match and default_all_match:
        print("   Both rules match! The ride-hailing rule should run first (priority 2 vs 5)")
        print("   This suggests a bug in rule priority processing.")
    else:
        print("   Only one rule matches, which explains the behavior.")

if __name__ == "__main__":
    debug_rule_matching()
