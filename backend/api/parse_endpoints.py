"""
CSV parsing endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import sys

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from enhanced_csv_parser import EnhancedCSVParser
    from robust_csv_parser import RobustCSVParser
    from data_cleaner import DataCleaner
except ImportError:
    # Fallback path for import issues
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, backend_path)
    from enhanced_csv_parser import EnhancedCSVParser
    from robust_csv_parser import RobustCSVParser
    from data_cleaner import DataCleaner

# Import file helper function
try:
    from api.file_endpoints import get_uploaded_file
except ImportError:
    # Fallback implementation
    def get_uploaded_file(file_id):
        # This will be populated by file_endpoints when it loads
        return None

parse_router = APIRouter()

# Initialize parsers
enhanced_parser = EnhancedCSVParser()
robust_parser = RobustCSVParser()
data_cleaner = DataCleaner()

class ParseRangeRequest(BaseModel):
    start_row: int
    end_row: Optional[int] = None
    start_col: int = 0
    end_col: Optional[int] = None
    encoding: str = "utf-8"
    enable_cleaning: bool = True

class MultiCSVParseRequest(BaseModel):
    file_ids: List[str]
    parse_configs: List[Dict[str, Any]]
    user_name: str = "Ammar Qazi"
    date_tolerance_hours: int = 24
    enable_cleaning: bool = True

@parse_router.get("/preview/{file_id}")
async def preview_csv(file_id: str, encoding: str = "utf-8"):
    """Preview uploaded CSV file"""
    print(f"🕵️‍♂️ Preview request for file_id: {file_id}")
    
    file_info = get_uploaded_file(file_id)
    if not file_info:
        print(f"❌ File {file_id} not found")
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = file_info["temp_path"]
    
    try:
        result = robust_parser.preview_csv(file_path, encoding)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        return result
    except Exception as e:
        print(f"❌ Preview exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@parse_router.get("/detect-range/{file_id}")
async def detect_data_range(file_id: str, encoding: str = "utf-8"):
    """Auto-detect data range in CSV"""
    print(f"🔍 Detect range request for file_id: {file_id}")
    
    file_info = get_uploaded_file(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = file_info["temp_path"]
    
    try:
        result = robust_parser.detect_data_range(file_path, encoding)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        return result
    except Exception as e:
        print(f"❌ Detect range exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@parse_router.post("/parse-range/{file_id}")
async def parse_range(file_id: str, request: ParseRangeRequest):
    """Parse CSV with specified range and data cleaning"""
    print(f"🕵️‍♂️ Parse range request for file_id: {file_id}")
    print(f"🧹 Data cleaning enabled: {request.enable_cleaning}")
    
    file_info = get_uploaded_file(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = file_info["temp_path"]
    
    try:
        # Parse with enhanced parser
        parse_result = enhanced_parser.parse_with_range(
            file_path, 
            request.start_row, 
            request.end_row, 
            request.start_col, 
            request.end_col, 
            request.encoding
        )
        
        if not parse_result['success']:
            raise HTTPException(status_code=400, detail=parse_result['error'])
        
        # Apply data cleaning if enabled
        final_result = parse_result
        if request.enable_cleaning:
            print(f"🧹 Applying data cleaning...")
            cleaning_result = data_cleaner.clean_parsed_data(parse_result)
            
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
                print(f"✅ Data cleaning successful")
            else:
                print(f"⚠️  Data cleaning failed, using uncleaned data")
                final_result['cleaning_applied'] = False
        else:
            final_result['cleaning_applied'] = False
        
        return final_result
        
    except Exception as e:
        print(f"❌ Parse exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@parse_router.post("/multi-csv/parse")
async def parse_multiple_csvs(request: MultiCSVParseRequest):
    """Parse multiple CSV files"""
    print(f"🚀 Multi-CSV parse request for {len(request.file_ids)} files")
    print(f"🧹 Data cleaning enabled: {request.enable_cleaning}")
    
    try:
        # Validate all file IDs exist
        for file_id in request.file_ids:
            if not get_uploaded_file(file_id):
                raise HTTPException(status_code=404, detail=f"File {file_id} not found")
        
        if len(request.file_ids) != len(request.parse_configs):
            raise HTTPException(status_code=400, detail="Number of file IDs must match number of parse configs")
        
        results = []
        
        # Process each file
        for i, file_id in enumerate(request.file_ids):
            print(f"📁 Processing file {i+1}/{len(request.file_ids)}: {file_id}")
            
            file_info = get_uploaded_file(file_id)
            file_path = file_info["temp_path"]
            config = request.parse_configs[i]
            
            # Parse with enhanced parser
            parse_result = enhanced_parser.parse_with_range(
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
            final_result = parse_result
            if request.enable_cleaning:
                print(f"🧹 Applying data cleaning to {file_info['original_name']}...")
                cleaning_result = data_cleaner.clean_parsed_data(parse_result)
                
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
                    print(f"⚠️  Data cleaning failed, using uncleaned data")
                    final_result['cleaning_applied'] = False
            else:
                final_result['cleaning_applied'] = False
            
            results.append({
                "file_id": file_id,
                "file_name": file_info["original_name"],
                "parse_result": final_result,
                "config": config,
                "data": final_result['data']
            })
        
        print(f"🎉 Successfully parsed all {len(results)} files")
        return {
            "success": True,
            "parsed_csvs": results,
            "total_files": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Multi-CSV parse exception: {str(e)}")
        import traceback
        print(f"📖 Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
