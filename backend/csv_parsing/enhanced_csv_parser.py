"""
Enhanced CSV Parser - Main orchestrator class (modular version)
"""
import json
import os
import sys
from typing import Dict, List, Optional

# Add transformation directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'transformation'))

# Import modular components
from .csv_reader import CSVReader
from .data_range_detector import DataRangeDetector
from .legacy_transformer import LegacyTransformer

try:
    from universal_transformer import UniversalTransformer
    UNIVERSAL_TRANSFORMER_AVAILABLE = True
    print("✅ Universal Transformer imported successfully in enhanced_csv_parser")
except ImportError as e:
    print(f"❌ Universal Transformer import failed: {e}")
    UNIVERSAL_TRANSFORMER_AVAILABLE = False

class EnhancedCSVParser:
    """Main orchestrator for CSV parsing with modular architecture"""
    
    def __init__(self):
        self.target_columns = ['Date', 'Amount', 'Category', 'Title', 'Note', 'Account']
        
        # Initialize modular components
        self.csv_reader = CSVReader()
        self.data_range_detector = DataRangeDetector()
        self.legacy_transformer = LegacyTransformer()
        
        # Initialize Universal Transformer
        if UNIVERSAL_TRANSFORMER_AVAILABLE:
            try:
                self.universal_transformer = UniversalTransformer()
                print("✅ Universal Transformer initialized in enhanced_csv_parser")
            except Exception as e:
                print(f"❌ Universal Transformer initialization failed: {e}")
                self.universal_transformer = None
        else:
            print("⚠️  Universal Transformer not available, using legacy transformation")
            self.universal_transformer = None
    
    def preview_csv(self, file_path: str, encoding: str = 'utf-8') -> Dict:
        """Preview CSV file and return basic info using robust CSV reading"""
        return self.csv_reader.preview_csv(file_path, encoding)
    
    def detect_data_range(self, file_path: str, encoding: str = 'utf-8') -> Dict:
        """Auto-detect where the actual transaction data starts"""
        try:
            lines = self.csv_reader.read_csv_lines(file_path, encoding)
            return self.data_range_detector.detect_data_range(lines)
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def parse_with_range(self, file_path: str, start_row: int, end_row: Optional[int] = None, 
                        start_col: int = 0, end_col: Optional[int] = None, 
                        encoding: str = 'utf-8') -> Dict:
        """Parse CSV with specified range using modular CSV reader"""
        return self.csv_reader.parse_with_range(file_path, start_row, end_row, start_col, end_col, encoding)
    
    def transform_to_cashew(self, data: List[Dict], column_mapping: Dict[str, str], 
                           bank_name: str = "", categorization_rules: List[Dict] = None,
                           default_category_rules: Dict = None, account_mapping: Dict = None,
                           bank_rules_settings: Dict[str, bool] = None) -> List[Dict]:
        """Transform parsed data to Cashew format with smart categorization"""
        
        # Use Universal Transformer if available
        if self.universal_transformer:
            print(f"\n🌟 USING UNIVERSAL TRANSFORMER")
            return self.universal_transformer.transform_to_cashew(
                data, column_mapping, bank_name, account_mapping, bank_rules_settings
            )
        
        # Fallback to legacy transformation
        return self.legacy_transformer.transform_to_cashew(
            data, column_mapping, bank_name, categorization_rules, 
            default_category_rules, account_mapping, bank_rules_settings
        )
    
    def save_template(self, template_name: str, config: Dict, template_dir: str = "templates"):
        """Save parsing template for reuse"""
        template_path = f"{template_dir}/{template_name}.json"
        with open(template_path, 'w') as f:
            json.dump(config, f, indent=2)
        return template_path
    
    def load_template(self, template_name: str, template_dir: str = "templates"):
        """Load saved parsing template"""
        template_path = f"{template_dir}/{template_name}.json"
        with open(template_path, 'r') as f:
            return json.load(f)
