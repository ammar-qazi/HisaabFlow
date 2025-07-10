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
from .exceptions import CSVParsingError

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
            print(f"   Detected dialect: delimiter='{dialect_result['delimiter']}', quoting={dialect_result['quoting']}")
            
            # Step 3: Parse with strategies
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
            
            # Step 3: Parse with strategies
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
            
            return {
                'success': True,
                'data': processing_result['data'],
                'headers': processing_result['headers'],
                'row_count': processing_result['row_count'],
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
    
    def detect_structure(self, file_path: str, encoding: Optional[str] = None) -> Dict:
        """
        Detect CSV structure without full parsing
        
        Args:
            file_path: Path to CSV file
            encoding: Optional encoding override
            
        Returns:
            dict: Structure detection result
        """
        print(f" Structure detection: {file_path}")
        
        try:
            # Detect encoding if needed
            if encoding is None:
                encoding_result = self.encoding_detector.detect_encoding(file_path)
                encoding = encoding_result['encoding']
            
            # Detect dialect
            dialect_result = self.dialect_detector.detect_dialect(file_path, encoding)
            
            # Parse small sample for structure analysis
            parsing_result = self.parsing_strategies.parse_with_fallbacks(
                file_path, encoding, dialect_result, max_rows=10
            )
            
            if not parsing_result['success']:
                return {
                    'success': False,
                    'error': parsing_result['error']
                }
            
            # Analyze structure
            structure_result = self.structure_analyzer.analyze_structure(parsing_result['raw_rows'])
            
            return {
                'success': True,
                'structure_analysis': structure_result,
                'encoding': encoding,
                'dialect': dialect_result
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
            # Get structure analysis
            structure_result = self.detect_structure(file_path, encoding)
            
            if not structure_result['success']:
                return structure_result
            
            # Extract validation info
            structure_analysis = structure_result['structure_analysis']
            validation = structure_analysis.get('validation', {})
            
            # Additional validation checks
            issues = validation.get('issues', [])
            warnings = validation.get('warnings', [])
            
            # Check confidence levels
            if structure_analysis.get('confidence', 0) < 0.5:
                warnings.append("Low confidence in structure detection")
            
            return {
                'success': True,
                'valid': validation.get('valid', False),
                'issues': issues,
                'warnings': warnings,
                'structure_confidence': structure_analysis.get('confidence', 0),
                'detailed_analysis': structure_analysis
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
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
            structure_result = self.detect_structure(file_path, encoding)
            
            if not structure_result['success']:
                return {
                    'success': False,
                    'error': structure_result['error']
                }
            
            structure_analysis = structure_result['structure_analysis']
            suggested_header_row = structure_analysis.get('suggested_header_row', 0)
            
            # Parse small sample to get total row estimate
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
                'confidence': structure_analysis.get('confidence', 0.0)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
