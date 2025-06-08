#!/usr/bin/env python3
"""
Test script for Multi-CSV Transfer Detection
"""

import sys
import os
sys.path.append('backend')

from transfer_detector import TransferDetector
import json

def test_transfer_detection():
    print("🧪 Testing Multi-CSV Transfer Detection")
    print("=" * 50)
    
    # Sample data simulating two CSV files with transfers
    csv_data_huf = {
        'file_name': 'HUF_Account.csv',
        'data': [
            {
                'Date': '2024-03-01',
                'Amount': '-1000.00',
                'Currency': 'HUF',
                'Description': 'Sent to Ammar Qazi USD Account',
                'Exchange To Amount': '300.00'  # ~$300 USD
            },
            {
                'Date': '2024-03-02',
                'Amount': '-5000.00',
                'Currency': 'HUF',
                'Description': 'Converted HUF to EUR',
                'Exchange To Amount': '125.00'  # ~€125 EUR
            },
            {
                'Date': '2024-03-03',
                'Amount': '-2000.00',
                'Currency': 'HUF',
                'Description': 'Lidl Budapest Central',
                'Exchange To Amount': ''
            }
        ],
        'template_config': {
            'bank_name': 'Hungarian',
            'column_mapping': {'Date': 'Date', 'Amount': 'Amount', 'Title': 'Description'},
            'account_mapping': {'HUF': 'Hungarian'}
        }
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
        'template_config': {
            'bank_name': 'TransferWise',
            'column_mapping': {'Date': 'Date', 'Amount': 'Amount', 'Title': 'Description'},
            'account_mapping': {'USD': 'TransferWise'}
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
            },
            {
                'Date': '2024-03-05',
                'Amount': '-80.00',
                'Currency': 'EUR',
                'Description': 'Hotels.com Booking',
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
    csv_data_list = [csv_data_huf, csv_data_usd, csv_data_eur]
    
    print("📊 Input Data:")
    for csv_data in csv_data_list:
        print(f"  {csv_data['file_name']}: {len(csv_data['data'])} transactions")
    print()
    
    # Detect transfers
    results = detector.detect_transfers(csv_data_list)
    
    print("🔍 Transfer Detection Results:")
    print(f"  Total transactions processed: {results['summary']['total_transactions']}")
    print(f"  Transfer pairs found: {results['summary']['transfer_pairs_found']}")
    print(f"  Potential transfers: {results['summary']['potential_transfers']}")
    print(f"  Conflicts detected: {results['summary']['conflicts']}")
    print(f"  Flagged for review: {results['summary']['flagged_for_review']}")
    print()
    
    # Show detected transfer pairs
    if results['transfers']:
        print("💸 Detected Transfer Pairs:")
        for i, pair in enumerate(results['transfers'], 1):
            print(f"  Transfer {i}:")
            print(f"    Outgoing: {pair['outgoing']['Description']} (-{pair['amount']})")
            print(f"    From: {pair['outgoing']['_csv_name']}")
            print(f"    Incoming: {pair['incoming']['Description']} (+{pair['incoming']['Amount']})")
            print(f"    To: {pair['incoming']['_csv_name']}")
            print(f"    Date: {pair['date']}")
            print(f"    Confidence: {pair['confidence']:.2f}")
            if pair.get('exchange_amount'):
                print(f"    Exchange Amount: {pair['exchange_amount']}")
            print()
    
    # Show conflicts if any
    if results['conflicts']:
        print("⚠️  Conflicts Detected:")
        for i, conflict in enumerate(results['conflicts'], 1):
            print(f"  Conflict {i}: {conflict['conflict_type']}")
            print(f"    Transaction: {conflict['outgoing_transaction']['Description']}")
            print(f"    Multiple matches: {len(conflict['potential_matches'])}")
            print()
    
    # Show flagged transactions
    if results['flagged_transactions']:
        print("🚩 Flagged for Manual Review:")
        for i, flagged in enumerate(results['flagged_transactions'], 1):
            print(f"  {i}. {flagged['Description']} ({flagged['_flag_reason']})")
            print(f"     Amount: {flagged['Amount']} from {flagged['_csv_name']}")
            print()
    
    # Test categorization application
    print("🏷️  Testing Balance Correction Application:")
    
    # Create sample transformed data
    sample_transformed = [
        {'Date': '2024-03-01', 'Amount': '-1000.0', 'Category': 'Expense', 'Title': 'Sent to Ammar Qazi USD Account', 'Account': 'Hungarian'},
        {'Date': '2024-03-01', 'Amount': '300.0', 'Category': 'Income', 'Title': 'Received from Ammar Qazi HUF Account', 'Account': 'TransferWise'},
        {'Date': '2024-03-02', 'Amount': '-5000.0', 'Category': 'Expense', 'Title': 'Converted HUF to EUR', 'Account': 'Hungarian'},
        {'Date': '2024-03-02', 'Amount': '125.0', 'Category': 'Income', 'Title': 'Converted from HUF Account', 'Account': 'EURO Wise'},
        {'Date': '2024-03-03', 'Amount': '-2000.0', 'Category': 'Groceries', 'Title': 'Lidl Budapest Central', 'Account': 'Hungarian'},
        {'Date': '2024-03-04', 'Amount': '-150.0', 'Category': 'Shopping', 'Title': 'Amazon Online Purchase', 'Account': 'TransferWise'},
        {'Date': '2024-03-05', 'Amount': '-80.0', 'Category': 'Travel', 'Title': 'Hotels.com Booking', 'Account': 'EURO Wise'},
    ]
    
    # Apply transfer categorization
    categorized_data = detector.apply_transfer_categorization(sample_transformed, results['transfers'])
    
    print("📋 Final Categorized Results:")
    for i, transaction in enumerate(categorized_data):
        status = "🔄 TRANSFER" if transaction.get('_is_transfer') else "💰 REGULAR"
        print(f"  {i+1}. {status} {transaction['Title']}")
        print(f"     Amount: {transaction['Amount']} | Category: {transaction['Category']}")
        print(f"     Account: {transaction['Account']}")
        if transaction.get('_is_transfer'):
            print(f"     Transfer Type: {transaction.get('_transfer_type')}")
            print(f"     Pair ID: {transaction.get('_transfer_pair_id')}")
        print()
    
    # Summary
    transfers_applied = len([t for t in categorized_data if t.get('Category') == 'Balance Correction'])
    print(f"✅ Summary: {transfers_applied} transactions categorized as 'Balance Correction'")
    
    return results['summary']['transfer_pairs_found'] > 0

if __name__ == "__main__":
    success = test_transfer_detection()
    if success:
        print("\n🎉 Transfer detection working correctly!")
    else:
        print("\n💥 No transfers detected - check test data or logic.")
