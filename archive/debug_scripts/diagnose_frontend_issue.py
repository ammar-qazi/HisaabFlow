#!/usr/bin/env python3
"""
Simulate the frontend workflow to see what's happening with column mapping
"""

import requests
import json

def simulate_frontend_workflow():
    print("🎭 Simulating Frontend Workflow")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # Step 1: Upload a file (simulate)
    print("1. 📤 File Upload (simulated)")
    print("   In real workflow: User uploads m022025correct.csv")
    print("   Expected: File gets uploaded and we get a file_id")
    
    # Step 2: Preview file (simulate what frontend should get)
    print(f"\n2. 👁️ File Preview")
    print("   Frontend calls: GET /preview/{file_id}")
    print("   Expected: Raw CSV structure for user to see")
    
    # Step 3: Detect range (simulate)
    print(f"\n3. 🔍 Auto-Detection")
    print("   Frontend calls: GET /detect-range/{file_id}")
    print("   Expected: start_row=13 for NayaPay")
    
    # Step 4: Parse with range (this is where the issue might be)
    print(f"\n4. 📊 Parse with Range")
    print("   Frontend calls: POST /parse-range/{file_id}")
    print("   Request body: {start_row: 13, end_row: null, start_col: 0, end_col: 5, enable_cleaning: true}")
    print("   Expected: Parsed data with headers for column mapping")
    
    # Step 5: Load template
    print(f"\n5. 📋 Load Template")
    print("   Frontend calls: GET /template/NayaPay_Enhanced_Template")
    print("   ✅ This works - we tested it above")
    
    # Step 6: Apply template mapping
    print(f"\n6. 🗺️ Apply Template Mapping")
    print("   Frontend should:")
    print("   - Take template column_mapping: {Date: 'TIMESTAMP', Amount: 'AMOUNT', ...}")
    print("   - Look for these columns in parsed headers")
    print("   - Pre-populate the dropdowns")
    
    print(f"\n🔍 DIAGNOSIS:")
    print("The issue is likely that:")
    print("1. ❌ Parsed headers after cleaning are: ['Date', 'Amount', 'Title', 'Note', 'Balance', 'Currency']")
    print("2. ❌ Template expects headers: ['TIMESTAMP', 'TYPE', 'DESCRIPTION', 'AMOUNT', 'BALANCE']")
    print("3. ❌ Frontend can't find 'TIMESTAMP' in cleaned headers, so dropdown shows '-- Select Column --'")
    
    print(f"\n💡 SOLUTION:")
    print("We need to either:")
    print("1. 🔄 Update template to use cleaned column names")
    print("2. 🔄 Provide both original and cleaned headers to frontend")
    print("3. 🔄 Use updated_column_mapping from cleaning result")

def test_parsing_headers():
    print(f"\n🧪 Testing What Headers Are Actually Returned")
    print("=" * 50)
    
    # Let's test our data cleaner directly to see what headers it produces
    import sys
    import os
    sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')
    
    from enhanced_csv_parser import EnhancedCSVParser
    from data_cleaner import DataCleaner
    
    # Initialize components
    enhanced_parser = EnhancedCSVParser()
    data_cleaner = DataCleaner()
    
    # Test file
    test_file = "/home/ammar/claude_projects/bank_statement_parser/m022025correct.csv"
    
    # Load template
    template_path = "/home/ammar/claude_projects/bank_statement_parser/templates/NayaPay_Enhanced_Template.json"
    with open(template_path, 'r') as f:
        template_config = json.load(f)
    
    # Step 1: Parse
    detection_result = enhanced_parser.detect_data_range(test_file)
    parse_result = enhanced_parser.parse_with_range(
        test_file,
        start_row=detection_result['suggested_header_row'],
        end_col=5
    )
    
    print(f"📊 Original parsed headers: {parse_result['headers']}")
    
    # Step 2: Clean
    cleaning_result = data_cleaner.clean_parsed_data(parse_result, template_config)
    
    if cleaning_result['success']:
        cleaned_headers = [col for col in cleaning_result['data'][0].keys()] if cleaning_result['data'] else []
        print(f"🧹 Cleaned headers: {cleaned_headers}")
        print(f"🗺️ Updated column mapping: {cleaning_result['updated_column_mapping']}")
        
        print(f"\n🔍 THE PROBLEM:")
        print(f"   Template column mapping: {template_config['column_mapping']}")
        print(f"   Template expects: {list(template_config['column_mapping'].values())}")
        print(f"   Cleaned data has: {cleaned_headers}")
        print(f"   ❌ NO MATCH! Frontend can't find expected columns")
        
        print(f"\n✅ THE SOLUTION:")
        print(f"   Use updated_column_mapping: {cleaning_result['updated_column_mapping']}")
        print(f"   This maps Cashew columns → Cleaned columns correctly")

if __name__ == "__main__":
    simulate_frontend_workflow()
    test_parsing_headers()
