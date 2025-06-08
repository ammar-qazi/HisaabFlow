#!/usr/bin/env python3
"""
Debug script to identify NayaPay parsing issues
"""

def debug_nayapay_csv():
    """Debug the actual structure of NayaPay CSV"""
    
    # Read the CSV manually line by line
    print("🔍 NayaPay CSV Structure Analysis:")
    print("=" * 60)
    
    try:
        with open('/home/ammar/claude_projects/bank_statement_parser/nayapay_statement.csv', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
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
        return len(lines)
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return 0

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
    
    except Exception as e:
        print(f"❌ Error in manual parsing test: {e}")

if __name__ == "__main__":
    print("🚀 NayaPay Parsing Debug Tool")
    print("🎯 Diagnosing start_row issues and NaN problems")
    
    total_rows = debug_nayapay_csv()
    test_manual_parsing()
    
    print(f"\n💡 Summary:")
    print("- Check which start_row gives the most valid data rows")
    print("- The correct start_row should be where headers (TIMESTAMP,TYPE,DESCRIPTION,AMOUNT,BALANCE) appear")
    print("- Data rows should start immediately after the header row")
