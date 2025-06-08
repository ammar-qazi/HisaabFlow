#!/usr/bin/env python3

# Test script to verify backend transformation works with Universal Transformer
import sys
import os

# Add backend to path
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

# Test imports and transformation
from enhanced_csv_parser import EnhancedCSVParser

def test_backend_integration():
    """Test that backend correctly uses Universal Transformer"""
    print("🧪 Testing Backend Integration with Universal Transformer")
    
    # Initialize parser
    parser = EnhancedCSVParser()
    
    print(f"✅ Parser initialized")
    print(f"   🔧 Universal Transformer available: {parser.universal_transformer is not None}")
    
    if parser.universal_transformer:
        print(f"   📋 Universal rules loaded: {len(parser.universal_transformer.universal_rules)}")
        print(f"   🏦 Bank overrides: {list(parser.universal_transformer.bank_overrides.keys())}")
    
    # Test transformation with real Wise data
    wise_data = [
        {
            'Date': '2025-06-01',
            'Amount': -3000.0,
            'Title': 'Card transaction of 3,000.00 HUF issued by Barionpay Ltd',
            'Note': 'Payment Reference',
            'Currency': 'HUF'
        },
        {
            'Date': '2025-05-29', 
            'Amount': -6288.0,
            'Title': 'Card transaction of 6,288.00 HUF issued by Lidl Hungary',
            'Note': 'Grocery shopping',
            'Currency': 'HUF'
        }
    ]
    
    column_mapping = {
        'Date': 'Date',
        'Amount': 'Amount', 
        'Title': 'Title',
        'Note': 'Note',
        'Account': 'Currency'
    }
    
    account_mapping = {
        'HUF': 'Hungarian',
        'USD': 'TransferWise',
        'EUR': 'EURO Wise'
    }
    
    print(f"\n🔥 Testing backend transformation:")
    
    # Call exactly like the backend does
    result = parser.transform_to_cashew(
        wise_data,
        column_mapping,
        "Wise",
        categorization_rules=None,
        default_category_rules=None,
        account_mapping=account_mapping
    )
    
    print(f"\n📊 Backend Transformation Results:")
    for i, row in enumerate(result):
        print(f"   Row {i}: {row['Category']} - {row['Title']} - Account: {row['Account']}")
    
    # Verify expected results
    success = True
    if len(result) != 2:
        print(f"❌ Expected 2 results, got {len(result)}")
        success = False
    
    if result[0]['Title'].startswith('Card transaction'):
        print(f"❌ Row 0 title not cleaned: {result[0]['Title']}")
        success = False
    else:
        print(f"✅ Row 0 title cleaned correctly")
    
    if result[1]['Category'] != 'Groceries':
        print(f"❌ Row 1 not categorized as Groceries: {result[1]['Category']}")
        success = False
    else:
        print(f"✅ Row 1 categorized as Groceries correctly")
    
    if result[0]['Account'] != 'Hungarian':
        print(f"❌ Row 0 account not mapped: {result[0]['Account']}")
        success = False
    else:
        print(f"✅ Row 0 account mapped correctly")
    
    if success:
        print(f"\n🎉 Backend integration test PASSED!")
        print(f"   ✅ Universal Transformer is working in your backend")
        print(f"   ✅ Description cleaning applied")
        print(f"   ✅ Smart categorization working")
        print(f"   ✅ Account mapping working")
    else:
        print(f"\n❌ Backend integration test FAILED!")

if __name__ == "__main__":
    test_backend_integration()
