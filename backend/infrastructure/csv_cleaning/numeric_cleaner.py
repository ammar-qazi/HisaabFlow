"""
Numeric Data Cleaner
Handles parsing and cleaning of numeric columns (amounts, balances, etc.)
Enhanced with AmountFormat support for different regional number formats.
"""

from typing import List, Dict, Any, Optional, Tuple
import re
from ...shared.amount_formats import AmountFormat, RegionalFormatRegistry, AmountFormatDetector, FormatValidator

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
        
        print(f"    [INIT] NumericCleaner initialized with format: {self.amount_format.name or 'Custom'}")
        print(f"           Decimal: '{self.amount_format.decimal_separator}', Thousand: '{self.amount_format.thousand_separator}'")
    
    def auto_detect_and_clean(self, data: List[Dict]) -> Tuple[List[Dict], AmountFormat]:
        """
        Auto-detect amount format from data and clean with detected format.
        
        Args:
            data: List of dictionaries with potentially dirty numeric data
            
        Returns:
            Tuple of (cleaned_data, detected_format)
        """
        print(f"    Step 4a: Auto-detecting amount format from data")
        
        if not data:
            return [], self.amount_format
        
        # Extract amount samples for format detection
        amount_samples = self._extract_amount_samples(data)
        print(f"      [DATA] Found {len(amount_samples)} amount samples for analysis")
        
        if amount_samples:
            # Detect format from samples
            detected_format, confidence = self.format_detector.detect_format(amount_samples)
            print(f"      [DETECTED] Format: {detected_format.name or 'Custom'} (confidence: {confidence:.2f})")
            print(f"                 Decimal: '{detected_format.decimal_separator}', Thousand: '{detected_format.thousand_separator}'")
            
            # Update our format if confidence is high enough
            if confidence > 0.6:
                self.amount_format = detected_format
                print(f"      [UPDATE] Using detected format for cleaning")
            else:
                print(f"      [FALLBACK] Low confidence, using default format: {self.amount_format.name or 'Custom'}")
        else:
            detected_format = self.amount_format
            print(f"      [FALLBACK] No amount samples found, using default format")
        
        # Clean with the determined format
        cleaned_data = self.clean_numeric_columns(data)
        return cleaned_data, detected_format
    
    def clean_numeric_columns(self, data: List[Dict]) -> List[Dict]:
        """
        Clean numeric columns using configured AmountFormat.
        
        Args:
            data: List of dictionaries with potentially dirty numeric data
            
        Returns:
            List[Dict]: Data with cleaned numeric values
        """
        print(f"    Step 4: Cleaning numeric columns with format: {self.amount_format.name or 'Custom'}")
        
        if not data:
            return []
        
        # Identify numeric columns
        numeric_cols = self._identify_numeric_columns(data)
        print(f"      [DATA] Numeric columns found: {numeric_cols}")
        
        cleaned_data = []
        for row_idx, row in enumerate(data):
            cleaned_row = {}
            for col, value in row.items():
                if col in numeric_cols:
                    cleaned_value = self.parse_numeric_value_with_format(value, self.amount_format)
                    cleaned_row[col] = cleaned_value
                    
                    # Debug first few rows
                    if row_idx < 3:
                        print(f"       Row {row_idx} {col}: '{value}' → {cleaned_value}")
                else:
                    cleaned_row[col] = value
            
            cleaned_data.append(cleaned_row)
        
        print(f"      [SUCCESS] Numeric cleaning complete")
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
        
        sample_row = data[0]
        numeric_cols = []
        
        for col, value in sample_row.items():
            if (self._is_numeric_column_name(col.lower()) or 
                self._looks_like_number(str(value)) or
                col.lower() in ['amount', 'balance']):  # Ensure Amount and Balance are always cleaned
                numeric_cols.append(col)
        
        return numeric_cols
    
    def _is_numeric_column_name(self, col_name: str) -> bool:
        """Check if column name indicates numeric data"""
        return any(keyword in col_name for keyword in self.numeric_keywords)
    
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
    
    def _extract_amount_samples(self, data: List[Dict]) -> List[str]:
        """
        Extract amount-like values from data for format detection.
        
        Args:
            data: List of dictionaries to extract samples from
            
        Returns:
            List of amount strings for analysis
        """
        samples = []
        amount_columns = ['amount', 'balance', 'exchange_amount', 'fee', 'total']
        
        # Look for amount columns
        if not data:
            return samples
        
        sample_row = data[0]
        found_amount_cols = []
        for col in sample_row.keys():
            if any(keyword in col.lower() for keyword in amount_columns):
                found_amount_cols.append(col)
        
        # Extract samples from amount columns
        max_samples = min(20, len(data))  # Limit sample size for performance
        for i in range(max_samples):
            if i >= len(data):
                break
            row = data[i]
            for col in found_amount_cols:
                value = row.get(col)
                if value and str(value).strip():
                    samples.append(str(value).strip())
        
        return samples
    
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
        print(f"      [FALLBACK] Format-aware parsing failed for '{value}', using legacy method")
        return self.parse_numeric_value(value)
    
    def parse_numeric_value(self, value: Any) -> float:
        """
        Parse and clean numeric value to float
        
        Args:
            value: Raw numeric value (string, int, float, etc.)
            
        Returns:
            float: Cleaned numeric value
        """
        try:
            if value is None or str(value).strip() == '':
                return 0.0
            
            value_str = str(value).strip()
            
            # Handle empty strings
            if not value_str:
                return 0.0
            
            # Remove currency symbols and spaces
            cleaned = re.sub(r'[$€£¥₹PKR USD EUR GBP\s]', '', value_str)
            
            # Handle parentheses (negative numbers)
            is_negative_paren = cleaned.startswith('(') and cleaned.endswith(')')
            if is_negative_paren:
                cleaned = cleaned[1:-1]  # Remove parentheses
            
            # Remove commas
            cleaned = cleaned.replace(',', '')
            
            # Handle plus/minus signs
            is_negative_sign = cleaned.startswith('-')
            is_positive_sign = cleaned.startswith('+')
            
            if is_positive_sign:
                cleaned = cleaned[1:]
            
            # Parse the number
            if cleaned:
                number = float(cleaned)
                if is_negative_paren or is_negative_sign:
                    number = -abs(number)
                return number
            else:
                return 0.0
                
        except (ValueError, TypeError):
            print(f"      [WARNING]  Could not parse numeric value: '{value}'")
            return 0.0
