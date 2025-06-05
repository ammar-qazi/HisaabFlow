#!/usr/bin/env python3
"""
🧪 TEST: Enhanced Transfer Detection with Currency Conversions

Tests the improved transfer detector with synthetic currency conversion data
"""
import json
from backend.transfer_detector import TransferDetector

def test_enhanced_currency_conversion_detection():
    """Test enhanced transfer detection with currency conversion scenarios"""
    print("🧪 TESTING ENHANCED CURRENCY CONVERSION DETECTION")
    print("=" * 60)
    
    # Create synthetic currency conversion data mimicking Wise
    wise_usd_data = [
        {
            'Date': '2025-01-15',
            'Amount': -565.24,
            'Description': 'Converted 565.24 USD to 200,000.00 HUF',
            'Currency': 'USD',
            'Exchange To Amount': 200000.00,
            'Exchange Rate': 354.0
        },
        {
            'Date': '2025-01-16', 
            'Amount': -100.0,
            'Description': 'Card transaction of 100.00 USD issued by Amazon',
            'Currency': 'USD'
        }
    ]
    
    wise_huf_data = [
        {
            'Date': '2025-01-15',
            'Amount': 200000.00,
            'Description': 'Converted 565.24 USD to 200,000.00 HUF',
            'Currency': 'HUF',
            'Exchange From Amount': 565.24,
            'Exchange Rate': 354.0
        },
        {
            'Date': '2025-01-16',
            'Amount': -35000.0,
            'Description': 'Card transaction of 35,000.00 HUF issued by Lidl Budapest',
            'Currency': 'HUF'
        }
    ]
    
    # Create CSV data structure
    csv_data_list = [
        {
            'file_name': 'wise_usd_account.csv',
            'data': wise_usd_data,
            'headers': ['Date', 'Amount', 'Description', 'Currency', 'Exchange To Amount', 'Exchange Rate'],
            'template_config': {'bank_name': 'Transferwise'}
        },
        {
            'file_name': 'wise_huf_account.csv', 
            'data': wise_huf_data,
            'headers': ['Date', 'Amount', 'Description', 'Currency', 'Exchange From Amount', 'Exchange Rate'],
            'template_config': {'bank_name': 'Transferwise'}
        }
    ]
    
    # Test enhanced transfer detection
    detector = TransferDetector(user_name="Ammar Qazi", date_tolerance_hours=24)
    transfer_results = detector.detect_transfers(csv_data_list)
    
    print(f"\n📊 ENHANCED DETECTION RESULTS:")
    print(f"   ✅ Transfer pairs found: {transfer_results['summary']['transfer_pairs_found']}")
    print(f"   💭 Potential transfers: {transfer_results['summary']['potential_transfers']}")
    print(f"   ⚠️  Conflicts: {transfer_results['summary']['conflicts']}")
    
    # Detailed analysis of found transfers
    if transfer_results['transfers']:
        print(f"\n🔄 DETECTED TRANSFER PAIRS:")
        for i, pair in enumerate(transfer_results['transfers']):
            transfer_type = pair.get('transfer_type', 'standard')
            print(f"   Pair {i+1} [{transfer_type.upper()}]:")
            print(f"      📤 Outgoing: {pair['outgoing']['Amount']} {pair['outgoing'].get('Currency', 'N/A')}")
            print(f"      📥 Incoming: {pair['incoming']['Amount']} {pair['incoming'].get('Currency', 'N/A')}")
            print(f"      🎖️  Confidence: {pair['confidence']:.2f}")
            print(f"      📅 Date: {pair['date'].strftime('%Y-%m-%d')}")
            
            # Check if descriptions match (for currency conversions)
            outgoing_desc = pair['outgoing']['Description']
            incoming_desc = pair['incoming']['Description']
            if outgoing_desc == incoming_desc:
                print(f"      ✅ Exact description match: {outgoing_desc}")
            else:
                print(f"      ❌ Description mismatch:")
                print(f"         Out: {outgoing_desc}")
                print(f"         In:  {incoming_desc}")
    
    # Check potential transfers that weren't matched
    if transfer_results['potential_transfers']:
        print(f"\n💭 UNMATCHED POTENTIAL TRANSFERS:")
        for candidate in transfer_results['potential_transfers']:
            print(f"   📝 {candidate['Description']}")
            print(f"      💰 Amount: {candidate['Amount']}")
            print(f"      🎯 Pattern: {candidate['_transfer_pattern']}")
    
    return transfer_results

def test_cross_bank_transfer_detection():
    """Test cross-bank transfer detection (Wise -> NayaPay)"""
    print("\n\n🧪 TESTING CROSS-BANK TRANSFER DETECTION")
    print("=" * 60)
    
    # Wise outgoing transfer
    wise_data = [
        {
            'Date': '2025-01-20',
            'Amount': -50000.0,
            'Description': 'Sent money to Ammar Qazi with reference PKR-TRANSFER-001',
            'Currency': 'PKR',
            'Exchange To Amount': 50000.0
        }
    ]
    
    # NayaPay incoming transfer
    nayapay_data = [
        {
            'Date': '2025-01-20',
            'Amount': 50000.0,
            'Description': 'Incoming fund transfer from Ammar Qazi',
            'Currency': 'PKR'
        }
    ]
    
    csv_data_list = [
        {
            'file_name': 'wise_pkr.csv',
            'data': wise_data,
            'headers': ['Date', 'Amount', 'Description', 'Currency', 'Exchange To Amount'],
            'template_config': {'bank_name': 'Transferwise'}
        },
        {
            'file_name': 'nayapay_statement.csv',
            'data': nayapay_data,
            'headers': ['Date', 'Amount', 'Description', 'Currency'],
            'template_config': {'bank_name': 'NayaPay'}
        }
    ]
    
    detector = TransferDetector(user_name="Ammar Qazi", date_tolerance_hours=24)
    transfer_results = detector.detect_transfers(csv_data_list)
    
    print(f"\n📊 CROSS-BANK DETECTION RESULTS:")
    print(f"   ✅ Transfer pairs found: {transfer_results['summary']['transfer_pairs_found']}")
    print(f"   💭 Potential transfers: {transfer_results['summary']['potential_transfers']}")
    
    if transfer_results['transfers']:
        for i, pair in enumerate(transfer_results['transfers']):
            transfer_type = pair.get('transfer_type', 'standard')
            print(f"\n   🌐 Cross-bank pair {i+1} [{transfer_type.upper()}]:")
            print(f"      📤 Out: {pair['outgoing']['_csv_name']} | {pair['outgoing']['Amount']}")
            print(f"      📥 In:  {pair['incoming']['_csv_name']} | {pair['incoming']['Amount']}")
            print(f"      🎖️  Confidence: {pair['confidence']:.2f}")
    
    return transfer_results

if __name__ == "__main__":
    print("🔧 TESTING ENHANCED TRANSFER DETECTION FIXES")
    print("=" * 80)
    
    # Test 1: Currency conversions
    currency_results = test_enhanced_currency_conversion_detection()
    
    # Test 2: Cross-bank transfers
    cross_bank_results = test_cross_bank_transfer_detection()
    
    print("\n" + "=" * 80)
    print("🎯 ENHANCED TESTING COMPLETE")
    
    total_pairs = (currency_results['summary']['transfer_pairs_found'] + 
                   cross_bank_results['summary']['transfer_pairs_found'])
    
    if total_pairs > 0:
        print(f"✅ SUCCESS: Found {total_pairs} transfer pairs with enhanced detection!")
    else:
        print("❌ ISSUE: No transfer pairs detected - may need further debugging")
