#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from transfer_detector_enhanced_ammar import TransferDetector
import pandas as pd
from datetime import datetime

def analyze_real_data():
    """Analyze the real CSV data to understand matching issues"""
    
    print("🔍 ANALYZING REAL CSV DATA")
    print("=" * 50)
    
    # Read the real CSV files
    print("📁 Reading NayaPay CSV...")
    nayapay_df = pd.read_csv('nayapay_feb.csv', skiprows=12)  # Skip header rows
    print(f"   Rows: {len(nayapay_df)}")
    print(f"   Columns: {list(nayapay_df.columns)}")
    
    print("\n📁 Reading Wise CSV...")
    wise_df = pd.read_csv('wise_USD.csv')
    print(f"   Rows: {len(wise_df)}")
    print(f"   Columns: {list(wise_df.columns)}")
    
    # Analyze Ammar-related transactions
    print("\n🔍 ANALYZING AMMAR-RELATED TRANSACTIONS")
    
    print("\n📥 NayaPay incoming transfers from Ammar:")
    ammar_incoming = nayapay_df[nayapay_df['DESCRIPTION'].str.contains('Ammar Qazi', case=False, na=False)]
    for idx, row in ammar_incoming.iterrows():
        print(f"   {row['TIMESTAMP']}: {row['AMOUNT']} - {row['DESCRIPTION'][:60]}...")
    
    print("\n📤 Wise outgoing transfers to Ammar:")
    ammar_outgoing = wise_df[wise_df['Description'].str.contains('Sent money to Ammar Qazi', case=False, na=False)]
    for idx, row in ammar_outgoing.iterrows():
        exchange_amount = row['Exchange To Amount'] if pd.notna(row['Exchange To Amount']) else 'N/A'
        print(f"   {row['Date']}: ${row['Amount']} → {exchange_amount} PKR - {row['Description']}")
    
    # Test the current detector with real data
    print("\n🧪 TESTING CURRENT DETECTOR WITH REAL DATA")
    
    # Convert to the format expected by the detector
    nayapay_data = []
    for idx, row in nayapay_df.iterrows():
        if pd.notna(row['TIMESTAMP']) and pd.notna(row['AMOUNT']):
            nayapay_data.append({
                'Date': row['TIMESTAMP'],
                'Amount': str(row['AMOUNT']).replace(',', ''),
                'Description': str(row['DESCRIPTION']),
                'Category': str(row['TYPE'])
            })
    
    wise_data = []
    for idx, row in wise_df.iterrows():
        if pd.notna(row['Date']) and pd.notna(row['Amount']):
            wise_record = {
                'Date': row['Date'],
                'Amount': str(row['Amount']),
                'Description': str(row['Description']),
                'Category': 'Transfer'  # Default category
            }
            
            # Add exchange information if available
            if pd.notna(row['Exchange To Amount']):
                wise_record['Exchange To Amount'] = str(row['Exchange To Amount'])
            if pd.notna(row['Exchange To']):
                wise_record['Exchange To'] = str(row['Exchange To'])
                
            wise_data.append(wise_record)
    
    csv_data_list = [
        {
            'file_name': 'nayapay_feb.csv',
            'data': nayapay_data,
            'template_config': {}
        },
        {
            'file_name': 'wise_USD.csv',
            'data': wise_data,
            'template_config': {}
        }
    ]
    
    print(f"\n📊 Converted data:")
    print(f"   NayaPay transactions: {len(nayapay_data)}")
    print(f"   Wise transactions: {len(wise_data)}")
    
    # Test with detector
    detector = TransferDetector(user_name="Ammar Qazi", date_tolerance_hours=72)  # Increased tolerance
    result = detector.detect_transfers(csv_data_list)
    
    print(f"\n📋 DETECTION RESULTS:")
    print(f"   Transfer pairs found: {len(result['transfers'])}")
    print(f"   Potential transfers: {len(result['potential_transfers'])}")
    
    if result['transfers']:
        print("\n✅ DETECTED TRANSFERS:")
        for i, transfer in enumerate(result['transfers']):
            print(f"\n   Transfer {i+1}:")
            print(f"      📤 Outgoing: {transfer['outgoing']['Description']}")
            print(f"      📥 Incoming: {transfer['incoming']['Description']}")
            print(f"      💰 Amount: {transfer['amount']}")
            print(f"      🎯 Strategy: {transfer.get('match_strategy', 'unknown')}")
            print(f"      📅 Outgoing Date: {transfer['outgoing']['Date']}")
            print(f"      📅 Incoming Date: {transfer['incoming']['Date']}")
    else:
        print("\n❌ NO TRANSFERS DETECTED")
        
        # Debug specific pairs manually
        print("\n🔍 MANUAL ANALYSIS OF POTENTIAL PAIRS:")
        
        # Check specific known pairs
        test_pairs = [
            ("09-03-25", "03 Feb 2025", 181.53, 50000),  # Should match
            ("02-14-25", "14 Feb 2025", 108.99, 30000),  # Should match
        ]
        
        for wise_date, nayapay_date, wise_amount, expected_pkr in test_pairs:
            print(f"\n   Testing pair: {wise_date} / {nayapay_date}")
            
            # Find wise transaction
            wise_tx = None
            for tx in wise_data:
                if wise_date in tx['Date'] and abs(float(tx['Amount'])) == wise_amount:
                    wise_tx = tx
                    break
            
            # Find nayapay transaction  
            nayapay_tx = None
            for tx in nayapay_data:
                if nayapay_date in tx['Date'] and expected_pkr in float(tx['Amount'].replace(',', '')):
                    nayapay_tx = tx
                    break
            
            if wise_tx and nayapay_tx:
                print(f"      ✅ Both transactions found")
                print(f"      📤 Wise: {wise_tx['Description'][:50]}...")
                print(f"      📥 NayaPay: {nayapay_tx['Description'][:50]}...")
                
                # Test Ammar detection manually
                is_ammar = detector._is_ammar_cross_bank_transfer({
                    **wise_tx,
                    '_bank_type': 'wise'
                }, {
                    **nayapay_tx, 
                    '_bank_type': 'nayapay'
                })
                print(f"      🎯 Is Ammar transfer: {is_ammar}")
                
                # Test date tolerance
                wise_parsed = detector._parse_date(wise_tx['Date'])
                nayapay_parsed = detector._parse_date(nayapay_tx['Date'])
                date_ok = detector._dates_within_tolerance(wise_parsed, nayapay_parsed)
                print(f"      📅 Date tolerance OK: {date_ok}")
                print(f"         Wise parsed: {wise_parsed}")
                print(f"         NayaPay parsed: {nayapay_parsed}")
                
            else:
                print(f"      ❌ Missing transactions")
                print(f"         Wise found: {wise_tx is not None}")
                print(f"         NayaPay found: {nayapay_tx is not None}")

if __name__ == "__main__":
    analyze_real_data()
