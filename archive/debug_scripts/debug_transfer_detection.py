#!/usr/bin/env python3
"""
Debug script for Multi-CSV Transfer Detection
"""

import sys
import os
sys.path.append('backend')

from transfer_detector import TransferDetector
import json

def debug_transfer_detection():
    print("🔧 Debugging Multi-CSV Transfer Detection")
    print("=" * 50)
    
    # Sample data simulating two CSV files with transfers
    csv_data_huf = {
        'file_name': 'HUF_Account.csv',
        'data': [
            {
                'Date': '2024-03-02',
                'Amount': '-5000.00',
                'Currency': 'HUF',
                'Description': 'Converted HUF to EUR',
                'Exchange To Amount': '125.00'  # ~€125 EUR
            }
        ],
        'template_config': {
            'bank_name': 'Hungarian',
            'column_mapping': {'Date': 'Date', 'Amount': 'Amount', 'Title': 'Description'},
            'account_mapping': {'HUF': 'Hungarian'}
        }
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
        'template_config': {
            'bank_name': 'EURO Wise',
            'column_mapping': {'Date': 'Date', 'Amount': 'Amount', 'Title': 'Description'},
            'account_mapping': {'EUR': 'EURO Wise'}
        }
    }
    
    # Initialize transfer detector
    detector = TransferDetector(user_name="Ammar Qazi", date_tolerance_hours=24)
    
    # Test transfer detection
    csv_data_list = [csv_data_huf, csv_data_eur]
    
    # Create all transactions manually to debug
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
    
    print("📊 Enhanced Transactions:")
    for i, trans in enumerate(all_transactions):
        print(f"  {i}: {trans['Description']} | Amount: {trans['Amount']} | CSV: {trans['_csv_name']}")
    print()
    
    # Check potential transfers
    potential_transfers = detector._find_transfer_candidates(all_transactions)
    print("🔍 Potential Transfer Candidates:")
    for i, trans in enumerate(potential_transfers):
        print(f"  {i}: {trans['Description']} | Pattern: {trans.get('_transfer_pattern', 'None')}")
    print()
    
    # Check amounts and dates specifically
    print("💰 Amount and Date Analysis:")
    for trans in all_transactions:
        amount = detector._parse_amount(trans.get('Amount', '0'))
        exchange_amount = detector._parse_amount(trans.get('Exchange To Amount', '0'))
        date = detector._parse_date(trans.get('Date', ''))
        print(f"  {trans['Description']}:")
        print(f"    Amount: {amount} | Exchange: {exchange_amount} | Date: {date}")
    print()
    
    # Check pattern matching manually
    print("🎯 Pattern Matching Test:")
    for pattern in detector.transfer_patterns:
        print(f"  Pattern: {pattern}")
        for trans in all_transactions:
            description = str(trans.get('Description', '')).lower()
            import re
            if re.search(pattern, description, re.IGNORECASE):
                print(f"    ✅ Matches: {trans['Description']}")
            else:
                print(f"    ❌ No match: {trans['Description']}")
        print()
    
    # Run full detection
    results = detector.detect_transfers(csv_data_list)
    print("🔍 Final Detection Results:")
    print(f"  Transfer pairs found: {results['summary']['transfer_pairs_found']}")
    if results['transfers']:
        for pair in results['transfers']:
            print(f"  Found pair: {pair['outgoing']['Description']} -> {pair['incoming']['Description']}")
    
    return results

if __name__ == "__main__":
    debug_transfer_detection()
