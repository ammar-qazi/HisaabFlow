"""
Multi-CSV processing with transfer detection
Handles parsing and transforming multiple CSV files with enhanced transfer detection
"""
from fastapi import HTTPException
from typing import List, Dict, Any
from ..enhanced_csv_parser import EnhancedCSVParser
from ..data_cleaner import DataCleaner
from ..transfer_detector import TransferDetector
from ..transfer_detector_improved import ImprovedTransferDetector
from ..transfer_detector_enhanced_ammar_refactored import TransferDetector as EnhancedAmmarTransferDetector
from .models import MultiCSVParseRequest, MultiCSVTransformRequest
from .file_manager import FileManager


class MultiCSVProcessor:
    """Handles multi-CSV operations with transfer detection"""
    
    def __init__(self, file_manager: FileManager):
        self.enhanced_parser = EnhancedCSVParser()
        self.data_cleaner = DataCleaner()
        self.file_manager = file_manager
    
    def parse_multiple_csvs(self, request: MultiCSVParseRequest) -> Dict[str, Any]:
        """Parse multiple CSV files with individual configurations"""
        try:
            print(f"🚀 Multi-CSV parse request received for {len(request.file_ids)} files")
            print(f"🧹 Data cleaning enabled: {request.enable_cleaning}")
            
            # Validation
            if not request.file_ids:
                raise HTTPException(status_code=400, detail="No file IDs provided")
            
            if len(request.file_ids) != len(request.parse_configs):
                raise HTTPException(status_code=400, detail="Number of file IDs must match number of parse configs")
            
            # Validate all file IDs exist
            self.file_manager.validate_file_ids(request.file_ids)
            
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
            print(f"🚀 Multi-CSV transform request received for {len(request.csv_data_list)} files")
            print(f"👤 User: {request.user_name}, Transfer detection: {request.enable_transfer_detection}")
            
            # Transform each CSV individually
            all_transformed_data, transformation_results = self._transform_all_csvs(request)
            
            # Perform transfer detection if enabled
            transfer_analysis = self._perform_transfer_detection(request, all_transformed_data)
            
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
    
    def _parse_single_file(self, file_info: Dict, file_path: str, config: Dict, enable_cleaning: bool) -> Dict:
        """Parse a single file with configuration"""
        print(f"📄 File: {file_info['original_name']} at {file_path}")
        print(f"🔧 Config: start_row={config.get('start_row', 0)}, encoding={config.get('encoding', 'utf-8')}")
        
        try:
            # Parse with enhanced parser
            parse_result = self.enhanced_parser.parse_with_range(
                file_path,
                config.get('start_row', 0),
                config.get('end_row'),
                config.get('start_col', 0),
                config.get('end_col'),
                config.get('encoding', 'utf-8')
            )
            
            if not parse_result['success']:
                raise HTTPException(status_code=400, detail=f"Failed to parse {file_info['original_name']}: {parse_result.get('error', 'Unknown error')}")
            
            # Apply data cleaning if enabled
            final_result = self._apply_cleaning_if_enabled(parse_result, config, enable_cleaning, file_info['original_name'])
            
            return {
                "file_id": config.get('file_id'),  # Get from config if available
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
            
            template_config = config.get('template_config', {})
            cleaning_result = self.data_cleaner.clean_parsed_data(parse_result, template_config)
            
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
            
            # Get template configuration
            template_config = csv_data.get('template_config', {})
            column_mapping = template_config.get('column_mapping', {})
            bank_name = template_config.get('bank_name', csv_data.get('file_name', 'Unknown'))
            categorization_rules = template_config.get('categorization_rules', [])
            default_category_rules = template_config.get('default_category_rules')
            account_mapping = template_config.get('account_mapping')
            
            print(f"🏦 Bank: {bank_name}, Rules: {len(categorization_rules)}, Rows: {len(csv_data.get('data', []))}")
            
            # Transform data
            try:
                transformed = self.enhanced_parser.transform_to_cashew(
                    csv_data['data'],
                    column_mapping,
                    bank_name,
                    categorization_rules,
                    default_category_rules,
                    account_mapping,
                    request.bank_rules_settings
                )
                
                print(f"✅ Transformed {len(transformed)} transactions for {csv_data.get('file_name')}")
                
                transformation_results.append({
                    "file_name": csv_data.get('file_name'),
                    "transactions": len(transformed),
                    "template_used": template_config.get('name', 'None')
                })
                
                all_transformed_data.extend(transformed)
                
                # Merge transformed data with original data
                for j, transformed_row in enumerate(transformed):
                    csv_data['data'][j].update(transformed_row)

            except Exception as transform_error:
                print(f"❌ Transform error for {csv_data.get('file_name')}: {str(transform_error)}")
                raise HTTPException(status_code=500, detail=f"Transform error for {csv_data.get('file_name')}: {str(transform_error)}")
        
        return all_transformed_data, transformation_results
    
    def _perform_transfer_detection(self, request: MultiCSVTransformRequest, all_transformed_data: List[Dict]) -> Dict:
        """Perform transfer detection between CSV files"""
        # Initialize with default values
        transfer_analysis = {
            'transfers': [],
            'summary': {
                'transfer_pairs_found': 0,
                'potential_transfers': 0,
                'conflicts': 0,
                'flagged_for_review': 0
            }
        }
        
        if not request.enable_transfer_detection or len(request.csv_data_list) <= 1:
            print("🚫 Transfer detection skipped (not enabled or insufficient CSVs)")
            return transfer_analysis
        
        try:
            print(f"🔄 Starting ENHANCED TRANSFER DETECTION between {len(request.csv_data_list)} CSVs...")
            
            # Try to use the new configuration-based transfer detector
            transfer_detector = self._initialize_transfer_detector(request)
            
            # Detect transfers
            transfer_analysis = transfer_detector.detect_transfers(request.csv_data_list)
            print(f"✅ Transfer detection complete: {transfer_analysis['summary']}")
            
            # Apply transfer categorization
            if transfer_analysis.get('transfers'):
                self._apply_transfer_categorization(transfer_detector, request, transfer_analysis, all_transformed_data)
            
            return transfer_analysis
            
        except Exception as transfer_error:
            print(f"⚠️ Transfer detection failed: {str(transfer_error)}")
            print("🔄 Continuing without transfer detection...")
            import traceback
            print(f"📚 Full error traceback: {traceback.format_exc()}")
            return transfer_analysis
    
    def _initialize_transfer_detector(self, request: MultiCSVTransformRequest):
        """Initialize the best available transfer detector"""
        # Try new configuration-based detector first
        try:
            transfer_detector = EnhancedAmmarTransferDetector("configs")
            print("🚀 Using NEW Configuration-Based Transfer Detector")
            return transfer_detector
        except Exception as e1:
            print(f"⚠️ Configuration-based detector failed: {e1}")
            
            # Fallback to enhanced ammar detector with old interface
            try:
                from ..transfer_detector_enhanced_ammar import TransferDetector as LegacyEnhancedAmmarTransferDetector
                transfer_detector = LegacyEnhancedAmmarTransferDetector(
                    user_name=request.user_name,
                    date_tolerance_hours=request.date_tolerance_hours
                )
                print("🚀 Using Legacy Enhanced Ammar Transfer Detector")
                return transfer_detector
            except Exception as e2:
                print(f"⚠️ Legacy Enhanced Ammar detector failed: {e2}")
                
                # Fallback to improved detector
                try:
                    transfer_detector = ImprovedTransferDetector(
                        user_name=request.user_name,
                        date_tolerance_hours=request.date_tolerance_hours
                    )
                    print("⚠️  Using Standard Improved Transfer Detector")
                    return transfer_detector
                except Exception as e3:
                    print(f"⚠️ Improved detector failed: {e3}")
                    
                    # Last fallback to basic detector
                    transfer_detector = TransferDetector(
                        user_name=request.user_name,
                        date_tolerance_hours=request.date_tolerance_hours
                    )
                    print("⚠️  Using Basic Transfer Detector")
                    return transfer_detector
    
    def _apply_transfer_categorization(self, transfer_detector, request, transfer_analysis, all_transformed_data):
        """Apply transfer categorization to detected transfers"""
        print(f"🔄 Applying transfer categorization to {len(transfer_analysis['transfers'])} pairs...")
        
        transfer_matches = transfer_detector.apply_transfer_categorization(
            request.csv_data_list, 
            transfer_analysis['transfers']
        )
        
        print(f"📝 Created {len(transfer_matches)} transfer matches for balance correction")
        
        # Apply balance corrections
        balance_corrections_applied = 0
        
        for i, transaction in enumerate(all_transformed_data):
            for match in transfer_matches:
                # Improved matching with cleaned numeric amounts
                trans_amount = float(transaction.get('Amount', '0'))
                match_amount = float(match['amount'])
                amount_match = abs(trans_amount - match_amount) < 0.01
                date_match = transaction.get('Date', '').startswith(match['date'])
                
                if amount_match and date_match:
                    all_transformed_data[i]['Category'] = match['category']
                    all_transformed_data[i]['Note'] = match['note']
                    all_transformed_data[i]['_transfer_pair_id'] = match['pair_id']
                    all_transformed_data[i]['_transfer_type'] = match['transfer_type']
                    all_transformed_data[i]['_is_transfer'] = True
                    all_transformed_data[i]['_match_strategy'] = match.get('match_strategy', 'traditional')
                    balance_corrections_applied += 1
                    break
        
        print(f"✅ Transfer categorization applied - {balance_corrections_applied} balance corrections")
    
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
