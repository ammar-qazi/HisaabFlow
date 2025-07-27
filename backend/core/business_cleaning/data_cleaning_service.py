"""
Data cleaning service for description cleaning and categorization
"""
from typing import Dict, List, Any, Optional
from pathlib import Path

from backend.infrastructure.config.unified_config_service import get_unified_config_service


class DataCleaningService:
    """Service focused on data cleaning and categorization"""
    
    def __init__(self):
        # Determine config directory path
        current_file_dir = Path(__file__).resolve().parent
        project_root = current_file_dir.parent.parent.parent
        config_dir_path = project_root / "configs"
        config_dir_path_str = str(config_dir_path)
        
        # Create unified config service instance
        self.config_service = get_unified_config_service(config_dir_path_str)
        
        print(f"ℹ [DataCleaningService] Initialized with unified config service")
    
    def apply_advanced_processing(self, transformed_data: List[Dict[str, Any]], 
                                 csv_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply comprehensive data cleaning pipeline
        
        Args:
            transformed_data: List of transformed transaction data
            csv_data_list: Original CSV data list with bank info
            
        Returns:
            List of cleaned transaction data
        """
        print(f"ℹ [DataCleaningService] Applying advanced processing pipeline...")
        
        # Step 1: Apply standard, config-based description cleaning
        data_after_standard_cleaning = self._apply_standard_description_cleaning(
            transformed_data, csv_data_list
        )
        
        # Step 2: Apply conditional description overrides from .conf files
        data_after_conditional_overrides = self._apply_conditional_description_overrides(
            data_after_standard_cleaning, csv_data_list
        )
        
        # Step 3: Re-apply keyword-based categorization using the fully cleaned descriptions
        data_after_recategorization = self._apply_keyword_categorization(
            data_after_conditional_overrides, csv_data_list
        )
        
        return data_after_recategorization
    
    def _apply_standard_description_cleaning(self, data: List[Dict[str, Any]], 
                                           csv_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply bank-specific description cleaning to data"""
        print(f"   Applying standard description cleaning...")
        print(f"      [DATA] Data rows to clean: {len(data)}")
        
        # DEBUG: Show sample data structure
        if data:
            print(f"         Sample row: {data[0]}")
        
        print(f"         CSV data list count: {len(csv_data_list)}")
        
        # Track cleaning results
        cleaned_count = 0
        bank_matches = {}
        
        for row_idx, row in enumerate(data):
            account = row.get('Account', '')
            bank_name = None
            
            print(f"         Row {row_idx + 1}: Account='{account}', Title='{row.get('Title', '')}'")
            
            # Find bank type based on Account name matching
            for csv_idx, csv_data in enumerate(csv_data_list):
                bank_info = csv_data.get('bank_info', {})
                detected_bank = bank_info.get('bank_name', bank_info.get('detected_bank'))
                print(f"            CSV {csv_idx}: detected_bank='{detected_bank}'")
                
                if detected_bank and detected_bank != 'unknown':
                    # Check if this transaction's account matches this bank's account
                    if self._account_matches_bank_config(account, detected_bank):
                        bank_name = detected_bank
                        print(f"            [SUCCESS] MATCH! Using bank: {bank_name}")
                        break
                    else:
                        print(f"            [NO MATCH] Account '{account}' doesn't match this bank")
            
            if bank_name:
                bank_matches[bank_name] = bank_matches.get(bank_name, 0) + 1
                
                original_title_for_row = row.get('Title', '')
                if '_original_title' not in row:
                    row['_original_title'] = original_title_for_row
                
                # Apply description cleaning for this bank
                cleaned_title = self.config_service.apply_description_cleaning(bank_name, original_title_for_row)
                if cleaned_title != original_title_for_row:
                    print(f"            CLEANED: '{original_title_for_row}' → '{cleaned_title}'")
                    row['Title'] = cleaned_title
                    cleaned_count += 1
                else:
                    print(f"            No change: '{original_title_for_row}'")
            else:
                print(f"         [ERROR] No bank match for account: '{account}'")
        
        print(f"      [DATA] Description cleaning summary:")
        print(f"            Total rows cleaned: {cleaned_count}")
        print(f"            Bank matches: {bank_matches}")
        
        return data
    
    def _apply_conditional_description_overrides(self, data: List[Dict[str, Any]], 
                                               csv_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply conditional description overrides defined in bank .conf files"""
        print(f"   Applying conditional description overrides...")
        conditional_changes_count = 0
        
        for row_idx, row in enumerate(data):
            account = row.get('Account', '')
            bank_name_for_row = None
            
            # Determine bank_name for the current row
            for csv_data in csv_data_list:
                bank_info = csv_data.get('bank_info', {})
                detected_bank = bank_info.get('bank_name', bank_info.get('detected_bank'))
                if detected_bank and detected_bank != 'unknown':
                    try:
                        bank_cfg_obj_check = self.config_service.get_bank_config(detected_bank)
                        if bank_cfg_obj_check and bank_cfg_obj_check.cashew_account == account:
                            bank_name_for_row = detected_bank
                            break
                    except Exception:
                        continue
            
            if not bank_name_for_row:
                continue
            
            bank_cfg_obj = self.config_service.get_bank_config(bank_name_for_row)
            if not bank_cfg_obj or not bank_cfg_obj.conditional_description_overrides:
                continue
            
            for rule in bank_cfg_obj.conditional_description_overrides:
                conditions_met = True
                amount_val = row.get('Amount')
                note_val = row.get('Note', '')
                current_title = row.get('Title', '')
                
                # Convert amount_val to float if it's a string
                if isinstance(amount_val, str):
                    try:
                        amount_val = float(amount_val)
                    except ValueError:
                        conditions_met = False
                        continue
                
                # Check conditions
                if 'if_amount_min' in rule and not (isinstance(amount_val, (int, float)) and amount_val >= float(rule['if_amount_min'])):
                    conditions_met = False
                if conditions_met and 'if_amount_max' in rule and not (isinstance(amount_val, (int, float)) and amount_val <= float(rule['if_amount_max'])):
                    conditions_met = False
                if conditions_met and 'if_amount_less_than' in rule and not (isinstance(amount_val, (int, float)) and amount_val < float(rule['if_amount_less_than'])):
                    conditions_met = False
                if conditions_met and 'if_amount_greater_than' in rule and not (isinstance(amount_val, (int, float)) and amount_val > float(rule['if_amount_greater_than'])):
                    conditions_met = False
                if conditions_met and 'if_amount_equals' in rule and not (isinstance(amount_val, (int, float)) and amount_val == float(rule['if_amount_equals'])):
                    conditions_met = False
                if conditions_met and 'if_note_equals' in rule and note_val != rule['if_note_equals']:
                    conditions_met = False
                if conditions_met and 'if_note_contains' in rule and rule['if_note_contains'].lower() not in note_val.lower():
                    conditions_met = False
                if conditions_met and 'if_description_contains' in rule and rule['if_description_contains'].lower() not in current_title.lower():
                    conditions_met = False
                
                if conditions_met:
                    new_title = rule.get('set_description')
                    if new_title and current_title != new_title:
                        rule_name_display = rule.get('name', rule.get('set_description', 'Unnamed Rule'))
                        print(f"            CONDITIONAL OVERRIDE (Row {row_idx + 1}, Bank: {bank_name_for_row}, Rule: {rule_name_display}): '{current_title}' → '{new_title}'")
                        row['Title'] = new_title
                        conditional_changes_count += 1
                        break
        
        if conditional_changes_count > 0:
            print(f"      Applied {conditional_changes_count} conditional override changes")
        
        return data
    
    def _apply_keyword_categorization(self, data: List[Dict[str, Any]], 
                                    csv_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply keyword-based categorization from .conf files using final descriptions"""
        print(f"   Applying keyword-based categorization (post-cleaning)...")
        categorized_count = 0
        
        for row_idx, row in enumerate(data):
            account = row.get('Account', '')
            bank_name_for_row = None
            
            # Determine bank_name for the current row
            for csv_data in csv_data_list:
                bank_info = csv_data.get('bank_info', {})
                detected_bank = bank_info.get('bank_name', bank_info.get('detected_bank'))
                if detected_bank and detected_bank != 'unknown':
                    try:
                        bank_cfg_obj_check = self.config_service.get_bank_config(detected_bank)
                        if bank_cfg_obj_check and self._account_matches_bank(bank_cfg_obj_check, account, csv_data_list):
                            bank_name_for_row = detected_bank
                            break
                    except Exception:
                        continue
            
            if not bank_name_for_row:
                continue
            
            description = row.get('Title', '')
            categorization_result = self.config_service.categorize_merchant_with_debug(bank_name_for_row, description)
            
            if categorization_result:
                category = categorization_result['category']
                pattern = categorization_result['pattern']
                source = categorization_result['source']
                rule_type = categorization_result['rule_type']
                
                # Log only if category changes or is newly set by this step
                if row.get('Category') != category:
                    print(f"            CATEGORIZED (Row {row_idx + 1}, Bank: {bank_name_for_row}): Desc='{description[:50]}...' → Category='{category}' [Pattern: '{pattern}' from {source} {rule_type}]")
                    row['Category'] = category
                    categorized_count += 1
        
        print(f"      Applied keyword categorization to {categorized_count} rows (post-cleaning)")
        return data
    
    def _account_matches_bank_config(self, account: str, bank_name: str) -> bool:
        """Check if account matches bank configuration"""
        try:
            bank_config = self.config_service.get_bank_config(bank_name)
            if bank_config:
                cashew_account = bank_config.cashew_account
                has_account_mapping = bool(bank_config.account_mapping)
                
                print(f"               Bank config cashew_account: '{cashew_account}'")
                
                # Check if this transaction's account matches this bank's account
                if cashew_account and account == cashew_account:
                    # Single account bank - direct match
                    print(f"               [MATCH] Account '{account}' matches cashew_account '{cashew_account}'")
                    return True
                elif has_account_mapping:
                    # Multi-currency bank - check account_mapping
                    account_mapping = bank_config.account_mapping
                    if account in account_mapping.values():
                        print(f"               [MATCH] Account '{account}' found in account_mapping")
                        return True
                    else:
                        print(f"               [NO MATCH] Account '{account}' not in account_mapping")
                        return False
                else:
                    print(f"               [NO MATCH] Account '{account}' doesn't match cashew_account '{cashew_account}'")
                    return False
        except Exception as e:
            print(f"            [WARNING] Error getting bank config: {e}")
            return False
        
        return False
    
    def _account_matches_bank(self, bank_config, account: str, csv_data_list: List[Dict[str, Any]]) -> bool:
        """Check if account matches bank configuration for both single and multi-currency banks"""
        # Tier 1: Single-currency banks (cashew_account match)
        if bank_config.cashew_account and bank_config.cashew_account == account:
            return True
        
        # Tier 2: Multi-currency banks (account_mapping values match)
        if bank_config.account_mapping:
            for currency, account_name in bank_config.account_mapping.items():
                if account_name == account:
                    return True
        
        return False