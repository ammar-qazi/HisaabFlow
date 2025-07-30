"""
Preview service for CSV files with bank-aware header detection
"""
from typing import Optional
from backend.infrastructure.csv_parsing import UnifiedCSVParser
from backend.core.bank_detection import BankDetector
from backend.infrastructure.config.unified_config_service import get_unified_config_service


class PreviewService:
    """Service for handling CSV file previews with bank detection"""
    
    def __init__(self, config_service):
        self.unified_parser = UnifiedCSVParser()
        self.config_service = config_service
    
    def preview_csv_file(self, file_path: str, filename: str, encoding: Optional[str] = None, header_row: Optional[int] = None):
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
        print(f"‍ Preview request for file: {filename}")
        try:
            # If no manual header_row override, try to get it from bank config
            effective_header_row = header_row
            if header_row is None:
                # Quick bank detection to get configured header_row
                from backend.core.bank_detection import BankDetector
                bank_detector = BankDetector(self.config_service)
                bank_result = bank_detector.detect_bank(filename, "", [])
                
                if bank_result.bank_name != 'unknown' and bank_result.confidence >= 0.5:
                    bank_config = self.config_service.get_bank_config(bank_result.bank_name)
                    if bank_config and bank_config.csv_config:
                        # Convert 1-based config to 0-based for parser
                        effective_header_row = bank_config.csv_config.header_row - 1 if bank_config.csv_config.header_row else None
                        print(f"      Using bank-specific header_row: {effective_header_row} (from {bank_result.bank_name} config)")
            
            # Single call to the robust parser
            print("ℹ [PreviewService] Calling UnifiedCSVParser to get a comprehensive preview.")
            result = self.unified_parser.preview_csv(file_path, encoding=None, header_row=effective_header_row)

            if not result.get('success'):
                return result  # Return the error dictionary directly

            # Now, use the successful result for bank detection
            effective_encoding = result['encoding_used']
            headers_for_detection = result.get('column_names', [])
            preview_data = result['preview_data']
            
            # Extract content for bank detection
            content_lines = []
            
            # Add the actual header line to content_for_detection
            if headers_for_detection:
                content_lines.append(' '.join(headers_for_detection))

            for row in preview_data[:10]:  # Use first 10 rows for detection
                row_text = ' '.join([str(cell) for cell in row.values() if cell])
                content_lines.append(row_text)

            content_for_detection = '\n'.join(content_lines)
            
            # Detect bank using filename, content, and the headers extracted by the parser
            bank_detector = BankDetector(self.config_service)
            bank_detection = bank_detector.detect_bank(filename, content_for_detection, headers_for_detection)
            print(f" Detected bank: {bank_detection.bank_name} (confidence: {bank_detection.confidence:.2f})")

            # Add bank detection info to the final result
            result['bank_detection'] = {
                'detected_bank': bank_detection.bank_name,
                'confidence': bank_detection.confidence,
                'reasons': bank_detection.reasons
            }

            print(f"[SUCCESS] Enhanced preview completed with {len(result['column_names'])} columns")
            return result

        except Exception as e:
            print(f"[ERROR]  Preview exception: {str(e)}")
            import traceback
            print(f" Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def detect_data_range(self, file_path: str, encoding: Optional[str] = None):
        """
        Auto-detect data range in CSV
        
        Args:
            file_path: Path to the CSV file
            encoding: File encoding
            
        Returns:
            dict: Data range detection result
        """
        print(f" Detect range request for file: {file_path}")
        
        try:
            # If encoding is None, UnifiedCSVParser will auto-detect.
            # If an encoding is provided, it will be used.
            print(f"ℹ [PreviewService] Calling unified_parser.detect_data_range. Encoding: {'auto-detect' if encoding is None else encoding}")
            result = self.unified_parser.detect_data_range(file_path, encoding=encoding)
            
            # unified_parser.detect_data_range itself calls detect_structure, which handles encoding detection if 'encoding' is None.
            if not result['success']:
                return {
                    'success': False,
                    'error': result['error']
                }
            return result
        except Exception as e:
            print(f"[ERROR]  Detect range exception: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def parse_range(self, file_path: str, request: dict):
        """
        Parse CSV with specified range and optional data cleaning
        
        Args:
            file_path: Path to the CSV file
            request: Dictionary containing parsing parameters
            
        Returns:
            dict: Parse result with optional data cleaning
        """
        print(f" Parse range request for file: {file_path}")
        
        try:
            # Extract parameters from request
            start_row = request.get('start_row', 0)
            end_row = request.get('end_row')
            encoding = request.get('encoding', 'utf-8')
            enable_cleaning = request.get('enable_cleaning', True)
            
            print(f"ℹ [PreviewService] Parse range: start_row={start_row}, end_row={end_row}, encoding={encoding}, cleaning={enable_cleaning}")
            
            # Calculate max_rows if end_row is specified
            max_rows = None
            if end_row is not None:
                if end_row >= start_row:
                    max_rows = end_row - start_row + 1
                else:
                    print(f"[WARNING] end_row ({end_row}) is less than start_row ({start_row})")
            
            # Use the unified parser for parsing
            parse_result = self.unified_parser.parse_csv(
                file_path,
                encoding=encoding,
                header_row=start_row,
                max_rows=max_rows
            )
            
            if not parse_result['success']:
                return {
                    'success': False,
                    'error': parse_result['error']
                }
            
            # Add parser info
            parse_result['parser_used'] = 'unified'
            
            # Apply data cleaning if enabled
            if enable_cleaning:
                print(f"ℹ [PreviewService] Applying data cleaning...")
                
                # For now, return the parsed result without cleaning
                # The cleaning logic would need to be integrated here if needed
                parse_result['cleaning_applied'] = False
                print(f"ℹ [PreviewService] Data cleaning not implemented in parse_range yet")
            else:
                parse_result['cleaning_applied'] = False
            
            print(f"[SUCCESS] Parse range completed: {parse_result.get('row_count', 0)} rows")
            return parse_result
            
        except Exception as e:
            print(f"[ERROR] Parse range exception: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
