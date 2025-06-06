#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from transfer_detector_enhanced_ammar import TransferDetector

def test_enhanced_matching():
    """Test the enhanced transfer detection with real-world variations"""
    
    print("🔧 TESTING ENHANCED AMMAR TRANSFER DETECTION")
    print("=" * 60)
    
    # Test cases covering various scenarios that might occur in real data
    test_cases = [
        {
            'name': '🎯 Perfect Exchange Amount Match',
            'data': [
                {
                    'file_name': 'nayapay_feb.csv',
                    'data': [
                        {
                            'Date': '2025-02-03',
                            'Amount': '50000.0',
                            'Description': 'Transfer from Ammar Qazi Bank Alfalah-2050',
                            'Category': 'Transfer'
                        }
                    ]
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
                        }
                    ]
                }
            ],
            'expected_matches': 1
        },
        {
            'name': '🔧 Name Variation Match (Ammar only)',
            'data': [
                {
                    'file_name': 'nayapay_feb.csv',
                    'data': [
                        {
                            'Date': '2025-02-03',
                            'Amount': '23000.0',
                            'Description': 'Incoming fund transfer from Ammar',
                            'Category': 'Transfer'
                        }
                    ]
                },
                {
                    'file_name': 'wise_USD.csv',
                    'data': [
                        {
                            'Date': '2025-02-03',
                            'Amount': '-150.0',
                            'Description': 'Sent money to Ammar Qazi',
                            'Category': 'Transfer',
                            'Exchange To Amount': '23000.0',
                            'Exchange To': 'PKR'
                        }
                    ]
                }
            ],
            'expected_matches': 1
        },
        {
            'name': '💰 Flexible Amount Match (with fees)',
            'data': [
                {
                    'file_name': 'nayapay_feb.csv',
                    'data': [
                        {
                            'Date': '2025-02-03',
                            'Amount': '19500.0',  # 5% fee difference
                            'Description': 'Transfer from Ammar Qazi',
                            'Category': 'Transfer'
                        }
                    ]
                },
                {
                    'file_name': 'wise_USD.csv',
                    'data': [
                        {
                            'Date': '2025-02-03',
                            'Amount': '-120.0',
                            'Description': 'Sent money to Ammar Qazi',
                            'Category': 'Transfer',
                            'Exchange To Amount': '20000.0',  # Different from received amount due to fees
                            'Exchange To': 'PKR'
                        }
                    ]
                }
            ],
            'expected_matches': 1
        },
        {
            'name': '❌ Non-Ammar Transfer (should not match)',
            'data': [
                {
                    'file_name': 'nayapay_feb.csv',
                    'data': [
                        {
                            'Date': '2025-02-03',
                            'Amount': '15000.0',
                            'Description': 'Transfer from Someone Else',
                            'Category': 'Transfer'
                        }
                    ]
                },
                {
                    'file_name': 'wise_USD.csv',
                    'data': [
                        {
                            'Date': '2025-02-03',
                            'Amount': '-100.0',
                            'Description': 'Sent money to Ammar Qazi',
                            'Category': 'Transfer',
                            'Exchange To Amount': '15000.0',
                            'Exchange To': 'PKR'
                        }
                    ]
                }
            ],
            'expected_matches': 0
        }
    ]
    
    detector = TransferDetector(user_name="Ammar Qazi", date_tolerance_hours=24)
    
    total_passed = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases):
        print(f"\n{'='*60}")
        print(f"TEST {i+1}/{total_tests}: {test_case['name']}")
        print(f"{'='*60}")
        
        try:
            result = detector.detect_transfers(test_case['data'])
            
            actual_matches = len(result['transfers'])
            expected_matches = test_case['expected_matches']
            
            if actual_matches == expected_matches:
                print(f"✅ PASSED: Found {actual_matches} matches (expected {expected_matches})")
                total_passed += 1
                
                if actual_matches > 0:
                    for j, transfer in enumerate(result['transfers']):
                        print(f"\n   Transfer {j+1}:")
                        print(f"      📤 Outgoing: {transfer['outgoing']['Description']}")
                        print(f"      📥 Incoming: {transfer['incoming']['Description']}")
                        print(f"      💰 Amount: {transfer['amount']}")
                        print(f"      🎯 Strategy: {transfer.get('match_strategy', 'unknown')}")
                        print(f"      🎯 Confidence: {transfer['confidence']:.2f}")
                        
                        if transfer.get('exchange_amount'):
                            print(f"      💱 Exchange Amount: {transfer['exchange_amount']}")
            else:
                print(f"❌ FAILED: Found {actual_matches} matches (expected {expected_matches})")
                
        except Exception as e:
            print(f"💥 ERROR: {str(e)}")
    
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY: {total_passed}/{total_tests} tests passed")
    print(f"{'='*60}")
    
    if total_passed == total_tests:
        print("🎉 All tests passed! Enhanced Ammar transfer detection is working correctly.")
    else:
        print("⚠️ Some tests failed. Review the output above for details.")

if __name__ == "__main__":
    test_enhanced_matching()
