#!/usr/bin/env python3
"""
Debug script to test NayaPay template categorization rules
This script will help identify why template rules aren't being applied in multi-CSV mode
"""

import json
import sys
import os

# Add the backend directory to the path
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from enhanced_csv_parser import EnhancedCSVParser

def test_nayapay_categorization():
    """Test NayaPay categorization rules with sample data"""
    
    # Sample NayaPay transaction data (simulating parsed CSV)
    sample_data = [
        {
            "TIMESTAMP": "07 Feb 2025 1:47 PM",
            "TYPE": "Raast Out", 
            "DESCRIPTION": "Outgoing fund transfer to Usman Siddique\neasypaisa Bank-9171|Transaction ID 67a5c88bcf6694682c772ac0",
            "AMOUNT": "-400",
            "BALANCE": "23,472.40"
        },
        {
            "TIMESTAMP": "05 Feb 2025 9:17 AM",
            "TYPE": "Mobile Topup",
            "DESCRIPTION": "Mobile top-up purchased|Zong 03142919528\nNickname: Ammar Zong", 
            "AMOUNT": "-2,000",
            "BALANCE": "48,872.40"
        },
        {
            "TIMESTAMP": "09 Feb 2025 10:48 PM",
            "TYPE": "Raast Out",
            "DESCRIPTION": "Outgoing fund transfer to Ali Abbas Khan\nMCB Bank-4089|Transaction ID 67a8ea770b9d0a6763870e9b",
            "AMOUNT": "-13,000", 
            "BALANCE": "7,072.40"
        }
    ]
    
    # Load the actual NayaPay Enhanced Template
    template_path = "/home/ammar/claude_projects/bank_statement_parser/templates/NayaPay_Enhanced_Template.json"
    with open(template_path, 'r') as f:
        template_config = json.load(f)
    
    print("🔍 Template Configuration:")
    print(f"   Bank Name: {template_config.get('bank_name')}")
    print(f"   Column Mapping: {json.dumps(template_config.get('column_mapping'), indent=2)}")
    print(f"   Number of Categorization Rules: {len(template_config.get('categorization_rules', []))}")
    print(f"   Default Category Rules: {json.dumps(template_config.get('default_category_rules'), indent=2)}")
    print()
    
    # Test the transformation
    parser = EnhancedCSVParser()
    
    print("🧪 Testing transformation with categorization rules...")
    
    transformed_data = parser.transform_to_cashew(
        data=sample_data,
        column_mapping=template_config['column_mapping'],
        bank_name=template_config['bank_name'],
        categorization_rules=template_config['categorization_rules'],
        default_category_rules=template_config['default_category_rules']
    )
    
    print(f"✅ Transformation complete! {len(transformed_data)} transactions processed")
    print()
    
    # Analyze results
    print("📊 Transformation Results:")
    for i, transaction in enumerate(transformed_data):
        print(f"   Transaction {i+1}:")
        print(f"      Original TYPE: {sample_data[i]['TYPE']}")
        print(f"      Original AMOUNT: {sample_data[i]['AMOUNT']}")
        print(f"      → Category: {transaction['Category']}")
        print(f"      → Title: {transaction['Title']}")
        print(f"      → Amount: {transaction['Amount']}")
        print()
    
    # Test specific rule: Ride Hailing Services
    print("🎯 Testing Ride Hailing Rule (Raast Out with amount -400 to -2000):")
    ride_hailing_rule = None
    for rule in template_config['categorization_rules']:
        if rule['rule_name'] == 'Ride Hailing Services':
            ride_hailing_rule = rule
            break
    
    if ride_hailing_rule:
        print(f"   Rule found: {json.dumps(ride_hailing_rule, indent=2)}")
        
        # Check if the -400 transaction should match
        test_transaction = sample_data[0]  # -400 Raast Out
        print(f"   Testing transaction: TYPE={test_transaction['TYPE']}, AMOUNT={test_transaction['AMOUNT']}")
        
        # Manual condition check
        amount_val = float(test_transaction['AMOUNT'].replace(',', ''))
        type_match = 'raast out' in test_transaction['TYPE'].lower()
        amount_match = -2000 <= amount_val <= 0
        
        print(f"   → TYPE contains 'Raast Out': {type_match}")
        print(f"   → Amount ({amount_val}) in range [-2000, 0]: {amount_match}")
        print(f"   → Should categorize as Travel/Ride Hailing: {type_match and amount_match}")
        
        actual_result = transformed_data[0]
        print(f"   → Actual result: Category='{actual_result['Category']}', Title='{actual_result['Title']}'")
        
        if actual_result['Category'] == 'Travel' and actual_result['Title'] == 'Ride Hailing App':
            print("   ✅ Rule applied correctly!")
        else:
            print("   ❌ Rule NOT applied - there's an issue!")
    else:
        print("   ❌ Ride Hailing rule not found in template!")

def test_multi_csv_flow():
    """Simulate the multi-CSV transformation flow to identify the issue"""
    
    print("\n" + "="*60)
    print("🔄 Testing Multi-CSV Transformation Flow")
    print("="*60)
    
    # Simulate the frontend data structure as sent to backend
    csv_data_list = [
        {
            "file_name": "m032025.csv",
            "data": [
                {
                    "TIMESTAMP": "07 Feb 2025 1:47 PM",
                    "TYPE": "Raast Out",
                    "DESCRIPTION": "Outgoing fund transfer to Usman Siddique\neasypaisa Bank-9171|Transaction ID 67a5c88bcf6694682c772ac0", 
                    "AMOUNT": "-400",
                    "BALANCE": "23,472.40"
                }
            ],
            "headers": ["TIMESTAMP", "TYPE", "DESCRIPTION", "AMOUNT", "BALANCE"],
            "template_config": {
                # This is what gets sent from frontend - let's see if it's complete
                "column_mapping": {
                    "Date": "TIMESTAMP",
                    "Amount": "AMOUNT", 
                    "Category": "",
                    "Title": "DESCRIPTION",
                    "Note": "TYPE",
                    "Account": ""
                }
                # ❌ ISSUE: Missing categorization_rules, default_category_rules, bank_name!
            }
        }
    ]
    
    print("🔍 Analyzing CSV data structure sent to backend:")
    for i, csv_data in enumerate(csv_data_list):
        print(f"   CSV {i+1}: {csv_data['file_name']}")
        print(f"      Data rows: {len(csv_data['data'])}")
        print(f"      Headers: {csv_data['headers']}")
        print(f"      Template config keys: {list(csv_data['template_config'].keys())}")
        
        # Check if template config is complete
        template_config = csv_data['template_config']
        missing_keys = []
        if 'categorization_rules' not in template_config:
            missing_keys.append('categorization_rules')
        if 'default_category_rules' not in template_config:
            missing_keys.append('default_category_rules')
        if 'bank_name' not in template_config:
            missing_keys.append('bank_name')
            
        if missing_keys:
            print(f"      ❌ MISSING: {', '.join(missing_keys)}")
        else:
            print(f"      ✅ Template config complete")
    
    print()
    print("🔧 Simulating backend transformation...")
    
    parser = EnhancedCSVParser()
    
    for csv_data in csv_data_list:
        template_config = csv_data.get('template_config', {})
        column_mapping = template_config.get('column_mapping', {})
        bank_name = template_config.get('bank_name', csv_data.get('file_name', 'Unknown'))
        categorization_rules = template_config.get('categorization_rules', [])  # 🚨 This will be empty!
        default_category_rules = template_config.get('default_category_rules')
        
        print(f"   Processing {csv_data['file_name']}:")
        print(f"      Bank name: '{bank_name}'")
        print(f"      Categorization rules: {len(categorization_rules)} rules")
        print(f"      Default rules: {default_category_rules}")
        
        transformed = parser.transform_to_cashew(
            csv_data['data'],
            column_mapping,
            bank_name,
            categorization_rules,
            default_category_rules
        )
        
        print(f"      → Result: {len(transformed)} transactions")
        if transformed:
            result = transformed[0]
            print(f"      → Sample: Category='{result['Category']}', Title='{result['Title']}'")
            
            if result['Category'] == 'Travel':
                print("      ✅ Categorization rules applied!")
            else:
                print("      ❌ Categorization rules NOT applied!")

if __name__ == "__main__":
    print("🧪 NayaPay Template Categorization Debugging")
    print("=" * 50)
    
    # Test 1: Direct template application (should work)
    test_nayapay_categorization()
    
    # Test 2: Multi-CSV flow simulation (should reveal the issue)
    test_multi_csv_flow()
    
    print("\n🔍 DIAGNOSIS:")
    print("   The issue is likely in the frontend MultiCSVApp.js")
    print("   The template_config being sent to the backend is incomplete.")
    print("   It only contains column_mapping but missing:")
    print("   - categorization_rules")
    print("   - default_category_rules") 
    print("   - bank_name")
    print("\n💡 SOLUTION:")
    print("   Fix the frontend to send the complete template configuration")
    print("   including all categorization rules from the loaded template.")
