#!/usr/bin/env python3
"""
Test script to verify the pandas indexing bug fix
"""
import tempfile
import os
from robust_csv_parser import RobustCSVParser

def test_pandas_indexing_fix():
    """Test that the pandas indexing fix works"""
    
    # Create a test CSV file
    test_csv_content = """Header1,Header2,Header3,Header4,Header5
Row1Col1,Row1Col2,Row1Col3,Row1Col4,Row1Col5
Row2Col1,Row2Col2,Row2Col3,Row2Col4,Row2Col5
Row3Col1,Row3Col2,Row3Col3,Row3Col4,Row3Col5"""
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(test_csv_content)
        temp_file = f.name
    
    try:
        parser = RobustCSVParser()
        
        # Test the problematic case: string parameters that caused the original error
        print("🧪 Testing with string parameters (original bug scenario)...")
        
        # These string values would cause "cannot do positional indexing" error before fix
        result = parser.parse_with_range(
            temp_file, 
            start_row="1",  # String instead of int
            end_row="4",    # String instead of int  
            start_col="0",  # String instead of int
            end_col="5"     # String instead of int - this was the main culprit
        )
        
        if result['success']:
            print("✅ SUCCESS: String parameter bug is FIXED!")
            print(f"   - Extracted {result['row_count']} rows")
            print(f"   - Headers: {result['headers']}")
            print(f"   - Sample data: {result['data'][0] if result['data'] else 'No data'}")
            return True
        else:
            print(f"❌ FAILED: {result['error']}")
            return False
            
    finally:
        # Clean up temp file
        os.unlink(temp_file)

if __name__ == "__main__":
    print("🔧 Testing pandas indexing bug fix...")
    print("=" * 50)
    
    success = test_pandas_indexing_fix()
    
    print("=" * 50)
    if success:
        print("🎉 All tests passed! The pandas bug is fixed.")
    else:
        print("💥 Tests failed. More debugging needed.")
