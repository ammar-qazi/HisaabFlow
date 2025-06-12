"""
Parsing service for single CSV file operations
"""
import os
import sys

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from enhanced_csv_parser import EnhancedCSVParser
    from data_cleaner import DataCleaner
    from bank_detection import BankDetector, BankConfigManager
except ImportError:
    # Fallback path for import issues
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, backend_path)
    from enhanced_csv_parser import EnhancedCSVParser
    from data_cleaner import DataCleaner
    from bank_detection import BankDetector, BankConfigManager


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
        self.enhanced_parser = EnhancedCSVParser()
        self.data_cleaner = DataCleaner()
        self.bank_config_manager = BankConfigManager()
        self.bank_detector = BankDetector(self.bank_config_manager)
    
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
        print(f"🕵️‍♂️ Parse range request for file: {filename}")
        print(f"🧹 Data cleaning enabled: {config.enable_cleaning}")
        
        try:
            # Parse with enhanced parser
            parse_result = self.enhanced_parser.parse_with_range(
                file_path, 
                config.start_row, 
                config.end_row, 
                config.start_col, 
                config.end_col, 
                config.encoding
            )
            
            if not parse_result['success']:
                return {
                    'success': False,
                    'error': parse_result['error']
                }
            
            # Bank detection on raw data (before cleaning)
            print(f"🔍 Detecting bank for single file using RAW CSV data...")
            detection_result = self.bank_detector.detect_bank_from_data(
                filename, 
                parse_result['data']
            )
            print(f"🎯 Single file bank detected: {detection_result.bank_name} (confidence={detection_result.confidence:.2f})")
            
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
                print(f"🧹 Applying data cleaning...")
                
                # Create bank-specific cleaning config
                bank_cleaning_config = None
                if bank_info['detected_bank'] != 'unknown':
                    bank_column_mapping = self.bank_config_manager.get_column_mapping(bank_info['detected_bank'])
                    bank_cleaning_config = {
                        'column_mapping': bank_column_mapping,
                        'bank_name': bank_info['detected_bank']
                    }
                    print(f"🗺️ Using bank-specific cleaning config: {bank_cleaning_config}")
                
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
                    print(f"✅ Data cleaning successful")
                else:
                    print(f"⚠️ Data cleaning failed, using uncleaned data")
                    final_result['cleaning_applied'] = False
                    final_result['bank_info'] = bank_info
            else:
                final_result['cleaning_applied'] = False
                final_result['bank_info'] = bank_info
            
            return final_result
            
        except Exception as e:
            print(f"❌ Parse exception: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
