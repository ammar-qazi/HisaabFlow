#!/usr/bin/env python3
"""
Enhanced Transfer Detection Debug Script
Tests the enhanced exchange amount functionality with verbose debugging
"""

import sys
import os
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

# Test enhanced transfer detection with exchange amount support
def test_enhanced_transfer_detection():
    print("🚀 ENHANCED TRANSFER DETECTION DEBUG")
    print("=" * 70)
    
    try:
        # Import enhanced transfer detector
        from transfer_detector_enhanced_exchange import TransferDetector as EnhancedTransferDetector
        print("✅ Enhanced Transfer Detector with Exchange Amount Support: LOADED")
        enhanced_available = True
    except ImportError as e:
        print(f"❌ Enhanced Transfer Detector: NOT AVAILABLE - {e}")
        # Fallback to basic detector
        from transfer_detector import TransferDetector as EnhancedTransferDetector
        enhanced_available = False
    
    # Create test data simulating Wise EUR -> NayaPay PKR scenario
    print("\n📊 CREATING TEST DATA (Wise EUR -> NayaPay PKR)")
    
    # Wise CSV with Exchange To Amount
    wise_csv = {
        'file_name': 'wise_statement.csv',
        'data': [
            {
                'Date': '2025-06-01',
                'Amount': '-108.99',
                'Description': 'Sent money to Ammar Qazi',
                'Exchange To Amount': '30000',  # PKR amount
                'Currency': 'EUR'
            }
        ],
        'template_config': {
            'bank_name': 'Wise',
            'column_mapping': {
                'Date': 'Date',
                'Amount': 'Amount', 
                'Description': 'Description',
                'Exchange To Amount': 'Exchange To Amount'
            }
        }
    }
    
    # NayaPay CSV  
    nayapay_csv = {
        'file_name': 'nayapay_statement.csv',
        'data': [
            {
                'Date': '2025-06-01',
                'Amount': '30000',
                'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2050',
                'Currency': 'PKR'
            }
        ],
        'template_config': {
            'bank_name': 'NayaPay',
            'column_mapping': {
                'Date': 'Date',
                'Amount': 'Amount',
                'Description': 'Description'
            }
        }
    }
    
    csv_data_list = [wise_csv, nayapay_csv]
    
    print(f"   📁 Wise transaction: -108.99 EUR, Exchange To Amount: 30,000")
    print(f"   📁 NayaPay transaction: +30,000 PKR")
    
    # Initialize enhanced detector
    print(f"\n🔧 INITIALIZING ENHANCED TRANSFER DETECTOR...")
    detector = EnhancedTransferDetector(user_name="Ammar Qazi", date_tolerance_hours=24)
    
    # Test if enhanced functionality is available
    if enhanced_available:
        # Test the _get_exchange_amount method
        print(f"\n🧪 TESTING EXCHANGE AMOUNT EXTRACTION...")
        test_transaction = wise_csv['data'][0]
        test_transaction.update({
            '_csv_index': 0,
            '_transaction_index': 0,
            '_csv_name': 'wise_statement.csv',
            '_bank_type': 'wise'
        })
        
        exchange_amount = detector._get_exchange_amount(test_transaction)
        print(f"   💱 Exchange amount extracted: {exchange_amount}")
        
        if exchange_amount:
            print(f"   ✅ EXCHANGE AMOUNT EXTRACTION: WORKING")
        else:
            print(f"   ❌ EXCHANGE AMOUNT EXTRACTION: NOT WORKING")
    else:
        print(f"   ⚠️  Enhanced functionality not available - using basic detection")
    
    # Run transfer detection
    print(f"\n🔍 RUNNING ENHANCED TRANSFER DETECTION...")
    result = detector.detect_transfers(csv_data_list)
    
    print(f"\n📋 DETECTION RESULTS:")
    print(f"   🎯 Transfer pairs found: {result['summary']['transfer_pairs_found']}")
    print(f"   💱 Currency conversions: {result['summary']['currency_conversions']}")
    print(f"   🔄 Other transfers: {result['summary']['other_transfers']}")
    
    # Analyze detected transfers
    if result['transfers']:
        print(f"\n🔍 ANALYZING DETECTED TRANSFERS:")
        for i, transfer in enumerate(result['transfers']):
            print(f"   📤 Transfer {i+1}:")
            print(f"      🏦 Type: {transfer['transfer_type']}")
            print(f"      💰 Amount: {transfer['amount']}")
            print(f"      🎯 Confidence: {transfer['confidence']:.2f}")
            
            if 'exchange_amount' in transfer and transfer['exchange_amount']:
                print(f"      💱 Exchange Amount: {transfer['exchange_amount']}")
                print(f"      ✅ EXCHANGE AMOUNT MATCHING: WORKING")
            
            if 'match_strategy' in transfer:
                print(f"      🎯 Match Strategy: {transfer['match_strategy']}")
                
            print(f"      📤 Outgoing: {transfer['outgoing']['_csv_name']} | {transfer['outgoing'].get('Amount')}")
            print(f"      📥 Incoming: {transfer['incoming']['_csv_name']} | {transfer['incoming'].get('Amount')}")
    else:
        print(f"   ❌ NO TRANSFERS DETECTED")
    
    # Test transfer categorization
    if result['transfers']:
        print(f"\n📝 TESTING TRANSFER CATEGORIZATION...")
        transfer_matches = detector.apply_transfer_categorization(csv_data_list, result['transfers'])
        
        print(f"   📝 Transfer matches created: {len(transfer_matches)}")
        for match in transfer_matches:
            print(f"      📄 {match['transfer_type']}: {match['category']} | {match['note']}")
            if 'match_strategy' in match:
                print(f"         🎯 Strategy: {match['match_strategy']}")
    
    print(f"\n🎉 ENHANCED TRANSFER DETECTION DEBUG COMPLETE")
    print("=" * 70)
    
    return result, enhanced_available

if __name__ == "__main__":
    result, enhanced_available = test_enhanced_transfer_detection()
    
    # Summary
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   🚀 Enhanced detector available: {enhanced_available}")
    print(f"   🎯 Transfers detected: {len(result.get('transfers', []))}")
    
    if result.get('transfers'):
        print(f"   ✅ SUCCESS: Enhanced transfer detection is working!")
        
        # Check if exchange amount matching worked
        for transfer in result['transfers']:
            if transfer.get('match_strategy') == 'exchange_amount':
                print(f"   💱 SUCCESS: Exchange amount matching is working!")
                break
        else:
            print(f"   ⚠️  Exchange amount matching not used (may be working via other strategies)")
    else:
        print(f"   ❌ ISSUE: No transfers detected - may need debugging")
