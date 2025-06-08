#!/usr/bin/env python3

import sys
import os
sys.path.append('transformation')

from universal_transformer import UniversalTransformer

def test_real_nayapay_data():
    """Test with actual data from user's log"""
    print("🧪 Testing Real NayaPay Data (from your log)")
    
    transformer = UniversalTransformer()
    
    # Actual transactions from your log
    nayapay_data = [
        {
            'Date': '2025-02-02',
            'Amount': -5000.0,   # Surraiya Riaz (should become "Zunayyara Quran")
            'Title': 'Outgoing fund transfer to Surraiya Riaz (Asaan Ac) Meezan Bank-2000',
            'Note': 'Raast Out'
        },
        {
            'Date': '2025-02-05',
            'Amount': -2000.0,   # Mobile recharge
            'Title': 'Mobile top-up purchased|Zong 03142919528 Nickname: Zunayyar',
            'Note': 'Mobile Top-up'
        },
        {
            'Date': '2025-02-05',
            'Amount': -23000.0,  # Large transfer
            'Title': 'Outgoing fund transfer to Ammar Qazi Meezan Bank-3212',
            'Note': 'Raast Out'
        },
        {
            'Date': '2025-02-07',
            'Amount': -400.0,    # Small P2P transfer
            'Title': 'Outgoing fund transfer to Usman Siddique easypaisa Bank-9171',
            'Note': 'Peer to Peer'
        },
        {
            'Date': '2025-02-08',
            'Amount': -1500.0,   # Small P2P transfer
            'Title': 'Outgoing fund transfer to Muhammad Sajid easypaisa Bank-7717',
            'Note': 'Peer to Peer'
        },
        {
            'Date': '2025-02-03',
            'Amount': 50000.0,   # Income
            'Title': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-7840',
            'Note': 'IBFT In'
        }
    ]
    
    column_mapping = {
        'Date': 'Date',
        'Amount': 'Amount',
        'Title': 'Title', 
        'Note': 'Note'
    }
    
    print(f"\\n🔥 Testing real data from your log:")
    
    results = transformer.transform_to_cashew(nayapay_data, column_mapping, "NayaPay")
    
    print(f"\\n📊 Results:")
    expected_results = [
        ("Transfer", "Zunayyara Quran", "Contact name replacement"),
        ("Bills & Fees", "Mobile", "Mobile recharge detection"), 
        ("Transfer", "Transfer to Ammar", "Large transfer"),
        ("Transfer", "Transfer to Usman", "Small P2P transfer"),
        ("Transfer", "Transfer to Muhammad", "Small P2P transfer"),
        ("Income", "Incoming fund", "Income detection")
    ]
    
    all_correct = True
    for i, (row, (expected_cat, expected_title_contains, description)) in enumerate(zip(results, expected_results)):
        actual_cat = row['Category']
        actual_title = row['Title']
        
        cat_correct = actual_cat == expected_cat
        title_correct = expected_title_contains.lower() in actual_title.lower()
        
        if cat_correct and title_correct:
            status = "✅"
        else:
            status = "❌"
            all_correct = False
        
        print(f"   {status} Row {i+1}: {actual_cat} - {actual_title}")
        print(f"       Expected: {expected_cat} with '{expected_title_contains}' - {description}")
        print(f"       Amount: {row['Amount']}")
        print()
    
    if all_correct:
        print("🎉 ALL REAL DATA PROCESSED CORRECTLY!")
        print()
        print("✅ System Working Features:")
        print("   🔸 Mobile recharges → Bills & Fees")
        print("   🔸 Large transfers → Transfer with cleaned titles")  
        print("   🔸 Small P2P transfers → Transfer (correct!)")
        print("   🔸 Income detection → Income")
        print("   🔸 Contact name replacement → Zunayyara Quran")
        print("   🔸 Description cleaning → 'Transfer to...' format")
        print()
        print("🎯 The system is categorizing your data CORRECTLY!")
        print("   Your small transfers are person-to-person, so Transfer category is right.")
    else:
        print("⚠️  Some issues found")

if __name__ == "__main__":
    test_real_nayapay_data()
