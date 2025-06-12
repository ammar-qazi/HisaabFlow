#!/usr/bin/env python3
"""
Test the generic CSV preprocessor on the NayaPay sample file
"""
import sys
import os

# Add backend path
sys.path.insert(0, '/home/ammar/claude_projects/bank_statement_parser/backend')

from csv_preprocessing.csv_preprocessor import GenericCSVPreprocessor

def test_nayapay_preprocessing():
    """Test generic preprocessing on NayaPay file with multiline issues"""
    
    sample_file = '/home/ammar/claude_projects/bank_statement_parser/sample_data/m-02-2025.csv'
    
    print("=== TESTING GENERIC CSV PREPROCESSOR ===")
    print(f"Input file: {sample_file}")
    print()
    
    # Initialize preprocessor
    preprocessor = GenericCSVPreprocessor()
    
    # Run preprocessing
    result = preprocessor.preprocess_csv(sample_file)
    
    print("\n=== PREPROCESSING RESULTS ===")
    print(f"Success: {result['success']}")
    print(f"Original rows: {result['original_rows']}")
    print(f"Processed rows: {result['processed_rows']}")
    print(f"Issues fixed: {len(result['issues_fixed'])}")
    
    for issue in result['issues_fixed']:
        print(f"  - {issue}")
    
    if result['warnings']:
        print(f"Warnings: {len(result['warnings'])}")
        for warning in result['warnings']:
            print(f"  - {warning}")
    
    # If successful, show first few lines of processed file
    if result['success'] and result['processed_file_path']:
        print(f"\n=== FIRST 10 LINES OF PROCESSED FILE ===")
        print(f"File: {result['processed_file_path']}")
        print()
        
        try:
            with open(result['processed_file_path'], 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Find header row
            header_found = False
            for i, line in enumerate(lines):
                if 'TIMESTAMP' in line and 'TYPE' in line:
                    print(f"Header (line {i}): {line.strip()}")
                    header_found = True
                    
                    # Show next 10 data rows
                    for j in range(1, min(11, len(lines) - i)):
                        if i + j < len(lines):
                            print(f"Data {j}: {lines[i + j].strip()}")
                    break
            
            if not header_found:
                print("Header not found, showing first 10 lines:")
                for i, line in enumerate(lines[:10]):
                    print(f"Line {i}: {line.strip()}")
                    
        except Exception as e:
            print(f"Error reading processed file: {e}")
    
    print(f"\n=== Expected Result ===")
    print("Should show ~22 transactions instead of ~45 lines")
    print("Multiline descriptions should be merged into single lines")
    print("No more broken CSV structure from newlines in quoted fields")

if __name__ == "__main__":
    test_nayapay_preprocessing()
