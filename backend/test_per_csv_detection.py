"""
Test the new bank-agnostic multi-CSV processing (simplified)
"""
import sys
import os
import json

# Add backend path for imports
backend_path = '/home/ammar/claude_projects/bank_statement_parser/backend'
sys.path.insert(0, backend_path)

from bank_detection import BankDetector, BankConfigManager

# Copy the functions we need to test
def _create_fallback_mapping(sample_row: dict) -> dict:
    """Create a fallback column mapping when bank detection fails"""
    mapping = {}
    
    # Standard mappings based on common column names
    for key in sample_row.keys():
        key_lower = key.lower()
        
        if 'date' in key_lower or 'timestamp' in key_lower:
            mapping['Date'] = key
        elif 'amount' in key_lower:
            mapping['Amount'] = key
        elif 'description' in key_lower or 'title' in key_lower:
            mapping['Title'] = key
        elif 'note' in key_lower or 'type' in key_lower or 'reference' in key_lower:
            mapping['Note'] = key
        elif 'balance' in key_lower:
            mapping['Balance'] = key
        elif 'currency' in key_lower:
            mapping['Currency'] = key
    
    print(f"🔧 Created fallback mapping: {mapping}")
    return mapping

def test_per_csv_detection():
    """Test bank detection per CSV file"""
    
    print("🧪 Testing Per-CSV Bank Detection")
    print("=" * 50)
    
    # Initialize detection system
    config_manager = BankConfigManager()
    detector = BankDetector(config_manager)
    
    # Mock NayaPay data
    nayapay_data = [
        {
            'TIMESTAMP': '02 Feb 2025 11:17 PM',
            'TYPE': 'Raast Out', 
            'DESCRIPTION': 'Outgoing fund transfer to Surraiya Riaz',
            'AMOUNT': '-5,000',
            'BALANCE': '872.40'
        }
    ]
    
    # Mock Wise data
    wise_data = [
        {
            'Date': '02-06-25',
            'Amount': '-254.10',
            'Currency': 'USD',
            'Description': 'Sent money to Usama Qazi',
            'Payment Reference': 'eid-ul-adha-qurbani'
        }
    ]
    
    # Test NayaPay detection
    print(f"\n📁 Testing NayaPay detection:")
    nayapay_result = detector.detect_bank_from_data('nayapay_feb.csv', nayapay_data)
    print(f"   🎯 Result: {nayapay_result}")
    
    if nayapay_result.bank_name != 'unknown':
        nayapay_mapping = config_manager.get_column_mapping(nayapay_result.bank_name)
        print(f"   🗺️ Column mapping: {nayapay_mapping}")
        
        # Apply mapping
        standardized_nayapay = {}
        for target_col, source_col in nayapay_mapping.items():
            if source_col in nayapay_data[0]:
                standardized_nayapay[target_col] = nayapay_data[0][source_col]
        print(f"   📄 Standardized: {standardized_nayapay}")
    
    # Test Wise detection  
    print(f"\n📁 Testing Wise detection:")
    wise_result = detector.detect_bank_from_data('wise_USD.csv', wise_data)
    print(f"   🎯 Result: {wise_result}")
    
    if wise_result.bank_name != 'unknown':
        wise_mapping = config_manager.get_column_mapping(wise_result.bank_name)
        print(f"   🗺️ Column mapping: {wise_mapping}")
        
        # Apply mapping
        standardized_wise = {}
        for target_col, source_col in wise_mapping.items():
            if source_col in wise_data[0]:
                standardized_wise[target_col] = wise_data[0][source_col]
        print(f"   📄 Standardized: {standardized_wise}")
    
    print(f"\n🎯 Analysis:")
    print(f"   ✅ NayaPay: {nayapay_result.bank_name} (confidence: {nayapay_result.confidence:.2f})")
    print(f"   ✅ Wise: {wise_result.bank_name} (confidence: {wise_result.confidence:.2f})")
    
    # Check Title field mapping
    nayapay_title = standardized_nayapay.get('Title', 'MISSING')
    wise_title = standardized_wise.get('Title', 'MISSING') 
    
    print(f"\n🔍 Title Field Check (Bug 6 validation):")
    print(f"   NayaPay Title: '{nayapay_title}'")
    print(f"   Wise Title: '{wise_title}'")
    
    if nayapay_title != 'MISSING' and wise_title != 'MISSING':
        print(f"   ✅ Both banks have populated Title fields - Bug 6 would be FIXED!")
    else:
        print(f"   ❌ Missing Title fields detected - Bug 6 still present")

if __name__ == "__main__":
    test_per_csv_detection()
