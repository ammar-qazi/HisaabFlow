#!/usr/bin/env python3
"""
Comprehensive test for improved transfer detector
Testing the exact scenarios from the original issue
"""

import sys
import os
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from transfer_detector_improved import ImprovedTransferDetector

def test_comprehensive_scenarios():
    print('🧪 COMPREHENSIVE TRANSFER DETECTION TEST')
    print('='*50)
    
    # Test data matching the original issue from the log
    wise_data = {
        'file_name': 'wise_USD.csv',
        'data': [
            {'Date': '2025-05-15', 'Amount': '-500.0', 'Description': 'Sent money to Ammar Qazi...'},
            {'Date': '2025-05-14', 'Amount': '-1000.0', 'Description': 'Sent money to Zunayyara Khalid...'},
            {'Date': '2025-05-13', 'Amount': '-300.0', 'Description': 'Sent money to Muhammad Zakki Soh...'}
        ]
    }
    
    nayapay_data = {
        'file_name': 'nayapay_feb.csv', 
        'data': [
            {'Date': '2025-05-15', 'Amount': '500.0', 'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2050|Transaction ID 017707'},
            {'Date': '2025-05-14', 'Amount': '1000.0', 'Description': 'Incoming fund transfer from Zunayyara Khalid Bank Alfalah-1234|Transaction ID 018888'},
            {'Date': '2025-05-10', 'Amount': '2000.0', 'Description': 'Incoming fund transfer from Someone Else Bank Alfalah-5678|Transaction ID 019999'}
        ]
    }
    
    detector = ImprovedTransferDetector(user_name='Ammar Qazi', date_tolerance_hours=24)
    results = detector.detect_transfers([wise_data, nayapay_data])
    
    print(f'\n📊 SUMMARY:')
    print(f'   ✅ Total transfers detected: {results["summary"]["transfer_pairs_found"]}')
    print(f'   👤 Person-to-person transfers: {results["summary"]["person_to_person_transfers"]}')
    print(f'   💱 Currency conversions: {results["summary"]["currency_conversions"]}')
    
    # Verify specific matches
    person_transfers = [t for t in results['transfers'] if t['transfer_type'] == 'person_to_person']
    print(f'\n🎯 DETAILED RESULTS:')
    for i, transfer in enumerate(person_transfers):
        person_name = transfer.get('person_name', 'Unknown')
        outgoing_amount = abs(float(transfer['outgoing']['Amount']))
        confidence = transfer['confidence']
        print(f'   Transfer {i+1}: {person_name} - ${outgoing_amount} - Confidence: {confidence:.2f}')
    
    # Expected results based on our test data
    expected_matches = [
        ('Ammar', 500.0),
        ('Zunayyara', 1000.0)  # Should match "Zunayyara Khalid" with "Zunayyara"
    ]
    
    print(f'\n🔍 VALIDATION:')
    success_count = 0
    for expected_name, expected_amount in expected_matches:
        found = False
        for transfer in person_transfers:
            if (expected_name.lower() in transfer.get('person_name', '').lower() and 
                abs(float(transfer['outgoing']['Amount'])) == expected_amount):
                found = True
                success_count += 1
                print(f'   ✅ Found expected transfer: {expected_name} - ${expected_amount}')
                break
        if not found:
            print(f'   ❌ Missing expected transfer: {expected_name} - ${expected_amount}')
    
    if success_count == len(expected_matches):
        print(f'\n🎉 SUCCESS: All expected transfers detected! ({success_count}/{len(expected_matches)})')
        return True
    else:
        print(f'\n⚠️ PARTIAL SUCCESS: {success_count}/{len(expected_matches)} transfers detected')
        return False

if __name__ == "__main__":
    test_comprehensive_scenarios()
