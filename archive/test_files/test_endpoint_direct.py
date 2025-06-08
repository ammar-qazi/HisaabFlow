#!/usr/bin/env python3
"""
Test the multi-CSV endpoint directly
"""

import requests
import json

def test_multi_csv_endpoint():
    print("🧪 Testing Multi-CSV endpoint directly")
    print("=" * 50)
    
    # Test basic connectivity first
    try:
        response = requests.get("http://127.0.0.1:8000/")
        print(f"✅ Server connectivity: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Server not reachable: {e}")
        return
    
    # Test with empty request (should give validation error)
    try:
        print("\n📋 Testing with empty request...")
        response = requests.post("http://127.0.0.1:8000/multi-csv/parse", 
                                json={
                                    "file_ids": [],
                                    "parse_configs": [],
                                    "user_name": "Ammar Qazi",
                                    "date_tolerance_hours": 24
                                })
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 400:
            print("✅ Expected validation error received")
        else:
            print("⚠️ Unexpected response for empty request")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_multi_csv_endpoint()
