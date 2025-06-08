#!/usr/bin/env python3
"""
Test the new NayaPay Cleaned Template with the data cleaning pipeline
"""

import sys
import os
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from enhanced_csv_parser import EnhancedCSVParser
from data_cleaner import DataCleaner
import json

def test_cleaned_template():
    print("🧪 Testing NayaPay Cleaned Template")
    print("=" * 60)
    
    # Initialize components
    enhanced_parser = EnhancedCSVParser()
    data_cleaner = DataCleaner()
    
    # Test file
    test_file = "/home/ammar/claude_projects/bank_statement_parser/m022025correct.csv"
    
    # Load the NEW cleaned template
    template_path = "/home/ammar/claude_projects/bank_statement_parser/templates/NayaPay_Cleaned_Template.json"
    with open(template_path, 'r') as f:
        cleaned_template = json.load(f)
    
    print(f"📋 Using template: {cleaned_template['description']}")
    print(f"🗺️ Template column mapping: {cleaned_template['column_mapping']}")
    
    # STEP 1: Parse original data
    print(f"\n🚀 STEP 1: DATA PARSING")
    detection_result = enhanced_parser.detect_data_range(test_file)
    parse_result = enhanced_parser.parse_with_range(
        test_file,
        start_row=detection_result['suggested_header_row'],
        end_col=5
    )
    
    print(f"✅ Original headers: {parse_result['headers']}")
    
    # STEP 2: Clean data
    print(f"\n🚀 STEP 2: DATA CLEANING")
    cleaning_result = data_cleaner.clean_parsed_data(parse_result, cleaned_template)
    
    if not cleaning_result['success']:
        print(f"❌ Cleaning failed: {cleaning_result['error']}")
        return
    
    cleaned_headers = [col for col in cleaning_result['data'][0].keys()] if cleaning_result['data'] else []
    print(f"✅ Cleaned headers: {cleaned_headers}")
    print(f"🗺️ Updated mapping: {cleaning_result['updated_column_mapping']}")
    
    # STEP 3: Test template compatibility
    print(f"\n🚀 STEP 3: TEMPLATE COMPATIBILITY TEST")
    
    template_mapping = cleaned_template['column_mapping']
    print(f"📋 Template expects columns: {list(template_mapping.values())}")
    print(f"🧹 Cleaned data provides: {cleaned_headers}")
    
    # Check if all required columns are available
    missing_columns = []
    available_columns = []
    
    for cashew_col, expected_col in template_mapping.items():
        if expected_col and expected_col in cleaned_headers:
            available_columns.append(f"{cashew_col} → {expected_col}")
        elif expected_col:
            missing_columns.append(f"{cashew_col} → {expected_col} (MISSING)")
        else:
            available_columns.append(f"{cashew_col} → (empty)")
    
    print(f"\n✅ Available mappings:")
    for mapping in available_columns:
        print(f"   {mapping}")
    
    if missing_columns:
        print(f"\n❌ Missing mappings:")
        for mapping in missing_columns:
            print(f"   {mapping}")
        print(f"🔧 SOLUTION: Template needs to be fixed")
        return
    else:
        print(f"\n🎉 ALL MAPPINGS AVAILABLE!")
    
    # STEP 4: Test transformation
    print(f"\n🚀 STEP 4: TRANSFORMATION TEST")
    
    try:
        # Use the cleaned template for transformation
        transformed = enhanced_parser.transform_to_cashew(
            cleaning_result['data'],
            template_mapping,
            cleaned_template['bank_name'],
            cleaned_template['categorization_rules'],
            cleaned_template['default_category_rules']
        )
        
        print(f"✅ Transformation successful: {len(transformed)} transactions")
        
        # Show sample results
        for i, trans in enumerate(transformed[:3]):
            date = trans.get('Date', 'N/A')
            amount = trans.get('Amount', 'N/A')
            category = trans.get('Category', 'N/A')
            title = trans.get('Title', 'N/A')[:40]
            print(f"   💰 Trans {i+1}: {date} | {amount} | {category} | {title}...")
        
        # Analyze categories
        categories = {}
        for trans in transformed:
            cat = trans['Category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"📊 Categories found: {dict(categories)}")
        
        # Check if we have smart categorization working
        smart_categories = [cat for cat in categories.keys() if cat not in ['Income', 'Expense']]
        if smart_categories:
            print(f"🎯 Smart categorization working: {smart_categories}")
        else:
            print(f"⚠️  Only basic categorization: {list(categories.keys())}")
        
    except Exception as e:
        print(f"❌ Transformation failed: {str(e)}")
        import traceback
        print(f"📚 Error details: {traceback.format_exc()}")

def create_frontend_instructions():
    print(f"\n📋 FRONTEND INTEGRATION INSTRUCTIONS")
    print("=" * 60)
    
    print(f"""
🔧 FRONTEND CHANGES NEEDED:

1. **Use Cleaned Headers for Dropdowns**:
   - After parsing with cleaning enabled, use response.headers
   - These will be: ['Date', 'Amount', 'Title', 'Note', 'Balance', 'Currency']
   - NOT the original: ['TIMESTAMP', 'TYPE', 'DESCRIPTION', 'AMOUNT', 'BALANCE']

2. **Use the New Cleaned Template**:
   - Template: "NayaPay_Cleaned_Template" 
   - Column mapping: {{Date: "Date", Amount: "Amount", Title: "Title", Note: "Note"}}
   - This matches the cleaned headers exactly

3. **API Response Structure**:
   ```json
   {{
     "headers": ["Date", "Amount", "Title", "Note", "Balance", "Currency"],
     "updated_column_mapping": {{"Date": "Date", "Amount": "Amount", ...}},
     "original_headers": ["TIMESTAMP", "TYPE", "DESCRIPTION", "AMOUNT", "BALANCE"],
     "cleaning_applied": true
   }}
   ```

4. **Template Selection Logic**:
   - If cleaning_applied == true: Use "NayaPay_Cleaned_Template"
   - If cleaning_applied == false: Use "NayaPay_Enhanced_Template" 
   - Or let user choose, but default to cleaned template

5. **Dropdown Population**:
   - Use response.headers (cleaned) for dropdown options
   - Use template.column_mapping to pre-select defaults
   - Date dropdown should show "Date" and auto-select it
   - Amount dropdown should show "Amount" and auto-select it

✅ RESULT: Frontend will show correct column options and smart categorization will work!
""")

if __name__ == "__main__":
    test_cleaned_template()
    create_frontend_instructions()
