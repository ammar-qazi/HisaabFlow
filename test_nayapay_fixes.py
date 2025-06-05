#!/usr/bin/env python3

import sys
import os
sys.path.append('transformation')

from universal_transformer import UniversalTransformer

def test_nayapay_fixes():
    """Test the fixed NayaPay rules with problematic transactions"""
    print("🧪 Testing Fixed NayaPay Rules")
    
    transformer = UniversalTransformer()
    
    # Test problematic transactions from your log
    nayapay_data = [
        {
            'Date': '2025-02-05',
            'Amount': -23000.0,  # This should be Transfer (large Raast Out)
            'Title': 'Outgoing fund transfer to Ammar Qazi Meezan Bank-3212',
            'Note': 'Raast Out'
        },
        {
            'Date': '2025-02-07', 
            'Amount': -400.0,    # This should be Transfer (small fund transfer)
            'Title': 'Outgoing fund transfer to Usman Siddique easypaisa Bank-9171',
            'Note': 'Peer to Peer'
        },
        {
            'Date': '2025-02-08',
            'Amount': -1500.0,   # This should be Transfer (medium fund transfer) 
            'Title': 'Outgoing fund transfer to Muhammad Sajid easypaisa Bank-7717',
            'Note': 'Peer to Peer'
        },
        {
            'Date': '2025-02-05',
            'Amount': -2000.0,   # This should be Bills & Fees (mobile)
            'Title': 'Mobile top-up purchased|Jazz 03016190816 Nickname: Zunayyar',
            'Note': 'Mobile Top-up'
        },
        {
            'Date': '2025-02-02',
            'Amount': -5000.0,   # This should use specific contact rule 
            'Title': 'Outgoing fund transfer to Surraiya Riaz easypaisa Bank-5000',
            'Note': 'Peer to Peer'
        }
    ]
    
    column_mapping = {
        'Date': 'Date',
        'Amount': 'Amount',
        'Title': 'Title', 
        'Note': 'Note'
    }
    
    print(f"\n🔥 Testing {len(nayapay_data)} problematic transactions:")
    
    results = transformer.transform_to_cashew(nayapay_data, column_mapping, "NayaPay")
    
    print(f"\n📊 Results:")
    expected_categories = ['Transfer', 'Transfer', 'Transfer', 'Bills & Fees', 'Transfer']
    
    for i, (row, expected) in enumerate(zip(results, expected_categories)):
        actual = row['Category']
        status = "✅" if actual == expected else "❌"
        print(f"   {status} Row {i}: {actual} (expected {expected}) - {row['Title'][:50]}...")
        
        if actual != expected:
            print(f"      💰 Amount: {row['Amount']}")
            print(f"      📝 Title: {row['Title']}")
            print(f"      📋 Note: {row.get('Note', 'N/A')}")
    
    # Count successes
    successes = sum(1 for i, expected in enumerate(expected_categories) if results[i]['Category'] == expected)
    print(f"\n🎯 Success Rate: {successes}/{len(expected_categories)} ({successes/len(expected_categories)*100:.0f}%)")
    
    if successes == len(expected_categories):
        print("🎉 All transactions categorized correctly!")
    else:
        print("⚠️  Some transactions need rule adjustments")

if __name__ == "__main__":
    test_nayapay_fixes()
