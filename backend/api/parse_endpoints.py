"""
CSV parsing endpoints with preprocessing layer - Refactored to use services
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import sys

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import services
try:
    from services.preview_service import PreviewService
    from services.parsing_service import ParsingService, ParseConfig
    from services.multi_csv_service import MultiCSVService
except ImportError:
    # Fallback path for import issues
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    services_path = os.path.join(backend_path, 'services')
    sys.path.insert(0, services_path)
    from preview_service import PreviewService
    from parsing_service import ParsingService, ParseConfig
    from multi_csv_service import MultiCSVService

# Import file helper function
try:
    from api.file_endpoints import get_uploaded_file
except ImportError:
    # Fallback implementation
    def get_uploaded_file(file_id):
        # This will be populated by file_endpoints when it loads
        return None

parse_router = APIRouter()

# Initialize services
preview_service = PreviewService()
parsing_service = ParsingService()
multi_csv_service = MultiCSVService()


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
async def preview_csv(file_id: str, encoding: str = "utf-8", header_row: int = None):
    """Preview uploaded CSV file with bank-aware header detection"""
    print(f"🕵️‍♂️ Preview request for file_id: {file_id}, header_row: {header_row}")
    
    file_info = get_uploaded_file(file_id)
    if not file_info:
        print(f"❌ File {file_id} not found")
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = file_info["temp_path"]
    filename = file_info["original_name"]
    
    # Use preview service
    result = preview_service.preview_csv_file(file_path, filename, encoding, header_row)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return result


@parse_router.get("/detect-range/{file_id}")
async def detect_data_range(file_id: str, encoding: str = "utf-8"):
    """Auto-detect data range in CSV"""
    print(f"🔍 Detect range request for file_id: {file_id}")
    
    file_info = get_uploaded_file(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = file_info["temp_path"]
    
    # Use preview service for range detection
    result = preview_service.detect_data_range(file_path, encoding)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return result


@parse_router.post("/parse-range/{file_id}")
async def parse_range(file_id: str, request: ParseRangeRequest):
    """Parse CSV with specified range and data cleaning"""
    print(f"🕵️‍♂️ Parse range request for file_id: {file_id}")
    
    file_info = get_uploaded_file(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = file_info["temp_path"]
    filename = file_info["original_name"]
    
    # Create parse config
    config = ParseConfig(
        start_row=request.start_row,
        end_row=request.end_row,
        start_col=request.start_col,
        end_col=request.end_col,
        encoding=request.encoding,
        enable_cleaning=request.enable_cleaning
    )
    
    # Use parsing service
    result = parsing_service.parse_single_file(file_path, filename, config)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return result


@parse_router.post("/multi-csv/parse")
async def parse_multiple_csvs(request: MultiCSVParseRequest):
    """Parse multiple CSV files"""
    print(f"🚀 Multi-CSV parse request for {len(request.file_ids)} files")
    
    try:
        # Validate all file IDs exist
        file_infos = []
        for file_id in request.file_ids:
            file_info = get_uploaded_file(file_id)
            if not file_info:
                raise HTTPException(status_code=404, detail=f"File {file_id} not found")
            file_infos.append(file_info)
        
        if len(request.file_ids) != len(request.parse_configs):
            raise HTTPException(status_code=400, detail="Number of file IDs must match number of parse configs")
        
        # Use multi-CSV service
        result = multi_csv_service.parse_multiple_files(
            file_infos=file_infos,
            parse_configs=request.parse_configs,
            user_name=request.user_name,
            enable_cleaning=request.enable_cleaning
        )
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Multi-CSV parse exception: {str(e)}")
        import traceback
        print(f"📖 Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
