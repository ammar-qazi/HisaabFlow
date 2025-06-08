#!/usr/bin/env python3
"""
Debug script for currency transfer detection issues
Specifically for USD 22.83 → EUR 20 case
"""

import sys
import os
sys.path.append('.')

from backend.transfer_detection import TransferDetector, ConfigurationManager
import json
from datetime import datetime

def debug_currency_transfer():
    """Debug the specific case of USD 22.83 → EUR 20"""
    
    print("🐛 DEBUGGING CURRENCY TRANSFER DETECTION")
    print("=" * 60)
    print("🎯 Target: USD 22.83 → EUR 20.00")
    print("=" * 60)
    
    # Initialize configuration
    config = ConfigurationManager("configs")
    detector = TransferDetector("configs")
    
    # Create realistic test data based on actual Wise CSV format
    mock_csv_data = [
        {
            'file_name': 'wise_usd_statement.csv',
            'data': [
                {
                    'Date': '2025-01-15',
                    'Description': 'Send money to Ammar Qazi',
                    'Amount': '-22.83',
                    'Currency': 'USD',
                    'Exchange To Amount': '20.00',
                    'Exchange To': 'EUR',
                    'Status': 'COMPLETED',
                    'Source': 'USD Balance'
                }
            ]
        },
        {
            'file_name': 'wise_eur_statement.csv', 
            'data': [
                {
                    'Date': '2025-01-15',
                    'Description': 'Received money from Ammar Qazi',
                    'Amount': '20.00',
                    'Currency': 'EUR',
                    'Status': 'COMPLETED',
                    'Source': 'EUR Balance'
                }
            ]
        }
    ]
    
    print("\n📊 INPUT DATA:")
    print("-" * 40)
    for i, csv_data in enumerate(mock_csv_data):
        print(f"CSV {i}: {csv_data['file_name']}")
        for j, transaction in enumerate(csv_data['data']):
            print(f"  Transaction {j}:")
            for key, value in transaction.items():
                print(f"    {key}: {value}")
        print()
    
    # Add detailed debugging to the detector
    print("\n🔍 STEP-BY-STEP DEBUGGING:")
    print("-" * 40)
    
    # Step 1: Bank Detection
    print("\n1️⃣ BANK DETECTION:")
    for csv_data in mock_csv_data:
        bank_type = config.detect_bank_type(csv_data['file_name'])
        print(f"   📁 {csv_data['file_name']} → {bank_type}")
        
        if bank_type:
            outgoing_patterns = config.get_transfer_patterns(bank_type, 'outgoing')
            incoming_patterns = config.get_transfer_patterns(bank_type, 'incoming')
            print(f"      📤 Outgoing patterns: {outgoing_patterns}")
            print(f"      📥 Incoming patterns: {incoming_patterns}")
    
    # Step 2: Transaction Processing
    print("\n2️⃣ TRANSACTION PROCESSING:")
    all_transactions = []
    
    for csv_index, csv_data in enumerate(mock_csv_data):
        bank_type = config.detect_bank_type(csv_data['file_name'])
        print(f"\n   📁 Processing {csv_data['file_name']} (bank: {bank_type})")
        
        for trans_index, transaction in enumerate(csv_data['data']):
            # Add metadata like the detector does
            enhanced_transaction = {
                **transaction,
                '_csv_index': csv_index,
                '_transaction_index': len(all_transactions),
                '_bank_type': bank_type,
                '_file_name': csv_data['file_name']
            }
            all_transactions.append(enhanced_transaction)
            
            print(f"      Transaction {trans_index}:")
            print(f"        📅 Date: {transaction.get('Date')}")
            print(f"        📝 Description: {transaction.get('Description')}")
            print(f"        💰 Amount: {transaction.get('Amount')}")
            print(f"        💱 Currency: {transaction.get('Currency')}")
            
            # Check if this looks like an outgoing transfer
            desc = str(transaction.get('Description', '')).lower()
            user_name_lower = config.get_user_name().lower()
            
            outgoing_patterns = config.get_transfer_patterns(bank_type, 'outgoing') if bank_type else []
            incoming_patterns = config.get_transfer_patterns(bank_type, 'incoming') if bank_type else []
            
            is_outgoing = any(user_name_lower in pattern.lower() for pattern in outgoing_patterns)
            is_incoming = any(user_name_lower in pattern.lower() for pattern in incoming_patterns)
            
            print(f"        🔍 Matches outgoing pattern: {is_outgoing}")
            print(f"        🔍 Matches incoming pattern: {is_incoming}")
    
    # Step 3: Transfer Candidate Detection
    print("\n3️⃣ TRANSFER CANDIDATE DETECTION:")
    transfer_candidates = []
    
    for transaction in all_transactions:
        desc = str(transaction.get('Description', '')).lower()
        bank_type = transaction.get('_bank_type')
        
        if not bank_type:
            continue
            
        outgoing_patterns = config.get_transfer_patterns(bank_type, 'outgoing')
        incoming_patterns = config.get_transfer_patterns(bank_type, 'incoming')
        
        user_name_lower = config.get_user_name().lower()
        
        is_outgoing = any(user_name_lower in pattern.lower() for pattern in outgoing_patterns)
        is_incoming = any(user_name_lower in pattern.lower() for pattern in incoming_patterns)
        
        if is_outgoing or is_incoming:
            transfer_candidates.append(transaction)
            print(f"   ✅ Candidate: {transaction['_file_name']} - {transaction.get('Description')} ({transaction.get('Amount')})")
    
    print(f"\n   📊 Found {len(transfer_candidates)} transfer candidates")
    
    # Step 4: Cross-Bank Matching
    print("\n4️⃣ CROSS-BANK TRANSFER MATCHING:")
    
    if len(transfer_candidates) >= 2:
        print("   🔍 Attempting to match candidates...")
        
        for i, cand1 in enumerate(transfer_candidates):
            for j, cand2 in enumerate(transfer_candidates):
                if i >= j:
                    continue
                    
                print(f"\n   🔄 Comparing candidates {i} and {j}:")
                print(f"      Candidate {i}: {cand1['_file_name']} | {cand1.get('Amount')} {cand1.get('Currency')}")
                print(f"      Candidate {j}: {cand2['_file_name']} | {cand2.get('Amount')} {cand2.get('Currency')}")
                
                # Check if they are from different banks
                different_banks = cand1.get('_bank_type') != cand2.get('_bank_type')
                print(f"      🏦 Different banks: {different_banks}")
                
                # Check amount signs
                try:
                    amount1 = float(str(cand1.get('Amount', '0')).replace(',', ''))
                    amount2 = float(str(cand2.get('Amount', '0')).replace(',', ''))
                    opposite_signs = (amount1 * amount2) < 0
                    print(f"      💰 Amount1: {amount1}, Amount2: {amount2}")
                    print(f"      ⚖️ Opposite signs: {opposite_signs}")
                except Exception as e:
                    print(f"      ❌ Error parsing amounts: {e}")
                    continue
                
                # Check dates
                date1 = cand1.get('Date')
                date2 = cand2.get('Date')
                print(f"      📅 Date1: {date1}, Date2: {date2}")
                
                # Check for exchange information
                exchange_amount = cand1.get('Exchange To Amount') or cand2.get('Exchange To Amount')
                exchange_currency = cand1.get('Exchange To') or cand2.get('Exchange To')
                print(f"      💱 Exchange amount: {exchange_amount}")
                print(f"      💱 Exchange currency: {exchange_currency}")
                
                # Manual matching logic
                if different_banks and opposite_signs:
                    if exchange_amount and exchange_currency:
                        try:
                            exchange_amt = float(str(exchange_amount).replace(',', ''))
                            if abs(amount2) == exchange_amt or abs(amount1) == exchange_amt:
                                print(f"      🎯 POTENTIAL MATCH FOUND!")
                                print(f"         Exchange amount {exchange_amt} matches transaction amount")
                            else:
                                print(f"      ❌ Exchange amount {exchange_amt} doesn't match transaction amounts")
                        except:
                            print(f"      ❌ Could not parse exchange amount")
                    else:
                        print(f"      ❌ No exchange information available")
                else:
                    print(f"      ❌ Basic matching criteria not met")
    else:
        print(f"   ❌ Need at least 2 candidates, found {len(transfer_candidates)}")
    
    # Step 5: Run actual detector
    print("\n5️⃣ RUNNING ACTUAL DETECTOR:")
    print("-" * 40)
    
    try:
        results = detector.detect_transfers(mock_csv_data)
        print(f"   ✅ Detection completed")
        print(f"   📊 Transfer pairs found: {len(results['transfers'])}")
        print(f"   💱 Currency conversions: {results['summary']['currency_conversions']}")
        print(f"   🔄 Cross-bank transfers: {results['summary']['other_transfers']}")
        
        if results['transfers']:
            print("\n   📋 DETECTED TRANSFERS:")
            for i, transfer in enumerate(results['transfers']):
                print(f"      Transfer {i}:")
                print(f"        📤 Outgoing: {transfer.get('outgoing', {}).get('Description')} ({transfer.get('amount')})")
                print(f"        📥 Incoming: {transfer.get('incoming', {}).get('Description')} ({transfer.get('exchange_amount')})")
                print(f"        🎯 Confidence: {transfer.get('confidence')}")
                print(f"        🔧 Type: {transfer.get('transfer_type')}")
        else:
            print("   ❌ No transfers detected")
            
    except Exception as e:
        print(f"   ❌ Error in detection: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🐛 DEBUG COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    debug_currency_transfer()
