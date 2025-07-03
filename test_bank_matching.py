#!/usr/bin/env python3
"""
Test script to verify bank matching and account mapping fixes
"""
import requests
import json

# Test data mimicking the multi-CSV format with 3 banks
test_data = {
    "csv_data_list": [
        {
            "filename": "m-02-2025.csv",
            "bank_info": {
                "detected_bank": "nayapay",
                "bank_name": "nayapay",
                "confidence": 0.60
            },
            "data": [
                {
                    "amount": -5000,
                    "balance": 872.4,
                    "title": "Outgoing fund transfer to Surraiya Riaz (Asaan Ac) Meezan Bank-2660|Transaction ID 679fb6a0462d384309905d16",
                    "note": "Raast Out",
                    "date": "2025-02-02",
                    "Currency": "PKR"
                }
            ]
        },
        {
            "filename": "statement_23243482_EUR_2025-01-04_2025-06-02.csv",
            "bank_info": {
                "detected_bank": "wise",
                "bank_name": "wise",
                "confidence": 0.90
            },
            "data": [
                {
                    "amount": -155.0,
                    "title": "Card transaction of 155.00 EUR issued by Revolut**0540* Dublin",
                    "note": "",
                    "date": "2025-05-26",
                    "Currency": "EUR"
                }
            ]
        },
        {
            "filename": "11600006-00000000-96561234_2025-06-01_2025-06-30.csv",
            "bank_info": {
                "detected_bank": "Erste",
                "bank_name": "Erste", 
                "confidence": 1.00
            },
            "data": [
                {
                    "amount": -18063.0,
                    "title": "ING Bank N. V. Magyarországi Fióktelepe",
                    "note": "",
                    "date": "2025-06-09",
                    "Currency": "HUF"
                }
            ]
        }
    ]
}

def test_transformation():
    """Test the multi-CSV transformation endpoint"""
    url = "http://127.0.0.1:8000/api/v1/multi-csv/transform"
    
    try:
        print("🧪 Testing bank matching and account mapping fixes...")
        print(f"   Sending request to: {url}")
        print(f"   Test data: 3 CSVs (NayaPay, Wise EUR, Erste HUF)")
        
        response = requests.post(url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("\n✅ SUCCESS: Transformation completed")
                
                # Check account names
                transformed_data = result.get('transformed_data', [])
                print(f"\n📊 Transformed {len(transformed_data)} transactions:")
                
                for i, row in enumerate(transformed_data):
                    account = row.get('Account', 'Unknown')
                    title = row.get('Title', '')[:50] + '...' if len(row.get('Title', '')) > 50 else row.get('Title', '')
                    source_bank = row.get('_source_bank', 'Unknown')
                    print(f"   {i+1}. Bank: {source_bank}, Account: '{account}', Title: '{title}'")
                
                # Check if account names are correct
                expected_accounts = {
                    'nayapay': 'NayaPay',  # From nayapay.conf cashew_account
                    'wise': 'EURO Wise',   # From wise.conf account_mapping EUR -> EURO Wise  
                    'Erste': 'Forint Bank' # From Erste.conf cashew_account
                }
                
                print(f"\n🎯 Expected vs Actual Account Names:")
                for row in transformed_data:
                    source_bank = row.get('_source_bank', 'Unknown')
                    account = row.get('Account', 'Unknown')
                    expected = expected_accounts.get(source_bank, 'Unknown')
                    status = "✅" if account == expected else "❌"
                    print(f"   {status} {source_bank}: Expected '{expected}', Got '{account}'")
                
                return True
            else:
                print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_transformation()
    exit(0 if success else 1)