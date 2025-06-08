#!/usr/bin/env python3
"""
Test the enhanced transfer detector with Wise->NayaPay transfers
"""

import sys
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from transfer_detector import TransferDetector

def test_enhanced_wise_nayapay():
    """Test the enhanced detector with your specific Wise->NayaPay pattern"""
    
    print("🧪 TESTING ENHANCED WISE→NAYAPAY DETECTION")
    print("=" * 50)
    
    # Your exact transfer pattern
    wise_data = {
        'file_name': 'wise_transactions.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '-108.99',
                'Description': 'Sent money to Ammar Qazi',
                'Exchange To Amount': '30000'
            },
            {
                'Date': '2025-06-04',
                'Amount': '-181.1',
                'Description': 'Sent money to Ammar Qazi', 
                'Exchange To Amount': '50000'
            },
            {
                'Date': '2025-06-04',
                'Amount': '-75.00',
                'Description': 'Converted 75.00 USD to 68.30 EUR',
                'Exchange To Amount': '68.30'
            }
        ],
        'template_config': {'bank_name': 'Wise'}
    }
    
    nayapay_data = {
        'file_name': 'nayapay_transactions.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '30000',
                'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2050|Transaction ID 192351'
            },
            {
                'Date': '2025-06-04',
                'Amount': '50000',
                'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2051|Transaction ID 192352'
            }
        ],
        'template_config': {'bank_name': 'NayaPay'}
    }
    
    wise_eur_data = {
        'file_name': 'wise_eur_account.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '68.30',
                'Description': 'Converted USD from USD balance'
            }
        ],
        'template_config': {'bank_name': 'Wise EUR'}
    }
    
    print("📊 INPUT DATA:")
    print("   WISE:")
    for trans in wise_data['data']:
        print(f"     {trans['Amount']} - {trans['Description']}")
        if 'Exchange To Amount' in trans:
            print(f"       Exchange To: {trans['Exchange To Amount']}")
    
    print("   NAYAPAY:")
    for trans in nayapay_data['data']:
        print(f"     {trans['Amount']} - {trans['Description']}")
    
    print("   WISE EUR:")
    for trans in wise_eur_data['data']:
        print(f"     {trans['Amount']} - {trans['Description']}")
    
    # Test enhanced detector
    detector = TransferDetector(user_name="Ammar Qazi")
    csv_data_list = [wise_data, nayapay_data, wise_eur_data]
    
    print("\\n🔍 ENHANCED DETECTION RESULTS:")
    results = detector.detect_transfers(csv_data_list)
    
    print(f"   Total Transfers Found: {len(results['transfers'])}")
    print(f"   Potential Transfers: {len(results['potential_transfers'])}")
    
    if results['transfers']:
        print("\\n   ✅ DETECTED TRANSFERS:")
        for i, pair in enumerate(results['transfers'], 1):
            print(f"     {i}. OUT: {pair['outgoing']['Description']} ({pair['outgoing']['Amount']})")
            print(f"        IN:  {pair['incoming']['Description']} ({pair['incoming']['Amount']})")
            print(f"        Confidence: {pair['confidence']:.2f}")
            print(f"        Banks: {pair['outgoing'].get('_bank_type', 'unknown')} → {pair['incoming'].get('_bank_type', 'unknown')}")
            if pair.get('exchange_amount'):
                print(f"        Exchange Amount: {pair['exchange_amount']}")
    else:
        print("\\n   ❌ NO TRANSFERS DETECTED")
    
    # Count specific transfer types
    wise_to_nayapay = sum(1 for p in results['transfers'] 
                         if (p['outgoing'].get('_bank_type') == 'wise' and 
                             p['incoming'].get('_bank_type') == 'nayapay'))
    
    wise_internal = sum(1 for p in results['transfers']
                       if (p['outgoing'].get('_bank_type') == 'wise' and 
                           p['incoming'].get('_bank_type') == 'wise'))
    
    print(f"\\n🎯 SUMMARY:")
    print(f"   Wise→NayaPay transfers: {wise_to_nayapay}")
    print(f"   Wise internal transfers: {wise_internal}")
    print(f"   Total transfers: {len(results['transfers'])}")
    
    return results

if __name__ == "__main__":
    results = test_enhanced_wise_nayapay()
    
    print("\\n" + "="*60)
    print("🎯 TEST RESULTS")
    print("="*60)
    
    wise_to_nayapay_count = sum(1 for p in results['transfers'] 
                               if (p['outgoing'].get('_bank_type') == 'wise' and 
                                   p['incoming'].get('_bank_type') == 'nayapay'))
    
    if wise_to_nayapay_count >= 2:
        print("✅ SUCCESS: Enhanced detector found both Wise→NayaPay transfers!")
        print("   Your cross-bank transfer detection is now working.")
    elif wise_to_nayapay_count == 1:
        print("⚠️  PARTIAL: Found 1 Wise→NayaPay transfer, expected 2")
        print("   Check if both transfers match the expected pattern.")
    else:
        print("❌ ISSUE: No Wise→NayaPay transfers detected")
        print("   The enhancement may need debugging.")
    
    if len(results['transfers']) >= 3:
        print("✅ BONUS: Internal Wise transfers still working!")
    
    print("\\n🚀 Ready to test with your real data!")
