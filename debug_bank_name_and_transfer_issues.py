#!/usr/bin/env python3
"""
🐛 DEBUG: Bank Name Consistency & Transfer Detection Issues

This script reproduces and fixes:
1. Bank name inconsistency (Wise vs Transferwise)
2. Transfer detection failures for currency conversions
"""
import json
import pandas as pd
from transformation.universal_transformer import UniversalTransformer
from backend.transfer_detector import TransferDetector

def test_bank_name_consistency():
    """Test 1: Bank Name Consistency Bug"""
    print("🧪 TEST 1: BANK NAME CONSISTENCY")
    print("=" * 50)
    
    # Initialize transformer
    transformer = UniversalTransformer()
    
    # Test data simulating Wise file detection
    sample_data = [
        {
            'Date': '2025-01-15',
            'Amount': -3000.0,
            'Description': 'Card transaction of 3,000.00 HUF issued by Lidl Budapest Hungary',
            'Currency': 'HUF'
        }
    ]
    
    # Column mapping from Wise template
    column_mapping = {
        'Date': 'Date',
        'Amount': 'Amount', 
        'Title': 'Description',
        'Account': 'Currency'
    }
    
    # Test with different bank names
    test_cases = [
        ("Wise", "Frontend detects as 'Wise'"),
        ("Transferwise", "Rules stored as 'transferwise'"),
        ("transferwise", "Lowercase rule key")
    ]
    
    for bank_name, description in test_cases:
        print(f"\n🧪 Testing bank_name: '{bank_name}' ({description})")
        
        result = transformer.transform_to_cashew(
            data=sample_data,
            column_mapping=column_mapping,
            bank_name=bank_name,
            bank_rules_settings={'enableTransferwiseRules': True, 'enableUniversalRules': True}
        )
        
        print(f"   📋 Result: {len(result)} transactions")
        if result:
            print(f"   📝 Title: '{result[0]['Title']}'")
            print(f"   📂 Category: '{result[0]['Category']}'")
            
            # Check if title was cleaned (should show "Lidl" instead of full description)
            is_cleaned = "Lidl" in result[0]['Title'] and len(result[0]['Title']) < 20
            print(f"   🧹 Description cleaned: {'✅' if is_cleaned else '❌'}")


def test_transfer_detection():
    """Test 2: Transfer Detection for Currency Conversions"""
    print("\n\n🧪 TEST 2: TRANSFER DETECTION")
    print("=" * 50)
    
    # Load actual sample data
    try:
        # Load sample transferwise data
        wise_df = pd.read_csv('transferwise_sample.csv')
        print(f"📁 Loaded transferwise_sample.csv: {len(wise_df)} rows")
        print(f"📋 Columns: {list(wise_df.columns)}")
        
        # Show sample data
        print("\n📊 Sample transactions:")
        for idx, row in wise_df.head(5).iterrows():
            print(f"   Row {idx}: Date={row.get('Date', 'N/A')}, Amount={row.get('Amount', 'N/A')}")
            print(f"      Description: {str(row.get('Description', 'N/A'))[:60]}...")
        
        # Convert to list of dicts for transfer detector
        transactions = wise_df.to_dict('records')
        
        # Create CSV data structure expected by transfer detector
        csv_data_list = [
            {
                'file_name': 'transferwise_sample.csv',
                'data': transactions,
                'headers': list(wise_df.columns),
                'template_config': {
                    'bank_name': 'Transferwise'
                }
            }
        ]
        
        # Test transfer detection
        detector = TransferDetector(user_name="Ammar Qazi", date_tolerance_hours=24)
        transfer_results = detector.detect_transfers(csv_data_list)
        
        print(f"\n📊 Transfer Detection Results:")
        print(f"   ✅ Transfer pairs found: {transfer_results['summary']['transfer_pairs_found']}")
        print(f"   💭 Potential transfers: {transfer_results['summary']['potential_transfers']}")
        print(f"   ⚠️  Conflicts: {transfer_results['summary']['conflicts']}")
        
        # Look for conversion patterns specifically
        conversions = []
        for transaction in transactions:
            desc = str(transaction.get('Description', '')).lower()
            if 'converted' in desc and ('usd' in desc or 'huf' in desc):
                conversions.append(transaction)
        
        print(f"\n🔄 Currency conversion transactions found: {len(conversions)}")
        for i, conv in enumerate(conversions[:3]):
            print(f"   Conv {i+1}: {conv.get('Amount', 'N/A')} | {str(conv.get('Description', ''))[:60]}...")
            
    except FileNotFoundError:
        print("❌ transferwise_sample.csv not found, creating synthetic test data")
        
        # Create synthetic currency conversion data
        synthetic_data = [
            {
                'Date': '2025-01-15',
                'Amount': -565.24,
                'Description': 'Converted 565.24 USD to 200,000.00 HUF',
                'Currency': 'USD',
                'Exchange To Amount': 200000.00
            },
            {
                'Date': '2025-01-15', 
                'Amount': 200000.00,
                'Description': 'Converted 565.24 USD to 200,000.00 HUF',
                'Currency': 'HUF',
                'Exchange From Amount': 565.24
            }
        ]
        
        csv_data_list = [
            {
                'file_name': 'wise_usd.csv',
                'data': [synthetic_data[0]],
                'headers': ['Date', 'Amount', 'Description', 'Currency', 'Exchange To Amount'],
                'template_config': {'bank_name': 'Transferwise'}
            },
            {
                'file_name': 'wise_huf.csv', 
                'data': [synthetic_data[1]],
                'headers': ['Date', 'Amount', 'Description', 'Currency', 'Exchange From Amount'],
                'template_config': {'bank_name': 'Transferwise'}
            }
        ]
        
        detector = TransferDetector(user_name="Ammar Qazi", date_tolerance_hours=24)
        transfer_results = detector.detect_transfers(csv_data_list)
        
        print(f"📊 Synthetic Test Results:")
        print(f"   ✅ Transfer pairs found: {transfer_results['summary']['transfer_pairs_found']}")
        print(f"   💭 Potential transfers: {transfer_results['summary']['potential_transfers']}")


def analyze_rule_loading():
    """Test 3: Analyze Rule Loading Process"""
    print("\n\n🧪 TEST 3: RULE LOADING ANALYSIS")
    print("=" * 50)
    
    transformer = UniversalTransformer()
    
    # Check what bank overrides are loaded
    print("🏦 Available bank overrides:")
    for bank_key, rules in transformer.bank_overrides.items():
        rule_count = 0
        if 'overrides' in rules:
            for category, rule_list in rules['overrides'].items():
                if isinstance(rule_list, list):
                    rule_count += len(rule_list)
        
        print(f"   {bank_key}: {rule_count} rules")
    
    # Test rule loading for different bank names
    test_banks = ['wise', 'Wise', 'transferwise', 'Transferwise']
    
    for bank_name in test_banks:
        bank_key = bank_name.lower()
        rules = transformer._get_bank_override_rules(bank_key, {
            'enableTransferwiseRules': True,
            'enableUniversalRules': True
        })
        
        bank_rule_count = len(rules) - len(transformer.universal_rules)
        universal_rule_count = len(transformer.universal_rules)
        
        print(f"\n🔧 Bank name '{bank_name}' (key: '{bank_key}'):")
        print(f"   📋 Total rules: {len(rules)} (bank: {bank_rule_count}, universal: {universal_rule_count})")
        
        if bank_rule_count > 0:
            print("   ✅ Bank rules loaded successfully")
        else:
            print("   ❌ No bank rules loaded")


def propose_fixes():
    """Propose fixes for the identified issues"""
    print("\n\n🔧 PROPOSED FIXES")
    print("=" * 50)
    
    print("1. 🏦 BANK NAME CONSISTENCY FIX:")
    print("   ✅ Frontend detection should return 'Transferwise' (not 'Wise')")
    print("   ✅ Template bank_name should be 'Transferwise'")
    print("   ✅ Rules are already stored under 'transferwise' key")
    print("   📝 Update: MultiCSVApp.js detectBankFromFilename() function")
    
    print("\n2. 🔄 TRANSFER DETECTION FIX:")
    print("   🔍 Issue: Currency conversions aren't being detected as transfers")
    print("   🎯 Add pattern: r'converted\\s+[\\d,.]+\\s+\\w{3}\\s+to\\s+[\\d,.]+\\s+\\w{3}'")
    print("   🎯 Improve internal conversion detection")
    print("   📝 Update: transfer_detector.py transfer patterns")
    
    print("\n3. 📁 TEMPLATE ARCHITECTURE CLEANUP:")
    print("   ✅ Archive old templates ✓ (already done)")
    print("   ✅ Standardize bank names ✓ (already done)")
    print("   📝 Verify all templates use consistent bank names")


if __name__ == "__main__":
    print("🐛 DEBUGGING BANK STATEMENT PARSER ISSUES")
    print("=" * 60)
    
    test_bank_name_consistency()
    test_transfer_detection()
    analyze_rule_loading()
    propose_fixes()
    
    print("\n" + "=" * 60)
    print("🎯 DEBUGGING COMPLETE - See proposed fixes above")
