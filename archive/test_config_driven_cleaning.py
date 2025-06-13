#!/usr/bin/env python3
"""
Test script for config-driven description cleaning and transfer detection
"""
import sys
import os

# Add backend path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from transfer_detection.config_manager import ConfigurationManager

def test_description_cleaning():
    """Test bank-specific description cleaning"""
    print("🧹 Testing Description Cleaning")
    print("=" * 50)
    
    config = ConfigurationManager("configs")
    
    # Test NayaPay cleaning rules
    test_cases = [
        {
            'bank': 'nayapay',
            'original': 'Outgoing fund transfer to Surraiya Riaz - Monthly allowance',
            'expected': 'Zunayyara Quran'
        },
        {
            'bank': 'nayapay', 
            'original': 'Card transaction at Uber Technologies',
            'expected': 'Uber Ride'
        },
        {
            'bank': 'nayapay',
            'original': 'Purchase at Savemart Supermarket DHA',
            'expected': 'Savemart'
        },
        {
            'bank': 'wise_eur',
            'original': 'Purchase at Lidl Deutschland',
            'expected': 'Lidl'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        bank = test_case['bank']
        original = test_case['original'] 
        expected = test_case['expected']
        
        print(f"\n{i}. Testing {bank}:")
        print(f"   Original: '{original}'")
        
        cleaned = config.apply_description_cleaning(bank, original)
        print(f"   Cleaned:  '{cleaned}'")
        print(f"   Expected: '{expected}'")
        
        # Check if transformation worked
        if expected.lower() in cleaned.lower():
            print(f"   ✅ SUCCESS")
        else:
            print(f"   ❌ FAILED")

def test_transfer_pattern_extraction():
    """Test flexible name extraction from transfer patterns"""
    print("\n\n🔍 Testing Transfer Pattern Name Extraction")
    print("=" * 50)
    
    config = ConfigurationManager("configs")
    
    test_cases = [
        {
            'bank': 'nayapay',
            'pattern': 'Outgoing fund transfer to {name}',
            'description': 'Outgoing fund transfer to Surraiya Riaz',
            'expected_name': 'Surraiya Riaz'
        },
        {
            'bank': 'nayapay',
            'pattern': 'Incoming fund transfer from {name}',
            'description': 'Incoming fund transfer from John Smith',
            'expected_name': 'John Smith'
        },
        {
            'bank': 'wise_eur',
            'pattern': 'Send money to {name}',
            'description': 'Send money to Maria Garcia',
            'expected_name': 'Maria Garcia'
        },
        {
            'bank': 'wise_eur',
            'pattern': 'Received money from {name}',
            'description': 'Received money from Business Partner LLC',
            'expected_name': 'Business Partner LLC'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        pattern = test_case['pattern']
        description = test_case['description']
        expected_name = test_case['expected_name']
        
        print(f"\n{i}. Testing pattern: '{pattern}'")
        print(f"   Description: '{description}'")
        
        extracted_name = config.extract_name_from_transfer_pattern(pattern, description)
        print(f"   Extracted:   '{extracted_name}'")
        print(f"   Expected:    '{expected_name}'")
        
        if extracted_name == expected_name:
            print(f"   ✅ SUCCESS")
        else:
            print(f"   ❌ FAILED")

def test_bank_configs():
    """Test loading of bank configurations"""
    print("\n\n⚙️ Testing Bank Configuration Loading")
    print("=" * 50)
    
    config = ConfigurationManager("configs")
    
    banks = config.list_configured_banks()
    print(f"Configured banks: {banks}")
    
    for bank in banks:
        print(f"\n📋 {bank} configuration:")
        bank_config = config.get_bank_config(bank)
        if bank_config:
            print(f"   Currency: {bank_config.currency_primary}")
            print(f"   Account: {bank_config.cashew_account}")
            print(f"   Outgoing patterns: {len(bank_config.outgoing_patterns)}")
            print(f"   Incoming patterns: {len(bank_config.incoming_patterns)}")
            print(f"   Description cleaning rules: {len(bank_config.description_cleaning_rules)}")
            print(f"   Categorization rules: {len(bank_config.categorization_rules)}")
        else:
            print(f"   ❌ Failed to load config")

if __name__ == "__main__":
    print("🔧 CONFIG-DRIVEN CLEANING & TRANSFER DETECTION TEST")
    print("=" * 60)
    
    try:
        test_bank_configs()
        test_description_cleaning()
        test_transfer_pattern_extraction()
        
        print("\n\n🎉 All tests completed!")
        print("Check the results above to verify functionality.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
