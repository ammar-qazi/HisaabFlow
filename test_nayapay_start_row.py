#!/usr/bin/env python3
"""
Test script to verify NayaPay start row detection
"""

import pandas as pd
import os

def check_nayapay_csv_structure():
    """Check the actual structure of a NayaPay CSV file"""
    
    # Look for NayaPay CSV files
    nayapay_files = [
        "nayapay_statement.csv",
        "converted_nayapay.csv"
    ]
    
    for filename in nayapay_files:
        if os.path.exists(filename):
            print(f"\n🔍 Examining {filename}:")
            print("=" * 50)
            
            try:
                # Read first 20 rows to see structure
                df = pd.read_csv(filename, header=None, nrows=20)
                
                for i, row in df.iterrows():
                    print(f"Row {i:2d}: {list(row.fillna(''))}")
                    
                    # Check if this looks like a header row
                    row_str = ' '.join([str(cell).lower() for cell in row if pd.notna(cell)])
                    if any(keyword in row_str for keyword in ['timestamp', 'amount', 'description', 'balance', 'type']):
                        print(f"    ^^^^ Potential header row at index {i} ^^^^")
                
            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")
        else:
            print(f"❌ File {filename} not found")

def check_template_start_rows():
    """Check what start_row is set in templates"""
    template_files = [
        "templates/NayaPay_Template.json",
        "templates/NayaPay_Enhanced_Template.json"
    ]
    
    print(f"\n📋 Template Configuration:")
    print("=" * 50)
    
    for template_file in template_files:
        if os.path.exists(template_file):
            try:
                import json
                with open(template_file, 'r') as f:
                    config = json.load(f)
                
                start_row = config.get('start_row', 'Not set')
                print(f"{template_file}: start_row = {start_row}")
                
            except Exception as e:
                print(f"❌ Error reading {template_file}: {e}")
        else:
            print(f"❌ Template {template_file} not found")

if __name__ == "__main__":
    print("🚀 Testing NayaPay Start Row Configuration")
    
    check_nayapay_csv_structure()
    check_template_start_rows()
    
    print(f"\n💡 Summary:")
    print("- If templates show start_row = 13, but data starts at row 11, there's a mismatch")
    print("- Templates should be updated to start_row = 11")
    print("- OR the CSV structure has changed and we need to detect this automatically")
