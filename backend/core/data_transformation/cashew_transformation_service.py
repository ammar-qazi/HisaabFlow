"""
Cashew transformation service for converting parsed data to Cashew format
"""
from pathlib import Path
from typing import Dict, List, Any, Optional

from backend.services.cashew_transformer import CashewTransformer
from backend.bank_detection import BankDetector
from backend.shared.config.unified_config_service import get_unified_config_service


class CashewTransformationService:
    """Service focused on Cashew format transformation"""
    
    def __init__(self):
        self.transformer = CashewTransformer()
        self.config_service = get_unified_config_service()
        self.bank_detector = BankDetector(self.config_service)
        
        print(f"ℹ [CashewTransformationService] Initialized with CashewTransformer")
    
    def transform_single_data(self, data: List[Dict[str, Any]], column_mapping: Dict[str, str], 
                             bank_name: str = "", categorization_rules: Optional[List] = None, 
                             default_category_rules: Optional[Dict] = None,
                             account_mapping: Optional[Dict] = None, 
                             config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Transform single dataset to Cashew format
        
        Args:
            data: List of data rows
            column_mapping: Column mapping dictionary
            bank_name: Bank name for transformation
            categorization_rules: Optional categorization rules
            default_category_rules: Optional default category rules
            account_mapping: Optional account mapping
            config: Bank configuration for fallback logic
            
        Returns:
            dict: Transformation result
        """
        print(f"ℹ [CashewTransformationService] transform_single_data called for bank: {bank_name}")
        
        try:
            if categorization_rules or default_category_rules:
                result = self.transformer.transform_to_cashew(
                    data, 
                    column_mapping, 
                    bank_name,
                    categorization_rules,
                    default_category_rules,
                    account_mapping,
                    config=config
                )
            else:
                result = self.transformer.transform_to_cashew(
                    data, 
                    column_mapping, 
                    bank_name,
                    config=config
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
    
    def transform_multi_csv_data(self, csv_data_list: List[Dict[str, Any]], 
                                categorization_rules: Optional[List] = None,
                                default_category_rules: Optional[Dict] = None,
                                account_mapping: Optional[Dict] = None,
                                bank_configs: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Transform multi-CSV data to Cashew format
        
        Args:
            csv_data_list: List of CSV data for transformation
            categorization_rules: Optional categorization rules
            default_category_rules: Optional default category rules
            account_mapping: Optional account mapping
            bank_configs: Bank configurations for fallback logic
            
        Returns:
            dict: Multi-CSV transformation result
        """
        print(f"ℹ [CashewTransformationService] transform_multi_csv_data called")
        
        try:
            # Extract data from frontend format using bank-agnostic detection
            data, column_mapping, bank_name = self._extract_transform_data_per_bank(csv_data_list)
            
            print(f"   Final data length: {len(data)}")
            print(f"   Final bank name: {bank_name}")
            print(f"   Final column mapping: {column_mapping}")
            
            # Extract account_mapping from bank configs if not provided
            if not account_mapping and bank_configs:
                account_mapping = self._extract_account_mapping(bank_configs)
            
            # Show sample data for debugging
            if data:
                print(f"   Sample data (first row): {data[0] if data else 'none'}")
            
            # Transform data
            if categorization_rules or default_category_rules:
                print(f"ℹ [CashewTransformationService] Using transformation with categorization rules")
                result = self.transformer.transform_to_cashew(
                    data, 
                    column_mapping, 
                    bank_name,
                    categorization_rules,
                    default_category_rules,
                    account_mapping,
                    config=bank_configs
                )
            else:
                print(f"ℹ [CashewTransformationService] Using basic transformation")
                result = self.transformer.transform_to_cashew(
                    data, 
                    column_mapping, 
                    bank_name,
                    account_mapping=account_mapping,
                    config=bank_configs
                )
            
            print(f"[SUCCESS] Transformation successful: {len(result)} rows transformed")
            if result:
                print(f"   Sample result (first row): {result[0] if result else 'none'}")
            
            return {
                "success": True,
                "data": result,
                "row_count": len(result)
            }
            
        except Exception as e:
            print(f"[ERROR] Multi-CSV transform exception: {str(e)}")
            import traceback
            print(f"   Full traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_transform_data_per_bank(self, csv_data_list: List[Dict[str, Any]]):
        """Extract transformation data using PRE-DETECTED bank info from parse endpoints"""
        print(f"   Processing csv_data_list with {len(csv_data_list)} items")
        
        if not csv_data_list:
            print(f"[WARNING] No CSV data found in csv_data_list")
            return [], {}, ''
        
        return self._process_csv_data_list(csv_data_list)
    
    def _process_csv_data_list(self, csv_data_list: List[Dict[str, Any]]):
        """Process each CSV file using PRE-CLEANED data"""
        all_transformed_data = []
        
        for csv_index, csv_data in enumerate(csv_data_list):
            print(f"\n   Processing CSV {csv_index + 1}/{len(csv_data_list)}")
            
            # Get data from this CSV
            csv_file_data = csv_data.get('data', [])
            filename = csv_data.get('filename', f'file_{csv_index + 1}.csv')
            bank_info = csv_data.get('bank_info', {})
            
            if not csv_file_data:
                print(f"      [WARNING] No data in CSV {csv_index + 1}")
                continue
            
            print(f"      [DATA] CSV has {len(csv_file_data)} rows")
            print(f"      Filename: {filename}")
            
            # Log pre-detected bank info
            detected_bank = self._get_detected_bank(bank_info)
            print(f"      PRE-DETECTED bank: {detected_bank}")
            
            # Data is already cleaned and standardized
            print(f"      [SUCCESS] Using pre-cleaned data as-is")
            
            # Get Account name from bank configuration
            base_account_name = self._get_account_name(bank_info, filename)
            
            # Update Account field and add bank source for each row
            detected_bank_name = bank_info.get('bank_name', bank_info.get('detected_bank', 'unknown'))
            for row in csv_file_data:
                # For multi-currency banks like Wise, map account name based on currency
                final_account_name = self._map_account_by_currency(detected_bank_name, base_account_name, row, filename)
                row['Account'] = final_account_name
                row['_source_bank'] = detected_bank_name  # For bank-specific account mapping
            
            print(f"      [SUCCESS] Account field '{base_account_name}' set for all {len(csv_file_data)} rows")
            
            # Add cleaned data to combined results
            all_transformed_data.extend(csv_file_data)
        
        print(f"\n   Combined data from all CSVs: {len(all_transformed_data)} total rows")
        
        # Create identity mapping for all existing fields
        if all_transformed_data:
            sample_row = all_transformed_data[0]
            combined_column_mapping = {field: field for field in sample_row.keys()}
            print(f"      [DEBUG] Combined column mapping: {combined_column_mapping}")
        else:
            combined_column_mapping = {}
        
        combined_bank_name = 'multi_bank_combined'
        
        return all_transformed_data, combined_column_mapping, combined_bank_name
    
    def _extract_account_mapping(self, bank_configs: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Extract account mapping from bank configurations"""
        for bank_name_config, config_dict in bank_configs.items():
            if 'account_mapping' in config_dict:
                account_mapping = config_dict['account_mapping']
                print(f"      [DEBUG] Using account_mapping from bank config: {account_mapping}")
                return account_mapping
        return None
    
    def _get_detected_bank(self, bank_info: Dict[str, Any]) -> str:
        """Extract detected bank from bank info"""
        if bank_info:
            detected_bank = bank_info.get('bank_name', bank_info.get('detected_bank', 'unknown'))
            confidence = bank_info.get('confidence', 0.0)
            return f"{detected_bank} (confidence={confidence:.2f})"
        return 'unknown'
    
    def _get_account_name(self, bank_info: Dict[str, Any], filename: str) -> str:
        """Get account name from bank configuration or filename"""
        account_name = 'Unknown'
        
        detected_bank = None
        if bank_info:
            detected_bank = bank_info.get('bank_name', bank_info.get('detected_bank'))
        
        if detected_bank and detected_bank != 'unknown':
            try:
                bank_config = self.config_service.get_bank_config(detected_bank)
                if bank_config:
                    has_account_mapping = bool(bank_config.account_mapping)
                    cashew_account = bank_config.cashew_account
                    
                    if cashew_account:
                        account_name = cashew_account
                        print(f"         Using cashew_account from {detected_bank} config: '{account_name}'")
                    elif has_account_mapping:
                        print(f"         Multi-currency bank {detected_bank} detected, will need currency mapping")
                        account_name = 'Multi-Currency'
                    else:
                        print(f"      [WARNING] No cashew_account or account_mapping in {detected_bank} config")
                else:
                    print(f"      [WARNING] Could not load config for {detected_bank}")
            except Exception as e:
                print(f"      [WARNING] Error loading config for {detected_bank}: {e}")
        
        # Fallback to filename if config loading failed
        if account_name == 'Unknown' or account_name == 'Multi-Currency':
            filename_fallback = filename.replace('.csv', '').replace('_', ' ').replace('-', ' ').title()
            if account_name == 'Multi-Currency':
                print(f"         Multi-currency mapping needed, using filename fallback: '{filename_fallback}'")
                account_name = filename_fallback
            else:
                print(f"         Using filename fallback: '{filename_fallback}'")
                account_name = filename_fallback
        
        return account_name
    
    def _map_account_by_currency(self, detected_bank: str, base_account_name: str, 
                                row: Dict[str, Any], filename: str) -> str:
        """Map account name based on currency for multi-currency banks like Wise"""
        if not detected_bank or detected_bank == 'unknown':
            return base_account_name
        
        try:
            bank_config = self.config_service.get_bank_config(detected_bank)
            if bank_config and bank_config.account_mapping:
                # Get currency from row
                currency = row.get('Currency', row.get('currency', row.get('CURRENCY', '')))
                currency = currency.strip() if currency else ''
                
                print(f"         [DEBUG] Currency value found: '{currency}'")
                
                if currency:
                    # Map currency to account name (case-insensitive lookup)
                    account_mapping = bank_config.account_mapping
                    mapped_account = account_mapping.get(currency.lower())
                    if mapped_account:
                        print(f"         [CURRENCY MAP] {currency} → '{mapped_account}'")
                        return mapped_account
                    else:
                        print(f"         [WARNING] Currency '{currency}' not found in account_mapping for {detected_bank}")
                else:
                    print(f"         [WARNING] No currency field found for multi-currency bank {detected_bank}")
        except Exception as e:
            print(f"         [WARNING] Error mapping currency for {detected_bank}: {e}")
        
        return base_account_name