"""
Data transformation service for converting parsed data to Cashew format
"""
from pathlib import Path
import os
import sys
import json

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from enhanced_csv_parser import EnhancedCSVParser
    from bank_detection import BankDetector, BankConfigManager
    from transfer_detection.main_detector import TransferDetector
    from transfer_detection.config_manager import ConfigurationManager
except ImportError:
    # Fallback path for import issues
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, backend_path)
    from enhanced_csv_parser import EnhancedCSVParser
    from bank_detection import BankDetector, BankConfigManager
    from transfer_detection.main_detector import TransferDetector
    from transfer_detection.config_manager import ConfigurationManager


class TransformationService:
    """Service for transforming data to Cashew format"""
    
    def __init__(self):
        self.enhanced_parser = EnhancedCSVParser()
        self.bank_config_manager = BankConfigManager()
        self.bank_detector = BankDetector(self.bank_config_manager)

        # Determine the config directory path.
        # This should ideally be an absolute path or a path reliably relative to the project root.
        # Assuming 'configs' directory is at the project root.
        current_file_dir = Path(__file__).resolve().parent
        # Path to /backend/services/ -> /backend/ -> / (project root)
        project_root = current_file_dir.parent.parent 
        config_dir_path = project_root / "configs"
        config_dir_path_str = str(config_dir_path)

        # Create a single, shared ConfigurationManager instance for transfer detection logic
        self.shared_transfer_config = ConfigurationManager(config_dir=config_dir_path_str)
        
        self.transfer_detector = TransferDetector(config_manager=self.shared_transfer_config)
    
    def transform_single_data(self, data: list, column_mapping: dict, bank_name: str = "", 
                            categorization_rules: list = None, default_category_rules: dict = None,
                            account_mapping: dict = None):
        """
        Transform single dataset to Cashew format
        
        Args:
            data: List of data rows
            column_mapping: Column mapping dictionary
            bank_name: Bank name for transformation
            categorization_rules: Optional categorization rules
            default_category_rules: Optional default category rules
            account_mapping: Optional account mapping
            
        Returns:
            dict: Transformation result
        """
        try:
            if categorization_rules or default_category_rules:
                result = self.enhanced_parser.transform_to_cashew(
                    data, 
                    column_mapping, 
                    bank_name,
                    categorization_rules,
                    default_category_rules,
                    account_mapping
                )
            else:
                result = self.enhanced_parser.transform_to_cashew(
                    data, 
                    column_mapping, 
                    bank_name
                )
            
            return {
                "success": True,
                "data": result,
                "row_count": len(result)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def transform_multi_csv_data(self, raw_data: dict):
        """
        Transform multi-CSV data to Cashew format
        
        Args:
            raw_data: Raw request data from frontend
            
        Returns:
            dict: Multi-CSV transformation result
        """
        print(f"🔄 Multi-CSV transform request received")
        
        try:
            print(f"🗂️ Request keys: {list(raw_data.keys())}")
            
            # Extract data from frontend format using bank-agnostic detection
            data, column_mapping, bank_name = self._extract_transform_data_per_bank(raw_data)
            
            print(f"📈 Final data length: {len(data)}")
            print(f"🏦 Final bank name: {bank_name}")
            print(f"🗂️ Final column mapping: {column_mapping}")
            
            # Get categorization rules
            categorization_rules = raw_data.get('categorization_rules')
            default_category_rules = raw_data.get('default_category_rules')
            account_mapping = raw_data.get('account_mapping')
            
            # Show sample data for debugging
            if data:
                print(f"📄 Sample data (first row): {data[0] if data else 'none'}")
            
            # Transform data
            if categorization_rules or default_category_rules:
                print(f"📋 Using enhanced transformation with categorization rules")
                result = self.enhanced_parser.transform_to_cashew(
                    data, 
                    column_mapping, 
                    bank_name,
                    categorization_rules,
                    default_category_rules,
                    account_mapping
                )
            else:
                print(f"📋 Using basic transformation")
                result = self.enhanced_parser.transform_to_cashew(
                    data, 
                    column_mapping, 
                    bank_name
                )
            
            print(f"✅ Transformation successful: {len(result)} rows transformed")
            if result:
                print(f"📄 Sample result (first row): {result[0] if result else 'none'}")
            
            # Apply description cleaning and transfer detection
            print(f"\n🧹 Applying description cleaning and transfer detection...")
            enhanced_result, transfer_analysis = self._apply_advanced_processing(result, raw_data)
            
            print(f"🔍 Transfer detection summary:")
            print(f"   📊 Transfer pairs found: {transfer_analysis['summary']['transfer_pairs_found']}")
            print(f"   🔄 Potential transfers: {transfer_analysis['summary']['potential_transfers']}")
            
            # Frontend expects 'transformed_data' and 'transfer_analysis' format
            response_data = {
                "success": True,
                "transformed_data": enhanced_result,
                "transformation_summary": {
                    "total_transactions": len(enhanced_result),
                    "bank_name": bank_name,
                    "data_source": "multi-csv"
                },
                "transfer_analysis": transfer_analysis,
                # Legacy fields for compatibility
                "data": enhanced_result,
                "row_count": len(enhanced_result),
                "bank_name": bank_name
            }
            
            print(f"📦 Sending response with {len(result)} transformed_data rows")
            return response_data
            
        except Exception as e:
            print(f"❌ Multi-CSV transform exception: {str(e)}")
            import traceback
            print(f"📖 Full traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_transform_data_per_bank(self, raw_data: dict):
        """Extract transformation data using PRE-DETECTED bank info from parse endpoints"""
        
        # Handle different frontend data formats
        if 'csv_data_list' in raw_data:
            return self._process_multi_csv_format(raw_data)
        else:
            # Standard single-file format
            print(f"📋 Standard format detected")
            data = raw_data.get('data', [])
            column_mapping = raw_data.get('column_mapping', {})
            bank_name = raw_data.get('bank_name', '')
            
            return data, column_mapping, bank_name
    
    def _process_multi_csv_format(self, raw_data: dict):
        """Process multi-CSV format data"""
        print(f"📋 Frontend format detected: csv_data_list")
        csv_data_list = raw_data.get('csv_data_list', [])
        print(f"📈 CSV data list length: {len(csv_data_list)}")
        
        if not csv_data_list:
            print(f"⚠️ No CSV data found in csv_data_list")
            return [], {}, ''
        
        return self._process_csv_data_list(csv_data_list)
    
    def _process_csv_data_list(self, csv_data_list: list):
        """Process each CSV file using PRE-CLEANED data"""
        all_transformed_data = []
        
        for csv_index, csv_data in enumerate(csv_data_list):
            print(f"\n🗂️ Processing CSV {csv_index + 1}/{len(csv_data_list)}")
            
            # Get data from this CSV
            csv_file_data = csv_data.get('data', [])
            filename = csv_data.get('filename', f'file_{csv_index + 1}.csv')
            bank_info = csv_data.get('bank_info', {})
            
            if not csv_file_data:
                print(f"   ⚠️ No data in CSV {csv_index + 1}")
                continue
            
            print(f"   📊 CSV has {len(csv_file_data)} rows")
            print(f"   📁 Filename: {filename}")
            
            # Log pre-detected bank info
            detected_bank = self._get_detected_bank(bank_info)
            print(f"   🏦 PRE-DETECTED bank: {detected_bank}")
            
            # Data is already cleaned and standardized
            print(f"   ✅ Using pre-cleaned data as-is")
            
            # Get Account name from bank configuration
            account_name = self._get_account_name(bank_info, filename)
            
            # Update Account field for each row
            for row in csv_file_data:
                row['Account'] = account_name
            
            print(f"   ✅ Account field '{account_name}' set for all {len(csv_file_data)} rows")
            
            # Add cleaned data to combined results
            all_transformed_data.extend(csv_file_data)
        
        print(f"\n📈 Combined data from all CSVs: {len(all_transformed_data)} total rows")
        
        # Build a more comprehensive mapping to guide transform_to_cashew.
        # Data in all_transformed_data is already standardized from the /parse endpoint's cleaning.
        # This mapping tells transform_to_cashew which fields to prioritize and keep.
        combined_column_mapping = {
            # Core Cashew fields
            'Date': 'Date',
            'Amount': 'Amount',
            'Title': 'Title',
            'Note': 'Note',
            'Account': 'Account',
            'Category': 'Category' # Ensure Category is handled/created
        }
        
        # Add other known standardized fields that should be preserved,
        # especially those needed for transfer detection.
        # These fields are already present with these names in all_transformed_data
        # if they came from the cleaning step during parsing.
        fields_to_preserve_if_exist = [
            'ExchangeToAmount', 
            'ExchangeToCurrency', 
            'Balance', # Will be dropped by export_service anyway, but keep for internal processing
            'Currency', # Original currency if different from Account (e.g. Wise files)
            # Add other potentially useful standardized fields if needed by transfer detection:
            # 'TransferwiseId', 'RunningBalance', 'TotalFees' 
        ]
        if all_transformed_data: # Check if there's any data to inspect
            # Instead of only checking first row, check ALL fields across ALL rows
            all_fields_present_in_data = set()
            for row in all_transformed_data:
                all_fields_present_in_data.update(row.keys())

            # Preserve fields from fields_to_preserve_if_exist if they exist anywhere in the data
            for field in fields_to_preserve_if_exist:
                if field in all_fields_present_in_data:
                    # Add to mapping if not already a core Cashew field (to avoid accidental overwrite, though unlikely here)
                    if field not in combined_column_mapping:
                        combined_column_mapping[field] = field # Map to itself to preserve
        
        combined_bank_name = 'multi_bank_combined'
        
        return all_transformed_data, combined_column_mapping, combined_bank_name
    
    def _get_detected_bank(self, bank_info: dict):
        """Extract detected bank from bank info"""
        if bank_info:
            detected_bank = bank_info.get('detected_bank', 'unknown')
            confidence = bank_info.get('confidence', 0.0)
            return f"{detected_bank} (confidence={confidence:.2f})"
        return 'unknown'
    
    def _get_account_name(self, bank_info: dict, filename: str):
        """Get account name from bank configuration or filename"""
        account_name = 'Unknown'
        
        if bank_info and 'detected_bank' in bank_info:
            detected_bank = bank_info['detected_bank']
            if detected_bank != 'unknown':
                try:
                    bank_config = self.bank_config_manager.get_bank_config(detected_bank)
                    if bank_config and bank_config.has_section('bank_info'):
                        cashew_account = bank_config.get('bank_info', 'cashew_account', fallback=None)
                        if cashew_account:
                            account_name = cashew_account
                            print(f"   🏦 Using cashew_account from {detected_bank} config: '{account_name}'")
                        else:
                            print(f"   ⚠️  No cashew_account in {detected_bank} config")
                    else:
                        print(f"   ⚠️  Could not load config for {detected_bank}")
                except Exception as e:
                    print(f"   ⚠️  Error loading config for {detected_bank}: {e}")
        
        # Fallback to filename if config loading failed
        if account_name == 'Unknown':
            account_name = filename.replace('.csv', '').replace('_', ' ').replace('-', ' ').title()
            print(f"   🏦 Using filename fallback: '{account_name}'")
        
        return account_name
    
    def _apply_advanced_processing(self, transformed_data: list, raw_data: dict):
        """Apply description cleaning and transfer detection to transformed data"""
        
        # Step 1: Apply standard, config-based description cleaning
        data_after_standard_cleaning = self._apply_standard_description_cleaning(transformed_data, raw_data)
        
        # Step 1.5: Apply conditional description overrides from .conf files
        data_after_conditional_overrides = self._apply_conditional_description_overrides(data_after_standard_cleaning, raw_data)
        
        # Step 2: Re-apply keyword-based categorization using the fully cleaned descriptions
        data_after_recategorization = self._apply_keyword_categorization(data_after_conditional_overrides, raw_data)
        
        # Step 3: Run transfer detection
        transfer_analysis = self._run_transfer_detection(data_after_recategorization, raw_data)
        
        # Use the transactions processed by the detector (which have _transaction_index)
        # for the final categorization step.
        transactions_for_final_cat = transfer_analysis.get('processed_transactions', data_after_recategorization)
        
        # Step 4: Apply transfer-specific categorization (e.g., "Balance Correction")
        final_data_with_transfer_cats = self._apply_transfer_specific_categorization(transactions_for_final_cat, transfer_analysis)
        
        return final_data_with_transfer_cats, transfer_analysis # transfer_analysis now also contains processed_transactions
    
    def _apply_standard_description_cleaning(self, data: list, raw_data: dict):
        """Apply bank-specific description cleaning to data"""
        print(f"🧹 Applying description cleaning...")
        print(f"   📊 Data rows to clean: {len(data)}")
        
        # DEBUG: Print the bank_configs from the shared_transfer_config
        # print(f"   🐞 DEBUG: self.shared_transfer_config.bank_configs: {self.shared_transfer_config.bank_configs}")
        # print(f"   🐞 DEBUG: self.shared_transfer_config.list_configured_banks(): {self.shared_transfer_config.list_configured_banks()}")
        # print(f"   🐞 DEBUG: self.shared_transfer_config.config_dir: {self.shared_transfer_config.config_dir}")

        # DEBUG: Show sample data structure
        if data:
            print(f"   📄 Sample row: {data[0]}")
        
        # Get CSV data list to determine bank types for each transaction
        csv_data_list = raw_data.get('csv_data_list', [])
        print(f"   📂 CSV data list count: {len(csv_data_list)}")
        
        # Track cleaning results
        cleaned_count = 0
        bank_matches = {}
        
        for row_idx, row in enumerate(data):
            account = row.get('Account', '')
            bank_name = None
            
            print(f"   🔍 Row {row_idx + 1}: Account='{account}', Title='{row.get('Title', '')}'")
            
            # Find bank type based on Account name
            for csv_idx, csv_data in enumerate(csv_data_list):
                bank_info = csv_data.get('bank_info', {})
                detected_bank = bank_info.get('detected_bank')
                print(f"      📁 CSV {csv_idx}: detected_bank='{detected_bank}'")
                
                if detected_bank and detected_bank != 'unknown':
                    # Get cashew account name for this bank
                    try:
                        bank_config = self.bank_config_manager.get_bank_config(detected_bank)
                        if bank_config and bank_config.has_section('bank_info'):
                            cashew_account = bank_config.get('bank_info', 'cashew_account', fallback=None)
                            print(f"         🏦 Bank config cashew_account: '{cashew_account}'")
                            if cashew_account == account:
                                bank_name = detected_bank
                                print(f"         ✅ MATCH! Using bank: {bank_name}")
                                break
                    except Exception as e:
                        print(f"         ⚠️  Error getting bank config: {e}")
                        continue
            
            if bank_name:
                bank_matches[bank_name] = bank_matches.get(bank_name, 0) + 1
                
                original_title_for_row = row.get('Title', '')
                if '_original_title' not in row: # Store original title only once
                    row['_original_title'] = original_title_for_row

                # Apply description cleaning for this bank
                cleaned_title = self.shared_transfer_config.apply_description_cleaning(bank_name, original_title_for_row)
                if cleaned_title != original_title_for_row:
                    print(f"      🧹 CLEANED: '{original_title_for_row}' → '{cleaned_title}'")
                    row['Title'] = cleaned_title
                    cleaned_count += 1
                else:
                    print(f"      ⚪ No change: '{original_title_for_row}'")
            else:
                print(f"      ❌ No bank match for account: '{account}'")
        
        print(f"   📊 Description cleaning summary:")
        print(f"      🧹 Total rows cleaned: {cleaned_count}")
        print(f"      🏦 Bank matches: {bank_matches}")
        
        return data
    
    def _apply_conditional_description_overrides(self, data: list, raw_data: dict) -> list:
        """Apply conditional description overrides defined in bank .conf files."""
        print(f"🧠 Applying conditional description overrides...")
        conditional_changes_count = 0
        
        csv_data_list = raw_data.get('csv_data_list', [])

        for row_idx, row in enumerate(data):
            account = row.get('Account', '')
            bank_name_for_row = None

            # Determine bank_name for the current row (similar to _apply_standard_description_cleaning)
            for csv_data in csv_data_list:
                bank_info = csv_data.get('bank_info', {})
                detected_bank = bank_info.get('detected_bank')
                if detected_bank and detected_bank != 'unknown':
                    try:
                        # Use self.shared_transfer_config to get BankConfig object
                        bank_cfg_obj_check = self.shared_transfer_config.get_bank_config(detected_bank)
                        if bank_cfg_obj_check and bank_cfg_obj_check.cashew_account == account:
                            bank_name_for_row = detected_bank
                            break
                    except Exception: # pylint: disable=broad-except
                        continue # Error accessing config, try next CSV's bank info
            
            if not bank_name_for_row:
                continue

            bank_cfg_obj = self.shared_transfer_config.get_bank_config(bank_name_for_row)
            if not bank_cfg_obj or not bank_cfg_obj.conditional_description_overrides:
                continue

            for rule in bank_cfg_obj.conditional_description_overrides:
                conditions_met = True
                amount_val = row.get('Amount') 
                note_val = row.get('Note', '')
                current_title = row.get('Title', '')

                # Check conditions
                if 'if_amount_min' in rule and not (isinstance(amount_val, (int, float)) and amount_val >= rule['if_amount_min']):
                    conditions_met = False
                if conditions_met and 'if_amount_max' in rule and not (isinstance(amount_val, (int, float)) and amount_val <= rule['if_amount_max']):
                    conditions_met = False
                if conditions_met and 'if_amount_less_than' in rule and not (isinstance(amount_val, (int, float)) and amount_val < rule['if_amount_less_than']):
                    conditions_met = False
                if conditions_met and 'if_amount_greater_than' in rule and not (isinstance(amount_val, (int, float)) and amount_val > rule['if_amount_greater_than']):
                    conditions_met = False
                if conditions_met and 'if_amount_equals' in rule and not (isinstance(amount_val, (int, float)) and amount_val == rule['if_amount_equals']):
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
                        rule_name_display = rule.get('name', rule.get('set_description', 'Unnamed Rule')) # Get a display name for the rule
                        print(f"      ✨ CONDITIONAL OVERRIDE (Row {row_idx + 1}, Bank: {bank_name_for_row}, Rule: {rule_name_display}): '{current_title}' → '{new_title}'")
                        row['Title'] = new_title
                        conditional_changes_count += 1
                        break # Apply only the first matching conditional rule for this row
        
        if conditional_changes_count > 0:
            print(f"   🧠 Applied {conditional_changes_count} conditional override changes.")
        return data

    def _apply_keyword_categorization(self, data: list, raw_data: dict) -> list:
        """Apply keyword-based categorization from .conf files using final descriptions."""
        print(f"🏷️ Applying keyword-based categorization (post-cleaning)...")
        categorized_count = 0
        
        csv_data_list = raw_data.get('csv_data_list', [])

        for row_idx, row in enumerate(data):
            account = row.get('Account', '')
            # original_category = row.get('Category', '') # Keep if needed for more complex logic
            
            bank_name_for_row = None
            # Determine bank_name for the current row
            for csv_data in csv_data_list:
                bank_info = csv_data.get('bank_info', {})
                detected_bank = bank_info.get('detected_bank')
                if detected_bank and detected_bank != 'unknown':
                    try:
                        bank_cfg_obj_check = self.shared_transfer_config.get_bank_config(detected_bank)
                        if bank_cfg_obj_check and bank_cfg_obj_check.cashew_account == account:
                            bank_name_for_row = detected_bank
                            break
                    except Exception: # pylint: disable=broad-except
                        continue
            
            if not bank_name_for_row:
                continue

            description = row.get('Title', '') # Use the 'Title' field which holds the cleaned description
            # Use shared_transfer_config as it holds the BankConfig objects with categorization_rules
            category = self.shared_transfer_config.categorize_merchant(bank_name_for_row, description)
            
            if category:
                # Log only if category changes or is newly set by this step
                if row.get('Category') != category: 
                    print(f"      🏷️ CATEGORIZED (Row {row_idx + 1}, Bank: {bank_name_for_row}): Desc='{description[:50]}...' → Category='{category}'")
                    row['Category'] = category
                    categorized_count += 1
        print(f"   🏷️ Applied keyword categorization to {categorized_count} rows (post-cleaning).")
        return data

    def _run_transfer_detection(self, data: list, raw_data: dict):
        """Run transfer detection on the processed data"""
        print(f"🔍 Running transfer detection...")
        print(f"   📊 Input data rows: {len(data)}")
        
        # DEBUG: Show sample data structure
        if data:
            print(f"   📄 Sample row keys: {list(data[0].keys())}")
            print(f"   📄 Sample row: {data[0]}")
        
        # Convert data to the format expected by transfer detector
        csv_data_list = []
        
        # Group data by account/bank for transfer detection
        accounts = {}
        for row in data:
            account = row.get('Account', 'Unknown')
            if account not in accounts:
                accounts[account] = []
            accounts[account].append(row)
        
        print(f"   🏦 Accounts found: {list(accounts.keys())}")
        
        # Create csv_data_list format for transfer detector
        for account, rows in accounts.items():
            csv_data = {
                'data': rows,
                'file_name': f'{account}.csv',
                'template_config': {}
            }
            csv_data_list.append(csv_data)
            print(f"      📁 Account '{account}': {len(rows)} transactions")
        
        print(f"   📂 Prepared {len(csv_data_list)} CSV data items for transfer detection")
        
        try:
            # Run transfer detection
            print(f"   🔍 Calling TransferDetector.detect_transfers()...")
            detection_result = self.transfer_detector.detect_transfers(csv_data_list)
            
            print(f"   📊 Transfer detection results:")
            print(f"      📋 Summary: {detection_result.get('summary', {})}")
            print(f"      🔄 Transfer pairs: {len(detection_result.get('transfers', []))}")
            print(f"      💭 Potential transfers: {len(detection_result.get('potential_transfers', []))}")
            
            return {
                "summary": detection_result.get('summary', {}),
                "transfers": detection_result.get('transfers', []),
                "potential_transfers": detection_result.get('potential_transfers', []),
                "processed_transactions": detection_result.get('processed_transactions', data), # Pass back the processed list
                "conflicts": detection_result.get('conflicts', []), # Ensure these are also passed through
                "flagged_transactions": detection_result.get('flagged_transactions', []) # Ensure these are also passed through
            }
        except Exception as e:
            print(f"⚠️ Transfer detection error: {e}")
            import traceback
            print(f"📖 Transfer detection traceback: {traceback.format_exc()}")
            return {
                "summary": {
                    "transfer_pairs_found": 0,
                    "potential_transfers": 0,
                    "conflicts": 0,
                    "flagged_for_review": 0
                },
                "transfers": [],
                "processed_transactions": data, # Fallback to original data on error
                "potential_transfers": [],
                "conflicts": [],
                "flagged_transactions": []
            }

    
    def _apply_transfer_specific_categorization(self, data: list, transfer_analysis: dict) -> list:
        """Apply configured category to detected transfers and update notes."""
        print(f"🏷️ Applying transfer categorization...")
        
        transfer_pairs = transfer_analysis.get('transfers', [])
        # Get the configured category for transfers from the shared ConfigurationManager
        transfer_category = self.shared_transfer_config.get_default_transfer_category()
        print(f"   Using category '{transfer_category}' for transfer pairs.")

        if not transfer_pairs:
            print("   No transfer pairs found to categorize.")
            return data
        
        # Create a lookup for transfer transactions by their _transaction_index
        # Store type (outgoing/incoming), pair_id, and match_strategy for note generation
        transfer_details_by_index = {}
        for pair in transfer_pairs:
            outgoing_tx = pair.get('outgoing')
            incoming_tx = pair.get('incoming')
            pair_id = pair.get('pair_id', 'unknown_pair')
            match_strategy = pair.get('match_strategy', 'unknown_strategy')

            if outgoing_tx and '_transaction_index' in outgoing_tx:
                transfer_details_by_index[outgoing_tx['_transaction_index']] = {
                    'type': 'outgoing',
                    'pair_id': pair_id,
                    'match_strategy': match_strategy
                }
            if incoming_tx and '_transaction_index' in incoming_tx:
                transfer_details_by_index[incoming_tx['_transaction_index']] = {
                    'type': 'incoming',
                    'pair_id': pair_id,
                    'match_strategy': match_strategy
                }
        
        if not transfer_details_by_index:
            print("   No transactions with _transaction_index found in transfer pairs. Cannot apply categorization.")
            return data

        matches_applied = 0
        for row in data:
            row_transaction_index = row.get('_transaction_index') # Ensure _transaction_index is in your `data` rows
            if row_transaction_index is not None and row_transaction_index in transfer_details_by_index:
                details = transfer_details_by_index[row_transaction_index]
                row['Category'] = transfer_category # Use configured category
                
                current_note = row.get('Note', '')
                note_suffix = f" | Transfer {details['type']} (Pair: {details['pair_id']}, Strategy: {details['match_strategy']})"
                
                # Avoid appending if already present (e.g., if this function is called multiple times)
                if note_suffix not in current_note:
                    row['Note'] = (current_note + note_suffix).strip().lstrip(" | ")
                
                matches_applied += 1
        
        print(f"   ✅ Applied '{transfer_category}' category and updated notes for {matches_applied} transactions.")
        return data
