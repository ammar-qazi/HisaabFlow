#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_csv_parser import EnhancedCSVParser
import json

def test_amount_parsing():
    parser = EnhancedCSVParser()
    
    # Test the _parse_amount method directly
    test_amounts = ["-1,500", "-5,000", "-400", "-750", "50,000", "+30,000"]
    
    print("Testing _parse_amount method:")
    for amount in test_amounts:
        cleaned = parser._parse_amount(amount)
        print(f"'{amount}' -> '{cleaned}' -> {float(cleaned)}")
    
    print("\n" + "="*50 + "\n")
    
    # Test condition checking with sample data
    sample_row = {
        "TIMESTAMP": "08 Feb 2025 1:42 AM",
        "TYPE": "Raast Out", 
        "DESCRIPTION": "Outgoing fund transfer to Muhammad Sajid\neasypaisa Bank-7717|Transaction ID 67a6704b0b9d0a676329e19a",
        "AMOUNT": "-1,500",
        "BALANCE": "20,572.40"
    }
    
    # Test the ride hailing condition
    ride_condition = {
        "and": [
            {
                "field": "TYPE",
                "operator": "contains", 
                "value": "Raast Out",
                "case_sensitive": False
            },
            {
                "field": "AMOUNT",
                "operator": "range",
                "min": -2000,
                "max": 0
            }
        ]
    }
    
    print("Testing condition matching:")
    print(f"Sample row: {sample_row}")
    print(f"Condition: {ride_condition}")
    
    # Test individual conditions
    type_condition = ride_condition["and"][0]
    amount_condition = ride_condition["and"][1]
    
    type_match = parser._check_single_condition(sample_row, type_condition)
    amount_match = parser._check_single_condition(sample_row, amount_condition)
    overall_match = parser._check_rule_conditions(sample_row, ride_condition)
    
    print(f"Type condition matches: {type_match}")
    print(f"Amount condition matches: {amount_match}")
    print(f"Overall condition matches: {overall_match}")
    
    # Test the amount parsing specifically for the condition
    amount_str = sample_row["AMOUNT"]
    cleaned_amount = parser._parse_amount(amount_str)
    amount_float = float(cleaned_amount)
    in_range = -2000 <= amount_float <= 0
    
    print(f"\nAmount parsing details:")
    print(f"Original: '{amount_str}'")
    print(f"Cleaned: '{cleaned_amount}'")
    print(f"Float: {amount_float}")
    print(f"In range [-2000, 0]: {in_range}")

if __name__ == "__main__":
    test_amount_parsing()
