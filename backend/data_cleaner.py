import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import re
import csv

class DataCleaner:
    """
    Data Cleaning layer between parsing and transformation
    Ensures uniform, clean data structure before transformation
    """
    
    def __init__(self):
        self.numeric_columns = ['amount', 'balance', 'exchange_amount', 'fee', 'total']
        self.date_columns = ['date', 'timestamp', 'created_at', 'processed_at']
        
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
            print(f"\n🧹 STARTING DATA CLEANING")
            print(f"   📊 Input: {parsed_data.get('row_count', 0)} rows")
            
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
            
            # Step 2: Clean and standardize column names
            standardized_data, column_name_mapping = self._standardize_columns(focused_data, template_config)
            
            # Step 3: Add currency column if missing (NEW)
            currency_added_data = self._add_currency_column(standardized_data, template_config)
            
            # Step 4: Clean numeric columns (amounts, balances, etc.)
            numeric_cleaned_data = self._clean_numeric_columns(currency_added_data)
            
            # Step 5: Clean date columns
            date_cleaned_data = self._clean_date_columns(numeric_cleaned_data)
            
            # Step 6: Remove empty/invalid rows
            final_data = self._remove_invalid_rows(date_cleaned_data)
            
            # Step 7: Create updated column mapping for transformation (NEW)
            updated_column_mapping = self._create_updated_column_mapping(template_config, column_name_mapping)
            
            print(f"   ✅ Cleaning complete: {len(final_data)} clean rows")
            print(f"   🗺️ Updated column mapping: {updated_column_mapping}")
            
            return {
                'success': True,
                'data': final_data,
                'row_count': len(final_data),
                'updated_column_mapping': updated_column_mapping,  # NEW: For transformation
                'cleaning_summary': {
                    'original_rows': parsed_data.get('row_count', 0),
                    'final_rows': len(final_data),
                    'rows_removed': parsed_data.get('row_count', 0) - len(final_data),
                    'numeric_columns_cleaned': len([col for col in final_data[0].keys() if self._is_numeric_column(col)]) if final_data else 0,
                    'date_columns_cleaned': len([col for col in final_data[0].keys() if self._is_date_column(col)]) if final_data else 0,
                    'currency_column_added': 'currency' in final_data[0] if final_data else False
                }
            }
            
        except Exception as e:
            print(f"   ❌ Cleaning error: {str(e)}")
            import traceback
            print(f"   📚 Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': f'Data cleaning failed: {str(e)}'
            }
    
    def _focus_target_data(self, data: List[Dict], headers: List[str], template_config: Dict = None) -> List[Dict]:
        """
        Step 1: Focus on target data only - remove unwanted columns and rows
        """
        print(f"   🎯 Step 1: Focusing target data")
        
        if not data:
            return []
        
        # Get column mapping from template if available
        column_mapping = {}
        if template_config and 'column_mapping' in template_config:
            column_mapping = template_config['column_mapping']
        
        # Identify target columns (mapped columns + common transaction columns)
        target_columns = set()
        
        # Add columns from mapping
        for source_col in column_mapping.values():
            if source_col:  # Skip empty mappings
                target_columns.add(source_col)
        
        # Add common transaction columns (case-insensitive)
        common_columns = ['timestamp', 'date', 'type', 'description', 'amount', 'balance', 
                         'currency', 'exchange_amount', 'exchange_currency', 'fee', 'id', 'reference']
        
        for col in headers:
            col_lower = col.lower()
            if any(common in col_lower for common in common_columns):
                target_columns.add(col)
        
        # If no specific targets found, keep all columns
        if not target_columns:
            target_columns = set(headers)
        
        print(f"      📋 Target columns: {sorted(target_columns)}")
        
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
        
        print(f"      ✅ Focused data: {len(focused_data)} rows, {len(target_columns)} columns")
        return focused_data
    
    def _standardize_columns(self, data: List[Dict], template_config: Dict = None) -> Tuple[List[Dict], Dict[str, str]]:
        """
        Step 2: Standardize column names for consistency
        Returns: (standardized_data, column_name_mapping)
        """
        print(f"   📝 Step 2: Standardizing column names")
        
        if not data:
            return [], {}
        
        # Create column mapping for standardization
        column_mapping = {}
        
        # Use template mapping if available to maintain semantic meaning
        if template_config and 'column_mapping' in template_config:
            template_mapping = template_config['column_mapping']
            for target_semantic, source_col in template_mapping.items():
                if source_col and target_semantic:
                    # Map to semantic names (Date, Amount, etc.) instead of lowercase
                    column_mapping[source_col] = target_semantic
        
        # Add common standardizations for unmapped columns
        common_mappings = {
            'TIMESTAMP': 'Date',
            'TYPE': 'Note', 
            'DESCRIPTION': 'Title',
            'AMOUNT': 'Amount',
            'BALANCE': 'Balance',
            'CURRENCY': 'Currency',
            'Total amount': 'Amount',
            'Running balance': 'Balance'
        }
        
        # Apply common mappings only if not already mapped by template
        for old_col, new_col in common_mappings.items():
            if old_col not in column_mapping:
                column_mapping[old_col] = new_col
        
        # For any remaining columns, use title case
        sample_row = data[0]
        for col in sample_row.keys():
            if col not in column_mapping:
                # Convert to title case for unmapped columns
                standardized_name = col.replace('_', ' ').title().replace(' ', '')
                column_mapping[col] = standardized_name
        
        print(f"      🔄 Column name mapping: {column_mapping}")
        
        # Apply column renaming
        standardized_data = []
        for row in data:
            new_row = {}
            for old_col, value in row.items():
                new_col = column_mapping.get(old_col, old_col)
                new_row[new_col] = value
            standardized_data.append(new_row)
        
        print(f"      ✅ Standardized columns: {list(standardized_data[0].keys()) if standardized_data else []}")
        return standardized_data, column_mapping
    
    def _add_currency_column(self, data: List[Dict], template_config: Dict = None) -> List[Dict]:
        """
        Step 3: Add currency column if missing
        """
        print(f"   💱 Step 3: Adding currency column if needed")
        
        if not data:
            return []
        
        # Check if currency column already exists
        sample_row = data[0]
        has_currency_column = any('currency' in col.lower() for col in sample_row.keys())
        
        if has_currency_column:
            print(f"      ✅ Currency column already exists, skipping...")
            return data
        
        # Determine default currency from template or bank name
        default_currency = self._determine_default_currency(template_config)
        print(f"      💰 Adding currency column with default: {default_currency}")
        
        # Add currency column to all rows
        currency_added_data = []
        for row in data:
            new_row = row.copy()
            new_row['Currency'] = default_currency  # Use Title case for consistency
            currency_added_data.append(new_row)
        
        print(f"      ✅ Currency column added: {default_currency}")
        return currency_added_data
    
    def _determine_default_currency(self, template_config: Dict = None) -> str:
        """
        Determine default currency based on template config or bank name
        """
        if not template_config:
            return 'PKR'  # Default fallback
        
        # Check if template explicitly specifies currency
        if 'default_currency' in template_config:
            return template_config['default_currency']
        
        # Determine currency based on bank name
        bank_name = template_config.get('bank_name', '').lower()
        
        currency_mappings = {
            'nayapay': 'PKR',
            'easypaisa': 'PKR', 
            'jazzcash': 'PKR',
            'sadapay': 'PKR',
            'meezan': 'PKR',
            'hbl': 'PKR',
            'ubl': 'PKR',
            'wise': 'USD',  # Wise default, but they usually have currency columns
            'transferwise': 'USD',
            'revolut': 'EUR',
            'paypal': 'USD',
            'chase': 'USD',
            'wells fargo': 'USD',
            'bank of america': 'USD',
            'hsbc': 'GBP',
            'barclays': 'GBP',
            'lloyds': 'GBP'
        }
        
        for bank_keyword, currency in currency_mappings.items():
            if bank_keyword in bank_name:
                return currency
        
        # Default fallback
        return 'PKR'
    
    def _clean_numeric_columns(self, data: List[Dict]) -> List[Dict]:
        """
        Step 4: Clean numeric columns - convert to float, handle formatting
        """
        print(f"   💰 Step 4: Cleaning numeric columns")
        
        if not data:
            return []
        
        # Identify numeric columns
        sample_row = data[0]
        numeric_cols = []
        for col, value in sample_row.items():
            if (self._is_numeric_column(col.lower()) or 
                self._looks_like_number(str(value)) or
                col.lower() in ['amount', 'balance']):  # Ensure Amount and Balance are always cleaned
                numeric_cols.append(col)
        
        print(f"      📊 Numeric columns found: {numeric_cols}")
        
        cleaned_data = []
        for row_idx, row in enumerate(data):
            cleaned_row = {}
            for col, value in row.items():
                if col in numeric_cols:
                    cleaned_value = self._parse_numeric_value(value)
                    cleaned_row[col] = cleaned_value
                    
                    # Debug first few rows
                    if row_idx < 3:
                        print(f"      💱 Row {row_idx} {col}: '{value}' → {cleaned_value}")
                else:
                    cleaned_row[col] = value
            
            cleaned_data.append(cleaned_row)
        
        print(f"      ✅ Numeric cleaning complete")
        return cleaned_data
    
    def _clean_date_columns(self, data: List[Dict]) -> List[Dict]:
        """
        Step 5: Clean and standardize date columns
        """
        print(f"   📅 Step 5: Cleaning date columns")
        
        if not data:
            return []
        
        # Identify date columns
        sample_row = data[0]
        date_cols = []
        for col, value in sample_row.items():
            if (self._is_date_column(col.lower()) or 
                self._looks_like_date(str(value)) or
                col.lower() in ['date']):  # Ensure Date is always cleaned
                date_cols.append(col)
        
        print(f"      📋 Date columns found: {date_cols}")
        
        cleaned_data = []
        for row_idx, row in enumerate(data):
            cleaned_row = {}
            for col, value in row.items():
                if col in date_cols:
                    cleaned_value = self._parse_date_value(value)
                    cleaned_row[col] = cleaned_value
                    
                    # Debug first few rows
                    if row_idx < 3:
                        print(f"      📆 Row {row_idx} {col}: '{value}' → '{cleaned_value}'")
                else:
                    cleaned_row[col] = value
            
            cleaned_data.append(cleaned_row)
        
        print(f"      ✅ Date cleaning complete")
        return cleaned_data
    
    def _remove_invalid_rows(self, data: List[Dict]) -> List[Dict]:
        """
        Step 6: Remove rows with invalid or missing critical data
        """
        print(f"   🧹 Step 6: Removing invalid rows")
        
        if not data:
            return []
        
        original_count = len(data)
        valid_data = []
        
        for row in data:
            # Check if row has essential data
            has_amount = any(col for col in row.keys() if 'amount' in col.lower() and 
                           row[col] is not None and str(row[col]).strip() and 
                           str(row[col]) != '0' and str(row[col]) != '0.0')
            
            has_date = any(col for col in row.keys() if 'date' in col.lower() and 
                         row[col] is not None and str(row[col]).strip())
            
            # Keep row if it has either amount or date (some flexibility)
            if has_amount or has_date:
                valid_data.append(row)
        
        removed_count = original_count - len(valid_data)
        print(f"      ✅ Removed {removed_count} invalid rows, kept {len(valid_data)} valid rows")
        
        return valid_data
    
    def _create_updated_column_mapping(self, template_config: Dict = None, column_name_mapping: Dict = None) -> Dict[str, str]:
        """
        Step 7: Create updated column mapping for transformation
        Maps Cashew target columns to cleaned column names
        """
        print(f"   🗺️ Step 7: Creating updated column mapping")
        
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
        
        print(f"      ✅ Updated mapping created: {updated_mapping}")
        return updated_mapping
    
    def _is_numeric_column(self, col_name: str) -> bool:
        """Check if column name indicates numeric data"""
        col_lower = col_name.lower()
        return any(keyword in col_lower for keyword in self.numeric_columns)
    
    def _is_date_column(self, col_name: str) -> bool:
        """Check if column name indicates date data"""
        col_lower = col_name.lower()
        return any(keyword in col_lower for keyword in self.date_columns)
    
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
            r'\d{1,2}-\d{1,2}-\d{4}'        # 02-03-2025
        ]
        
        return any(re.search(pattern, value_str) for pattern in date_patterns)
    
    def _parse_numeric_value(self, value: Any) -> float:
        """Parse and clean numeric value to float"""
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
    
    def _parse_date_value(self, value: Any) -> str:
        """Parse and standardize date value to ISO format"""
        try:
            if value is None or str(value).strip() == '':
                return ''
            
            value_str = str(value).strip()
            
            # Common date parsing patterns
            date_formats = [
                '%d %b %Y %I:%M %p',    # 02 Feb 2025 11:17 PM
                '%d %b %Y',             # 02 Feb 2025
                '%Y-%m-%d',             # 2025-02-03
                '%d/%m/%Y',             # 02/03/2025
                '%m/%d/%Y',             # 03/02/2025
                '%d-%m-%Y',             # 02-03-2025
                '%Y-%m-%d %H:%M:%S',    # 2025-02-03 23:17:00
            ]
            
            for fmt in date_formats:
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


# Test the data cleaner
if __name__ == "__main__":
    cleaner = DataCleaner()
    
    # Test with sample NayaPay-like data (no currency column)
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
    
    print("🧪 Testing Data Cleaner with Fixed Column Mapping")
    result = cleaner.clean_parsed_data(sample_parsed_data, template_config)
    
    print(f"\n📊 Cleaning Result:")
    print(json.dumps(result, indent=2, default=str))
