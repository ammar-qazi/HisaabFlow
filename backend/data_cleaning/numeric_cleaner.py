"""
Numeric Data Cleaner
Handles parsing and cleaning of numeric columns (amounts, balances, etc.)
"""

from typing import List, Dict, Any
import re

class NumericCleaner:
    """
    Cleans and standardizes numeric data columns
    Handles currency symbols, formatting, and type conversion
    """
    
    def __init__(self):
        self.numeric_keywords = ['amount', 'balance', 'exchange_amount', 'fee', 'total']
    
    def clean_numeric_columns(self, data: List[Dict]) -> List[Dict]:
        """
        Clean numeric columns - convert to float, handle formatting
        
        Args:
            data: List of dictionaries with potentially dirty numeric data
            
        Returns:
            List[Dict]: Data with cleaned numeric values
        """
        print(f"   💰 Step 4: Cleaning numeric columns")
        
        if not data:
            return []
        
        # Identify numeric columns
        numeric_cols = self._identify_numeric_columns(data)
        print(f"      📊 Numeric columns found: {numeric_cols}")
        
        cleaned_data = []
        for row_idx, row in enumerate(data):
            cleaned_row = {}
            for col, value in row.items():
                if col in numeric_cols:
                    cleaned_value = self.parse_numeric_value(value)
                    cleaned_row[col] = cleaned_value
                    
                    # Debug first few rows
                    if row_idx < 3:
                        print(f"      💱 Row {row_idx} {col}: '{value}' → {cleaned_value}")
                else:
                    cleaned_row[col] = value
            
            cleaned_data.append(cleaned_row)
        
        print(f"      ✅ Numeric cleaning complete")
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
            print(f"      ⚠️  Could not parse numeric value: '{value}'")
            return 0.0
