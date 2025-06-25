"""
CSV parsing endpoints and logic
Handles single CSV file parsing, preview, and range detection
"""
from fastapi import HTTPException
from typing import Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from csv_parser import UnifiedCSVParser # New parser import
from data_cleaner import DataCleaner
from .models import ParseRangeRequest

class CSVProcessor:
    """Handles CSV parsing operations"""
    
    def __init__(self):
        self.unified_parser = UnifiedCSVParser() # New parser instance
        self.data_cleaner = DataCleaner()
        print(f"ℹ [MIGRATION][CSVProcessor] Initialized with UnifiedCSVParser.")
    
    def preview_csv(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Preview CSV file"""
        print(f"ℹ [MIGRATION][CSVProcessor] preview_csv called for: {file_path}")
        
        try:
            # Use UnifiedCSVParser for preview as per Phase 2 requirements
            # The UnifiedCSVParser.preview_csv can take header_row, bank_name, config_manager if needed,
            # but the original call from CSVProcessor only passed file_path and encoding.
            result = self.unified_parser.preview_csv(file_path, encoding=encoding)
            
            if not result['success']:
                print(f"[ERROR]  Preview failed: {result.get('error', 'Unknown error')}")
                raise HTTPException(status_code=400, detail=result['error'])
            
            # UnifiedCSVParser returns 'total_rows' within preview_csv's own structure
            print(f"[SUCCESS] Preview successful using UnifiedParser: {result.get('total_rows', 'N/A')} rows")
            return result
        except Exception as e:
            print(f"[ERROR]  Preview exception: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def detect_data_range(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Auto-detect data range in CSV"""
        print(f"ℹ [MIGRATION][CSVProcessor] detect_data_range called for: {file_path}")
        # Use UnifiedCSVParser for detect_data_range as per Phase 2 requirements
        result = self.unified_parser.detect_data_range(file_path, encoding=encoding)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
    
    def parse_range(self, file_path: str, request: ParseRangeRequest) -> Dict[str, Any]:
        """Parse CSV with specified range and optional data cleaning"""
        print(f"ℹ [MIGRATION][CSVProcessor] parse_range called for: {file_path}")
        print(f"  Request: start_row={request.start_row}, end_row={request.end_row}, start_col={request.start_col}, end_col={request.end_col}, encoding={request.encoding}")
        print(f"  Data cleaning enabled: {request.enable_cleaning}")
        
        try:
            # STEP 1: DATA PARSING with UnifiedCSVParser
            print(f"ℹ [MIGRATION][CSVProcessor] STEP 1: DATA PARSING with UnifiedCSVParser")
            
            # Prepare params for UnifiedCSVParser
            # Assuming request.start_row is the 0-indexed header row
            header_row_for_unified = request.start_row
            
            # max_rows for UnifiedCSVParser.parse_csv is the total number of lines to read from the file.
            # DataProcessor within UnifiedCSVParser will then use header_row_for_unified to correctly
            # identify header and data rows from the initially read chunk.
            max_rows_to_read_initially = None
            if request.end_row is not None:
                if request.end_row < request.start_row:
                    print(f"[WARNING] [MIGRATION][CSVProcessor] end_row ({request.end_row}) is less than start_row ({request.start_row}). Parsing up to header row to extract headers, data rows will be empty.")
                    max_rows_to_read_initially = request.start_row + 1 # Read enough to get the header
                else:
                    max_rows_to_read_initially = request.end_row + 1 # Read up to and including the specified end_row
            
            if request.start_col != 0 or request.end_col is not None:
                print(f"[WARNING] [MIGRATION][CSVProcessor] Column range (start_col={request.start_col}, end_col={request.end_col}) is not supported by UnifiedCSVParser. All columns will be parsed.")

            print(f"  UnifiedParser params: encoding='{request.encoding}', header_row={header_row_for_unified}, max_rows (to read initially)={max_rows_to_read_initially}")
            parse_result = self.unified_parser.parse_csv(
                file_path,
                encoding=request.encoding,
                header_row=header_row_for_unified,
                max_rows=max_rows_to_read_initially
            )
            print(f"  UnifiedParser parse_csv result success: {parse_result.get('success')}")
            
            if not parse_result['success']:
                error_detail = parse_result.get('error', 'Unknown parsing error from UnifiedCSVParser')
                print(f"[ERROR]  UnifiedCSVParser failed: {error_detail}")
                raise HTTPException(status_code=400, detail=f"Parsing failed: {error_detail}")
            
            parser_used = "unified" # Always unified now
            print(f"[SUCCESS] Parse successful using UnifiedCSVParser: {parse_result.get('row_count', 0)} rows")
            
            # STEP 2: DATA CLEANING
            final_result = parse_result
            # Ensure 'parser_used' is part of the result before cleaning, as cleaning might build a new dict
            final_result['parser_used'] = parser_used
            
            if request.enable_cleaning:
                print(f"ℹ [MIGRATION][CSVProcessor] STEP 2: DATA CLEANING")
                
                cleaning_result = self.data_cleaner.clean_parsed_data(parse_result)
                
                if cleaning_result['success']:
                    final_result = {
                        'success': True,
                        'headers': [col for col in cleaning_result['data'][0].keys()] if cleaning_result['data'] else [],
                        'data': cleaning_result['data'],
                        'row_count': cleaning_result['row_count'],
                        'parser_used': parser_used,
                        'cleaning_applied': True,
                        'cleaning_summary': cleaning_result['cleaning_summary'],
                        'updated_column_mapping': cleaning_result.get('updated_column_mapping', {}),
                        'original_headers': parse_result.get('headers', [])
                    }
                    print(f"[SUCCESS] Data cleaning successful: {cleaning_result['row_count']} clean rows")
                else:
                    print(f"[WARNING]  Data cleaning failed: {cleaning_result.get('error', 'Unknown error')}")
                    print(" Continuing with uncleaned data...")
                    final_result['cleaning_applied'] = False
                    final_result['cleaning_error'] = cleaning_result.get('error', 'Unknown error') # Keep original error key
            else:
                print(" Data cleaning skipped")
                final_result['cleaning_applied'] = False
            
            print(f"ℹ [MIGRATION][CSVProcessor] parse_range completed. Final rows: {final_result.get('row_count', 0)}")
            return final_result
            
        except Exception as e:
            print(f"[ERROR]  Parse exception: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
