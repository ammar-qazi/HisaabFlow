#!/usr/bin/env python3
"""
Debug script for header detection line counting
"""
import csv

def debug_line_counting():
    """Debug line counting in the CSV file"""
    sample_file = "sample_data/m-02-2025.csv"
    
    print("🔍 Manual line counting:")
    with open(sample_file, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            print(f"   Row {i}: {row}")
            if i >= 15:  # Only show first 15 rows
                break
    
    print("\n🔍 Looking for TIMESTAMP row:")
    with open(sample_file, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if row and 'TIMESTAMP' in row[0]:
                print(f"   Found TIMESTAMP at row {i}: {row}")
                break

if __name__ == "__main__":
    debug_line_counting()
