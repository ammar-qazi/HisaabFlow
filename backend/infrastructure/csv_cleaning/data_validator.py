"""
Data Validator
Handles validation and removal of invalid/incomplete rows
"""

from typing import List, Dict

class DataValidator:
    """
    Validates data quality and removes invalid rows
    Ensures only meaningful transaction data is preserved
    """
    
    def remove_invalid_rows(self, data: List[Dict]) -> List[Dict]:
        """
        Remove rows with invalid or missing critical data
        
        Args:
            data: List of dictionaries to validate
            
        Returns:
            List[Dict]: Data with invalid rows removed
        """
        print(f"    Step 6: Removing invalid rows")
        
        if not data:
            return []
        
        original_count = len(data)
        valid_data = []
        
        for row in data:
            if self._is_valid_row(row):
                valid_data.append(row)
        
        removed_count = original_count - len(valid_data)
        print(f"      [SUCCESS] Removed {removed_count} invalid rows, kept {len(valid_data)} valid rows")
        
        return valid_data
    
    def _is_valid_row(self, row: Dict) -> bool:
        """
        Check if a row contains valid transaction data
        
        Args:
            row: Dictionary representing a data row
            
        Returns:
            bool: True if row is valid
        """
        # Check if row has essential data
        has_amount = self._has_valid_amount(row)
        has_date = self._has_valid_date(row)
        
        # Keep row if it has either amount or date (some flexibility)
        return has_amount or has_date
    
    def _has_valid_amount(self, row: Dict) -> bool:
        """
        Check if row has a valid amount value
        
        Args:
            row: Data row to check
            
        Returns:
            bool: True if valid amount found
        """
        for col in row.keys():
            if 'amount' in col.lower():
                value = row[col]
                if (value is not None and 
                    str(value).strip() and 
                    str(value) != '0' and 
                    str(value) != '0.0'):
                    return True
        return False
    
    def _has_valid_date(self, row: Dict) -> bool:
        """
        Check if row has a valid date value
        
        Args:
            row: Data row to check
            
        Returns:
            bool: True if valid date found
        """
        for col in row.keys():
            if 'date' in col.lower():
                value = row[col]
                if value is not None and str(value).strip():
                    return True
        return False
    
    def validate_essential_columns(self, data: List[Dict], required_columns: List[str] = None) -> Dict[str, Dict]:
        """
        Validate that essential columns exist and have data
        
        Args:
            data: Data to validate
            required_columns: List of required column names
            
        Returns:
            Dict[str, Dict]: Validation results with counts
        """
        if not data:
            return {}
        
        if required_columns is None:
            required_columns = ['Date', 'Amount']
        
        results = {}
        for col in required_columns:
            if col in data[0]:
                empty_count = sum(1 for row in data if not row.get(col) or str(row.get(col)).strip() == '')
                results[col] = {
                    'total_rows': len(data),
                    'empty_rows': empty_count,
                    'valid_rows': len(data) - empty_count
                }
            else:
                results[col] = {
                    'total_rows': len(data),
                    'empty_rows': len(data),
                    'valid_rows': 0,
                    'column_missing': True
                }
        
        return results
    
    def get_data_completeness_score(self, data: List[Dict]) -> float:
        """
        Calculate data completeness score (0.0 to 1.0)
        
        Args:
            data: Data to analyze
            
        Returns:
            float: Completeness score
        """
        if not data:
            return 0.0
        
        essential_columns = ['Date', 'Amount', 'Title']
        total_cells = len(data) * len(essential_columns)
        filled_cells = 0
        
        for row in data:
            for col in essential_columns:
                if col in row and row[col] and str(row[col]).strip():
                    filled_cells += 1
        
        return filled_cells / total_cells if total_cells > 0 else 0.0
