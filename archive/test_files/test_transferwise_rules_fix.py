#!/usr/bin/env python3

import sys
import os
sys.path.append('/home/ammar/claude_projects/bank_statement_parser')

from transformation.universal_transformer import UniversalTransformer

def test_transferwise_rules():
    """Test that Transferwise rules are properly loaded"""
    print("🧪 Testing Transferwise Rules Loading")
    
    # Initialize transformer
    transformer = UniversalTransformer()
    
    # Test sample Transferwise data
    test_data = [
        {
            'Date': '2025-06-01',
            'Amount': -3000.0,
            'Description': 'Card transaction of 3,000.00 HUF issued by Barionpay Kft',
            'Payment Reference': 'card',
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
    
    print(f"\n📊 Input data: {test_data[0]}")
    
    result = transformer.transform_to_cashew(test_data, column_mapping, "Transferwise")
    
    print(f"\n✅ Output result:")
    for row in result:
        print(f"   📋 Date: {row['Date']}")
        print(f"   💰 Amount: {row['Amount']}")
        print(f"   📂 Category: {row['Category']}")
        print(f"   🏷️  Title: {row['Title']}")
        print(f"   📝 Note: {row['Note']}")
        print(f"   🏦 Account: {row['Account']}")

if __name__ == "__main__":
    test_transferwise_rules()
