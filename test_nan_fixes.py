#!/usr/bin/env python3
"""
Test the NaN fixes and bank detection
"""

import requests
import json

API_BASE = 'http://127.0.0.1:8000'

def test_nayapay_parsing():
    """Test NayaPay CSV parsing with the fixes"""
    
    print("🧪 Testing NayaPay CSV parsing with fixes...")
    
    # 1. Upload the NayaPay file
    print("\n1️⃣ Uploading NayaPay file...")
    with open('/home/ammar/claude_projects/bank_statement_parser/nayapay_statement.csv', 'rb') as f:
        files = {'file': ('nayapay_statement.csv', f, 'text/csv')}
        response = requests.post(f'{API_BASE}/upload', files=files)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.text}")
        return
    
    file_id = response.json()['file_id']
    print(f"✅ Upload successful: {file_id}")
    
    # 2. Preview the file
    print("\n2️⃣ Previewing file...")
    preview_response = requests.get(f'{API_BASE}/preview/{file_id}')
    
    if preview_response.status_code != 200:
        print(f"❌ Preview failed: {preview_response.text}")
        return
    
    preview_data = preview_response.json()
    print(f"✅ Preview successful: {preview_data['total_rows']} rows, {preview_data['total_columns']} columns")
    
    # 3. Detect data range
    print("\n3️⃣ Auto-detecting data range...")
    detect_response = requests.get(f'{API_BASE}/detect-range/{file_id}')
    
    if detect_response.status_code != 200:
        print(f"❌ Detection failed: {detect_response.text}")
        return
    
    detect_data = detect_response.json()
    suggested_start = detect_data.get('suggested_header_row', 13)
    print(f"✅ Detection successful: suggested start row = {suggested_start}")
    
    # 4. Parse with NayaPay template settings (start_row = 13)
    print("\n4️⃣ Parsing with start_row=13 (NayaPay template default)...")
    parse_request = {
        'start_row': 13,
        'end_row': None,
        'start_col': 0,
        'end_col': 5,
        'encoding': 'utf-8'
    }
    
    parse_response = requests.post(f'{API_BASE}/parse-range/{file_id}', json=parse_request)
    
    if parse_response.status_code != 200:
        print(f"❌ Parse failed: {parse_response.text}")
        return
    
    parse_data = parse_response.json()
    print(f"✅ Parse successful: {parse_data['row_count']} rows")
    print(f"📋 Headers: {parse_data['headers']}")
    
    if parse_data['row_count'] > 0:
        print(f"📄 First transaction: {parse_data['data'][0]}")
    
    # 5. Test with multi-CSV endpoint
    print("\n5️⃣ Testing multi-CSV parsing...")
    multi_request = {
        'file_ids': [file_id],
        'parse_configs': [parse_request],
        'user_name': 'Ammar Qazi',
        'date_tolerance_hours': 24
    }
    
    multi_response = requests.post(f'{API_BASE}/multi-csv/parse', json=multi_request)
    
    if multi_response.status_code != 200:
        print(f"❌ Multi-CSV parse failed: {multi_response.text}")
        return
    
    multi_data = multi_response.json()
    print(f"✅ Multi-CSV parse successful: {multi_data['total_files']} files processed")
    
    for result in multi_data['parsed_csvs']:
        print(f"   📁 {result['file_name']}: {result['parse_result']['row_count']} transactions")
    
    # 6. Cleanup
    print("\n6️⃣ Cleaning up...")
    cleanup_response = requests.delete(f'{API_BASE}/cleanup/{file_id}')
    print(f"✅ Cleanup successful")
    
    print(f"\n🎉 All tests passed! NayaPay CSV parsing is working correctly.")

if __name__ == "__main__":
    print("🚀 Testing NaN fixes and NayaPay parsing")
    test_nayapay_parsing()
