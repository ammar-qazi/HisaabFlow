"""
Multi-CSV parsing service for coordinating CSV processing operations
"""

from backend.services.export_formatting_service import ExportFormattingService
from backend.infrastructure.config.unified_config_service import get_unified_config_service
import logging

logger = logging.getLogger(__name__)

class MultiCSVService:
    """Service for coordinating multi-CSV parsing operations using focused services"""
    
    def __init__(self, preview_service=None):
        self.config_service = get_unified_config_service()
        
        # Initialize focused services with preview service for bank detection caching
        from backend.infrastructure.config.dependency_injection import create_csv_processing_service
        self.csv_processing_service = create_csv_processing_service(preview_service=preview_service)
        self.export_formatting_service = ExportFormattingService()
        
        logger.debug(f"ℹ [MultiCSVService] Initialized with focused services and bank detection caching")
    
    def parse_multiple_files(self, file_infos: list, parse_configs: list, 
                           enable_cleaning: bool = True, use_pydantic: bool = False):
        """
        Parse multiple CSV files using focused services
        
        Args:
            file_infos: List of file info dictionaries
            parse_configs: List of parsing configurations
            enable_cleaning: Whether to enable data cleaning
            use_pydantic: Whether to convert parsed data to CSVRow Pydantic models
            
        Returns:
            dict: Multi-CSV parsing result
        """
        user_name = self.config_service.get_user_name()
        logger.debug(f"ℹ [MultiCSVService] parse_multiple_files called for {len(file_infos)} files")
        logger.debug(f"   User name from config: {user_name}")
        logger.debug(f"   Data cleaning enabled: {enable_cleaning}")
        
        try:
            results = []
            
            # Process each file using the focused CSV processing service
            for i, (file_info, config) in enumerate(zip(file_infos, parse_configs)):
                logger.debug(f"   Processing file {i+1}/{len(file_infos)}: {file_info['file_id']}")
                
                # Use the focused CSV processing service
                processing_result = self.csv_processing_service.process_single_file(
                    file_info, config, enable_cleaning
                )
                
                if not processing_result['success']:
                    logger.error(f"      [ERROR] Failed to process file: {processing_result.get('error', 'Unknown error')}")
                    results.append(processing_result)
                    continue
                
                # Handle Pydantic conversion if requested
                final_data_for_response = processing_result['parse_result']['data']
                data_type_for_response = 'dict'
                
                if use_pydantic and processing_result['bank_info']['bank_name'] != 'unknown':
                    column_mapping = self.config_service.get_column_mapping(processing_result['bank_info']['bank_name'])
                    if column_mapping:
                        try:
                            pydantic_data = self.export_formatting_service.map_to_pydantic_rows(
                                final_data_for_response, column_mapping
                            )
                            final_data_for_response = pydantic_data
                            data_type_for_response = 'pydantic'
                            logger.debug(f"      Mapped {len(pydantic_data)} rows to CSVRow models for {processing_result['filename']}")
                        except Exception as e:
                            logger.warning(f"      [WARNING] Pydantic mapping failed for {processing_result['filename']}: {e}")
                
                # Update the result with the processed data
                processing_result['parse_result']['data'] = final_data_for_response
                processing_result['data_type'] = data_type_for_response
                
                results.append(processing_result)
            
            logger.debug(f"   Successfully processed all {len(results)} files")
            return {
                "success": True,
                "parsed_csvs": results,
                "total_files": len(results)
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Multi-CSV parse exception: {str(e)}")
            import traceback
            logger.error(f"   Full traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
