"""
CSV parsing endpoints and logic
Handles single CSV file parsing, preview, and range detection
"""
from fastapi import HTTPException
from typing import Dict, Any
from ..csv_parser import CSVParser
from ..enhanced_csv_parser import EnhancedCSVParser
from ..robust_csv_parser import RobustCSVParser
from ..data_cleaner import DataCleaner
from .models import ParseRangeRequest


class CSVProcessor:
    """Handles CSV parsing operations"""
    
    def __init__(self):
        self.parser = CSVParser()
        self.enhanced_parser = EnhancedCSVParser()
        self.robust_parser = RobustCSVParser()
        self.data_cleaner = DataCleaner()
    
    def preview_csv(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Preview CSV file"""
        print(f"📁 Reading file: {file_path}")
        
        try:
            result = self.robust_parser.preview_csv(file_path, encoding)
            
            if not result['success']:
                print(f"❌ Preview failed: {result.get('error', 'Unknown error')}")
                raise HTTPException(status_code=400, detail=result['error'])
            
            print(f"✅ Preview successful: {result.get('total_rows', 0)} rows")
            return result
        except Exception as e:
            print(f"❌ Preview exception: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def detect_data_range(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Auto-detect data range in CSV"""
        result = self.robust_parser.detect_data_range(file_path, encoding)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
    
    def parse_range(self, file_path: str, request: ParseRangeRequest) -> Dict[str, Any]:
        """Parse CSV with specified range and optional data cleaning"""
        print(f"🔢 Parameters: start_row={request.start_row}, end_row={request.end_row}")
        print(f"🧹 Data cleaning enabled: {request.enable_cleaning}")
        print(f"📁 Processing file: {file_path}")
        
        try:
            # STEP 1: DATA PARSING
            print("🚀 STEP 1: DATA PARSING")
            
            # Try enhanced parser first, then robust parser as fallback
            enhanced_result = self.enhanced_parser.parse_with_range(
                file_path, 
                request.start_row, 
                request.end_row, 
                request.start_col, 
                request.end_col, 
                request.encoding
            )
            
            robust_result = self.robust_parser.parse_with_range(
                file_path, 
                request.start_row, 
                request.end_row, 
                request.start_col, 
                request.end_col, 
                request.encoding
            )
            
            # Choose the better result
            parse_result = self._choose_best_parse_result(enhanced_result, robust_result)
            parser_used = "enhanced" if parse_result == enhanced_result else "robust"
            
            if not parse_result['success']:
                print(f"❌ Both parsers failed: {parse_result.get('error', 'Unknown error')}")
                raise HTTPException(status_code=400, detail=f"Parsing failed: {parse_result.get('error', 'Unknown parsing error')}")
            
            print(f"✅ Parse successful using {parser_used} parser: {parse_result.get('row_count', 0)} rows")
            
            # STEP 2: DATA CLEANING
            final_result = parse_result
            if request.enable_cleaning:
                print("🚀 STEP 2: DATA CLEANING")
                
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
                    print(f"✅ Data cleaning successful: {cleaning_result['row_count']} clean rows")
                else:
                    print(f"⚠️  Data cleaning failed: {cleaning_result.get('error', 'Unknown error')}")
                    print("🔄 Continuing with uncleaned data...")
                    final_result['cleaning_applied'] = False
                    final_result['cleaning_error'] = cleaning_result.get('error', 'Unknown error')
            else:
                print("🚫 Data cleaning skipped")
                final_result['cleaning_applied'] = False
            
            print(f"🎉 Final result: {final_result.get('row_count', 0)} rows ready for transformation")
            return final_result
            
        except Exception as e:
            print(f"❌ Parse exception: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _choose_best_parse_result(self, enhanced_result: Dict, robust_result: Dict) -> Dict:
        """Choose the better parsing result"""
        # Use robust parser if it has more data
        if (robust_result['success'] and 
            robust_result.get('row_count', 0) > enhanced_result.get('row_count', 0)):
            return robust_result
        # Use robust parser as fallback if enhanced failed
        elif not enhanced_result['success'] and robust_result['success']:
            return robust_result
        # Default to enhanced parser
        else:
            return enhanced_result
