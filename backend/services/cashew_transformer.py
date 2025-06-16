"""
CashewTransformer Service - Clean, standalone data transformation to Cashew format.
Handles column mapping, data parsing, and universal fallback logic.
"""
from typing import Dict, List, Optional
import re
from datetime import datetime
import pandas as pd


class CashewTransformer:
    """
    Clean, standalone service for transforming parsed data to Cashew format.
    No external dependencies - handles all transformation logic internally.
    """

    def __init__(self):
        print("🚀 [CashewTransformer] Initializing clean standalone transformer...")

    def transform_to_cashew(self, data: List[Dict], column_mapping: Dict[str, str],
                           bank_name: str = "", categorization_rules: List[Dict] = None,
                           default_category_rules: Dict = None, account_mapping: Dict = None,
                           config: Dict = None) -> List[Dict]:
        """
        Transform parsed data to Cashew format with universal fallback logic.
        
        Args:
            data: List of data rows
            column_mapping: Column mapping dictionary  
            bank_name: Bank name for Account field
            config: Bank configuration for fallback logic (optional)
            
        Returns:
            List of transformed Cashew format rows
        """
        print(f"🔄 [CashewTransformer] Starting clean transformation for bank: '{bank_name}'")
        print(f"   📊 Input rows: {len(data)}, Column mapping: {column_mapping}")
        
        cashew_data = []
        
        for idx, row in enumerate(data):
            # Initialize Cashew row with required fields
            cashew_row = {
                'Date': '',
                'Amount': '',
                'Category': '',
                'Title': '',
                'Note': '',
                'Account': bank_name
            }
            
            # Apply column mapping
            for cashew_col, source_col in column_mapping.items():
                if source_col in row and pd.notna(row[source_col]):
                    if cashew_col == 'Date':
                        cashew_row[cashew_col] = self.parse_date(str(row[source_col]))
                    elif cashew_col == 'Amount':
                        original_amount = str(row[source_col])
                        parsed_amount = self.parse_amount(original_amount)
                        cashew_row[cashew_col] = parsed_amount
                        if idx < 3: 
                            print(f"   💰 Row {idx} Amount: '{original_amount}' → '{parsed_amount}'")
                    elif cashew_col == 'Account' and account_mapping:
                        currency = str(row[source_col])
                        cashew_row[cashew_col] = account_mapping.get(currency, bank_name)
                    else:
                        cashew_row[cashew_col] = str(row[source_col])
            
            # Apply universal fallback logic for any empty field
            for cashew_field in ['Date', 'Title', 'Amount', 'Currency']:
                if not cashew_row.get(cashew_field):
                    fallback_value = self.resolve_field_with_fallback(row, cashew_field)
                    if fallback_value:
                        if cashew_field == 'Date':
                            cashew_row[cashew_field] = self.parse_date(fallback_value)
                        elif cashew_field == 'Amount':
                            cashew_row[cashew_field] = self.parse_amount(fallback_value)
                        else:
                            cashew_row[cashew_field] = str(fallback_value)
                        
                        if idx < 3:
                            print(f"   🔄 Row {idx} Used Backup{cashew_field}: '{fallback_value}' → '{cashew_row[cashew_field]}'")
            
            # Apply basic categorization
            self.apply_basic_categorization(cashew_row)
            
            # Debug output for first few rows
            if idx < 3:
                print(f"   📋 Row {idx}: Date='{cashew_row['Date']}', Amount='{cashew_row['Amount']}', Title='{cashew_row['Title'][:50]}...'")
            
            # Only include rows with valid amounts
            if cashew_row['Amount'] and cashew_row['Amount'] != '0':
                cashew_data.append(cashew_row)
            else:
                if idx < 5:
                    print(f"   ⚠️  Skipping row {idx}: Invalid/zero amount '{cashew_row['Amount']}'")
        
        print(f"   ✅ Clean transformation complete: {len(cashew_data)} valid rows")
        return cashew_data

    def resolve_field_with_fallback(self, row, primary_field):
        """
        Universal fallback logic - directly looks for Backup[Field] in data.
        Works for any field: BackupDate, BackupTitle, BackupAmount, BackupCurrency, etc.
        """
        # Try primary field first
        value = row.get(primary_field)
        if value and str(value).strip():
            return value
        
        # Try backup field with direct lookup
        backup_field = f'Backup{primary_field}'
        backup_value = row.get(backup_field)
        
        if backup_value and str(backup_value).strip():
            return backup_value
        
        return ""  # Graceful fallback

    def apply_basic_categorization(self, cashew_row: Dict):
        """Apply basic categorization based on amount"""
        if not cashew_row.get('Category'):
            try:
                amount = float(cashew_row['Amount'])
                if amount > 0:
                    cashew_row['Category'] = 'Income'
                elif amount < 0:
                    cashew_row['Category'] = 'Expense'
                else:
                    cashew_row['Category'] = 'Transfer'
            except (ValueError, TypeError):
                cashew_row['Category'] = 'Uncategorized'

    def parse_date(self, date_str: str) -> str:
        """
        Parse a date string into standard Cashew format: YYYY-MM-DD HH:MM:SS
        Uses 00:00:00 as default time when no time is provided.
        """
        if not date_str or str(date_str).strip() == '' or str(date_str).lower() == 'nan':
            return ''
            
        date_str = str(date_str).strip()
        
        try:
            # Handle common date formats with time
            datetime_formats = [
                '%Y-%m-%d %H:%M:%S',  # 2025-04-30 15:23:00
                '%Y.%m.%d %H:%M:%S',  # 2025.04.30 15:23:00 (Hungarian with time)
                '%d %b %Y %I:%M %p',  # 30 Apr 2025 3:23 PM
                '%d %b %Y %H:%M',     # 30 Apr 2025 15:23
            ]
            
            # Try formats with time first
            for fmt in datetime_formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue
            
            # Handle date-only formats (add 00:00:00 time)
            date_only_formats = [
                '%Y-%m-%d',           # 2025-04-30
                '%Y.%m.%d',           # 2025.04.30 (Hungarian format)
                '%d/%m/%Y',           # 30/04/2025
                '%m/%d/%Y',           # 04/30/2025
                '%d-%m-%Y',           # 30-04-2025
            ]
            
            for fmt in date_only_formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d 00:00:00')
                except ValueError:
                    continue
            
            # If no format matches, return original
            return date_str
            
        except Exception as e:
            print(f"⚠️  Date parsing error for '{date_str}': {e}")
            return date_str

    def parse_amount(self, amount_str: str) -> str:
        """
        Clean and parse an amount string to float format.
        """
        try:
            if not amount_str or str(amount_str).strip() == '' or str(amount_str).lower() == 'nan':
                return '0'
            
            amount_str = str(amount_str).strip()
            amount_str = amount_str.strip('"').strip("'")
            
            # Handle Hungarian format (comma as thousands separator)
            # e.g., "-6,325" becomes "-6325"
            if ',' in amount_str and '.' not in amount_str:
                # Check if comma is thousands separator or decimal
                comma_pos = amount_str.rfind(',')
                after_comma = amount_str[comma_pos + 1:]
                
                # If 3 digits after comma, it's thousands separator
                if len(after_comma) == 3 and after_comma.isdigit():
                    amount_str = amount_str.replace(',', '')
                # Otherwise assume it's decimal separator
                else:
                    amount_str = amount_str.replace(',', '.')
            
            # Clean up and determine sign
            cleaned = re.sub(r'[^0-9.\-+]', '', amount_str)
            
            is_negative = False
            if (amount_str.startswith('-') or amount_str.startswith('(') or 
                amount_str.endswith(')') or '(' in amount_str):
                is_negative = True
            elif amount_str.startswith('+'):
                is_negative = False
            
            cleaned = cleaned.lstrip('+-')
            
            if is_negative and not cleaned.startswith('-'):
                cleaned = '-' + cleaned
            
            if cleaned:
                return str(float(cleaned))
            else:
                return '0'
                
        except Exception as e:
            print(f"⚠️  Amount parsing error for '{amount_str}': {e}")
            return '0'
