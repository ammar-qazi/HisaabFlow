#!/usr/bin/env python3

import sys
import os
import json

# Add the backend directory to the path
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from enhanced_csv_parser import EnhancedCSVParser

def comprehensive_nayapay_test():
    """Comprehensive test of NayaPay categorization with various transaction types"""
    
    print("🔍 COMPREHENSIVE NAYAPAY CATEGORIZATION TEST")
    print("=" * 60)
    
    # Initialize parser
    parser = EnhancedCSVParser()
    
    # Load the NayaPay Enhanced Template
    template_path = "/home/ammar/claude_projects/bank_statement_parser/templates/NayaPay_Enhanced_Template.json"
    with open(template_path, 'r') as f:
        template = json.load(f)
    
    print(f"📋 Template: {template['bank_name']} v{template['version']}")
    print(f"   Rules: {len(template.get('categorization_rules', []))}")
    print(f"   Description: {template['description']}")
    print()
    
    # Comprehensive test data covering all rule types
    test_transactions = [
        {
            'name': 'Surraiya Riaz Transaction',
            'data': {
                'TIMESTAMP': '05 Mar 2025 11:54 PM',
                'TYPE': 'Raast Out',
                'DESCRIPTION': 'Outgoing fund transfer to Surraiya Riaz (Asaan Ac)\nMeezan Bank-2660|Transaction ID 67c89de7380c9e24a2e7e92b',
                'AMOUNT': '-5,000',
                'BALANCE': '16,022.40'
            },
            'expected': {
                'Category': 'Transfer',
                'Title': 'Zunayyara Quran'
            }
        },
        {
            'name': 'Small Ride Hailing Transaction',
            'data': {
                'TIMESTAMP': '15 Mar 2025 02:30 PM',
                'TYPE': 'Raast Out',
                'DESCRIPTION': 'Outgoing fund transfer to Careem\nCareem-1234|Transaction ID abc123',
                'AMOUNT': '-400',
                'BALANCE': '20,622.40'
            },
            'expected': {
                'Category': 'Travel',
                'Title': 'Ride Hailing App'
            }
        },
        {
            'name': 'Medium Ride Hailing Transaction',
            'data': {
                'TIMESTAMP': '16 Mar 2025 08:15 AM',
                'TYPE': 'Raast Out',
                'DESCRIPTION': 'Outgoing fund transfer to Uber\nUber-5678|Transaction ID def456',
                'AMOUNT': '-1,200',
                'BALANCE': '19,422.40'
            },
            'expected': {
                'Category': 'Travel',
                'Title': 'Ride Hailing App'
            }
        },
        {
            'name': 'Large Transfer (NOT Ride Hailing)',
            'data': {
                'TIMESTAMP': '17 Mar 2025 10:00 AM',
                'TYPE': 'Raast Out',
                'DESCRIPTION': 'Outgoing fund transfer to Business Partner\nBank-9999|Transaction ID ghi789',
                'AMOUNT': '-15,000',
                'BALANCE': '4,422.40'
            },
            'expected': {
                'Category': 'Transfer',
                'Title': 'Transfer to Business Partner Bank-9999'  # Should get cleaned
            }
        },
        {
            'name': 'Incoming Transfer',
            'data': {
                'TIMESTAMP': '18 Mar 2025 11:00 AM',
                'TYPE': 'IBFT In',
                'DESCRIPTION': 'Incoming fund transfer from Client\nHBL-1111|Transaction ID jkl012',
                'AMOUNT': '+25,000',
                'BALANCE': '29,422.40'
            },
            'expected': {
                'Category': 'Transfer',
                'Title': 'Transfer from Client HBL-1111'  # Should get cleaned
            }
        },
        {
            'name': 'Peer to Peer Transfer',
            'data': {
                'TIMESTAMP': '19 Mar 2025 03:45 PM',
                'TYPE': 'Peer to Peer',
                'DESCRIPTION': 'Money sent to SARAH AHMED|(sarah@nayapay)\nNayaPay xxxx789',
                'AMOUNT': '-3,000',
                'BALANCE': '26,422.40'
            },
            'expected': {
                'Category': 'Transfer',
                'Title': 'Transfer to SARAH AHMED|(sarah@nayapay) NayaPay xxxx789'  # Should get cleaned
            }
        }
    ]
    
    # Transform all test data
    all_test_data = [tx['data'] for tx in test_transactions]
    
    transformed = parser.transform_to_cashew(
        all_test_data,
        template['column_mapping'],
        template['bank_name'],
        template.get('categorization_rules', []),
        template.get('default_category_rules'),
        template.get('account_mapping')
    )
    
    print("📊 TEST RESULTS:")
    print("=" * 40)
    
    all_passed = True
    
    for i, (test_case, result) in enumerate(zip(test_transactions, transformed)):
        test_name = test_case['name']
        expected = test_case['expected']
        
        print(f"\n{i+1}. {test_name}")
        print(f"   Original: TYPE={test_case['data']['TYPE']}, AMOUNT={test_case['data']['AMOUNT']}")
        print(f"   Result:   Category='{result['Category']}', Title='{result['Title']}'")
        
        # Check expectations
        category_match = result['Category'] == expected['Category']
        title_match = result['Title'] == expected['Title']
        
        if category_match and title_match:
            print(f"   ✅ PASS")
        else:
            print(f"   ❌ FAIL")
            if not category_match:
                print(f"      Expected Category: '{expected['Category']}', Got: '{result['Category']}'")
            if not title_match:
                print(f"      Expected Title: '{expected['Title']}', Got: '{result['Title']}'")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! NayaPay categorization is working correctly!")
    else:
        print("❌ Some tests failed. Check the rules and priorities.")
    
    print(f"\n📈 SUMMARY:")
    print(f"   Total transactions: {len(transformed)}")
    print(f"   Travel categories: {len([t for t in transformed if t['Category'] == 'Travel'])}")
    print(f"   Transfer categories: {len([t for t in transformed if t['Category'] == 'Transfer'])}")
    print(f"   Zunayyara Quran transactions: {len([t for t in transformed if t['Title'] == 'Zunayyara Quran'])}")
    print(f"   Ride Hailing transactions: {len([t for t in transformed if t['Title'] == 'Ride Hailing App'])}")

if __name__ == "__main__":
    comprehensive_nayapay_test()
