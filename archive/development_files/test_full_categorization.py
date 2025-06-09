#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_csv_parser import EnhancedCSVParser
import json

def test_full_categorization():
    parser = EnhancedCSVParser()
    
    # Load the template
    template_path = "../templates/NayaPay_Enhanced_Template.json"
    with open(template_path, 'r') as f:
        template = json.load(f)
    
    # Test data samples from the actual CSV
    test_data = [
        {
            "TIMESTAMP": "08 Feb 2025 1:42 AM",
            "TYPE": "Raast Out", 
            "DESCRIPTION": "Outgoing fund transfer to Muhammad Sajid easypaisa Bank-7717|Transaction ID 67a6704b0b9d0a676329e19a",
            "AMOUNT": "-1,500",
            "BALANCE": "20,572.40"
        },
        {
            "TIMESTAMP": "02 Feb 2025 11:17 PM",
            "TYPE": "Raast Out",
            "DESCRIPTION": "Outgoing fund transfer to Surraiya Riaz (Asaan Ac) Meezan Bank-2660|Transaction ID 679fb6a0462d384309905d16",
            "AMOUNT": "-5,000", 
            "BALANCE": "872.4"
        },
        {
            "TIMESTAMP": "07 Feb 2025 1:47 PM",
            "TYPE": "Raast Out",
            "DESCRIPTION": "Outgoing fund transfer to Usman Siddique easypaisa Bank-9171|Transaction ID 67a5c88bcf6694682c772ac0",
            "AMOUNT": "-400",
            "BALANCE": "23,472.40"
        },
        {
            "TIMESTAMP": "05 Feb 2025 9:17 AM",
            "TYPE": "Mobile Topup",
            "DESCRIPTION": "Mobile top-up purchased|Zong 03142919528 Nickname: Ammar Zong",
            "AMOUNT": "-2,000",
            "BALANCE": "48,872.40"
        },
        {
            "TIMESTAMP": "03 Feb 2025 12:15 PM",
            "TYPE": "IBFT In",
            "DESCRIPTION": "Incoming fund transfer from Ammar Qazi Bank Alfalah-2050|Transaction ID 017707",
            "AMOUNT": "+50,000",
            "BALANCE": "50,872.40"
        }
    ]
    
    print("Testing full categorization pipeline:")
    print("="*60)
    
    for i, row in enumerate(test_data, 1):
        print(f"\nTest {i}:")
        print(f"Original: {row['TYPE']} | {row['AMOUNT']} | {row['DESCRIPTION'][:50]}...")
        
        # Transform to cashew format
        cashew_result = parser.transform_to_cashew(
            [row], 
            template['column_mapping'],
            template['bank_name'],
            template['categorization_rules'],
            template['default_category_rules']
        )
        
        if cashew_result:
            result = cashew_result[0]
            print(f"Result: {result['Category']} | {result['Amount']} | {result['Title']}")
            
            # Check if ride hailing was categorized correctly
            if row['TYPE'] == 'Raast Out':
                amount_float = float(result['Amount'])
                if -2000 <= amount_float <= 0:
                    expected_category = "Travel"
                    if result['Category'] == expected_category:
                        print("✅ CORRECTLY categorized as Travel (Ride Hailing)")
                    else:
                        print(f"❌ INCORRECTLY categorized as {result['Category']}, expected {expected_category}")
                else:
                    print(f"✅ Amount {amount_float} outside ride hailing range, categorized as {result['Category']}")
        else:
            print("❌ No result generated")

if __name__ == "__main__":
    test_full_categorization()
