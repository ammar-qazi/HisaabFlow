#!/usr/bin/env python3
"""
Test the updated transfer detection system with configuration
"""

import sys
import os
sys.path.append('.')

from backend.transfer_detection import TransferDetector, ConfigurationManager

def test_configuration_system():
    """Test that the configuration system is properly integrated"""
    
    print("🧪 TESTING UPDATED TRANSFER DETECTION SYSTEM")
    print("=" * 60)
    
    # Test 1: Configuration Manager
    print("\n📋 Testing Configuration Manager...")
    config = ConfigurationManager("configs")
    
    print(f"👤 User name: {config.get_user_name()}")
    print(f"📅 Date tolerance: {config.get_date_tolerance()} hours")
    print(f"🎯 Confidence threshold: {config.get_confidence_threshold()}")
    print(f"🏦 Configured banks: {config.list_configured_banks()}")
    
    # Test 2: Bank detection
    print("\n🏦 Testing Bank Detection...")
    test_files = [
        "wise_usd_statement.csv",
        "wise_eur_statement.csv", 
        "wise_huf_statement.csv",
        "nayapay_statement.csv",
        "unknown_bank.csv"
    ]
    
    for file_name in test_files:
        bank_type = config.detect_bank_type(file_name)
        print(f"   📁 {file_name} → {bank_type or 'unknown'}")
    
    # Test 3: Transfer patterns
    print("\n🔄 Testing Transfer Patterns...")
    user_name = config.get_user_name()
    
    for bank_name in config.list_configured_banks():
        outgoing_patterns = config.get_transfer_patterns(bank_name, 'outgoing')
        incoming_patterns = config.get_transfer_patterns(bank_name, 'incoming')
        
        print(f"   🏦 {bank_name}:")
        print(f"      📤 Outgoing: {outgoing_patterns}")
        print(f"      📥 Incoming: {incoming_patterns}")
    
    # Test 4: TransferDetector initialization 
    print("\n🔍 Testing TransferDetector...")
    try:
        detector = TransferDetector("configs")
        print("   ✅ TransferDetector initialized successfully")
        print(f"   👤 User: {detector.user_name}")
        print(f"   📅 Date tolerance: {detector.date_tolerance_hours} hours")
        print(f"   🏦 Banks loaded: {len(detector.config.list_configured_banks())}")
    except Exception as e:
        print(f"   ❌ Error initializing TransferDetector: {e}")
        return False
    
    # Test 5: Mock transfer detection
    print("\n📊 Testing Transfer Detection (Mock Data)...")
    
    mock_csv_data = [
        {
            'file_name': 'wise_usd_statement.csv',
            'data': [
                {
                    'Date': '2025-01-15',
                    'Description': f'Send money to {user_name}',
                    'Amount': '-100.00',
                    'Currency': 'USD',
                    'Exchange To Amount': '95.50',
                    'Exchange To': 'EUR'
                }
            ]
        },
        {
            'file_name': 'wise_eur_statement.csv', 
            'data': [
                {
                    'Date': '2025-01-15',
                    'Description': f'Received money from {user_name}',
                    'Amount': '95.50',
                    'Currency': 'EUR'
                }
            ]
        }
    ]
    
    try:
        results = detector.detect_transfers(mock_csv_data)
        print(f"   ✅ Transfer detection completed")
        print(f"   📊 Found {len(results['transfers'])} transfer pairs")
        print(f"   💱 Currency conversions: {results['summary']['currency_conversions']}")
        print(f"   🔄 Cross-bank transfers: {results['summary']['other_transfers']}")
        
    except Exception as e:
        print(f"   ❌ Error in transfer detection: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✅ ALL TESTS PASSED!")
    print("🎉 Configuration system is properly integrated!")
    return True

if __name__ == "__main__":
    success = test_configuration_system()
    sys.exit(0 if success else 1)
