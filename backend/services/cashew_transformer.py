"""
CashewTransformer Service - Clean, standalone data transformation to Cashew format.
Handles column mapping, data parsing, and universal fallback logic.
"""
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal
import pandas as pd

from backend.infrastructure.csv_cleaning.date_cleaner import DateCleaner
from backend.shared.utils.amount_text import format_amount, parse_amount_text
import logging

logger = logging.getLogger(__name__)


class CashewTransformer:
    """
    Clean, standalone service for transforming parsed data to Cashew format.
    No external dependencies - handles all transformation logic internally.
    """

    def __init__(self):
        logger.debug("[START] [CashewTransformer] Initializing clean standalone transformer...")

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
        logger.debug(f" [CashewTransformer] Starting clean transformation for bank: '{bank_name}'")
        logger.debug(f"   [DATA] Input rows: {len(data)}, Column mapping: {column_mapping}")
        logger.debug(f"   [DEBUG] Account mapping: {account_mapping}")
        
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
                                logger.debug(f"    Row {idx} Auto Account mapping: Currency='{currency}' → Account='{mapped_account}'")
                
                # If no bank-specific account mapping found, preserve existing account value
                # (which should be the cashew_account for single-currency banks)
                if not should_apply_account_mapping:
                    # Keep the existing account value (set during multi-CSV processing)
                    if idx < 3:
                        existing_account = cashew_row.get('account', bank_name)
                        logger.debug(f"    Row {idx} Preserving existing account: Currency='{currency}', Account='{existing_account}'")
            
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
                            pass
                    elif cashew_col in ['debit', 'credit']:
                        # Store debit/credit values for later calculation
                        cashew_row[cashew_col] = str(value_found)
                        if idx < 3:
                            pass
                    elif cashew_col == 'account' and account_mapping:
                        currency = str(value_found)
                        mapped_account = account_mapping.get(currency, bank_name)
                        cashew_row[cashew_col] = mapped_account
                        if idx < 3:
                            logger.debug(f"    Row {idx} Account mapping: source_col='{source_col}', Currency='{currency}' → Account='{mapped_account}'")
                    else:
                        cashew_row[cashew_col] = str(value_found)
            
            # Preserve exchange fields for transfer detection (keep original source column names)
            for source_col in row.keys():
                if any(keyword in source_col.lower() for keyword in ['exchange', 'convert', 'target', 'destination']):
                    if source_col not in cashew_row:  # Don't override mapped fields
                        cashew_row[source_col] = row[source_col]
                        if idx < 3:
                            pass
            
            # Calculate amount from debit/credit if no direct amount mapping exists or amount is empty
            amount_val = cashew_row.get('amount', '')
            has_debit_credit = ('debit' in cashew_row or 'credit' in cashew_row or 
                               'debit' in row or 'credit' in row)
            
            if (not amount_val or str(amount_val).strip() == '') and has_debit_credit:
                # Check both cashew_row (from column mapping) and original row for debit/credit
                debit_val = parse_amount_text(cashew_row.get('debit', row.get('debit', '0'))) or Decimal(0)
                credit_val = parse_amount_text(cashew_row.get('credit', row.get('credit', '0'))) or Decimal(0)
                
                # Calculate final amount: credit - debit (credit is positive, debit is negative)
                final_amount = format_amount(credit_val - debit_val)
                cashew_row['amount'] = final_amount
                
            
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
                            pass
            
            # Apply basic categorization
            self.apply_basic_categorization(cashew_row)
            
            # Debug output for first few rows
            if idx < 3:
                pass
            
            # Only include rows with valid amounts
            amount_val = cashew_row['amount']
            source_bank = cashew_row.get('_source_bank', 'unknown')
            
            # Enhanced debugging for amount validation
            
            if parse_amount_text(amount_val):
                # Convert to uppercase for final Cashew format before adding to results
                final_cashew_row = self._convert_to_final_cashew_format(cashew_row)
                cashew_data.append(final_cashew_row)
                if source_bank == 'Meezan':
                    pass
            else:
                if source_bank == 'Meezan':
                    pass
        
        logger.debug(f"   [SUCCESS] Clean transformation complete: {len(cashew_data)} valid rows")
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
        Format a date for Cashew: YYYY-MM-DD HH:MM:SS.

        Dates normally arrive already normalised to YYYY-MM-DD by DateCleaner
        during parsing. Anything else (e.g. data that skipped cleaning) is
        parsed by DateCleaner with the bank's configured format.
        """
        if date_str is None or str(date_str).strip() == '' or str(date_str).lower() == 'nan':
            return ''
        date_str = str(date_str).strip()

        try:
            return datetime.fromisoformat(date_str).strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            pass

        cleaned = DateCleaner(config_date_format=date_format).parse_date_value(date_str)
        try:
            return datetime.strptime(cleaned, '%Y-%m-%d').strftime('%Y-%m-%d 00:00:00')
        except ValueError:
            return date_str  # unreadable: keep the original text

    def parse_amount(self, amount_str: str) -> str:
        """
        Clean and parse an amount string to float format.
        """
        amount = parse_amount_text(amount_str)
        if amount is None:
            if amount_str is not None and str(amount_str).strip() not in ('', 'nan'):
                pass
            return '0'
        return format_amount(amount)
