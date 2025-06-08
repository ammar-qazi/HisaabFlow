#!/usr/bin/env python3
"""
Quick test of multi-CSV parsing without the server
"""

import sys
import os
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from enhanced_csv_parser import EnhancedCSVParser

def test_simple_multi_csv_parse():
    print("🧪 Testing Enhanced CSV Parser (standalone)")
    print("=" * 50)
    
    # Initialize parser
    parser = EnhancedCSVParser()
    
    # Test file path
    csv_path = "/home/ammar/claude_projects/bank_statement_parser/m022025.csv"
    
    print(f"📁 Testing with file: {csv_path}")
    
    try:
        # Test basic parsing
        result = parser.parse_with_range(csv_path, 13, None, 0, 5, 'utf-8')
        
        if result['success']:
            print(f"✅ Parse successful: {result['row_count']} rows")
            print(f"📊 Headers: {result['headers']}")
            print("🔍 First row sample:")
            if result['data']:
                print(f"   {result['data'][0]}")
        else:
            print(f"❌ Parse failed: {result['error']}")
            
    except Exception as e:
        print(f"💥 Exception during parsing: {str(e)}")
        import traceback
        print(f"📚 Full traceback:\n{traceback.format_exc()}")

    print(f"\n🎉 Test complete!")

if __name__ == "__main__":
    test_simple_multi_csv_parse()
