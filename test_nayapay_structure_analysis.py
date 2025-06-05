#!/usr/bin/env python3
"""
Analyze the structural differences between modified and correct NayaPay files
"""

import sys
import os
import csv
import json

def analyze_csv_structure(filepath, label):
    """Analyze the structure of a CSV file"""
    print(f"\n=== {label} ===")
    print(f"File: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        lines = list(reader)
    
    print(f"Total lines: {len(lines)}")
    
    # Show first 15 lines with their structure
    for i, line in enumerate(lines[:15]):
        if i == 13:  # Expected header row
            print(f">>> Row {i:2}: {len(line)} columns -> {line}")
        else:
            print(f"    Row {i:2}: {len(line)} columns -> {line[:5]}..." if len(line) > 5 else f"    Row {i:2}: {len(line)} columns -> {line}")
    
    # Check consistency of transaction rows (starting from row 14)
    if len(lines) > 14:
        transaction_column_counts = [len(line) for line in lines[14:]]
        unique_counts = set(transaction_column_counts)
        print(f"Transaction rows column counts: {unique_counts}")
        
        # Show sample transaction rows
        print(f"Sample transaction rows:")
        for i in range(14, min(18, len(lines))):
            print(f"    Row {i:2}: {len(lines[i])} cols -> {lines[i]}")
    
    return lines

def main():
    print("🔍 NayaPay CSV Structure Analysis")
    print("=" * 60)
    
    # File paths
    modified_file = "/home/ammar/claude_projects/bank_statement_parser/m022025.csv"
    correct_file = "/home/ammar/claude_projects/bank_statement_parser/m022025correct.csv"
    march_file = "/home/ammar/claude_projects/bank_statement_parser/m032025.csv"
    
    # Analyze each file
    modified_lines = analyze_csv_structure(modified_file, "MODIFIED FILE (m022025.csv)")
    correct_lines = analyze_csv_structure(correct_file, "CORRECT FILE (m022025correct.csv)")
    march_lines = analyze_csv_structure(march_file, "MARCH FILE (m032025.csv)")
    
    print(f"\n=== KEY DIFFERENCES IDENTIFIED ===")
    
    # Compare header structures
    print(f"1. Header Structure Differences:")
    if len(modified_lines) > 0:
        print(f"   Modified header row 0: {len(modified_lines[0])} columns")
        print(f"   Modified data row 13: {len(modified_lines[13]) if len(modified_lines) > 13 else 'N/A'} columns")
    
    if len(correct_lines) > 0:
        print(f"   Correct header row 0: {len(correct_lines[0])} columns")
        print(f"   Correct data row 13: {len(correct_lines[13]) if len(correct_lines) > 13 else 'N/A'} columns")
    
    # Compare account number format
    print(f"\n2. Account Number Format:")
    if len(modified_lines) > 3:
        print(f"   Modified: {modified_lines[3][1] if len(modified_lines[3]) > 1 else 'N/A'}")
    if len(correct_lines) > 3:
        print(f"   Correct: {correct_lines[3][1] if len(correct_lines[3]) > 1 else 'N/A'}")
    
    # Compare transaction data structure
    print(f"\n3. Transaction Data Structure:")
    if len(modified_lines) > 14:
        print(f"   Modified transaction: {len(modified_lines[14])} columns -> {modified_lines[14]}")
    if len(correct_lines) > 14:
        print(f"   Correct transaction: {len(correct_lines[14])} columns -> {correct_lines[14]}")
    
    print(f"\n=== RECOMMENDED TEMPLATE CHANGES ===")
    print(f"1. Update detection to handle clean CSV structure (5 columns exactly)")
    print(f"2. Account number should expect leading apostrophe format")
    print(f"3. Transaction parsing should expect exactly 5 columns: TIMESTAMP,TYPE,DESCRIPTION,AMOUNT,BALANCE")
    print(f"4. Date format can vary: '09:17 AM' (correct) vs '9:17 AM' (modified)")

if __name__ == "__main__":
    main()
