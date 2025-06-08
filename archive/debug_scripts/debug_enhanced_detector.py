#!/usr/bin/env python3
"""
Debug the enhanced transfer detector to see why internal Wise transfers aren't being detected
"""

import sys
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from transfer_detector_enhanced import EnhancedTransferDetector

def test_wise_internal_transfers():
    """Test Wise internal currency conversions that should be detected"""
    
    print("🔍 DEBUGGING WISE INTERNAL TRANSFER DETECTION")
    print("=" * 55)
    
    # Simple Wise internal transfer (USD->EUR conversion)
    wise_data = {
        'file_name': 'wise_usd_account.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '-100.00',
                'Description': 'Converted 100.00 USD to 92.00 EUR',
                'Exchange To Amount': '92.00',
                'Currency': 'USD'
            }
        ],
        'template_config': {'bank_name': 'Wise'}
    }
    
    wise_eur_data = {
        'file_name': 'wise_eur_account.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '92.00',
                'Description': 'Converted USD from USD balance',
                'Currency': 'EUR'
            }
        ],
        'template_config': {'bank_name': 'Wise EUR'}
    }
    
    print("📊 INPUT DATA:")
    print("   WISE USD:")
    for trans in wise_data['data']:
        print(f"     Amount: {trans['Amount']}, Desc: {trans['Description']}")
        print(f"     Exchange To: {trans.get('Exchange To Amount', 'N/A')}")
    
    print("\n   WISE EUR:")
    for trans in wise_eur_data['data']:
        print(f"     Amount: {trans['Amount']}, Desc: {trans['Description']}")
    
    # Test enhanced detector
    detector = EnhancedTransferDetector(user_name="Ammar Qazi")
    csv_data_list = [wise_data, wise_eur_data]
    
    print("\n🔍 ENHANCED DETECTOR RESULTS:")
    results = detector.detect_transfers(csv_data_list)
    
    print(f"   Total Transfers: {len(results['transfers'])}")
    print(f"   Cross-Bank: {results['detection_strategies']['cross_bank_transfers']}")
    print(f"   Currency Conversions: {results['detection_strategies']['currency_conversions']}")
    print(f"   Traditional: {results['detection_strategies']['traditional_transfers']}")
    
    if results['transfers']:
        for i, pair in enumerate(results['transfers'], 1):
            print(f"\n   {i}. {pair['transfer_type'].upper()} Transfer:")
            print(f"      OUT: {pair['outgoing']['Description']}")
            print(f"      IN:  {pair['incoming']['Description']}")
            print(f"      Confidence: {pair['confidence']}")
    else:
        print("\n   ❌ NO TRANSFERS DETECTED")
    
    return results

def test_original_detector():
    """Test with the original detector to compare"""
    
    print("\n🔍 TESTING ORIGINAL DETECTOR")
    print("=" * 35)
    
    sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')
    
    # Import the backup original detector
    try:
        # Read the backup file and create a temporary test
        with open('/home/ammar/claude_projects/bank_statement_parser/backend/transfer_detector_backup_20250604_151535.py', 'r') as f:
            content = f.read()
            
        # Extract the class name from original
        if 'class TransferDetector:' in content:
            print("   📁 Found original TransferDetector in backup")
            
            # Write to a temp file and import
            with open('/tmp/original_transfer_detector.py', 'w') as f:
                f.write(content)
            
            sys.path.insert(0, '/tmp')
            from original_transfer_detector import TransferDetector as OriginalTransferDetector
            
            # Test data
            wise_data = {
                'file_name': 'wise_usd_account.csv',
                'data': [
                    {
                        'Date': '2025-06-04',
                        'Amount': '-100.00',
                        'Description': 'Converted 100.00 USD to 92.00 EUR',
                        'Exchange To Amount': '92.00'
                    }
                ],
                'template_config': {'bank_name': 'Wise'}
            }
            
            wise_eur_data = {
                'file_name': 'wise_eur_account.csv',
                'data': [
                    {
                        'Date': '2025-06-04',
                        'Amount': '92.00',
                        'Description': 'Converted USD from USD balance'
                    }
                ],
                'template_config': {'bank_name': 'Wise EUR'}
            }
            
            original_detector = OriginalTransferDetector(user_name="Ammar Qazi")
            csv_data_list = [wise_data, wise_eur_data]
            
            original_results = original_detector.detect_transfers(csv_data_list)
            
            print(f"   Original Detector Results:")
            print(f"     Transfers Found: {len(original_results['transfers'])}")
            
            if original_results['transfers']:
                for i, pair in enumerate(original_results['transfers'], 1):
                    print(f"     {i}. {pair['outgoing']['Description']} -> {pair['incoming']['Description']}")
            
            return original_results
            
    except Exception as e:
        print(f"   ❌ Could not test original detector: {e}")
        return None

def debug_detection_steps():
    """Debug each step of the enhanced detection process"""
    
    print("\n🔧 DEBUGGING DETECTION STEPS")
    print("=" * 40)
    
    # Test data
    wise_data = {
        'file_name': 'wise_usd_account.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '-100.00',
                'Description': 'Converted 100.00 USD to 92.00 EUR',
                'Exchange To Amount': '92.00'
            }
        ],
        'template_config': {'bank_name': 'Wise'}
    }
    
    wise_eur_data = {
        'file_name': 'wise_eur_account.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '92.00',
                'Description': 'Converted USD from USD balance'
            }
        ],
        'template_config': {'bank_name': 'Wise EUR'}
    }
    
    detector = EnhancedTransferDetector(user_name="Ammar Qazi")
    
    # Step 1: Check bank type detection
    print("🏦 STEP 1: Bank Type Detection")
    for csv_data in [wise_data, wise_eur_data]:
        for trans in csv_data['data']:
            bank_type = detector._detect_bank_type(csv_data['file_name'], trans)
            print(f"   {csv_data['file_name']}: {bank_type}")
    
    # Step 2: Check cross-bank detection
    print("\n🌐 STEP 2: Cross-Bank Detection")
    csv_data_list = [wise_data, wise_eur_data]
    
    # Flatten transactions like the detector does
    all_transactions = []
    for csv_idx, csv_data in enumerate(csv_data_list):
        for trans_idx, transaction in enumerate(csv_data['data']):
            enhanced_transaction = {
                **transaction,
                '_csv_index': csv_idx,
                '_transaction_index': trans_idx,
                '_csv_name': csv_data.get('file_name', f'CSV_{csv_idx}'),
                '_template_config': csv_data.get('template_config', {}),
                '_bank_type': detector._detect_bank_type(csv_data.get('file_name', ''), transaction)
            }
            all_transactions.append(enhanced_transaction)
    
    print("   Flattened transactions:")
    for i, trans in enumerate(all_transactions):
        print(f"     {i+1}. {trans['Description']} (Bank: {trans['_bank_type']}, Amount: {trans['Amount']})")
    
    # Step 3: Test currency conversion detection specifically
    print("\n💱 STEP 3: Currency Conversion Detection")
    
    # Test the _detect_wise_conversions method directly
    wise_transactions = [t for t in all_transactions if t['_bank_type'] == 'wise']
    matched_transactions = set()
    
    if len(wise_transactions) >= 2:
        print("   Found Wise transactions for conversion testing:")
        for trans in wise_transactions:
            print(f"     - {trans['Description']} ({trans['Amount']})")
            
        # Test conversion detection
        conversions = detector._detect_wise_conversions(wise_transactions, matched_transactions)
        print(f"   Conversions detected: {len(conversions)}")
        
        for conv in conversions:
            print(f"     - {conv['outgoing']['Description']} -> {conv['incoming']['Description']}")
    else:
        print("   ❌ Not enough Wise transactions for conversion testing")
    
    return all_transactions

if __name__ == "__main__":
    # Test 1: Enhanced detector with simple Wise conversion
    enhanced_results = test_wise_internal_transfers()
    
    # Test 2: Original detector comparison
    original_results = test_original_detector()
    
    # Test 3: Step-by-step debugging
    debug_transactions = debug_detection_steps()
    
    print("\n" + "="*60)
    print("🎯 DEBUGGING SUMMARY")
    print("="*60)
    
    enhanced_found = len(enhanced_results['transfers']) if enhanced_results else 0
    original_found = len(original_results['transfers']) if original_results else 0
    
    print(f"Enhanced Detector: {enhanced_found} transfers")
    print(f"Original Detector: {original_found} transfers")
    
    if enhanced_found == 0 and original_found > 0:
        print("\n❌ REGRESSION: Enhanced detector broke existing functionality")
        print("   The enhanced detector is too restrictive")
    elif enhanced_found == 0:
        print("\n❌ ISSUE: Neither detector finds transfers")
        print("   Problem might be in test data or detection logic")
    else:
        print("\n✅ Enhanced detector is working")
    
    print("\n🔧 NEXT STEPS:")
    print("   1. Check if the enhanced detector's bank type detection is too strict")
    print("   2. Verify currency conversion logic in _detect_wise_conversions")
    print("   3. Compare with original detector behavior")
