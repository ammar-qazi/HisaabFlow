#!/usr/bin/env python3
"""
Simple test to verify the enhanced transfer detection is working with debugging
"""

import sys
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

# Import everything we need to simulate the backend process
from transfer_detector_enhanced import EnhancedTransferDetector
from enhanced_csv_parser import EnhancedCSVParser

def simulate_backend_process():
    """Simulate exactly what happens in the backend when you upload your CSVs"""
    
    print("🚀 SIMULATING FULL BACKEND PROCESS")
    print("=" * 50)
    
    # Step 1: Your CSV data after parsing but before transformation
    print("📊 Step 1: Raw CSV Data (after parsing)")
    
    wise_csv_data = {
        'file_name': 'wise_transactions.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '-181.1',
                'Description': 'Sent money to Ammar Qazi',
                'Exchange To Amount': '50000'
            },
            {
                'Date': '2025-06-04', 
                'Amount': '-109',
                'Description': 'Sent money to Ammar Qazi',
                'Exchange To Amount': '30000'
            }
        ],
        'template_config': {
            'bank_name': 'Wise',
            'column_mapping': {
                'Date': 'Date',
                'Amount': 'Amount',
                'Description': 'Title'  # This becomes Title in Cashew format
            },
            'categorization_rules': [
                {
                    'conditions': [{'field': 'Description', 'operator': 'contains', 'value': 'Sent money'}],
                    'category': 'Expense',  # Template rule that's overriding
                    'priority': 1
                }
            ]
        }
    }
    
    nayapay_csv_data = {
        'file_name': 'nayapay_transactions.csv', 
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '50000',
                'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2050'
            },
            {
                'Date': '2025-06-04',
                'Amount': '30000', 
                'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2051'
            }
        ],
        'template_config': {
            'bank_name': 'NayaPay',
            'column_mapping': {
                'Date': 'Date',
                'Amount': 'Amount',
                'Description': 'Title'
            }
        }
    }
    
    csv_data_list = [wise_csv_data, nayapay_csv_data]
    
    # Step 2: Transfer Detection (on raw data)
    print("\n🔍 Step 2: Transfer Detection")
    detector = EnhancedTransferDetector(user_name="Ammar Qazi")
    transfer_analysis = detector.detect_transfers(csv_data_list)
    
    print(f"   Transfers found: {len(transfer_analysis['transfers'])}")
    for i, pair in enumerate(transfer_analysis['transfers'], 1):
        print(f"   {i}. {pair['outgoing']['Description']} → {pair['incoming']['Description']}")
    
    # Step 3: Template Transformation
    print("\n🏷️  Step 3: Template Transformation")
    parser = EnhancedCSVParser()
    all_transformed_data = []
    
    for csv_data in csv_data_list:
        template_config = csv_data.get('template_config', {})
        transformed = parser.transform_to_cashew(
            csv_data['data'],
            template_config.get('column_mapping', {}),
            template_config.get('bank_name', ''),
            template_config.get('categorization_rules', []),
            template_config.get('default_category_rules'),
            template_config.get('account_mapping')
        )
        all_transformed_data.extend(transformed)
        
        print(f"   {csv_data['file_name']}: {len(transformed)} transactions")
        for trans in transformed[:2]:  # Show first 2
            print(f"     - Title: {trans.get('Title', 'N/A')}")
            print(f"       Category: {trans.get('Category', 'N/A')} (from template)")
    
    # Step 4: Apply Transfer Categorization (should override template)
    print("\n🔄 Step 4: Apply Transfer Categorization")
    
    if transfer_analysis['transfers']:
        transfer_matches = detector.apply_transfer_categorization(
            csv_data_list, 
            transfer_analysis['transfers']
        )
        
        print(f"   Transfer matches to apply: {len(transfer_matches)}")
        
        balance_corrections_applied = 0
        
        for i, transaction in enumerate(all_transformed_data):
            for match in transfer_matches:
                # Enhanced matching
                amount_match = abs(float(transaction.get('Amount', '0')) - float(match['amount'])) < 0.01
                date_match = transaction.get('Date', '').startswith(match['date'])
                
                if amount_match and date_match:
                    # Use Title field for matching (as that's what Cashew format uses)
                    trans_title = str(transaction.get('Title', '')).lower()
                    match_desc = str(match['description']).lower()
                    
                    # Simple matching for demo
                    if 'sent money' in match_desc and 'sent money' in trans_title:
                        print(f"   ✅ MATCH: {trans_title} ← Template: {transaction['Category']}")
                        print(f"   🔄 OVERRIDE: {transaction['Category']} → {match['category']}")
                        
                        transaction['Category'] = match['category']
                        transaction['Note'] = match['note']
                        balance_corrections_applied += 1
                        break
                    elif 'incoming fund transfer' in match_desc and 'incoming fund transfer' in trans_title:
                        print(f"   ✅ MATCH: {trans_title}")
                        print(f"   🔄 OVERRIDE: {transaction['Category']} → {match['category']}")
                        
                        transaction['Category'] = match['category']
                        transaction['Note'] = match['note']
                        balance_corrections_applied += 1
                        break
                    else:
                        print(f"   ⚠️  NO MATCH: '{trans_title}' vs '{match_desc}'")
        
        print(f"\n   ✅ Applied {balance_corrections_applied} transfer categorizations")
    
    # Step 5: Final Results
    print("\n📋 Step 5: Final Results")
    
    balance_corrections = [t for t in all_transformed_data if t.get('Category') == 'Balance Correction']
    expenses = [t for t in all_transformed_data if t.get('Category') == 'Expense']
    
    print(f"   Balance Corrections: {len(balance_corrections)}")
    print(f"   Expenses: {len(expenses)}")
    
    print("\n📊 Detailed Final Results:")
    for i, transaction in enumerate(all_transformed_data, 1):
        print(f"   {i}. {transaction.get('Title', 'N/A')[:40]}...")
        print(f"      Amount: {transaction.get('Amount', 'N/A')}")
        print(f"      Category: {transaction.get('Category', 'N/A')}")
        if transaction.get('Note'):
            print(f"      Note: {transaction.get('Note', '')}")
    
    return all_transformed_data, balance_corrections

if __name__ == "__main__":
    final_data, balance_corrections = simulate_backend_process()
    
    print("\n" + "="*60)
    print("🎯 SIMULATION RESULTS")
    print("="*60)
    
    if len(balance_corrections) > 0:
        print(f"✅ SUCCESS: {len(balance_corrections)} transfer(s) correctly categorized as 'Balance Correction'")
        print("   The enhanced transfer detection is working!")
    else:
        print("❌ ISSUE: No transfers were categorized as 'Balance Correction'")
        print("   The template categorization is winning over transfer detection")
    
    print("\n🔧 NEXT STEPS:")
    print("   1. Test this with your actual data")
    print("   2. Check the backend logs when you run the real process")
    print("   3. Verify both Wise and NayaPay CSVs are being uploaded")
