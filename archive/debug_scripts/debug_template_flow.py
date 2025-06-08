#!/usr/bin/env python3

import sys
import os
import json

# Add the backend directory to the path
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from enhanced_csv_parser import EnhancedCSVParser

def debug_template_loading():
    """Debug the template loading process to match what frontend does"""
    
    print("🔍 Debugging Template Loading Process")
    print("=" * 60)
    
    # Initialize parser
    parser = EnhancedCSVParser()
    
    # Load template like frontend does
    template_path = "/home/ammar/claude_projects/bank_statement_parser/templates/NayaPay_Enhanced_Template.json"
    with open(template_path, 'r') as f:
        template_config = json.load(f)
    
    print(f"📋 Loaded template NayaPay_Enhanced_Template:")
    print(f"   - Bank name: {template_config['bank_name']}")
    print(f"   - Categorization rules: {len(template_config.get('categorization_rules', []))}")
    print(f"   - Default category rules: {bool(template_config.get('default_category_rules'))}")
    print()
    
    # Show the first few rules
    print("🔍 First 3 categorization rules:")
    for i, rule in enumerate(template_config.get('categorization_rules', [])[:3]):
        print(f"   {i+1}. {rule['rule_name']} (priority: {rule.get('priority', 'N/A')})")
    print()
    
    # Sample data from m022025.csv 
    sample_data = [
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
    
    # Create CSV data like frontend does
    csv_data = {
        'file_name': 'm022025.csv',
        'data': sample_data,
        'headers': ['TIMESTAMP', 'TYPE', 'DESCRIPTION', 'AMOUNT', 'BALANCE'],
        'template_config': template_config  # Complete template config
    }
    
    print("🔧 CSV data template_config keys:")
    print(f"   {list(csv_data['template_config'].keys())}")
    print()
    
    # Mimic backend processing
    template_config_from_csv = csv_data.get('template_config', {})
    column_mapping = template_config_from_csv.get('column_mapping', {})
    bank_name = template_config_from_csv.get('bank_name', 'Unknown')
    categorization_rules = template_config_from_csv.get('categorization_rules', [])
    default_category_rules = template_config_from_csv.get('default_category_rules')
    account_mapping = template_config_from_csv.get('account_mapping')
    
    print("🔄 Backend processing simulation:")
    print(f"   Column mapping: {column_mapping}")
    print(f"   Bank name: {bank_name}")
    print(f"   Categorization rules count: {len(categorization_rules)}")
    print(f"   Default category rules: {default_category_rules}")
    print(f"   Account mapping: {account_mapping}")
    print()
    
    # Check if rules are actually there
    if len(categorization_rules) == 0:
        print("❌ PROBLEM: No categorization rules found!")
        print("   This explains why default categorization is being used.")
        return
    
    print("✅ Categorization rules found. Testing transformation...")
    
    # Transform data
    transformed = parser.transform_to_cashew(
        sample_data,
        column_mapping,
        bank_name,
        categorization_rules,
        default_category_rules,
        account_mapping
    )
    
    print(f"\n📊 Transformation Results:")
    for i, result in enumerate(transformed):
        original = sample_data[i]
        print(f"\n{i+1}. {original['TYPE']} - {original['AMOUNT']}")
        print(f"   Category: '{result['Category']}'")
        print(f"   Title: '{result['Title']}'")
        
        # Check specific cases
        if original['AMOUNT'] == '-400':
            expected = "Travel/Ride Hailing App"
            actual = f"{result['Category']}/{result['Title']}"
            status = "✅ PASS" if result['Category'] == 'Travel' and result['Title'] == 'Ride Hailing App' else "❌ FAIL"
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}")
            print(f"   Status: {status}")
        
        if 'Surraiya Riaz' in original['DESCRIPTION']:
            expected = "Zunayyara Quran"
            actual = result['Title']
            status = "✅ PASS" if actual == expected else "❌ FAIL"
            print(f"   Expected Title: {expected}")
            print(f"   Actual Title: {actual}")
            print(f"   Status: {status}")
        
        if original['TYPE'] == 'Mobile Topup':
            expected = "Bills & Fees"
            actual = result['Category']
            status = "✅ PASS" if actual == expected else "❌ FAIL"
            print(f"   Expected Category: {expected}")
            print(f"   Actual Category: {actual}")
            print(f"   Status: {status}")

if __name__ == "__main__":
    debug_template_loading()
