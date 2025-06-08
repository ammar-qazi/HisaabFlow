#!/usr/bin/env python3

import sys
import os
import json

# Add the backend directory to the path
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from enhanced_csv_parser import EnhancedCSVParser

def test_nayapay_categorization():
    """Test NayaPay categorization with real data"""
    
    print("🔍 Testing NayaPay Categorization Issues")
    print("=" * 50)
    
    # Initialize parser
    parser = EnhancedCSVParser()
    
    # Load the NayaPay Enhanced Template
    template_path = "/home/ammar/claude_projects/bank_statement_parser/templates/NayaPay_Enhanced_Template.json"
    with open(template_path, 'r') as f:
        template = json.load(f)
    
    print("📋 Template loaded:")
    print(f"   - Bank: {template['bank_name']}")
    print(f"   - Categorization rules: {len(template.get('categorization_rules', []))}")
    print(f"   - Column mapping: {template['column_mapping']}")
    print()
    
    # Test data from the actual CSV
    test_data = [
        {
            'TIMESTAMP': '05 Mar 2025 11:54 PM',
            'TYPE': 'Raast Out',
            'DESCRIPTION': 'Outgoing fund transfer to Surraiya Riaz (Asaan Ac)\nMeezan Bank-2660|Transaction ID 67c89de7380c9e24a2e7e92b',
            'AMOUNT': '-5,000',
            'BALANCE': '16,022.40'
        },
        {
            'TIMESTAMP': '09 Mar 2025 03:14 PM',
            'TYPE': 'IBFT In', 
            'DESCRIPTION': 'Incoming fund transfer from Ammar Qazi\nBank Alfalah-2050|Transaction ID 901341',
            'AMOUNT': '+50,000',
            'BALANCE': '51,022.40'
        },
        {
            'TIMESTAMP': '31 Mar 2025 11:05 PM',
            'TYPE': 'Peer to Peer',
            'DESCRIPTION': 'Money sent to HUMNA QAZI|(humnaqazi@nayapay)\nNayaPay xxxx513',
            'AMOUNT': '-2,500',
            'BALANCE': '40,691.40'
        },
        # Add a small ride-hailing type transaction
        {
            'TIMESTAMP': '15 Mar 2025 02:30 PM',
            'TYPE': 'Raast Out',
            'DESCRIPTION': 'Outgoing fund transfer to Careem\nCareem-1234|Transaction ID abc123',
            'AMOUNT': '-400',
            'BALANCE': '20,622.40'
        }
    ]
    
    # Transform the data
    print("🔄 Transforming test data...")
    transformed = parser.transform_to_cashew(
        test_data,
        template['column_mapping'],
        template['bank_name'],
        template.get('categorization_rules', []),
        template.get('default_category_rules'),
        template.get('account_mapping')
    )
    
    print("✅ Transformation complete!")
    print()
    
    # Analyze results
    print("📊 RESULTS ANALYSIS:")
    print("-" * 30)
    
    for i, result in enumerate(transformed):
        print(f"Transaction {i+1}:")
        print(f"   Original: TYPE={test_data[i]['TYPE']}, AMOUNT={test_data[i]['AMOUNT']}")
        print(f"   Result: Category='{result['Category']}', Title='{result['Title']}'")
        print(f"   Amount: {result['Amount']}")
        
        # Check specific rules
        if test_data[i]['TYPE'] == 'Raast Out' and float(result['Amount']) == -400:
            expected_category = "Travel"
            expected_title = "Ride Hailing App"
            if result['Category'] == expected_category and result['Title'] == expected_title:
                print(f"   ✅ Ride Hailing rule applied correctly!")
            else:
                print(f"   ❌ Ride Hailing rule FAILED! Expected Category='{expected_category}', Title='{expected_title}'")
        
        if 'Surraiya Riaz' in test_data[i]['DESCRIPTION']:
            expected_title = "Zunayyara Quran"
            if result['Title'] == expected_title:
                print(f"   ✅ Surraiya Riaz rule applied correctly!")
            else:
                print(f"   ❌ Surraiya Riaz rule FAILED! Expected Title='{expected_title}'")
        
        print()
    
    # Test specific rule conditions
    print("🔍 RULE CONDITION TESTING:")
    print("-" * 30)
    
    # Test ride hailing rule specifically
    ride_hailing_rule = None
    for rule in template['categorization_rules']:
        if rule['rule_name'] == 'Ride Hailing Services':
            ride_hailing_rule = rule
            break
    
    if ride_hailing_rule:
        print("🚗 Testing Ride Hailing Rule:")
        print(f"   Rule: {ride_hailing_rule}")
        
        test_row = {
            'TYPE': 'Raast Out',
            'AMOUNT': '-400'
        }
        
        condition_met = parser._check_rule_conditions(test_row, ride_hailing_rule['conditions'])
        print(f"   Condition met for test row: {condition_met}")
        
        # Test each condition individually
        if 'and' in ride_hailing_rule['conditions']:
            for i, cond in enumerate(ride_hailing_rule['conditions']['and']):
                individual_result = parser._check_single_condition(test_row, cond)
                print(f"   Condition {i+1}: {cond} -> {individual_result}")
    
    print("\n🏁 Test Complete!")

if __name__ == "__main__":
    test_nayapay_categorization()
