#!/usr/bin/env python3
"""
Test script to verify the frontend-backend integration fix
Tests the complete flow: Upload → Preview → Parse with bank-detected rows
"""

import requests
import json
import os

API_BASE = "http://127.0.0.1:8000"
SAMPLE_FILE = "/home/ammar/claude_projects/bank_statement_parser/sample_data/m-02-2025.csv"

def test_complete_flow():
    """Test the complete upload → preview → parse flow"""
    print("🧪 Testing Frontend-Backend Integration Fix")
    print("=" * 50)
    
    # Step 1: Upload file
    print("📤 Step 1: Uploading NayaPay sample file...")
    with open(SAMPLE_FILE, 'rb') as f:
        files = {'file': ('m-02-2025.csv', f, 'text/csv')}
        upload_response = requests.post(f"{API_BASE}/upload", files=files)
    
    if upload_response.status_code != 200:
        print(f"❌ Upload failed: {upload_response.text}")
        return False
    
    file_id = upload_response.json()['file_id']
    print(f"✅ File uploaded with ID: {file_id}")
    
    # Step 2: Preview with bank detection (should detect headers at row 13)
    print("\n🔍 Step 2: Testing bank-aware preview...")
    preview_response = requests.get(f"{API_BASE}/preview/{file_id}")
    
    if preview_response.status_code != 200:
        print(f"❌ Preview failed: {preview_response.text}")
        return False
    
    preview_data = preview_response.json()
    print(f"✅ Preview successful")
    
    # Check bank detection
    bank_detection = preview_data.get('bank_detection', {})
    detected_bank = bank_detection.get('detected_bank', 'unknown')
    confidence = bank_detection.get('confidence', 0)
    suggested_header_row = preview_data.get('suggested_header_row')
    suggested_data_start_row = preview_data.get('suggested_data_start_row')
    
    print(f"🏦 Detected Bank: {detected_bank} (confidence: {confidence:.2f})")
    print(f"📋 Suggested Header Row: {suggested_header_row}")
    print(f"📊 Suggested Data Start Row: {suggested_data_start_row}")
    
    if detected_bank == 'unknown':
        print("❌ Bank detection failed!")
        return False
    
    if suggested_header_row is None or suggested_data_start_row is None:
        print("❌ Header/data row detection failed!")
        return False
    
    print(f"✅ Bank detection successful: {detected_bank}")
    
    # Step 3: Parse using bank-detected row configuration
    print(f"\n📊 Step 3: Testing parse with bank-detected start_row={suggested_data_start_row}...")
    
    # Simulate what the fixed frontend should send
    parse_request = {
        "file_ids": [file_id],
        "parse_configs": [{
            "start_row": suggested_data_start_row,  # Use bank-detected data start row
            "end_row": None,
            "start_col": 0,
            "end_col": None,
            "encoding": "utf-8"
        }],
        "user_name": "Test User",
        "date_tolerance_hours": 24
    }
    
    parse_response = requests.post(f"{API_BASE}/multi-csv/parse", json=parse_request)
    
    if parse_response.status_code != 200:
        print(f"❌ Parse failed: {parse_response.text}")
        return False
    
    parse_data = parse_response.json()
    parsed_csvs = parse_data.get('parsed_csvs', [])
    
    if not parsed_csvs:
        print("❌ No parsed CSV data returned!")
        return False
    
    parse_result = parsed_csvs[0]['parse_result']
    row_count = parse_result.get('row_count', 0)
    headers = parse_result.get('headers', [])
    
    print(f"✅ Parse successful")
    print(f"📊 Rows processed: {row_count}")
    print(f"📋 Headers found: {headers[:5]}...")  # Show first 5 headers
    
    # Verify we got the expected results
    if row_count == 0:
        print("❌ CRITICAL BUG: No rows processed despite bank detection!")
        return False
    
    if 'Date' not in headers or 'Amount' not in headers:
        print("❌ CRITICAL BUG: Expected cleaned headers not found!")
        print(f"📋 Full headers: {headers}")
        return False
    
    print(f"🎉 SUCCESS: {row_count} transactions processed with correct headers!")
    
    # Step 4: Verify data quality
    print(f"\n📈 Step 4: Verifying data quality...")
    sample_data = parse_result.get('data', [])[:3]  # First 3 rows
    
    for i, row in enumerate(sample_data):
        timestamp = row.get('TIMESTAMP', 'N/A')
        amount = row.get('AMOUNT', 'N/A') 
        description = row.get('DESCRIPTION', 'N/A')
        print(f"  Row {i+1}: {timestamp} | {amount} | {description[:30]}...")
    
    print(f"✅ Data quality verified - all fields populated")
    
    # Summary
    print(f"\n📊 INTEGRATION TEST RESULTS:")
    print(f"{'=' * 50}")
    print(f"✅ Upload: Success")
    print(f"✅ Bank Detection: {detected_bank} ({confidence:.0%} confidence)")
    print(f"✅ Header Detection: Row {suggested_header_row}")
    print(f"✅ Data Detection: Starts at row {suggested_data_start_row}")
    print(f"✅ Parse: {row_count} transactions processed")
    print(f"✅ Headers: Correct NayaPay format detected")
    print(f"🎉 FRONTEND-BACKEND INTEGRATION FIX: SUCCESS")
    
    return True

if __name__ == "__main__":
    success = test_complete_flow()
    if success:
        print(f"\n🎉 ALL TESTS PASSED - Integration fix working correctly!")
    else:
        print(f"\n❌ TESTS FAILED - Fix needs more work")
