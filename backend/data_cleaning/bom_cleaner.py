"""
BOM (Byte Order Mark) Character Cleaner
Handles BOM character issues in CSV data

RECOMMENDED APPROACH: Use utf-8-sig encoding when reading CSV files
This module provides fallback cleanup for cases where proper encoding wasn't used
"""

from typing import List, Dict

class BOMCleaner:
    """
    Handles BOM character cleanup in CSV data
    
    BEST PRACTICE: Use pandas.read_csv(file, encoding='utf-8-sig') 
    This eliminates BOM issues at the source rather than post-processing
    """
    
    def clean_bom_from_data(self, data: List[Dict]) -> List[Dict]:
        """
        Remove BOM characters from column names in data
        
        Args:
            data: List of dictionaries with potentially BOM-affected column names
            
        Returns:
            List[Dict]: Data with clean column names
            
        Note:
            This is a fallback method. Better approach is using utf-8-sig encoding
            when reading the CSV file: pd.read_csv(file, encoding='utf-8-sig')
        """
        if not data:
            return []
        
        # Check first row for BOM characters
        if not self.has_bom_characters(data):
            print(f"      [SUCCESS] No BOM characters detected, skipping BOM cleanup")
            return data
        
        print(f"      🧹 BOM characters detected, cleaning column names...")
        print(f"       RECOMMENDATION: Use utf-8-sig encoding when reading CSV files")
        
        # Strip BOM from all column names
        cleaned_data = []
        for row in data:
            cleaned_row = {}
            for col, value in row.items():
                # Remove BOM character (\ufeff) from column name
                clean_col = str(col).replace('\ufeff', '').strip()
                cleaned_row[clean_col] = value
                
                # Debug first few BOM cleanups
                if len(cleaned_data) < 3 and clean_col != str(col):
                    print(f"       BOM cleanup: '{col}' → '{clean_col}'")
            
            cleaned_data.append(cleaned_row)
        
        print(f"      [SUCCESS] BOM cleanup complete: {len(cleaned_data)} rows processed")
        return cleaned_data
    
    def has_bom_characters(self, data: List[Dict]) -> bool:
        """
        Check if data contains BOM characters in column names
        
        Args:
            data: List of dictionaries to check
            
        Returns:
            bool: True if BOM characters found
        """
        if not data:
            return False
        
        sample_row = data[0]
        return any('\ufeff' in str(col) for col in sample_row.keys())
    
    @staticmethod
    def get_encoding_recommendation() -> str:
        """
        Get the recommended encoding for reading CSV files
        
        Returns:
            str: Recommended encoding string for pandas.read_csv()
        """
        return 'utf-8-sig'
    
    @staticmethod
    def get_pandas_read_example() -> str:
        """
        Get example code for proper CSV reading with BOM handling
        
        Returns:
            str: Example pandas.read_csv() code
        """
        return """
# RECOMMENDED: Use utf-8-sig encoding to handle BOM at source
import pandas as pd

df = pd.read_csv('file.csv', encoding='utf-8-sig')
# This automatically handles BOM characters without post-processing
"""
