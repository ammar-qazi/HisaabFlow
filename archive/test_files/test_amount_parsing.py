#!/usr/bin/env python3
"""
Test the enhanced amount parsing fix
"""

import sys
sys.path.append('backend')

from enhanced_csv_parser import EnhancedCSVParser
import re

def test_amount_parsing():
    """Test the enhanced amount parsing"""
    parser = EnhancedCSVParser()
    
    # Test cases from actual NayaPay data
    test_amounts = [
        '"-5,000"',      # Quoted negative with comma
        '"+50,000"',     # Quoted positive with comma  
        '"+30,000"',     # Quoted positive with comma
        '-5000',         # Simple negative
        '50000',         # Simple positive
        '872.4',         # Decimal
        '',              # Empty
        'nan',           # NaN
        '(1,000)',       # Parentheses negative
        '$1,234.56',     # With currency symbol
    ]
    
    print("🧪 TESTING ENHANCED AMOUNT PARSING")
    print("=" * 50)
    
    for amount in test_amounts:
        parsed = parser._parse_amount(amount)
        print(f"'{amount}' → '{parsed}'")
    
    print("\n🧪 TESTING DATE PARSING")
    print("=" * 50)
    
    test_dates = [
        '02 Feb 2025 11:17 PM',
        '14 Feb 2025 3:19 PM', 
        '2025-02-14',
        '',
        'nan'
    ]
    
    for date in test_dates:
        parsed = parser._parse_date(date)
        print(f"'{date}' → '{parsed}'")

if __name__ == "__main__":
    test_amount_parsing()
