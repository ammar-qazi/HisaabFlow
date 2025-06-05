#!/usr/bin/env python3

import sys
import os
sys.path.append('/home/ammar/claude_projects/bank_statement_parser')

from transformation.universal_transformer import UniversalTransformer

def test_transferwise_cleaning():
    """Test if Transferwise description cleaning works correctly"""
    print("🧪 Testing Transferwise Description Cleaning")
    
    # Initialize transformer
    transformer = UniversalTransformer()
    
    # Test sample Transferwise data with card transactions
    test_data = [
        {
            'Date': '2025-06-01',
            'Amount': -3000.0,
            'Description': 'Card transaction of 3,000.00 HUF issued by Barionpay Kft',
            'Payment Reference': 'card',
            'Currency': 'HUF'
        },
        {
            'Date': '2025-06-01',
            'Amount': -1500.0,
            'Description': 'Card transaction of 3,546.00 HUF issued by Lidl Hu 108 Cegled Cegled',
            'Payment Reference': 'card',
            'Currency': 'HUF'
        },
        {
            'Date': '2025-06-01',
            'Amount': -2000.0,
            'Description': 'Sent money to Usama Qazi',
            'Payment Reference': 'transfer',
            'Currency': 'USD'
        },
        {
            'Date': '2025-06-01',
            'Amount': 5000.0,
            'Description': 'Received money from The Blogsmith LLC with reference payment',
            'Payment Reference': 'income',
            'Currency': 'USD'
        }
    ]
    
    column_mapping = {
        'Date': 'Date',
        'Amount': 'Amount', 
        'Title': 'Description',
        'Note': 'Payment Reference',
        'Account': 'Currency'
    }
    
    # Test with all rules enabled
    print(f"\n📊 Testing with bank rules enabled:")
    result = transformer.transform_to_cashew(
        test_data, column_mapping, "Transferwise", None, {
            'enableNayaPayRules': True,
            'enableTransferwiseRules': True,
            'enableUniversalRules': True
        }
    )
    
    print(f"\n✅ **FULL RESULTS:**")
    for i, row in enumerate(result):
        print(f"   Row {i}:")
        print(f"      Category: {row['Category']}")
        print(f"      Title: '{row['Title']}'")
        print(f"      Amount: {row['Amount']}")
        print(f"      Account: {row['Account']}")
        print()
    
    # Test with Transferwise rules disabled  
    print(f"\n📊 Testing with Transferwise rules DISABLED:")
    result2 = transformer.transform_to_cashew(
        test_data, column_mapping, "Transferwise", None, {
            'enableNayaPayRules': True,
            'enableTransferwiseRules': False,
            'enableUniversalRules': True
        }
    )
    
    print(f"\n✅ **RESULTS (Transferwise disabled):**")
    for i, row in enumerate(result2):
        print(f"   Row {i}:")
        print(f"      Category: {row['Category']}")
        print(f"      Title: '{row['Title']}'")
        print(f"      Amount: {row['Amount']}")
        print()

if __name__ == "__main__":
    test_transferwise_cleaning()
