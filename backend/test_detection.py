"""
Test the bank detection engine with sample data
"""
import sys
import os

# Add backend path for imports
backend_path = '/home/ammar/claude_projects/bank_statement_parser/backend'
sys.path.insert(0, backend_path)

from bank_detection import BankDetector, BankConfigManager

def test_bank_detection():
    """Test bank detection with sample CSV files"""
    
    print("🧪 Testing Bank Detection Engine")
    print("=" * 50)
    
    # Initialize detection system
    config_manager = BankConfigManager()
    detector = BankDetector(config_manager)
    
    print(f"🏦 Available banks: {detector.get_available_banks()}")
    print()
    
    # Test files
    sample_dir = '/home/ammar/claude_projects/bank_statement_parser/sample_data'
    test_files = [
        'nayapay_statement.csv',
        'wise_USD.csv',
        'nayapay_feb.csv'
    ]
    
    for filename in test_files:
        file_path = os.path.join(sample_dir, filename)
        
        if not os.path.exists(file_path):
            print(f"⚠️ File not found: {filename}")
            continue
            
        print(f"📁 Testing file: {filename}")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
            content = ''.join(lines[:10])  # First 10 lines for detection
            
            # Find headers (look for line with comma-separated values that look like headers)
            headers = []
            for line in lines:
                if ',' in line and not line.strip().startswith('#'):
                    # Check if this looks like a header line
                    parts = [p.strip().strip('"') for p in line.split(',')]
                    if len(parts) >= 3:  # Minimum columns
                        # Look for header-like content (no pure numbers)
                        # Also check for known header patterns
                        line_upper = line.upper()
                        if ('TIMESTAMP' in line_upper or 'DATE' in line_upper or 
                            'AMOUNT' in line_upper or 'DESCRIPTION' in line_upper):
                            headers = parts
                            break
                        elif not all(p.replace('.', '').replace('-', '').replace('+', '').replace(',', '').isdigit() for p in parts[:3] if p):
                            headers = parts
                            break
            
            print(f"   📄 Headers detected: {headers[:5]}...")  # Show first 5
            print(f"   📖 Content preview: {content[:100]}...")
            
            # Detect bank
            result = detector.detect_bank(filename, content, headers)
            
            print(f"   🎯 Detection result: {result}")
            print(f"   ✅ Confident: {result.is_confident}")
            
            # Get column mapping for detected bank
            if result.bank_name != 'unknown':
                mapping = config_manager.get_column_mapping(result.bank_name)
                print(f"   🗺️ Column mapping: {mapping}")
            
            print()

if __name__ == "__main__":
    test_bank_detection()
