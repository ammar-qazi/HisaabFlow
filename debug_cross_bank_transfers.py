#!/usr/bin/env python3

"""
Debug script to analyze why cross-bank transfers aren't being detected
between Wise and NayaPay CSVs
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.transfer_detector_enhanced_exchange import TransferDetector
import re

def analyze_cross_bank_detection():
    """Analyze why cross-bank transfers aren't working"""
    
    print("🔍 DEBUGGING CROSS-BANK TRANSFER DETECTION")
    print("=" * 60)
    
    # Create sample transactions based on the log output
    wise_transactions = [
        {
            'Amount': -254.1,
            'Date': '2025-06-02',
            'Description': 'Sent money to Usama Qazi',
            '_csv_index': 2,
            '_transaction_index': 0,
            '_csv_name': 'wise_USD.csv',
            '_bank_type': 'wise'
        },
        {
            'Amount': -164.0,
            'Date': '2025-06-01', 
            'Description': 'Sent money to Zunayyara Khalid',
            '_csv_index': 2,
            '_transaction_index': 1,
            '_csv_name': 'wise_USD.csv',
            '_bank_type': 'wise'
        },
        {
            'Amount': -181.53,
            'Date': '2025-05-15',
            'Description': 'Sent money to Ammar Qazi',
            '_csv_index': 2,
            '_transaction_index': 15,
            '_csv_name': 'wise_USD.csv',
            '_bank_type': 'wise'
        }
    ]
    
    nayapay_transactions = [
        {
            'Amount': 50000.0,
            'Date': '2025-02-03',
            'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfala',
            '_csv_index': 0,
            '_transaction_index': 1,
            '_csv_name': 'nayapay_feb.csv',
            '_bank_type': 'nayapay'
        }
    ]
    
    detector = TransferDetector(user_name="Ammar Qazi")
    
    print("\n📝 TESTING CROSS-BANK DETECTION LOGIC")
    print("-" * 40)
    
    # Test each Wise outgoing against NayaPay incoming
    for wise_tx in wise_transactions:
        print(f"\n🏦 WISE OUTGOING: {wise_tx['Amount']} | {wise_tx['Description']}")
        
        for nayapay_tx in nayapay_transactions:
            print(f"🏦 NAYAPAY INCOMING: {nayapay_tx['Amount']} | {nayapay_tx['Description']}")
            
            # Test the cross-bank detection
            is_cross_bank = detector._is_cross_bank_transfer(wise_tx, nayapay_tx)
            print(f"   ✅ Cross-bank detected: {is_cross_bank}")
            
            # Test individual components
            outgoing_desc = wise_tx['Description'].lower()
            incoming_desc = nayapay_tx['Description'].lower()
            
            print(f"   🔍 Analysis:")
            print(f"      📤 Outgoing bank type: {wise_tx.get('_bank_type')}")
            print(f"      📥 Incoming bank type: {nayapay_tx.get('_bank_type')}")
            print(f"      📝 Outgoing desc: '{outgoing_desc}'")
            print(f"      📝 Incoming desc: '{incoming_desc}'")
            
            # Check individual conditions
            bank_type_check = (wise_tx.get('_bank_type') == 'wise' and 
                              nayapay_tx.get('_bank_type') in ['nayapay', 'bank_alfalah', 'pakistani_bank'])
            print(f"      ✅ Bank type check: {bank_type_check}")
            
            sent_money_check = ('sent money' in outgoing_desc and detector.user_name.lower() in outgoing_desc)
            print(f"      ✅ Sent money check: {sent_money_check}")
            print(f"         - 'sent money' in desc: {'sent money' in outgoing_desc}")
            print(f"         - user name in desc: {detector.user_name.lower() in outgoing_desc}")
            print(f"         - user name: '{detector.user_name.lower()}'")
            
            incoming_transfer_check = ('incoming fund transfer' in incoming_desc and detector.user_name.lower() in incoming_desc)
            print(f"      ✅ Incoming transfer check: {incoming_transfer_check}")
            print(f"         - 'incoming fund transfer' in desc: {'incoming fund transfer' in incoming_desc}")
            print(f"         - user name in desc: {detector.user_name.lower() in incoming_desc}")
            
            # Test amount matching
            amount_match = abs(abs(wise_tx['Amount']) - nayapay_tx['Amount']) < 0.01
            print(f"      ✅ Amount match: {amount_match} ({abs(wise_tx['Amount'])} vs {nayapay_tx['Amount']})")
            
            print()
    
    print("\n🔧 TESTING TRANSFER PATTERN MATCHING")
    print("-" * 40)
    
    # Test pattern matching for each transaction
    all_transactions = wise_transactions + nayapay_transactions
    
    for tx in all_transactions:
        desc = tx['Description'].lower()
        print(f"\n📝 Testing: {tx['Description']}")
        print(f"   🏦 Bank: {tx['_csv_name']}")
        
        # Test against each pattern
        for i, pattern in enumerate(detector.transfer_patterns):
            match = re.search(pattern, desc, re.IGNORECASE)
            if match:
                print(f"   ✅ Matched pattern {i}: {pattern}")
                print(f"      🎯 Match: {match.group()}")
            else:
                # Only show specific patterns for debugging
                if 'sent' in pattern or 'transfer' in pattern or 'incoming' in pattern:
                    print(f"   ❌ Pattern {i}: {pattern}")
        
        print()

def test_pattern_improvements():
    """Test improved patterns for better detection"""
    print("\n🚀 TESTING IMPROVED PATTERNS")
    print("=" * 40)
    
    # Test descriptions from the actual log
    test_descriptions = [
        "Sent money to Usama Qazi",
        "Sent money to Zunayyara Khalid", 
        "Sent money to Ammar Qazi",
        "Incoming fund transfer from Ammar Qazi Bank Alfala"
    ]
    
    # Current patterns
    current_patterns = [
        r"sent\s+(money\s+)?to\s+ammar qazi",
        r"transfer\s+to\s+ammar qazi",
        r"transfer\s+from\s+ammar qazi", 
        r"incoming\s+fund\s+transfer\s+from\s+ammar qazi"
    ]
    
    # Improved patterns
    improved_patterns = [
        r"sent\s+(money\s+)?to\s+\w+",  # "Sent money to anyone"
        r"sent\s+(money\s+)?to\s+ammar\s+qazi",  # Specific to user
        r"transfer\s+to\s+\w+",  # "Transfer to anyone"
        r"transfer\s+from\s+\w+",  # "Transfer from anyone"
        r"incoming\s+fund\s+transfer\s+from\s+\w+",  # "Incoming from anyone"
        r"incoming\s+fund\s+transfer",  # General incoming transfer
        r"fund\s+transfer\s+from"  # Bank Alfalah pattern
    ]
    
    print("Testing current patterns:")
    for desc in test_descriptions:
        print(f"\n📝 Testing: '{desc}'")
        desc_lower = desc.lower()
        
        for i, pattern in enumerate(current_patterns):
            match = re.search(pattern, desc_lower, re.IGNORECASE)
            status = "✅" if match else "❌"
            print(f"   {status} Pattern {i}: {pattern}")
    
    print("\n" + "="*40)
    print("Testing improved patterns:")
    for desc in test_descriptions:
        print(f"\n📝 Testing: '{desc}'")
        desc_lower = desc.lower()
        
        for i, pattern in enumerate(improved_patterns):
            match = re.search(pattern, desc_lower, re.IGNORECASE)
            status = "✅" if match else "❌"
            print(f"   {status} Pattern {i}: {pattern}")

if __name__ == "__main__":
    analyze_cross_bank_detection()
    test_pattern_improvements()
