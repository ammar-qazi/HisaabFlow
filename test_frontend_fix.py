#!/usr/bin/env python3
"""
Test script to reproduce and verify the frontend column mapping issue fix.
This simulates the exact workflow that the frontend follows.
"""

import requests
import json
import sys

API_BASE = 'http://127.0.0.1:8000'

def test_workflow():
    print("🧪 Testing Frontend Column Mapping Fix")
    print("=" * 50)
    
    # Step 1: Upload file
    print("\n📤 Step 1: Upload file")
    try:
        with open('m022025correct.csv', 'rb') as f:
            files = {'file': f}
            response = requests.post(f'{API_BASE}/upload', files=files)
            response.raise_for_status()
            file_id = response.json()['file_id']
            print(f"✅ File uploaded: {file_id}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False
    
    # Step 2: Load Enhanced Template (what frontend would do initially)
    print("\n📋 Step 2: Load NayaPay_Enhanced_Template")
    try:
        response = requests.get(f'{API_BASE}/template/NayaPay_Enhanced_Template')
        response.raise_for_status()
        enhanced_template = response.json()['config']
        print(f"✅ Enhanced template loaded")
        print(f"   - Column mapping: {enhanced_template['column_mapping']}")
        print(f"   - Bank: {enhanced_template.get('bank_name', 'Unknown')}")
    except Exception as e:
        print(f"❌ Template load failed: {e}")
        return False
    
    # Step 3: Parse with range (with data cleaning enabled - this is the key)
    print("\n🧹 Step 3: Parse with data cleaning enabled")
    parse_request = {
        'start_row': enhanced_template['start_row'],
        'end_row': enhanced_template.get('end_row'),
        'start_col': enhanced_template.get('start_col', 0),
        'end_col': enhanced_template.get('end_col'),
        'encoding': 'utf-8',
        'enable_cleaning': True  # This is crucial!
    }
    
    try:
        response = requests.post(f'{API_BASE}/parse-range/{file_id}', json=parse_request)
        response.raise_for_status()
        parse_result = response.json()
        print(f"✅ Parse successful")
        print(f"   - Headers (cleaned): {parse_result['headers']}")
        print(f"   - Original headers: {parse_result.get('original_headers', [])}")
        print(f"   - Cleaning applied: {parse_result.get('cleaning_applied', False)}")
        print(f"   - Updated mapping: {parse_result.get('updated_column_mapping', {})}")
    except Exception as e:
        print(f"❌ Parse failed: {e}")
        return False
    
    # Step 4: Load Cleaned Template (what frontend should do automatically)
    print("\n🧽 Step 4: Load NayaPay_Cleaned_Template")
    try:
        response = requests.get(f'{API_BASE}/template/NayaPay_Cleaned_Template')
        response.raise_for_status()
        cleaned_template = response.json()['config']
        print(f"✅ Cleaned template loaded")
        print(f"   - Column mapping: {cleaned_template['column_mapping']}")
        print(f"   - Bank: {cleaned_template.get('bank_name', 'Unknown')}")
    except Exception as e:
        print(f"❌ Cleaned template load failed: {e}")
        return False
    
    # Step 5: Check compatibility
    print("\n🔍 Step 5: Check column mapping compatibility")
    
    # Available headers from parsing (cleaned)
    available_headers = set(parse_result['headers'])
    
    # Required headers from Enhanced Template (original column names)
    enhanced_required = set(enhanced_template['column_mapping'].values())
    enhanced_required.discard('')  # Remove empty mappings
    
    # Required headers from Cleaned Template (cleaned column names)  
    cleaned_required = set(cleaned_template['column_mapping'].values())
    cleaned_required.discard('')  # Remove empty mappings
    
    print(f"   📊 Available headers: {sorted(available_headers)}")
    print(f"   🔧 Enhanced template needs: {sorted(enhanced_required)}")
    print(f"   🧽 Cleaned template needs: {sorted(cleaned_required)}")
    
    enhanced_missing = enhanced_required - available_headers
    cleaned_missing = cleaned_required - available_headers
    
    print(f"\n🚨 Compatibility Check:")
    print(f"   - Enhanced template missing: {sorted(enhanced_missing) if enhanced_missing else 'None ✅'}")
    print(f"   - Cleaned template missing: {sorted(cleaned_missing) if cleaned_missing else 'None ✅'}")
    
    # The fix: Use cleaned template for cleaned data
    if parse_result.get('cleaning_applied') and not cleaned_missing:
        print(f"\n✅ SOLUTION: Use cleaned template for cleaned data!")
        correct_template = cleaned_template
        template_name = "NayaPay_Cleaned_Template"
    elif not enhanced_missing:
        print(f"\n⚠️  Using enhanced template (but may have issues)")
        correct_template = enhanced_template  
        template_name = "NayaPay_Enhanced_Template"
    else:
        print(f"\n❌ Neither template is compatible!")
        return False
    
    # Step 6: Transform with correct template
    print(f"\n🔄 Step 6: Transform with {template_name}")
    try:
        transform_request = {
            'data': parse_result['data'],
            'column_mapping': correct_template['column_mapping'],
            'bank_name': correct_template.get('bank_name', 'NayaPay'),
            'categorization_rules': correct_template.get('categorization_rules', []),
            'default_category_rules': correct_template.get('default_category_rules', {}),
            'account_mapping': correct_template.get('account_mapping', {})
        }
        
        response = requests.post(f'{API_BASE}/transform', json=transform_request)
        response.raise_for_status()
        transform_result = response.json()
        print(f"✅ Transform successful: {transform_result['row_count']} transactions")
        
        # Show sample transformed data
        if transform_result['data']:
            sample = transform_result['data'][0]
            print(f"   📋 Sample transaction:")
            for key, value in sample.items():
                print(f"      {key}: {value}")
                
    except Exception as e:
        print(f"❌ Transform failed: {e}")
        return False
    
    print(f"\n🎉 All tests passed! Frontend fix should work correctly.")
    return True

if __name__ == "__main__":
    success = test_workflow()
    sys.exit(0 if success else 1)
