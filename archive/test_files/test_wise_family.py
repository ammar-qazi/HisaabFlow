#!/usr/bin/env python3
"""Test the wise_family.conf implementation"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.transfer_detection.config_manager import ConfigurationManager

def test_wise_family_cleaning():
    """Test generic card transaction cleaning"""
    print("🧪 Testing wise_family.conf Description Cleaning")
    print("=" * 60)
    
    config_manager = ConfigurationManager("configs")
    
    # Test cases with various card transactions
    test_cases = [
        {
            'bank': 'wise_usd',
            'description': 'Card transaction of 12,295.00 HUF issued by Lidl Hu 108 Cegled Cegled',
            'expected': 'Lidl Hu 108 Cegled Cegled'
        },
        {
            'bank': 'wise_eur', 
            'description': 'Card transaction of 1,596.00 HUF issued by Aldi 142.sz. CEGLED',
            'expected': 'Aldi 142.sz. CEGLED'
        },
        {
            'bank': 'wise_huf',
            'description': 'Card transaction of 1,892.00 HUF issued by Otpmobl*Szamlazz Budapest',
            'expected': 'Otpmobl*Szamlazz Budapest'
        },
        {
            'bank': 'wise_usd',
            'description': 'Card transaction of 25,492.52 PKR issued by National Data Base A ISLAMABAD',
            'expected': 'National Data Base A ISLAMABAD'
        },
        {
            'bank': 'wise_huf',
            'description': 'Card transaction of 30.00 USD issued by Revolut**0540* Dublin',
            'expected': 'Revolut**0540* Dublin'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        bank = test_case['bank']
        original = test_case['description']
        expected = test_case['expected']
        
        print(f"\n{i}. Testing {bank}:")
        print(f"   Original: '{original}'")
        
        cleaned = config_manager.apply_description_cleaning(bank, original)
        print(f"   Cleaned:  '{cleaned}'")
        print(f"   Expected: '{expected}'")
        
        # Test categorization too
        category = config_manager.categorize_merchant(bank, cleaned)
        print(f"   Category: {category or 'None'}")
        
        if cleaned == expected:
            print("   ✅ PASS")
        else:
            print("   ❌ FAIL")

def test_family_config_loading():
    """Test that family configs are loaded"""
    print(f"\n🔧 Testing Family Config Loading")
    print("=" * 40)
    
    config_manager = ConfigurationManager("configs")
    
    print(f"Family configs loaded: {list(config_manager.family_configs.keys())}")
    
    if 'wise' in config_manager.family_configs:
        wise_family = config_manager.family_configs['wise']
        if wise_family.has_section('description_cleaning'):
            rules = dict(wise_family.items('description_cleaning'))
            print(f"Wise family cleaning rules: {len(rules)}")
            for rule_name, pattern in rules.items():
                print(f"  - {rule_name}: {pattern[:60]}...")
        
        if wise_family.has_section('categorization'):
            cats = dict(wise_family.items('categorization'))
            print(f"Wise family categorization rules: {len(cats)}")
            for pattern, category in list(cats.items())[:5]:
                print(f"  - {pattern}: {category}")
    else:
        print("❌ wise_family.conf not loaded!")

if __name__ == "__main__":
    try:
        test_family_config_loading()
        test_wise_family_cleaning()
        print(f"\n🎉 All tests completed!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
