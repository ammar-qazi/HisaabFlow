#!/usr/bin/env python3

"""
Test script for the new Ammar-specific transfer detector
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_ammar_detector():
    """Test the Ammar-specific transfer detector with sample data"""
    
    print("🧪 TESTING AMMAR-SPECIFIC TRANSFER DETECTOR")
    print("=" * 60)
    
    try:
        from backend.transfer_detector_enhanced_ammar import TransferDetector
        print("✅ Successfully imported AmmarTransferDetector")
    except ImportError as e:
        print(f"❌ Failed to import AmmarTransferDetector: {e}")
        return False
    
    # Create sample CSV data lists based on your specifications
    csv_data_list = [
        {
            'file_name': 'nayapay_feb.csv',
            'data': [
                {
                    'Date': '2025-02-14',
                    'Amount': 30000.0,
                    'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah',
                    'Currency': 'PKR'
                }
            ]
        },
        {
            'file_name': 'wise_USD.csv', 
            'data': [
                {
                    'Date': '2025-02-14',
                    'Amount': -108.99,
                    'Description': 'Sent money to Ammar Qazi',
                    'Currency': 'USD',
                    'Exchange To': 'PKR',
                    'Exchange To Amount': 30000.0
                }
            ]
        }
    ]
    
    # Initialize detector
    detector = TransferDetector(user_name="Ammar Qazi", date_tolerance_hours=24)
    print("✅ Successfully initialized AmmarTransferDetector")
    
    # Test detection
    print("\n🔍 Running transfer detection...")
    result = detector.detect_transfers(csv_data_list)
    
    print(f"\n📊 RESULTS:")
    print(f"   Transfer pairs found: {result['summary']['transfer_pairs_found']}")
    print(f"   Currency conversions: {result['summary']['currency_conversions']}")
    print(f"   Other transfers: {result['summary']['other_transfers']}")
    print(f"   Potential transfers: {result['summary']['potential_transfers']}")
    
    if result['transfers']:
        print(f"\n🎉 SUCCESS! Found {len(result['transfers'])} transfer pairs:")
        for i, transfer in enumerate(result['transfers']):
            print(f"\n   Transfer {i+1}:")
            print(f"      📤 Outgoing: {transfer['outgoing']['_csv_name']}")
            print(f"         Amount: {transfer['outgoing']['Amount']}")
            print(f"         Description: {transfer['outgoing']['Description']}")
            print(f"      📥 Incoming: {transfer['incoming']['_csv_name']}")
            print(f"         Amount: {transfer['incoming']['Amount']}")
            print(f"         Description: {transfer['incoming']['Description']}")
            print(f"      🎯 Confidence: {transfer['confidence']:.2f}")
            print(f"      🔧 Strategy: {transfer.get('match_strategy', 'unknown')}")
            if transfer.get('exchange_amount'):
                print(f"      💱 Exchange Amount: {transfer['exchange_amount']}")
    else:
        print(f"\n⚠️  No transfer pairs detected")
        
        print(f"\n🔍 DEBUG INFO:")
        print(f"   Potential transfers found: {len(result.get('potential_transfers', []))}")
        if result.get('potential_transfers'):
            for pt in result['potential_transfers']:
                print(f"      - {pt.get('_csv_name', 'unknown')}: {pt.get('Description', 'no desc')}")
    
    return result['summary']['transfer_pairs_found'] > 0

if __name__ == "__main__":
    success = test_ammar_detector()
    if success:
        print(f"\n🎉 TEST PASSED: Ammar detector working correctly!")
    else:
        print(f"\n❌ TEST FAILED: Ammar detector needs debugging")
