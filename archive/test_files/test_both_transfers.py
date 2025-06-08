#!/usr/bin/env python3
"""
Test script to verify both transfer pairs are working
"""

import sys
import os
sys.path.append('backend')

from transfer_detector import TransferDetector

def test_both_transfers():
    print("🧪 Testing Both Transfer Pairs")
    print("=" * 50)
    
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
            }
        ],
        'template_config': {
            'bank_name': 'EURO Wise',
            'column_mapping': {'Date': 'Date', 'Amount': 'Amount', 'Title': 'Description'},
            'account_mapping': {'EUR': 'EURO Wise'}
        }
    }
    
    detector = TransferDetector(user_name="Ammar Qazi", date_tolerance_hours=24)
    csv_data_list = [csv_data_huf, csv_data_usd, csv_data_eur]
    
    results = detector.detect_transfers(csv_data_list)
    
    print(f"🔍 Transfer pairs found: {results['summary']['transfer_pairs_found']}")
    
    for i, pair in enumerate(results['transfers'], 1):
        print(f"  Transfer {i}:")
        print(f"    OUT: {pair['outgoing']['Description']} (-{pair['amount']})")
        print(f"    IN:  {pair['incoming']['Description']} (+{pair['incoming']['Amount']})")
        print(f"    Confidence: {pair['confidence']:.2f}")
        print()
    
    # Test categorization
    sample_transformed = [
        {'Date': '2024-03-01', 'Amount': '-1000.0', 'Category': 'Expense', 'Title': 'Sent to Ammar Qazi USD Account', 'Account': 'Hungarian'},
        {'Date': '2024-03-01', 'Amount': '300.0', 'Category': 'Income', 'Title': 'Received from Ammar Qazi HUF Account', 'Account': 'TransferWise'},
        {'Date': '2024-03-02', 'Amount': '-5000.0', 'Category': 'Expense', 'Title': 'Converted HUF to EUR', 'Account': 'Hungarian'},
        {'Date': '2024-03-02', 'Amount': '125.0', 'Category': 'Income', 'Title': 'Converted from HUF Account', 'Account': 'EURO Wise'},
    ]
    
    categorized_data = detector.apply_transfer_categorization(sample_transformed, results['transfers'])
    
    balance_corrections = len([t for t in categorized_data if t.get('Category') == 'Balance Correction'])
    print(f"✅ Balance corrections applied: {balance_corrections}")
    
    for i, transaction in enumerate(categorized_data):
        status = "🔄 TRANSFER" if transaction.get('_is_transfer') else "💰 REGULAR"
        print(f"  {i+1}. {status} {transaction['Title']} | Category: {transaction['Category']}")

if __name__ == "__main__":
    test_both_transfers()
