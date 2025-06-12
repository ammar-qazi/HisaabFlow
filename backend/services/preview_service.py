"""
Preview service for CSV files with bank-aware header detection
"""
import os
import sys

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from robust_csv_parser import RobustCSVParser
    from bank_detection import BankDetector, BankConfigManager
except ImportError:
    # Fallback path for import issues
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, backend_path)
    from robust_csv_parser import RobustCSVParser
    from bank_detection import BankDetector, BankConfigManager


class PreviewService:
    """Service for handling CSV file previews with bank detection"""
    
    def __init__(self):
        self.robust_parser = RobustCSVParser()
        self.bank_config_manager = BankConfigManager()
        self.bank_detector = BankDetector(self.bank_config_manager)
    
    def preview_csv_file(self, file_path: str, filename: str, encoding: str = "utf-8", header_row: int = None):
        """
        Preview CSV file with bank-aware header detection
        
        Args:
            file_path: Path to the CSV file
            filename: Original filename for bank detection
            encoding: File encoding
            header_row: Manual header row override
            
        Returns:
            dict: Preview result with bank detection info
        """
        print(f"🕵️‍♂️ Preview request for file: {filename}")
        
        try:
            # Step 1: Detect bank first for header detection
            print(f"🔍 Step 1: Detecting bank for header detection...")
            
            # Read first few lines for bank detection
            preview_result = self.robust_parser.preview_csv(file_path, encoding, header_row=0)
            if not preview_result['success']:
                return {
                    'success': False,
                    'error': preview_result['error']
                }
            
            # Extract content for bank detection
            preview_data = preview_result['preview_data']
            content_lines = []
            headers_detected = []
            
            for row in preview_data[:10]:  # Use first 10 rows for detection
                row_text = ' '.join([str(cell) for cell in row.values() if cell])
                content_lines.append(row_text)
                
                # Also collect potential headers
                row_values = list(row.values())
                if row_values and any(cell for cell in row_values):
                    headers_detected = row_values
            
            content_for_detection = '\n'.join(content_lines)
            
            # Detect bank using filename and content
            bank_detection = self.bank_detector.detect_bank(filename, content_for_detection, headers_detected)
            print(f"🏦 Detected bank: {bank_detection.bank_name} (confidence: {bank_detection.confidence:.2f})")
            
            # Step 2: Use bank-specific header detection if available
            detected_header_row = header_row
            header_detection_info = None
            
            if bank_detection.bank_name != 'unknown' and bank_detection.confidence > 0.5:
                print(f"🔍 Step 2: Using bank-specific header detection for {bank_detection.bank_name}")
                header_detection_result = self.bank_config_manager.detect_header_row(
                    file_path, bank_detection.bank_name, encoding
                )
                
                if header_detection_result['success']:
                    detected_header_row = header_detection_result['header_row']
                    header_detection_info = header_detection_result
                    print(f"📋 Bank-specific header detection: row {detected_header_row}")
                else:
                    print(f"⚠️ Bank-specific header detection failed: {header_detection_result.get('error', 'Unknown error')}")
            
            # Step 3: Generate enhanced preview with proper headers
            print(f"🔍 Step 3: Generating enhanced preview with header_row={detected_header_row}")
            
            # Use the detected header row for the final preview
            result = self.robust_parser.preview_csv(file_path, encoding, detected_header_row)
            if not result['success']:
                return {
                    'success': False,
                    'error': result['error']
                }
            
            # Add bank detection and header detection info to response
            result['bank_detection'] = {
                'detected_bank': bank_detection.bank_name,
                'confidence': bank_detection.confidence,
                'reasons': bank_detection.reasons
            }
            
            if header_detection_info:
                result['header_detection'] = header_detection_info
                result['suggested_header_row'] = header_detection_info['header_row']
                result['suggested_data_start_row'] = header_detection_info['data_start_row']
            
            print(f"✅ Enhanced preview completed with {len(result['column_names'])} columns")
            return result
            
        except Exception as e:
            print(f"❌ Preview exception: {str(e)}")
            import traceback
            print(f"📚 Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def detect_data_range(self, file_path: str, encoding: str = "utf-8"):
        """
        Auto-detect data range in CSV
        
        Args:
            file_path: Path to the CSV file
            encoding: File encoding
            
        Returns:
            dict: Data range detection result
        """
        print(f"🔍 Detect range request for file: {file_path}")
        
        try:
            result = self.robust_parser.detect_data_range(file_path, encoding)
            if not result['success']:
                return {
                    'success': False,
                    'error': result['error']
                }
            return result
        except Exception as e:
            print(f"❌ Detect range exception: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
