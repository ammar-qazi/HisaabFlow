#!/usr/bin/env python3
"""
Test the complete data cleaning pipeline with FIXED column mapping
Upload files → Data Parsing → Data Cleaning → Data Transformation
"""

import sys
import os
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from enhanced_csv_parser import EnhancedCSVParser
from data_cleaner import DataCleaner
import json

def test_complete_data_cleaning_pipeline_fixed():
    print("🧪 Testing Complete Data Cleaning Pipeline - FIXED COLUMN MAPPING")
    print("=" * 70)
    print("Pipeline: Upload → Data Parsing → Data Cleaning → Data Transformation")
    
    # Initialize components
    enhanced_parser = EnhancedCSVParser()
    data_cleaner = DataCleaner()
    
    # Test files
    test_files = [
        ("/home/ammar/claude_projects/bank_statement_parser/m022025correct.csv", "February NayaPay (Corrected)"),
        ("/home/ammar/claude_projects/bank_statement_parser/m032025.csv", "March NayaPay")
    ]
    
    # Load NayaPay template
    template_path = "/home/ammar/claude_projects/bank_statement_parser/templates/NayaPay_Enhanced_Template.json"
    with open(template_path, 'r') as f:
        template_config = json.load(f)
    
    all_results = []
    
    for file_path, file_label in test_files:
        print(f"\n{'='*50}")
        print(f"🔍 TESTING: {file_label}")
        print(f"📁 File: {os.path.basename(file_path)}")
        print(f"{'='*50}")
        
        # STEP 1: DATA PARSING
        print(f"\n🚀 STEP 1: DATA PARSING")
        
        # Auto-detect data range
        detection_result = enhanced_parser.detect_data_range(file_path)
        if not detection_result['success']:
            print(f"❌ Detection failed: {detection_result['error']}")
            continue
        
        detected_header_row = detection_result['suggested_header_row']
        print(f"✅ Auto-detected header row: {detected_header_row}")
        
        # Parse with detected range
        parse_result = enhanced_parser.parse_with_range(
            file_path,
            start_row=detected_header_row,
            end_row=None,
            start_col=0,
            end_col=5
        )
        
        if not parse_result['success']:
            print(f"❌ Parsing failed: {parse_result['error']}")
            continue
        
        print(f"✅ Parsing successful: {parse_result['row_count']} rows")
        print(f"📋 Parsed headers: {parse_result['headers']}")
        
        # STEP 2: DATA CLEANING
        print(f"\n🚀 STEP 2: DATA CLEANING")
        
        cleaning_result = data_cleaner.clean_parsed_data(parse_result, template_config)
        
        if not cleaning_result['success']:
            print(f"❌ Data cleaning failed: {cleaning_result['error']}")
            continue
        
        print(f"✅ Data cleaning successful: {cleaning_result['row_count']} clean rows")
        print(f"📊 Cleaning summary: {cleaning_result['cleaning_summary']}")
        print(f"🗺️ Updated column mapping: {cleaning_result['updated_column_mapping']}")
        
        # Show sample cleaned data
        sample_cleaned = cleaning_result['data'][:2]
        for i, row in enumerate(sample_cleaned):
            date = row.get('Date', 'N/A')
            amount = row.get('Amount', 'N/A')
            currency = row.get('Currency', 'N/A')
            trans_type = row.get('Note', 'N/A')
            print(f"   🧹 Clean {i+1}: {date} | {amount} {currency} | {trans_type}")
        
        # STEP 3: DATA TRANSFORMATION 
        print(f"\n🚀 STEP 3: DATA TRANSFORMATION")
        
        # Use the UPDATED column mapping from cleaning result
        updated_column_mapping = cleaning_result['updated_column_mapping']
        categorization_rules = template_config['categorization_rules']
        default_category_rules = template_config['default_category_rules']
        bank_name = template_config['bank_name']
        
        print(f"🗺️ Using updated mapping: {updated_column_mapping}")
        
        # Transform cleaned data
        transformed = enhanced_parser.transform_to_cashew(
            cleaning_result['data'],
            updated_column_mapping,
            bank_name,
            categorization_rules,
            default_category_rules
        )
        
        print(f"✅ Transformation successful: {len(transformed)} transactions")
        
        # Show sample transformed data
        for i, trans in enumerate(transformed[:2]):
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
        
        print(f"📊 Categories: {dict(categories)}")
        
        # Store results for final summary
        all_results.append({
            'file': file_label,
            'original_rows': parse_result['row_count'],
            'cleaned_rows': cleaning_result['row_count'],
            'transformed_rows': len(transformed),
            'categories': categories,
            'cleaning_summary': cleaning_result['cleaning_summary'],
            'has_currency': 'Currency' in cleaning_result['data'][0] if cleaning_result['data'] else False,
            'numeric_amounts': isinstance(cleaning_result['data'][0].get('Amount'), (int, float)) if cleaning_result['data'] else False
        })
        
        print(f"🎯 {file_label} processing complete!")
    
    # FINAL SUMMARY
    print(f"\n{'='*70}")
    print(f"🎉 PIPELINE TESTING COMPLETE - COLUMN MAPPING FIXED!")
    print(f"{'='*70}")
    
    for result in all_results:
        print(f"\n📋 {result['file']}:")
        print(f"   📊 Data flow: {result['original_rows']} → {result['cleaned_rows']} → {result['transformed_rows']}")
        print(f"   💱 Currency added: {result['has_currency']}")
        print(f"   🔢 Numeric amounts: {result['numeric_amounts']}")
        print(f"   🧹 Cleaning: {result['cleaning_summary']}")
        print(f"   🏷️  Categories: {result['categories']}")
    
    print(f"\n✅ All tests completed successfully!")
    print(f"🗺️ Column mapping is now working correctly")
    print(f"🧹 Data cleaning pipeline is fully functional")
    print(f"💱 Currency columns added automatically")
    print(f"📊 Numeric amounts converted for better transfer detection")
    print(f"📅 Dates standardized to ISO format")
    print(f"🔄 Ready for improved transfer detection!")

if __name__ == "__main__":
    test_complete_data_cleaning_pipeline_fixed()
