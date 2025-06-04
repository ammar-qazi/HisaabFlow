#!/usr/bin/env python3

import sys
import os
import json

# Add the backend directory to the path
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from enhanced_csv_parser import EnhancedCSVParser

def test_surraiya_specific():
    """Test specifically the Surraiya rule issue"""
    
    print("🔍 Testing Surraiya Rule Specifically")
    print("=" * 50)
    
    # Initialize parser
    parser = EnhancedCSVParser()
    
    # Load the NayaPay Enhanced Template
    template_path = "/home/ammar/claude_projects/bank_statement_parser/templates/NayaPay_Enhanced_Template.json"
    with open(template_path, 'r') as f:
        template = json.load(f)
    
    # Test data with Surraiya
    surraiya_row = {
        'TIMESTAMP': '05 Mar 2025 11:54 PM',
        'TYPE': 'Raast Out',
        'DESCRIPTION': 'Outgoing fund transfer to Surraiya Riaz (Asaan Ac)\nMeezan Bank-2660|Transaction ID 67c89de7380c9e24a2e7e92b',
        'AMOUNT': '-5,000',
        'BALANCE': '16,022.40'
    }
    
    # Create cashew row as it would be initially
    cashew_row = {
        'Date': parser._parse_date(surraiya_row['TIMESTAMP']),
        'Amount': parser._parse_amount(surraiya_row['AMOUNT']),
        'Category': '',
        'Title': surraiya_row['DESCRIPTION'],  # Start with original description
        'Note': surraiya_row['TYPE'],
        'Account': 'NayaPay'
    }
    
    print(f"Initial cashew row: {cashew_row}")
    print()
    
    # Get categorization rules sorted by priority
    rules = template.get('categorization_rules', [])
    sorted_rules = sorted(rules, key=lambda x: x.get('priority', 999))
    
    print("📋 Processing Rules Step by Step:")
    print("-" * 40)
    
    for i, rule in enumerate(sorted_rules):
        rule_name = rule.get('rule_name', f'Rule {i}')
        priority = rule.get('priority', 999)
        conditions = rule.get('conditions', {})
        actions = rule.get('actions', {})
        
        print(f"\nRule {priority}: {rule_name}")
        
        # Check if conditions are met
        condition_met = parser._check_rule_conditions(surraiya_row, conditions)
        print(f"   Conditions met: {condition_met}")
        
        if condition_met:
            print(f"   Actions: {actions}")
            print("   ✅ APPLYING RULE")
            
            # Apply the actions to see what happens
            if 'set_category' in actions:
                old_category = cashew_row['Category']
                cashew_row['Category'] = actions['set_category']
                print(f"      Category: '{old_category}' → '{actions['set_category']}'")
            
            if 'set_title' in actions:
                old_title = cashew_row['Title']
                cashew_row['Title'] = actions['set_title']
                print(f"      Title: '{old_title}' → '{actions['set_title']}'")
            
            if 'clean_description' in actions:
                old_title = cashew_row['Title']
                # Simulate the clean description logic
                cleaned_desc = parser._clean_description(surraiya_row, actions['clean_description'])
                print(f"      clean_description would set title to: '{cleaned_desc}'")
                
                # Check if we should apply it (logic from the fix)
                if not cashew_row['Title'] or cashew_row['Title'] == surraiya_row['DESCRIPTION']:
                    cashew_row['Title'] = cleaned_desc
                    print(f"      Applied clean_description: '{old_title}' → '{cleaned_desc}'")
                else:
                    print(f"      SKIPPED clean_description (title already set by higher priority rule)")
            
            # Check if we should continue processing
            continue_processing = actions.get('continue_processing', False)
            print(f"      Continue processing: {continue_processing}")
            
            if not continue_processing:
                print("   🛑 Stopping rule processing")
                break
            else:
                print("   ➡️ Continuing to next rule")
        else:
            print("   ❌ Conditions not met, skipping")
    
    print(f"\n🎯 FINAL RESULT:")
    print(f"   Category: '{cashew_row['Category']}'")
    print(f"   Title: '{cashew_row['Title']}'")
    
    # Compare with actual method call
    print(f"\n🔍 COMPARING WITH ACTUAL METHOD:")
    actual_result = parser._apply_categorization_rules(
        {
            'Date': parser._parse_date(surraiya_row['TIMESTAMP']),
            'Amount': parser._parse_amount(surraiya_row['AMOUNT']),
            'Category': '',
            'Title': surraiya_row['DESCRIPTION'],
            'Note': surraiya_row['TYPE'],
            'Account': 'NayaPay'
        },
        surraiya_row,
        template.get('categorization_rules', []),
        template.get('default_category_rules')
    )
    
    print(f"   Actual result: {actual_result}")
    
    if actual_result['Title'] == 'Zunayyara Quran':
        print("   ✅ SUCCESS: Surraiya rule applied correctly!")
    else:
        print("   ❌ FAILED: Surraiya rule not applied correctly")

if __name__ == "__main__":
    test_surraiya_specific()
