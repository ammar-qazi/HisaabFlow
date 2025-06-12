#!/usr/bin/env python3
"""
Enhanced debug test to identify the exact issue in parsing
"""

import requests
import json
import os

API_BASE = "http://127.0.0.1:8000"
SAMPLE_FILE = "/home/ammar/claude_projects/bank_statement_parser/sample_data/m-02-2025.csv"

def debug_csv_structure():
    """Debug the CSV structure to understand parsing issues"""
    print("🔍 Debugging CSV Structure")
    print("=" * 50)
    
    with open(SAMPLE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 Total lines in CSV: {len(lines)}")
    print(f"📋 Line 13 (expected headers): {lines[13].strip()}")
    print(f"📊 Line 14 (first data row): {lines[14].strip()}")
    print(f"📊 Line 15 (second data row): {lines[15].strip()}")
    
    # Count actual data rows (starting from line 14)
    data_lines = lines[14:]
    non_empty_data = [line for line in data_lines if line.strip()]
    print(f"📊 Data rows available (from line 14): {len(non_empty_data)}")
    
    return len(non_empty_data)

def test_parsing_with_debug():
    """Test parsing with detailed debugging"""
    expected_rows = debug_csv_structure()
    print(f"\n🎯 Expected transaction count: {expected_rows}")
    
    # Upload file
    print(f"\n📤 Uploading file...")
    with open(SAMPLE_FILE, 'rb') as f:
        files = {'file': ('m-02-2025.csv', f, 'text/csv')}
        upload_response = requests.post(f"{API_BASE}/upload", files=files)
    
    file_id = upload_response.json()['file_id']
    print(f"✅ File uploaded: {file_id}")
    
    # Preview
    print(f"\n🔍 Getting preview...")
    preview_response = requests.get(f"{API_BASE}/preview/{file_id}")
    preview_data = preview_response.json()
    
    suggested_data_start_row = preview_data.get('suggested_data_start_row')
    print(f"🎯 Bank-detected data start row: {suggested_data_start_row}")
    
    # Test different parsing configurations
    test_configs = [
        {"name": "Bank-detected (row 14)", "start_row": 14, "expected": "SUCCESS"},
        {"name": "Manual (row 11)", "start_row": 11, "expected": "FAIL"},
        {"name": "Headers (row 13)", "start_row": 13, "expected": "HEADERS_ONLY"},
        {"name": "From start (row 0)", "start_row": 0, "expected": "METADATA"},
    ]
    
    for config in test_configs:
        print(f"\n🧪 Testing: {config['name']} (start_row={config['start_row']})")
        
        parse_request = {
            "file_ids": [file_id],
            "parse_configs": [{
                "start_row": config['start_row'],
                "end_row": None,
                "start_col": 0,
                "end_col": None,
                "encoding": "utf-8"
            }],
            "user_name": "Test User",
            "date_tolerance_hours": 24
        }
        
        parse_response = requests.post(f"{API_BASE}/multi-csv/parse", json=parse_request)
        
        if parse_response.status_code == 200:
            parse_data = parse_response.json()
            parsed_csvs = parse_data.get('parsed_csvs', [])
            
            if parsed_csvs:
                parse_result = parsed_csvs[0]['parse_result']
                row_count = parse_result.get('row_count', 0)
                headers = parse_result.get('headers', [])
                sample_data = parse_result.get('data', [])[:2]  # First 2 rows
                
                print(f"   📊 Rows: {row_count}")
                print(f"   📋 Headers: {headers[:3]}..." if headers else "   📋 Headers: None")
                
                if sample_data:
                    first_row = sample_data[0]
                    print(f"   📝 Sample: {list(first_row.keys())[:3]}..." if isinstance(first_row, dict) else f"   📝 Sample: {first_row}")
                
                # Determine result
                if row_count == expected_rows:
                    print(f"   ✅ PERFECT: Got expected {expected_rows} rows")
                elif row_count > 0:
                    print(f"   ⚠️  PARTIAL: Got {row_count} rows, expected {expected_rows}")
                else:
                    print(f"   ❌ FAILED: No rows processed")
            else:
                print(f"   ❌ No parsed data returned")
        else:
            print(f"   ❌ Parse request failed: {parse_response.text}")

if __name__ == "__main__":
    test_parsing_with_debug()
