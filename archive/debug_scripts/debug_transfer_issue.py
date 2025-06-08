#!/usr/bin/env python3
"""
Diagnostic script to debug the transfer detection issue
"""

import sys
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from transfer_detector_enhanced import EnhancedTransferDetector

def debug_transfer_detection():
    """Debug the transfer detection with sample data similar to what you're seeing"""
    
    print("🔍 DEBUGGING TRANSFER DETECTION ISSUE")
    print("=" * 50)
    
    # Sample data based on your output - this is likely what's happening
    wise_data_after_categorization = {
        'file_name': 'wise_test.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '-413.89',
                'Description': 'Converted 413.89 USD to 150,000.00 HUF for HUF balance',  # Original description
                'Category': 'Expense',  # Template already applied!
                'Exchange To Amount': '150000.00'
            },
            {
                'Date': '2025-06-04',
                'Amount': '-181.1',
                'Description': 'Sent money to Ammar Qazi',  # This should be detected!
                'Category': 'Expense',  # Template already applied!
                'Exchange To Amount': '50000'  # Assuming PKR equivalent
            }
        ],
        'template_config': {'bank_name': 'Wise'}
    }
    
    nayapay_data_after_categorization = {
        'file_name': 'nayapay_test.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '50000',  # PKR incoming
                'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2050',
                'Category': 'Transfer'  # Template categorization
            }
        ],
        'template_config': {'bank_name': 'NayaPay'}
    }
    
    print("📊 TESTING WITH CATEGORIZED DATA (Current Issue):")
    detector = EnhancedTransferDetector(user_name="Ammar Qazi")
    
    # This is what's happening now - detection after categorization
    csv_data_list = [wise_data_after_categorization, nayapay_data_after_categorization]
    results = detector.detect_transfers(csv_data_list)
    
    print(f"   Transfers Found: {len(results['transfers'])}")
    print(f"   Potential Transfers: {len(results['potential_transfers'])}")
    print(f"   Cross-Bank Transfers: {results['detection_strategies']['cross_bank_transfers']}")
    
    # Show what transfers were found
    for i, pair in enumerate(results['transfers']):
        print(f"   Transfer {i+1}: {pair['outgoing']['Description']} -> {pair['incoming']['Description']}")
    
    # Now test with raw data (before categorization)
    print(f"\n📊 TESTING WITH RAW DATA (Should Work):")
    
    wise_data_raw = {
        'file_name': 'wise_test.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '-413.89',
                'Description': 'Converted 413.89 USD to 150,000.00 HUF for HUF balance',
                'Exchange To Amount': '150000.00'
                # No Category field - raw data
            },
            {
                'Date': '2025-06-04',
                'Amount': '-181.1',
                'Description': 'Sent money to Ammar Qazi',
                'Exchange To Amount': '50000'
                # No Category field - raw data
            }
        ],
        'template_config': {'bank_name': 'Wise'}
    }
    
    nayapay_data_raw = {
        'file_name': 'nayapay_test.csv',
        'data': [
            {
                'Date': '2025-06-04',
                'Amount': '50000',
                'Description': 'Incoming fund transfer from Ammar Qazi Bank Alfalah-2050'
                # No Category field - raw data
            }
        ],
        'template_config': {'bank_name': 'NayaPay'}
    }
    
    csv_data_list_raw = [wise_data_raw, nayapay_data_raw]
    results_raw = detector.detect_transfers(csv_data_list_raw)
    
    print(f"   Transfers Found: {len(results_raw['transfers'])}")
    print(f"   Cross-Bank Transfers: {results_raw['detection_strategies']['cross_bank_transfers']}")
    
    # Show what transfers were found
    for i, pair in enumerate(results_raw['transfers']):
        print(f"   Transfer {i+1}: {pair['outgoing']['Description']} -> {pair['incoming']['Description']}")
        print(f"   Transfer Type: {pair['transfer_type']}")
        print(f"   Confidence: {pair['confidence']}")
        
    return results, results_raw

if __name__ == "__main__":
    debug_transfer_detection()
