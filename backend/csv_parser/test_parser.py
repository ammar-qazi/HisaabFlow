#!/usr/bin/env python3
"""
Quick test for UnifiedCSVParser
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from unified_parser import UnifiedCSVParser

def test_unified_parser():
    print("=== Testing UnifiedCSVParser ===")
    
    parser = UnifiedCSVParser()
    test_file = "../test_forint.csv"
    
    print(f"\n1. Testing Forint Bank quote-all format: {test_file}")
    result = parser.preview_csv(test_file, max_rows=10)
    
    if result['success']:
        print(f"[SUCCESS] SUCCESS: Parsed {result['total_rows']} rows, {result['total_columns']} columns")
        print(f" Headers: {result['column_names']}")
        print(f" Detection info:")
        detection = result.get('detection_info', {})
        if 'encoding' in detection:
            print(f"   Encoding: {detection['encoding']['encoding']} (confidence: {detection['encoding']['confidence']:.2f})")
        if 'dialect' in detection:
            d = detection['dialect']
            print(f"   Dialect: delimiter='{d['delimiter']}', quoting={d['quoting']}, confidence={d['confidence']:.2f}")
        
        print(f"[DATA] Sample data:")
        for i, row in enumerate(result['preview_data'][:3]):
            print(f"   Row {i}: {row}")
    else:
        print(f"[ERROR]  FAILED: {result['error']}")
    
    print("\n2. Testing structure detection")
    structure = parser.detect_structure(test_file)
    if structure['success']:
        print(f"[SUCCESS] Structure detected successfully")
        print(f"   Suggested header row: {structure['structure']['suggested_header_row']}")
    else:
        print(f"[ERROR]  Structure detection failed: {structure['error']}")

if __name__ == "__main__":
    test_unified_parser()
