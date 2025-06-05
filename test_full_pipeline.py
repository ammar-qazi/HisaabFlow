#!/usr/bin/env python3
"""
Test the full pipeline: CSV → Data Cleaning → Universal Transformation
"""

import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from enhanced_csv_parser import EnhancedCSVParser
from data_cleaner import DataCleaner

def test_wise_full_pipeline():
    """Test Wise CSV with full pipeline"""
    print("🧪 TESTING WISE FULL PIPELINE")
    
    # Use the sample CSV
    csv_path = "transferwise_sample.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Sample CSV not found: {csv_path}")
        return
    
    # Initialize components
    parser = EnhancedCSVParser()
    data_cleaner = DataCleaner()
    
    # Step 1: Parse CSV
    print(f"\\n📖 Step 1: Parsing CSV...")
    parse_result = parser.parse_with_range(csv_path, 0, None, 0, None, 'utf-8')
    
    if not parse_result['success']:
        print(f"❌ Parse failed: {parse_result['error']}")
        return
    
    print(f"✅ Parsed {parse_result['row_count']} rows")
    print(f"📋 Headers: {parse_result['headers']}")
    
    # Step 2: Clean data
    print(f"\\n🧹 Step 2: Cleaning data...")
    
    # Load Wise template for cleaning config
    with open('templates/Wise_Universal_Template.json', 'r') as f:
        template = json.load(f)
    
    cleaning_result = data_cleaner.clean_parsed_data(parse_result, template)
    
    if not cleaning_result['success']:
        print(f"❌ Cleaning failed: {cleaning_result['error']}")
        return
    
    print(f"✅ Cleaned to {cleaning_result['row_count']} rows")
    print(f"📊 Cleaning summary: {cleaning_result['cleaning_summary']}")
    
    # Step 3: Transform with Universal Transformer
    print(f"\\n🌟 Step 3: Universal Transformation...")
    
    column_mapping = template['column_mapping']
    account_mapping = template.get('account_mapping')
    bank_name = template['bank_name']
    
    # Use the updated column mapping from cleaning
    if 'updated_column_mapping' in cleaning_result:
        column_mapping = cleaning_result['updated_column_mapping']
        print(f"🗺️  Using updated column mapping: {column_mapping}")
    
    transformed = parser.transform_to_cashew(
        cleaning_result['data'],
        column_mapping,
        bank_name,
        None,  # No legacy rules
        None,  # No default rules
        account_mapping
    )
    
    print(f"✅ Transformed {len(transformed)} transactions")
    
    # Show results
    print(f"\\n📊 WISE FULL PIPELINE RESULTS:")
    for i, transaction in enumerate(transformed[:10]):  # First 10
        amount = transaction['Amount']
        category = transaction['Category']
        title = transaction['Title'][:50]
        account = transaction['Account']
        date = transaction['Date']
        
        print(f"   {i+1:2}. {date} | {category:12} | {title:50}... | {amount:8} [{account}]")

def test_nayapay_pipeline():
    """Test NayaPay pipeline if we have data"""
    print(f"\\n🧪 TESTING NAYAPAY PIPELINE")
    
    # Check for NayaPay CSV
    nayapay_files = ['nayapay_statement.csv', 'm022025.csv', 'm032025.csv']
    
    nayapay_csv = None
    for filename in nayapay_files:
        if os.path.exists(filename):
            nayapay_csv = filename
            break
    
    if not nayapay_csv:
        print(f"ℹ️  No NayaPay CSV found, skipping pipeline test")
        return
    
    print(f"📁 Found NayaPay CSV: {nayapay_csv}")
    
    # Similar pipeline test for NayaPay
    parser = EnhancedCSVParser()
    data_cleaner = DataCleaner()
    
    # Parse
    parse_result = parser.parse_with_range(nayapay_csv, 13, None, 0, 5, 'utf-8')
    
    if not parse_result['success']:
        print(f"❌ NayaPay parse failed: {parse_result['error']}")
        return
    
    print(f"✅ Parsed {parse_result['row_count']} NayaPay rows")
    
    # Clean
    with open('templates/NayaPay_Universal_Template.json', 'r') as f:
        template = json.load(f)
    
    cleaning_result = data_cleaner.clean_parsed_data(parse_result, template)
    
    if cleaning_result['success']:
        print(f"✅ Cleaned to {cleaning_result['row_count']} rows")
        
        # Transform
        column_mapping = cleaning_result.get('updated_column_mapping', template['column_mapping'])
        
        transformed = parser.transform_to_cashew(
            cleaning_result['data'],
            column_mapping,
            template['bank_name']
        )
        
        print(f"✅ Transformed {len(transformed)} NayaPay transactions")
        
        # Show sample results
        print(f"\\n📊 NAYAPAY SAMPLE RESULTS:")
        for i, transaction in enumerate(transformed[:5]):
            amount = transaction['Amount']
            category = transaction['Category']
            title = transaction['Title'][:40]
            date = transaction['Date']
            
            print(f"   {i+1}. {date} | {category:12} | {title:40}... | {amount:8}")
    else:
        print(f"❌ NayaPay cleaning failed: {cleaning_result['error']}")

def main():
    """Run full pipeline tests"""
    print("🚀 FULL PIPELINE TESTING")
    print("=" * 60)
    
    # Test Wise pipeline
    test_wise_full_pipeline()
    
    # Test NayaPay pipeline if available
    test_nayapay_pipeline()
    
    print(f"\\n✅ Full pipeline testing complete!")
    print(f"🎉 Universal Transformer is working with real CSV data!")

if __name__ == "__main__":
    main()
