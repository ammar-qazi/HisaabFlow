#!/usr/bin/env python3

import sys
import os
import json

# Add the backend directory to the path
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from enhanced_csv_parser import EnhancedCSVParser

def debug_rule_application():
    """Debug the rule application process step by step"""
    
    print("🔍 DEBUGGING RULE APPLICATION PROCESS")
    print("=" * 50)
    
    # Initialize parser
    parser = EnhancedCSVParser()
    
    # Load the NayaPay Enhanced Template
    template_path = "/home/ammar/claude_projects/bank_statement_parser/templates/NayaPay_Enhanced_Template.json"
    with open(template_path, 'r') as f:
        template = json.load(f)
    
    # Test with a small ride-hailing transaction
    test_row_original = {
        'TIMESTAMP': '15 Mar 2025 02:30 PM',
        'TYPE': 'Raast Out',
        'DESCRIPTION': 'Outgoing fund transfer to Careem\nCareem-1234|Transaction ID abc123',
        'AMOUNT': '-400',
        'BALANCE': '20,622.40'
    }
    
    # Create cashew row as it would be initially
    cashew_row = {
        'Date': parser._parse_date(test_row_original['TIMESTAMP']),
        'Amount': parser._parse_amount(test_row_original['AMOUNT']),
        'Category': '',
        'Title': test_row_original['DESCRIPTION'],
        'Note': test_row_original['TYPE'],
        'Account': 'NayaPay'
    }
    
    print("🚗 Testing Ride Hailing Transaction:")
    print(f"   Original: {test_row_original}")
    print(f"   Initial Cashew Row: {cashew_row}")
    print()
    
    # Get categorization rules sorted by priority
    rules = template.get('categorization_rules', [])
    sorted_rules = sorted(rules, key=lambda x: x.get('priority', 999))
    
    print("📋 Checking Rules by Priority:")
    print("-" * 40)
    
    for i, rule in enumerate(sorted_rules):
        rule_name = rule.get('rule_name', f'Rule {i}')
        priority = rule.get('priority', 999)
        conditions = rule.get('conditions', {})
        actions = rule.get('actions', {})
        
        print(f"Rule {priority}: {rule_name}")
        
        # Check if conditions are met
        condition_met = parser._check_rule_conditions(test_row_original, conditions)
        print(f"   Conditions met: {condition_met}")
        
        if condition_met:
            print(f"   Actions: {actions}")
            print("   ✅ RULE WOULD BE APPLIED")
            
            # Apply the actions to see what happens
            if 'set_category' in actions:
                cashew_row['Category'] = actions['set_category']
                print(f"      Category set to: {actions['set_category']}")
            
            if 'set_title' in actions:
                cashew_row['Title'] = actions['set_title']
                print(f"      Title set to: {actions['set_title']}")
            
            # Check if we should continue processing
            if not actions.get('continue_processing', False):
                print("   🛑 Stopping rule processing (continue_processing not set)")
                break
            else:
                print("   ➡️ Continuing to next rule")
        else:
            print("   ❌ Conditions not met")
        print()
    
    print("🔍 FINAL CATEGORIZATION CALL:")
    print("-" * 30)
    
    # Now call the actual categorization method
    final_result = parser._apply_categorization_rules(
        {
            'Date': parser._parse_date(test_row_original['TIMESTAMP']),
            'Amount': parser._parse_amount(test_row_original['AMOUNT']),
            'Category': '',
            'Title': test_row_original['DESCRIPTION'],
            'Note': test_row_original['TYPE'],
            'Account': 'NayaPay'
        },
        test_row_original,
        template.get('categorization_rules', []),
        template.get('default_category_rules')
    )
    
    print(f"Final Result: {final_result}")
    
    # Test Surraiya Riaz rule
    print("\n" + "=" * 50)
    print("🔍 TESTING SURRAIYA RIAZ RULE")
    print("=" * 50)
    
    surraiya_row = {
        'TIMESTAMP': '05 Mar 2025 11:54 PM',
        'TYPE': 'Raast Out',
        'DESCRIPTION': 'Outgoing fund transfer to Surraiya Riaz (Asaan Ac)\nMeezan Bank-2660|Transaction ID 67c89de7380c9e24a2e7e92b',
        'AMOUNT': '-5,000',
        'BALANCE': '16,022.40'
    }
    
    print(f"Test row: {surraiya_row}")
    
    # Find the Surraiya rule
    surraiya_rule = None
    for rule in rules:
        if rule['rule_name'] == 'Surraiya Riaz Transactions':
            surraiya_rule = rule
            break
    
    if surraiya_rule:
        print(f"Surraiya Rule: {surraiya_rule}")
        condition_met = parser._check_rule_conditions(surraiya_row, surraiya_rule['conditions'])
        print(f"Condition met: {condition_met}")
        
        # Test the condition manually
        description_text = surraiya_row['DESCRIPTION'].lower()
        contains_surraiya = 'surraiya riaz' in description_text
        print(f"Manual check - Description contains 'surraiya riaz': {contains_surraiya}")
        print(f"Description text: '{description_text}'")

if __name__ == "__main__":
    debug_rule_application()
