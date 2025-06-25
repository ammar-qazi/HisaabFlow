"""
Column Standardizer
Handles column name standardization and mapping for consistent data structure
"""

from typing import List, Dict, Tuple

class ColumnStandardizer:
    """
    Standardizes column names for consistent data processing
    Creates mapping between original and standardized column names
    """
    
    def __init__(self):
        self.common_mappings = {
            'TIMESTAMP': 'Date',
            'TYPE': 'Note', 
            'DESCRIPTION': 'Title',
            'AMOUNT': 'Amount',
            'BALANCE': 'Balance',
            'CURRENCY': 'Currency',
            'Total amount': 'Amount',
            'Running balance': 'Balance'
        }
    
    def standardize_columns(self, data: List[Dict], template_config: Dict = None) -> Tuple[List[Dict], Dict[str, str]]:
        """
        Standardize column names for consistency
        
        Args:
            data: List of dictionaries with original column names
            template_config: Template configuration with column mapping
            
        Returns:
            Tuple: (standardized_data, column_name_mapping)
        """
        print(f"    Step 2: Standardizing column names")
        
        if not data:
            return [], {}
        
        # Create column mapping for standardization
        column_mapping = self._create_column_mapping(data, template_config)
        
        print(f"       Column name mapping: {column_mapping}")
        
        # Apply column renaming
        standardized_data = self._apply_column_mapping(data, column_mapping)
        
        print(f"      [SUCCESS] Standardized columns: {list(standardized_data[0].keys()) if standardized_data else []}")
        return standardized_data, column_mapping
    
    def _create_column_mapping(self, data: List[Dict], template_config: Dict = None) -> Dict[str, str]:
        """
        Create mapping from original to standardized column names
        
        Args:
            data: Sample data to analyze columns
            template_config: Template configuration for semantic mappings
            
        Returns:
            Dict[str, str]: Mapping from original to standardized names
        """
        column_mapping = {}
        
        # Use template mapping if available to maintain semantic meaning
        if template_config and 'column_mapping' in template_config:
            template_mapping = template_config['column_mapping']
            for target_semantic, source_col in template_mapping.items():
                if source_col and target_semantic:
                    # Map to semantic names (Date, Amount, etc.) instead of lowercase
                    column_mapping[source_col] = target_semantic
        
        # Add common standardizations for unmapped columns
        # Apply common mappings only if not already mapped by template
        for old_col, new_col in self.common_mappings.items():
            if old_col not in column_mapping:
                column_mapping[old_col] = new_col
        
        # For any remaining columns, use title case
        if data:
            sample_row = data[0]
            for col in sample_row.keys():
                if col not in column_mapping:
                    # Convert to title case for unmapped columns
                    standardized_name = col.replace('_', ' ').title().replace(' ', '')
                    column_mapping[col] = standardized_name
        
        return column_mapping
    
    def _apply_column_mapping(self, data: List[Dict], column_mapping: Dict[str, str]) -> List[Dict]:
        """
        Apply column name mapping to data
        
        Args:
            data: Original data with old column names
            column_mapping: Mapping from old to new column names
            
        Returns:
            List[Dict]: Data with standardized column names
        """
        standardized_data = []
        for row in data:
            new_row = {}
            for old_col, value in row.items():
                new_col = column_mapping.get(old_col, old_col)
                new_row[new_col] = value
            standardized_data.append(new_row)
        
        return standardized_data
    
    def create_cashew_mapping(self, template_config: Dict = None, column_name_mapping: Dict = None) -> Dict[str, str]:
        """
        Create mapping for Cashew transformation format
        Maps Cashew target columns to cleaned column names
        
        Args:
            template_config: Original template configuration
            column_name_mapping: Mapping from original to standardized names
            
        Returns:
            Dict[str, str]: Mapping for Cashew transformation
        """
        print(f"    Creating Cashew column mapping")
        
        # Start with template mapping if available
        original_mapping = {}
        if template_config and 'column_mapping' in template_config:
            original_mapping = template_config['column_mapping']
        
        # Create updated mapping
        updated_mapping = {}
        
        # Map each Cashew target column to the corresponding cleaned column
        for cashew_col, original_source_col in original_mapping.items():
            if original_source_col and column_name_mapping:
                # Find the cleaned column name
                cleaned_col = column_name_mapping.get(original_source_col, original_source_col)
                updated_mapping[cashew_col] = cleaned_col
            elif original_source_col:
                updated_mapping[cashew_col] = original_source_col
        
        # Ensure we have the essential mappings
        essential_mappings = {
            'Date': 'Date',
            'Amount': 'Amount', 
            'Title': 'Title',
            'Note': 'Note',
            'Category': '',  # Will be set during categorization
            'Account': ''    # Will be set to bank name
        }
        
        for cashew_col, default_col in essential_mappings.items():
            if cashew_col not in updated_mapping:
                updated_mapping[cashew_col] = default_col
        
        print(f"      [SUCCESS] Cashew mapping created: {updated_mapping}")
        return updated_mapping
