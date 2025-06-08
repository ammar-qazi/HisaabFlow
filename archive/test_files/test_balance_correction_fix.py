#!/usr/bin/env python3

"""
Test script to verify the balance correction fix
"""

import sys
import os
sys.path.append('backend')

from transfer_detector import TransferDetector
from enhanced_csv_parser import EnhancedCSVParser

def test_balance_correction_fix():
    """Test the balance correction mapping fix"""
    
    print("🧪 Testing Balance Correction Fix")
    print("=" * 50)
    
    # Create sample data that mimics the issue (using real TransferWise data format)
    csv_data_list = [
        {
            'file_name': 'statement_USD.csv',
            'data': [
                {
                    'Date': '2025-05-26',
                    'Amount': '-22.83',
                    'Description': 'Converted 22.83 USD to 20.00 EUR for EUR balance',
                    'TYPE': 'Balance Correction',
                    'Exchange To Amount': '20.00'  # Add this field that TransferWise uses
                },
                {
                    'Date': '2025-05-26',
                    'Amount': '-155.0', 
                    'Description': 'Revolut**0540* Dublin',
                    'TYPE': 'Expense'
                }
            ]
        },
        {
            'file_name': 'statement_EUR.csv', 
            'data': [
                {
                    'Date': '2025-05-26',
                    'Amount': '20.0',
                    'Description': 'Converted 22.83 USD from USD balance to 20.00 EUR',
                    'TYPE': 'Balance Correction'
                }
            ]
        }
    ]
    
    # Add required metadata and process for transfer detection
    for i, csv_data in enumerate(csv_data_list):
        for j, transaction in enumerate(csv_data['data']):
            transaction['_csv_index'] = i
            transaction['_transaction_index'] = j
            
            # Mark transfer candidates based on description patterns
            description = str(transaction.get('Description', '')).lower()
            if 'converted' in description:
                transaction['_is_transfer_candidate'] = True
                transaction['_transfer_pattern'] = r"converted\s+\w+"
    
    # Initialize transfer detector
    detector = TransferDetector()
    
    # Detect transfers
    print("🔍 Detecting transfers...")
    transfer_analysis = detector.detect_transfers(csv_data_list)
    
    print(f"✅ Found {len(transfer_analysis['transfers'])} transfer pairs")
    
    # Print detected transfers
    for pair in transfer_analysis['transfers']:
        print(f"📤 OUT: {pair['outgoing']['Description'][:50]}... Amount: {pair['outgoing']['Amount']}")
        print(f"📥 IN:  {pair['incoming']['Description'][:50]}... Amount: {pair['incoming']['Amount']}")
        print(f"   Confidence: {pair['confidence']*100:.0f}%")
        print()
    
    # Test new transfer categorization method
    print("🔄 Testing new transfer categorization method...")
    transfer_matches = detector.apply_transfer_categorization(csv_data_list, transfer_analysis['transfers'])
    
    print(f"✅ Generated {len(transfer_matches)} transfer matches")
    
    # Show transfer matches
    for match in transfer_matches:
        print(f"💰 Amount: {match['amount']}, Date: {match['date']}")
        print(f"📝 Description: {match['description'][:50]}...")
        print(f"🏷️  Category: {match['category']}, Type: {match['transfer_type']}")
        print()
    
    # Simulate transformed data (what would come from enhanced_csv_parser)
    print("🔄 Simulating transformed data application...")
    
    # This simulates the transformed data array that would be created
    all_transformed_data = [
        {
            'Date': '2025-05-26 00:00:00',
            'Amount': '-22.83',
            'Category': 'Expense',  # Initially categorized as expense
            'Title': 'Converted 22.83 USD to 20.00 EUR for EUR balance',
            'Note': 'Balance Correction',
            'Account': 'TransferWise'
        },
        {
            'Date': '2025-05-26 00:00:00', 
            'Amount': '-155.0',
            'Category': 'Expense',
            'Title': 'Revolut**0540* Dublin',
            'Note': 'Expense',
            'Account': 'EURO Wise'
        },
        {
            'Date': '2025-05-26 00:00:00',
            'Amount': '20.0',
            'Category': 'Income',  # Initially categorized as income
            'Title': 'Converted 22.83 USD from USD balance to 20.00 EUR',
            'Note': 'Balance Correction', 
            'Account': 'EURO Wise'
        }
    ]
    
    print("📊 Original transformed data:")
    for i, trans in enumerate(all_transformed_data):
        print(f"  {i}: {trans['Amount']:>8} | {trans['Category']:>12} | {trans['Title'][:40]}")
    print()
    
    # Apply the new balance correction logic
    print("🔧 Applying balance correction logic...")
    corrections_applied = 0
    
    for i, transaction in enumerate(all_transformed_data):
        for match in transfer_matches:
            # Match by amount and date
            amount_match = abs(float(transaction.get('Amount', '0')) - float(match['amount'])) < 0.01
            date_match = transaction.get('Date', '').startswith(match['date'])
            
            if amount_match and date_match:
                # Additional check for description similarity to avoid false matches
                trans_desc = str(transaction.get('Title', '')).lower()
                match_desc = str(match['description']).lower()
                
                # Check if descriptions contain similar key words (avoid very short words)
                desc_words_trans = [word for word in trans_desc.split() if len(word) > 3]
                desc_words_match = [word for word in match_desc.split() if len(word) > 3]
                
                desc_match = (len(desc_words_trans) == 0 or len(desc_words_match) == 0 or 
                            any(word in trans_desc for word in desc_words_match) or 
                            any(word in match_desc for word in desc_words_trans))
                
                if desc_match:
                    print(f"✅ Match found for transaction {i}:")
                    print(f"   Amount: {transaction['Amount']} ≈ {match['amount']}")
                    print(f"   Date: {transaction['Date']} starts with {match['date']}")
                    print(f"   Description similarity: {desc_match}")
                    
                    all_transformed_data[i]['Category'] = match['category']
                    all_transformed_data[i]['Note'] = match['note']
                    all_transformed_data[i]['_transfer_pair_id'] = match['pair_id']
                    all_transformed_data[i]['_transfer_type'] = match['transfer_type']
                    all_transformed_data[i]['_is_transfer'] = True
                    corrections_applied += 1
                    break
    
    print(f"\n🎉 Applied {corrections_applied} balance corrections")
    print("\n📊 Final transformed data:")
    for i, trans in enumerate(all_transformed_data):
        transfer_indicator = "🔄" if trans.get('_is_transfer') else "  "
        print(f"  {transfer_indicator} {i}: {trans['Amount']:>8} | {trans['Category']:>15} | {trans['Title'][:40]}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed successfully!")
    
    # Verify the fix worked
    balance_corrections = [t for t in all_transformed_data if t.get('Category') == 'Balance Correction']
    print(f"📈 Result: {len(balance_corrections)} transactions now marked as 'Balance Correction'")
    
    if len(balance_corrections) == len(transfer_analysis['transfers']) * 2:
        print("🎯 SUCCESS: Correct number of balance corrections applied!")
        return True
    else:
        print("❌ ISSUE: Mismatch in balance correction count")
        return False

if __name__ == "__main__":
    try:
        success = test_balance_correction_fix()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
