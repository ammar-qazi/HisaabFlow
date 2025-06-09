#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_csv_parser import EnhancedCSVParser
import json

def test_updated_template():
    parser = EnhancedCSVParser()
    
    # Load the updated template
    template_path = "../templates/NayaPay_Enhanced_Template.json"
    with open(template_path, 'r') as f:
        template = json.load(f)
    
    # Test data including Surraiya Riaz transaction
    test_data = [
        {
            "TIMESTAMP": "02 Feb 2025 11:17 PM",
            "TYPE": "Raast Out",
            "DESCRIPTION": "Outgoing fund transfer to Surraiya Riaz (Asaan Ac) Meezan Bank-2660|Transaction ID 679fb6a0462d384309905d16",
            "AMOUNT": "-5,000", 
            "BALANCE": "872.4"
        },
        {
            "TIMESTAMP": "08 Feb 2025 1:42 AM",
            "TYPE": "Raast Out", 
            "DESCRIPTION": "Outgoing fund transfer to Muhammad Sajid easypaisa Bank-7717|Transaction ID 67a6704b0b9d0a676329e19a",
            "AMOUNT": "-1,500",
            "BALANCE": "20,572.40"
        },
        {
            "TIMESTAMP": "05 Feb 2025 9:17 AM",
            "TYPE": "Mobile Topup",
            "DESCRIPTION": "Mobile top-up purchased|Zong 03142919528 Nickname: Ammar Zong",
            "AMOUNT": "-2,000",
            "BALANCE": "48,872.40"
        }
    ]
    
    print("Testing updated template with Surraiya Riaz rule:")
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
            
            # Special checks
            if "Surraiya Riaz" in row['DESCRIPTION']:
                if result['Title'] == "Zunayyara Quran":
                    print("✅ CORRECTLY replaced title with 'Zunayyara Quran'")
                else:
                    print(f"❌ Expected 'Zunayyara Quran', got '{result['Title']}'")
            
            if row['TYPE'] == 'Mobile Topup':
                if result['Category'] == "Bills & Fees":
                    print("✅ CORRECTLY categorized as 'Bills & Fees'")
                else:
                    print(f"❌ Expected 'Bills & Fees', got '{result['Category']}'")
        else:
            print("❌ No result generated")

if __name__ == "__main__":
    test_updated_template()
