#!/usr/bin/env python3
"""
Test script to verify the parameter type conversion fix
Tests the NayaPay CSV parsing with the corrected integer parameters
"""

import sys
import os
import pandas as pd

# Add the backend directory to the path
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from robust_csv_parser import RobustCSVParser

def test_parameter_conversion():
    """Test that the parameter conversion works correctly"""
    
    print("🧪 Testing Parameter Type Conversion Fix")
    print("=" * 50)
    
    # Initialize parser
    parser = RobustCSVParser()
    
    # Test file path
    test_file = "/home/ammar/claude_projects/bank_statement_parser/m022025.csv"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print(f"📁 Testing with file: {test_file}")
    
    # Test 1: Normal integer parameters (should work)
    print("\n🧪 Test 1: Integer parameters")
    try:
        result1 = parser.parse_with_range(
            file_path=test_file,
            start_row=13,     # Integer
            end_row=None,
            start_col=0,      # Integer
            end_col=None,
            encoding='utf-8'
        )
        print(f"✅ Integer params: Success={result1['success']}, Rows={result1.get('row_count', 0)}")
        
        if result1['success'] and result1.get('row_count', 0) > 0:
            print(f"📋 Headers: {result1.get('headers', [])[:5]}")  # Show first 5 headers
            print("✅ Test 1 PASSED")
        else:
            print(f"❌ Test 1 FAILED: {result1.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test 1 FAILED with exception: {e}")
        return False
    
    # Test 2: Test the safe_parse_with_range function (the one used in the API)
    print("\n🧪 Test 2: Testing safe_parse_with_range function")
    try:
        # Import the safe function from main.py
        from main import safe_parse_with_range
        
        result2 = safe_parse_with_range(
            parser=parser,
            file_path=test_file,
            start_row="13",    # String (simulating what might come from frontend)
            end_row=None,
            start_col="0",     # String
            end_col=None,
            encoding='utf-8'
        )
        print(f"✅ String params via safe function: Success={result2['success']}, Rows={result2.get('row_count', 0)}")
        
        if result2['success'] and result2.get('row_count', 0) > 0:
            print(f"📋 Headers: {result2.get('headers', [])[:5]}")
            print("✅ Test 2 PASSED - Type conversion working!")
        else:
            print(f"❌ Test 2 FAILED: {result2.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test 2 FAILED with exception: {e}")
        return False
    
    # Test 3: Edge case - mixed types
    print("\n🧪 Test 3: Mixed parameter types")
    try:
        result3 = safe_parse_with_range(
            parser=parser,
            file_path=test_file,
            start_row=13,      # Integer
            end_row="20",      # String
            start_col="0",     # String  
            end_col=9,         # Integer
            encoding='utf-8'
        )
        print(f"✅ Mixed params: Success={result3['success']}, Rows={result3.get('row_count', 0)}")
        
        if result3['success']:
            print("✅ Test 3 PASSED - Mixed type conversion working!")
        else:
            print(f"❌ Test 3 FAILED: {result3.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test 3 FAILED with exception: {e}")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Parameter type conversion fix is working correctly")
    print("✅ The pandas indexing error should now be resolved")
    return True

def test_template_loading():
    """Test that templates load correctly with the fix"""
    print("\n🧪 Testing Template Loading")
    print("=" * 30)
    
    try:
        # Test loading the NayaPay template
        from main import enhanced_parser
        
        template_name = "NayaPay_Enhanced_Template"
        template_path = "/home/ammar/claude_projects/bank_statement_parser/templates"
        
        if os.path.exists(f"{template_path}/{template_name}.json"):
            config = enhanced_parser.load_template(template_name, template_path)
            print(f"✅ Template loaded: {template_name}")
            print(f"📋 Start row from template: {config.get('start_row')} (type: {type(config.get('start_row'))})")
            
            # Verify the start_row is the expected value
            if config.get('start_row') == 13:
                print("✅ Template start_row is correct (13)")
                return True
            else:
                print(f"⚠️ Template start_row is {config.get('start_row')}, expected 13")
                return False
        else:
            print(f"⚠️ Template file not found: {template_path}/{template_name}.json")
            return False
            
    except Exception as e:
        print(f"❌ Template loading failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running Parameter Type Conversion Tests")
    print("=" * 60)
    
    # Run the main parameter conversion test
    success = test_parameter_conversion()
    
    if success:
        # If main test passes, also test template loading
        template_success = test_template_loading()
        
        if template_success:
            print("\n🎯 FINAL RESULT: ALL TESTS PASSED!")
            print("🚀 The NayaPay CSV multiline description issue should now be resolved!")
            print("💡 You can now run the application and test with m022025.csv")
        else:
            print("\n⚠️ Parameter conversion works, but template loading has issues")
    else:
        print("\n❌ FINAL RESULT: Tests failed - parameter conversion needs more work")
    
    print("\n" + "=" * 60)
