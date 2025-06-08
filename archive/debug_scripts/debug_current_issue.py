#!/usr/bin/env python3
"""
Debug script to analyze current transfer detection issue
Based on the output showing 0 transfer pairs but 12 potential transfers
"""

import sys
sys.path.append('backend')

from transfer_detector import TransferDetector
import json

# Sample data structure to test with
def test_current_detection():
    detector = TransferDetector()
    
    # Test with sample Wise transaction
    wise_transaction = {
        'Amount': -254.10,
        'Description': 'Sent money to Usama Qazi',
        'Exchange To Amount': 70000,  # PKR equivalent
        'Date': '2025-02-15',
        '_bank_type': 'wise',
        '_file_name': 'wise_USD.csv'
    }
    
    # Test with sample NayaPay transaction  
    nayapay_transaction = {
        'Amount': 70000,
        'Description': 'Incoming fund transfer from Usama Qazi Bank Alfalah-2050|Transaction ID 192351',
        'Date': '2025-02-15',
        '_bank_type': 'nayapay',
        '_file_name': 'nayapay_feb.csv'
    }
    
    print("🧪 Testing Transfer Detection Patterns")
    print("=" * 50)
    
    # Test pattern matching
    patterns = detector.transfer_patterns
    print(f"📋 Available patterns: {len(patterns)}")
    
    for i, pattern in enumerate(patterns):
        print(f"Pattern {i+1}: {pattern}")
        
    print("\n🔍 Testing Wise Transaction Pattern Matching:")
    wise_desc = wise_transaction['Description'].lower()
    user_name = "usama qazi"
    
    for i, pattern in enumerate(patterns):
        import re
        try:
            if re.search(pattern.format(user_name=user_name), wise_desc):
                print(f"✅ Pattern {i+1} MATCHES: {pattern}")
            else:
                print(f"❌ Pattern {i+1} no match: {pattern}")
        except Exception as e:
            print(f"⚠️  Pattern {i+1} error: {e}")
    
    print("\n🔍 Testing NayaPay Transaction Pattern Matching:")
    nayapay_desc = nayapay_transaction['Description'].lower()
    
    for i, pattern in enumerate(patterns):
        import re
        try:
            if re.search(pattern.format(user_name=user_name), nayapay_desc):
                print(f"✅ Pattern {i+1} MATCHES: {pattern}")
            else:
                print(f"❌ Pattern {i+1} no match: {pattern}")
        except Exception as e:
            print(f"⚠️  Pattern {i+1} error: {e}")
    
    print("\n🎯 Testing Cross-Bank Transfer Detection:")
    is_cross_bank = detector._is_cross_bank_transfer(wise_transaction, nayapay_transaction)
    print(f"Cross-bank detection result: {is_cross_bank}")
    
    print("\n💰 Testing Amount Matching:")
    amounts_match = detector._amounts_match(wise_transaction, nayapay_transaction)
    print(f"Amounts match result: {amounts_match}")
    
    print("\n📅 Testing Date Matching:")
    dates_match = detector._dates_match(wise_transaction, nayapay_transaction)
    print(f"Dates match result: {dates_match}")

if __name__ == "__main__":
    test_current_detection()
