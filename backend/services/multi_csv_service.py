"""
Multi-CSV parsing service for handling multiple file operations
"""
import os # Add this import
from typing import Any, Dict, List # Add these imports
from backend.models.csv_models import CSVRow, BankDetectionResult
from decimal import Decimal
from backend.csv_parser import UnifiedCSVParser
from backend.data_cleaner import DataCleaner
from backend.bank_detection import BankDetector
from backend.shared.config.unified_config_service import get_unified_config_service
from backend.csv_parser import EncodingDetector
from backend.csv_preprocessing.csv_preprocessor import CSVPreprocessor

class MultiCSVService:
    """Service for handling multi-CSV parsing operations"""
    
    def __init__(self):
        self.unified_parser = UnifiedCSVParser() # New parser instance
        self.data_cleaner = DataCleaner()
        self.config_service = get_unified_config_service()
        self.bank_detector = BankDetector(self.config_service)
        self.csv_preprocessor = CSVPreprocessor()
        self.encoding_detector = EncodingDetector() # Initialize EncodingDetector
        
        # Configuration service is already initialized as self.config_service
    
    def parse_multiple_files(self, file_infos: list, parse_configs: list, 
                           enable_cleaning: bool = True, use_pydantic: bool = False):
        """
        Parse multiple CSV files with preprocessing and bank detection
        
        Args:
            file_infos: List of file info dictionaries
            parse_configs: List of parsing configurations
            enable_cleaning: Whether to enable data cleaning
            use_pydantic: Whether to convert parsed data to CSVRow Pydantic models
            
        Returns:
            dict: Multi-CSV parsing result
        """
        # Get user_name from config instead of parameter
        user_name = self.config_service.get_user_name()
        print(f"ℹ [MIGRATION][MultiCSVService] parse_multiple_files called for {len(file_infos)} files.")
        print(f"  User name from config: {user_name}")
        print(f"  Data cleaning enabled: {enable_cleaning}")
        
        try:
            results = []
            
            # Process each file
            for i, (file_info, config) in enumerate(zip(file_infos, parse_configs)):
                print(f" Processing file {i+1}/{len(file_infos)}: {file_info['file_id']}")
                
                file_path = file_info["temp_path"]
                filename = file_info["original_name"]
                
                # Step 1: Determine effective encoding
                encoding_from_config = config.encoding
                effective_encoding = encoding_from_config
                
                # If config encoding is None or a generic 'utf-8' (which might be a default), try to detect.
                # For Forint bank files, we know 'utf-8' is often wrong.
                if not effective_encoding or (effective_encoding.lower() == 'utf-8' and filename.startswith("11600006-")):
                    print(f"ℹ [MultiCSVService] Config encoding is '{effective_encoding}'. Detecting encoding for '{filename}'.")
                    detection_result = self.encoding_detector.detect_encoding(file_path)
                    effective_encoding = detection_result['encoding']
                    print(f" [MultiCSVService] Detected encoding for '{filename}': {effective_encoding} (confidence: {detection_result['confidence']:.2f})")
                
                # Update config with the effective encoding to be used by subsequent steps
                # Create a new ParseConfig with updated encoding
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
                
                # Step 2: Quick bank detection for preprocessing decisions
                quick_bank_detection = self._quick_bank_detection(filename)
                
                # Step 3: Generic CSV preprocessing (conditional)
                preprocessing_result = self._apply_preprocessing(file_path, current_config, quick_bank_detection)
                
                # Step 4: Bank detection and header finding
                bank_detection, header_info = self._detect_bank_and_headers(
                    preprocessing_result['file_path'], filename, current_config,
                    effective_encoding, # Pass effective_encoding
                    preprocessing_result['info']['applied'] # Pass preprocessing status
                )
                
                # Step 5: Parse with enhanced parser
                parse_result = self._parse_with_bank_info(
                    preprocessing_result['file_path'], current_config, header_info # Pass current_config
                )


                if not parse_result['success']:
                    raise Exception(f"Failed to parse {filename}: {parse_result.get('error', 'Unknown error')}")
                
                # Step 6: Final bank detection on parsed data
                final_bank_info = self._finalize_bank_detection( # Renamed from Step 4 to Step 5
                    filename, parse_result, bank_detection, preprocessing_result['info']
                )
                
                # Step 5: Apply data cleaning if enabled
                final_result = self._apply_cleaning_if_enabled( # Renamed from Step 5 to Step 6
                    parse_result, final_bank_info, enable_cleaning
                )
                
                # --- Pydantic Model Conversion (after cleaning) ---
                # Convert final_bank_info dict to Pydantic BankDetectionResult model
                bank_info_pydantic = BankDetectionResult(
                    bank_name=final_bank_info.get('bank_name', final_bank_info.get('detected_bank', 'unknown')),
                    confidence=final_bank_info.get('confidence', 0.0),
                    reasons=final_bank_info.get('reasons', [])
                )

                final_data_for_response = final_result['data'] # This is List[Dict[str, Any]]
                data_type_for_response = 'dict'

                if use_pydantic and bank_info_pydantic.bank_name != 'unknown':
                    column_mapping = self.config_service.get_column_mapping(bank_info_pydantic.bank_name)
                    if column_mapping:
                        try:
                            pydantic_data = self._map_to_pydantic_rows(final_data_for_response, column_mapping)
                            final_data_for_response = pydantic_data
                            data_type_for_response = 'pydantic'
                            print(f"   Mapped {len(pydantic_data)} rows to CSVRow models for {filename}.")
                        except Exception as e:
                            print(f"  [WARNING] Pydantic mapping failed for {filename}: {e}. Returning raw typed dictionaries.")

                results.append({
                    "file_id": file_info["file_id"],
                    "filename": filename, # Renamed to match DATA_STANDARDS.md
                    "success": final_result['success'], # Use cleaning result's success
                    "bank_info": bank_info_pydantic.dict(), # Convert Pydantic model to dict for response
                    "parse_result": { # Structure to match DATA_STANDARDS.md
                        "success": final_result['success'],
                        "headers": final_result['headers'],
                        "data": final_data_for_response,
                        "row_count": len(final_data_for_response)
                    },
                    "config": current_config, # Store the config that was actually used
                })
            
            print(f" Successfully parsed all {len(results)} files")
            return {
                "success": True,
                "parsed_csvs": results,
                "total_files": len(results)
            }
            
        except Exception as e:
            print(f"[ERROR]  Multi-CSV parse exception: {str(e)}")
            import traceback
            print(f" Full traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _quick_bank_detection(self, filename: str) -> dict:
        """Quick filename-based bank detection for preprocessing decisions"""
        # Simple filename-based detection to determine preprocessing strategy
        bank_result = self.bank_detector.detect_bank(filename, "", [])
        
        if bank_result.bank_name != 'unknown' and bank_result.confidence >= 0.1:
            try:
                # Check if this bank uses header_row (all banks now use absolute positioning)
                import os
                import configparser
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
    
    def _apply_preprocessing(self, file_path: str, config: dict, quick_detection: dict = None):
        """Apply generic CSV preprocessing"""
        print(f" Step 1: Generic CSV preprocessing (bank-agnostic)")
        
        # Check if we should skip empty row removal for absolute positioning banks
        skip_empty_row_removal = False
        if quick_detection and quick_detection.get('uses_absolute_positioning', False):
            skip_empty_row_removal = True
            print(f" Using bank-aware preprocessing for {quick_detection['bank_name']} (preserving empty rows)")
        else:
            print(f" Using bank-agnostic CSV preprocessing (bank_type 'generic' ignored)")
        
        # Apply generic CSV preprocessing (fixes multiline fields, encoding, etc.)
        # Ensure the preprocessor uses the provided encoding from config
        preprocessing_result = self.csv_preprocessor.preprocess_csv(
            file_path, 
            'generic',  # Bank-agnostic preprocessing
            config.encoding, # Use the effective_encoding from the config
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
            print(f"[SUCCESS] Generic preprocessing applied: {len(preprocessing_result['issues_fixed'])} issues fixed")
            print(f"   [DATA] Rows: {preprocessing_result['original_rows']} → {preprocessing_result['processed_rows']}")
        else:
            print(f" Generic preprocessing skipped (no issues found)")
        
        return {
            'file_path': actual_file_path,
            'info': preprocessing_info
        }
    
    def _detect_bank_and_headers(self, file_path: str, filename: str, current_file_config: dict, file_encoding: str, preprocessing_applied: bool):
        """Detect bank and validate header using robust header validation."""
        from backend.csv_parser.header_validator import find_and_validate_header, HeaderValidationError
        
        print(f" Step 4: Detecting bank and headers for {filename} with encoding {file_encoding}")

        # Read initial content for bank detection
        content_for_detection = ""
        sample_headers_for_detection = []
        try:
            with open(file_path, 'r', encoding=file_encoding, newline='') as f:
                raw_lines_for_detection = [next(f, '') for _ in range(20)]
            content_for_detection = "".join(raw_lines_for_detection)
            for line in raw_lines_for_detection:
                if line.strip():
                    sample_headers_for_detection = [h.strip() for h in line.split(',')] # Basic CSV split
                    break
        except Exception as e:
            print(f"  [WARNING] Warning: Could not read initial lines from {file_path} for bank detection: {e}")

        bank_detection_result = self.bank_detector.detect_bank(filename, content_for_detection, sample_headers_for_detection)

        if bank_detection_result.bank_name != 'unknown' and bank_detection_result.confidence > 0.1:
            detected_bank_name = bank_detection_result.bank_name
            print(f" Tentatively detected bank: {detected_bank_name} (confidence: {bank_detection_result.confidence:.2f})")

            try:
                # Get config from the unified service
                bank_config = self.config_service.get_bank_config(detected_bank_name)
                if not bank_config:
                    raise ValueError(f"Could not retrieve config for bank '{detected_bank_name}'")

                detection_conf = bank_config.detection_info

                # Read header_row directly from config file (not in CSVConfig object)
                import os
                import configparser
                config_file_path = os.path.join(self.config_service.config_dir, f"{detected_bank_name}.conf")
                raw_config = configparser.ConfigParser()
                raw_config.read(config_file_path)
                
                configured_row_1_indexed = raw_config.getint('csv_config', 'header_row', fallback=None)
                if configured_row_1_indexed is None:
                    raise ValueError(f"Configuration for '{detected_bank_name}' is missing 'header_row'.")

                header_row_0_indexed = configured_row_1_indexed - 1

                # The new, simple, and robust validation call
                find_and_validate_header(
                    file_path=file_path,
                    encoding=file_encoding,
                    configured_header_row=header_row_0_indexed,
                    expected_headers=detection_conf.required_headers
                )

                effective_header_row = header_row_0_indexed
                effective_data_start_row = effective_header_row + 1
                print(f"Header validated for {detected_bank_name}. Effective header_row={effective_header_row}, data_start_row={effective_data_start_row}")

                return bank_detection_result, {
                    'header_row': effective_header_row,
                    'data_start_row': effective_data_start_row
                }

            except (ValueError, HeaderValidationError) as e:
                print(f"[ERROR] Header detection/validation failed for {detected_bank_name}: {e}")
                # Return a failure state
                return bank_detection_result, {
                    'header_row': None,
                    'data_start_row': None,
                    'error': str(e)
                }

        else:
            print(f" No specific bank detected with sufficient confidence, or bank is 'unknown'. Using fallback.")
            # For unknown banks, use fallback approach
            return bank_detection_result, {
                'header_row': 0,  # Default to first row
                'data_start_row': 1
            }
    
    
    def _parse_with_bank_info(self, file_path: str, config: dict, header_info: dict):
        """Parse file with enhanced parser using bank-detected info"""
        print(f"ℹ [MIGRATION][MultiCSVService] _parse_with_bank_info using UnifiedCSVParser.")
        print(f"  Config: end_row={config.end_row}, start_col={config.start_col}, end_col={config.end_col}, encoding={config.encoding}")
        print(f"  Header info: data_start_row={header_info['data_start_row']}, header_row={header_info['header_row']}")

        header_row_for_unified = header_info['header_row']
        data_start_row_for_unified = header_info['data_start_row']
        max_rows_for_unified = None
        if config.end_row is not None and header_row_for_unified is not None and config.end_row >= header_row_for_unified:
             # max_rows is number of data rows after header
            max_rows_for_unified = config.end_row - header_row_for_unified
        
        if config.start_col != 0 or config.end_col is not None:
            print(f"[WARNING] [MIGRATION][MultiCSVService] Column range (start_col={config.start_col}, end_col={config.end_col}) is not supported by UnifiedCSVParser. All columns will be parsed.")

        print(f"  UnifiedParser params: encoding='{config.encoding}', header_row={header_row_for_unified}, start_row={data_start_row_for_unified}, max_rows={max_rows_for_unified}")

        # Parse with UnifiedCSVParser
        parse_result = self.unified_parser.parse_csv(
            file_path,
            encoding=config.encoding,
            header_row=header_row_for_unified,
            start_row=data_start_row_for_unified,
            max_rows=max_rows_for_unified
        )
        print(f"  UnifiedParser parse_csv result success: {parse_result.get('success')}")

        if parse_result.get('success'):
            parsed_headers = parse_result.get('headers', [])
            print(f"  [MultiCSVService] Headers parsed by UnifiedCSVParser: {parsed_headers}")
            
        else:
            print(f"  [MultiCSVService] UnifiedCSVParser failed. Error: {parse_result.get('error')}")

        return parse_result
    
    def _finalize_bank_detection(self, filename: str, parse_result: dict, 
                                bank_detection, preprocessing_info: dict):
        """Finalize bank detection on parsed data"""
        print(f" Step 6: Final bank detection on parsed data for {filename}")
        
        detection_result = self.bank_detector.detect_bank_from_data(
            filename, 
            parse_result['data']
        )
        print(f"Final bank detected: {detection_result.bank_name} (confidence={detection_result.confidence:.2f})")
        print(f" Detection reasons: {detection_result.reasons}")
        
        # Store comprehensive bank detection info
        return {
            'bank_name': detection_result.bank_name,  # Changed from detected_bank to bank_name for Pydantic compatibility
            'detected_bank': detection_result.bank_name,  # Keep for backwards compatibility
            'confidence': detection_result.confidence,
            'reasons': detection_result.reasons,
            'original_headers': parse_result.get('headers', []),
            'preprocessing_applied': preprocessing_info['applied'],
            'preprocessing_info': preprocessing_info
        }
    
    def _apply_cleaning_if_enabled(self, parse_result: dict, bank_info: dict, enable_cleaning: bool):
        """Apply data cleaning if enabled"""
        final_result = parse_result
        
        if enable_cleaning:
            print(f" Applying data cleaning...")
            
            # Create bank-specific cleaning config
            bank_cleaning_config = None
            if bank_info['detected_bank'] != 'unknown':
                bank_column_mapping = self.config_service.get_column_mapping(bank_info['detected_bank'])
                # Get expected headers from bank detection info instead of CSV config
                detection_patterns = self.config_service.get_detection_patterns()
                expected_headers = []
                if bank_info['detected_bank'] in detection_patterns:
                    expected_headers = detection_patterns[bank_info['detected_bank']].required_headers
                
                bank_cleaning_config = {
                    'column_mapping': bank_column_mapping,
                    'bank_name': bank_info['detected_bank'],
                    'expected_headers': expected_headers # Pass expected_headers from detection info
                }
                print(f" Using bank-specific cleaning config for {bank_info['detected_bank']}: {bank_cleaning_config}")
            
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
                print(f"[SUCCESS] Data cleaning successful: {cleaning_result['row_count']} clean rows")
            else:
                print(f"[WARNING] Data cleaning failed, using uncleaned data")
                final_result['cleaning_applied'] = False
                final_result['bank_info'] = bank_info
        else:
            final_result['cleaning_applied'] = False
            final_result['bank_info'] = bank_info
        
        return final_result

    def _map_to_pydantic_rows(self, data_dicts: List[Dict[str, Any]], column_mapping: Dict[str, str]) -> List[CSVRow]:
        """
        Maps a list of dictionaries (with pre-converted types) to a list of CSVRow Pydantic models
        using a provided column mapping.
        """
        csv_rows: List[CSVRow] = []
        
        # Invert mapping for easier lookup: {'target_field': 'source_header'}
        # This assumes column_mapping is like {'source_header': 'target_field'}
        # We need to map from target_field to source_header for lookup in row_dict
        target_to_source_map = {v: k for k, v in column_mapping.items()}

        for row_dict in data_dicts:
            try:
                # Find values from the source dict using the mapping
                # Use .get() with a default of None to handle missing optional fields gracefully
                date_val = row_dict.get(target_to_source_map.get('date'))
                desc_val = row_dict.get(target_to_source_map.get('description'), '') # Default to empty string
                balance_val = row_dict.get(target_to_source_map.get('balance'))
                
                # Handle amount, which can be from 'amount', 'debit', or 'credit'
                amount_val = row_dict.get(target_to_source_map.get('amount'))
                if amount_val is None:
                    debit_val = row_dict.get(target_to_source_map.get('debit'))
                    credit_val = row_dict.get(target_to_source_map.get('credit'))
                    if debit_val is not None and isinstance(debit_val, (Decimal, int, float)):
                        amount_val = -Decimal(debit_val) # Debits are negative
                    elif credit_val is not None and isinstance(credit_val, (Decimal, int, float)):
                        amount_val = Decimal(credit_val)

                # Create the Pydantic model, which will validate the types
                csv_row = CSVRow(
                    date=date_val,
                    amount=amount_val,
                    description=str(desc_val), # Ensure description is string
                    balance=balance_val
                )
                csv_rows.append(csv_row)
            except Exception as e:
                print(f"[WARNING] Skipping row due to CSVRow conversion error: {e}. Row: {row_dict}")
                continue
        return csv_rows
