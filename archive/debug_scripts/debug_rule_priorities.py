#!/usr/bin/env python3

import sys
import os
sys.path.append('transformation')

from universal_transformer import UniversalTransformer

def debug_rule_priorities():
    """Debug why rule priorities aren't working correctly"""
    print("🔍 Debugging Rule Priorities")
    
    transformer = UniversalTransformer()
    
    # Check what rules are loaded and in what order
    bank_key = "nayapay"
    if bank_key in transformer.bank_overrides:
        bank_data = transformer.bank_overrides[bank_key]
        overrides = bank_data.get('overrides', bank_data)
        
        print(f"\\n📋 Bank override structure:")
        for category_name, rules_list in overrides.items():
            if isinstance(rules_list, list):
                print(f"   {category_name}: {len(rules_list)} rules")
                for rule in rules_list:
                    print(f"      - {rule.get('rule_name', 'Unnamed')} (priority: {rule.get('priority', 'None')})")
    
    # Get the actual combined rules that would be used
    combined_rules = transformer._get_bank_override_rules(bank_key)
    
    print(f"\\n🔗 Combined rules in processing order:")
    for i, rule in enumerate(combined_rules[:10]):  # Show first 10
        rule_name = rule.get('rule_name', f'Rule_{i}')
        priority = rule.get('priority', 'None')
        print(f"   {i+1:2}. {rule_name} (priority: {priority})")
    
    print(f"\\n🧪 Test single transaction:")
    # Test with one ride-hailing transaction
    test_data = [{
        'Date': '2025-02-07', 
        'Amount': -500.0,
        'Title': 'Outgoing fund transfer to Muhammad Ali - ride driver',
        'Note': 'Raast Out'
    }]
    
    column_mapping = {'Date': 'Date', 'Amount': 'Amount', 'Title': 'Title', 'Note': 'Note'}
    
    # This should trigger the ride-hailing rule (priority 2) not the default rule (priority 5)
    result = transformer.transform_to_cashew(test_data, column_mapping, "NayaPay")
    
    print(f"\\n📊 Result:")
    print(f"   Category: {result[0]['Category']} (should be Travel)")
    print(f"   Title: {result[0]['Title']} (should contain 'Ride payment')")

if __name__ == "__main__":
    debug_rule_priorities()
