#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from transfer_detector_enhanced_ammar import TransferDetector

def diagnose_incoming_transactions():
    """Diagnose why incoming transactions are not being matched"""
    
    print("🔍 DIAGNOSING INCOMING TRANSACTION DETECTION")
    print("=" * 60)
    
    # Simulate the issue with real-like data
    csv_data_list = [
        {
            'file_name': 'nayapay_feb.csv',
            'data': [
                {
                    'Date': '2025-02-03',
                    'Amount': '50000.0',
                    'Description': 'Transfer from Ammar Qazi Bank Alfalah-2050',
                    'Category': 'Transfer'
                },
                {
                    'Date': '2025-02-04', 
                    'Amount': '23000.0',
                    'Description': 'Incoming fund transfer from Ammar Qazi',
                    'Category': 'Transfer'
                },
                {
                    'Date': '2025-02-05',
                    'Amount': '750.0', 
                    'Description': 'Regular incoming payment',
                    'Category': 'Income'
                }
            ],
            'template_config': {}
        },
        {
            'file_name': 'wise_USD.csv',
            'data': [
                {
                    'Date': '2025-02-03',
                    'Amount': '-100.0',
                    'Description': 'Sent money to Ammar Qazi',
                    'Category': 'Transfer',
                    'Exchange To Amount': '50000.0',
                    'Exchange To': 'PKR'
                },
                {
                    'Date': '2025-02-04',
                    'Amount': '-150.0', 
                    'Description': 'Sent money to Ammar Qazi',
                    'Category': 'Transfer',
                    'Exchange To Amount': '23000.0',
                    'Exchange To': 'PKR'
                },
                {
                    'Date': '2025-02-05',
                    'Amount': '-25.0',
                    'Description': 'Sent money to Someone Else',
                    'Category': 'Transfer'
                }
            ],
            'template_config': {}
        }
    ]
    
    # Initialize detector
    detector = TransferDetector(user_name="Ammar Qazi", date_tolerance_hours=24)
    
    # Manually call the internal methods to diagnose
    print("\n🔧 STEP 1: Flatten transactions")
    all_transactions = []
    for csv_idx, csv_data in enumerate(csv_data_list):
        for trans_idx, transaction in enumerate(csv_data['data']):
            enhanced_transaction = {
                **transaction,
                '_csv_index': csv_idx,
                '_transaction_index': trans_idx,
                '_csv_name': csv_data.get('file_name', f'CSV_{csv_idx}'),
                '_template_config': csv_data.get('template_config', {}),
                '_bank_type': detector._detect_bank_type(csv_data.get('file_name', ''), transaction),
                '_raw_data': transaction
            }
            all_transactions.append(enhanced_transaction)
    
    print(f"✅ Total transactions: {len(all_transactions)}")
    
    # Check incoming transactions specifically
    print("\n🔧 STEP 2: Analyze incoming transactions")
    incoming_transactions = [
        t for t in all_transactions 
        if detector._parse_amount(t.get('Amount', '0')) > 0
    ]
    
    print(f"✅ Incoming transactions found: {len(incoming_transactions)}")
    
    for i, trans in enumerate(incoming_transactions):
        print(f"\n📥 Incoming {i+1}:")
        print(f"   💰 Amount: {trans.get('Amount')}")
        print(f"   📝 Description: {trans.get('Description')}")
        print(f"   🏦 Bank: {trans.get('_bank_type')}")
        print(f"   📁 File: {trans.get('_csv_name')}")
        
        # Test Ammar pattern matching manually
        desc = str(trans.get('Description', '')).lower()
        user_name_lower = "ammar qazi"
        
        transfer_from_ammar = ('transfer from' in desc and user_name_lower in desc)
        incoming_fund_from_ammar = ('incoming fund transfer from' in desc and user_name_lower in desc)
        incoming_from_ammar = transfer_from_ammar or incoming_fund_from_ammar
        
        print(f"   🔍 Pattern analysis:")
        print(f"      'transfer from' + 'ammar qazi': {transfer_from_ammar}")
        print(f"      'incoming fund transfer from' + 'ammar qazi': {incoming_fund_from_ammar}")
        print(f"      Combined result: {incoming_from_ammar}")
    
    # Check potential transfer candidates
    print("\n🔧 STEP 3: Check transfer candidates")
    potential_transfers = detector._find_transfer_candidates(all_transactions)
    print(f"✅ Potential transfer candidates: {len(potential_transfers)}")
    
    for i, trans in enumerate(potential_transfers):
        print(f"\n🎯 Candidate {i+1}:")
        print(f"   💰 Amount: {trans.get('Amount')}")
        print(f"   📝 Description: {trans.get('Description')}")
        print(f"   🏦 Bank: {trans.get('_bank_type')}")
        print(f"   📁 File: {trans.get('_csv_name')}")
        print(f"   🔄 Pattern: {trans.get('_transfer_pattern', 'None')}")
    
    # Now run the full detection to see what happens
    print("\n🔧 STEP 4: Run full detection")
    result = detector.detect_transfers(csv_data_list)
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"   Total transfer pairs: {len(result['transfers'])}")
    print(f"   Cross-bank transfers: {result['summary']['other_transfers']}")
    
    if result['transfers']:
        print("\n✅ Transfers found:")
        for i, transfer in enumerate(result['transfers']):
            print(f"   Transfer {i+1}:")
            print(f"      📤 Outgoing: {transfer['outgoing']['Description']}")
            print(f"      📥 Incoming: {transfer['incoming']['Description']}")
            print(f"      💰 Amount: {transfer['amount']}")
            print(f"      🎯 Confidence: {transfer['confidence']}")
    else:
        print("\n❌ No transfers detected")
        
        # Additional diagnosis
        print("\n🔍 ADDITIONAL DIAGNOSIS:")
        available_outgoing = [
            t for t in potential_transfers 
            if detector._parse_amount(t.get('Amount', '0')) < 0
        ]
        available_incoming = [
            t for t in all_transactions 
            if detector._parse_amount(t.get('Amount', '0')) > 0
        ]
        
        print(f"   Available outgoing: {len(available_outgoing)}")
        print(f"   Available incoming: {len(available_incoming)}")
        
        # Test a specific pairing manually
        if available_outgoing and available_incoming:
            outgoing = available_outgoing[0]  # First outgoing Wise transaction
            incoming = available_incoming[0]  # First incoming NayaPay transaction
            
            print(f"\n🧪 Testing specific pair:")
            print(f"   📤 Outgoing: {outgoing['Description']}")
            print(f"   📥 Incoming: {incoming['Description']}")
            
            is_match = detector._is_ammar_cross_bank_transfer(outgoing, incoming)
            print(f"   🎯 Is Ammar cross-bank transfer: {is_match}")

if __name__ == "__main__":
    diagnose_incoming_transactions()
