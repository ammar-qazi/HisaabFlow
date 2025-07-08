"""
Parsing service for single CSV file operations
"""
from backend.csv_parser import UnifiedCSVParser
from backend.data_cleaner import DataCleaner
from backend.bank_detection import BankDetector
from backend.shared.config.unified_config_service import get_unified_config_service


class ParseConfig:
    """Configuration for parsing operations"""
    def __init__(self, start_row: int, end_row: int = None, start_col: int = 0, 
                 end_col: int = None, encoding: str = "utf-8", enable_cleaning: bool = True):
        self.start_row = start_row
        self.end_row = end_row
        self.start_col = start_col
        self.end_col = end_col
        self.encoding = encoding
        self.enable_cleaning = enable_cleaning


class ParsingService:
    """Service for handling single CSV file parsing operations"""
    
    def __init__(self):
        self.unified_parser = UnifiedCSVParser() # New parser instance
        self.data_cleaner = DataCleaner()
        self.config_service = get_unified_config_service()
        self.bank_detector = BankDetector(self.config_service)
        print(f"ℹ [MIGRATION][ParsingService] Initialized with UnifiedCSVParser.")
    
    def parse_single_file(self, file_path: str, filename: str, config: ParseConfig):
        """
        Parse single CSV file with specified range and data cleaning
        
        Args:
            file_path: Path to the CSV file
            filename: Original filename for bank detection
            config: ParseConfig with parsing parameters
            
        Returns:
            dict: Parsing result with bank detection and cleaning info
        """
        print(f"ℹ [MIGRATION][ParsingService] parse_single_file called for: {filename}")
        print(f"  Config: start_row={config.start_row}, end_row={config.end_row}, start_col={config.start_col}, end_col={config.end_col}, encoding={config.encoding}")
        print(f"  Data cleaning enabled: {config.enable_cleaning}")
        
        try:
            # Determine header_row and max_rows for UnifiedCSVParser
            # Assuming config.start_row is the 0-indexed header row
            header_row_for_unified = config.start_row
            max_rows_for_unified = None
            if config.end_row is not None and config.end_row >= header_row_for_unified:
                # max_rows is number of data rows after header
                max_rows_for_unified = config.end_row - header_row_for_unified
            
            if config.start_col != 0 or config.end_col is not None:
                print(f"[WARNING] [MIGRATION][ParsingService] Column range (start_col={config.start_col}, end_col={config.end_col}) is not supported by UnifiedCSVParser. All columns will be parsed.")

            print(f"  UnifiedParser params: encoding='{config.encoding}', header_row={header_row_for_unified}, max_rows={max_rows_for_unified}")
            
            # Parse with UnifiedCSVParser
            parse_result = self.unified_parser.parse_csv(
                file_path,
                encoding=config.encoding,
                header_row=header_row_for_unified, # Pass determined header_row
                max_rows=max_rows_for_unified     # Pass determined max_rows
            )
            print(f"  UnifiedParser parse_csv result success: {parse_result.get('success')}")

            if not parse_result['success']:
                return {
                    'success': False,
                    'error': parse_result['error']
                }
            
            # Bank detection on raw data (before cleaning)
            print(f" Detecting bank for single file using RAW CSV data...")
            detection_result = self.bank_detector.detect_bank_from_data(
                filename, 
                parse_result['data']
            )
            print(f"Single file bank detected: {detection_result.bank_name} (confidence={detection_result.confidence:.2f})")
            
            # Store bank detection info
            bank_info = {
                'detected_bank': detection_result.bank_name,
                'confidence': detection_result.confidence,
                'reasons': detection_result.reasons,
                'original_headers': parse_result.get('headers', [])
            }
            
            # Apply data cleaning if enabled
            final_result = parse_result
            if config.enable_cleaning:
                print(f" Applying data cleaning...")
                
                # Create bank-specific cleaning config
                bank_cleaning_config = None
                if bank_info['detected_bank'] != 'unknown':
                    bank_column_mapping = self.config_service.get_column_mapping(bank_info['detected_bank'])
                    bank_cleaning_config = {
                        'column_mapping': bank_column_mapping,
                        'bank_name': bank_info['detected_bank']
                    }
                    print(f" Using bank-specific cleaning config: {bank_cleaning_config}")
                
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
                    print(f"[SUCCESS] Data cleaning successful")
                else:
                    print(f"[WARNING] Data cleaning failed, using uncleaned data")
                    final_result['cleaning_applied'] = False
                    final_result['bank_info'] = bank_info
            else:
                final_result['cleaning_applied'] = False
                final_result['bank_info'] = bank_info
            
            return final_result
            
        except Exception as e:
            print(f"[ERROR]  Parse exception: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
