"""
Multi-CSV processing coordinator
Handles parsing and transforming multiple CSV files, delegating transfer detection to specialized handler
"""
from fastapi import HTTPException
from typing import List, Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.cashew_transformer import CashewTransformer # New transformer import
    from services.multi_csv_service import MultiCSVService # New service import
except ImportError:
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if backend_path not in sys.path: # Ensure backend_path is added only once
        sys.path.insert(0, backend_path)
    from services.cashew_transformer import CashewTransformer
    from services.multi_csv_service import MultiCSVService
from .models import MultiCSVParseRequest, MultiCSVTransformRequest, ParseConfig
from .file_manager import FileManager
from .transfer_detection_handler import TransferDetectionHandler
from .config_manager import ConfigManager

class MultiCSVProcessor:
    """Handles multi-CSV operations"""
    
    def __init__(self, file_manager: FileManager):
        self.cashew_transformer = CashewTransformer() # New transformer instance
        self.file_manager = file_manager
        self.transfer_handler = TransferDetectionHandler()
        self.config_manager = ConfigManager()
        self.multi_csv_service = MultiCSVService() # Initialize the service
        print(f"ℹ️ [MIGRATION][MultiCSVProcessor] Initialized with UnifiedCSVParser and CashewTransformer.")

    
    def parse_multiple_csvs(self, request: MultiCSVParseRequest) -> Dict[str, Any]:
        """Parse multiple CSV files with individual configurations"""
        try:
            print(f"ℹ️ [MIGRATION][MultiCSVProcessor] parse_multiple_csvs called for {len(request.file_ids)} files.")
            print(f"  Data cleaning enabled: {request.enable_cleaning}")
            
            # Validation
            self._validate_parse_request(request)
            
            results = []
            
            # Prepare file_infos for the service call
            file_infos = []
            for file_id in request.file_ids:
                file_info = self.file_manager.get_file_info(file_id)
                # The service expects file_info to contain 'file_id'
                file_info_with_id = file_info.copy()
                file_info_with_id['file_id'] = file_id
                file_infos.append(file_info_with_id)

            # Delegate parsing to the MultiCSVService
            service_result = self.multi_csv_service.parse_multiple_files(
                file_infos=file_infos,
                parse_configs=request.parse_configs,
                enable_cleaning=request.enable_cleaning,
                use_pydantic=True # Request Pydantic models
            )
            
            print(f" Successfully parsed all {len(service_result.get('parsed_csvs', []))} files")
            return service_result # Return the result directly from the service
            
        except HTTPException:
            raise
        except Exception as e:
            print(f" Unexpected error in multi-CSV parse: {str(e)}")
            import traceback
            print(f" Full traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    def transform_multiple_csvs(self, request: MultiCSVTransformRequest) -> Dict[str, Any]:
        """Transform multiple CSVs with enhanced transfer detection"""
        try:
            print(f"ℹ️ [MIGRATION][MultiCSVProcessor] transform_multiple_csvs called for {len(request.csv_data_list)} files.")
            print(f"  Transfer detection: {request.enable_transfer_detection}")
            
            # Transform each CSV individually
            all_transformed_data, transformation_results = self._transform_all_csvs(request)
            
            # Perform transfer detection if enabled
            transfer_analysis = self.transfer_handler.perform_transfer_detection(request, all_transformed_data)
            
            return {
                "success": True,
                "transformed_data": all_transformed_data,
                "transfer_analysis": transfer_analysis,
                "transformation_summary": self._create_transformation_summary(
                    all_transformed_data, transfer_analysis, request.csv_data_list
                ),
                "file_results": transformation_results
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f" Unexpected transform error: {str(e)}")
            import traceback
            print(f" Full traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    def _validate_parse_request(self, request: MultiCSVParseRequest):
        """Validate multi-CSV parse request"""
        if not request.file_ids:
            raise HTTPException(status_code=400, detail="No file IDs provided")
        
        if len(request.file_ids) != len(request.parse_configs):
            raise HTTPException(status_code=400, detail="Number of file IDs must match number of parse configs")
        
        # Validate all file IDs exist
        self.file_manager.validate_file_ids(request.file_ids)
    
    
    def _transform_all_csvs(self, request: MultiCSVTransformRequest) -> tuple:
        """Transform all CSV files"""
        all_transformed_data = []
        transformation_results = []
        
        for i, csv_data in enumerate(request.csv_data_list):
            print(f" Processing CSV: {csv_data.get('file_name', 'Unknown')}")
            
            # Get configuration (supports both new config and legacy template)
            config_data = csv_data.get('config_config', csv_data.get('template_config', {}))
            print(f" DEBUG: Config keys = {list(config_data.keys())}")
            print(f" DEBUG: Config name = '{config_data.get('name', 'NONE')}'")
            print(f" DEBUG: Config bank_name = '{config_data.get('bank_name', 'NONE')}'")
            
            column_mapping = config_data.get('column_mapping', {})
            bank_name = config_data.get('bank_name', csv_data.get('file_name', 'Unknown'))
            categorization_rules = config_data.get('categorization_rules', [])
            default_category_rules = config_data.get('default_category_rules')
            account_mapping = config_data.get('account_mapping')
            
            print(f" DEBUG: Final bank_name for processing = '{bank_name}'")
            print(f" Using configuration-based system (template support as fallback)")
            
            print(f" Bank: {bank_name}, Rules: {len(categorization_rules)}, Rows: {len(csv_data.get('data', []))}")
            print(f"ℹ️ [MIGRATION][MultiCSVProcessor] _transform_all_csvs: Transforming for bank {bank_name} using CashewTransformer.")
            
            # Transform data
            try:
                transformed = self.cashew_transformer.transform_to_cashew( # Use new transformer
                    csv_data.get('data', []), # Ensure data is accessed safely
                    column_mapping,
                    bank_name,
                    categorization_rules,
                    default_category_rules,
                    account_mapping
                )
                
                print(f"  Transformed {len(transformed)} transactions for {csv_data.get('file_name')}")
                
                config_name_used = config_data.get('name', 'None')
                print(f" DEBUG: Recording config_used = '{config_name_used}'")
                
                transformation_results.append({
                    "file_name": csv_data.get('file_name'),
                    "transactions": len(transformed),
                    "config_used": config_name_used
                })
                
                all_transformed_data.extend(transformed)
                
                # Merge transformed data with original data
                for j, transformed_row in enumerate(transformed):
                    csv_data['data'][j].update(transformed_row)

            except Exception as transform_error:
                print(f"[ERROR]  Transform error for {csv_data.get('file_name')}: {str(transform_error)}")
                raise HTTPException(status_code=500, detail=f"Transform error for {csv_data.get('file_name')}: {str(transform_error)}")
        
        return all_transformed_data, transformation_results
    
    def _create_transformation_summary(self, all_transformed_data: List[Dict], transfer_analysis: Dict, csv_data_list: List[Dict]) -> Dict:
        """Create transformation summary with transfer detection results"""
        return {
            "total_transactions": len(all_transformed_data),
            "files_processed": len(csv_data_list),
            "transfers_detected": len(transfer_analysis.get('transfers', [])),
            "balance_corrections_applied": len([t for t in all_transformed_data if t.get('Category') == 'Balance Correction']),
            "detector_used": transfer_analysis.get('detector_used', 'none'),
            "exchange_amount_matches": transfer_analysis.get('exchange_amount_matches', 0),
            "traditional_matches": transfer_analysis.get('traditional_matches', 0)
        }
