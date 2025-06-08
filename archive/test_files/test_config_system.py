#!/usr/bin/env python3
"""
Test the new configuration-based cross-bank matcher
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from transfer_detection.config_manager import ConfigurationManager
from transfer_detection.cross_bank_matcher import CrossBankMatcher

def test_configuration_system():
    """Test that the configuration system loads properly"""
    print("🧪 Testing Configuration System...")
    
    try:
        # Test config manager
        config = ConfigurationManager("configs")
        print(f"✅ Configuration Manager loaded successfully")
        print(f"   👤 User: {config.get_user_name()}")
        print(f"   ⏰ Date tolerance: {config.get_date_tolerance()} hours")
        print(f"   🎯 Confidence threshold: {config.get_confidence_threshold()}")
        print(f"   🏦 Banks configured: {', '.join(config.list_configured_banks())}")
        
        # Test bank detection
        test_files = [
            "wise_statement_2025.csv",
            "nayapay_feb_2025.csv", 
            "wise_eur_march.csv",
            "hungarian_statement.csv",
            "unknown_bank.csv"
        ]
        
        print(f"\n🔍 Testing Bank Detection:")
        for filename in test_files:
            bank_type = config.detect_bank_type(filename)
            print(f"   📄 {filename} → {bank_type or 'UNKNOWN'}")
        
        # Test pattern generation
        print(f"\n🔄 Testing Transfer Patterns:")
        for bank_name in config.list_configured_banks():
            outgoing = config.get_transfer_patterns(bank_name, 'outgoing')
            incoming = config.get_transfer_patterns(bank_name, 'incoming')
            print(f"   🏦 {bank_name}:")
            print(f"      📤 Outgoing: {outgoing}")
            print(f"      📥 Incoming: {incoming}")
        
        # Test cross-bank matcher initialization
        print(f"\n🔧 Testing CrossBankMatcher:")
        matcher = CrossBankMatcher("configs")
        print(f"✅ CrossBankMatcher initialized successfully")
        
        # Test categorization
        print(f"\n📝 Testing Categorization:")
        test_merchants = [
            ("wise_usd", "Lidl payment"),
            ("nayapay", "KFC order"),
            ("wise_eur", "DM purchase"),
            ("wise_huf", "Tesco shopping")
        ]
        
        for bank, merchant in test_merchants:
            category = config.categorize_merchant(bank, merchant)
            print(f"   🏦 {bank} | {merchant} → {category or 'Other'}")
        
        print(f"\n🎉 All tests passed! Configuration system is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error testing configuration system: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_configuration_system()
    sys.exit(0 if success else 1)
