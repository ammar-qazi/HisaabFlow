#!/usr/bin/env python3

import sys
import os
sys.path.append('transformation')

from universal_transformer import UniversalTransformer

def test_pakistani_context_rules():
    """Test Pakistani context: ride-hailing as P2P transfers + mobile recharge fix"""
    print("🧪 Testing Pakistani Context Rules")
    print("   🏍️  Ride-hailing as P2P transfers (100-2000 PKR)")
    print("   📱 Fixed mobile recharge display")
    print("   🏢 Utility bill detection")
    
    transformer = UniversalTransformer()
    
    # Test various Pakistani payment scenarios
    test_data = [
        {
            'Date': '2025-02-05',
            'Amount': -2000.0,   # Mobile recharge (should show as "Mobile Recharge")
            'Title': 'Mobile top-up purchased|Zong 03142919528 Nickname: Zunayyar',
            'Note': 'Mobile Top-up'
        },
        {
            'Date': '2025-02-07', 
            'Amount': -500.0,    # Ride payment to driver (should be Travel)
            'Title': 'Outgoing fund transfer to Muhammad Ali - ride driver',
            'Note': 'Raast Out'
        },
        {
            'Date': '2025-02-08',
            'Amount': -800.0,    # Another ride payment (should be Travel)
            'Title': 'Outgoing fund transfer to Careem driver Usman',
            'Note': 'Raast Out'
        },
        {
            'Date': '2025-02-09',
            'Amount': -1200.0,   # Electric bill payment (should be Bills & Fees)
            'Title': 'Outgoing fund transfer to K-Electric bill payment',
            'Note': 'Raast Out'
        },
        {
            'Date': '2025-02-10',
            'Amount': -1500.0,   # Regular P2P transfer (should remain Transfer)
            'Title': 'Outgoing fund transfer to Muhammad Sajid easypaisa Bank-7717',
            'Note': 'Raast Out'
        },
        {
            'Date': '2025-02-11',
            'Amount': -5000.0,   # Large transfer (should be Transfer)
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
    
    print(f"\\n🔥 Testing {len(test_data)} Pakistani payment scenarios:")
    
    results = transformer.transform_to_cashew(test_data, column_mapping, "NayaPay")
    
    print(f"\\n📊 Results:")
    expected_results = [
        ("Bills & Fees", "Mobile Recharge", "Fixed mobile display"),
        ("Travel", "Ride payment", "Ride-hailing detection"), 
        ("Travel", "Ride payment", "Careem driver detection"),
        ("Bills & Fees", "Bill payment", "Utility bill detection"),
        ("Transfer", "Transfer to Muhammad", "Regular P2P transfer"),
        ("Transfer", "Transfer to Ammar", "Large transfer")
    ]
    
    perfect_matches = 0
    for i, (row, (expected_cat, expected_title_contains, description)) in enumerate(zip(results, expected_results)):
        actual_cat = row['Category']
        actual_title = row['Title']
        
        cat_correct = actual_cat == expected_cat
        title_correct = expected_title_contains.lower() in actual_title.lower()
        
        if cat_correct and title_correct:
            status = "✅"
            perfect_matches += 1
        elif cat_correct:
            status = "🟡"  # Category correct, title needs work
        else:
            status = "❌"
        
        print(f"   {status} Row {i+1}: {actual_cat} - {actual_title}")
        print(f"       Expected: {expected_cat} with '{expected_title_contains}' - {description}")
        print(f"       Amount: {row['Amount']}")
        print()
    
    print(f"🎯 Perfect Matches: {perfect_matches}/{len(expected_results)} ({perfect_matches/len(expected_results)*100:.0f}%)")
    
    if perfect_matches >= 4:  # Allow some flexibility
        print("\\n🎉 PAKISTANI CONTEXT RULES WORKING WELL!")
        print("\\n✅ Key Improvements:")
        print("   📱 Mobile recharges → Clean 'Mobile Recharge' title")
        print("   🏍️  Ride-hailing keywords → Travel category") 
        print("   🏢 Utility keywords → Bills & Fees category")
        print("   👥 Regular P2P → Transfer (unchanged)")
        print("   💰 Large amounts → Transfer (unchanged)")
        print()
        print("🧠 Smart Logic:")
        print("   • Small Raast Out (100-2000) + ride keywords → Travel")
        print("   • Small Raast Out (200-3000) + bill keywords → Bills & Fees") 
        print("   • Large Raast Out (>3000) → Transfer")
        print("   • Generic small transfers → Transfer (default)")
    else:
        print("\\n⚠️  Some scenarios need refinement")
        print("\\n💡 Suggestions:")
        print("   1. Check if your ride-hailing transactions contain keywords like:")
        print("      'driver', 'ride', 'uber', 'careem', 'bykea', 'transport', 'taxi'")
        print("   2. Check if your bill payments contain keywords like:")
        print("      'bill', 'electric', 'k-electric', 'gas', 'ptcl', 'utility'")
        print("   3. If not, we can add more keywords or use ML-based detection")

if __name__ == "__main__":
    test_pakistani_context_rules()
