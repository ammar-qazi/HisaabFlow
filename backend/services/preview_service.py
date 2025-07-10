"""
Preview service for CSV files with bank-aware header detection
"""
from typing import Optional
from backend.infrastructure.csv_parsing import UnifiedCSVParser
from backend.core.bank_detection import BankDetector
from backend.infrastructure.config.unified_config_service import get_unified_config_service


class PreviewService:
    """Service for handling CSV file previews with bank detection"""
    
    def __init__(self):
        self.unified_parser = UnifiedCSVParser()
        self.config_service = get_unified_config_service()
        self.bank_detector = BankDetector(self.config_service)
    
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
            # Step 1: Detect bank first for header detection
            print(f" Step 1: Detecting bank for header detection...")
            
            # If encoding is not provided by the user, it will be None,
            # allowing UnifiedCSVParser to auto-detect it.
            initial_encoding_to_use = encoding

            # Defensive check: If a default 'utf-8' is passed (likely from API layer)
            # and the filename is known to often have other encodings (e.g., Forint Bank),
            # force auto-detection by setting encoding to None.
            if initial_encoding_to_use == "utf-8" and filename.startswith("11600006-"):
                print(f"[WARNING] [PreviewService] Forcing encoding auto-detection for Forint Bank pattern file '{filename}' due to 'utf-8' input potentially masking true encoding.")
                initial_encoding_to_use = None
            
            # Read first few lines for bank detection
            print(f"ℹ [PreviewService] Calling unified_parser.preview_csv with header_row=0 for initial bank detection content. User-provided encoding: {initial_encoding_to_use}")
            preview_result = self.unified_parser.preview_csv(file_path, initial_encoding_to_use, header_row=0)
            if not preview_result['success']:
                return {
                    'success': False,
                    'error': preview_result['error']
                }
            
            # Use the encoding determined by the parser (either user-provided or auto-detected)
            effective_encoding = preview_result['encoding_used']
            print(f"ℹ [PreviewService] Effective encoding after initial preview: {effective_encoding}")
            
            # Extract content for bank detection
            preview_data = preview_result['preview_data']
            headers_for_detection = preview_result.get('column_names', []) # Actual headers from parser
            content_lines = []
            
            # Add the actual header line to content_for_detection
            if headers_for_detection:
                content_lines.append(' '.join(headers_for_detection))

            for row in preview_data[:10]:  # Use first 10 rows for detection
                row_text = ' '.join([str(cell) for cell in row.values() if cell])
                content_lines.append(row_text)

            content_for_detection = '\n'.join(content_lines)
            # Detect bank using filename, content, and the headers extracted by the parser at the initial header_row (0)
            bank_detection = self.bank_detector.detect_bank(filename, content_for_detection, headers_for_detection)
            print(f" Detected bank: {bank_detection.bank_name} (confidence: {bank_detection.confidence:.2f})")
            
            # Step 2: Use bank-specific header detection if available
            detected_header_row = header_row
            header_detection_info = None
            
            if bank_detection.bank_name != 'unknown' and bank_detection.confidence >= 0.5:
                print(f" Step 2: Using bank-specific header detection for {bank_detection.bank_name}")
                try:
                    from backend.infrastructure.csv_parsing.header_validator import find_and_validate_header, HeaderValidationError
                    
                    # Get bank config and read header_row from config file
                    bank_config = self.config_service.get_bank_config(bank_detection.bank_name)
                    if bank_config:
                        import os
                        import configparser
                        config_file_path = os.path.join(self.config_service.config_dir, f"{bank_detection.bank_name}.conf")
                        
                        if os.path.exists(config_file_path):
                            raw_config = configparser.ConfigParser()
                            raw_config.read(config_file_path)
                            
                            configured_row_1_indexed = raw_config.getint('csv_config', 'header_row', fallback=None)
                            if configured_row_1_indexed is not None:
                                header_row_0_indexed = configured_row_1_indexed - 1
                                
                                # Validate header using HeaderValidator
                                actual_headers = find_and_validate_header(
                                    file_path=file_path,
                                    encoding=effective_encoding,
                                    configured_header_row=header_row_0_indexed,
                                    expected_headers=bank_config.detection_info.required_headers
                                )
                                
                                detected_header_row = header_row_0_indexed
                                header_detection_info = {
                                    'success': True,
                                    'header_row': header_row_0_indexed,
                                    'data_start_row': header_row_0_indexed + 1,
                                    'detected_headers': actual_headers,
                                    'confidence': 100.0
                                }
                                print(f" Bank-specific header detection: row {detected_header_row}")
                            else:
                                print(f"[WARNING] No header_row configured for {bank_detection.bank_name}")
                        else:
                            print(f"[WARNING] Config file not found for {bank_detection.bank_name}")
                    else:
                        print(f"[WARNING] Bank config not found for {bank_detection.bank_name}")
                        
                except (HeaderValidationError, Exception) as e:
                    print(f"[WARNING] Header validation failed: {e}")
                    header_detection_info = {'success': False, 'error': str(e)}
            
            # Step 3: Generate enhanced preview with proper headers
            print(f" Step 3: Generating enhanced preview with header_row={detected_header_row}")
            
            # Use data start row from header detection if available
            start_row = None
            if header_detection_info and header_detection_info.get('success'):
                start_row = header_detection_info.get('data_start_row')
                if start_row is not None:
                    print(f"ℹ [PreviewService] Using start_row={start_row} for bank {bank_detection.bank_name}")
            
            # Use the detected header row for the final preview
            print(f"ℹ [PreviewService] Calling unified_parser.preview_csv for final preview. Effective header_row: {detected_header_row}. start_row: {start_row}. Effective encoding: {effective_encoding}. Detected bank: {bank_detection.bank_name}")
            result = self.unified_parser.preview_csv(file_path, effective_encoding, header_row=detected_header_row, start_row=start_row)
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
            
            if header_detection_info and header_detection_info.get('success'):
                result['header_detection'] = header_detection_info
                result['suggested_header_row'] = header_detection_info['header_row']
                result['suggested_data_start_row'] = header_detection_info['data_start_row']
            
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
            print(f"ℹ [PreviewService] Calling unified_parser.detect_data_range. User-provided encoding: {encoding}")
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
