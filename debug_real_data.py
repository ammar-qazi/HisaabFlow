#!/usr/bin/env python3
"""
Debug script with REAL data patterns from the screenshot
"""

import json
import sys
import os

# Add the backend path
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from enhanced_csv_parser import EnhancedCSVParser

def main():
    print("🔍 Debug: Real NayaPay Data Patterns")
    print("=" * 60)
    
    # Load the enhanced template
    template_path = "/home/ammar/claude_projects/bank_statement_parser/templates/NayaPay_Enhanced_Template.json"
    
    with open(template_path, 'r') as f:
        template = json.load(f)
    
    # REAL data patterns from the screenshot
    test_transactions = [
        # Mobile top-ups - should extract contact names
        {
            "TIMESTAMP": "2025-02-05 09:17:00",
            "AMOUNT": "-2000.0",
            "TYPE": "Raast Out", 
            "DESCRIPTION": "Mobile top-up purchased|Zong 030...|Nickname: John Doe|Transaction ID 123"
        },
        {
            "TIMESTAMP": "2025-02-05 09:19:00",
            "AMOUNT": "-2000.0", 
            "TYPE": "Raast Out",
            "DESCRIPTION": "Mobile top-up purchased|Jazz 030...|Nickname: Sarah Khan|Transaction ID 456"
        },
        
        # Ride-hailing payments - should be Travel category
        {
            "TIMESTAMP": "2025-02-07 13:47:00",
            "AMOUNT": "-400.0",
            "TYPE": "Raast Out", 
            "DESCRIPTION": "Transfer to Usman Siddique easypaisa|Transaction ID ABC123"
        },
        {
            "TIMESTAMP": "2025-02-07 17:52:00", 
            "AMOUNT": "-750.0",
            "TYPE": "Raast Out",
            "DESCRIPTION": "Transfer to Muhammad Riafat easypaisa Bank-3892"
        },
        {
            "TIMESTAMP": "2025-02-07 19:15:00",
            "AMOUNT": "-650.0", 
            "TYPE": "Raast Out",
            "DESCRIPTION": "Transfer to Ghulam Asghar easypaisa Bank-9944"
        },
        
        # Large transfers - should remain as Transfer
        {
            "TIMESTAMP": "2025-02-09 22:48:00",
            "AMOUNT": "-13000.0",
            "TYPE": "Raast Out",
            "DESCRIPTION": "Transfer to Ali Abbas Khan MCB Bank-4089"
        }
    ]
    
    parser = EnhancedCSVParser()
    
    print("\n🧪 Testing with REAL data patterns:")
    print("-" * 50)
    
    for i, transaction in enumerate(test_transactions):
        print(f"\n📊 Transaction {i+1}:")
        print(f"   Amount: {transaction['AMOUNT']}")
        print(f"   Type: {transaction['TYPE']}")
        print(f"   Description: {transaction['DESCRIPTION'][:60]}...")
        
        # Create a cashew row template
        cashew_row = {
            'Date': transaction['TIMESTAMP'],
            'Amount': transaction['AMOUNT'],
            'Category': '',
            'Title': '',
            'Note': transaction['TYPE'],
            'Account': 'NayaPay'
        }
        
        # Apply categorization rules
        result = parser._apply_categorization_rules(
            cashew_row, 
            transaction, 
            template['categorization_rules'],
            template['default_category_rules']
        )
        
        print(f"   ✅ Result Category: {result['Category']}")
        print(f"   ✅ Result Title: {result['Title']}")
        
        # Expected results check
        amount = float(transaction['AMOUNT'])
        if "mobile top-up" in transaction['DESCRIPTION'].lower():
            expected_category = "Bills & Fees"
            expected_title_contains = "Mobile charge"
            print(f"   📋 Expected: {expected_category} / Mobile charge for [contact]")
        elif -2000 <= amount <= -100 and "transfer to" in transaction['DESCRIPTION'].lower():
            expected_category = "Travel" 
            expected_title = "Ride Hailing App"
            print(f"   📋 Expected: {expected_category} / {expected_title}")
        elif amount < -2000:
            expected_category = "Transfer"
            print(f"   📋 Expected: {expected_category} / [cleaned description]")
        
        # Check if result matches expectation
        if "mobile top-up" in transaction['DESCRIPTION'].lower():
            if result['Category'] == "Bills & Fees" and "Mobile charge" in result['Title']:
                print("   ✅ CORRECT!")
            else:
                print("   ❌ INCORRECT - should be Bills & Fees / Mobile charge for [contact]")
        elif -2000 <= amount <= -100 and "transfer to" in transaction['DESCRIPTION'].lower():
            if result['Category'] == "Travel" and result['Title'] == "Ride Hailing App":
                print("   ✅ CORRECT!")
            else:
                print("   ❌ INCORRECT - should be Travel / Ride Hailing App")

if __name__ == "__main__":
    main()
