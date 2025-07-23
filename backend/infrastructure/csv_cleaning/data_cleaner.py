"""
Modular Data Cleaner
Main orchestration class for data cleaning pipeline
Coordinates all cleaning modules for comprehensive data processing
"""

from typing import Dict, List, Optional
from backend.shared.amount_formats import AmountFormat
try:
    # Package imports (when used as module)
    from .bom_cleaner import BOMCleaner
    from .column_standardizer import ColumnStandardizer
    from .numeric_cleaner import NumericCleaner
    from .date_cleaner import DateCleaner
    from .currency_handler import CurrencyHandler
    from .data_validator import DataValidator
    from .quality_checker import QualityChecker
except ImportError:
    # Direct imports (when running as script)
    from bom_cleaner import BOMCleaner
    from column_standardizer import ColumnStandardizer
    from numeric_cleaner import NumericCleaner
    from date_cleaner import DateCleaner
    from currency_handler import CurrencyHandler
    from data_validator import DataValidator
    from quality_checker import QualityChecker

class DataCleaner:
    """
    Main data cleaning orchestrator
    Coordinates modular cleaning pipeline for uniform, clean data structure
    """
    
    def __init__(self, amount_format: Optional[AmountFormat] = None):
        # Initialize all cleaning modules
        self.bom_cleaner = BOMCleaner()
        self.column_standardizer = ColumnStandardizer()
        self.numeric_cleaner = NumericCleaner(amount_format=amount_format)
        self.date_cleaner = DateCleaner()
        self.currency_handler = CurrencyHandler()
        self.data_validator = DataValidator()
        self.quality_checker = QualityChecker()
    
    def clean_parsed_data(self, parsed_data: Dict, template_config: Dict = None) -> Dict:
        """
        Main cleaning function - transforms raw parsed data into clean, uniform structure
        
        Args:
            parsed_data: Raw data from CSV parser
            template_config: Template configuration for cleaning hints
            
        Returns:
            Dict with cleaned data structure including updated column mapping
        """
        try:
            print(f"\n STARTING DATA CLEANING")
            print(f"   [DATA] Input: {parsed_data.get('row_count', 0)} rows")
            
            if not parsed_data.get('success', False) or not parsed_data.get('data'):
                return {
                    'success': False,
                    'error': 'Invalid input data for cleaning'
                }
            
            # Step 1: Focus on target data only (remove unwanted rows/columns)
            focused_data = self._focus_target_data(
                parsed_data['data'], 
                parsed_data.get('headers', []),
                template_config
            )
            
            # Step 2: Clean BOM characters from column names (IMPROVED - should use proper encoding)
            bom_cleaned_data = self.bom_cleaner.clean_bom_from_data(focused_data)
            
            # Step 3: Clean and standardize column names
            standardized_data, column_name_mapping = self.column_standardizer.standardize_columns(
                bom_cleaned_data, template_config
            )
            
            # Step 4: Add currency column if missing
            currency_added_data = self.currency_handler.add_currency_column(
                standardized_data, template_config
            )
            
            # Step 5: Clean numeric columns (amounts, balances, etc.)
            numeric_cleaned_data = self.numeric_cleaner.clean_numeric_columns(currency_added_data)
            
            # Step 6: Clean date columns
            date_cleaned_data = self.date_cleaner.clean_date_columns(numeric_cleaned_data)
            
            # Step 7: Remove empty/invalid rows
            valid_data = self.data_validator.remove_invalid_rows(date_cleaned_data)
            
            # Step 8: Create updated column mapping for transformation
            updated_column_mapping = self.column_standardizer.create_cashew_mapping(
                template_config, column_name_mapping
            )
            
            # Step 9: Quality assessment
            quality_report = self.quality_checker.check_data_quality(valid_data)
            
            print(f"   [SUCCESS] Cleaning complete: {len(valid_data)} clean rows")
            print(f"    Updated column mapping: {updated_column_mapping}")
            
            return {
                'success': True,
                'data': valid_data,
                'row_count': len(valid_data),
                'updated_column_mapping': updated_column_mapping,
                'quality_report': quality_report,
                'cleaning_summary': {
                    'original_rows': parsed_data.get('row_count', 0),
                    'final_rows': len(valid_data),
                    'rows_removed': parsed_data.get('row_count', 0) - len(valid_data),
                    'numeric_columns_cleaned': self._count_numeric_columns(valid_data),
                    'date_columns_cleaned': self._count_date_columns(valid_data),
                    'currency_column_added': 'Currency' in valid_data[0] if valid_data else False,
                    'quality_grade': quality_report.get('completeness', {}).get('grade', 'Unknown')
                }
            }
            
        except Exception as e:
            print(f"   [ERROR]  Cleaning error: {str(e)}")
            import traceback
            print(f"    Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': f'Data cleaning failed: {str(e)}'
            }
    
    def _focus_target_data(self, data: List[Dict], headers: List[str], template_config: Dict = None) -> List[Dict]:
        """
        Step 1: Focus on target data only - remove unwanted columns and rows
        """
        print(f"   Step 1: Focusing target data")
        
        if not data:
            return []
        
        # Get column mapping from template if available
        column_mapping = {}
        if template_config and 'column_mapping' in template_config:
            column_mapping = template_config['column_mapping']
        
        # Check if this is an unknown bank
        is_unknown_bank = template_config and template_config.get('bank_name') == 'unknown'
        
        # Identify target columns (mapped columns + common transaction columns)
        target_columns = set()
        
        # Add columns from mapping
        for source_col in column_mapping.values():
            if source_col:  # Skip empty mappings
                target_columns.add(source_col)
        
        # Enhanced multilingual pattern matching for transaction columns
        transaction_patterns = {
            # English patterns
            'date': ['timestamp', 'date', 'created', 'processed', 'transaction_date', 'booking_date'],
            'amount': ['amount', 'value', 'sum', 'total', 'debit', 'credit'],
            'balance': ['balance', 'saldo', 'remaining', 'available'],
            'description': ['description', 'memo', 'note', 'reference', 'details', 'narrative'],
            'currency': ['currency', 'curr', 'ccy'],
            'type': ['type', 'category', 'kind'],
            'account': ['account', 'iban', 'bban'],
            'counterparty': ['counterparty', 'partner', 'recipient', 'sender', 'naam'],
            
            # Multilingual patterns (Dutch, German, French, etc.)
            'date_intl': ['datum', 'date', 'fecha', 'data', 'rentedatum'],
            'amount_intl': ['bedrag', 'betrag', 'montant', 'importo', 'valor'],
            'balance_intl': ['saldo', 'solde', 'bilanz', 'balance'],
            'description_intl': ['omschrijving', 'beschreibung', 'description', 'descrizione'],
            'currency_intl': ['munt', 'währung', 'monnaie', 'valuta'],
            'reference_intl': ['referentie', 'referenz', 'référence', 'riferimento', 'transactiereferentie'],
        }
        
        # Flatten all patterns for matching
        all_patterns = []
        for pattern_list in transaction_patterns.values():
            all_patterns.extend(pattern_list)
        
        # Find columns that match transaction patterns
        for col in headers:
            col_lower = col.lower().replace(' ', '').replace('-', '').replace('_', '')
            col_original_lower = col.lower()
            
            # Check for exact matches or partial matches
            for pattern in all_patterns:
                pattern_clean = pattern.replace(' ', '').replace('-', '').replace('_', '')
                if (pattern_clean in col_lower or 
                    pattern in col_original_lower or
                    col_lower.startswith(pattern_clean) or
                    col_lower.endswith(pattern_clean)):
                    target_columns.add(col)
                    break
        
        # For unknown banks, be more inclusive - if we found very few columns, keep all
        if is_unknown_bank and len(target_columns) < 3:
            print(f"       Unknown bank with few matching columns ({len(target_columns)}), keeping all columns")
            target_columns = set(headers)
        
        # If no specific targets found at all, keep all columns
        if not target_columns:
            target_columns = set(headers)
        
        print(f"       Target columns: {sorted(target_columns)}")
        
        # Filter data to only include target columns
        focused_data = []
        for row in data:
            focused_row = {}
            for col in target_columns:
                if col in row:
                    focused_row[col] = row[col]
            
            # Only include rows that have at least some meaningful data
            if any(str(value).strip() for value in focused_row.values()):
                focused_data.append(focused_row)
        
        print(f"      [SUCCESS] Focused data: {len(focused_data)} rows, {len(target_columns)} columns")
        return focused_data
    
    def _count_numeric_columns(self, data: List[Dict]) -> int:
        """Count numeric columns in cleaned data"""
        if not data:
            return 0
        
        numeric_keywords = ['amount', 'balance', 'exchange_amount', 'fee', 'total']
        sample_row = data[0]
        return len([col for col in sample_row.keys() 
                   if any(keyword in col.lower() for keyword in numeric_keywords)])
    
    def _count_date_columns(self, data: List[Dict]) -> int:
        """Count date columns in cleaned data"""
        if not data:
            return 0
        
        date_keywords = ['date', 'timestamp', 'created_at', 'processed_at']
        sample_row = data[0]
        return len([col for col in sample_row.keys() 
                   if any(keyword in col.lower() for keyword in date_keywords)])


# Test the modular data cleaner
if __name__ == "__main__":
    cleaner = DataCleaner()
    
    # Test with sample NayaPay-like data
    sample_parsed_data = {
        'success': True,
        'headers': ['TIMESTAMP', 'TYPE', 'DESCRIPTION', 'AMOUNT', 'BALANCE'],
        'data': [
            {
                'TIMESTAMP': '02 Feb 2025 11:17 PM',
                'TYPE': 'Raast Out',
                'DESCRIPTION': 'Transfer to Someone',
                'AMOUNT': '-5,000',
                'BALANCE': '872.40'
            },
            {
                'TIMESTAMP': '03 Feb 2025 12:15 PM',
                'TYPE': 'IBFT In',
                'DESCRIPTION': 'Transfer from Someone',
                'AMOUNT': '+50,000',
                'BALANCE': '50,872.40'
            }
        ],
        'row_count': 2
    }
    
    # Test with sample template config for NayaPay
    template_config = {
        'column_mapping': {
            'Date': 'TIMESTAMP',
            'Amount': 'AMOUNT',
            'Title': 'DESCRIPTION',
            'Note': 'TYPE'
        },
        'bank_name': 'NayaPay'
    }
    
    print("🧪 Testing Modular Data Cleaner")
    result = cleaner.clean_parsed_data(sample_parsed_data, template_config)
    
    print(f"\n[DATA] Cleaning Result:")
    import json
    print(json.dumps(result, indent=2, default=str))
