#!/usr/bin/env python3

import sys
import os
sys.path.append('../transformation')

from universal_transformer import UniversalTransformer

def test_wise_real_data():
    """Test Universal Transformer with real Wise data like your backend does"""
    print("🧪 Testing Universal Transformer with Real Wise Data")
    
    # Initialize transformer (will auto-detect rules directory)
    transformer = UniversalTransformer()
    
    # Simulate real Wise data from your log
    wise_data = [
        {
            'Date': '2025-06-01',
            'Amount': -3000.0,
            'Title': 'Card transaction of 3,000.00 HUF issued by Barionp...',
            'Note': 'Payment Reference',
            'Currency': 'HUF'
        },
        {
            'Date': '2025-05-29', 
            'Amount': -6288.0,
            'Title': 'Card transaction of 6,288.00 HUF issued by Lidl Hu...',
            'Note': 'Grocery shopping',
            'Currency': 'HUF'
        },
        {
            'Date': '2025-05-27',
            'Amount': -1892.0,
            'Title': 'Card transaction of 1,892.00 HUF issued by Otpmobl...',
            'Note': 'Mobile payment',
            'Currency': 'HUF'
        }
    ]
    
    # Column mapping used by your backend
    column_mapping = {
        'Date': 'Date',
        'Amount': 'Amount', 
        'Title': 'Title',
        'Note': 'Note',
        'Account': 'Currency'
    }
    
    # Account mapping for multi-currency
    account_mapping = {
        'HUF': 'Hungarian',
        'USD': 'TransferWise',
        'EUR': 'EURO Wise'
    }
    
    print(f"\n🔥 Testing transformation with backend-like setup:")
    print(f"   📊 Input: {len(wise_data)} transactions")
    print(f"   🏦 Bank: Wise")
    print(f"   🗺️  Column mapping: {column_mapping}")
    print(f"   💱 Account mapping: {account_mapping}")
    
    # Run transformation exactly like backend does
    result = transformer.transform_to_cashew(
        wise_data, 
        column_mapping, 
        "Wise", 
        account_mapping
    )
    
    print(f"\n📊 Results:")
    for i, row in enumerate(result):
        print(f"   Row {i}: {row['Category']} - {row['Title']} - {row['Amount']} - Account: {row['Account']}")
    
    print(f"\n🎯 Expected vs Actual:")
    print(f"   ✅ Row 0: Should have cleaned title (not 'Card transaction...')")
    print(f"   ✅ Row 1: Should be categorized as 'Groceries' (Lidl)")
    print(f"   ✅ Row 2: Should be categorized as 'Bills & Fees' (mobile)")
    print(f"   ✅ All: Should have Account='Hungarian' (HUF currency)")

if __name__ == "__main__":
    test_wise_real_data()
