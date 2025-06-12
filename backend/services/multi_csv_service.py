"""
Multi-CSV parsing service for handling multiple file operations
"""
import os
import sys

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from enhanced_csv_parser import EnhancedCSVParser
    from data_cleaner import DataCleaner
    from bank_detection import BankDetector, BankConfigManager
    from csv_preprocessing.csv_preprocessor import CSVPreprocessor
except ImportError:
    # Fallback path for import issues
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, backend_path)
    from enhanced_csv_parser import EnhancedCSVParser
    from data_cleaner import DataCleaner
    from bank_detection import BankDetector, BankConfigManager
    from csv_preprocessing.csv_preprocessor import CSVPreprocessor


class MultiCSVService:
    """Service for handling multi-CSV parsing operations"""
    
    def __init__(self):
        self.enhanced_parser = EnhancedCSVParser()
        self.data_cleaner = DataCleaner()
        self.bank_config_manager = BankConfigManager()
        self.bank_detector = BankDetector(self.bank_config_manager)
        self.csv_preprocessor = CSVPreprocessor()
    
    def parse_multiple_files(self, file_infos: list, parse_configs: list, 
                           user_name: str = "Ammar Qazi", enable_cleaning: bool = True):
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
        print(f"🚀 Multi-CSV parse request for {len(file_infos)} files")
        print(f"🧹 Data cleaning enabled: {enable_cleaning}")
        
        try:
            results = []
            
            # Process each file
            for i, (file_info, config) in enumerate(zip(file_infos, parse_configs)):
                print(f"📁 Processing file {i+1}/{len(file_infos)}: {file_info['file_id']}")
                
                file_path = file_info["temp_path"]
                filename = file_info["original_name"]
                
                # Step 1: Generic CSV preprocessing
                preprocessing_result = self._apply_preprocessing(file_path, config)
                
                # Step 2: Bank detection and header finding
                bank_detection, header_info = self._detect_bank_and_headers(
                    preprocessing_result['file_path'], filename, config
                )
                
                # Step 3: Parse with enhanced parser
                parse_result = self._parse_with_bank_info(
                    preprocessing_result['file_path'], config, header_info
                )
                
                if not parse_result['success']:
                    raise Exception(f"Failed to parse {filename}: {parse_result.get('error', 'Unknown error')}")
                
                # Step 4: Final bank detection on parsed data
                final_bank_info = self._finalize_bank_detection(
                    filename, parse_result, bank_detection, preprocessing_result['info']
                )
                
                # Step 5: Apply data cleaning if enabled
                final_result = self._apply_cleaning_if_enabled(
                    parse_result, final_bank_info, enable_cleaning
                )
                
                results.append({
                    "file_id": file_info["file_id"],
                    "file_name": filename,
                    "parse_result": final_result,
                    "config": config,
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
        preprocessing_result = self.csv_preprocessor.preprocess_csv(
            file_path, 
            'generic',  # Bank-agnostic preprocessing
            config.get('encoding', 'utf-8')
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
    
    def _detect_bank_and_headers(self, file_path: str, filename: str, config: dict):
        """Detect bank and find headers in the file"""
        print(f"🔧 Step 2: Detecting bank for proper parsing of {filename}")
        
        # Detect bank on cleaned file (should be more accurate now)
        bank_detection = self.bank_detector.detect_bank(filename, "", [])
        header_row = None
        data_start_row = config.get('start_row', 0)
        
        if bank_detection.bank_name != 'unknown' and bank_detection.confidence > 0.1:
            print(f"🏦 Bank detected: {bank_detection.bank_name} (confidence: {bank_detection.confidence:.2f})")
            
            # Dynamic header detection: Find headers in preprocessed file
            header_row, data_start_row = self._find_headers_dynamically(
                file_path, bank_detection.bank_name, config
            )
        else:
            print(f"📝 Using manual config for unknown bank")
        
        return bank_detection, {
            'header_row': header_row,
            'data_start_row': data_start_row
        }
    
    def _find_headers_dynamically(self, file_path: str, bank_name: str, config: dict):
        """Find headers dynamically in preprocessed file"""
        print(f"🔧 Finding headers dynamically in preprocessed file")
        
        header_row = None
        data_start_row = config.get('start_row', 0)
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
            
            # Look for the characteristic headers based on bank type
            header_patterns = {
                'nayapay': ['TIMESTAMP', 'TYPE', 'DESCRIPTION'],
                'wise_usd': ['Date', 'Amount', 'Description'],
                'wise_eur': ['Date', 'Amount', 'Description'],
                'wise_huf': ['Date', 'Amount', 'Description']
            }
            
            patterns = header_patterns.get(bank_name, ['Date', 'Amount'])
            
            for i, line in enumerate(lines):
                line_upper = line.upper()
                if all(pattern.upper() in line_upper for pattern in patterns):
                    header_row = i
                    data_start_row = i + 1
                    print(f"🔧 Found headers at row {header_row} in preprocessed file")
                    print(f"🔧 Headers: {line.strip()}")
                    break
            
            if header_row is None:
                print(f"⚠️ Could not find headers in preprocessed file, using manual config")
                
        except Exception as e:
            print(f"⚠️ Header detection failed: {e}")
        
        return header_row, data_start_row
    
    def _parse_with_bank_info(self, file_path: str, config: dict, header_info: dict):
        """Parse file with enhanced parser using bank-detected info"""
        print(f"🔧 Step 3: Parsing with enhanced parser")
        
        # Parse with enhanced parser using proper header/data separation
        parse_result = self.enhanced_parser.parse_with_range(
            file_path,  # Use preprocessed file
            header_info['data_start_row'],  # Use bank-detected data start row
            config.get('end_row'),
            config.get('start_col', 0),
            config.get('end_col'),
            config.get('encoding', 'utf-8'),
            header_info['header_row']  # Pass separate header row
        )
        
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
                bank_cleaning_config = {
                    'column_mapping': bank_column_mapping,
                    'bank_name': bank_info['detected_bank']
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
