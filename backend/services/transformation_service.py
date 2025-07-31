"""
Data transformation service for orchestrating transformation workflows
"""
from pathlib import Path
import json

from backend.core.data_transformation.cashew_transformation_service import CashewTransformationService
from backend.core.transfer_detection.transfer_processing_service import TransferProcessingService
from backend.core.business_cleaning.data_cleaning_service import DataCleaningService
from backend.services.export_formatting_service import ExportFormattingService
from backend.core.bank_detection import BankDetector
from backend.infrastructure.config.unified_config_service import get_unified_config_service

class TransformationService:
    """Service for orchestrating transformation workflows using focused services"""
    
    def __init__(self):
        self.config_service = get_unified_config_service()
        
        # Initialize focused services
        self.cashew_transformation_service = CashewTransformationService()
        self.transfer_processing_service = TransferProcessingService()
        self.data_cleaning_service = DataCleaningService()
        self.export_formatting_service = ExportFormattingService()
        
        print(f"ℹ [TransformationService] Initialized with focused services")
    
    def transform_single_data(self, data: list, column_mapping: dict, bank_name: str = "", 
                            categorization_rules: list = None, default_category_rules: dict = None,
                            account_mapping: dict = None, config: dict = None):
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
        print(f"ℹ [TransformationService] transform_single_data called for bank: {bank_name}")
        
        return self.cashew_transformation_service.transform_single_data(
            data, column_mapping, bank_name, categorization_rules, 
            default_category_rules, account_mapping, config
        )
    
    def transform_multi_csv_data(self, raw_data: dict):
        """
        Transform multi-CSV data to Cashew format using focused services
        
        Args:
            raw_data: Raw request data from frontend, may include:
                     - csv_data_list: CSV data for transformation
                     - manually_confirmed_pairs: User-confirmed transfer pairs for categorization
            
        Returns:
            dict: Multi-CSV transformation result
        """
        print(f"ℹ [TransformationService] Multi-CSV transform request received")
        
        try:
            print(f"   Request keys: {list(raw_data.keys())}")
            
            # Extract manually confirmed pairs if provided
            manually_confirmed_pairs = raw_data.get('manually_confirmed_pairs', [])
            if manually_confirmed_pairs:
                print(f"   Received {len(manually_confirmed_pairs)} manually confirmed transfer pairs")
            
            # Extract CSV data list
            csv_data_list = raw_data.get('csv_data_list', [])
            if not csv_data_list:
                raise ValueError("No CSV data found in request")
            
            # Step 1: Transform data using CashewTransformationService
            categorization_rules = raw_data.get('categorization_rules')
            default_category_rules = raw_data.get('default_category_rules')
            account_mapping = raw_data.get('account_mapping')
            bank_configs = self._get_bank_configs_for_data(raw_data)
            
            print(f"   Step 1: Cashew transformation...")
            transformation_result = self.cashew_transformation_service.transform_multi_csv_data(
                csv_data_list, categorization_rules, default_category_rules, account_mapping, bank_configs
            )
            
            if not transformation_result['success']:
                raise Exception(f"Cashew transformation failed: {transformation_result.get('error', 'Unknown error')}")
            
            result = transformation_result['data']
            print(f"   [SUCCESS] Transformation successful: {len(result)} rows transformed")
            
            # Step 2: Apply data cleaning and categorization
            print(f"   Step 2: Data cleaning and categorization...")
            enhanced_result = self.data_cleaning_service.apply_advanced_processing(result, csv_data_list)
            
            # Step 3: Run transfer detection
            print(f"   Step 3: Transfer detection...")
            transfer_analysis_raw = self.transfer_processing_service.run_transfer_detection(enhanced_result, csv_data_list)
            
            # Step 4: Apply transfer categorization
            print(f"   Step 4: Transfer categorization...")
            final_result = self.transfer_processing_service.apply_transfer_categorization(
                transfer_analysis_raw.get('processed_transactions', enhanced_result),
                transfer_analysis_raw,
                manually_confirmed_pairs
            )
            
            # Step 5: Format for API response
            print(f"   Step 5: Format for API response...")
            transfer_analysis = self.export_formatting_service.format_transfer_analysis(transfer_analysis_raw)
            cleaned_transformed_data = self.export_formatting_service.clean_transformed_data(final_result)
            
            formatting_result = self.export_formatting_service.format_transformation_summary(
                csv_data_list, cleaned_transformed_data
            )
            
            print(f"   [DATA] Transfer pairs found: {transfer_analysis.get('summary', {}).get('transfer_pairs_found', 0)}")
            print(f"   [DATA] Potential transfers: {transfer_analysis.get('summary', {}).get('potential_transfers', 0)}")
            
            # Response matching MultiCSVResponse model exactly
            response_data = {
                "success": True,
                "transformed_data": cleaned_transformed_data,
                "transfer_analysis": transfer_analysis,
                "transformation_summary": formatting_result["transformation_summary"],
                "file_results": formatting_result["file_results"]
            }
            
            print(f"   Sending response with {len(cleaned_transformed_data)} cleaned transformed_data rows")
            return response_data
            
        except Exception as e:
            print(f"[ERROR] Multi-CSV transform exception: {str(e)}")
            import traceback
            print(f"   Full traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_bank_configs_for_data(self, raw_data: dict):
        """Get bank configurations for fallback logic"""
        csv_data_list = raw_data.get('csv_data_list', [])
        configs = {}
        
        for csv_data in csv_data_list:
            bank_info = csv_data.get('bank_info', {})
            detected_bank = bank_info.get('detected_bank')
            
            if detected_bank and detected_bank != 'unknown':
                try:
                    bank_config = self.config_service.get_bank_config(detected_bank)
                    if bank_config:
                        # Convert UnifiedBankConfig to dict structure for compatibility
                        config_dict = {
                            'bank_info': {
                                'name': bank_config.name,
                                'display_name': bank_config.display_name,
                                'cashew_account': bank_config.cashew_account,
                                'currency_primary': bank_config.currency_primary
                            },
                            'column_mapping': bank_config.column_mapping,
                            'account_mapping': bank_config.account_mapping,
                            'categorization': bank_config.categorization_rules,
                            'default_category_rules': bank_config.default_category_rules,
                            'csv_config': {
                                'date_format': bank_config.csv_config.date_format
                            }
                        }
                        configs[detected_bank] = config_dict
                        print(f"      Loaded config for {detected_bank}")
                except Exception as e:
                    print(f"      [WARNING] Error loading config for {detected_bank}: {e}")
        
        return configs
    
    def apply_transfer_categorization_only(self, request_data: dict):
        """
        Apply transfer categorization to existing transformed data (lightweight operation)
        
        Args:
            request_data: {
                transformed_data: list,
                manually_confirmed_pairs: list,
                transfer_analysis: dict
            }
        
        Returns:
            dict: Updated transformed data with proper categorization
        """
        print(f"ℹ [TransformationService] Applying transfer categorization only...")
        
        # Extract data from request
        transformed_data = request_data.get('transformed_data', [])
        manually_confirmed_pairs = request_data.get('manually_confirmed_pairs', [])
        transfer_analysis = request_data.get('transfer_analysis', {})
        
        # Use the focused TransferProcessingService
        return self.transfer_processing_service.apply_transfer_categorization_only(
            transformed_data, manually_confirmed_pairs, transfer_analysis
        )
