#!/usr/bin/env python3
"""
Test script for the improved transfer detector
"""

import sys
import os
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from transfer_detector_improved import ImprovedTransferDetector

# Test data simulating the issue from the log
def test_improved_transfer_detector():
    print("🚀 Testing Improved Transfer Detector")
    print("="*50)
    
    # Sample data representing the issue: 
    # Wise outgoing: "Sent money to Ammar Qazi" 
    # NayaPay incoming: "Incoming fund transfer from Ammar Qazi"
    
    wise_csv_data = {
        'file_name': 'wise_USD.csv',
        'data': [
            {
                'Date': '2025-06-02',
                'Amount': '-254.1',
                'Description': 'Sent money to Usama Qazi...',
                'Currency': 'USD'
            },
            {
                'Date': '2025-05-15',
                'Amount': '-500.0', 
                'Description': 'Sent money to Ammar Qazi...',
                'Currency': 'USD'
            },
            {
                'Date': '2025-05-14',
                'Amount': '-1000.0',
                'Description': 'Sent money to Zunayyara Khalid...',
                'Currency': 'USD'
            }
        ]
    }
    
    nayapay_csv_data = {
        'file_name': 'nayapay_feb.csv',
        'data': [
            {
                'Date': '2025-05-15',
                'Amount': '500.0',
                'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2050|Transaction ID 017707',
                'Type': 'IBFT In'
            },
            {
                'Date': '2025-05-14',
                'Amount': '1000.0',
                'Description': 'Incoming fund transfer from Zunayyara Khalid Bank Alfalah-1234|Transaction ID 018888',
                'Type': 'IBFT In'
            },
            {
                'Date': '2025-02-03',
                'Amount': '50000.0',
                'Description': 'Incoming fund transfer from Someone Else Bank Alfalah-5678|Transaction ID 019999',
                'Type': 'IBFT In'
            }
        ]
    }
    
    csv_data_list = [wise_csv_data, nayapay_csv_data]
    
    # Test the improved detector
    detector = ImprovedTransferDetector(user_name="Ammar Qazi", date_tolerance_hours=24)
    
    print("Testing transfer detection...")
    results = detector.detect_transfers(csv_data_list)
    
    print("\n" + "="*50)
    print("🎯 RESULTS SUMMARY:")
    print(f"   Total transfers found: {results['summary']['transfer_pairs_found']}")
    print(f"   Currency conversions: {results['summary']['currency_conversions']}")
    print(f"   Person-to-person: {results['summary']['person_to_person_transfers']}")
    print(f"   Potential transfers: {results['summary']['potential_transfers']}")
    
    # Check if we found the expected transfer pairs
    if results['summary']['person_to_person_transfers'] > 0:
        print("\n✅ SUCCESS: Person-to-person transfers detected!")
        for i, transfer in enumerate(results['transfers']):
            if transfer['transfer_type'] == 'person_to_person':
                print(f"\n🎯 Transfer Pair {i+1}:")
                print(f"   👤 Person: {transfer.get('person_name', 'Unknown')}")
                print(f"   📤 Outgoing: {transfer['outgoing']['_csv_name']} | {transfer['outgoing']['Amount']}")
                print(f"   📥 Incoming: {transfer['incoming']['_csv_name']} | {transfer['incoming']['Amount']}")
                print(f"   🎯 Confidence: {transfer['confidence']:.2f}")
    else:
        print("\n❌ ISSUE: No person-to-person transfers detected")
        print("   This indicates the algorithm still needs improvement")
    
    return results

if __name__ == "__main__":
    test_improved_transfer_detector()
