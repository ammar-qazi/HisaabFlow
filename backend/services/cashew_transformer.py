"""
CashewTransformer Service - Standalone data transformation to Cashew format.
This service extracts the transformation logic from the legacy EnhancedCSVParser.
"""
import os
import sys
from typing import Dict, List, Optional
import re # For inlined legacy parsing and categorization logic
from datetime import datetime # For inlined legacy date parsing
import pandas as pd # For inlined legacy transformation logic

# Attempt to make project-level 'transformation' directory importable for UniversalTransformer
# This path adjustment mirrors the one in the original EnhancedCSVParser.
# It assumes 'universal_transformer.py' is in a 'transformation' directory at the project root.
try:
    # Path from 'backend/services/' to project root is '../..'
    # Then into 'transformation/'
    transformation_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'transformation'))
    if transformation_dir not in sys.path:
        sys.path.append(transformation_dir)
    print(f"ℹ️ [CashewTransformer] Added to sys.path for UniversalTransformer: {transformation_dir}")
except Exception as e:
    print(f"⚠️ [CashewTransformer] Error adjusting sys.path for UniversalTransformer: {e}")


try:
    from universal_transformer import UniversalTransformer
    UNIVERSAL_TRANSFORMER_AVAILABLE = True
    print("✅ [CashewTransformer] Universal Transformer imported successfully.")
except ImportError as e:
    print(f"❌ [CashewTransformer] Universal Transformer import failed: {e}")
    UNIVERSAL_TRANSFORMER_AVAILABLE = False
    UniversalTransformer = None # Ensure it's None if import fails

class CashewTransformer:
    """
    Handles transformation of parsed data to Cashew format.
    Orchestrates using UniversalTransformer if available, otherwise LegacyTransformer.
    """

    def __init__(self):
        print("🚀 [CashewTransformer] Initializing...")

        # Attempt to initialize Universal Transformer
        self.universal_transformer = None
        if UNIVERSAL_TRANSFORMER_AVAILABLE and UniversalTransformer:
            try:
                self.universal_transformer = UniversalTransformer()
                print("✅ [CashewTransformer] Universal Transformer initialized successfully.")
            except Exception as e:
                print(f"❌ [CashewTransformer] UniversalTransformer initialization failed: {e}")
                self.universal_transformer = None # Ensure it's None on failure
        
        if not self.universal_transformer:
             print("⚠️ [CashewTransformer] UniversalTransformer not available/failed. Will attempt to use Inlined Legacy Transformer.")

        # For the inlined legacy path, methods from DataParser and CategorizationEngine
        # will be copied directly into this class as private methods. No separate initialization needed.

    def resolve_field_with_fallback(self, row, primary_field, config):
        """
        Universal fallback logic that works for any bank config
        """
        # Try primary field first
        value = row.get(primary_field)
        if value and str(value).strip():
            return value
        
        # Handle both single config dict and multi-bank configs dict
        if config:
            if isinstance(config, dict):
                # If it's a multi-bank config (from multi-CSV), find the right one
                if 'column_mapping' in config:
                    # Single bank config
                    column_mapping = config.get('column_mapping', {})
                else:
                    # Multi-bank config - for now, try to find any config with the backup field
                    column_mapping = {}
                    for bank_name, bank_config in config.items():
                        if isinstance(bank_config, dict) and 'column_mapping' in bank_config:
                            column_mapping = bank_config.get('column_mapping', {})
                            break
                
                # Try backup field if defined in config
                backup_key = f'Backup{primary_field}'
                backup_column = column_mapping.get(backup_key)
                
                if backup_column:
                    backup_value = row.get(backup_column)
                    if backup_value and str(backup_value).strip():
                        print(f"🔄 Used fallback {backup_column} for {primary_field}")
                        return backup_value
        
        return ""  # Graceful fallback

        # Attempt to initialize Universal Transformer
        self.universal_transformer = None
        if UNIVERSAL_TRANSFORMER_AVAILABLE and UniversalTransformer:
            try:
                self.universal_transformer = UniversalTransformer()
                print("✅ [CashewTransformer] Universal Transformer initialized successfully.")
            except Exception as e:
                print(f"❌ [CashewTransformer] UniversalTransformer initialization failed: {e}")
                self.universal_transformer = None # Ensure it's None on failure
        
        if not self.universal_transformer:
             print("⚠️ [CashewTransformer] UniversalTransformer not available/failed. Will attempt to use Inlined Legacy Transformer.")

        # For the inlined legacy path, methods from DataParser and CategorizationEngine
        # will be copied directly into this class as private methods. No separate initialization needed.

    def transform_to_cashew(self, data: List[Dict], column_mapping: Dict[str, str],
                           bank_name: str = "", categorization_rules: List[Dict] = None,
                           default_category_rules: Dict = None, account_mapping: Dict = None,
                           bank_rules_settings: Dict[str, bool] = None, config: Dict = None) -> List[Dict]:
        """
        Transform parsed data to Cashew format with smart categorization.
        Uses UniversalTransformer if available, otherwise falls back to inlined legacy logic.
        """
        print(f"🔄 [CashewTransformer] Starting transform_to_cashew for bank: '{bank_name}'")
        print(f"   Input data rows: {len(data)}, Column mapping: {column_mapping}")

        if self.universal_transformer:
            print(f"🌟 [CashewTransformer] USING UNIVERSAL TRANSFORMER for bank '{bank_name}'")
            # Note: UniversalTransformer's transform_to_cashew signature might differ slightly.
            # The original EnhancedCSVParser call was:
            # self.universal_transformer.transform_to_cashew(data, column_mapping, bank_name, account_mapping, bank_rules_settings)
            # We replicate this here.
            return self.universal_transformer.transform_to_cashew(
                data, column_mapping, bank_name, account_mapping, bank_rules_settings
            )
        
        # Fallback to Inlined Legacy Transformation
        # This path is now self-contained within this class.
        print(f"🔄 [CashewTransformer] USING INLINED LEGACY TRANSFORMATION for bank '{bank_name}' (Universal Transformer not available/failed or not used).")
        return self._inlined_legacy_transform(
            data, column_mapping, bank_name, categorization_rules,
            default_category_rules, account_mapping, bank_rules_settings, config
        )
        
        # The critical error for missing transformation method is less likely now,
        # as the inlined legacy path doesn't depend on external initializations that can fail,
        # assuming the methods are copied correctly.
        # However, if for some reason _inlined_legacy_transform itself had an issue,
        # a more robust error handling or logging could be here.
        # For now, it directly calls _inlined_legacy_transform.

    # --- Inlined Legacy Helper Methods ---
    # These methods should contain the exact code from DataParser and CategorizationEngine

    def _legacy_parse_date(self, date_str: str) -> str:
        """
        Inlined from DataParser.parse_date.
        Parses a date string into a standard format.
        """
        # <<<< COPY ACTUAL CODE FROM DataParser.parse_date HERE >>>>
        if not date_str or str(date_str).strip() == '' or str(date_str).lower() == 'nan':
            return ''
            
        date_str = str(date_str).strip()
        
        try:
            if re.match(r'\d{2} \w{3} \d{4} \d{1,2}:\d{2} (AM|PM)', date_str):
                dt = datetime.strptime(date_str, '%d %b %Y %I:%M %p')
                return dt.strftime('%Y-%m-%d')
            
            if re.match(r'\d{2} \w{3} \d{4} \d{2}:\d{2} (AM|PM)', date_str):
                dt = datetime.strptime(date_str, '%d %b %Y %I:%M %p')
                return dt.strftime('%Y-%m-%d')
            
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%d-%m-%Y %H:%M:%S']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            return date_str
        except Exception as e:
            print(f"⚠️  [LegacyFallback] Date parsing error for '{date_str}': {e}")
            return date_str

    def _legacy_parse_amount(self, amount_str: str) -> str:
        """
        Inlined from DataParser.parse_amount.
        Cleans and formats an amount string.
        """
        # <<<< COPY ACTUAL CODE FROM DataParser.parse_amount HERE >>>>
        try:
            if not amount_str or str(amount_str).strip() == '' or str(amount_str).lower() == 'nan':
                return '0'
            
            amount_str = str(amount_str).strip()
            amount_str = amount_str.strip('"').strip("'")
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
            print(f"⚠️  [LegacyFallback] Amount parsing error for '{amount_str}': {e}")
            return '0'

    def _legacy_parse_amount_for_comparison(self, amount_str: str) -> str:
        """
        Inlined from CategorizationEngine._parse_amount_for_comparison.
        Helper for parsing amount strings for numeric comparisons in categorization.
        This is essentially a copy of DataParser.parse_amount.
        """
        # <<<< ACTUAL CODE FROM CategorizationEngine._parse_amount_for_comparison COPIED HERE >>>>
        # This method in CategorizationEngine was identical to DataParser.parse_amount
        return self._legacy_parse_amount(amount_str)

    def _legacy_apply_categorization_rules(self, cashew_row: Dict, original_row: Dict,
                                          categorization_rules: List[Dict] = None,
                                          default_category_rules: Dict = None) -> Dict:
        """
        Inlined from CategorizationEngine.apply_categorization_rules.
        Applies categorization rules to a transaction row.
        """
        # <<<< ACTUAL CODE FROM CategorizationEngine.apply_categorization_rules COPIED HERE >>>>
        if not categorization_rules:
            return self._legacy_apply_default_categorization(cashew_row, default_category_rules)
        
        sorted_rules = sorted(categorization_rules, key=lambda x: x.get('priority', 999))
        
        for rule in sorted_rules:
            if self._legacy_check_rule_conditions(original_row, rule.get('conditions', {})):
                actions = rule.get('actions', {})
                
                if 'set_category' in actions:
                    cashew_row['Category'] = actions['set_category']
                
                if 'set_title' in actions:
                    cashew_row['Title'] = actions['set_title']
                elif 'set_title_template' in actions:
                    template = actions['set_title_template']
                    if 'extract_name' in actions:
                        extracted_name = self._legacy_extract_name(original_row, actions['extract_name'])
                        cashew_row['Title'] = template.format(extract_name=extracted_name)
                    else:
                        cashew_row['Title'] = template
                elif 'clean_description' in actions:
                    clean_config = actions['clean_description']
                    cleaned_desc = self._legacy_clean_description(original_row, clean_config)
                    cashew_row['Title'] = cleaned_desc
                elif not actions.get('keep_original_title', False):
                    pass # Keep original title if not specified otherwise
                
                if not actions.get('continue_processing', False):
                    break
        
        if not cashew_row['Category']:
            cashew_row = self._legacy_apply_default_categorization(cashew_row, default_category_rules)
        
        return cashew_row

    def _legacy_check_rule_conditions(self, row: Dict, conditions: Dict) -> bool:
        """Inlined from CategorizationEngine.check_rule_conditions."""
        if not conditions:
            return False
        
        if 'and' in conditions:
            return all(self._legacy_check_single_condition(row, cond) for cond in conditions['and'])
        elif 'or' in conditions:
            return any(self._legacy_check_single_condition(row, cond) for cond in conditions['or'])
        else:
            return self._legacy_check_single_condition(row, conditions)

    def _legacy_check_single_condition(self, row: Dict, condition: Dict) -> bool:
        """Inlined from CategorizationEngine.check_single_condition."""
        field = condition.get('field')
        operator = condition.get('operator')
        value = condition.get('value')
        case_sensitive = condition.get('case_sensitive', True)
        
        if field not in row:
            return False
        
        field_value = str(row[field])
        if not case_sensitive:
            field_value = field_value.lower()
            value = str(value).lower() if value is not None else ''
        
        if operator == 'equals':
            return field_value == str(value)
        elif operator == 'contains':
            return str(value) in field_value
        elif operator == 'starts_with':
            return field_value.startswith(str(value))
        elif operator == 'ends_with':
            return field_value.endswith(str(value))
        elif operator == 'regex':
            return bool(re.search(str(value), field_value))
        elif operator == 'greater_than':
            try:
                cleaned_field = self._legacy_parse_amount_for_comparison(field_value)
                return float(cleaned_field) > float(value)
            except (ValueError, TypeError):
                return False
        elif operator == 'less_than':
            try:
                cleaned_field = self._legacy_parse_amount_for_comparison(field_value)
                return float(cleaned_field) < float(value)
            except (ValueError, TypeError):
                return False
        elif operator == 'range':
            try:
                cleaned_field = self._legacy_parse_amount_for_comparison(field_value)
                field_num = float(cleaned_field)
                min_val = condition.get('min', float('-inf'))
                max_val = condition.get('max', float('inf'))
                return min_val <= field_num <= max_val
            except (ValueError, TypeError):
                return False
        return False

    def _legacy_extract_name(self, row: Dict, extract_config: Dict) -> str:
        """Inlined from CategorizationEngine.extract_name."""
        from_field = extract_config.get('from_field')
        pattern = extract_config.get('pattern')
        group = extract_config.get('group', 0)
        default = extract_config.get('default', 'Unknown')
        
        if not from_field or from_field not in row:
            return default
        
        try:
            match = re.search(pattern, str(row[from_field]), re.IGNORECASE)
            if match:
                extracted = match.group(group).strip()
                return extracted if extracted else default
            return default
        except Exception:
            return default

    def _legacy_clean_description(self, row: Dict, clean_config: Dict) -> str:
        """Inlined from CategorizationEngine.clean_description."""
        from_field = clean_config.get('from_field', 'DESCRIPTION')
        rules = clean_config.get('rules', [])
        default = clean_config.get('default', 'Transaction')
        
        if from_field not in row:
            return default
        
        description = str(row[from_field])
        
        try:
            for rule in rules:
                pattern = rule.get('pattern')
                replacement = rule.get('replacement', '')
                if pattern:
                    description = re.sub(pattern, replacement, description, flags=re.IGNORECASE | re.MULTILINE)
            
            description = re.sub(r'\s+', ' ', description).strip()
            return description if description else default
        except Exception:
            return default

    def _legacy_apply_default_categorization(self, cashew_row: Dict, default_rules: Dict = None) -> Dict:
        """Inlined from CategorizationEngine.apply_default_categorization."""
        if not default_rules:
            default_rules = {
                "positive_amount": "Income",
                "negative_amount": "Expense",
                "zero_amount": "Transfer"
            }
        
        try:
            amount = float(cashew_row['Amount'])
            if amount > 0:
                cashew_row['Category'] = default_rules.get('positive_amount', 'Income')
            elif amount < 0:
                cashew_row['Category'] = default_rules.get('negative_amount', 'Expense')
            else:
                cashew_row['Category'] = default_rules.get('zero_amount', 'Transfer')
        except (ValueError, TypeError):
            cashew_row['Category'] = 'Uncategorized'
        return cashew_row

    # --- End of Inlined Legacy Helper Methods ---

    def _inlined_legacy_transform(self, data: List[Dict], column_mapping: Dict[str, str],
                                 bank_name: str = "", categorization_rules: List[Dict] = None,
                                 default_category_rules: Dict = None, account_mapping: Dict = None,
                                 bank_rules_settings: Dict[str, bool] = None, config: Dict = None) -> List[Dict]:
        """
        Inlined legacy transformation logic, originally from LegacyTransformer.
        Uses inlined helper methods for parsing and categorization.
        """
        print(f"   [LegacyFallback] 🏦 Bank: {bank_name}")
        print(f"   [LegacyFallback] 📋 Input rows: {len(data)}")
        print(f"   [LegacyFallback] 🗺️ Column mapping: {column_mapping}")
        
        cashew_data = []
        for idx, row in enumerate(data):
            cashew_row = {'Date': '', 'Amount': '', 'Category': '', 'Title': '', 'Note': '', 'Account': bank_name}
            for cashew_col, source_col in column_mapping.items():
                if source_col in row and pd.notna(row[source_col]):
                    if cashew_col == 'Date':
                        cashew_row[cashew_col] = self._legacy_parse_date(str(row[source_col]))
                    elif cashew_col == 'Amount':
                        original_amount = str(row[source_col])
                        parsed_amount = self._legacy_parse_amount(original_amount)
                        cashew_row[cashew_col] = parsed_amount
                        if idx < 3: print(f"   [LegacyFallback] 💰 Row {idx} Amount: '{original_amount}' → '{parsed_amount}'")
                    elif cashew_col == 'Account' and account_mapping:
                        currency = str(row[source_col])
                        cashew_row[cashew_col] = account_mapping.get(currency, bank_name)
                    else:
                        cashew_row[cashew_col] = str(row[source_col])
            
            # Universal fallback logic using config-driven approach
            if config:
                # Use universal fallback for Date
                if not cashew_row.get('Date'):
                    fallback_date = self.resolve_field_with_fallback(row, 'Date', config)
                    if fallback_date:
                        cashew_row['Date'] = self._legacy_parse_date(fallback_date)
                        if idx < 3: print(f"   [LegacyFallback] ℹ️ Row {idx} Used fallback for Date: '{fallback_date}' -> '{cashew_row['Date']}'")

                # Use universal fallback for Title  
                if not cashew_row.get('Title'):
                    fallback_title = self.resolve_field_with_fallback(row, 'Title', config)
                    if fallback_title:
                        cashew_row['Title'] = str(fallback_title)
                        if idx < 3: print(f"   [LegacyFallback] ℹ️ Row {idx} Used fallback for Title: '{fallback_title}'")

            if idx < 3: print(f"   [LegacyFallback] 📋 Row {idx}: Date='{cashew_row['Date']}', Amount='{cashew_row['Amount']}', Title='{cashew_row['Title'][:50]}...'")
            
            if cashew_row['Amount'] and cashew_row['Amount'] != '0':
                cashew_row = self._legacy_apply_categorization_rules(
                    cashew_row, row, categorization_rules, default_category_rules
                )
                cashew_data.append(cashew_row)
            else:
                if idx < 5: print(f"   [LegacyFallback] ⚠️  Skipping row {idx}: Invalid/zero amount '{cashew_row['Amount']}'")
        
        print(f"   [LegacyFallback] ✅ Transformation complete: {len(cashew_data)} valid rows")
        return cashew_data