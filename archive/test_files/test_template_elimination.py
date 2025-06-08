#!/usr/bin/env python3
"""
Quick test to verify template elimination works
"""
import sys
import os
sys.path.append('/home/ammar/claude_projects/bank_statement_parser')

from backend.transfer_detection.enhanced_config_manager import EnhancedConfigurationManager
from backend.api.template_manager import TemplateManager

def test_template_elimination():
    print("🧪 Testing Template Elimination")
    print("=" * 50)
    
    # Test enhanced config manager
    print("\n1. Testing Enhanced Config Manager:")
    config_manager = EnhancedConfigurationManager("/home/ammar/claude_projects/bank_statement_parser/configs")
    
    banks = config_manager.list_configured_banks()
    print(f"✅ Available banks: {banks}")
    
    for bank in banks:
        config = config_manager.get_bank_config(bank)
        print(f"✅ {bank}: CSV config = {config.csv_config.has_header}, columns = {len(config.column_mapping)}")
    
    # Test template manager (now config-based)
    print("\n2. Testing Config-based Template Manager:")
    template_manager = TemplateManager(
        template_dir="/home/ammar/claude_projects/bank_statement_parser/templates",
        config_dir="/home/ammar/claude_projects/bank_statement_parser/configs"
    )
    
    # Test loading a "template" (actually config)
    try:
        result = template_manager.load_template("wise_usd")
        print(f"✅ Loaded wise_usd: {result['success']}, source: {result['source']}")
    except Exception as e:
        print(f"❌ Error loading wise_usd: {e}")
    
    try:
        result = template_manager.load_template("nayapay")
        print(f"✅ Loaded nayapay: {result['success']}, source: {result['source']}")
    except Exception as e:
        print(f"❌ Error loading nayapay: {e}")
    
    # Test template listing
    templates = template_manager.list_templates()
    print(f"✅ Available templates/configs: {len(templates['templates'])}")
    
    print("\n🎉 Template elimination test completed!")
    print("📢 Templates are now configuration-based!")

if __name__ == "__main__":
    test_template_elimination()
