#!/usr/bin/env python3
"""
Simple test to examine March file structure manually
"""

def examine_march_file():
    """Examine the March file structure to find header row"""
    
    print("🔍 Examining March File Structure")
    print("=" * 50)
    
    march_file = "/home/ammar/claude_projects/bank_statement_parser/m032025.csv"
    
    try:
        with open(march_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"📁 File: {march_file}")
        print(f"📊 Total lines: {len(lines)}")
        print("\n📋 Line-by-line analysis:")
        
        for i, line in enumerate(lines):
            clean_line = line.strip()
            lower_line = clean_line.lower()
            
            print(f"Row {i:2d}: {clean_line[:80]}{'...' if len(clean_line) > 80 else ''}")
            
            # Check for header indicators
            if 'timestamp' in lower_line and 'type' in lower_line and 'description' in lower_line:
                print(f"     🎯 HEADER ROW DETECTED! ← This is the header row")
            elif 'customer' in lower_line:
                print(f"     📝 Customer info")
            elif 'opening balance' in lower_line or 'closing balance' in lower_line:
                print(f"     💰 Balance summary")
            elif clean_line == "":
                print(f"     ⬜ Empty line")
            elif any(month in lower_line for month in ['mar', 'feb', 'jan', 'apr']):
                print(f"     📅 Date/period info")
        
        # Find the header row specifically
        header_row = None
        for i, line in enumerate(lines):
            if 'TIMESTAMP,TYPE,DESCRIPTION,AMOUNT,BALANCE' in line.upper():
                header_row = i
                break
        
        if header_row is not None:
            print(f"\n✅ NayaPay header row found at: {header_row}")
            print(f"🎯 This should be the start_row value for March file")
            
            # Count transactions after header
            transaction_count = len(lines) - header_row - 1
            print(f"📊 Expected transactions after header: {transaction_count}")
            
            return header_row
        else:
            print(f"\n❌ Could not find NayaPay header row")
            return None
            
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

def examine_february_file():
    """Examine the February file for comparison"""
    
    print("\n🔍 Examining February File Structure (for comparison)")
    print("=" * 50)
    
    feb_file = "/home/ammar/claude_projects/bank_statement_parser/m022025.csv"
    
    try:
        with open(feb_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the header row specifically
        header_row = None
        for i, line in enumerate(lines):
            if 'TIMESTAMP,TYPE,DESCRIPTION,AMOUNT,BALANCE' in line.upper():
                header_row = i
                break
        
        if header_row is not None:
            print(f"✅ February header row found at: {header_row}")
            transaction_count = len(lines) - header_row - 1
            print(f"📊 Expected transactions after header: {transaction_count}")
            return header_row
        else:
            print(f"❌ Could not find February header row")
            return None
            
    except Exception as e:
        print(f"❌ Error reading February file: {e}")
        return None

if __name__ == "__main__":
    print("🧪 Manual File Structure Analysis")
    print("=" * 70)
    
    # Examine March file (the problematic one)
    march_header = examine_march_file()
    
    # Examine February file for comparison
    feb_header = examine_february_file()
    
    print("\n" + "=" * 70)
    print("📊 SUMMARY:")
    print(f"   March file header row: {march_header}")
    print(f"   February file header row: {feb_header}")
    
    if march_header is not None and feb_header is not None:
        if march_header != feb_header:
            print(f"\n🎯 INSIGHT: Different NayaPay files have different header rows!")
            print(f"   📅 February starts at row {feb_header}")
            print(f"   📅 March starts at row {march_header}")
            print(f"   💡 This explains why the hardcoded start_row=13 doesn't work for March")
            print(f"\n✅ Solution: Enhanced auto-detection should detect row {march_header} for March")
        else:
            print(f"\n🤔 Both files have the same header row: {march_header}")
    
    print("=" * 70)
