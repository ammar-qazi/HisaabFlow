#!/usr/bin/env python3

import sys
import os
import json
import requests

def test_api_transformation():
    """Test the API transformation with m022025.csv data"""
    
    print("🔍 Testing API Transformation with Real Data")
    print("=" * 60)
    
    API_BASE = 'http://127.0.0.1:8000'
    
    # Test if API is running
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"✅ API is running: {response.json()}")
    except Exception as e:
        print(f"❌ API not running: {e}")
        print("💡 Start the API with: ./start_app.sh")
        return
    
    # Load the template from API
    try:
        response = requests.get(f"{API_BASE}/template/NayaPay_Enhanced_Template")
        if response.status_code == 200:
            template_data = response.json()
            config = template_data['config']
            print(f"✅ Template loaded from API:")
            print(f"   Bank: {config['bank_name']}")
            print(f"   Rules: {len(config.get('categorization_rules', []))}")
            print(f"   Version: {config.get('version', 'Unknown')}")
            
            # Check key rules
            rule_names = [rule['rule_name'] for rule in config.get('categorization_rules', [])]
            print(f"   Rule names: {rule_names[:3]}...")  # First 3 rules
            
        else:
            print(f"❌ Failed to load template: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Template load error: {e}")
        return
    
    # Test transformation with sample data
    test_data = [
        {
            'TIMESTAMP': '07 Feb 2025 1:47 PM',
            'TYPE': 'Raast Out', 
            'DESCRIPTION': 'Outgoing fund transfer to Usman Siddique\neasypaisa Bank-9171|Transaction ID 67a5c88bcf6694682c772ac0',
            'AMOUNT': '-400',
            'BALANCE': '23,472.40'
        },
        {
            'TIMESTAMP': '02 Feb 2025 11:17 PM',
            'TYPE': 'Raast Out',
            'DESCRIPTION': 'Outgoing fund transfer to Surraiya Riaz (Asaan Ac)\nMeezan Bank-2660|Transaction ID 679fb6a0462d384309905d16',
            'AMOUNT': '-5,000',
            'BALANCE': '872.4'
        },
        {
            'TIMESTAMP': '05 Feb 2025 9:17 AM',
            'TYPE': 'Mobile Topup',
            'DESCRIPTION': 'Mobile top-up purchased|Zong 03142919528\nNickname: Ammar Zong',
            'AMOUNT': '-2,000',
            'BALANCE': '48,872.40'
        }
    ]
    
    # Create transformation request
    transform_request = {
        'data': test_data,
        'column_mapping': config['column_mapping'],
        'bank_name': config['bank_name'],
        'categorization_rules': config.get('categorization_rules', []),
        'default_category_rules': config.get('default_category_rules'),
        'account_mapping': config.get('account_mapping')
    }
    
    print(f"\n🔄 Testing transformation with {len(test_data)} transactions...")
    print(f"   Column mapping: {config['column_mapping']}")
    print(f"   Categorization rules count: {len(config.get('categorization_rules', []))}")
    print(f"   First rule: {config.get('categorization_rules', [{}])[0].get('rule_name', 'None')}")
    
    try:
        response = requests.post(f"{API_BASE}/transform", json=transform_request)
        if response.status_code == 200:
            result = response.json()
            transformed_data = result['data']
            
            print(f"\n✅ Transformation successful: {len(transformed_data)} transactions")
            
            for i, transaction in enumerate(transformed_data):
                original = test_data[i]
                print(f"\n{i+1}. {original['TYPE']} - {original['AMOUNT']}")
                print(f"   Category: '{transaction['Category']}'")
                print(f"   Title: '{transaction['Title']}'")
                
                # Check expectations
                if original['AMOUNT'] == '-400' and original['TYPE'] == 'Raast Out':
                    expected = "Travel/Ride Hailing App"
                    actual = f"{transaction['Category']}/{transaction['Title']}"
                    status = "✅ PASS" if transaction['Category'] == 'Travel' and transaction['Title'] == 'Ride Hailing App' else "❌ FAIL"
                    print(f"   Expected: {expected}")
                    print(f"   Actual: {actual}")
                    print(f"   Status: {status}")
                
                if 'Surraiya Riaz' in original['DESCRIPTION']:
                    expected = "Zunayyara Quran"
                    actual = transaction['Title']
                    status = "✅ PASS" if actual == expected else "❌ FAIL"
                    print(f"   Expected Title: {expected}")
                    print(f"   Actual Title: {actual}")
                    print(f"   Status: {status}")
                
                if original['TYPE'] == 'Mobile Topup':
                    expected = "Bills & Fees"
                    actual = transaction['Category']
                    status = "✅ PASS" if actual == expected else "❌ FAIL"
                    print(f"   Expected Category: {expected}")
                    print(f"   Actual Category: {actual}")
                    print(f"   Status: {status}")
        else:
            print(f"❌ Transformation failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Transformation error: {e}")

if __name__ == "__main__":
    test_api_transformation()
