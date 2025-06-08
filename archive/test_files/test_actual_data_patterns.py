#!/usr/bin/env python3
"""
Quick test to verify the issue with your actual transaction descriptions
"""

import sys
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from transfer_detector_enhanced import EnhancedTransferDetector

def test_your_actual_data():
    """Test with the exact data patterns you showed me"""
    
    print("🔍 TESTING WITH YOUR ACTUAL TRANSACTION PATTERNS")
    print("=" * 55)
    
    # Your actual Wise data (based on what you showed)
    wise_data = {
        'file_name': 'wise_actual.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '-413.89',
                'Description': 'Converted 413.89 USD to 150,000.00 HUF for HUF balance',
                'Exchange To Amount': '150000.00'
            },
            {
                'Date': '2025-06-04',
                'Amount': '-546.51',
                'Description': 'Converted 546.51 USD to 200,000.00 HUF for HUF balance',
                'Exchange To Amount': '200000.00'
            },
            {
                'Date': '2025-06-04',
                'Amount': '-181.1',
                'Description': 'Sent money to Ammar Qazi',
                'Exchange To Amount': '50000'  # Assuming PKR equivalent
            },
            {
                'Date': '2025-06-04',
                'Amount': '-109',
                'Description': 'Sent money to Ammar Qazi',
                'Exchange To Amount': '30000'  # Assuming PKR equivalent
            }
        ],
        'template_config': {'bank_name': 'Wise'}
    }
    
    # Assuming you have corresponding NayaPay data
    nayapay_data = {
        'file_name': 'nayapay_actual.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '50000',
                'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2050|Transaction ID 123456'
            },
            {
                'Date': '2025-06-04',
                'Amount': '30000',
                'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2051|Transaction ID 123457'
            }
        ],
        'template_config': {'bank_name': 'NayaPay'}
    }
    
    print("📊 INPUT DATA:")
    print("   WISE TRANSACTIONS:")
    for i, trans in enumerate(wise_data['data']):
        print(f"     {i+1}. Amount: {trans['Amount']}, Desc: {trans['Description']}")
        print(f"        Exchange To: {trans.get('Exchange To Amount', 'N/A')}")
    
    print("\n   NAYAPAY TRANSACTIONS:")
    for i, trans in enumerate(nayapay_data['data']):
        print(f"     {i+1}. Amount: {trans['Amount']}, Desc: {trans['Description']}")
    
    # Test transfer detection
    detector = EnhancedTransferDetector(user_name="Ammar Qazi")
    csv_data_list = [wise_data, nayapay_data]
    
    print("\n🔍 TRANSFER DETECTION RESULTS:")
    results = detector.detect_transfers(csv_data_list)
    
    print(f"   Total Transfers Found: {len(results['transfers'])}")
    print(f"   Cross-Bank Transfers: {results['detection_strategies']['cross_bank_transfers']}")
    print(f"   Currency Conversions: {results['detection_strategies']['currency_conversions']}")
    print(f"   Potential Transfers: {len(results['potential_transfers'])}")
    print(f"   Flagged for Review: {len(results['flagged_transactions'])}")
    
    print("\n📋 DETAILED RESULTS:")
    
    # Show detected transfers
    if results['transfers']:
        print("   ✅ DETECTED TRANSFERS:")
        for i, pair in enumerate(results['transfers'], 1):
            print(f"     {i}. {pair['transfer_type'].upper()} Transfer:")
            print(f"        📤 OUT: {pair['outgoing']['Description']} ({pair['outgoing']['Amount']})")
            print(f"        📥 IN:  {pair['incoming']['Description']} ({pair['incoming']['Amount']})")
            print(f"        🎯 Confidence: {pair['confidence']:.2f}")
            if pair.get('exchange_amount'):
                print(f"        💱 Exchange Amount: {pair['exchange_amount']}")
    else:
        print("   ❌ NO TRANSFERS DETECTED")
    
    # Show potential transfers
    if results['potential_transfers']:
        print("\n   ⚠️  POTENTIAL TRANSFERS (UNMATCHED):")
        for i, potential in enumerate(results['potential_transfers'], 1):
            print(f"     {i}. {potential['Description']} ({potential['Amount']})")
            print(f"        Reason: {potential.get('_unmatched_reason', 'Unknown')}")
    
    # Show flagged transactions
    if results['flagged_transactions']:
        print("\n   🚩 FLAGGED FOR REVIEW:")
        for i, flagged in enumerate(results['flagged_transactions'], 1):
            print(f"     {i}. {flagged['Description']} ({flagged['Amount']})")
            print(f"        Reason: {flagged.get('_flag_reason', 'Unknown')}")
    
    print("\n🎯 ANALYSIS:")
    
    # Check if your specific transfers were detected
    sent_money_181_detected = any(
        pair for pair in results['transfers']
        if '181.1' in str(pair['outgoing']['Amount']) and 'sent money' in pair['outgoing']['Description'].lower()
    )
    
    sent_money_109_detected = any(
        pair for pair in results['transfers']
        if '109' in str(pair['outgoing']['Amount']) and 'sent money' in pair['outgoing']['Description'].lower()
    )
    
    print(f"   🎯 'Sent money to Ammar Qazi' (-181.1): {'✅ DETECTED' if sent_money_181_detected else '❌ MISSED'}")
    print(f"   🎯 'Sent money to Ammar Qazi' (-109): {'✅ DETECTED' if sent_money_109_detected else '❌ MISSED'}")
    
    # Check why HUF conversions aren't detected as transfers
    huf_conversions = [t for t in wise_data['data'] if 'HUF' in t['Description']]
    print(f"\n   💱 HUF Conversions Found: {len(huf_conversions)}")
    print(f"     These should NOT be detected as cross-bank transfers (correct behavior)")
    
    return results

def test_with_debug_info():
    """Test with additional debug information"""
    
    print("\n🔧 DEBUGGING TRANSFER DETECTION LOGIC")
    print("=" * 45)
    
    # Test the bank detection logic
    from transfer_detector_enhanced import EnhancedTransferDetector
    
    detector = EnhancedTransferDetector()
    
    # Test individual transactions
    test_transactions = [
        {
            'Description': 'Sent money to Ammar Qazi',
            'Amount': '-181.1',
            'Exchange To Amount': '50000',
            '_csv_name': 'wise_test.csv'
        },
        {
            'Description': 'Converted 413.89 USD to 150,000.00 HUF for HUF balance',
            'Amount': '-413.89',
            'Exchange To Amount': '150000',
            '_csv_name': 'wise_test.csv'
        },
        {
            'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2050',
            'Amount': '50000',
            '_csv_name': 'nayapay_test.csv'
        }
    ]
    
    print("🏦 BANK TYPE DETECTION:")
    for i, trans in enumerate(test_transactions, 1):
        bank_type = detector._detect_bank_type(trans['_csv_name'], trans)
        print(f"   {i}. {trans['Description'][:40]}... → {bank_type}")
    
    print("\n🔍 TRANSFER PATTERN MATCHING:")
    for i, trans in enumerate(test_transactions, 1):
        desc = trans['Description'].lower()
        patterns_matched = []
        
        for pattern_name, pattern in detector.transfer_patterns.items():
            import re
            if re.search(pattern, desc, re.IGNORECASE):
                patterns_matched.append(pattern_name)
        
        print(f"   {i}. {trans['Description'][:40]}...")
        print(f"      Patterns matched: {patterns_matched if patterns_matched else 'None'}")
    
    return test_transactions

if __name__ == "__main__":
    # Run the main test
    results = test_your_actual_data()
    
    # Run debug test
    debug_results = test_with_debug_info()
    
    print("\n" + "="*60)
    print("🎯 SUMMARY")
    print("="*60)
    
    if len(results['transfers']) > 0:
        print("✅ Transfer detection is WORKING")
        print(f"   Found {len(results['transfers'])} transfer pairs")
        print("   Issue might be in the template categorization override")
    else:
        print("❌ Transfer detection is NOT working")
        print("   Need to investigate pattern matching or data structure")
    
    print("\n💡 NEXT STEPS:")
    print("   1. Check if your actual CSV data matches this test structure")
    print("   2. Verify template isn't overriding transfer categorization")
    print("   3. Check the backend logs for debug output during processing")
