#!/usr/bin/env python3
"""
Test script to examine the preprocessed file structure
"""
import sys
sys.path.insert(0, '/home/ammar/claude_projects/bank_statement_parser/backend')

from csv_preprocessing.csv_preprocessor import GenericCSVPreprocessor

def analyze_preprocessed_file():
    """Analyze the structure of the preprocessed NayaPay file"""
    
    sample_file = '/home/ammar/claude_projects/bank_statement_parser/sample_data/m-02-2025.csv'
    
    print("=== ANALYZING PREPROCESSED FILE STRUCTURE ===")
    
    # Run preprocessing
    preprocessor = GenericCSVPreprocessor()
    result = preprocessor.preprocess_csv(sample_file)
    
    if result['success']:
        preprocessed_file = result['processed_file_path']
        print(f"Preprocessed file: {preprocessed_file}")
        print()
        
        # Read and analyze the preprocessed file
        with open(preprocessed_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"=== FIRST 15 LINES OF PREPROCESSED FILE ===")
        for i, line in enumerate(lines[:15]):
            line_content = line.strip()
            print(f"Row {i:2d}: {line_content}")
            
            # Check if this looks like the header row
            if 'TIMESTAMP' in line_content and 'TYPE' in line_content:
                print(f"     ^^^ HEADER ROW FOUND AT INDEX {i} ^^^")
        
        print()
        print("=== HEADER DETECTION ANALYSIS ===")
        
        # Find the actual header row
        header_row_index = None
        for i, line in enumerate(lines):
            if 'TIMESTAMP' in line and 'TYPE' in line and 'DESCRIPTION' in line:
                header_row_index = i
                print(f"✅ Header row found at index: {i}")
                print(f"   Content: {line.strip()}")
                break
        
        if header_row_index is not None:
            print(f"✅ Data should start at index: {header_row_index + 1}")
            
            # Show some data rows
            print(f"\n=== SAMPLE DATA ROWS ===")
            for i in range(header_row_index + 1, min(header_row_index + 6, len(lines))):
                if i < len(lines):
                    print(f"Data {i - header_row_index}: {lines[i].strip()}")
        else:
            print("❌ Header row not found!")
    else:
        print(f"❌ Preprocessing failed: {result.get('error')}")

if __name__ == "__main__":
    analyze_preprocessed_file()
