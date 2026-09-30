"""
Data cleaning service for description cleaning and categorization
"""
from typing import Dict, List, Any
from pathlib import Path

from backend.infrastructure.config.unified_config_service import get_unified_config_service
from backend.shared.utils.bank_lookup import bank_for_row
import logging

logger = logging.getLogger(__name__)


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
        
        logger.debug(f"ℹ [DataCleaningService] Initialized with unified config service")
    
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
        logger.debug(f"ℹ [DataCleaningService] Applying advanced processing pipeline...")
        
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
        logger.debug(f"   Applying standard description cleaning...")
        logger.debug(f"      [DATA] Data rows to clean: {len(data)}")
        
        # DEBUG: Show sample data structure
        if data:
            pass
        
        logger.debug(f"         CSV data list count: {len(csv_data_list)}")
        
        # Track cleaning results
        cleaned_count = 0
        bank_matches = {}
        
        for row_idx, row in enumerate(data):
            account = row.get('Account', '')
            bank_name = bank_for_row(row, csv_data_list, self.config_service)
            
            if bank_name:
                bank_matches[bank_name] = bank_matches.get(bank_name, 0) + 1
                
                original_title_for_row = row.get('Title', '')
                if '_original_title' not in row:
                    row['_original_title'] = original_title_for_row
                
                # Apply description cleaning for this bank
                cleaned_title = self.config_service.apply_description_cleaning(bank_name, original_title_for_row)
                if cleaned_title != original_title_for_row:
                    row['Title'] = cleaned_title
                    cleaned_count += 1
                else:
                    pass
            else:
                logger.debug(f"         No bank match for account: '{account}'")
        
        logger.debug(f"      [DATA] Description cleaning summary:")
        logger.debug(f"            Total rows cleaned: {cleaned_count}")
        logger.debug(f"            Bank matches: {bank_matches}")
        
        return data
    
    def _apply_conditional_description_overrides(self, data: List[Dict[str, Any]], 
                                               csv_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply conditional description overrides defined in bank .conf files"""
        logger.debug(f"   Applying conditional description overrides...")
        conditional_changes_count = 0
        
        for row_idx, row in enumerate(data):
            bank_name_for_row = bank_for_row(row, csv_data_list, self.config_service)
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
                        row['Title'] = new_title
                        conditional_changes_count += 1
                        break
        
        if conditional_changes_count > 0:
            logger.debug(f"      Applied {conditional_changes_count} conditional override changes")
        
        return data
    
    def _apply_keyword_categorization(self, data: List[Dict[str, Any]], 
                                    csv_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply keyword-based categorization from .conf files using final descriptions"""
        logger.debug(f"   Applying keyword-based categorization (post-cleaning)...")
        categorized_count = 0
        
        for row_idx, row in enumerate(data):
            bank_name_for_row = bank_for_row(row, csv_data_list, self.config_service)
            if not bank_name_for_row:
                continue
            
            description = row.get('Title', '')
            categorization_result = self.config_service.categorize_merchant_with_debug(bank_name_for_row, description)
            
            if categorization_result:
                category = categorization_result['category']
                
                # Log only if category changes or is newly set by this step
                if row.get('Category') != category:
                    row['Category'] = category
                    categorized_count += 1
        
        logger.debug(f"      Applied keyword categorization to {categorized_count} rows (post-cleaning)")
        return data
    
