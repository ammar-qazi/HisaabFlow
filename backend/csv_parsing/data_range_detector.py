"""
Data Range Detector Module - Automatic detection of transaction data location
"""
from typing import Dict, List

class DataRangeDetector:
    """Detects where transaction data starts in CSV files"""
    
    def detect_data_range(self, lines: List[List[str]]) -> Dict:
        """Auto-detect where the actual transaction data starts with improved bank detection"""
        try:
            if not lines:
                raise ValueError("No data found in file")
            
            print(f"🔍 Detecting data range in file with {len(lines)} lines")
            
            # Look for rows that contain transaction headers
            data_start_row = None
            
            for idx, row in enumerate(lines):
                # Convert row to lowercase string for searching
                row_text = ' '.join([str(cell).lower() for cell in row if cell])
                
                print(f"   Row {idx:2}: {len(row)} cols -> {row_text[:80]}..." if len(row_text) > 80 else f"   Row {idx:2}: {len(row)} cols -> {row_text}")
                
                # Enhanced NayaPay detection: look for the specific transaction header pattern
                # Must have exactly these 5 columns: TIMESTAMP, TYPE, DESCRIPTION, AMOUNT, BALANCE
                if (len(row) == 5 and 
                    any('timestamp' in str(cell).lower() for cell in row) and
                    any('type' in str(cell).lower() for cell in row) and
                    any('description' in str(cell).lower() for cell in row) and
                    any('amount' in str(cell).lower() for cell in row) and
                    any('balance' in str(cell).lower() for cell in row)):
                    
                    data_start_row = idx
                    print(f"   ✅ Found NayaPay transaction headers at row {idx}: {row}")
                    break
                
                # Skip problematic rows we know about
                if ('opening balance' in row_text and 'closing balance' in row_text):
                    print(f"   ⚠️  Skipping balance summary row {idx}")
                    continue
            
            if data_start_row is None:
                # Fallback: look for any row with transaction-like headers
                for idx, row in enumerate(lines):
                    row_text = ' '.join([str(cell).lower() for cell in row if cell])
                    if any(indicator in row_text for indicator in ['timestamp', 'date', 'amount', 'description']):
                        if not ('opening balance' in row_text or 'closing balance' in row_text):
                            data_start_row = idx
                            print(f"   🔄 Fallback: Found headers at row {idx}")
                            break
            
            print(f"   🎯 Final detection result: row {data_start_row}")
            
            return {
                'success': True,
                'suggested_header_row': data_start_row,
                'total_rows': len(lines)
            }
        except Exception as e:
            print(f"   ❌ Detection error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
