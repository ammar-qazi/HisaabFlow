"""
Numeric Data Cleaner
Handles parsing and cleaning of numeric columns (amounts, balances, etc.)
Enhanced with AmountFormat support for different regional number formats.
"""

from typing import List, Dict, Any, Optional
import re
from ...shared.amount_formats import AmountFormat, RegionalFormatRegistry, AmountFormatDetector, FormatValidator
from ...shared.utils.amount_text import parse_amount_text
import logging

logger = logging.getLogger(__name__)

class NumericCleaner:
    """
    Cleans and standardizes numeric data columns with AmountFormat support.
    Handles currency symbols, formatting, and type conversion using configurable
    regional number formats (American, European, Space-separated, etc.).
    """
    
    def __init__(self, amount_format: Optional[AmountFormat] = None):
        self.numeric_keywords = ['amount', 'balance', 'debit', 'credit', 'exchange_amount', 'fee', 'total']
        self.amount_format = amount_format or RegionalFormatRegistry.AMERICAN
        self.format_detector = AmountFormatDetector()
        self.format_validator = FormatValidator()
        
        logger.debug(f"    [INIT] NumericCleaner initialized with format: {self.amount_format.name or 'Custom'}")
        logger.debug(f"           Decimal: '{self.amount_format.decimal_separator}', Thousand: '{self.amount_format.thousand_separator}'")
    
    def clean_numeric_columns(self, data: List[Dict]) -> List[Dict]:
        """
        Clean numeric columns using configured AmountFormat.
        
        Args:
            data: List of dictionaries with potentially dirty numeric data
            
        Returns:
            List[Dict]: Data with cleaned numeric values
        """
        logger.debug(f"    Step 4: Cleaning numeric columns with format: {self.amount_format.name or 'Custom'}")
        
        if not data:
            return []
        
        # Identify numeric columns
        numeric_cols = self._identify_numeric_columns(data)
        logger.debug(f"      [DATA] Numeric columns found: {numeric_cols}")
        
        cleaned_data = []
        for row_idx, row in enumerate(data):
            cleaned_row = {}
            for col, value in row.items():
                if col in numeric_cols:
                    cleaned_value = self.parse_numeric_value_with_format(value, self.amount_format)
                    cleaned_row[col] = cleaned_value
                    
                    # Debug first few rows
                    if row_idx < 3:
                        pass
                else:
                    cleaned_row[col] = value
            
            cleaned_data.append(cleaned_row)
        
        logger.debug(f"      [SUCCESS] Numeric cleaning complete")
        return cleaned_data
    
    def _identify_numeric_columns(self, data: List[Dict]) -> List[str]:
        """
        Identify which columns contain numeric data
        
        Args:
            data: Sample data to analyze
            
        Returns:
            List[str]: Column names that contain numeric data
        """
        if not data:
            return []
        
        # Use up to 10 sample rows for better accuracy
        sample_size = min(10, len(data))
        sample_rows = data[:sample_size]
        numeric_cols = []
        
        # Get all column names from first row
        all_columns = list(data[0].keys())
        
        for col in all_columns:
            col_lower = col.lower()
            
            # Skip columns that are clearly non-numeric (IBAN, account numbers, etc.)
            if self._is_non_numeric_column(col_lower):
                continue
            
            # Always include known amount/balance columns
            if col_lower in ['amount', 'balance'] or self._is_numeric_column_name(col_lower):
                numeric_cols.append(col)
                continue
            
            # Check if majority of sample values look like numbers
            numeric_count = 0
            total_count = 0
            
            for row in sample_rows:
                value = row.get(col)
                if value is not None and str(value).strip():  # Only count non-empty values
                    total_count += 1
                    if self._looks_like_number(str(value)):
                        numeric_count += 1
            
            # Consider it numeric if at least 70% of non-empty values look like numbers
            # and we have at least 2 samples to avoid false positives
            if total_count >= 2 and numeric_count / total_count >= 0.7:
                numeric_cols.append(col)
        
        return numeric_cols
    
    def _is_numeric_column_name(self, col_name: str) -> bool:
        """Check if column name indicates numeric data"""
        return any(keyword in col_name for keyword in self.numeric_keywords)
    
    def _is_non_numeric_column(self, col_name: str) -> bool:
        """Check if column name indicates non-numeric data (IBAN, account numbers, etc.)"""
        non_numeric_keywords = [
            'iban', 'bban', 'account', 'rekening', 'tegenrekening',
            'reference', 'referentie', 'transactiereferentie',
            'naam', 'name', 'partij', 'party', 'tegenpartij',
            'description', 'omschrijving', 'title', 'note',
            'date', 'datum', 'timestamp', 'tijd',
            'currency', 'munt', 'valuta'
        ]
        return any(keyword in col_name for keyword in non_numeric_keywords)
    
    def _looks_like_number(self, value: str) -> bool:
        """Check if value looks like a number"""
        if not value or not str(value).strip():
            return False
        
        value_str = str(value).strip()
        
        # Check for currency symbols, commas, parentheses, +/- signs
        numeric_patterns = [
            r'^[+-]?\$?[0-9,]+\.?[0-9]*$',  # $1,234.56 or -1,234
            r'^\([0-9,]+\.?[0-9]*\)$',      # (1,234.56) - negative in parentheses
            r'^[+-]?[0-9,]+$',              # 1,234 or +1,234
            r'^[+-]?[0-9]+\.?[0-9]*$'       # 1234.56
        ]
        
        return any(re.match(pattern, value_str) for pattern in numeric_patterns)
    
    def parse_numeric_value_with_format(self, value: Any, format_obj: AmountFormat) -> float:
        """
        Parse numeric value using specified AmountFormat.
        
        Args:
            value: Raw numeric value (string, int, float, etc.)
            format_obj: AmountFormat to use for parsing
            
        Returns:
            float: Cleaned numeric value
        """
        # Use the format validator's parsing method
        parsed = self.format_validator.parse_amount_with_format(str(value) if value is not None else "", format_obj)
        if parsed is not None:
            return parsed
        
        # Fallback to legacy parsing if format-aware parsing fails
        return self.parse_numeric_value(value)
    
    def parse_numeric_value(self, value: Any) -> float:
        """Parse loosely formatted amount text; unreadable or empty values become 0.0"""
        amount = parse_amount_text(value)
        return float(amount) if amount is not None else 0.0
