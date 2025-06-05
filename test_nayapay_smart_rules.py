#!/usr/bin/env python3

import sys
import os
sys.path.append('transformation')

from universal_transformer import UniversalTransformer

def test_nayapay_smart_categorization():
    """Test the improved NayaPay rules with smart categorization"""
    print("🧪 Testing NayaPay Smart Categorization Rules")
    
    transformer = UniversalTransformer()
    
    # Test various types of small Raast Out payments
    nayapay_data = [
        {
            'Date': '2025-02-05',
            'Amount': -2000.0,   # Mobile recharge - should be Bills & Fees
            'Title': 'Mobile top-up purchased|Zong 03142919528 Nickname: Zunayyar',
            'Note': 'Mobile Top-up'
        },
        {
            'Date': '2025-02-07', 
            'Amount': -800.0,    # Ride hailing - should be Travel (if it has ride keywords)
            'Title': 'Outgoing fund transfer to Uber Pakistan - ride service',
            'Note': 'Raast Out'
        },
        {
            'Date': '2025-02-08',
            'Amount': -1200.0,   # Utility bill - should be Bills & Fees (if it has bill keywords)
            'Title': 'Outgoing fund transfer to Electric Bill Payment Company',
            'Note': 'Raast Out'
        },
        {
            'Date': '2025-02-09',
            'Amount': -500.0,    # Generic small transfer - should be Transfer
            'Title': 'Outgoing fund transfer to Usman Siddique easypaisa Bank-9171',
            'Note': 'Raast Out'
        },
        {
            'Date': '2025-02-10',
            'Amount': -5000.0,   # Large transfer - should be Transfer
            'Title': 'Outgoing fund transfer to Ammar Qazi Meezan Bank-3212',
            'Note': 'Raast Out'
        }
    ]
    
    column_mapping = {
        'Date': 'Date',
        'Amount': 'Amount',
        'Title': 'Title', 
        'Note': 'Note'
    }
    
    print(f"\\n🔥 Testing {len(nayapay_data)} different transaction types:")
    
    results = transformer.transform_to_cashew(nayapay_data, column_mapping, "NayaPay")
    
    print(f"\\n📊 Results:")
    expected_categories = ['Bills & Fees', 'Travel', 'Bills & Fees', 'Transfer', 'Transfer']
    expected_titles = ['Mobile Recharge', 'Ride Hailing', 'Electric Bill Payment', 'Transfer to Usman', 'Transfer to Ammar']
    
    for i, (row, expected_cat, expected_title_contains) in enumerate(zip(results, expected_categories, expected_titles)):
        actual_cat = row['Category']
        actual_title = row['Title']
        
        cat_status = "✅" if actual_cat == expected_cat else "❌"
        title_status = "✅" if expected_title_contains in actual_title else "❌"
        
        print(f"   {cat_status} Row {i}: {actual_cat} (expected {expected_cat})")
        print(f"   {title_status}     Title: {actual_title}")
        print(f"       Amount: {row['Amount']}, Note: {row.get('Note', 'N/A')}")
        print()
    
    # Count successes
    cat_successes = sum(1 for i, expected in enumerate(expected_categories) if results[i]['Category'] == expected)
    print(f"🎯 Category Success Rate: {cat_successes}/{len(expected_categories)} ({cat_successes/len(expected_categories)*100:.0f}%)")
    
    if cat_successes == len(expected_categories):
        print("🎉 All transactions categorized correctly!")
        print("✅ Mobile recharges → Bills & Fees")
        print("✅ Ride hailing → Travel") 
        print("✅ Utility bills → Bills & Fees")
        print("✅ Small transfers → Transfer")
        print("✅ Large transfers → Transfer")
    else:
        print("⚠️  Some transactions need rule adjustments")
        print("\\n🔧 Rule priority explanation:")
        print("   1. Mobile Top-ups → Bills & Fees")
        print("   2. Ride Hailing (small Raast Out with ride keywords) → Travel")
        print("   3. Bills & Fees (small Raast Out with bill keywords) → Bills & Fees")
        print("   4. Large Transfers (Raast Out > -2000) → Transfer")
        print("   5. Generic Fund Transfers → Transfer")

if __name__ == "__main__":
    test_nayapay_smart_categorization()
