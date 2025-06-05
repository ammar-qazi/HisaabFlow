#!/usr/bin/env python3
"""
Debug NayaPay CSV parsing to see what's going wrong
"""

import sys
sys.path.append('backend')

import pandas as pd
from enhanced_csv_parser import EnhancedCSVParser

def debug_nayapay_parsing():
    """Debug the NayaPay CSV parsing"""
    
    file_path = "m022025.csv"
    parser = EnhancedCSVParser()
    
    print("🔍 DEBUGGING NAYAPAY CSV PARSING")
    print("=" * 50)
    
    # Step 1: Raw file reading
    print("📁 Step 1: Raw file preview")
    try:
        df_raw = pd.read_csv(file_path, header=None, nrows=20)
        print(f"   📊 Raw shape: {df_raw.shape}")
        print(f"   📋 First few rows:")
        for i, row in df_raw.head(5).iterrows():
            print(f"   Row {i}: {list(row)}")
    except Exception as e:
        print(f"   ❌ Raw reading failed: {e}")
    
    # Step 2: Parse with range (start_row=13)
    print(f"\n📁 Step 2: Parse with range (start_row=13)")
    try:
        parse_result = parser.parse_with_range(file_path, start_row=13, end_col=5)
        print(f"   📊 Parse success: {parse_result.get('success', False)}")
        print(f"   📊 Row count: {parse_result.get('row_count', 0)}")
        print(f"   📋 Headers: {parse_result.get('headers', [])}")
        
        if parse_result.get('success') and parse_result.get('data'):
            print(f"   📋 First 3 data rows:")
            for i, row in enumerate(parse_result['data'][:3]):
                print(f"   Row {i}: {row}")
        
    except Exception as e:
        print(f"   ❌ Parse failed: {e}")
    
    # Step 3: Test transformation
    print(f"\n📁 Step 3: Test transformation")
    try:
        if parse_result.get('success') and parse_result.get('data'):
            column_mapping = {
                "Date": "TIMESTAMP",
                "Amount": "AMOUNT", 
                "Title": "DESCRIPTION",
                "Note": "TYPE"
            }
            
            print(f"   🔧 Column mapping: {column_mapping}")
            
            # Transform first few rows
            transformed = parser.transform_to_cashew(
                parse_result['data'][:3], 
                column_mapping, 
                "NayaPay"
            )
            
            print(f"   📊 Transformed {len(transformed)} rows:")
            for i, row in enumerate(transformed):
                print(f"   Row {i}: Date='{row.get('Date', '')}', Amount='{row.get('Amount', '')}', Title='{row.get('Title', '')[:50]}...'")
    
    except Exception as e:
        print(f"   ❌ Transform failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_nayapay_parsing()
