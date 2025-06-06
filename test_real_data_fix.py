#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from transfer_detector_enhanced_ammar import TransferDetector
import json

def test_real_data():
    """Test with the real data that was failing"""
    
    print("🔧 TESTING WITH REAL DATA")
    print("=" * 50)
    
    # Real data from the original debug output - simplified version
    csv_data_list = [
        {
            'file_name': 'nayapay_feb.csv',
            'data': [
                {
                    'Date': '2025-02-03',
                    'Amount': '50000.0',
                    'Description': 'Transfer from Ammar Qazi Bank Alfalah-2050',
                    'Category': 'Transfer'
                }
            ],
            'template_config': {}
        },
        {
            'file_name': 'wise_USD.csv',
            'data': [
                {
                    'Date': '2025-06-02',
                    'Amount': '-254.1',
                    'Description': 'Sent money to Usama Qazi',
                    'Category': 'Transfer'
                },
                {
                    'Date': '2025-02-03',  # Match the NayaPay date
                    'Amount': '-100.0',    # Different amount for testing
                    'Description': 'Sent money to Ammar Qazi',
                    'Category': 'Transfer',
                    'Exchange To Amount': '50000.0',  # This should match NayaPay
                    'Exchange To': 'PKR'
                }
            ],
            'template_config': {}
        }
    ]
    
    # Initialize detector
    detector = TransferDetector(user_name="Ammar Qazi", date_tolerance_hours=24)
    
    # Run detection
    result = detector.detect_transfers(csv_data_list)
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"   Transfer pairs found: {len(result['transfers'])}")
    print(f"   Cross-bank transfers: {result['summary']['other_transfers']}")
    print(f"   Currency conversions: {result['summary']['currency_conversions']}")
    
    # Check for Ammar cross-bank transfers specifically
    ammar_transfers = []
    for transfer in result['transfers']:
        outgoing_desc = transfer['outgoing'].get('Description', '').lower()
        incoming_desc = transfer['incoming'].get('Description', '').lower()
        
        if ('ammar' in outgoing_desc or 'ammar' in incoming_desc):
            ammar_transfers.append(transfer)
    
    if ammar_transfers:
        print(f"\n✅ SUCCESS! Found {len(ammar_transfers)} Ammar-related transfer(s)")
        for i, transfer in enumerate(ammar_transfers):
            print(f"\n   Transfer {i+1}:")
            print(f"      📤 Outgoing: {transfer['outgoing']['Description']}")
            print(f"      📥 Incoming: {transfer['incoming']['Description']}")
            print(f"      💰 Amount: {transfer['amount']}")
            print(f"      💱 Exchange Amount: {transfer.get('exchange_amount', 'N/A')}")
            print(f"      🎯 Confidence: {transfer['confidence']}")
            print(f"      🔧 Strategy: {transfer.get('match_strategy', 'unknown')}")
            print(f"      📅 Date: {transfer['date']}")
    else:
        print("\n❌ FAILED! No Ammar-related transfers detected")
    
    # Also test non-Ammar transfers to make sure they're ignored
    non_ammar_transfers = [t for t in result['transfers'] if t not in ammar_transfers]
    if non_ammar_transfers:
        print(f"\n⚠️  Found {len(non_ammar_transfers)} non-Ammar transfers (should be ignored for cross-bank)")
    
    return len(ammar_transfers) > 0

if __name__ == "__main__":
    success = test_real_data()
    print(f"\n{'🎉 TEST PASSED' if success else '❌ TEST FAILED'}")
