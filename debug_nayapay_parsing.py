#!/usr/bin/env python3
"""
Debug script to identify NayaPay parsing issues
"""

import json
import math

def debug_nayapay_csv():
    """Debug the actual structure of NayaPay CSV"""
    
    # Read the CSV manually line by line
    try:
        with open('/home/ammar/claude_projects/bank_statement_parser/nayapay_statement.csv', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("🔍 NayaPay CSV Structure Analysis:")
        print("=" * 60)
        
        for i, line in enumerate(lines[:20]):  # First 20 lines
            cleaned_line = line.strip()
            if cleaned_line:
                print(f"Row {i:2d}: {cleaned_line[:100]}{'...' if len(cleaned_line) > 100 else ''}")
            else:
                print(f"Row {i:2d}: [EMPTY LINE]")
        
        # Look for the actual header row
        print(f"\n🎯 Looking for header row with keywords...")
        header_keywords = ['timestamp', 'type', 'description', 'amount', 'balance']
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in header_keywords):
                print(f"📍 Potential header at row {i}: {line.strip()}")
                
                # Check what's on the next few rows
                print(f"📋 Next 3 data rows:")
                for j in range(1, 4):
                    if i + j < len(lines):
                        data_line = lines[i + j].strip()
                        if data_line:
                            print(f"  Row {i+j}: {data_line[:150]}{'...' if len(data_line) > 150 else ''}")
                break
        
        print(f"\n📊 Total rows in file: {len(lines)}")
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")

def debug_template_config():
    """Check the current template configuration"""
    
    print(f"\n📋 Template Configuration Analysis:")
    print("=" * 60)
    
    template_files = [
        '/home/ammar/claude_projects/bank_statement_parser/templates/NayaPay_Enhanced_Template.json',
        '/home/ammar/claude_projects/bank_statement_parser/templates/NayaPay_Template.json'
    ]
    
    for template_file in template_files:
        try:
            with open(template_file, 'r') as f:
                config = json.load(f)
            
            print(f"\n🗂️ {template_file.split('/')[-1]}:")
            print(f"   start_row: {config.get('start_row', 'Not set')}")
            print(f"   end_row: {config.get('end_row', 'Not set')}")
            print(f"   start_col: {config.get('start_col', 'Not set')}")
            print(f"   end_col: {config.get('end_col', 'Not set')}")
            print(f"   column_mapping: {config.get('column_mapping', {})}")
            
        except Exception as e:
            print(f"❌ Error reading {template_file}: {e}")

def test_manual_parsing():
    """Test manual parsing with different start rows"""
    
    print(f"\n🧪 Manual Parsing Test:")
    print("=" * 60)
    
    try:
        with open('/home/ammar/claude_projects/bank_statement_parser/nayapay_statement.csv', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Test different start rows
        test_rows = [11, 12, 13, 14]
        
        for start_row in test_rows:
            print(f"\n🎯 Testing start_row = {start_row}:")
            
            if start_row < len(lines):
                # Get headers
                header_line = lines[start_row].strip()
                print(f"   Headers: {header_line}")
                
                # Parse headers
                headers = [h.strip() for h in header_line.split(',')]
                print(f"   Parsed headers: {headers}")
                
                # Check first few data rows
                data_count = 0
                for i in range(start_row + 1, min(start_row + 6, len(lines))):
                    data_line = lines[i].strip()
                    if data_line and ',' in data_line:
                        data_parts = data_line.split(',')
                        if len(data_parts) >= 4:  # At least Date, Type, Description, Amount
                            data_count += 1
                            print(f"   Data row {i}: {data_line[:100]}{'...' if len(data_line) > 100 else ''}")
                
                print(f"   ✅ Found {data_count} valid data rows")
            else:
                print(f"   ❌ start_row {start_row} exceeds file length ({len(lines)} rows)")

def check_nan_issues():
    """Check for potential NaN issues in the data"""
    
    print(f"\n🔬 NaN Value Analysis:")
    print("=" * 60)
    
    try:
        with open('/home/ammar/claude_projects/bank_statement_parser/nayapay_statement.csv', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check row 13 and beyond for amount values
        start_row = 13
        if start_row < len(lines):
            header_line = lines[start_row].strip()
            headers = [h.strip() for h in header_line.split(',')]
            
            print(f"Headers: {headers}")
            
            # Find amount column
            amount_col = None
            for i, header in enumerate(headers):
                if 'amount' in header.lower():
                    amount_col = i
                    print(f"Amount column found at index {i}: {header}")
                    break
            
            if amount_col is not None:
                print(f"\n💰 Checking amount values:")
                for i in range(start_row + 1, min(start_row + 11, len(lines))):
                    data_line = lines[i].strip()
                    if data_line:
                        parts = data_line.split(',')
                        if len(parts) > amount_col:
                            amount_str = parts[amount_col].strip()
                            print(f"   Row {i}: '{amount_str}'")
                            
                            # Try to parse as float
                            try:
                                # Clean the amount string
                                cleaned = amount_str.replace(',', '').replace('"', '').strip()
                                if cleaned.startswith('-'):
                                    cleaned = cleaned[1:]
                                    sign = -1
                                else:
                                    sign = 1
                                
                                if cleaned:
                                    amount_float = float(cleaned) * sign
                                    if math.isnan(amount_float):
                                        print(f"     ⚠️ NaN detected!")
                                    else:
                                        print(f"     ✅ Valid: {amount_float}")
                                else:
                                    print(f"     ⚠️ Empty amount")
                            except ValueError as e:
                                print(f"     ❌ Parse error: {e}")
    
    except Exception as e:
        print(f"❌ Error in NaN analysis: {e}")

if __name__ == "__main__":
    print("🚀 NayaPay Parsing Debug Tool")
    print("🎯 Diagnosing start_row issues and NaN problems")
    
    debug_nayapay_csv()
    debug_template_config()
    test_manual_parsing()
    check_nan_issues()
    
    print(f"\n💡 Recommendations:")
    print("1. Based on analysis above, determine correct start_row")
    print("2. Update template if needed")
    print("3. Add NaN handling in enhanced_csv_parser.py")
    print("4. Test with fixed configuration")
