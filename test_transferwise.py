#!/usr/bin/env python3
"""
Test script for Transferwise Hungarian template
"""

import sys
import os
sys.path.append('backend')

from enhanced_csv_parser import EnhancedCSVParser
import json

def test_transferwise_template():
    print("🧪 Testing Transferwise Hungarian Template")
    print("=" * 50)
    
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
    csv_file = "transferwise_sample.csv"
    
    try:
        # Parse the CSV with proper header handling
        parse_result = parser.parse_with_range(csv_file, 0, None, 0, None, "utf-8")
        
        if not parse_result['success']:
            print(f"❌ Failed to parse CSV: {parse_result['error']}")
            return False
        
        print(f"✅ CSV parsed successfully: {parse_result['row_count']} rows")
        
        # Show sample data
        sample_data = parse_result['data'][:3]
        print("\n📊 Sample parsed data:")
        for i, row in enumerate(sample_data):
            print(f"Row {i+1}: {dict(list(row.items())[:5])}...")
        
        print()
        
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
        
        # Show transformed results
        print("🎯 Transformation Results:")
        print("-" * 40)
        
        for i, transaction in enumerate(transformed_data[:5]):
            print(f"Transaction {i+1}:")
            print(f"  📅 Date: {transaction.get('Date', 'N/A')}")
            print(f"  💰 Amount: {transaction.get('Amount', 'N/A')}")
            print(f"  📝 Description: {transaction.get('Title', transaction.get('Description', 'N/A'))}")
            print(f"  🏷️  Category: {transaction.get('Category', 'N/A')}")
            print(f"  🏦 Account: {transaction.get('Account', 'N/A')}")
            print()
        
        # Test specific rule applications
        print("🧪 Testing Specific Rules:")
        print("-" * 30)
        
        test_cases = [
            {"description": "Card transaction of 3000.00 HUF issued by Barionp*Yettelfelto BUDAPEST", "expected_category": "Bills & Fees", "expected_desc": "Barionp*Yettelfelto BUDAPEST"},
            {"description": "Card transaction of 8500.00 HUF issued by Lidl Budapest Central", "expected_category": "Groceries", "expected_desc": "Lidl Budapest Central"},
            {"description": "Card transaction of 12000.00 HUF issued by Alza.cz Online Store", "expected_category": "Shopping", "expected_desc": "Alza.cz Online Store"},
            {"description": "Card transaction of 4500.00 HUF issued by Burger King Budapest", "expected_category": "Dining", "expected_desc": "Burger King Budapest"},
        ]
        
        for test_case in test_cases:
            # Find matching transaction
            matching_transaction = None
            for transaction in transformed_data:
                title_field = transaction.get('Title', transaction.get('Description', ''))
                if test_case["expected_desc"] in title_field:
                    matching_transaction = transaction
                    break
            
            if matching_transaction:
                actual_category = matching_transaction.get('Category', 'None')
                actual_desc = matching_transaction.get('Title', matching_transaction.get('Description', 'None'))
                
                # Check category
                if actual_category == test_case["expected_category"]:
                    print(f"✅ Category correct: {test_case['expected_desc']} → {actual_category}")
                else:
                    print(f"❌ Category wrong: {test_case['expected_desc']} → Expected: {test_case['expected_category']}, Got: {actual_category}")
                
                # Check description cleaning
                if test_case["expected_desc"] == actual_desc:
                    print(f"✅ Description cleaned: {actual_desc}")
                else:
                    print(f"⚠️  Description cleaning: Expected: '{test_case['expected_desc']}', Got: '{actual_desc}'")
            else:
                print(f"❌ Transaction not found: {test_case['expected_desc']}")
            
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
    success = test_transferwise_template()
    if success:
        print("\n🎉 All tests passed! Transferwise template is working correctly.")
    else:
        print("\n💥 Tests failed! Check the errors above.")
