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
        print("[START] [CashewTransformer] Initializing clean standalone transformer...")

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
        print(f" [CashewTransformer] Starting clean transformation for bank: '{bank_name}'")
        print(f"   [DATA] Input rows: {len(data)}, Column mapping: {column_mapping}")
        print(f"   [DEBUG] Account mapping: {account_mapping}")
        
        cashew_data = []
        
        for idx, row in enumerate(data):
            # Initialize Cashew row with required fields (lowercase internally)
            # Preserve existing Account value if it exists (from multi-CSV processing)
            existing_account = row.get('Account', row.get('account', bank_name))
            cashew_row = {
                'date': '',
                'amount': '',
                'category': '',
                'title': '',
                'note': '',
                'account': existing_account
            }
            
            # Handle account mapping when no explicit account column mapping exists
            if 'currency' in row or 'Currency' in row:  # Support both cases during transition
                currency = str(row.get('currency', row.get('Currency', '')))
                transaction_bank = row.get('_source_bank')
                
                # Check if this bank uses account mapping (multi-currency)
                should_apply_account_mapping = False
                
                if config and isinstance(config, dict) and transaction_bank and transaction_bank in config:
                    bank_config_dict = config[transaction_bank]
                    if 'account_mapping' in bank_config_dict:
                        should_apply_account_mapping = True
                        bank_account_mapping = bank_config_dict['account_mapping']
                        if currency in bank_account_mapping:
                            mapped_account = bank_account_mapping[currency]
                            cashew_row['account'] = mapped_account
                            if idx < 3:
                                print(f"    Row {idx} Auto Account mapping: Currency='{currency}' → Account='{mapped_account}'")
                
                # If no bank-specific account mapping found, preserve existing account value
                # (which should be the cashew_account for single-currency banks)
                if not should_apply_account_mapping:
                    # Keep the existing account value (set during multi-CSV processing)
                    if idx < 3:
                        existing_account = cashew_row.get('account', bank_name)
                        print(f"    Row {idx} Preserving existing account: Currency='{currency}', Account='{existing_account}'")
            
            # Apply column mapping (lowercase internally)
            for cashew_col, source_col in column_mapping.items():
                if source_col in row and pd.notna(row[source_col]):
                    if cashew_col == 'date':
                        cashew_row[cashew_col] = self.parse_date(str(row[source_col]))
                    elif cashew_col == 'amount':
                        source_value = row[source_col]
                        original_amount = str(source_value)
                        parsed_amount = self.parse_amount(original_amount)
                        cashew_row[cashew_col] = parsed_amount
                        if idx < 3: 
                            print(f"    Row {idx} Amount mapping - source_col='{source_col}', raw_value='{source_value}' (type: {type(source_value)}), str_value='{original_amount}', parsed='{parsed_amount}'")
                    elif cashew_col == 'account' and account_mapping:
                        currency = str(row[source_col])
                        mapped_account = account_mapping.get(currency, bank_name)
                        cashew_row[cashew_col] = mapped_account
                        if idx < 3:
                            print(f"    Row {idx} Account mapping: source_col='{source_col}', Currency='{currency}' → Account='{mapped_account}'")
                    else:
                        cashew_row[cashew_col] = str(row[source_col])
            
            # Apply universal fallback logic for any empty field (lowercase internally)
            for cashew_field in ['date', 'title', 'amount', 'currency']:
                if not cashew_row.get(cashew_field):
                    fallback_value = self.resolve_field_with_fallback(row, cashew_field)
                    if fallback_value:
                        if cashew_field == 'date':
                            cashew_row[cashew_field] = self.parse_date(fallback_value)
                        elif cashew_field == 'amount':
                            cashew_row[cashew_field] = self.parse_amount(fallback_value)
                        else:
                            cashew_row[cashew_field] = str(fallback_value)
                        
                        if idx < 3:
                            print(f"    Row {idx} Used Backup{cashew_field}: '{fallback_value}' → '{cashew_row[cashew_field]}'")
            
            # Apply basic categorization
            self.apply_basic_categorization(cashew_row)
            
            # Debug output for first few rows
            if idx < 3:
                print(f"    Row {idx}: date='{cashew_row['date']}', amount='{cashew_row['amount']}', title='{cashew_row['title'][:50]}...'")
            
            # Only include rows with valid amounts
            amount_val = cashew_row['amount']
            if idx < 5:
                print(f"   [DEBUG] Row {idx} final amount check - value: '{amount_val}', type: {type(amount_val)}, bool: {bool(amount_val)}")
            
            if amount_val and amount_val != '0' and amount_val != 0:
                # Convert to uppercase for final Cashew format before adding to results
                final_cashew_row = self._convert_to_final_cashew_format(cashew_row)
                cashew_data.append(final_cashew_row)
            else:
                if idx < 5:
                    print(f"   [WARNING]  Skipping row {idx}: Invalid/zero amount '{amount_val}' (type: {type(amount_val)})")
        
        print(f"   [SUCCESS] Clean transformation complete: {len(cashew_data)} valid rows")
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
        """Apply basic categorization based on amount (lowercase internally)"""
        if not cashew_row.get('category'):
            try:
                amount = float(cashew_row['amount'])
                if amount > 0:
                    cashew_row['category'] = 'Income'
                elif amount < 0:
                    cashew_row['category'] = 'Expense'
                else:
                    cashew_row['category'] = 'Transfer'
            except (ValueError, TypeError):
                cashew_row['category'] = 'Uncategorized'
    
    def _convert_to_final_cashew_format(self, lowercase_row: Dict) -> Dict:
        """Convert lowercase internal format to uppercase Cashew export format"""
        return {
            'Date': lowercase_row.get('date', ''),
            'Amount': lowercase_row.get('amount', ''),
            'Category': lowercase_row.get('category', ''),
            'Title': lowercase_row.get('title', ''),
            'Note': lowercase_row.get('note', ''),
            'Account': lowercase_row.get('account', '')
        }

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
            print(f"[WARNING]  Date parsing error for '{date_str}': {e}")
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
            print(f"[WARNING]  Amount parsing error for '{amount_str}': {e}")
            return '0'
