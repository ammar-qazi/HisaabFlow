#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

from csv_parser import CSVParser
import pandas as pd

def test_nayapay_parsing():
    parser = CSVParser()
    file_path = "../nayapay_statement.csv"
    
    print("=== Testing NayaPay CSV Parser ===")
    
    # Test 1: Preview CSV
    print("\n1. CSV Preview:")
    preview = parser.preview_csv(file_path)
    if preview['success']:
        print(f"   ✓ Total rows: {preview['total_rows']}")
        print(f"   ✓ Total columns: {preview['total_columns']}")
    else:
        print(f"   ✗ Error: {preview['error']}")
        return
    
    # Test 2: Auto-detect data range
    print("\n2. Auto-detect Data Range:")
    detection = parser.detect_data_range(file_path)
    if detection['success']:
        print(f"   ✓ Suggested header row: {detection['suggested_header_row']}")
    else:
        print(f"   ✗ Error: {detection['error']}")
    
    # Test 3: Parse with specific range (we know it's row 13 for headers)
    print("\n3. Parse Data Range (Row 13-end, Columns 0-4):")
    parsed = parser.parse_with_range(file_path, start_row=13, start_col=0, end_col=5)
    if parsed['success']:
        print(f"   ✓ Headers: {parsed['headers']}")
        print(f"   ✓ Rows parsed: {parsed['row_count']}")
        print("   ✓ First 2 data rows:")
        for i, row in enumerate(parsed['data'][:2]):
            print(f"      {i+1}: {row}")
    else:
        print(f"   ✗ Error: {parsed['error']}")
        return
    
    # Test 4: Transform to Cashew format
    print("\n4. Transform to Cashew Format:")
    nayapay_mapping = {
        'Date': 'TIMESTAMP',
        'Amount': 'AMOUNT', 
        'Title': 'DESCRIPTION',
        'Note': 'TYPE',
        'Category': '',  # Will be empty for now
    }
    
    cashew_data = parser.transform_to_cashew(parsed['data'], nayapay_mapping, "NayaPay")
    print(f"   ✓ Converted {len(cashew_data)} transactions")
    
    if cashew_data:
        print("   ✓ First 3 converted rows:")
        for i, row in enumerate(cashew_data[:3]):
            print(f"      {i+1}: {row}")
        
        # Test 5: Save converted data
        print("\n5. Save Converted Data:")
        df_cashew = pd.DataFrame(cashew_data)
        output_path = "../converted_nayapay.csv"
        df_cashew.to_csv(output_path, index=False)
        print(f"   ✓ Saved to: {output_path}")
        
        # Show what the saved file looks like
        print("   ✓ Saved file preview:")
        print(df_cashew.head().to_string(index=False))
    
    print("\n=== Test Completed Successfully! ===")

if __name__ == "__main__":
    test_nayapay_parsing()
