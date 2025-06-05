#!/usr/bin/env python3
"""
Debug the Universal Transformer issues
"""

import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'transformation'))

from universal_transformer import UniversalTransformer

def debug_wise_categorization():
    """Debug why Wise items aren't being categorized properly"""
    print("🔍 DEBUGGING WISE CATEGORIZATION")
    
    # Initialize transformer
    transformer = UniversalTransformer()
    
    # Sample Wise data
    wise_data = [
        {
            'Date': '2024-03-02',
            'Amount': -8500.0,
            'Description': 'Card transaction of 8500.00 HUF issued by Lidl Budapest Central',
            'Payment Reference': 'REF002',
            'Currency': 'HUF'
        }
    ]
    
    column_mapping = {
        'Date': 'Date',
        'Amount': 'Amount',
        'Title': 'Description',
        'Note': 'Payment Reference',
        'Account': 'Currency'
    }
    
    account_mapping = {
        'HUF': 'Hungarian',
        'USD': 'TransferWise',
        'EUR': 'EURO Wise'
    }
    
    print(f"📊 Input data: {wise_data[0]}")
    print(f"🗺️  Column mapping: {column_mapping}")
    
    # Map to cashew format first
    mapped_row = transformer._map_to_cashew_format(
        wise_data[0], column_mapping, "Wise", account_mapping
    )
    print(f"🔄 Mapped row: {mapped_row}")
    
    # Get rules for Wise
    bank_rules = transformer._get_bank_override_rules('wise')
    print(f"📋 Number of rules: {len(bank_rules)}")
    
    # Test individual rules
    for i, rule in enumerate(bank_rules[:5]):  # First 5 rules
        rule_name = rule.get('rule_name', f'Rule {i}')
        conditions = rule.get('conditions', {})
        
        print(f"\\n📝 Testing rule: {rule_name}")
        print(f"   Conditions: {conditions}")
        
        # Test the rule
        matches = transformer._check_rule_conditions(mapped_row, wise_data[0], conditions)
        print(f"   Matches: {matches}")
        
        if matches:
            print(f"   ✅ RULE MATCHES!")
            actions = rule.get('actions', {})
            print(f"   Actions: {actions}")
            break
    
    # Test full transformation
    print(f"\\n🔄 Full transformation test:")
    result = transformer.transform_to_cashew(
        wise_data, column_mapping, "Wise", account_mapping
    )
    
    print(f"📊 Final result: {result[0]}")

def debug_rule_matching():
    """Debug why specific rules aren't matching"""
    print("\\n🔍 DEBUGGING RULE MATCHING")
    
    # Test a simple Lidl case
    test_row = {
        'Date': '2024-03-02',
        'Amount': -8500.0,
        'Title': 'Card transaction of 8500.00 HUF issued by Lidl Budapest Central',
        'Note': 'REF002',
        'Account': 'Hungarian'
    }
    
    print(f"📊 Test row: {test_row}")
    
    # Test the Groceries rule manually
    title_contains_lidl = 'lidl' in test_row['Title'].lower()
    print(f"🔍 Title contains 'lidl': {title_contains_lidl}")
    
    # Look at the universal rules
    with open('transformation/rules/universal_rules.json', 'r') as f:
        rules_data = json.load(f)
    
    groceries_rule = None
    for rule in rules_data['rules']:
        if 'Groceries' in rule.get('rule_name', ''):
            groceries_rule = rule
            break
    
    if groceries_rule:
        print(f"\\n📝 Groceries rule found:")
        print(f"   {groceries_rule}")
        
        # Test the conditions manually
        conditions = groceries_rule.get('conditions', {})
        if 'or' in conditions:
            for condition in conditions['or']:
                field = condition.get('field')
                value = condition.get('value')
                print(f"   Testing: {field} contains '{value}'")
                if field in test_row:
                    field_value = str(test_row[field]).lower()
                    contains_value = value.lower() in field_value
                    print(f"   Result: '{value}' in '{field_value}' = {contains_value}")

if __name__ == "__main__":
    debug_wise_categorization()
    debug_rule_matching()
