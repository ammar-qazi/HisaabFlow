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
        Preview CSV file with global structure analysis and single-pass bank detection
        
        Args:
            file_path: Path to the CSV file
            filename: Original filename for bank detection
            encoding: File encoding override
            header_row: Manual header row override (0-based)
            
        Returns:
            dict: Preview result with bank detection info and global support
        """
        print(f"ℹ [REFACTORED] Preview request for file: {filename}")
        
        try:
            # Step 1: Single comprehensive structure analysis
            print("ℹ [REFACTORED] Performing global structure analysis...")
            structure_result = self.unified_parser.analyze_structure(file_path, encoding)
            
            if not structure_result['success']:
                return structure_result
            
            # Step 2: Handle headerless files
            if not structure_result.get('has_headers', True):
                print(f"ℹ [REFACTORED] Headerless CSV detected: {structure_result['total_columns']} columns")
                
                # Parse some sample data for preview
                sample_parse = self.unified_parser.preview_csv(
                    file_path,
                    encoding=structure_result['encoding'],
                    header_row=None,  # No headers
                    max_rows=20
                )
                
                return {
                    'success': True,
                    'headerless_file': True,
                    'preview_data': sample_parse.get('preview_data', []),
                    'column_names': structure_result['suggested_columns'],
                    'total_rows': sample_parse.get('total_rows', 0),
                    'encoding_used': structure_result['encoding'],
                    'dialect_detected': structure_result['dialect'],
                    'language_hints': structure_result.get('language_hints', []),
                    'structure_confidence': structure_result['confidence'],
                    'bank_detection': {
                        'detected_bank': 'unknown',
                        'confidence': 0.0,
                        'reasons': ['Headerless file - bank detection not applicable']
                    },
                    'message': 'CSV file has no headers. Generated column names provided.'
                }
            
            # Step 3: Override header row if manually specified
            effective_header_row = header_row if header_row is not None else structure_result['suggested_header_row']
            
            print(f"ℹ [REFACTORED] Using header row: {effective_header_row}")
            
            # Step 4: Single bank detection with complete structure info
            print("ℹ [REFACTORED] Performing bank detection with complete structure...")
            bank_detector = BankDetector(self.config_service)
            bank_detection = bank_detector.detect_bank(
                filename=filename,
                csv_content=structure_result['content_sample'],
                headers=structure_result['raw_headers']
            )
            
            print(f"ℹ [REFACTORED] Detected bank: {bank_detection.bank_name} (confidence: {bank_detection.confidence:.2f})")
            
            # Step 5: Parse with known structure (no more guessing!)
            print("ℹ [REFACTORED] Parsing with definitive structure...")
            parse_result = self.unified_parser.preview_csv(
                file_path,
                encoding=structure_result['encoding'],
                header_row=effective_header_row,
                max_rows=20
            )
            
            if not parse_result.get('success'):
                return parse_result
            
            # Step 6: Combine results
            final_result = {
                **parse_result,
                'bank_detection': {
                    'detected_bank': bank_detection.bank_name,
                    'confidence': bank_detection.confidence,
                    'reasons': bank_detection.reasons
                },
                'structure_analysis': {
                    'method': structure_result.get('method', 'multilingual_analysis'),
                    'confidence': structure_result['confidence'],
                    'language_hints': structure_result.get('language_hints', []),
                    'has_headers': structure_result['has_headers']
                },
                'encoding_used': structure_result['encoding'],
                'dialect_detected': structure_result['dialect']
            }
            
            print(f"ℹ [SUCCESS] Single-pass preview completed: {len(parse_result.get('column_names', []))} columns")
            return final_result

        except Exception as e:
            print(f"[ERROR] Preview exception: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
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
