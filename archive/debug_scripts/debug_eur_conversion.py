#!/usr/bin/env python3
"""
Specific debug for the EUR conversion transfer
"""

import sys
import os
sys.path.append('backend')

from transfer_detector import TransferDetector

def debug_eur_conversion():
    print("🔧 Debugging EUR Conversion Transfer")
    print("=" * 50)
    
    # Just the EUR conversion pair
    csv_data_huf = {
        'file_name': 'HUF_Account.csv',
        'data': [
            {
                'Date': '2024-03-02',
                'Amount': '-5000.00',
                'Currency': 'HUF',
                'Description': 'Converted HUF to EUR',
                'Exchange To Amount': '125.00'
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
            }
        ],
        'template_config': {}
    }
    
    detector = TransferDetector(user_name="Ammar Qazi", date_tolerance_hours=24)
    csv_data_list = [csv_data_huf, csv_data_eur]
    
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
    
    print("📊 All transactions:")
    for i, trans in enumerate(all_transactions):
        amount = detector._parse_amount(trans.get('Amount', '0'))
        exchange = detector._parse_amount(trans.get('Exchange To Amount', '0'))
        print(f"  {i}: {trans['Description']} | Amount: {amount} | Exchange: {exchange}")
    
    # Find potential transfers
    potential_transfers = detector._find_transfer_candidates(all_transactions)
    print(f"\n🔍 Potential transfers found: {len(potential_transfers)}")
    for i, trans in enumerate(potential_transfers):
        amount = detector._parse_amount(trans.get('Amount', '0'))
        print(f"  {i}: {trans['Description']} | Amount: {amount} | Negative: {amount < 0}")
    
    # Check outgoing candidates specifically
    outgoing_candidates = [t for t in potential_transfers if detector._parse_amount(t.get('Amount', '0')) < 0]
    print(f"\n📤 Outgoing candidates: {len(outgoing_candidates)}")
    for i, trans in enumerate(outgoing_candidates):
        print(f"  {i}: {trans['Description']}")
    
    # Manual matching test
    if len(outgoing_candidates) > 0:
        outgoing = outgoing_candidates[0]
        print(f"\n🔗 Testing match for: {outgoing['Description']}")
        
        outgoing_amount = detector._parse_amount(outgoing.get('Amount', '0'))
        outgoing_date = detector._parse_date(outgoing.get('Date', ''))
        outgoing_exchange_to = detector._parse_amount(outgoing.get('Exchange To Amount', '0'))
        
        print(f"  Outgoing amount: {outgoing_amount}")
        print(f"  Exchange amount: {outgoing_exchange_to}")
        print(f"  Date: {outgoing_date}")
        
        for incoming in all_transactions:
            if incoming['_csv_index'] == outgoing['_csv_index']:
                continue
                
            incoming_amount = detector._parse_amount(incoming.get('Amount', '0'))
            incoming_date = detector._parse_date(incoming.get('Date', ''))
            
            print(f"\n  Testing against: {incoming['Description']}")
            print(f"    Incoming amount: {incoming_amount}")
            print(f"    Positive: {incoming_amount > 0}")
            
            if incoming_amount > 0:
                # Check amount matching
                amount_match = False
                if outgoing_exchange_to != 0:
                    amount_match = abs(outgoing_exchange_to - incoming_amount) < 0.01
                    print(f"    Exchange match: {outgoing_exchange_to} vs {incoming_amount} = {amount_match}")
                else:
                    amount_match = abs(abs(outgoing_amount) - incoming_amount) < 0.01
                    print(f"    Amount match: {abs(outgoing_amount)} vs {incoming_amount} = {amount_match}")
                
                # Check date match
                date_match = detector._dates_within_tolerance(outgoing_date, incoming_date)
                print(f"    Date match: {date_match}")
                
                if amount_match and date_match:
                    print(f"    ✅ MATCH FOUND!")
                else:
                    print(f"    ❌ No match")
    
    # Run full detection
    results = detector.detect_transfers(csv_data_list)
    print(f"\n🎯 Final result: {results['summary']['transfer_pairs_found']} pairs found")
    
if __name__ == "__main__":
    debug_eur_conversion()
