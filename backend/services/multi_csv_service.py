"""
Multi-CSV parsing service for handling multiple file operations
"""
import os
import sys

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # from enhanced_csv_parser import EnhancedCSVParser # Old import
    from csv_parser import UnifiedCSVParser # New parser import
    from data_cleaner import DataCleaner
    from bank_detection import BankDetector, BankConfigManager
    from csv_parser import EncodingDetector # Import EncodingDetector
    from csv_preprocessing.csv_preprocessor import CSVPreprocessor
except ImportError:
    # Fallback path for import issues
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if backend_path not in sys.path: # Ensure backend_path is added only once
        sys.path.insert(0, backend_path)
    # from enhanced_csv_parser import EnhancedCSVParser # Old import
    from csv_parser import UnifiedCSVParser # New parser import
    from data_cleaner import DataCleaner
    from bank_detection import BankDetector, BankConfigManager
    from csv_parser import EncodingDetector # Import EncodingDetector
    from csv_preprocessing.csv_preprocessor import CSVPreprocessor

class MultiCSVService:
    """Service for handling multi-CSV parsing operations"""
    
    def __init__(self):
        self.unified_parser = UnifiedCSVParser() # New parser instance
        self.data_cleaner = DataCleaner()
        self.bank_config_manager = BankConfigManager()
        self.bank_detector = BankDetector(self.bank_config_manager)
        self.csv_preprocessor = CSVPreprocessor()
        self.encoding_detector = EncodingDetector() # Initialize EncodingDetector
    
    def parse_multiple_files(self, file_infos: list, parse_configs: list, 
                           user_name: str = "User", enable_cleaning: bool = True): # Changed default user_name for generic use
        """
        Parse multiple CSV files with preprocessing and bank detection
        
        Args:
            file_infos: List of file info dictionaries
            parse_configs: List of parsing configurations
            user_name: User name for processing
            enable_cleaning: Whether to enable data cleaning
            
        Returns:
            dict: Multi-CSV parsing result
        """
        print(f"ℹ️ [MIGRATION][MultiCSVService] parse_multiple_files called for {len(file_infos)} files.")
        print(f"  Data cleaning enabled: {enable_cleaning}")
        
        try:
            results = []
            
            # Process each file
            for i, (file_info, config) in enumerate(zip(file_infos, parse_configs)):
                print(f"📁 Processing file {i+1}/{len(file_infos)}: {file_info['file_id']}")
                
                file_path = file_info["temp_path"]
                filename = file_info["original_name"]
                
                # Step 1: Determine effective encoding
                encoding_from_config = config.get('encoding')
                effective_encoding = encoding_from_config
                
                # If config encoding is None or a generic 'utf-8' (which might be a default), try to detect.
                # For Forint bank files, we know 'utf-8' is often wrong.
                if not effective_encoding or (effective_encoding.lower() == 'utf-8' and filename.startswith("11600006-")):
                    print(f"ℹ️ [MultiCSVService] Config encoding is '{effective_encoding}'. Detecting encoding for '{filename}'.")
                    detection_result = self.encoding_detector.detect_encoding(file_path)
                    effective_encoding = detection_result['encoding']
                    print(f"👍 [MultiCSVService] Detected encoding for '{filename}': {effective_encoding} (confidence: {detection_result['confidence']:.2f})")
                
                # Update config with the effective encoding to be used by subsequent steps
                current_config = {**config, 'encoding': effective_encoding}
                
                # Step 2: Generic CSV preprocessing
                preprocessing_result = self._apply_preprocessing(file_path, current_config)
                
                # Step 3: Bank detection and header finding
                bank_detection, header_info = self._detect_bank_and_headers(
                    preprocessing_result['file_path'], filename, current_config,
                    effective_encoding, # Pass effective_encoding
                    preprocessing_result['info']['applied'] # Pass preprocessing status
                )
                
                # Step 4: Parse with enhanced parser
                parse_result = self._parse_with_bank_info(
                    preprocessing_result['file_path'], current_config, header_info # Pass current_config
                )


                if not parse_result['success']:
                    raise Exception(f"Failed to parse {filename}: {parse_result.get('error', 'Unknown error')}")
                
                # Step 4: Final bank detection on parsed data
                final_bank_info = self._finalize_bank_detection( # Renamed from Step 4 to Step 5
                    filename, parse_result, bank_detection, preprocessing_result['info']
                )
                
                # Step 5: Apply data cleaning if enabled
                final_result = self._apply_cleaning_if_enabled( # Renamed from Step 5 to Step 6
                    parse_result, final_bank_info, enable_cleaning
                )
                
                results.append({
                    "file_id": file_info["file_id"],
                    "file_name": filename,
                    "parse_result": final_result,
                    "config": current_config, # Store the config that was actually used
                    "data": final_result['data'],
                    "bank_info": final_bank_info
                })
            
            print(f"🎉 Successfully parsed all {len(results)} files")
            return {
                "success": True,
                "parsed_csvs": results,
                "total_files": len(results)
            }
            
        except Exception as e:
            print(f"❌ Multi-CSV parse exception: {str(e)}")
            import traceback
            print(f"📖 Full traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _apply_preprocessing(self, file_path: str, config: dict):
        """Apply generic CSV preprocessing"""
        print(f"🔧 Step 1: Generic CSV preprocessing (bank-agnostic)")
        
        # Apply generic CSV preprocessing (fixes multiline fields, encoding, etc.)
        # Ensure the preprocessor uses the provided encoding from config
        preprocessing_result = self.csv_preprocessor.preprocess_csv(
            file_path, 
            'generic',  # Bank-agnostic preprocessing
            config['encoding'] # Use the effective_encoding from the config
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
            print(f"✅ Generic preprocessing applied: {len(preprocessing_result['issues_fixed'])} issues fixed")
            print(f"   📊 Rows: {preprocessing_result['original_rows']} → {preprocessing_result['processed_rows']}")
        else:
            print(f"📝 Generic preprocessing skipped (no issues found)")
        
        return {
            'file_path': actual_file_path,
            'info': preprocessing_info
        }
    
    def _detect_bank_and_headers(self, file_path: str, filename: str, current_file_config: dict, file_encoding: str, preprocessing_applied: bool):
        """Detect bank and determine effective header_row and data_start_row, considering preprocessing."""
        print(f"🔧 Step 2: Detecting bank and headers for {filename} with encoding {file_encoding}")

        user_header_row = current_file_config.get('header_row')
        user_data_start_row = current_file_config.get('start_row') # This is the 'start_row' from the input parse_configs
        print(f"  Initial user-provided config: header_row={user_header_row}, data_start_row={user_data_start_row}")

        # Read initial content for more accurate bank detection
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
            print(f"  ⚠️ Warning: Could not read initial lines from {file_path} for bank detection: {e}")

        bank_detection_result = self.bank_detector.detect_bank(filename, content_for_detection, sample_headers_for_detection)

        effective_header_row = user_header_row
        effective_data_start_row = user_data_start_row # Placeholder, will be refined

        if bank_detection_result.bank_name != 'unknown' and bank_detection_result.confidence > 0.1:
            detected_bank_name = bank_detection_result.bank_name
            print(f"🏦 Tentatively detected bank: {detected_bank_name} (confidence: {bank_detection_result.confidence:.2f})")

            bank_csv_config = self.bank_config_manager.get_csv_config(detected_bank_name)
            bank_config_header_row = bank_csv_config.get('header_row')
            # 'data_start_row' from get_csv_config is guaranteed to be header_row + 1 or more
            bank_config_data_start_row = bank_csv_config.get('data_start_row')

            print(f"  Bank-specific config for {detected_bank_name}: header_row={bank_config_header_row}, data_start_row={bank_config_data_start_row}")

            if user_header_row is not None:
                effective_header_row = user_header_row
                print(f"  Using user-provided header_row: {effective_header_row}")
                if user_data_start_row is not None: # User also provided data_start_row
                    effective_data_start_row = user_data_start_row
                elif effective_header_row is not None: # User provided header_row, derive data_start_row
                    effective_data_start_row = effective_header_row + 1
            # If no user_header_row, proceed with detection logic
            # Prioritize dynamic detection if preprocessing was applied or if bank config doesn't have a fixed header_row
            elif preprocessing_applied or bank_config_header_row is None:
                print(f"  Preprocessing applied ({preprocessing_applied}) or bank_config_header_row is None. Attempting dynamic header detection on file '{os.path.basename(file_path)}' using BankConfigManager for {detected_bank_name}.")
                header_detection_cfg_result = self.bank_config_manager.detect_header_row(
                    file_path, detected_bank_name, file_encoding
                )
                if header_detection_cfg_result['success'] and header_detection_cfg_result.get('header_row') is not None:
                    effective_header_row = header_detection_cfg_result['header_row']
                    effective_data_start_row = header_detection_cfg_result['data_start_row']
                    print(f"  Dynamically detected header_row: {effective_header_row}, data_start_row: {effective_data_start_row} using BankConfigManager (method: {header_detection_cfg_result.get('method')}).")
                # Fallback to bank_config_header_row if dynamic detection failed but a config value exists
                elif bank_config_header_row is not None:
                    effective_header_row = bank_config_header_row
                    effective_data_start_row = bank_config_data_start_row
                    print(f"  Dynamic detection failed. Using header_row {effective_header_row} from {detected_bank_name} config as fallback.")
                else:
                    print(f"  ⚠️ Dynamic header detection using BankConfigManager failed for {detected_bank_name}. Error: {header_detection_cfg_result.get('error')}")
                    # effective_header_row remains None or its previous value
            elif bank_config_header_row is not None: # No user override, no preprocessing (or preproc didn't trigger dynamic), but bank_config_header_row exists
                effective_header_row = bank_config_header_row
                effective_data_start_row = bank_config_data_start_row
                print(f"  Using header_row {effective_header_row} from {detected_bank_name} config (preprocessing_applied={preprocessing_applied}).")

            # If user_data_start_row was explicitly provided, it should override any derived data_start_row,
            # unless user_header_row was also provided (handled above).
            if user_data_start_row is not None and user_header_row is None:
                effective_data_start_row = user_data_start_row
                print(f"  Applying user-provided data_start_row: {effective_data_start_row} (as user_header_row was not set).")

        else:
            print(f"📝 No specific bank detected with sufficient confidence, or bank is 'unknown'. Using user-provided or default header/data start rows.")
            # If user_header_row or user_data_start_row were provided, they are already set in effective_header_row/effective_data_start_row

        # Final adjustments for data_start_row if it's still not sensible
        if effective_header_row is not None:
            # If effective_data_start_row is still None or not after header, set it to header_row + 1
            if effective_data_start_row is None or effective_data_start_row <= effective_header_row:
                effective_data_start_row = effective_header_row + 1
                print(f"  Adjusted data_start_row to {effective_data_start_row} (as header_row + 1).")
        elif effective_data_start_row is None: # Header is None, data_start_row is None
            effective_data_start_row = 1 # Default to 1 (assuming header is 0 for parser)
            print(f"  Defaulting data_start_row to {effective_data_start_row} as header_row is unknown.")
        
        print(f"  Final effective settings for parsing: header_row={effective_header_row}, data_start_row={effective_data_start_row}")
        return bank_detection_result, {
            'header_row': effective_header_row,
            'data_start_row': effective_data_start_row
        }
    
    def _find_headers_dynamically(self, file_path: str, bank_name: str, config: dict):
        """DEPRECATED: Find headers dynamically. BankConfigManager.detect_header_row is preferred."""
        print(f"⚠️ [MultiCSVService] _find_headers_dynamically is deprecated and should not be called directly. Using BankConfigManager.detect_header_row instead.")
        # Fallback to BankConfigManager's method if somehow called.
        header_detection_result = self.bank_config_manager.detect_header_row(file_path, bank_name, config.get('encoding', 'utf-8'))
        if header_detection_result['success']:
            return header_detection_result['header_row'], header_detection_result['data_start_row']
        return config.get('header_row'), config.get('start_row', config.get('header_row', 0) + 1 if config.get('header_row') is not None else 1)
    
    def _parse_with_bank_info(self, file_path: str, config: dict, header_info: dict):
        """Parse file with enhanced parser using bank-detected info"""
        print(f"ℹ️ [MIGRATION][MultiCSVService] _parse_with_bank_info using UnifiedCSVParser.")
        print(f"  Config: end_row={config.get('end_row')}, start_col={config.get('start_col', 0)}, end_col={config.get('end_col')}, encoding={config['encoding']}")
        print(f"  Header info: data_start_row={header_info['data_start_row']}, header_row={header_info['header_row']}")

        header_row_for_unified = header_info['header_row']
        max_rows_for_unified = None
        if config.get('end_row') is not None and header_row_for_unified is not None and config.get('end_row') >= header_row_for_unified:
             # max_rows is number of data rows after header
            max_rows_for_unified = config.get('end_row') - header_row_for_unified
        
        if config.get('start_col', 0) != 0 or config.get('end_col') is not None:
            print(f"⚠️ [MIGRATION][MultiCSVService] Column range (start_col={config.get('start_col', 0)}, end_col={config.get('end_col')}) is not supported by UnifiedCSVParser. All columns will be parsed.")

        print(f"  UnifiedParser params: encoding='{config['encoding']}', header_row={header_row_for_unified}, max_rows={max_rows_for_unified}")

        # Parse with UnifiedCSVParser
        parse_result = self.unified_parser.parse_csv(
            file_path,
            encoding=config['encoding'],
            header_row=header_row_for_unified,
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
        print(f"🔍 Step 4: Final bank detection on parsed data for {filename}")
        
        detection_result = self.bank_detector.detect_bank_from_data(
            filename, 
            parse_result['data']
        )
        print(f"🎯 Final bank detected: {detection_result.bank_name} (confidence={detection_result.confidence:.2f})")
        print(f"📋 Detection reasons: {detection_result.reasons}")
        
        # Store comprehensive bank detection info
        return {
            'detected_bank': detection_result.bank_name,
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
            print(f"🧹 Applying data cleaning...")
            
            # Create bank-specific cleaning config
            bank_cleaning_config = None
            if bank_info['detected_bank'] != 'unknown':
                bank_column_mapping = self.bank_config_manager.get_column_mapping(bank_info['detected_bank'])
                bank_csv_cfg = self.bank_config_manager.get_csv_config(bank_info['detected_bank'])
                bank_cleaning_config = {
                    'column_mapping': bank_column_mapping,
                    'bank_name': bank_info['detected_bank'],
                    'expected_headers': bank_csv_cfg.get('expected_headers', []) # Pass expected_headers
                }
                print(f"🗺️ Using bank-specific cleaning config for {bank_info['detected_bank']}: {bank_cleaning_config}")
            
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
                print(f"✅ Data cleaning successful: {cleaning_result['row_count']} clean rows")
            else:
                print(f"⚠️ Data cleaning failed, using uncleaned data")
                final_result['cleaning_applied'] = False
                final_result['bank_info'] = bank_info
        else:
            final_result['cleaning_applied'] = False
            final_result['bank_info'] = bank_info
        
        return final_result
