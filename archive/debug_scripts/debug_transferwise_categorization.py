#!/usr/bin/env python3

import json
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from enhanced_csv_parser import EnhancedCSVParser

def debug_transferwise_categorization():
    """Debug why Lidl and Aldi aren't being categorized as Groceries"""
    
    # Load the Transferwise template
    template_path = "../templates/Transferwise_Hungarian_Template.json"
    
    try:
        with open(template_path, 'r') as f:
            template = json.load(f)
        print(f"✅ Template loaded: {template['name']}")
    except Exception as e:
        print(f"❌ Error loading template: {e}")
        return
    
    # Initialize parser
    parser = EnhancedCSVParser()
    
    # Parse the test CSV
    csv_path = "../transferwise_final_test.csv"
    
    try:
        parse_result = parser.parse_with_range(csv_path, 0, None, 0, None, 'utf-8')
        if not parse_result['success']:
            print(f"❌ Parse failed: {parse_result['error']}")
            return
        
        print(f"✅ CSV parsed successfully: {parse_result['row_count']} rows")
        print(f"📋 Headers: {parse_result['headers']}")
        
    except Exception as e:
        print(f"❌ Error parsing CSV: {e}")
        return
    
    # Find test transactions with Lidl/Aldi
    test_data = parse_result['data']
    lidl_transactions = []
    
    for i, row in enumerate(test_data):
        description = str(row.get('Description', '')).lower()
        if 'lidl' in description or 'aldi' in description:
            lidl_transactions.append((i, row))
            print(f"\n🔍 Found test transaction {i}:")
            print(f"   Description: {row.get('Description', 'N/A')}")
            print(f"   Amount: {row.get('Amount', 'N/A')}")
            print(f"   Currency: {row.get('Currency', 'N/A')}")
    
    if not lidl_transactions:
        print("\n❌ No Lidl/Aldi transactions found in test data")
        return
    
    # Test the categorization rules
    categorization_rules = template.get('categorization_rules', [])
    column_mapping = template.get('column_mapping', {})
    account_mapping = template.get('account_mapping', {})
    
    print(f"\n📋 Template has {len(categorization_rules)} rules")
    print(f"🗺️  Column mapping: {column_mapping}")
    
    # Find Lidl/Aldi rules
    lidl_rule = None
    aldi_rule = None
    
    for rule in categorization_rules:
        if 'Lidl' in rule.get('name', ''):
            lidl_rule = rule
            print(f"\n✅ Found Lidl rule (priority {rule.get('priority')}):")
            print(f"   Conditions: {rule.get('conditions')}")
            print(f"   Actions: {rule.get('actions')}")
        if 'Aldi' in rule.get('name', ''):
            aldi_rule = rule
            print(f"\n✅ Found Aldi rule (priority {rule.get('priority')}):")
            print(f"   Conditions: {rule.get('conditions')}")
            print(f"   Actions: {rule.get('actions')}")
    
    # Test transformation
    print(f"\n🔄 Testing transformation...")
    
    try:
        transformed = parser.transform_to_cashew(
            test_data,
            column_mapping,
            template.get('bank_name', 'Transferwise'),
            categorization_rules,
            None,  # default_category_rules
            account_mapping
        )
        
        print(f"✅ Transformation successful: {len(transformed)} transactions")
        
        # Check if Lidl transactions got categorized correctly
        for i, (original_idx, original_row) in enumerate(lidl_transactions):
            if original_idx < len(transformed):
                transformed_row = transformed[original_idx]
                print(f"\n📊 Transaction {original_idx} results:")
                print(f"   Original Description: {original_row.get('Description', 'N/A')}")
                print(f"   Transformed Title: {transformed_row.get('Title', 'N/A')}")
                print(f"   Category: {transformed_row.get('Category', 'N/A')}")
                print(f"   Account: {transformed_row.get('Account', 'N/A')}")
                
                if transformed_row.get('Category') == 'Groceries':
                    print(f"   ✅ CORRECTLY categorized as Groceries!")
                else:
                    print(f"   ❌ NOT categorized as Groceries")
                    
                    # Debug the rule matching
                    print(f"\n🔍 Debugging rule matching for this transaction...")
                    
                    # Test the condition manually
                    if lidl_rule:
                        conditions = lidl_rule.get('conditions', {})
                        if 'description_contains' in conditions:
                            description_field = None
                            for key in original_row:
                                if 'description' in key.lower():
                                    description_field = key
                                    break
                            
                            print(f"   Description field found: {description_field}")
                            if description_field:
                                description_text = str(original_row[description_field]).lower()
                                print(f"   Description text: '{description_text}'")
                                
                                for search_term in conditions['description_contains']:
                                    found = search_term.lower() in description_text
                                    print(f"   Searching for '{search_term}': {found}")
                                    
        
    except Exception as e:
        print(f"❌ Transformation error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_transferwise_categorization()
