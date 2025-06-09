"""
Test the bank detection engine with sample data (improved header detection)
"""
import sys
import os

# Add backend path for imports
backend_path = '/home/ammar/claude_projects/bank_statement_parser/backend'
sys.path.insert(0, backend_path)

from bank_detection import BankDetector, BankConfigManager

def find_csv_headers(lines):
    """Find the actual CSV headers in the file"""
    potential_headers = []
    
    for i, line in enumerate(lines):
        if ',' in line and line.strip():
            parts = [p.strip().strip('"').strip("'") for p in line.split(',')]
            
            # Skip lines with less than 3 columns
            if len(parts) < 3:
                continue
                
            # Skip lines that are mostly empty
            if sum(1 for p in parts if p) < 3:
                continue
            
            # Check for header-like patterns
            line_upper = line.upper()
            header_keywords = ['TIMESTAMP', 'DATE', 'AMOUNT', 'DESCRIPTION', 'TYPE', 'BALANCE', 
                             'CURRENCY', 'PAYMENT', 'REFERENCE', 'TITLE', 'NOTE']
            
            keyword_matches = sum(1 for keyword in header_keywords if keyword in line_upper)
            
            # If we find header keywords, this is likely the header
            if keyword_matches >= 2:
                potential_headers.append((i, parts, keyword_matches))
            
            # Also check for lines that don't contain numbers in first few columns (header-like)
            non_numeric_count = 0
            for part in parts[:min(5, len(parts))]:
                if part and not part.replace('.', '').replace('-', '').replace('+', '').replace(',', '').isdigit():
                    non_numeric_count += 1
            
            if non_numeric_count >= 3:
                potential_headers.append((i, parts, keyword_matches + non_numeric_count * 0.5))
    
    # Sort by score and return the best match
    if potential_headers:
        potential_headers.sort(key=lambda x: x[2], reverse=True)
        best_match = potential_headers[0]
        print(f"   🎯 Found headers at line {best_match[0] + 1}: {best_match[1][:5]}... (score: {best_match[2]:.1f})")
        return best_match[1]
    
    return []

def test_bank_detection():
    """Test bank detection with sample CSV files"""
    
    print("🧪 Testing Bank Detection Engine (Improved)")
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
            content = ''.join(lines[:15])  # More lines for better detection
            
            # Find headers using improved detection
            headers = find_csv_headers(lines)
            
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
