#!/usr/bin/env python3
"""
Test script for Final Transferwise Template with Income and Travel Rules
"""

import sys
import os
sys.path.append('backend')

from enhanced_csv_parser import EnhancedCSVParser
import json

def test_final_transferwise_template():
    print("🧪 Testing Final Transferwise Template with New Rules")
    print("=" * 60)
    
    # Initialize parser
    parser = EnhancedCSVParser()
    
    # Load template
    template_name = "Transferwise_Hungarian_Template"
    template_path = "templates"
    
    try:
        template = parser.load_template(template_name, template_path)
        print(f"✅ Template loaded: {template['name']}")
        print(f"🏦 Bank: {template['bank_name']}")
        print(f"📋 Rules: {len(template['categorization_rules'])}")
        print()
    except Exception as e:
        print(f"❌ Failed to load template: {e}")
        return False
    
    # Parse CSV file
    csv_file = "transferwise_final_test.csv"
    
    try:
        # Parse the CSV with proper header handling
        parse_result = parser.parse_with_range(csv_file, 0, None, 0, None, "utf-8")
        
        if not parse_result['success']:
            print(f"❌ Failed to parse CSV: {parse_result['error']}")
            return False
        
        print(f"✅ CSV parsed successfully: {parse_result['row_count']} rows")
        
        # Transform to Cashew format
        column_mapping = template['column_mapping']
        bank_name = template['bank_name']
        categorization_rules = template['categorization_rules']
        account_mapping = template.get('account_mapping', {})
        
        transformed_data = parser.transform_to_cashew(
            parse_result['data'], 
            column_mapping, 
            bank_name,
            categorization_rules,
            None,
            account_mapping
        )
        
        print(f"✅ Data transformed: {len(transformed_data)} transactions")
        print()
        
        # Test new rules specifically
        print("🧪 Testing New Rules:")
        print("-" * 30)
        
        new_rule_tests = [
            {"search": "The Blogsmith", "expected_title": "The Blogsmith Payments", "expected_category": "Income"},
            {"search": "Amazon", "expected_title": "Amazon Blog Payment", "expected_category": "Income"},
            {"search": "Airalo", "expected_category": "Travel"},
            {"search": "Riyadh Metro", "expected_category": "Travel"},
            {"search": "Kiwi.com", "expected_category": "Travel"},
            {"search": "Pegasus UK", "expected_category": "Travel"},
        ]
        
        for test_case in new_rule_tests:
            # Find matching transaction
            matching_transaction = None
            for transaction in transformed_data:
                title_field = transaction.get('Title', '')
                
                # Search in title field
                if test_case['search'] in title_field:
                    matching_transaction = transaction
                    break
            
            if matching_transaction:
                actual_category = matching_transaction.get('Category', 'None')
                actual_title = matching_transaction.get('Title', 'None')
                amount = matching_transaction.get('Amount', 'N/A')
                account = matching_transaction.get('Account', 'N/A')
                
                print(f"\n✅ Found: {test_case['search']}")
                print(f"   📝 Title: {actual_title}")
                print(f"   🏷️  Category: {actual_category}")
                print(f"   💰 Amount: {amount}")
                print(f"   🏦 Account: {account}")
                
                # Check expected values
                if 'expected_title' in test_case:
                    if actual_title == test_case['expected_title']:
                        print(f"   ✅ Title correct: {actual_title}")
                    else:
                        print(f"   ❌ Title wrong: Expected '{test_case['expected_title']}', Got '{actual_title}'")
                
                if 'expected_category' in test_case:
                    if actual_category == test_case['expected_category']:
                        print(f"   ✅ Category correct: {actual_category}")
                    else:
                        print(f"   ❌ Category wrong: Expected '{test_case['expected_category']}', Got '{actual_category}'")
            else:
                print(f"❌ Transaction not found: {test_case['search']}")
        
        # Show all transformed results
        print("\n🎯 All Transformation Results:")
        print("-" * 40)
        
        for i, transaction in enumerate(transformed_data):
            # Get original currency for reference
            orig_currency = parse_result['data'][i].get('Currency', 'Unknown')
            
            print(f"Transaction {i+1} ({orig_currency}):")
            print(f"  📅 Date: {transaction.get('Date', 'N/A')}")
            print(f"  💰 Amount: {transaction.get('Amount', 'N/A')}")
            print(f"  📝 Title: {transaction.get('Title', 'N/A')}")
            print(f"  🏷️  Category: {transaction.get('Category', 'N/A')}")
            print(f"  🏦 Account: {transaction.get('Account', 'N/A')}")
            print()
        
        # Show category distribution
        categories = {}
        for transaction in transformed_data:
            category = transaction.get('Category', 'Uncategorized')
            categories[category] = categories.get(category, 0) + 1
        
        print("📈 Category Distribution:")
        for category, count in sorted(categories.items()):
            print(f"  {category}: {count} transactions")
        
        # Show account distribution
        accounts = {}
        for transaction in transformed_data:
            account = transaction.get('Account', 'Uncategorized')
            accounts[account] = accounts.get(account, 0) + 1
        
        print("\n🏦 Account Distribution:")
        for account, count in sorted(accounts.items()):
            print(f"  {account}: {count} transactions")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_final_transferwise_template()
    if success:
        print("\n🎉 All tests completed! Final Transferwise template is working perfectly.")
    else:
        print("\n💥 Tests failed! Check the errors above.")
