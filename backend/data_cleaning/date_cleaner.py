"""
Date Data Cleaner
Handles parsing and standardization of date columns
"""

from typing import List, Dict, Any
from datetime import datetime
import re

class DateCleaner:
    """
    Cleans and standardizes date columns
    Handles various date formats and converts to ISO standard
    """
    
    def __init__(self):
        self.date_keywords = ['date', 'timestamp', 'created_at', 'processed_at']
        self.date_formats = [
            '%d %b %Y %I:%M %p',    # 02 Feb 2025 11:17 PM
            '%d %b %Y',             # 02 Feb 2025
            '%Y-%m-%d',             # 2025-02-03
            '%d/%m/%Y',             # 02/03/2025
            '%m/%d/%Y',             # 03/02/2025
            '%d-%m-%Y',             # 02-03-2025
            '%m-%d-%y',             # 05-30-25 (MM-DD-YY)
            '%d-%m-%y',             # 02-03-25 (DD-MM-YY)
            '%y-%m-%d',             # 25-03-02 (YY-MM-DD)
            '%Y-%m-%d %H:%M:%S',    # 2025-02-03 23:17:00
        ]
    
    def clean_date_columns(self, data: List[Dict]) -> List[Dict]:
        """
        Clean and standardize date columns
        
        Args:
            data: List of dictionaries with potentially dirty date data
            
        Returns:
            List[Dict]: Data with cleaned date values
        """
        print(f"   📅 Step 5: Cleaning date columns")
        
        if not data:
            return []
        
        # Identify date columns
        date_cols = self._identify_date_columns(data)
        print(f"      📋 Date columns found: {date_cols}")
        
        cleaned_data = []
        for row_idx, row in enumerate(data):
            cleaned_row = {}
            for col, value in row.items():
                if col in date_cols:
                    cleaned_value = self.parse_date_value(value)
                    cleaned_row[col] = cleaned_value
                    
                    # Debug first few rows
                    if row_idx < 3:
                        print(f"      📆 Row {row_idx} {col}: '{value}' → '{cleaned_value}'")
                else:
                    cleaned_row[col] = value
            
            cleaned_data.append(cleaned_row)
        
        print(f"      ✅ Date cleaning complete")
        return cleaned_data
    
    def _identify_date_columns(self, data: List[Dict]) -> List[str]:
        """
        Identify which columns contain date data
        
        Args:
            data: Sample data to analyze
            
        Returns:
            List[str]: Column names that contain date data
        """
        if not data:
            return []
        
        sample_row = data[0]
        date_cols = []
        
        for col, value in sample_row.items():
            if (self._is_date_column_name(col.lower()) or 
                self._looks_like_date(str(value)) or
                col.lower() in ['date']):  # Ensure Date is always cleaned
                date_cols.append(col)
        
        return date_cols
    
    def _is_date_column_name(self, col_name: str) -> bool:
        """Check if column name indicates date data"""
        return any(keyword in col_name for keyword in self.date_keywords)
    
    def _looks_like_date(self, value: str) -> bool:
        """Check if value looks like a date"""
        if not value or not str(value).strip():
            return False
        
        value_str = str(value).strip()
        
        # Common date patterns
        date_patterns = [
            r'\d{1,2}\s+\w{3}\s+\d{4}',     # 02 Feb 2025
            r'\d{1,2}/\d{1,2}/\d{4}',       # 02/03/2025
            r'\d{4}-\d{1,2}-\d{1,2}',       # 2025-02-03
            r'\d{1,2}-\d{1,2}-\d{4}',       # 02-03-2025
            r'\d{1,2}-\d{1,2}-\d{2}'        # 02-03-25
        ]
        
        return any(re.search(pattern, value_str) for pattern in date_patterns)
    
    def parse_date_value(self, value: Any) -> str:
        """
        Parse and standardize date value to ISO format
        
        Args:
            value: Raw date value (string, datetime, etc.)
            
        Returns:
            str: Standardized date in YYYY-MM-DD format
        """
        try:
            if value is None or str(value).strip() == '':
                return ''
            
            value_str = str(value).strip()
            
            # Try parsing with common date formats
            for fmt in self.date_formats:
                try:
                    dt = datetime.strptime(value_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # If no format matches, return original
            return value_str
            
        except Exception as e:
            print(f"      ⚠️  Could not parse date value: '{value}' - {e}")
            return str(value) if value else ''
    
    def add_custom_date_format(self, date_format: str):
        """
        Add a custom date format to the parser
        
        Args:
            date_format: Python strptime format string
        """
        if date_format not in self.date_formats:
            self.date_formats.append(date_format)
            print(f"      ➕ Added custom date format: {date_format}")
