"""
CSV processing service for handling CSV parsing and preprocessing coordination

This service implements the domain logic for CSV processing operations using
dependency injection and clean architecture principles.
"""
import os
import configparser
from typing import Dict, List, Any, Optional, Tuple

from .interfaces import CSVParserPort, CSVPreprocessorPort, EncodingDetectorPort
from .exceptions import CSVProcessingError, CSVParsingError, BankDetectionError
from backend.data_cleaning.data_cleaner import DataCleaner
from backend.bank_detection import BankDetector
from backend.shared.config.unified_config_service import get_unified_config_service
from backend.models.csv_models import BankDetectionResult


class CSVProcessingService:
    """Service focused on CSV processing coordination using dependency injection"""
    
    def __init__(self, 
                 csv_parser: CSVParserPort,
                 csv_preprocessor: CSVPreprocessorPort,
                 encoding_detector: EncodingDetectorPort):
        """
        Initialize service with injected dependencies
        
        Args:
            csv_parser: CSV parsing implementation
            csv_preprocessor: CSV preprocessing implementation  
            encoding_detector: Encoding detection implementation
        """
        self.csv_parser = csv_parser
        self.csv_preprocessor = csv_preprocessor
        self.encoding_detector = encoding_detector
        
        # Domain services - these stay as direct dependencies
        self.data_cleaner = DataCleaner()
        self.config_service = get_unified_config_service()
        self.bank_detector = BankDetector(self.config_service)
        
        print(f"ℹ [CSVProcessingService] Initialized with injected components")
    
    def process_single_file(self, file_info: Dict[str, Any], parse_config: Any, 
                           enable_cleaning: bool = True) -> Dict[str, Any]:
        """
        Process a single CSV file with preprocessing and bank detection
        
        Args:
            file_info: File information dictionary
            parse_config: Parsing configuration
            enable_cleaning: Whether to enable data cleaning
            
        Returns:
            dict: Processing result
        """
        print(f"ℹ [CSVProcessingService] Processing file: {file_info['file_id']}")
        
        file_path = file_info["temp_path"]
        filename = file_info["original_name"]
        
        try:
            # Step 1: Determine effective encoding
            effective_encoding = self._determine_effective_encoding(file_path, filename, parse_config)
            
            # Update config with effective encoding
            current_config = self._update_config_with_encoding(parse_config, effective_encoding)
            
            # Step 2: Quick bank detection for preprocessing decisions
            quick_bank_detection = self._quick_bank_detection(filename)
            
            # Step 3: Apply preprocessing if needed
            preprocessing_result = self._apply_preprocessing(file_path, current_config, quick_bank_detection)
            
            # Step 4: Bank detection and header finding
            bank_detection, header_info = self._detect_bank_and_headers(
                preprocessing_result['file_path'], filename, current_config,
                effective_encoding, preprocessing_result['info']['applied']
            )
            
            # Step 5: Parse with enhanced parser
            parse_result = self._parse_with_bank_info(
                preprocessing_result['file_path'], current_config, header_info
            )
            
            if not parse_result['success']:
                raise Exception(f"Failed to parse {filename}: {parse_result.get('error', 'Unknown error')}")
            
            # Step 6: Finalize bank detection on parsed data
            final_bank_info = self._finalize_bank_detection(
                filename, parse_result, bank_detection, preprocessing_result['info']
            )
            
            # Step 7: Apply data cleaning if enabled
            final_result = self._apply_cleaning_if_enabled(
                parse_result, final_bank_info, enable_cleaning
            )
            
            # Convert to proper response format
            bank_info_pydantic = BankDetectionResult(
                bank_name=final_bank_info.get('bank_name', final_bank_info.get('detected_bank', 'unknown')),
                confidence=final_bank_info.get('confidence', 0.0),
                reasons=final_bank_info.get('reasons', [])
            )
            
            return {
                "file_id": file_info["file_id"],
                "filename": filename,
                "success": final_result['success'],
                "bank_info": bank_info_pydantic.dict(),
                "parse_result": {
                    "success": final_result['success'],
                    "headers": final_result['headers'],
                    "data": final_result['data'],
                    "row_count": len(final_result['data'])
                },
                "config": current_config,
            }
            
        except Exception as e:
            print(f"[ERROR] File processing exception for {filename}: {str(e)}")
            import traceback
            print(f"   Full traceback: {traceback.format_exc()}")
            return {
                "file_id": file_info["file_id"],
                "filename": filename,
                "success": False,
                "error": str(e),
                "bank_info": {"bank_name": "unknown", "confidence": 0.0, "reasons": []},
                "parse_result": {"success": False, "headers": [], "data": [], "row_count": 0},
                "config": parse_config,
            }
    
    def _determine_effective_encoding(self, file_path: str, filename: str, config: Any) -> str:
        """Determine the effective encoding for the file"""
        encoding_from_config = config.encoding if hasattr(config, 'encoding') else config.get('encoding')
        effective_encoding = encoding_from_config
        
        # If config encoding is None or generic 'utf-8', try to detect
        if not effective_encoding or (effective_encoding.lower() == 'utf-8' and filename.startswith("11600006-")):
            print(f"      Config encoding is '{effective_encoding}'. Detecting encoding for '{filename}'")
            detection_result = self.encoding_detector.detect_encoding(file_path)
            effective_encoding = detection_result['encoding']
            print(f"      Detected encoding for '{filename}': {effective_encoding} (confidence: {detection_result['confidence']:.2f})")
        
        return effective_encoding
    
    def _update_config_with_encoding(self, config: Any, effective_encoding: str) -> Any:
        """Update config with effective encoding"""
        if hasattr(config, 'encoding'):
            # It's a Pydantic model - create a new instance with updated encoding
            from backend.api.models import ParseConfig
            current_config = ParseConfig(
                start_row=config.start_row,
                end_row=config.end_row,
                start_col=config.start_col,
                end_col=config.end_col,
                encoding=effective_encoding,
                enable_cleaning=config.enable_cleaning
            )
        else:
            # It's a dictionary - use dictionary merging
            current_config = {**config, 'encoding': effective_encoding}
        
        return current_config
    
    def _quick_bank_detection(self, filename: str) -> Dict[str, Any]:
        """Quick filename-based bank detection for preprocessing decisions"""
        bank_result = self.bank_detector.detect_bank(filename, "", [])
        
        if bank_result.bank_name != 'unknown' and bank_result.confidence >= 0.1:
            try:
                # Check if this bank uses header_row (absolute positioning)
                config_file_path = os.path.join(self.config_service.config_dir, f"{bank_result.bank_name}.conf")
                if os.path.exists(config_file_path):
                    raw_config = configparser.ConfigParser()
                    raw_config.read(config_file_path)
                    header_row = raw_config.getint('csv_config', 'header_row', fallback=None)
                    uses_absolute_positioning = header_row is not None
                else:
                    uses_absolute_positioning = False
                
                return {
                    'bank_name': bank_result.bank_name,
                    'confidence': bank_result.confidence,
                    'uses_absolute_positioning': uses_absolute_positioning
                }
            except Exception:
                pass
        
        return {
            'bank_name': 'unknown',
            'confidence': 0.0,
            'uses_absolute_positioning': False
        }
    
    def _apply_preprocessing(self, file_path: str, config: Any, quick_detection: Dict[str, Any]) -> Dict[str, Any]:
        """Apply generic CSV preprocessing"""
        print(f"      Generic CSV preprocessing (bank-agnostic)")
        
        # Check if we should skip empty row removal for absolute positioning banks
        skip_empty_row_removal = False
        if quick_detection and quick_detection.get('uses_absolute_positioning', False):
            skip_empty_row_removal = True
            print(f"      Using bank-aware preprocessing for {quick_detection['bank_name']} (preserving empty rows)")
        else:
            print(f"      Using bank-agnostic CSV preprocessing")
        
        # Apply generic CSV preprocessing
        encoding = config.encoding if hasattr(config, 'encoding') else config.get('encoding')
        preprocessing_result = self.csv_preprocessor.preprocess_csv(
            file_path, 
            'generic',
            encoding,
            skip_empty_row_removal=skip_empty_row_removal
        )
        
        # Use preprocessed file if successful, otherwise use original
        actual_file_path = file_path
        preprocessing_info = {'applied': False}
        
        if preprocessing_result['success'] and preprocessing_result['issues_fixed']:
            actual_file_path = preprocessing_result['processed_file_path']
            preprocessing_info = {
                'applied': True,
                'issues_fixed': preprocessing_result['issues_fixed'],
                'original_rows': preprocessing_result['original_rows'],
                'processed_rows': preprocessing_result['processed_rows']
            }
            print(f"      [SUCCESS] Generic preprocessing applied: {len(preprocessing_result['issues_fixed'])} issues fixed")
            print(f"         [DATA] Rows: {preprocessing_result['original_rows']} → {preprocessing_result['processed_rows']}")
        else:
            print(f"      Generic preprocessing skipped (no issues found)")
        
        return {
            'file_path': actual_file_path,
            'info': preprocessing_info
        }
    
    def _detect_bank_and_headers(self, file_path: str, filename: str, current_file_config: Any, 
                                file_encoding: str, preprocessing_applied: bool) -> Tuple[Any, Dict[str, Any]]:
        """Detect bank and validate header using robust header validation"""
        from backend.infrastructure.csv_parsing.header_validator import find_and_validate_header, HeaderValidationError
        
        print(f"      Detecting bank and headers for {filename} with encoding {file_encoding}")
        
        # Read initial content for bank detection
        content_for_detection = ""
        sample_headers_for_detection = []
        try:
            with open(file_path, 'r', encoding=file_encoding, newline='') as f:
                raw_lines_for_detection = [next(f, '') for _ in range(20)]
            content_for_detection = "".join(raw_lines_for_detection)
            for line in raw_lines_for_detection:
                if line.strip():
                    sample_headers_for_detection = [h.strip() for h in line.split(',')]
                    break
        except Exception as e:
            print(f"         [WARNING] Could not read initial lines from {file_path} for bank detection: {e}")
        
        bank_detection_result = self.bank_detector.detect_bank(filename, content_for_detection, sample_headers_for_detection)
        
        if bank_detection_result.bank_name != 'unknown' and bank_detection_result.confidence > 0.1:
            detected_bank_name = bank_detection_result.bank_name
            print(f"      Tentatively detected bank: {detected_bank_name} (confidence: {bank_detection_result.confidence:.2f})")
            
            try:
                # Get config from the unified service
                bank_config = self.config_service.get_bank_config(detected_bank_name)
                if not bank_config:
                    raise ValueError(f"Could not retrieve config for bank '{detected_bank_name}'")
                
                detection_conf = bank_config.detection_info
                
                # Read header_row directly from config file
                config_file_path = os.path.join(self.config_service.config_dir, f"{detected_bank_name}.conf")
                raw_config = configparser.ConfigParser()
                raw_config.read(config_file_path)
                
                configured_row_1_indexed = raw_config.getint('csv_config', 'header_row', fallback=None)
                if configured_row_1_indexed is None:
                    raise ValueError(f"Configuration for '{detected_bank_name}' is missing 'header_row'")
                
                header_row_0_indexed = configured_row_1_indexed - 1
                
                # Validate header
                find_and_validate_header(
                    file_path=file_path,
                    encoding=file_encoding,
                    configured_header_row=header_row_0_indexed,
                    expected_headers=detection_conf.required_headers
                )
                
                effective_header_row = header_row_0_indexed
                effective_data_start_row = effective_header_row + 1
                print(f"      Header validated for {detected_bank_name}. header_row={effective_header_row}, data_start_row={effective_data_start_row}")
                
                return bank_detection_result, {
                    'header_row': effective_header_row,
                    'data_start_row': effective_data_start_row
                }
                
            except (ValueError, HeaderValidationError) as e:
                print(f"      [ERROR] Header detection/validation failed for {detected_bank_name}: {e}")
                return bank_detection_result, {
                    'header_row': None,
                    'data_start_row': None,
                    'error': str(e)
                }
        else:
            print(f"      No specific bank detected with sufficient confidence, using fallback")
            return bank_detection_result, {
                'header_row': 0,
                'data_start_row': 1
            }
    
    def _parse_with_bank_info(self, file_path: str, config: Any, header_info: Dict[str, Any]) -> Dict[str, Any]:
        """Parse file with enhanced parser using bank-detected info"""
        print(f"      Parsing with UnifiedCSVParser")
        
        header_row_for_unified = header_info['header_row']
        data_start_row_for_unified = header_info['data_start_row']
        max_rows_for_unified = None
        
        end_row = config.end_row if hasattr(config, 'end_row') else config.get('end_row')
        if end_row is not None and header_row_for_unified is not None and end_row >= header_row_for_unified:
            max_rows_for_unified = end_row - header_row_for_unified
        
        encoding = config.encoding if hasattr(config, 'encoding') else config.get('encoding')
        
        print(f"         UnifiedParser params: encoding='{encoding}', header_row={header_row_for_unified}, start_row={data_start_row_for_unified}, max_rows={max_rows_for_unified}")
        
        # Parse with injected CSV parser
        parse_result = self.csv_parser.parse_csv(
            file_path,
            encoding=encoding,
            header_row=header_row_for_unified,
            start_row=data_start_row_for_unified,
            max_rows=max_rows_for_unified
        )
        
        print(f"         UnifiedParser result success: {parse_result.get('success')}")
        
        if parse_result.get('success'):
            parsed_headers = parse_result.get('headers', [])
            print(f"         Headers parsed: {parsed_headers}")
        else:
            print(f"         UnifiedParser failed. Error: {parse_result.get('error')}")
        
        return parse_result
    
    def _finalize_bank_detection(self, filename: str, parse_result: Dict[str, Any], 
                                bank_detection: Any, preprocessing_info: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize bank detection on parsed data"""
        print(f"      Final bank detection on parsed data for {filename}")
        
        detection_result = self.bank_detector.detect_bank_from_data(
            filename, 
            parse_result['data']
        )
        print(f"      Final bank detected: {detection_result.bank_name} (confidence={detection_result.confidence:.2f})")
        print(f"      Detection reasons: {detection_result.reasons}")
        
        # Store comprehensive bank detection info
        return {
            'bank_name': detection_result.bank_name,
            'detected_bank': detection_result.bank_name,
            'confidence': detection_result.confidence,
            'reasons': detection_result.reasons,
            'original_headers': parse_result.get('headers', []),
            'preprocessing_applied': preprocessing_info['applied'],
            'preprocessing_info': preprocessing_info
        }
    
    def _apply_cleaning_if_enabled(self, parse_result: Dict[str, Any], bank_info: Dict[str, Any], 
                                  enable_cleaning: bool) -> Dict[str, Any]:
        """Apply data cleaning if enabled"""
        final_result = parse_result
        
        if enable_cleaning:
            print(f"      Applying data cleaning...")
            
            # Create bank-specific cleaning config
            bank_cleaning_config = None
            if bank_info['detected_bank'] != 'unknown':
                bank_column_mapping = self.config_service.get_column_mapping(bank_info['detected_bank'])
                detection_patterns = self.config_service.get_detection_patterns()
                expected_headers = []
                if bank_info['detected_bank'] in detection_patterns:
                    expected_headers = detection_patterns[bank_info['detected_bank']].required_headers
                
                bank_cleaning_config = {
                    'column_mapping': bank_column_mapping,
                    'bank_name': bank_info['detected_bank'],
                    'expected_headers': expected_headers
                }
                print(f"         Using bank-specific cleaning config for {bank_info['detected_bank']}")
            
            cleaning_result = self.data_cleaner.clean_parsed_data(parse_result, bank_cleaning_config)
            
            if cleaning_result['success']:
                final_result = {
                    'success': True,
                    'headers': [col for col in cleaning_result['data'][0].keys()] if cleaning_result['data'] else [],
                    'data': cleaning_result['data'],
                    'row_count': cleaning_result['row_count'],
                    'cleaning_applied': True,
                    'cleaning_summary': cleaning_result['cleaning_summary'],
                    'updated_column_mapping': cleaning_result.get('updated_column_mapping', {}),
                    'original_headers': parse_result.get('headers', []),
                    'bank_info': bank_info
                }
                print(f"         [SUCCESS] Data cleaning successful: {cleaning_result['row_count']} clean rows")
            else:
                print(f"         [WARNING] Data cleaning failed, using uncleaned data")
                final_result['cleaning_applied'] = False
                final_result['bank_info'] = bank_info
        else:
            final_result['cleaning_applied'] = False
            final_result['bank_info'] = bank_info
        
        return final_result