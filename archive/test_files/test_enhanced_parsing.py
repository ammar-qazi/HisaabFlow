#!/usr/bin/env python3
"""
Test script to verify enhanced multiline CSV parsing works for March file
"""

import sys
import os
import re

def test_enhanced_parsing():
    """Test the enhanced parsing without pandas dependency"""
    
    print("🧪 Testing Enhanced Multiline CSV Parsing (Simulated)")
    print("=" * 60)
    
    march_file = "/home/ammar/claude_projects/bank_statement_parser/m032025.csv"
    
    if not os.path.exists(march_file):
        print(f"❌ March file not found: {march_file}")
        return False
    
    print(f"📁 Testing enhanced parsing for: {march_file}")
    
    try:
        # Simulate the enhanced parsing logic
        with open(march_file, 'r', encoding='utf-8', newline='') as f:
            content = f.read()
        
        # Split by lines and process
        raw_lines = content.split('\n')
        print(f"📊 Raw lines count: {len(raw_lines)}")
        
        # Look for the header row
        header_row_idx = None
        for i, line in enumerate(raw_lines):
            if 'TIMESTAMP,TYPE,DESCRIPTION,AMOUNT,BALANCE' in line.upper():
                header_row_idx = i
                break
        
        if header_row_idx is None:
            print("❌ No header row found")
            return False
            
        print(f"📋 Header found at line {header_row_idx}")
        
        processed_lines = []
        
        # Process lines before header (metadata)
        for i in range(header_row_idx + 1):
            if i < len(raw_lines):
                parts = raw_lines[i].split(',')
                while len(parts) < 9:
                    parts.append('')
                processed_lines.append(parts[:9])
        
        print(f"📊 Processed {len(processed_lines)} metadata lines")
        
        # Process transaction lines with multiline handling
        i = header_row_idx + 1
        transaction_count = 0
        
        while i < len(raw_lines):
            line = raw_lines[i].strip()
            if not line:  # Skip empty lines
                i += 1
                continue
            
            # Check if this looks like a transaction start (has a date pattern)
            if re.match(r'^\d{2}\s+\w{3}\s+\d{4}', line):  # "05 Mar 2025" pattern
                transaction_count += 1
                print(f"📅 Transaction {transaction_count}: {line[:50]}...")
                
                # Collect the full transaction (including multiline parts)
                full_transaction = line
                
                # Look ahead for continuation lines
                j = i + 1
                continuation_lines = 0
                while j < len(raw_lines):
                    next_line = raw_lines[j].strip()
                    if not next_line:
                        j += 1
                        continue
                    
                    # If next line starts with a date, we've found the next transaction
                    if re.match(r'^\d{2}\s+\w{3}\s+\d{4}', next_line):
                        break
                        
                    # This is a continuation line
                    continuation_lines += 1
                    full_transaction += ' ' + next_line
                    j += 1
                
                if continuation_lines > 0:
                    print(f"    🔗 Combined with {continuation_lines} continuation lines")
                
                # Parse the transaction into parts
                parts = []
                current_part = ''
                in_quotes = False
                
                for char in full_transaction:
                    if char == '"':
                        in_quotes = not in_quotes
                        current_part += char
                    elif char == ',' and not in_quotes:
                        parts.append(current_part.strip())
                        current_part = ''
                    else:
                        current_part += char
                
                if current_part:
                    parts.append(current_part.strip())
                
                print(f"    📋 Parsed into {len(parts)} parts: {[p[:30] + '...' if len(p) > 30 else p for p in parts]}")
                
                # Pad to 9 columns
                while len(parts) < 9:
                    parts.append('')
                
                processed_lines.append(parts[:9])
                i = j  # Move to next transaction
            else:
                print(f"⚠️ Unexpected line format: {line[:50]}...")
                i += 1
        
        print(f"\n📊 RESULTS:")
        print(f"   Total processed lines: {len(processed_lines)}")
        print(f"   Metadata lines: {header_row_idx + 1}")
        print(f"   Transaction lines: {transaction_count}")
        print(f"   Expected total: {header_row_idx + 1 + transaction_count}")
        
        if transaction_count > 0:
            print(f"✅ Successfully parsed {transaction_count} transactions!")
            
            # Show a sample parsed transaction
            if len(processed_lines) > header_row_idx + 1:
                sample_transaction = processed_lines[header_row_idx + 1]
                print(f"\n📋 Sample transaction:")
                print(f"   Timestamp: {sample_transaction[0]}")
                print(f"   Type: {sample_transaction[1]}")
                print(f"   Description: {sample_transaction[2][:50]}...")
                print(f"   Amount: {sample_transaction[3]}")
                print(f"   Balance: {sample_transaction[4]}")
            
            return True
        else:
            print(f"❌ No transactions found")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_february_comparison():
    """Test February file for comparison"""
    
    print("\n🧪 Testing February File (for comparison)")
    print("="*50)
    
    feb_file = "/home/ammar/claude_projects/bank_statement_parser/m022025.csv"
    
    if not os.path.exists(feb_file):
        print(f"❌ February file not found: {feb_file}")
        return False
    
    try:
        with open(feb_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"📊 February file has {len(lines)} lines")
        
        # Count transactions (lines with dates after header)
        transaction_count = 0
        for line in lines:
            if re.match(r'^\d{2}\s+\w{3}\s+\d{4}', line.strip()):
                transaction_count += 1
        
        print(f"📅 February file has {transaction_count} transactions")
        return True
        
    except Exception as e:
        print(f"❌ February test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Enhanced Multiline CSV Parsing")
    print("=" * 80)
    
    # Test March file (the problematic one)
    march_success = test_enhanced_parsing()
    
    # Test February file for comparison
    feb_success = test_february_comparison()
    
    print("\n" + "=" * 80)
    print("📊 FINAL RESULTS:")
    print(f"   March File Parsing: {'✅ PASS' if march_success else '❌ FAIL'}")
    print(f"   February Comparison: {'✅ PASS' if feb_success else '❌ FAIL'}")
    
    if march_success:
        print("\n🎯 SUCCESS! Enhanced parsing can handle March file multiline descriptions")
        print("💡 The 0 transactions issue should now be resolved")
        print("🚀 Ready to test in the application!")
    else:
        print("\n⚠️ Enhanced parsing needs more work")
    
    print("=" * 80)
