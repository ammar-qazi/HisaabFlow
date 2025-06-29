#!/usr/bin/env python3
"""
Test script for UnifiedConfigService
Validates that the new unified service works correctly with existing configurations
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.shared.config import get_unified_config_service, reset_unified_config_service
from backend.shared.config.api_facade import APIConfigFacade
from backend.shared.config.bank_detection_facade import BankDetectionFacade


def test_unified_config_service():
    """Test basic UnifiedConfigService functionality"""
    print("🧪 Testing UnifiedConfigService...")
    
    # Reset singleton to ensure clean state
    reset_unified_config_service()
    
    # Get service instance
    service = get_unified_config_service()
    
    # Test app configuration
    print("📋 Testing app configuration...")
    user_name = service.get_user_name()
    date_tolerance = service.get_date_tolerance()
    confidence_threshold = service.get_confidence_threshold()
    
    print(f"  User name: {user_name}")
    print(f"  Date tolerance: {date_tolerance} hours")
    print(f"  Confidence threshold: {confidence_threshold}")
    
    # Test bank listing
    print("📋 Testing bank listing...")
    banks = service.list_banks()
    print(f"  Available banks: {banks}")
    
    if not banks:
        print("  ⚠️  No banks found - check if configs directory exists")
        return False
    
    # Test bank configuration loading
    print("📋 Testing bank configuration loading...")
    for bank in banks[:2]:  # Test first 2 banks
        bank_config = service.get_bank_config(bank)
        if bank_config:
            print(f"  ✅ {bank}: {bank_config.display_name}")
            print(f"     Detection patterns: {len(bank_config.detection_info.filename_patterns)}")
            print(f"     Column mappings: {len(bank_config.column_mapping)}")
        else:
            print(f"  ❌ Failed to load config for {bank}")
            return False
    
    # Test bank detection
    print("📋 Testing bank detection...")
    test_filenames = [
        "statement_20141677_USD_2025-01-04_2025-06-02.csv",
        "m-02-2025.csv",
        "account-statement_2024-04-01_2025-06-25_en-us_b9705c.csv"
    ]
    
    for filename in test_filenames:
        detected_bank = service.detect_bank(filename)
        print(f"  {filename} → {detected_bank}")
    
    print("✅ UnifiedConfigService tests passed!")
    return True


def test_api_facade():
    """Test APIConfigFacade backward compatibility"""
    print("🧪 Testing APIConfigFacade...")
    
    facade = APIConfigFacade()
    
    # Test list configs
    print("📋 Testing list configs...")
    configs_result = facade.list_configs()
    print(f"  Success: {configs_result.get('success')}")
    print(f"  Configurations count: {len(configs_result.get('configurations', []))}")
    
    if not configs_result.get('success'):
        print("  ❌ List configs failed")
        return False
    
    # Test load config
    print("📋 Testing load config...")
    configurations = configs_result.get('configurations', [])
    if configurations:
        config_name = configurations[0]  # Test first config
        load_result = facade.load_config(config_name)
        print(f"  Loading {config_name}: {load_result.get('success')}")
        
        if load_result.get('success'):
            print(f"  Bank name: {load_result.get('bank_name')}")
            config_data = load_result.get('config', {})
            print(f"  Config sections: {list(config_data.keys())}")
        else:
            print(f"  ❌ Load config failed: {load_result.get('error')}")
            return False
    
    print("✅ APIConfigFacade tests passed!")
    return True


def test_bank_detection_facade():
    """Test BankDetectionFacade backward compatibility"""
    print("🧪 Testing BankDetectionFacade...")
    
    facade = BankDetectionFacade()
    
    # Test get available banks
    print("📋 Testing get available banks...")
    banks = facade.get_available_banks()
    print(f"  Available banks: {banks}")
    
    if not banks:
        print("  ⚠️  No banks available")
        return False
    
    # Test get detection patterns
    print("📋 Testing get detection patterns...")
    patterns = facade.get_detection_patterns()
    print(f"  Detection patterns for {len(patterns)} banks")
    
    # Test bank config loading
    print("📋 Testing bank config loading...")
    for bank in banks[:2]:  # Test first 2 banks
        config = facade.get_bank_config(bank)
        if config:
            print(f"  ✅ {bank}: loaded ConfigParser object")
            sections = config.sections()
            print(f"     Sections: {sections}")
        else:
            print(f"  ❌ Failed to load config for {bank}")
            return False
    
    # Test column mapping
    print("📋 Testing column mapping...")
    if banks:
        bank = banks[0]
        mapping = facade.get_column_mapping(bank)
        print(f"  {bank} column mapping: {len(mapping)} mappings")
    
    print("✅ BankDetectionFacade tests passed!")
    return True


def test_csv_file_detection():
    """Test with actual CSV files if available"""
    print("🧪 Testing with actual CSV files...")
    
    # Look for sample CSV files
    sample_data_dir = "sample_data"
    if not os.path.exists(sample_data_dir):
        print("  ⚠️  No sample_data directory found, skipping CSV tests")
        return True
    
    csv_files = [f for f in os.listdir(sample_data_dir) if f.endswith('.csv')]
    if not csv_files:
        print("  ⚠️  No CSV files found in sample_data, skipping CSV tests")
        return True
    
    service = get_unified_config_service()
    facade = BankDetectionFacade()
    
    print(f"📋 Testing detection with {len(csv_files)} CSV files...")
    
    for csv_file in csv_files:  # Test ALL files
        file_path = os.path.join(sample_data_dir, csv_file)
        
        # Test unified service detection
        detected_bank = service.detect_bank(csv_file)
        print(f"  {csv_file} → {detected_bank if detected_bank else 'None'}")
        
        # Test header detection if bank detected
        if detected_bank:
            header_info = facade.detect_header_row(file_path, detected_bank)
            print(f"    Header row: {header_info.get('header_row')}, confidence: {header_info.get('confidence', 0):.1f}")
        else:
            print(f"    No bank detected - skipping header detection")
    
    print("✅ CSV file detection tests passed!")
    return True


def main():
    """Run all tests"""
    print("🧪 UnifiedConfigService Validation Tests")
    print("=" * 50)
    
    all_passed = True
    
    try:
        # Test core service
        if not test_unified_config_service():
            all_passed = False
        print()
        
        # Test API facade
        if not test_api_facade():
            all_passed = False
        print()
        
        # Test bank detection facade
        if not test_bank_detection_facade():
            all_passed = False
        print()
        
        # Test with actual CSV files
        if not test_csv_file_detection():
            all_passed = False
        print()
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # Results
    print("=" * 50)
    if all_passed:
        print("✅ All UnifiedConfigService tests PASSED!")
        print("🎯 Ready for migration to unified configuration system")
        return 0
    else:
        print("❌ Some tests FAILED!")
        print("🔧 Fix issues before proceeding with migration")
        return 1


if __name__ == "__main__":
    exit(main())