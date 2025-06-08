#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from transfer_detector_enhanced_ammar import TransferDetector

def test_transfer_detection():
    """Test the fixed transfer detection logic"""
    
    print("🔧 TESTING FIXED TRANSFER DETECTION")
    print("=" * 50)
    
    # Create sample data matching the debug output patterns
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
                    'Date': '2025-02-03',
                    'Amount': '-254.1',
                    'Description': 'Sent money to Ammar Qazi',
                    'Category': 'Transfer',
                    'Exchange To Amount': '50000.0',
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
    
    print(f"\n📊 RESULTS:")
    print(f"   Transfer pairs found: {len(result['transfers'])}")
    print(f"   Cross-bank transfers: {result['summary']['other_transfers']}")
    print(f"   Currency conversions: {result['summary']['currency_conversions']}")
    
    # Check if we found any cross-bank transfers
    cross_bank_transfers = [t for t in result['transfers'] if 'cross_bank' in t.get('transfer_type', '')]
    
    if cross_bank_transfers:
        print(f"\n✅ SUCCESS! Found {len(cross_bank_transfers)} cross-bank transfer(s)")
        for i, transfer in enumerate(cross_bank_transfers):
            print(f"\n   Transfer {i+1}:")
            print(f"      📤 Outgoing: {transfer['outgoing']['Description']}")
            print(f"      📥 Incoming: {transfer['incoming']['Description']}")
            print(f"      💰 Amount: {transfer['amount']}")
            print(f"      🎯 Confidence: {transfer['confidence']}")
            print(f"      🔧 Strategy: {transfer.get('match_strategy', 'unknown')}")
    else:
        print("\n❌ FAILED! No cross-bank transfers detected")
        
        # Debug: Check potential transfers
        potential = result['potential_transfers']
        print(f"\n🔍 Debug info:")
        print(f"   Potential transfers found: {len(potential)}")
        
        for i, pot in enumerate(potential):
            print(f"   Potential {i+1}: {pot.get('Description', 'N/A')}")

if __name__ == "__main__":
    test_transfer_detection()
