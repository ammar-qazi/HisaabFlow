#!/usr/bin/env python3
"""
Test script for Transferwise Currency-Based Account Mapping
"""

import sys
import os
sys.path.append('backend')

from enhanced_csv_parser import EnhancedCSVParser
import json

def test_currency_account_mapping():
    print("🧪 Testing Transferwise Currency-Based Account Mapping")
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
        print(f"💱 Account Mapping: {template.get('account_mapping', 'None')}")
        print()
    except Exception as e:
        print(f"❌ Failed to load template: {e}")
        return False
    
    # Parse CSV file
    csv_file = "transferwise_currency_test.csv"
    
    try:
        # Parse the CSV with proper header handling
        parse_result = parser.parse_with_range(csv_file, 0, None, 0, None, "utf-8")
        
        if not parse_result['success']:
            print(f"❌ Failed to parse CSV: {parse_result['error']}")
            return False
        
        print(f"✅ CSV parsed successfully: {parse_result['row_count']} rows")
        
        # Transform to Cashew format with account mapping
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
        
        # Test currency-based account assignment
        print("🧪 Testing Currency-Based Account Assignment:")
        print("-" * 50)
        
        currency_tests = {
            "HUF": "Hungarian",
            "USD": "TransferWise", 
            "EUR": "EURO Wise"
        }
        
        # Group transactions by currency from original data
        currency_groups = {}
        for i, orig_row in enumerate(parse_result['data']):
            currency = orig_row.get('Currency', 'Unknown')
            if currency not in currency_groups:
                currency_groups[currency] = []
            currency_groups[currency].append((i, transformed_data[i]))
        
        # Test each currency
        for currency, expected_account in currency_tests.items():
            if currency in currency_groups:
                transactions = currency_groups[currency]
                print(f"\n💱 {currency} Transactions (Expected Account: {expected_account}):")
                
                for idx, transaction in transactions:
                    actual_account = transaction.get('Account', 'None')
                    amount = transaction.get('Amount', 'N/A')
                    title = transaction.get('Title', 'N/A')[:50]  # Truncate long titles
                    
                    if actual_account == expected_account:
                        print(f"   ✅ Transaction {idx+1}: {title} → Account: {actual_account}")
                    else:
                        print(f"   ❌ Transaction {idx+1}: {title} → Expected: {expected_account}, Got: {actual_account}")
                    print(f"      💰 Amount: {amount} {currency}")
            else:
                print(f"\n⚠️  No {currency} transactions found in test data")
        
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
        
        # Show account distribution
        accounts = {}
        for transaction in transformed_data:
            account = transaction.get('Account', 'Uncategorized')
            accounts[account] = accounts.get(account, 0) + 1
        
        print("📈 Account Distribution:")
        for account, count in sorted(accounts.items()):
            print(f"  {account}: {count} transactions")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_currency_account_mapping()
    if success:
        print("\n🎉 Currency-based account mapping test completed!")
    else:
        print("\n💥 Tests failed! Check the errors above.")
