#!/usr/bin/env python3
"""
Comprehensive integration test for the enhanced transfer detection system
Tests realistic Wise→NayaPay transfer scenarios and edge cases
"""

import sys
import os

# Add backend to path
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from transfer_detector_enhanced import EnhancedTransferDetector

def test_realistic_wise_nayapay_scenario():
    """Test with realistic data that matches your actual transfer pattern"""
    
    print("🧪 REALISTIC WISE→NAYAPAY TRANSFER TEST")
    print("=" * 50)
    
    # Wise CSV data (outgoing transfer)
    wise_data = {
        'file_name': 'wise_statement_june_2025.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '-108.99',
                'Description': 'Sent money to Ammar Qazi',
                'Exchange To Amount': '30000',
                'Currency': 'USD'
            },
            {
                'Date': '2025-06-02',
                'Amount': '-75.00',
                'Description': 'Converted 75.00 USD to 68.30 EUR',
                'Exchange To Amount': '68.30',
                'Currency': 'USD'
            }
        ],
        'template_config': {'bank_name': 'Wise'}
    }
    
    # NayaPay CSV data (incoming transfer)
    nayapay_data = {
        'file_name': 'nayapay_statement_june_2025.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '30000',
                'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2050|Transaction ID 192351'
            },
            {
                'Date': '2025-06-04',
                'Amount': '-150',
                'Description': 'ATM withdrawal at Standard Chartered Bank'
            }
        ],
        'template_config': {'bank_name': 'NayaPay'}
    }
    
    # Wise EUR account
    wise_eur_data = {
        'file_name': 'wise_eur_account_june_2025.csv',
        'data': [
            {
                'Date': '2025-06-02',
                'Amount': '68.30',
                'Description': 'Converted USD from USD balance',
                'Currency': 'EUR'
            }
        ],
        'template_config': {'bank_name': 'Wise EUR'}
    }
    
    # Run detection
    detector = EnhancedTransferDetector(user_name="Ammar Qazi", date_tolerance_hours=24)
    csv_data_list = [wise_data, nayapay_data, wise_eur_data]
    results = detector.detect_transfers(csv_data_list)
    
    print("📊 DETECTION RESULTS:")
    print(f"   Total Transactions: {results['summary']['total_transactions']}")
    print(f"   Transfer Pairs Found: {results['summary']['transfer_pairs_found']}")
    print(f"   Cross-Bank Transfers: {results['detection_strategies']['cross_bank_transfers']}")
    print(f"   Currency Conversions: {results['detection_strategies']['currency_conversions']}")
    
    # Analyze results
    wise_to_nayapay_found = False
    usd_to_eur_found = False
    
    print("\n🔍 DETECTED TRANSFERS:")
    for i, pair in enumerate(results['transfers'], 1):
        print(f"\n{i}. {pair['transfer_type'].upper()} Transfer:")
        print(f"   📤 OUT: {pair['outgoing']['Description']} ({pair['outgoing']['Amount']})")
        print(f"   📥 IN:  {pair['incoming']['Description']} ({pair['incoming']['Amount']})")
        
        if pair['transfer_type'] == 'cross_bank':
            if pair['from_bank'] == 'wise' and pair['to_bank'] == 'nayapay':
                wise_to_nayapay_found = True
                print(f"   ✅ WISE→NAYAPAY DETECTED!")
        elif pair['transfer_type'] == 'currency_conversion':
            if 'usd' in pair['outgoing']['Description'].lower() and 'eur' in pair['outgoing']['Description'].lower():
                usd_to_eur_found = True
                print(f"   ✅ USD→EUR CONVERSION DETECTED!")
    
    # Apply categorization
    transfer_matches = detector.apply_transfer_categorization(csv_data_list, results['transfers'])
    
    print(f"\n🎯 SUMMARY:")
    print(f"✅ Wise→NayaPay Transfer: {'DETECTED' if wise_to_nayapay_found else 'MISSED'}")
    print(f"✅ USD→EUR Conversion: {'DETECTED' if usd_to_eur_found else 'MISSED'}")
    print(f"✅ Balance Corrections Created: {len(transfer_matches)}")
    
    return results, transfer_matches

def test_edge_cases():
    """Test edge cases - similar amounts but different purposes"""
    
    print(f"\n🧪 TESTING EDGE CASES")
    print("=" * 30)
    
    edge_case_data = [
        {
            'file_name': 'wise_edge_test.csv',
            'data': [
                {
                    'Date': '2025-06-04',
                    'Amount': '-100.00',
                    'Description': 'Sent money to Ammar Qazi',  # Real transfer
                    'Exchange To Amount': '28000'
                },
                {
                    'Date': '2025-06-04', 
                    'Amount': '-100.00',
                    'Description': 'Payment to Amazon',  # Not a transfer
                    'Exchange To Amount': '0'
                }
            ],
            'template_config': {'bank_name': 'Wise'}
        },
        {
            'file_name': 'nayapay_edge_test.csv',
            'data': [
                {
                    'Date': '2025-06-04',
                    'Amount': '28000',
                    'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2050'
                },
                {
                    'Date': '2025-06-04',
                    'Amount': '28000', 
                    'Description': 'Salary payment from Company XYZ'  # Not a transfer
                }
            ],
            'template_config': {'bank_name': 'NayaPay'}
        }
    ]
    
    detector = EnhancedTransferDetector(user_name="Ammar Qazi")
    edge_results = detector.detect_transfers(edge_case_data)
    
    print(f"📊 Edge Case Results:")
    print(f"   Transfers Found: {len(edge_results['transfers'])}")
    print(f"   Expected: 1 (only the real Wise→NayaPay transfer)")
    
    # Verify only correct transfer detected
    correct_detection = False
    if len(edge_results['transfers']) == 1:
        pair = edge_results['transfers'][0]
        if ('sent money' in pair['outgoing']['Description'].lower() and 
            'incoming fund transfer' in pair['incoming']['Description'].lower()):
            correct_detection = True
            print(f"   ✅ CORRECT: Only real transfer detected")
        else:
            print(f"   ❌ WRONG: Incorrect transfer detected")
    else:
        print(f"   ❌ WRONG: {len(edge_results['transfers'])} transfers detected instead of 1")
    
    return correct_detection

def test_multiple_currencies():
    """Test handling of multiple currencies and exchange rates"""
    
    print(f"\n🌍 TESTING MULTIPLE CURRENCIES")
    print("=" * 35)
    
    multi_currency_data = [
        {
            'file_name': 'wise_multi_currency.csv',
            'data': [
                {
                    'Date': '2025-06-04',
                    'Amount': '-200.00',  # USD
                    'Description': 'Sent money to Ammar Qazi', 
                    'Exchange To Amount': '56000',  # PKR
                    'Currency': 'USD'
                },
                {
                    'Date': '2025-06-04',
                    'Amount': '-150.00',  # EUR
                    'Description': 'Sent money to Ammar Qazi',
                    'Exchange To Amount': '42000',  # PKR 
                    'Currency': 'EUR'
                }
            ],
            'template_config': {'bank_name': 'Wise'}
        },
        {
            'file_name': 'nayapay_multi_currency.csv', 
            'data': [
                {
                    'Date': '2025-06-04',
                    'Amount': '56000',  # PKR from USD
                    'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2050'
                },
                {
                    'Date': '2025-06-04',
                    'Amount': '42000',  # PKR from EUR
                    'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2051'
                }
            ],
            'template_config': {'bank_name': 'NayaPay'}
        }
    ]
    
    detector = EnhancedTransferDetector(user_name="Ammar Qazi")
    multi_results = detector.detect_transfers(multi_currency_data)
    
    print(f"📊 Multi-Currency Results:")
    print(f"   Transfers Found: {len(multi_results['transfers'])}")
    print(f"   Expected: 2 (USD→PKR and EUR→PKR)")
    
    usd_transfer = any(pair for pair in multi_results['transfers'] 
                      if '200.00' in str(pair['outgoing']['Amount']) and '56000' in str(pair['incoming']['Amount']))
    eur_transfer = any(pair for pair in multi_results['transfers']
                      if '150.00' in str(pair['outgoing']['Amount']) and '42000' in str(pair['incoming']['Amount']))
    
    print(f"   ✅ USD→PKR Transfer: {'DETECTED' if usd_transfer else 'MISSED'}")
    print(f"   ✅ EUR→PKR Transfer: {'DETECTED' if eur_transfer else 'MISSED'}")
    
    return len(multi_results['transfers']) == 2 and usd_transfer and eur_transfer

def run_comprehensive_test():
    """Run all tests and provide final assessment"""
    
    print("🚀 COMPREHENSIVE ENHANCED TRANSFER DETECTION TEST")
    print("=" * 55)
    
    try:
        # Test 1: Realistic scenario
        print("\n1️⃣ TESTING REALISTIC SCENARIO...")
        results, matches = test_realistic_wise_nayapay_scenario()
        realistic_success = len(results['transfers']) >= 2
        
        # Test 2: Edge cases 
        print("\n2️⃣ TESTING EDGE CASES...")
        edge_success = test_edge_cases()
        
        # Test 3: Multiple currencies
        print("\n3️⃣ TESTING MULTIPLE CURRENCIES...")
        multi_success = test_multiple_currencies()
        
        # Final assessment
        print(f"\n🎯 FINAL TEST RESULTS")
        print("=" * 25)
        print(f"✅ Realistic Scenario: {'PASS' if realistic_success else 'FAIL'}")
        print(f"✅ Edge Case Handling: {'PASS' if edge_success else 'FAIL'}")
        print(f"✅ Multi-Currency Support: {'PASS' if multi_success else 'FAIL'}")
        
        overall_success = realistic_success and edge_success and multi_success
        
        if overall_success:
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"   Enhanced Transfer Detection is ready for production use.")
            print(f"   Your Wise→NayaPay transfers will be detected automatically.")
        else:
            print(f"\n⚠️ Some tests failed. Review results above.")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        import traceback
        print(f"📚 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)
