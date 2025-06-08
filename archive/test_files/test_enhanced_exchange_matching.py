#!/usr/bin/env python3
"""
Test script for enhanced exchange amount matching functionality
Demonstrates how -108.99 EUR with Exchange To Amount 30,000 PKR 
can match with incoming 30,000 PKR transfer in NayaPay
"""

import sys
import os
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from transfer_detector_enhanced_exchange import TransferDetector
from datetime import datetime

def test_exchange_amount_matching():
    """Test the enhanced exchange amount matching functionality"""
    
    print("🧪 TESTING ENHANCED EXCHANGE AMOUNT MATCHING")
    print("=" * 60)
    
    # Sample data simulating your scenario:
    # Wise: -108.99 EUR with Exchange To Amount: 30,000 PKR
    # NayaPay: +30,000 PKR incoming transfer
    
    # Mock CSV data structure
    wise_data = {
        'file_name': 'wise_statement.csv',
        'data': [
            {
                'Date': '2025-02-14',
                'Amount': '-108.99',
                'Currency': 'EUR',
                'Description': 'Sent money to Ammar Qazi',
                'Payment Reference': 'International transfer',
                'Exchange To Amount': '30000.00',  # THIS IS THE KEY FIELD
                'Exchange From': 'EUR',
                'Exchange To': 'PKR',
                'Exchange Rate': '275.23'
            },
            {
                'Date': '2025-02-14',
                'Amount': '-50.00',
                'Currency': 'USD',
                'Description': 'Regular transfer without exchange',
                'Payment Reference': 'Normal transfer',
                'Exchange To Amount': '',  # No exchange amount
            }
        ],
        'template_config': {'bank_name': 'Wise'}
    }
    
    nayapay_data = {
        'file_name': 'nayapay_statement.csv', 
        'data': [
            {
                'Date': '2025-02-14',
                'Amount': '30000.00',
                'Title': 'IBFT In',
                'Note': 'Incoming fund transfer from Ammar Qazi\nBank Alfalah-2050|Transaction ID 192351',
                'Currency': 'PKR'
            },
            {
                'Date': '2025-02-14',
                'Amount': '50.00',
                'Title': 'Regular Transfer',
                'Note': 'Another incoming transfer',
                'Currency': 'PKR'
            }
        ],
        'template_config': {'bank_name': 'NayaPay'}
    }
    
    # Initialize the enhanced transfer detector
    detector = TransferDetector(user_name="Ammar Qazi", date_tolerance_hours=24)
    
    # Run detection
    csv_data_list = [wise_data, nayapay_data]
    results = detector.detect_transfers(csv_data_list)
    
    print("\n📊 DETAILED RESULTS:")
    print("=" * 60)
    
    # Print summary
    summary = results['summary']
    print(f"Total transactions processed: {summary['total_transactions']}")
    print(f"Transfer pairs found: {summary['transfer_pairs_found']}")
    print(f"Currency conversions: {summary['currency_conversions']}")
    print(f"Other transfers: {summary['other_transfers']}")
    
    # Print each detected transfer pair
    print(f"\n🎯 DETECTED TRANSFER PAIRS ({len(results['transfers'])}):")
    print("-" * 60)
    
    for i, pair in enumerate(results['transfers']):
        print(f"\n📌 PAIR {i+1}: {pair['pair_id']}")
        print(f"   Type: {pair['transfer_type']}")
        print(f"   Strategy: {pair.get('match_strategy', 'N/A')}")
        print(f"   Confidence: {pair['confidence']:.2f}")
        
        # Outgoing transaction
        out = pair['outgoing']
        print(f"   📤 OUTGOING ({out['_csv_name']}):")
        print(f"      Amount: {out.get('Amount')} {out.get('Currency', '')}")
        print(f"      Date: {out.get('Date')}")
        print(f"      Description: {out.get('Description', '')[:80]}...")
        
        # Show exchange amount if available
        if pair.get('exchange_amount'):
            print(f"      💱 Exchange Amount: {pair['exchange_amount']}")
        
        # Incoming transaction
        inc = pair['incoming']
        print(f"   📥 INCOMING ({inc['_csv_name']}):")
        print(f"      Amount: {inc.get('Amount')} {inc.get('Currency', '')}")
        print(f"      Date: {inc.get('Date')}")
        print(f"      Description: {inc.get('Title', inc.get('Description', ''))[:80]}...")
        
        print(f"   💰 Matched Amount: {pair.get('matched_amount', 'N/A')}")
    
    # Show potential transfers that weren't matched
    print(f"\n🤔 POTENTIAL TRANSFERS NOT MATCHED ({len(results['potential_transfers'])}):")
    print("-" * 60)
    
    matched_ids = set()
    for pair in results['transfers']:
        matched_ids.add(pair['outgoing']['_transaction_index'])
        matched_ids.add(pair['incoming']['_transaction_index'])
    
    unmatched_potential = [t for t in results['potential_transfers'] if t['_transaction_index'] not in matched_ids]
    
    for i, trans in enumerate(unmatched_potential):
        print(f"{i+1}. {trans['_csv_name']}: {trans.get('Amount')} - {trans.get('Description', trans.get('Title', ''))[:60]}...")
    
    return results

def test_edge_cases():
    """Test various edge cases for exchange amount matching"""
    
    print("\n\n🧪 TESTING EDGE CASES")
    print("=" * 60)
    
    # Test case with multiple exchange amounts
    wise_data = {
        'file_name': 'wise_multiple_exchanges.csv',
        'data': [
            {
                'Date': '2025-02-15',
                'Amount': '-200.00',
                'Currency': 'USD',
                'Description': 'Sent money to Ammar Qazi',
                'Exchange To Amount': '55000.00',  # PKR equivalent
            },
            {
                'Date': '2025-02-15',
                'Amount': '-150.00',
                'Currency': 'EUR',
                'Description': 'Another transfer to Ammar Qazi',
                'Exchange To Amount': '45000.00',  # PKR equivalent
            }
        ]
    }
    
    nayapay_data = {
        'file_name': 'nayapay_multiple_incoming.csv',
        'data': [
            {
                'Date': '2025-02-15',
                'Amount': '55000.00',
                'Title': 'IBFT In',
                'Note': 'Incoming fund transfer from Ammar Qazi',
            },
            {
                'Date': '2025-02-15', 
                'Amount': '45000.00',
                'Title': 'IBFT In',
                'Note': 'Incoming fund transfer from Ammar Qazi',
            },
            {
                'Date': '2025-02-15',
                'Amount': '20000.00',
                'Title': 'IBFT In', 
                'Note': 'Unmatched transfer',
            }
        ]
    }
    
    detector = TransferDetector(user_name="Ammar Qazi")
    results = detector.detect_transfers([wise_data, nayapay_data])
    
    print(f"Edge case results: Found {len(results['transfers'])} pairs")
    for pair in results['transfers']:
        print(f"- {pair['match_strategy']}: {pair['outgoing']['Amount']} -> {pair['incoming']['Amount']}")
    
    return results

if __name__ == "__main__":
    print("🚀 ENHANCED EXCHANGE AMOUNT MATCHING TEST")
    print("=" * 60)
    print("This test demonstrates how the enhanced transfer detector can match:")
    print("  • Wise transaction: -108.99 EUR (Exchange To Amount: 30,000 PKR)")
    print("  • NayaPay transaction: +30,000 PKR (incoming transfer)")
    print("=" * 60)
    
    # Run main test
    main_results = test_exchange_amount_matching()
    
    # Run edge cases
    edge_results = test_edge_cases()
    
    print("\n✅ TEST COMPLETED!")
    print(f"Main test: {len(main_results['transfers'])} pairs found")
    print(f"Edge test: {len(edge_results['transfers'])} pairs found")
    
    # Check if our specific scenario was detected
    exchange_matches = [p for p in main_results['transfers'] if p.get('match_strategy') == 'exchange_amount']
    
    if exchange_matches:
        print(f"\n🎉 SUCCESS! Found {len(exchange_matches)} exchange amount matches!")
        print("The system can now detect transfers using exchange amounts.")
    else:
        print(f"\n⚠️  No exchange amount matches found. Traditional matches: {len(main_results['transfers'])}")
        print("Check if exchange amount columns are properly detected.")
