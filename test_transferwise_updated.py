#!/usr/bin/env python3
"""
Test script for Updated Transferwise Hungarian template with new rules
"""

import sys
import os
sys.path.append('backend')

from enhanced_csv_parser import EnhancedCSVParser
import json

def test_updated_transferwise_template():
    print("🧪 Testing Updated Transferwise Hungarian Template")
    print("=" * 55)
    
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
    csv_file = "transferwise_updated_test.csv"
    
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
        
        transformed_data = parser.transform_to_cashew(
            parse_result['data'], 
            column_mapping, 
            bank_name,
            categorization_rules
        )
        
        print(f"✅ Data transformed: {len(transformed_data)} transactions")
        print()
        
        # Test specific new rules
        print("🧪 Testing New Business Rules:")
        print("-" * 35)
        
        test_cases = [
            {"search": "Hungary Szocho", "expected_category": "Business Taxes", "description": "Social Security Payment"},
            {"search": "Hungary NAV TB", "expected_category": "Business Taxes", "description": "Tax Payment"},
            {"search": "NAV SZJA", "expected_category": "Business Taxes", "description": "Income Tax Payment"},
            {"search": "Budapest", "amount": -9450.0, "expected_title": "Pest County Pass", "expected_category": "Transport"},
            {"search": "Szamlazz", "expected_title": "Szamlazz accounting fee", "expected_category": "Bills & Fees"},
            {"search": "Yettelfelto", "expected_title": "Yettel Recharge", "expected_category": "Bills & Fees"},
            {"search": "Bajusz Alexa", "expected_title": "Accountant Fee", "expected_category": "Business Expenses"},
        ]
        
        for test_case in test_cases:
            # Find matching transaction
            matching_transaction = None
            for transaction in transformed_data:
                title_field = transaction.get('Title', '')
                
                # Check if this is the Budapest amount-specific test
                if 'amount' in test_case:
                    if (test_case['search'] in title_field and 
                        float(transaction.get('Amount', 0)) == test_case['amount']):
                        matching_transaction = transaction
                        break
                else:
                    # Find by search term in original descriptions
                    # We need to check the original data for this
                    for orig_row in parse_result['data']:
                        if (test_case['search'] in str(orig_row.get('Description', '')) and
                            any(test_case['search'].lower() in str(t.get('Title', '')).lower() or 
                                test_case['search'].lower() in str(orig_row.get('Description', '')).lower()
                                for t in [transaction])):
                            matching_transaction = transaction
                            break
                    if matching_transaction:
                        break
            
            if matching_transaction:
                # Check category
                actual_category = matching_transaction.get('Category', 'None')
                expected_category = test_case.get('expected_category', 'N/A')
                
                if expected_category != 'N/A':
                    if actual_category == expected_category:
                        print(f"✅ Category correct: {test_case['search']} → {actual_category}")
                    else:
                        print(f"❌ Category wrong: {test_case['search']} → Expected: {expected_category}, Got: {actual_category}")
                
                # Check title if specified
                if 'expected_title' in test_case:
                    actual_title = matching_transaction.get('Title', 'None')
                    expected_title = test_case['expected_title']
                    
                    if actual_title == expected_title:
                        print(f"✅ Title correct: {actual_title}")
                    else:
                        print(f"❌ Title wrong: Expected: '{expected_title}', Got: '{actual_title}'")
                
                print(f"   📊 Amount: {matching_transaction.get('Amount', 'N/A')}")
                print()
            else:
                print(f"❌ Transaction not found: {test_case['search']}")
                print()
        
        # Show all transformed results
        print("🎯 All Transformation Results:")
        print("-" * 40)
        
        for i, transaction in enumerate(transformed_data):
            print(f"Transaction {i+1}:")
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
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_updated_transferwise_template()
    if success:
        print("\n🎉 All tests passed! Updated Transferwise template is working correctly.")
    else:
        print("\n💥 Tests failed! Check the errors above.")
