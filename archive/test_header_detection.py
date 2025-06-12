#!/usr/bin/env python3
"""
Test script for header detection functionality
"""
import sys
import os

# Add backend path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

try:
    from bank_detection.config_manager import BankConfigManager
    from bank_detection.bank_detector import BankDetector
    print("✅ Successfully imported modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_header_detection():
    """Test header detection with NayaPay sample file"""
    print("🧪 Testing Header Detection System")
    print("=" * 50)
    
    # Initialize components
    config_manager = BankConfigManager()
    bank_detector = BankDetector(config_manager)
    
    # Test with NayaPay sample file
    sample_file = "sample_data/m-02-2025.csv"
    
    if not os.path.exists(sample_file):
        print(f"❌ Sample file not found: {sample_file}")
        return False
    
    print(f"📄 Testing with file: {sample_file}")
    
    # Test 1: Bank detection
    print("\n🔍 Test 1: Bank Detection")
    try:
        # Read file content for detection
        with open(sample_file, 'r', encoding='utf-8') as f:
            content = f.read()[:1000]  # First 1000 chars
        
        # Extract headers from first few lines  
        lines = content.split('\n')[:15]
        headers = []
        for line in lines:
            if 'TIMESTAMP' in line.upper():
                headers = line.split(',')
                break
        
        filename = os.path.basename(sample_file)
        detection_result = bank_detector.detect_bank(filename, content, headers)
        
        print(f"   🏦 Detected bank: {detection_result.bank_name}")
        print(f"   📊 Confidence: {detection_result.confidence:.2f}")
        print(f"   📋 Reasons: {detection_result.reasons}")
        
        if detection_result.bank_name == 'nayapay':
            print("   ✅ Bank detection successful!")
        else:
            print("   ❌ Bank detection failed!")
            return False
            
    except Exception as e:
        print(f"   ❌ Bank detection error: {e}")
        return False
    
    # Test 2: Header row detection
    print("\n🔍 Test 2: Header Row Detection")
    try:
        header_result = config_manager.detect_header_row(sample_file, 'nayapay')
        
        print(f"   📍 Detected header row: {header_result['header_row']}")
        print(f"   📊 Data start row: {header_result['data_start_row']}")
        print(f"   📋 Headers found: {header_result['headers']}")
        print(f"   🔧 Method used: {header_result['method']}")
        
        # Verify the headers are correct
        expected_headers = ['TIMESTAMP', 'TYPE', 'DESCRIPTION', 'AMOUNT', 'BALANCE']
        actual_headers = header_result['headers']
        
        if header_result['header_row'] == 13:  # Should be row 13 (0-indexed)
            print("   ✅ Header row detection successful!")
        else:
            print(f"   ❌ Expected header row 13, got {header_result['header_row']}")
            return False
            
        # Check headers match
        headers_match = all(expected in actual_headers for expected in expected_headers)
        if headers_match:
            print("   ✅ Header content validation successful!")
        else:
            print(f"   ❌ Header mismatch. Expected: {expected_headers}, Got: {actual_headers}")
            return False
            
    except Exception as e:
        print(f"   ❌ Header detection error: {e}")
        import traceback
        print(f"   📚 Traceback: {traceback.format_exc()}")
        return False
    
    # Test 3: CSV Config retrieval
    print("\n🔍 Test 3: CSV Config Retrieval")
    try:
        csv_config = config_manager.get_csv_config('nayapay')
        
        print(f"   📍 Header row from config: {csv_config['header_row']}")
        print(f"   📊 Data start row from config: {csv_config['data_start_row']}")
        print(f"   📋 Expected headers from config: {csv_config['expected_headers']}")
        print(f"   🔧 Detection method: {csv_config['header_detection_method']}")
        
        if csv_config['header_row'] == 13:
            print("   ✅ CSV config retrieval successful!")
        else:
            print(f"   ❌ Expected header row 13 from config, got {csv_config['header_row']}")
            return False
            
    except Exception as e:
        print(f"   ❌ CSV config error: {e}")
        return False
    
    print("\n🎉 All tests passed! Header detection system is working correctly.")
    return True

if __name__ == "__main__":
    success = test_header_detection()
    if success:
        print("\n✅ Header detection implementation is ready for Phase 2!")
    else:
        print("\n❌ Header detection implementation needs fixes.")
        sys.exit(1)
