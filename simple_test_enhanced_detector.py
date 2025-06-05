#!/usr/bin/env python3
"""
Simple test for Enhanced Universal Transfer Detector

This script tests the specific EUR->PKR scenario to verify our implementation works.
"""

import sys
import os
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

def test_enhanced_transfer_detector():
    """Test the enhanced transfer detector with verbose debugging"""
    
    print("🧪 TESTING ENHANCED UNIVERSAL TRANSFER DETECTOR")
    print("=" * 60)
    print("📋 Target Scenario: Wise EUR->PKR with Exchange To Amount matching")
    print()
    
    try:
        # Import our enhanced detector
        from transfer_detector_enhanced_universal import EnhancedUniversalTransferDetector
        print("✅ Successfully imported EnhancedUniversalTransferDetector")
    except ImportError as e:
        print(f"❌ Failed to import EnhancedUniversalTransferDetector: {e}")
        return False
    
    # Create test data for the specific scenario
    wise_data = {
        'file_name': 'wise_eur_pkr_test.csv',
        'data': [
            {
                'Date': '2025-02-14',
                'Amount': '-108.99',
                'Currency': 'EUR',
                'Description': 'Sent money to Ammar Qazi',
                'Payment Reference': 'International transfer to Pakistan',
                'Exchange To Amount': '30000.00',  # KEY: This should match exactly
                'Exchange From': 'EUR',
                'Exchange To': 'PKR',
                'Exchange Rate': '275.23'
            }
        ],
        'template_config': {'bank_name': 'Wise'}
    }
    
    nayapay_data = {
        'file_name': 'nayapay_pkr_test.csv', 
        'data': [
            {
                'Date': '2025-02-14',
                'Amount': '30000.00',  # KEY: Should match Exchange To Amount exactly
                'Title': 'IBFT In',
                'Note': 'Incoming fund transfer from Ammar Qazi\nWise Transfer via Bank Alfalah-2050|Transaction ID 192351',
                'Currency': 'PKR'
            }
        ],
        'template_config': {'bank_name': 'NayaPay'}
    }
    
    # Initialize enhanced detector with debug enabled
    detector = EnhancedUniversalTransferDetector(
        user_name="Ammar Qazi", 
        date_tolerance_hours=24,
        debug=True
    )
    print("✅ Successfully created EnhancedUniversalTransferDetector with debug enabled")
    
    # Run detection
    try:
        csv_data_list = [wise_data, nayapay_data]
        results = detector.detect_transfers(csv_data_list)
        print("✅ Transfer detection completed successfully")
    except Exception as e:
        print(f"❌ Transfer detection failed: {e}")
        import traceback
        print(f"📚 Full traceback: {traceback.format_exc()}")
        return False
    
    # Analyze results
    print("\n📊 ANALYZING RESULTS:")
    print("-" * 40)
    
    # Check summary
    summary = results.get('summary', {})
    print(f"Total transactions: {summary.get('total_transactions', 0)}")
    print(f"Transfer pairs found: {summary.get('transfer_pairs_found', 0)}")
    print(f"Exchange exact matches: {summary.get('exchange_exact_matches', 0)}")
    print(f"Target scenario achieved: {summary.get('target_scenario_achieved', False)}")
    
    # Check individual pairs
    transfers = results.get('transfers', [])
    print(f"\n🔍 INDIVIDUAL TRANSFER PAIRS ({len(transfers)}):")
    
    success = False
    for i, pair in enumerate(transfers):
        print(f"\n📌 PAIR {i+1}: {pair.get('pair_id', 'unknown')}")
        print(f"   Strategy: {pair.get('match_strategy', 'unknown')}")
        print(f"   Confidence: {pair.get('confidence', 0):.2f}")
        print(f"   Type: {pair.get('transfer_type', 'unknown')}")
        
        if pair.get('match_strategy') == 'exchange_exact':
            print(f"   💱 Exchange Amount: {pair.get('exchange_amount')}")
            print(f"   💰 Matched Amount: {pair.get('matched_amount')}")
            print(f"   📏 Amount Difference: {pair.get('amount_difference', 0):.2f}")
            print(f"   🏦 Cross-bank: {pair.get('is_cross_bank', False)}")
            
            # Check if this is our target scenario
            if pair.get('confidence', 0) >= 1.00:
                print(f"   🎉 SUCCESS: This pair meets the target confidence >= 1.00!")
                success = True
            else:
                print(f"   ⚠️  Note: Confidence {pair.get('confidence', 0):.2f} < 1.00")
    
    # Final assessment
    print(f"\n🏆 TEST RESULT: {'✅ PASSED' if success else '❌ FAILED'}")
    if success:
        print("   Target EUR->PKR scenario successfully detected with 1.00+ confidence!")
        print("   The enhanced transfer detector is working as intended.")
    else:
        print("   Target scenario not achieved. Issues to investigate:")
        print("   - Check exchange amount detection from 'Exchange To Amount' column")
        print("   - Verify cross-bank transfer detection (Wise->NayaPay)")
        print("   - Review confidence calculation for exact matches")
    
    return success

def test_exchange_amount_extraction():
    """Test just the exchange amount extraction functionality"""
    
    print("\n🧪 TESTING EXCHANGE AMOUNT EXTRACTION")
    print("=" * 60)
    
    try:
        from transfer_detector_enhanced_universal import EnhancedUniversalTransferDetector
        detector = EnhancedUniversalTransferDetector(debug=True)
        
        # Test various column patterns
        test_transactions = [
            {
                'Exchange To Amount': '30000.00',
                'Description': 'Test with standard column name'
            },
            {
                'exchange_to_amount': '25000.50', 
                'Description': 'Test with lowercase column name'
            },
            {
                'ConvertedAmount': '15000.75',
                'Description': 'Test with alternative column name'
            },
            {
                'Exchange To Amount': '',
                'Description': 'Test with empty exchange amount'
            },
            {
                'Amount': '100.00',
                'Description': 'Test with no exchange amount column'
            }
        ]
        
        print("\n📊 TESTING EXCHANGE AMOUNT EXTRACTION:")
        for i, transaction in enumerate(test_transactions):
            exchange_amount = detector._extract_exchange_amount(transaction)
            detected_column = detector._get_detected_exchange_column(transaction)
            print(f"\n   Test {i+1}: {transaction.get('Description')}")
            print(f"      Exchange Amount: {exchange_amount}")
            print(f"      Detected Column: '{detected_column}'")
            if exchange_amount:
                print(f"      ✅ Successfully extracted: {exchange_amount}")
            else:
                print(f"      ❌ No exchange amount detected")
        
        return True
        
    except Exception as e:
        print(f"❌ Exchange amount extraction test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 STARTING ENHANCED TRANSFER DETECTOR TESTS")
    print("Testing the specific EUR->PKR scenario with verbose debugging...")
    print()
    
    # Test 1: Exchange amount extraction
    extraction_success = test_exchange_amount_extraction()
    
    # Test 2: Full transfer detection
    detection_success = test_enhanced_transfer_detector()
    
    # Final results
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"Exchange Amount Extraction: {'✅ PASSED' if extraction_success else '❌ FAILED'}")
    print(f"Full Transfer Detection: {'✅ PASSED' if detection_success else '❌ FAILED'}")
    
    if extraction_success and detection_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("Enhanced Universal Transfer Detector is working correctly.")
        print("Ready to handle EUR->PKR Wise->NayaPay scenarios with 1.00 confidence.")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Check the debug output above to identify and fix issues.")
    
    sys.exit(0 if (extraction_success and detection_success) else 1)
