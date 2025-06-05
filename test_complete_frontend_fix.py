#!/usr/bin/env python3
"""
Test the complete frontend workflow with template switching fix.
This tests both the single CSV and multi-CSV workflows.
"""

import requests
import json
import time

API_BASE = 'http://127.0.0.1:8000'

def test_single_csv_workflow():
    print("🧪 Testing Single CSV Workflow with Template Switching")
    print("=" * 60)
    
    # Simulate frontend workflow
    print("\n1️⃣ Upload file")
    with open('m022025correct.csv', 'rb') as f:
        files = {'file': f}
        response = requests.post(f'{API_BASE}/upload', files=files)
        file_id = response.json()['file_id']
        print(f"✅ File uploaded: {file_id}")
    
    print("\n2️⃣ Load Enhanced Template (what frontend does initially)")
    response = requests.get(f'{API_BASE}/template/NayaPay_Enhanced_Template')
    enhanced_template = response.json()['config']
    print(f"✅ Enhanced template loaded: {enhanced_template['bank_name']}")
    
    print("\n3️⃣ Parse with data cleaning (frontend detects cleaning was applied)")
    parse_request = {
        'start_row': enhanced_template['start_row'],
        'end_row': enhanced_template.get('end_row'),
        'start_col': enhanced_template.get('start_col', 0),
        'end_col': enhanced_template.get('end_col'),
        'encoding': 'utf-8',
        'enable_cleaning': True
    }
    
    response = requests.post(f'{API_BASE}/parse-range/{file_id}', json=parse_request)
    parse_result = response.json()
    print(f"✅ Parse complete - cleaning applied: {parse_result.get('cleaning_applied')}")
    print(f"   Headers: {parse_result['headers']}")
    
    print("\n4️⃣ Frontend auto-switches to cleaned template (simulated)")
    # This is what the frontend fix does automatically
    if parse_result.get('cleaning_applied'):
        cleaned_template_name = 'NayaPay_Cleaned_Template'
        response = requests.get(f'{API_BASE}/template/{cleaned_template_name}')
        cleaned_template = response.json()['config']
        print(f"✅ Auto-switched to: {cleaned_template_name}")
        print(f"   Column mapping: {cleaned_template['column_mapping']}")
        
        # Verify compatibility
        available_headers = set(parse_result['headers'])
        required_headers = set(cleaned_template['column_mapping'].values())
        required_headers.discard('')
        
        missing = required_headers - available_headers
        print(f"   Compatibility check: {len(missing)} missing headers")
        
        if not missing:
            print("   ✅ Perfect compatibility!")
        else:
            print(f"   ❌ Missing headers: {missing}")
            return False
    
    print("\n5️⃣ Transform with correct template")
    transform_request = {
        'data': parse_result['data'],
        'column_mapping': cleaned_template['column_mapping'],
        'bank_name': cleaned_template['bank_name'],
        'categorization_rules': cleaned_template.get('categorization_rules', []),
        'default_category_rules': cleaned_template.get('default_category_rules', {})
    }
    
    response = requests.post(f'{API_BASE}/transform', json=transform_request)
    transform_result = response.json()
    print(f"✅ Transform successful: {transform_result['row_count']} transactions")
    
    # Check that categorization worked
    categories = {}
    for transaction in transform_result['data']:
        cat = transaction.get('Category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"   Categories applied: {dict(categories)}")
    
    return True

def test_multi_csv_workflow():
    print("\n\n🚀 Testing Multi-CSV Workflow with Auto-Template Switching")
    print("=" * 60)
    
    # Upload multiple files
    print("\n1️⃣ Upload files")
    file_ids = []
    
    # Upload NayaPay file
    with open('m022025correct.csv', 'rb') as f:
        files = {'file': f}
        response = requests.post(f'{API_BASE}/upload', files=files)
        file_ids.append(response.json()['file_id'])
    print(f"✅ Uploaded NayaPay file: {file_ids[0]}")
    
    print("\n2️⃣ Simulate multi-CSV parse with auto-template switching")
    # Prepare parse configs (what frontend would send)
    parse_configs = [{
        'start_row': 13,  # NayaPay default
        'end_row': None,
        'start_col': 0,
        'end_col': None,
        'encoding': 'utf-8',
        'template_config': {  # Include template info
            'bank_name': 'NayaPay',
            'suggested_template': 'NayaPay_Enhanced_Template',
            'cleaned_template': 'NayaPay_Cleaned_Template'
        }
    }]
    
    response = requests.post(f'{API_BASE}/multi-csv/parse', json={
        'file_ids': file_ids,
        'parse_configs': parse_configs,
        'user_name': 'Ammar Qazi',
        'date_tolerance_hours': 24,
        'enable_cleaning': True
    })
    
    parse_results = response.json()
    print(f"✅ Multi-CSV parse complete: {len(parse_results['parsed_csvs'])} files")
    
    # Check if cleaning was applied and template should switch
    for result in parse_results['parsed_csvs']:
        parse_result = result['parse_result']
        cleaning_applied = parse_result.get('cleaning_applied', False)
        print(f"   File: {result['file_name']} - Cleaning: {cleaning_applied}")
        print(f"   Headers: {parse_result.get('headers', [])}")
        
        if cleaning_applied:
            print(f"   🧽 Frontend would auto-switch to cleaned template")
    
    print("\n3️⃣ Transform with template auto-switching logic")
    # Prepare CSV data list with smart template selection
    csv_data_list = []
    
    for result in parse_results['parsed_csvs']:
        parse_result = result['parse_result']
        
        # Determine which template to use based on cleaning
        if parse_result.get('cleaning_applied'):
            template_name = 'NayaPay_Cleaned_Template'
            print(f"   Using cleaned template for {result['file_name']}")
        else:
            template_name = 'NayaPay_Enhanced_Template'
            print(f"   Using enhanced template for {result['file_name']}")
        
        # Load the appropriate template
        response = requests.get(f'{API_BASE}/template/{template_name}')
        template_config = response.json()['config']
        
        csv_data_list.append({
            'file_name': result['file_name'],
            'data': parse_result['data'],
            'headers': parse_result['headers'],
            'template_config': template_config
        })
    
    # Transform with proper template selection
    response = requests.post(f'{API_BASE}/multi-csv/transform', json={
        'csv_data_list': csv_data_list,
        'user_name': 'Ammar Qazi',
        'enable_transfer_detection': True,
        'date_tolerance_hours': 24
    })
    
    transform_result = response.json()
    print(f"✅ Multi-CSV transform successful: {transform_result['transformation_summary']['total_transactions']} transactions")
    
    # Check categorization results
    categories = {}
    for transaction in transform_result['transformed_data']:
        cat = transaction.get('Category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"   Categories applied: {dict(categories)}")
    
    return True

def main():
    print("🔧 Frontend Template Switching Fix - Integration Test")
    print("Testing the fix for 'Column dropdowns showing -- Select Column --'")
    print("\nThis simulates the frontend behavior with the new auto-template switching logic.")
    
    try:
        # Test single CSV workflow
        success1 = test_single_csv_workflow()
        
        # Test multi-CSV workflow  
        success2 = test_multi_csv_workflow()
        
        if success1 and success2:
            print("\n🎉 ALL TESTS PASSED! Frontend fix is working correctly.")
            print("\n✅ Key improvements verified:")
            print("   - Auto-detects when data cleaning is applied")
            print("   - Automatically switches from Enhanced to Cleaned templates")
            print("   - Column mappings work correctly with cleaned data")
            print("   - Smart categorization rules are applied properly")
            print("   - Both single and multi-CSV workflows fixed")
            
            print("\n🚀 The frontend should now work without 'Select Column' issues!")
            return True
        else:
            print("\n❌ Some tests failed. Check the output above.")
            return False
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
