#!/usr/bin/env python3
"""
Test the corrected NayaPay files with our existing parsers
"""

import sys
import os
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from robust_csv_parser import RobustCSVParser
from enhanced_csv_parser import EnhancedCSVParser
import json

def test_nayapay_correct_file():
    print("🧪 Testing CORRECTED NayaPay File Structure")
    print("=" * 60)
    
    # File paths
    correct_file = "/home/ammar/claude_projects/bank_statement_parser/m022025correct.csv"
    march_file = "/home/ammar/claude_projects/bank_statement_parser/m032025.csv"
    
    # Initialize parsers
    robust_parser = RobustCSVParser()
    enhanced_parser = EnhancedCSVParser()
    
    for test_file, label in [(correct_file, "February Correct"), (march_file, "March File")]:
        print(f"\n=== Testing {label}: {os.path.basename(test_file)} ===")
        
        # Test 1: Detection
        print(f"1. Testing auto-detection...")
        detection = enhanced_parser.detect_data_range(test_file)
        
        if detection['success']:
            detected_row = detection['suggested_header_row']
            print(f"   ✅ Detected header row: {detected_row}")
        else:
            print(f"   ❌ Detection failed: {detection['error']}")
            continue
        
        # Test 2: Parse with detected range
        print(f"2. Testing parsing with detected range...")
        parse_result = enhanced_parser.parse_with_range(
            test_file,
            start_row=detected_row,
            end_row=None,
            start_col=0,
            end_col=5
        )
        
        if parse_result['success']:
            row_count = parse_result['row_count']
            headers = parse_result['headers']
            print(f"   ✅ Parse successful: {row_count} rows")
            print(f"   📋 Headers: {headers}")
            
            # Show first 3 transactions
            sample_data = parse_result['data'][:3]
            for i, row in enumerate(sample_data):
                print(f"   📄 Row {i+1}: {row.get('TIMESTAMP', 'N/A')} | {row.get('AMOUNT', 'N/A')} | {row.get('TYPE', 'N/A')}")
        else:
            print(f"   ❌ Parse failed: {parse_result['error']}")
            continue
        
        # Test 3: Transform to Cashew format
        print(f"3. Testing transformation to Cashew format...")
        
        # Load NayaPay template
        template_path = "/home/ammar/claude_projects/bank_statement_parser/templates/NayaPay_Enhanced_Template.json"
        try:
            with open(template_path, 'r') as f:
                template = json.load(f)
            
            column_mapping = template['column_mapping']
            categorization_rules = template['categorization_rules']
            default_category_rules = template['default_category_rules']
            bank_name = template['bank_name']
            
            transformed = enhanced_parser.transform_to_cashew(
                parse_result['data'],
                column_mapping,
                bank_name,
                categorization_rules,
                default_category_rules
            )
            
            print(f"   ✅ Transform successful: {len(transformed)} transactions")
            
            # Show sample transformed data
            for i, trans in enumerate(transformed[:3]):
                print(f"   💰 Transaction {i+1}: {trans['Date']} | {trans['Amount']} | {trans['Category']} | {trans['Title'][:50]}...")
            
            # Summary statistics
            categories = {}
            for trans in transformed:
                cat = trans['Category']
                categories[cat] = categories.get(cat, 0) + 1
            
            print(f"   📊 Categories found: {dict(categories)}")
            
        except Exception as e:
            print(f"   ❌ Transform failed: {str(e)}")
        
        print(f"   🎯 Test complete for {label}")

if __name__ == "__main__":
    test_nayapay_correct_file()
