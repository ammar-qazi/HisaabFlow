#!/usr/bin/env python3
"""
Test Transferwise parsing API endpoint
"""

import requests
import json
import sys

def test_transferwise_api():
    print("🧪 Testing Transferwise API Parsing")
    print("=" * 40)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test if backend is running
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Backend is running: {response.json()}")
    except Exception as e:
        print(f"❌ Backend not running: {e}")
        return False
    
    # Upload the Transferwise sample file
    try:
        with open("transferwise_sample.csv", "rb") as f:
            files = {"file": ("transferwise_sample.csv", f, "text/csv")}
            response = requests.post(f"{base_url}/upload", files=files)
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return False
        
        upload_result = response.json()
        file_id = upload_result["file_id"]
        print(f"✅ File uploaded: {file_id}")
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False
    
    # Test parsing
    try:
        parse_data = {
            "start_row": 0,
            "end_row": None,
            "start_col": 0,
            "end_col": None,
            "encoding": "utf-8"
        }
        
        response = requests.post(f"{base_url}/parse-range/{file_id}", json=parse_data)
        
        if response.status_code != 200:
            print(f"❌ Parse failed: {response.status_code} - {response.text}")
            return False
        
        parse_result = response.json()
        print(f"✅ Parse successful: {parse_result.get('row_count', 0)} rows")
        print(f"📋 Headers: {parse_result.get('headers', [])[:5]}...")
        
        # Check if data is serializable
        if parse_result.get('data'):
            sample_row = parse_result['data'][0]
            print(f"📄 Sample row keys: {list(sample_row.keys())[:5]}...")
            print(f"📄 Sample values: {list(sample_row.values())[:3]}...")
            
            # Test JSON serialization
            json_str = json.dumps(sample_row)
            print("✅ JSON serialization: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Parse error: {e}")
        return False

if __name__ == "__main__":
    success = test_transferwise_api()
    sys.exit(0 if success else 1)
