#!/usr/bin/env python3
"""
Debug the full transfer detection process
"""

import sys
import os
sys.path.append('backend')

from transfer_detector import TransferDetector

def debug_full_detection():
    print("🔧 Debugging Full Transfer Detection Process")
    print("=" * 60)
    
    # Complete test data
    csv_data_huf = {
        'file_name': 'HUF_Account.csv',
        'data': [
            {
                'Date': '2024-03-01',
                'Amount': '-1000.00',
                'Currency': 'HUF',
                'Description': 'Sent to Ammar Qazi USD Account',
                'Exchange To Amount': '300.00'
            },
            {
                'Date': '2024-03-02',
                'Amount': '-5000.00',
                'Currency': 'HUF',
                'Description': 'Converted HUF to EUR',
                'Exchange To Amount': '125.00'
            },
            {
                'Date': '2024-03-03',
                'Amount': '-2000.00',
                'Currency': 'HUF',
                'Description': 'Lidl Budapest Central',
                'Exchange To Amount': ''
            }
        ],
        'template_config': {}
    }
    
    csv_data_usd = {
        'file_name': 'USD_Account.csv',
        'data': [
            {
                'Date': '2024-03-01',
                'Amount': '300.00',
                'Currency': 'USD',
                'Description': 'Received from Ammar Qazi HUF Account',
                'Exchange To Amount': ''
            },
            {
                'Date': '2024-03-04',
                'Amount': '-150.00',
                'Currency': 'USD',
                'Description': 'Amazon Online Purchase',
                'Exchange To Amount': ''
            }
        ],
        'template_config': {}
    }
    
    csv_data_eur = {
        'file_name': 'EUR_Account.csv',
        'data': [
            {
                'Date': '2024-03-02',
                'Amount': '125.00',
                'Currency': 'EUR',
                'Description': 'Converted from HUF Account',
                'Exchange To Amount': ''
            },
            {
                'Date': '2024-03-05',
                'Amount': '-80.00',
                'Currency': 'EUR',
                'Description': 'Hotels.com Booking',
                'Exchange To Amount': ''
            }
        ],
        'template_config': {}
    }
    
    detector = TransferDetector(user_name="Ammar Qazi", date_tolerance_hours=24)
    csv_data_list = [csv_data_huf, csv_data_usd, csv_data_eur]
    
    # Create all transactions manually
    all_transactions = []
    for csv_idx, csv_data in enumerate(csv_data_list):
        for trans_idx, transaction in enumerate(csv_data['data']):
            enhanced_transaction = {
                **transaction,
                '_csv_index': csv_idx,
                '_transaction_index': trans_idx,
                '_csv_name': csv_data.get('file_name', f'CSV_{csv_idx}'),
                '_template_config': csv_data.get('template_config', {})
            }
            all_transactions.append(enhanced_transaction)
    
    print("📊 All transactions with indices:")
    for trans in all_transactions:
        amount = detector._parse_amount(trans.get('Amount', '0'))
        print(f"  [{trans['_transaction_index']}] {trans['Description']} | Amount: {amount} | CSV: {trans['_csv_name']}")
    
    # Find potential transfers
    potential_transfers = detector._find_transfer_candidates(all_transactions)
    print(f"\n🔍 Potential transfers ({len(potential_transfers)}):")
    for trans in potential_transfers:
        amount = detector._parse_amount(trans.get('Amount', '0'))
        print(f"  [{trans['_transaction_index']}] {trans['Description']} | Amount: {amount} | Negative: {amount < 0}")
    
    # Check outgoing candidates
    outgoing_candidates = [t for t in potential_transfers if detector._parse_amount(t.get('Amount', '0')) < 0]
    print(f"\n📤 Outgoing candidates ({len(outgoing_candidates)}):")
    for trans in outgoing_candidates:
        print(f"  [{trans['_transaction_index']}] {trans['Description']}")
    
    # Manual step-by-step matching simulation
    print(f"\n🔗 Step-by-step matching simulation:")
    matched_transactions = set()
    transfer_pairs = []
    
    for i, outgoing in enumerate(outgoing_candidates):
        print(f"\n  Step {i+1}: Processing outgoing [{outgoing['_transaction_index']}] {outgoing['Description']}")
        
        if outgoing['_transaction_index'] in matched_transactions:
            print(f"    ❌ Already matched, skipping")
            continue
            
        outgoing_amount = detector._parse_amount(outgoing.get('Amount', '0'))
        outgoing_date = detector._parse_date(outgoing.get('Date', ''))
        outgoing_exchange_to = detector._parse_amount(outgoing.get('Exchange To Amount', '0'))
        
        print(f"    Amount: {outgoing_amount} | Exchange: {outgoing_exchange_to}")
        
        found_match = False
        for incoming in all_transactions:
            if incoming['_transaction_index'] in matched_transactions:
                continue
                
            if incoming['_csv_index'] == outgoing['_csv_index']:
                continue
            
            incoming_amount = detector._parse_amount(incoming.get('Amount', '0'))
            incoming_date = detector._parse_date(incoming.get('Date', ''))
            
            if incoming_amount <= 0:
                continue
            
            # Check amount matching
            amount_match = False
            if outgoing_exchange_to != 0:
                amount_match = abs(outgoing_exchange_to - incoming_amount) < 0.01
            else:
                amount_match = abs(abs(outgoing_amount) - incoming_amount) < 0.01
            
            # Check date match
            date_match = detector._dates_within_tolerance(outgoing_date, incoming_date)
            
            if amount_match and date_match:
                print(f"    ✅ MATCHED with [{incoming['_transaction_index']}] {incoming['Description']}")
                transfer_pairs.append({
                    'outgoing': outgoing,
                    'incoming': incoming,
                    'pair_id': f'transfer_{len(transfer_pairs)}'
                })
                matched_transactions.add(outgoing['_transaction_index'])
                matched_transactions.add(incoming['_transaction_index'])
                found_match = True
                break
        
        if not found_match:
            print(f"    ❌ No match found")
    
    print(f"\n🎯 Manual simulation result: {len(transfer_pairs)} pairs found")
    for pair in transfer_pairs:
        print(f"  {pair['outgoing']['Description']} -> {pair['incoming']['Description']}")
    
    # Compare with actual detection
    results = detector.detect_transfers(csv_data_list)
    print(f"\n🔍 Actual detection result: {results['summary']['transfer_pairs_found']} pairs found")
    for pair in results['transfers']:
        print(f"  {pair['outgoing']['Description']} -> {pair['incoming']['Description']}")

if __name__ == "__main__":
    debug_full_detection()
