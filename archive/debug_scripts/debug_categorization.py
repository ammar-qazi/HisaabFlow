#!/usr/bin/env python3
"""
Debug script to isolate and fix NayaPay categorization rule issues
This script tests the exact data flow from your screenshot
"""

import json
import sys
import os

# Add the backend path
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from enhanced_csv_parser import EnhancedCSVParser

def main():
    print("🔍 Debug: NayaPay Categorization Rules")
    print("=" * 60)
    
    # Load the enhanced template
    template_path = "/home/ammar/claude_projects/bank_statement_parser/templates/NayaPay_Enhanced_Template.json"
    
    with open(template_path, 'r') as f:
        template = json.load(f)
    
    print(f"📋 Template loaded: {template['bank_name']} v{template['version']}")
    print(f"🔧 Categorization rules: {len(template['categorization_rules'])}")
    
    # Create test data based on your screenshot
    test_transactions = [
        {
            "TIMESTAMP": "2025-02-05 09:17:00",
            "AMOUNT": "-2000.0",
            "TYPE": "Raast Out",
            "DESCRIPTION": "Mobile top-up purchased|Zong 030...",
            "CURRENCY": "PKR"
        },
        {
            "TIMESTAMP": "2025-02-05 09:19:00", 
            "AMOUNT": "-2000.0",
            "TYPE": "Raast Out",
            "DESCRIPTION": "Mobile top-up purchased|Jazz 030...",
            "CURRENCY": "PKR"
        },
        {
            "TIMESTAMP": "2025-02-07 13:47:00",
            "AMOUNT": "-400.0", 
            "TYPE": "Raast Out",
            "DESCRIPTION": "Transfer to Usman Siddique easypaisa|Transaction ID ABC123",
            "CURRENCY": "PKR"
        },
        {
            "TIMESTAMP": "2025-02-02 23:17:00",
            "AMOUNT": "-5000.0",
            "TYPE": "Transfer",
            "DESCRIPTION": "Transfer contains Surraiya Riaz somewhere",
            "CURRENCY": "PKR"
        }
    ]
    
    # Initialize parser
    parser = EnhancedCSVParser()
    
    print("\n🧪 Testing categorization rules:")
    print("-" * 40)
    
    for i, transaction in enumerate(test_transactions):
        print(f"\n📊 Transaction {i+1}:")
        print(f"   Amount: {transaction['AMOUNT']}")
        print(f"   Type: {transaction['TYPE']}")
        print(f"   Description: {transaction['DESCRIPTION'][:50]}...")
        
        # Create a cashew row template
        cashew_row = {
            'Date': transaction['TIMESTAMP'],
            'Amount': transaction['AMOUNT'],
            'Category': '',
            'Title': '',
            'Note': transaction['TYPE'],
            'Account': 'NayaPay'
        }
        
        # Apply categorization rules
        result = parser._apply_categorization_rules(
            cashew_row, 
            transaction, 
            template['categorization_rules'],
            template['default_category_rules']
        )
        
        print(f"   ✅ Result Category: {result['Category']}")
        print(f"   ✅ Result Title: {result['Title']}")
        
        # Now let's debug WHY this happened
        print(f"   🔍 Rule matching analysis:")
        
        # Test each rule manually
        sorted_rules = sorted(template['categorization_rules'], key=lambda x: x.get('priority', 999))
        
        for rule in sorted_rules:
            rule_name = rule.get('rule_name', 'Unknown Rule')
            conditions = rule.get('conditions', {})
            
            # Check if this rule matches
            matches = parser._check_rule_conditions(transaction, conditions)
            
            if matches:
                print(f"      ✅ MATCHED: {rule_name} (priority {rule.get('priority', 'N/A')})")
                actions = rule.get('actions', {})
                if 'set_category' in actions:
                    print(f"         -> Would set category: {actions['set_category']}")
                if 'set_title' in actions:
                    print(f"         -> Would set title: {actions['set_title']}")
                
                # Check if processing should continue
                if not actions.get('continue_processing', False):
                    print(f"         -> STOPS processing here (continue_processing: {actions.get('continue_processing', False)})")
                    break
                else:
                    print(f"         -> CONTINUES processing (continue_processing: True)")
            else:
                print(f"      ❌ No match: {rule_name}")
                
                # Debug WHY it didn't match
                if 'and' in conditions:
                    print(f"         Checking AND conditions:")
                    for cond in conditions['and']:
                        field = cond.get('field')
                        operator = cond.get('operator')
                        value = cond.get('value')
                        field_value = transaction.get(field, 'MISSING')
                        
                        condition_result = parser._check_single_condition(transaction, cond)
                        print(f"           - {field} {operator} '{value}': {field_value} -> {condition_result}")
                
                elif 'or' in conditions:
                    print(f"         Checking OR conditions:")
                    for cond in conditions['or']:
                        field = cond.get('field')
                        operator = cond.get('operator')
                        value = cond.get('value')
                        field_value = transaction.get(field, 'MISSING')
                        
                        condition_result = parser._check_single_condition(transaction, cond)
                        print(f"           - {field} {operator} '{value}': {field_value} -> {condition_result}")
        
        print("-" * 40)

if __name__ == "__main__":
    main()
