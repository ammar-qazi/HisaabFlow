#!/usr/bin/env python3
"""
Test script for Enhanced Transfer Detection
Demonstrates detection of Wise->NayaPay cross-bank transfers
"""

import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/enhanced_transfer_detection')

from enhanced_transfer_detector import EnhancedTransferDetector

def test_wise_nayapay_transfer():
    """Test the specific Wise->NayaPay transfer pattern you described"""
    
    print("🧪 Testing Enhanced Transfer Detection - Wise→NayaPay Cross-Bank Transfers")
    print("=" * 70)
    
    # Sample data based on your example
    wise_csv_data = {
        'file_name': 'wise_transactions.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '-108.99',
                'Description': 'Sent money to Ammar Qazi',
                'Exchange To Amount': '30000',
                'Currency': 'USD'
            },
            {
                'Date': '2025-06-04', 
                'Amount': '-50.00',
                'Description': 'Converted 50.00 USD to 45.00 EUR',
                'Exchange To Amount': '45.00',
                'Currency': 'USD'
            }
        ],
        'template_config': {
            'bank_name': 'Wise',
            'column_mapping': {'Date': 'Date', 'Amount': 'Amount', 'Description': 'Description'}
        }
    }
    
    nayapay_csv_data = {
        'file_name': 'nayapay_transactions.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '30000',
                'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2050|Transaction ID 192351',
                'Category': 'Transfer'
            },
            {
                'Date': '2025-06-04',
                'Amount': '5000',
                'Description': 'Regular purchase at Store XYZ',
                'Category': 'Shopping'
            }
        ],
        'template_config': {
            'bank_name': 'NayaPay',
            'column_mapping': {'Date': 'Date', 'Amount': 'Amount', 'Description': 'Description'}
        }
    }
    
    wise_eur_csv_data = {
        'file_name': 'wise_eur_account.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '45.00',
                'Description': 'Converted USD from USD balance',
                'Currency': 'EUR'
            }
        ],
        'template_config': {
            'bank_name': 'Wise EUR',
            'column_mapping': {'Date': 'Date', 'Amount': 'Amount', 'Description': 'Description'}
        }
    }
    
    # Initialize enhanced detector
    detector = EnhancedTransferDetector(user_name="Ammar Qazi", date_tolerance_hours=24)
    
    # Test detection
    csv_data_list = [wise_csv_data, nayapay_csv_data, wise_eur_csv_data]
    results = detector.detect_transfers(csv_data_list)
    
    print(f"📊 Detection Results Summary:")
    print(f"   Total Transactions: {results['summary']['total_transactions']}")
    print(f"   Transfer Pairs Found: {results['summary']['transfer_pairs_found']}")
    print(f"   Cross-Bank Transfers: {results['detection_strategies']['cross_bank_transfers']}")
    print(f"   Currency Conversions: {results['detection_strategies']['currency_conversions']}")
    print(f"   Traditional Transfers: {results['detection_strategies']['traditional_transfers']}")
    print()
    
    # Display detected transfer pairs
    print("🔄 Detected Transfer Pairs:")
    print("-" * 50)
    
    for i, pair in enumerate(results['transfers'], 1):
        print(f"\n{i}. {pair['transfer_type'].upper()} Transfer:")
        print(f"   📤 OUT: {pair['outgoing']['Description']}")
        print(f"        Amount: {pair['outgoing']['Amount']} ({pair['outgoing']['_bank_type']})")
        print(f"        Date: {pair['outgoing']['Date']}")
        if pair.get('exchange_amount'):
            print(f"        Exchange To: {pair['exchange_amount']}")
        
        print(f"   📥 IN:  {pair['incoming']['Description']}")
        print(f"        Amount: {pair['incoming']['Amount']} ({pair['incoming']['_bank_type']})")
        print(f"        Date: {pair['incoming']['Date']}")
        
        print(f"   ✅ Confidence: {pair['confidence']:.2f}")
        print(f"   🏦 Transfer: {pair['from_bank']} → {pair['to_bank']}")
    
    # Show potential unmatched transfers
    if results['potential_transfers']:
        print("\n⚠️  Potential Unmatched Transfers:")
        print("-" * 40)
        for potential in results['potential_transfers']:
            print(f"   💰 {potential['Description']} - {potential['Amount']}")
            print(f"       Reason: {potential.get('_unmatched_reason', 'Unknown')}")
    
    # Show conflicts if any
    if results['conflicts']:
        print("\n⚡ Conflicts Requiring Manual Review:")
        print("-" * 45)
        for conflict in results['conflicts']:
            print(f"   🔥 {conflict['conflict_type']}: {len(conflict['potential_matches'])} matches")
    
    print("\n" + "="*70)
    return results

def test_categorization_application(transfer_results, csv_data_list):
    """Test applying the transfer categorization"""
    
    print("🏷️  Testing Transfer Categorization Application")
    print("=" * 50)
    
    detector = EnhancedTransferDetector(user_name="Ammar Qazi")
    
    # Apply transfer categorization
    transfer_matches = detector.apply_transfer_categorization(
        csv_data_list, 
        transfer_results['transfers']
    )
    
    print(f"\n📋 Transfer Categorization Matches Generated: {len(transfer_matches)}")
    print("-" * 55)
    
    for match in transfer_matches:
        print(f"\n🏦 {match['bank_transfer_type'].title()} Transfer ({match['transfer_type']})")
        print(f"   💰 Amount: {match['amount']}")
        print(f"   📅 Date: {match['date']}")
        print(f"   📝 Description: {match['description'][:50]}...")
        print(f"   🏷️  Category: {match['category']}")
        print(f"   📄 Note: {match['note']}")
        if match.get('exchange_amount'):
            print(f"   💱 Exchange Amount: {match['exchange_amount']}")
    
    return transfer_matches

def simulate_full_pipeline():
    """Simulate the full enhanced transfer detection pipeline"""
    
    print("\n🚀 FULL ENHANCED TRANSFER DETECTION PIPELINE")
    print("=" * 60)
    
    # Run the main test
    transfer_results = test_wise_nayapay_transfer()
    
    # Test categorization
    wise_csv_data = {
        'file_name': 'wise_transactions.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '-108.99',
                'Description': 'Sent money to Ammar Qazi',
                'Exchange To Amount': '30000',
                'Currency': 'USD'
            },
            {
                'Date': '2025-06-04', 
                'Amount': '-50.00',
                'Description': 'Converted 50.00 USD to 45.00 EUR',
                'Exchange To Amount': '45.00',
                'Currency': 'USD'
            }
        ],
        'template_config': {
            'bank_name': 'Wise',
            'column_mapping': {'Date': 'Date', 'Amount': 'Amount', 'Description': 'Description'}
        }
    }
    
    nayapay_csv_data = {
        'file_name': 'nayapay_transactions.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '30000',
                'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2050|Transaction ID 192351',
                'Category': 'Transfer'
            }
        ],
        'template_config': {
            'bank_name': 'NayaPay',
            'column_mapping': {'Date': 'Date', 'Amount': 'Amount', 'Description': 'Description'}
        }
    }
    
    wise_eur_csv_data = {
        'file_name': 'wise_eur_account.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '45.00',
                'Description': 'Converted USD from USD balance',
                'Currency': 'EUR'
            }
        ],
        'template_config': {
            'bank_name': 'Wise EUR',
            'column_mapping': {'Date': 'Date', 'Amount': 'Amount', 'Description': 'Description'}
        }
    }
    
    csv_data_list = [wise_csv_data, nayapay_csv_data, wise_eur_csv_data]
    
    transfer_matches = test_categorization_application(transfer_results, csv_data_list)
    
    print("\n🎯 SUMMARY:")
    print("=" * 20)
    print(f"✅ Cross-bank transfers detected: {len([p for p in transfer_results['transfers'] if p['transfer_type'] == 'cross_bank'])}")
    print(f"✅ Currency conversions detected: {len([p for p in transfer_results['transfers'] if p['transfer_type'] == 'currency_conversion'])}")
    print(f"✅ Transfer categorizations created: {len(transfer_matches)}")
    print(f"✅ Wise→NayaPay transfer: {'✓ DETECTED' if any(p['from_bank'] == 'wise' and p['to_bank'] == 'nayapay' for p in transfer_results['transfers']) else '✗ MISSED'}")
    print(f"✅ Wise USD→EUR conversion: {'✓ DETECTED' if any(p['transfer_type'] == 'currency_conversion' for p in transfer_results['transfers']) else '✗ MISSED'}")
    
    return transfer_results, transfer_matches

if __name__ == "__main__":
    try:
        # Run the full test
        results, matches = simulate_full_pipeline()
        
        print("\n🎉 Enhanced Transfer Detection Test Completed Successfully!")
        print("   Ready for integration into main system.")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        print(f"📚 Traceback: {traceback.format_exc()}")
