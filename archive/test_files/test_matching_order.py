#!/usr/bin/env python3
"""
Quick test to verify the matching logic issue
"""

import sys
import os
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from transfer_detector_improved import ImprovedTransferDetector

def test_matching_order():
    print('🧪 TESTING MATCHING ORDER LOGIC')
    print('='*50)
    
    # Test with reversed order to see if matching is order-dependent
    wise_data = {
        'file_name': 'wise_USD.csv',
        'data': [
            # Feb 3 outgoing should match Feb 3 incoming
            {'Date': '2025-02-03', 'Amount': '-50000.0', 'Description': 'Sent money to Ammar Qazi Bank Transfer'},
            # Feb 14 outgoing should match Feb 14 incoming  
            {'Date': '2025-02-14', 'Amount': '-30000.0', 'Description': 'Sent money to Ammar Qazi Bank Transfer'},
        ]
    }
    
    nayapay_data = {
        'file_name': 'nayapay_feb.csv', 
        'data': [
            # Feb 3 incoming should match Feb 3 outgoing
            {'Date': '2025-02-03', 'Amount': '50000.0', 'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2050|Transaction ID 017707'},
            # Feb 14 incoming should match Feb 14 outgoing
            {'Date': '2025-02-14', 'Amount': '30000.0', 'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2050|Transaction ID 192351'},
        ]
    }
    
    print("🎯 TEST: Same data but in matching order")
    print("   Expected: 2 matches (both should work)")
    print()
    
    detector = ImprovedTransferDetector(user_name='Ammar Qazi', date_tolerance_hours=24)
    results = detector.detect_transfers([wise_data, nayapay_data])
    
    person_transfers = [t for t in results['transfers'] if t['transfer_type'] == 'person_to_person']
    print(f'\n📊 RESULT: Found {len(person_transfers)} person-to-person transfers')
    
    for i, transfer in enumerate(person_transfers):
        person_name = transfer.get('person_name', 'Unknown')
        outgoing_amount = abs(float(transfer['outgoing']['Amount']))
        date = transfer['date'].strftime('%Y-%m-%d')
        print(f'   Transfer {i+1}: {person_name} - ${outgoing_amount} on {date}')
    
    if len(person_transfers) == 2:
        print(f'\n🎉 SUCCESS: Found both expected transfers!')
        print("   ✅ The algorithm works perfectly with proper data ordering")
    else:
        print(f'\n⚠️ ISSUE CONFIRMED: Only found {len(person_transfers)}/2 transfers')
        print("   📝 The matching algorithm stops after first match per outgoing transaction")

if __name__ == "__main__":
    test_matching_order()
