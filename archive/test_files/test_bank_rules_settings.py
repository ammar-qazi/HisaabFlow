#!/usr/bin/env python3

import sys
import os
sys.path.append('/home/ammar/claude_projects/bank_statement_parser')

from transformation.universal_transformer import UniversalTransformer

def test_bank_rules_settings():
    """Test bank-specific rules can be enabled/disabled via settings"""
    print("🧪 Testing Bank Rules Settings Feature")
    
    # Initialize transformer
    transformer = UniversalTransformer()
    
    # Test sample data that would trigger different bank rules
    test_data = [
        {
            'Date': '2025-06-01',
            'Amount': -1000.0,  # Small amount that would trigger NayaPay ride-hailing rule
            'Title': 'Outgoing fund transfer to Driver',
            'Note': 'Raast Out'
        }
    ]
    
    column_mapping = {
        'Date': 'Date',
        'Amount': 'Amount', 
        'Title': 'Title',
        'Note': 'Note'
    }
    
    print(f"\n📊 Test Data: {test_data[0]}")
    
    # Test 1: All rules enabled (default)
    print(f"\n🧪 Test 1: All rules enabled")
    result1 = transformer.transform_to_cashew(
        test_data, column_mapping, "NayaPay", None, {
            'enableNayaPayRules': True,
            'enableTransferwiseRules': True,
            'enableUniversalRules': True
        }
    )
    print(f"   Result: Category='{result1[0]['Category']}', Title='{result1[0]['Title']}'")
    
    # Test 2: NayaPay rules disabled
    print(f"\n🧪 Test 2: NayaPay rules disabled")
    result2 = transformer.transform_to_cashew(
        test_data, column_mapping, "NayaPay", None, {
            'enableNayaPayRules': False,
            'enableTransferwiseRules': True,
            'enableUniversalRules': True
        }
    )
    print(f"   Result: Category='{result2[0]['Category']}', Title='{result2[0]['Title']}'")
    
    # Test 3: Only universal rules enabled
    print(f"\n🧪 Test 3: Only universal rules enabled")
    result3 = transformer.transform_to_cashew(
        test_data, column_mapping, "NayaPay", None, {
            'enableNayaPayRules': False,
            'enableTransferwiseRules': False,
            'enableUniversalRules': True
        }
    )
    print(f"   Result: Category='{result3[0]['Category']}', Title='{result3[0]['Title']}'")
    
    # Test 4: All rules disabled
    print(f"\n🧪 Test 4: All rules disabled")
    result4 = transformer.transform_to_cashew(
        test_data, column_mapping, "NayaPay", None, {
            'enableNayaPayRules': False,
            'enableTransferwiseRules': False,
            'enableUniversalRules': False
        }
    )
    print(f"   Result: Category='{result4[0]['Category']}', Title='{result4[0]['Title']}'")
    
    print(f"\n✅ Bank Rules Settings Test Complete!")
    print(f"📋 Summary:")
    print(f"   • All enabled: {result1[0]['Category']} - {result1[0]['Title']}")
    print(f"   • NayaPay disabled: {result2[0]['Category']} - {result2[0]['Title']}")
    print(f"   • Only universal: {result3[0]['Category']} - {result3[0]['Title']}")
    print(f"   • All disabled: {result4[0]['Category']} - {result4[0]['Title']}")

if __name__ == "__main__":
    test_bank_rules_settings()
