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
            # Get source bank for debugging
            source_bank = row.get('_source_bank', 'unknown')
            
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
            
            # Preserve _source_bank for bank matching in description cleaning
            if '_source_bank' in row:
                cashew_row['_source_bank'] = row['_source_bank']
            
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
            # This now handles both raw data (using source_col) and pre-cleaned data (using cashew_col)
            for cashew_col, source_col in column_mapping.items():
                value_found = None
                if source_col in row and pd.notna(row[source_col]):
                    value_found = row[source_col]
                elif cashew_col in row and pd.notna(row[cashew_col]):
                    value_found = row[cashew_col]

                if value_found is not None:
                    if cashew_col == 'date':
                        # --- NEW LOGIC ---
                        date_format_from_config = None
                        if config and source_bank in config:
                            bank_specific_config = config.get(source_bank, {})
                            date_format_from_config = bank_specific_config.get('csv_config', {}).get('date_format')
                        
                        cashew_row[cashew_col] = self.parse_date(str(value_found), date_format=date_format_from_config)
                        # --- END NEW LOGIC ---
                    elif cashew_col == 'amount':
                        source_value = value_found
                        original_amount = str(source_value)
                        parsed_amount = self.parse_amount(original_amount)
                        cashew_row[cashew_col] = parsed_amount
                        if idx < 3: 
                            print(f"    Row {idx} Amount mapping - source_col='{source_col}', raw_value='{source_value}' (type: {type(source_value)}), str_value='{original_amount}', parsed='{parsed_amount}'")
                    elif cashew_col in ['debit', 'credit']:
                        # Store debit/credit values for later calculation
                        cashew_row[cashew_col] = str(value_found)
                        if idx < 3:
                            print(f"    Row {idx} {cashew_col.title()} mapping - source_col='{source_col}', raw_value='{value_found}'")
                    elif cashew_col == 'account' and account_mapping:
                        currency = str(value_found)
                        mapped_account = account_mapping.get(currency, bank_name)
                        cashew_row[cashew_col] = mapped_account
                        if idx < 3:
                            print(f"    Row {idx} Account mapping: source_col='{source_col}', Currency='{currency}' → Account='{mapped_account}'")
                    else:
                        cashew_row[cashew_col] = str(value_found)
            
            # Preserve exchange fields for transfer detection (keep original source column names)
            for source_col in row.keys():
                if any(keyword in source_col.lower() for keyword in ['exchange', 'convert', 'target', 'destination']):
                    if source_col not in cashew_row:  # Don't override mapped fields
                        cashew_row[source_col] = row[source_col]
                        if idx < 3:
                            print(f"    Row {idx} Preserving exchange field: {source_col} = {row[source_col]}")
            
            # Calculate amount from debit/credit if no direct amount mapping exists or amount is empty
            amount_val = cashew_row.get('amount', '')
            has_debit_credit = ('debit' in cashew_row or 'credit' in cashew_row or 
                               'debit' in row or 'credit' in row)
            
            if (not amount_val or str(amount_val).strip() == '') and has_debit_credit:
                # Check both cashew_row (from column mapping) and original row for debit/credit
                debit_val = self.parse_amount(cashew_row.get('debit', row.get('debit', '0')))
                credit_val = self.parse_amount(cashew_row.get('credit', row.get('credit', '0')))
                
                # Calculate final amount: credit - debit (credit is positive, debit is negative)
                final_amount = float(credit_val) - float(debit_val)
                cashew_row['amount'] = str(final_amount)
                
                print(f"    Row {idx} ({source_bank}) Debit/Credit calculation - debit='{debit_val}', credit='{credit_val}', final_amount='{final_amount}'")
            
            # Apply universal fallback logic for any empty field (lowercase internally)
            for cashew_field in ['date', 'title', 'amount', 'currency']:
                if not cashew_row.get(cashew_field):
                    fallback_value = self.resolve_field_with_fallback(row, cashew_field)
                    if fallback_value:
                        if cashew_field == 'date':
                            # Use the same date format from config for fallback parsing
                            date_format_from_config = None
                            if config and source_bank in config:
                                bank_specific_config = config.get(source_bank, {})
                                date_format_from_config = bank_specific_config.get('csv_config', {}).get('date_format')
                            cashew_row[cashew_field] = self.parse_date(fallback_value, date_format=date_format_from_config)
                        elif cashew_field == 'amount':
                            cashew_row[cashew_field] = self.parse_amount(fallback_value)
                        else:
                            cashew_row[cashew_field] = str(fallback_value)
                        
                        if idx < 3:
                            print(f"    Row {idx} Used fallback for {cashew_field}: '{fallback_value}' → '{cashew_row[cashew_field]}'")
            
            # Apply basic categorization
            self.apply_basic_categorization(cashew_row)
            
            # Debug output for first few rows
            if idx < 3:
                print(f"    Row {idx}: date='{cashew_row['date']}', amount='{cashew_row['amount']}', title='{cashew_row['title'][:50]}...'")
            
            # Only include rows with valid amounts
            amount_val = cashew_row['amount']
            source_bank = cashew_row.get('_source_bank', 'unknown')
            
            # Enhanced debugging for amount validation
            print(f"   [DEBUG] Row {idx} ({source_bank}) final amount check - value: '{amount_val}', type: {type(amount_val)}, bool: {bool(amount_val)}")
            
            if amount_val and amount_val != '0' and amount_val != 0:
                # Convert to uppercase for final Cashew format before adding to results
                final_cashew_row = self._convert_to_final_cashew_format(cashew_row)
                cashew_data.append(final_cashew_row)
                if source_bank == 'Meezan':
                    print(f"   [SUCCESS] Meezan row {idx} INCLUDED with amount '{amount_val}'")
            else:
                print(f"   [WARNING] FILTERING OUT row {idx} ({source_bank}): Invalid/zero amount '{amount_val}' (type: {type(amount_val)})")
                if source_bank == 'Meezan':
                    print(f"   [CRITICAL] MEEZAN ROW FILTERED! Row data: {cashew_row}")
                    print(f"   [DEBUG] Original row data from input: {data[idx] if idx < len(data) else 'Index out of range'}")
        
        print(f"   [SUCCESS] Clean transformation complete: {len(cashew_data)} valid rows")
        return cashew_data

    def resolve_field_with_fallback(self, row, primary_field):
        """
        Universal fallback logic - directly looks for backup fields in data.
        Works for any field: backupdate, backuptitle, backupamount, backupcurrency, etc.
        """
        # Try primary field first
        value = row.get(primary_field)
        if value and str(value).strip():
            return value
        
        # Try backup field with direct lookup (e.g., backupdate)
        backup_field = f'backup{primary_field}'
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
        final_row = {
            'Date': lowercase_row.get('date', ''),
            'Amount': lowercase_row.get('amount', ''),
            'Category': lowercase_row.get('category', ''),
            'Title': lowercase_row.get('title', ''),
            'Note': lowercase_row.get('note', ''),
            'Account': lowercase_row.get('account', '')
        }
        
        # Preserve _source_bank field for bank matching in description cleaning
        if '_source_bank' in lowercase_row:
            final_row['_source_bank'] = lowercase_row['_source_bank']
        
        # Preserve exchange fields for transfer detection
        for field_name, value in lowercase_row.items():
            if any(keyword in field_name.lower() for keyword in ['exchange', 'convert', 'target', 'destination']):
                final_row[field_name] = value
            
        return final_row

    def parse_date(self, date_str: str, date_format: Optional[str] = None) -> str:
        """
        Parse a date string into standard Cashew format: YYYY-MM-DD HH:MM:SS
        """
        if not date_str or str(date_str).strip() == '' or str(date_str).lower() == 'nan':
            return ''
            
        date_str = str(date_str).strip()
        
        # --- NEW LOGIC ---
        if date_format:
            try:
                dt = datetime.strptime(date_str, date_format)
                # Check if time info is present in the format string
                if any(c in date_format for c in ['%H', '%I', '%M', '%S', '%p']):
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    return dt.strftime('%Y-%m-%d 00:00:00')
            except (ValueError, TypeError):
                print(f"[WARNING] Date '{date_str}' did not match configured format '{date_format}'. Falling back.")
        # --- END NEW LOGIC ---
        
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
                '%d.%m.%y',           # 20.02.18 (German format)
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
