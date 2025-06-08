#!/usr/bin/env python3
"""
Test NayaPay files with a manual CSV reader to understand the structure better
"""

import csv
import sys
import os

def manual_csv_analysis(file_path, label):
    """Manually read and analyze CSV structure"""
    print(f"\n=== {label} ===")
    print(f"File: {os.path.basename(file_path)}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        lines = list(reader)
    
    print(f"Total lines: {len(lines)}")
    
    # Analyze each line
    for i, line in enumerate(lines):
        if i <= 15:  # Show first 16 lines
            if i == 11:  # Expected balance summary
                print(f">>> Row {i:2}: {len(line)} columns -> BALANCE SUMMARY: {line}")
            elif i == 13:  # Expected header row  
                print(f">>> Row {i:2}: {len(line)} columns -> HEADERS: {line}")
            else:
                print(f"    Row {i:2}: {len(line)} columns -> {line[:3]}..." if len(line) > 3 else f"    Row {i:2}: {len(line)} columns -> {line}")
    
    # Find the transaction header row
    header_row = None
    for i, line in enumerate(lines):
        if len(line) >= 5 and any(word.lower() in str(line).lower() for word in ['timestamp', 'type', 'description', 'amount', 'balance']):
            header_row = i
            print(f"\n🎯 Found transaction headers at row {i}: {line}")
            break
    
    if header_row is not None:
        # Show transaction data structure
        print(f"\n📊 Transaction Data Structure:")
        transaction_start = header_row + 1
        for i in range(transaction_start, min(transaction_start + 3, len(lines))):
            if i < len(lines):
                print(f"   Row {i}: {len(lines[i])} cols -> {lines[i][:2]}... | Amount: {lines[i][3] if len(lines[i]) > 3 else 'N/A'}")
    
    return lines, header_row

def test_robust_parsing():
    """Test with our robust CSV parser approach"""
    print(f"\n🔧 Testing Robust Parsing Approach")
    print(f"=" * 50)
    
    sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')
    
    correct_file = "/home/ammar/claude_projects/bank_statement_parser/m022025correct.csv"
    march_file = "/home/ammar/claude_projects/bank_statement_parser/m032025.csv"
    
    for test_file, label in [(correct_file, "February Correct"), (march_file, "March File")]:
        lines, header_row = manual_csv_analysis(test_file, label)
        
        if header_row is not None:
            print(f"\n✅ {label}: Found headers at row {header_row}")
            print(f"   🎯 Expected: start_row={header_row}, end_col=5")
            
            # Extract just the transaction data manually
            transaction_start = header_row + 1
            headers = lines[header_row][:5]  # Take first 5 columns as headers
            
            print(f"   📋 Headers: {headers}")
            
            # Process transaction rows
            transactions = []
            for i in range(transaction_start, len(lines)):
                if len(lines[i]) >= 5:  # Must have at least 5 columns
                    transaction_row = lines[i][:5]  # Take first 5 columns
                    transactions.append(dict(zip(headers, transaction_row)))
            
            print(f"   💰 Transactions found: {len(transactions)}")
            
            # Show first 3 transactions
            for i, trans in enumerate(transactions[:3]):
                timestamp = trans.get('TIMESTAMP', 'N/A')
                amount = trans.get('AMOUNT', 'N/A')
                trans_type = trans.get('TYPE', 'N/A')
                print(f"   Transaction {i+1}: {timestamp} | {amount} | {trans_type}")
        else:
            print(f"❌ {label}: Could not find transaction headers")

def create_improved_nayapay_parser():
    """Create an improved parser specifically for NayaPay structure"""
    print(f"\n🏗️  Creating Improved NayaPay Parser")
    print(f"=" * 50)
    
    parser_code = '''
def parse_nayapay_csv(file_path):
    """Parse NayaPay CSV handling inconsistent column structure"""
    import csv
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        lines = list(reader)
    
    # Find the transaction header row (contains TIMESTAMP, TYPE, DESCRIPTION, AMOUNT, BALANCE)
    header_row_idx = None
    for i, line in enumerate(lines):
        if (len(line) >= 5 and 
            any('timestamp' in str(cell).lower() for cell in line) and
            any('amount' in str(cell).lower() for cell in line) and
            any('balance' in str(cell).lower() for cell in line)):
            header_row_idx = i
            break
    
    if header_row_idx is None:
        raise ValueError("Could not find NayaPay transaction headers")
    
    # Extract headers (first 5 columns)
    headers = lines[header_row_idx][:5]
    
    # Extract transaction data (rows after headers, first 5 columns only)
    transactions = []
    for i in range(header_row_idx + 1, len(lines)):
        if len(lines[i]) >= 5:  # Must have at least 5 columns
            row_data = lines[i][:5]  # Take only first 5 columns
            transaction = dict(zip(headers, row_data))
            
            # Skip empty transactions
            if transaction.get('AMOUNT', '').strip() and transaction.get('TIMESTAMP', '').strip():
                transactions.append(transaction)
    
    return {
        'success': True,
        'headers': headers,
        'data': transactions,
        'row_count': len(transactions),
        'header_row': header_row_idx
    }
'''
    
    print(f"✅ Improved parser function created")
    return parser_code

if __name__ == "__main__":
    print("🔍 NayaPay CSV Structure Deep Analysis")
    print("=" * 60)
    
    test_robust_parsing()
    create_improved_nayapay_parser()
    
    print(f"\n🎯 RECOMMENDATIONS:")
    print(f"1. ✅ Transaction headers are at row 13 (index 13)")
    print(f"2. ✅ Use only first 5 columns: TIMESTAMP,TYPE,DESCRIPTION,AMOUNT,BALANCE")
    print(f"3. ✅ Ignore balance summary row (row 11) with 9 columns")
    print(f"4. ✅ Skip empty rows and rows with insufficient columns")
    print(f"5. ✅ Updated template should work with start_row=13, end_col=5")
