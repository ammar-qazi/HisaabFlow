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
    # from enhanced_csv_parser import EnhancedCSVParser # Old import
    from csv_parser import UnifiedCSVParser # New parser import
    from services.cashew_transformer import CashewTransformer # New transformer import
except ImportError:
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if backend_path not in sys.path: # Ensure backend_path is added only once
        sys.path.insert(0, backend_path)
    from csv_parser import UnifiedCSVParser
    from services.cashew_transformer import CashewTransformer
from data_cleaner import DataCleaner
from .models import MultiCSVParseRequest, MultiCSVTransformRequest
from .file_manager import FileManager
from .transfer_detection_handler import TransferDetectionHandler
from .config_manager import ConfigManager


class MultiCSVProcessor:
    """Handles multi-CSV operations"""
    
    def __init__(self, file_manager: FileManager):
        self.unified_parser = UnifiedCSVParser() # New parser instance
        self.cashew_transformer = CashewTransformer() # New transformer instance
        self.data_cleaner = DataCleaner()
        self.file_manager = file_manager
        self.transfer_handler = TransferDetectionHandler()
        self.config_manager = ConfigManager()
        print(f"ℹ️ [MIGRATION][MultiCSVProcessor] Initialized with UnifiedCSVParser and CashewTransformer.")

    
    def parse_multiple_csvs(self, request: MultiCSVParseRequest) -> Dict[str, Any]:
        """Parse multiple CSV files with individual configurations"""
        try:
            print(f"ℹ️ [MIGRATION][MultiCSVProcessor] parse_multiple_csvs called for {len(request.file_ids)} files.")
            print(f"  Data cleaning enabled: {request.enable_cleaning}")
            
            # Validation
            self._validate_parse_request(request)
            
            results = []
            
            # Process each file
            for i, file_id in enumerate(request.file_ids):
                print(f"📁 Processing file {i+1}/{len(request.file_ids)}: {file_id}")
                
                file_info = self.file_manager.get_file_info(file_id)
                file_path = file_info["temp_path"]
                config = request.parse_configs[i]
                
                result = self._parse_single_file(file_info, file_path, config, request.enable_cleaning)
                results.append(result)
            
            print(f"🎉 Successfully parsed all {len(results)} files")
            return {
                "success": True,
                "parsed_csvs": results,
                "total_files": len(results)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"💥 Unexpected error in multi-CSV parse: {str(e)}")
            import traceback
            print(f"📚 Full traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    def transform_multiple_csvs(self, request: MultiCSVTransformRequest) -> Dict[str, Any]:
        """Transform multiple CSVs with enhanced transfer detection"""
        try:
            print(f"ℹ️ [MIGRATION][MultiCSVProcessor] transform_multiple_csvs called for {len(request.csv_data_list)} files.")
            print(f"  User: {request.user_name}, Transfer detection: {request.enable_transfer_detection}")
            
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
            print(f"💥 Unexpected transform error: {str(e)}")
            import traceback
            print(f"📚 Full traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    def _validate_parse_request(self, request: MultiCSVParseRequest):
        """Validate multi-CSV parse request"""
        if not request.file_ids:
            raise HTTPException(status_code=400, detail="No file IDs provided")
        
        if len(request.file_ids) != len(request.parse_configs):
            raise HTTPException(status_code=400, detail="Number of file IDs must match number of parse configs")
        
        # Validate all file IDs exist
        self.file_manager.validate_file_ids(request.file_ids)
    
    def _parse_single_file(self, file_info: Dict, file_path: str, config: Dict, enable_cleaning: bool) -> Dict:
        """Parse a single file with configuration"""
        print(f"ℹ️ [MIGRATION][MultiCSVProcessor] _parse_single_file: {file_info['original_name']}")
        print(f"  Config: start_row={config.get('start_row', 0)}, end_row={config.get('end_row')}, start_col={config.get('start_col',0)}, end_col={config.get('end_col')}, encoding={config.get('encoding', 'utf-8')}")
        
        try:
            # Prepare params for UnifiedCSVParser
            # Assuming config.get('start_row', 0) is the 0-indexed header row
            header_row_for_unified = config.get('start_row', 0)
            max_rows_for_unified = None
            if config.get('end_row') is not None and config.get('end_row') >= header_row_for_unified:
                max_rows_for_unified = config.get('end_row') - header_row_for_unified
            
            if config.get('start_col', 0) != 0 or config.get('end_col') is not None:
                print(f"⚠️ [MIGRATION][MultiCSVProcessor] Column range (start_col={config.get('start_col', 0)}, end_col={config.get('end_col')}) is not supported by UnifiedCSVParser. All columns will be parsed.")

            print(f"  UnifiedParser params: encoding='{config.get('encoding', 'utf-8')}', header_row={header_row_for_unified}, max_rows={max_rows_for_unified}")
            
            # Parse with UnifiedCSVParser
            parse_result = self.unified_parser.parse_csv( # Use new parser
                file_path,
                encoding=config.get('encoding', 'utf-8'),
                header_row=header_row_for_unified,
                max_rows=max_rows_for_unified
            )
            print(f"  UnifiedParser parse_csv result success: {parse_result.get('success')}")
            
            if not parse_result['success']:
                raise HTTPException(status_code=400, detail=f"Failed to parse {file_info['original_name']}: {parse_result.get('error', 'Unknown error')}")
            
            # Apply data cleaning if enabled
            final_result = self._apply_cleaning_if_enabled(parse_result, config, enable_cleaning, file_info['original_name'])
            
            return {
                "file_id": config.get('file_id'),
                "file_name": file_info["original_name"],
                "parse_result": final_result,
                "config": config,
                "data": final_result['data']
            }
            
        except Exception as parse_error:
            print(f"❌ Parse error for {file_info['original_name']}: {str(parse_error)}")
            raise HTTPException(status_code=500, detail=f"Parse error for {file_info['original_name']}: {str(parse_error)}")
    
    def _apply_cleaning_if_enabled(self, parse_result: Dict, config: Dict, enable_cleaning: bool, file_name: str) -> Dict:
        """Apply data cleaning if enabled"""
        final_result = parse_result
        
        if enable_cleaning:
            print(f"🧹 Applying data cleaning to {file_name}...")
            
            # Use configuration-based cleaning instead of template
            config_config = config.get('config_config', {})
            cleaning_result = self.data_cleaner.clean_parsed_data(parse_result, config_config)
            
            if cleaning_result['success']:
                final_result = {
                    'success': True,
                    'headers': [col for col in cleaning_result['data'][0].keys()] if cleaning_result['data'] else [],
                    'data': cleaning_result['data'],
                    'row_count': cleaning_result['row_count'],
                    'cleaning_applied': True,
                    'cleaning_summary': cleaning_result['cleaning_summary'],
                    'updated_column_mapping': cleaning_result.get('updated_column_mapping', {}),
                    'original_headers': parse_result.get('headers', [])
                }
                print(f"✅ Data cleaning successful: {cleaning_result['row_count']} clean rows")
            else:
                print(f"⚠️  Data cleaning failed for {file_name}: {cleaning_result.get('error', 'Unknown error')}")
                final_result['cleaning_applied'] = False
                final_result['cleaning_error'] = cleaning_result.get('error', 'Unknown error')
        else:
            final_result['cleaning_applied'] = False
        
        return final_result
    
    def _transform_all_csvs(self, request: MultiCSVTransformRequest) -> tuple:
        """Transform all CSV files"""
        all_transformed_data = []
        transformation_results = []
        
        for i, csv_data in enumerate(request.csv_data_list):
            print(f"📁 Processing CSV: {csv_data.get('file_name', 'Unknown')}")
            
            # Get configuration (supports both new config and legacy template)
            config_data = csv_data.get('config_config', csv_data.get('template_config', {}))
            print(f"🔍 DEBUG: Config keys = {list(config_data.keys())}")
            print(f"🔍 DEBUG: Config name = '{config_data.get('name', 'NONE')}'")
            print(f"🔍 DEBUG: Config bank_name = '{config_data.get('bank_name', 'NONE')}'")
            
            column_mapping = config_data.get('column_mapping', {})
            bank_name = config_data.get('bank_name', csv_data.get('file_name', 'Unknown'))
            categorization_rules = config_data.get('categorization_rules', [])
            default_category_rules = config_data.get('default_category_rules')
            account_mapping = config_data.get('account_mapping')
            
            print(f"🔍 DEBUG: Final bank_name for processing = '{bank_name}'")
            print(f"🔧 Using configuration-based system (template support as fallback)")
            
            print(f"🏦 Bank: {bank_name}, Rules: {len(categorization_rules)}, Rows: {len(csv_data.get('data', []))}")
            print(f"ℹ️ [MIGRATION][MultiCSVProcessor] _transform_all_csvs: Transforming for bank {bank_name} using CashewTransformer.")
            
            # Transform data
            try:
                transformed = self.cashew_transformer.transform_to_cashew( # Use new transformer
                    csv_data.get('data', []), # Ensure data is accessed safely
                    column_mapping,
                    bank_name,
                    categorization_rules,
                    default_category_rules,
                    account_mapping,
                    request.bank_rules_settings
                )
                
                print(f"  Transformed {len(transformed)} transactions for {csv_data.get('file_name')}")
                
                config_name_used = config_data.get('name', 'None')
                print(f"🔍 DEBUG: Recording config_used = '{config_name_used}'")
                
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
                print(f"❌ Transform error for {csv_data.get('file_name')}: {str(transform_error)}")
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
