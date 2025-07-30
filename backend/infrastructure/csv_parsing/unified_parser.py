"""
Unified CSV Parser - Main orchestrator class
Lightweight facade that coordinates all parsing components
"""
from typing import Dict, List, Optional, Any
from .encoding_detector import EncodingDetector
from .dialect_detector import DialectDetector
from .parsing_strategies import ParsingStrategies
from .data_processor import DataProcessor
from .structure_analyzer import StructureAnalyzer
from .exceptions import CSVParsingError, NoHeadersFoundError, HeaderlessCSVDetected

class UnifiedCSVParser:
    """Main API orchestrator for unified CSV parsing"""
    
    def __init__(self):
        self.encoding_detector = EncodingDetector()
        self.dialect_detector = DialectDetector()
        self.parsing_strategies = ParsingStrategies()
        self.data_processor = DataProcessor()
        self.structure_analyzer = StructureAnalyzer()
    
    def preview_csv(self, file_path: str, encoding: Optional[str] = None, bank_name: Optional[str] = None, 
                   config_manager: Optional[Any] = None, header_row: Optional[int] = None, max_rows: int = 20, 
                   start_row: Optional[int] = None) -> Dict:
        """
        Preview CSV file with automatic detection - maintains existing interface
        
        Args:
            file_path: Path to CSV file
            encoding: Optional encoding override
            bank_name: Optional bank name (not used directly, maintained for compatibility)
            config_manager: Optional config manager (not used directly, maintained for compatibility)
            header_row: Optional header row override
            max_rows: Maximum rows to preview
            start_row: Optional starting row index (skip rows before this)
            
        Returns:
            dict: Preview result compatible with existing PreviewService
        """
        print(f" UnifiedCSVParser preview: {file_path}")
        
        try:
            # Step 1: Detect encoding
            if encoding is None:
                encoding_result = self.encoding_detector.detect_encoding(file_path)
                encoding = encoding_result['encoding']
                print(f"    Detected encoding: {encoding}")
            else:
                print(f"    Using provided encoding: {encoding}")
            
            # Step 2: Detect dialect
            dialect_result = self.dialect_detector.detect_dialect(file_path, encoding)
            print(f"   Detected dialect: delimiter='{dialect_result['delimiter']}', quoting={dialect_result['quoting']}, lineterminator={repr(dialect_result.get('line_terminator', 'N/A'))}")
            
            # Step 3: Parse with strategies (including line terminator)
            parsing_result = self.parsing_strategies.parse_with_fallbacks(
                file_path, encoding, dialect_result, header_row, max_rows, start_row
            )
            
            if not parsing_result['success']:
                return {
                    'success': False,
                    'error': parsing_result['error']
                }
            
            print(f"   [SUCCESS] Parsing succeeded with {parsing_result['strategy_used']} strategy")
            
            # Step 4: Process data
            # If we used start_row filtering, the header is now at position 0
            effective_header_row = 0 if start_row is not None and header_row is not None and header_row < start_row else header_row
            processing_result = self.data_processor.process_raw_data(
                parsing_result['raw_rows'], effective_header_row
            )
            
            if not processing_result['success']:
                return {
                    'success': False,
                    'error': processing_result['error']
                }
            
            # Format response to match existing PreviewService expectations
            preview_data = processing_result['data']
            headers = processing_result['headers']
            
            return {
                'success': True,
                'preview_data': preview_data,
                'column_names': headers,
                'total_rows': processing_result['row_count'],
                'encoding_used': encoding,
                'parsing_info': {
                    'strategy_used': parsing_result['strategy_used'],
                    'dialect_detected': dialect_result,
                    'processing_info': processing_result['processing_info']
                }
            }
            
        except Exception as e:
            print(f"[ERROR]  Preview failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def parse_csv(self, file_path: str, encoding: Optional[str] = None, **parsing_options) -> Dict:
        """
        Full CSV parsing with automatic detection
        
        Args:
            file_path: Path to CSV file
            encoding: Optional encoding override
            **parsing_options: Additional parsing options (header_row, max_rows, etc.)
            
        Returns:
            dict: Complete parsing result
        """
        print(f"[DATA] UnifiedCSVParser full parse: {file_path}")
        
        try:
            # Extract options
            header_row = parsing_options.get('header_row')
            max_rows = parsing_options.get('max_rows')
            start_row = parsing_options.get('start_row')
            
            # Step 1: Detect encoding
            if encoding is None:
                encoding_result = self.encoding_detector.detect_encoding(file_path)
                encoding = encoding_result['encoding']
            else:
                encoding_result = {'encoding': encoding, 'confidence': 1.0}
            
            # Step 2: Detect dialect
            dialect_result = self.dialect_detector.detect_dialect(file_path, encoding)
            
            # Step 3: Parse with strategies (including line terminator)
            parsing_result = self.parsing_strategies.parse_with_fallbacks(
                file_path, encoding, dialect_result, header_row, max_rows, start_row
            )
            
            if not parsing_result['success']:
                raise CSVParsingError(parsing_result['error'], file_path)
            
            # Step 4: Process data
            # If we used start_row filtering, the header is now at position 0
            effective_header_row = 0 if start_row is not None and header_row is not None and header_row < start_row else header_row
            processing_result = self.data_processor.process_raw_data(
                parsing_result['raw_rows'], effective_header_row
            )
            
            if not processing_result['success']:
                raise CSVParsingError(processing_result['error'], file_path)
            
            print(f"  DEBUG: UnifiedCSVParser - Encoding result being returned: {encoding_result}")
            return {
                'success': True,
                'data': processing_result['data'],
                'headers': processing_result['headers'],
                'row_count': processing_result['row_count'],
                'raw_rows': parsing_result['raw_rows'],  # Include raw_rows for unknown bank analysis
                'metadata': {
                    'encoding_detection': encoding_result,
                    'dialect_detection': dialect_result,
                    'parsing_strategy': parsing_result['strategy_used'],
                    'processing_info': processing_result['processing_info']
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    
    def validate_csv(self, file_path: str, encoding: Optional[str] = None) -> Dict:
        """
        Validate CSV file structure and format
        
        Args:
            file_path: Path to CSV file
            encoding: Optional encoding override
            
        Returns:
            dict: Validation result
        """
        print(f"[SUCCESS] CSV validation: {file_path}")
        
        try:
            # Get structure analysis using new global method
            structure_result = self.analyze_structure(file_path, encoding)
            
            if not structure_result['success']:
                return structure_result
            
            # Simplified validation based on new structure analysis
            issues = []
            warnings = []
            
            # Check confidence levels
            confidence = structure_result.get('confidence', 0)
            if confidence < 0.5:
                warnings.append("Low confidence in structure detection")
            
            # Check if headers were found
            has_headers = structure_result.get('has_headers', True)
            if not has_headers:
                warnings.append("No headers detected in CSV file")
            
            return {
                'success': True,
                'valid': confidence > 0.3,  # Basic validity check
                'issues': issues,
                'warnings': warnings,
                'structure_confidence': confidence,
                'has_headers': has_headers,
                'method': structure_result.get('method', 'unknown')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_structure(self, file_path: str, encoding: Optional[str] = None) -> Dict:
        """
        Global-ready, bank-agnostic CSV structure analysis.
        
        This is the main method for decoupled structure analysis that:
        - Detects encoding automatically using chardet
        - Detects CSV dialect (delimiter, quotes, etc.)
        - Uses multilingual header detection
        - Handles headerless files gracefully
        - Provides content sample for bank detection
        
        Args:
            file_path: Path to CSV file
            encoding: Optional encoding override
            
        Returns:
            dict: {
                'success': True,
                'encoding': 'utf-8',
                'dialect': {'delimiter': ';', 'quotechar': '"'},
                'suggested_header_row': 2 or None,
                'suggested_data_start_row': 3,
                'raw_headers': ['Fecha', 'Descripción'] or [],
                'content_sample': "...",
                'confidence': 0.95,
                'has_headers': True,
                'language_hints': ['es'],
                'total_columns': 5
            }
        """
        print(f" Global structure analysis: {file_path}")
        
        try:
            # Step 1: Detect encoding (leveraging existing robust detection)
            if encoding is None:
                encoding_result = self.encoding_detector.detect_encoding(file_path)
                detected_encoding = encoding_result['encoding']
                print(f"    Detected encoding: {detected_encoding}")
            else:
                detected_encoding = encoding
                print(f"    Using provided encoding: {detected_encoding}")
            
            # Step 2: Detect dialect (supports international CSV formats)
            dialect_result = self.dialect_detector.detect_dialect(file_path, detected_encoding)
            print(f"   Detected dialect: delimiter='{dialect_result['delimiter']}'")
            
            # Step 3: Parse sample for structure analysis (50 rows to handle bank CSVs with metadata)
            parsing_result = self.parsing_strategies.parse_with_fallbacks(
                file_path, detected_encoding, dialect_result, max_rows=50
            )
            
            if not parsing_result['success']:
                return {
                    'success': False,
                    'error': f"Failed to parse CSV for structure analysis: {parsing_result['error']}"
                }
            
            sample_rows = parsing_result['raw_rows']
            print(f"   Parsed {len(sample_rows)} sample rows for analysis")
            
            # Step 4: Global header detection with multilingual support
            header_result = self.structure_analyzer.detect_header_row_global(sample_rows)
            
            # Step 5: Handle results based on header detection
            if not header_result['has_headers']:
                # Headerless file detected
                total_columns = len(sample_rows[0]) if sample_rows else 0
                suggested_columns = [f'Column_{i+1}' for i in range(total_columns)]
                
                print(f"   Headerless CSV detected: {total_columns} columns")
                
                # Create content sample from first few data rows
                content_sample = self._create_content_sample_from_rows(sample_rows[:10])
                
                return {
                    'success': True,
                    'encoding': detected_encoding,
                    'dialect': dialect_result,
                    'suggested_header_row': None,
                    'suggested_data_start_row': 0,
                    'raw_headers': [],
                    'suggested_columns': suggested_columns,
                    'content_sample': content_sample,
                    'confidence': header_result['confidence'],
                    'has_headers': False,
                    'language_hints': header_result.get('detected_languages', []),
                    'total_columns': total_columns,
                    'method': header_result['method']
                }
            else:
                # Headers found
                header_row_idx = header_result['suggested_row']
                data_start_row = header_row_idx + 1
                
                raw_headers = sample_rows[header_row_idx] if header_row_idx < len(sample_rows) else []
                print(f"   Headers found at row {header_row_idx}: {raw_headers}")
                
                # Create content sample including headers and some data
                content_sample = self._create_content_sample_with_headers(sample_rows, header_row_idx)
                
                return {
                    'success': True,
                    'encoding': detected_encoding,
                    'dialect': dialect_result,
                    'suggested_header_row': header_row_idx,
                    'suggested_data_start_row': data_start_row,
                    'raw_headers': raw_headers,
                    'content_sample': content_sample,
                    'confidence': header_result['confidence'],
                    'has_headers': True,
                    'language_hints': header_result.get('detected_languages', []),
                    'total_columns': len(raw_headers),
                    'method': header_result['method']
                }
                
        except Exception as e:
            print(f"[ERROR]  Structure analysis failed: {str(e)}")
            return {
                'success': False,
                'error': f"Structure analysis failed: {str(e)}"
            }
    
    def _create_content_sample_from_rows(self, rows: List[List[str]]) -> str:
        """Create content sample from raw CSV rows for bank detection"""
        content_lines = []
        for row in rows[:10]:  # First 10 rows
            if row:  # Skip empty rows
                row_text = ' '.join([str(cell) for cell in row if cell])
                content_lines.append(row_text)
        return '\n'.join(content_lines)
    
    def _create_content_sample_with_headers(self, rows: List[List[str]], header_row_idx: int) -> str:
        """Create content sample including headers and data for bank detection"""
        content_lines = []
        
        # Include first 15 rows for content signature matching (covers bank info sections)
        # This ensures we capture content signatures like "NayaPay ID", "Customer Name" etc.
        for i in range(min(15, len(rows))):
            row = rows[i]
            if row:  # Skip empty rows
                row_text = ' '.join([str(cell) for cell in row if cell])
                if row_text.strip():  # Only add non-empty content
                    content_lines.append(row_text)
        
        # Also add header row if it's beyond row 15
        if header_row_idx >= 15 and header_row_idx < len(rows):
            header_row = rows[header_row_idx]
            header_text = ' '.join([str(cell) for cell in header_row if cell])
            if header_text.strip():
                content_lines.append(header_text)
        
        # Add some data rows after headers
        data_start = header_row_idx + 1
        for i in range(data_start, min(data_start + 5, len(rows))):
            row = rows[i]
            if row:  # Skip empty rows
                row_text = ' '.join([str(cell) for cell in row if cell])
                if row_text.strip():
                    content_lines.append(row_text)
        
        return '\n'.join(content_lines)

    def detect_data_range(self, file_path: str, encoding: Optional[str] = None) -> Dict:
        """
        Auto-detect where the actual data starts (compatibility method)
        
        Args:
            file_path: Path to CSV file
            encoding: Optional encoding override
            
        Returns:
            dict: Data range detection result
        """
        print(f" Data range detection: {file_path}")
        
        try:
            # Use structure detection to find header row
            structure_result = self.analyze_structure(file_path, encoding)
            
            if not structure_result['success']:
                return {
                    'success': False,
                    'error': structure_result['error']
                }
            
            suggested_header_row = structure_result.get('suggested_header_row', 0)
            
            # Parse small sample to get total row estimate (including line terminator)
            parsing_result = self.parsing_strategies.parse_with_fallbacks(
                file_path, 
                structure_result['encoding'], 
                structure_result['dialect'], 
                max_rows=50
            )
            
            if parsing_result['success']:
                total_rows = len(parsing_result['raw_rows'])
            else:
                total_rows = None
            
            return {
                'success': True,
                'suggested_header_row': suggested_header_row,
                'total_rows': total_rows,
                'confidence': structure_result.get('confidence', 0.0)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
