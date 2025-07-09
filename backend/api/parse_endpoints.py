"""
CSV parsing endpoints with preprocessing layer - Refactored to use services
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os

# Import services
from backend.services.preview_service import PreviewService
from backend.services.parsing_service import ParsingService, ParseConfig
from backend.services.multi_csv_service import MultiCSVService

# Import file helper function
try:
    from backend.api.file_endpoints import get_uploaded_file
except ImportError:
    # Fallback implementation
    def get_uploaded_file(file_id):
        # This will be populated by file_endpoints when it loads
        return None

# Import models from centralized location
from backend.api.models import (
    MultiCSVParseRequest, 
    ParseRangeRequest, 
    PreviewResponse, 
    DetectRangeResponse, 
    ParseResponse, 
    MultiCSVParseResponse
)

parse_router = APIRouter()

# Initialize services
preview_service = PreviewService()
parsing_service = ParsingService()
multi_csv_service = MultiCSVService()


@parse_router.get("/preview/{file_id}", response_model=PreviewResponse)
async def preview_csv(file_id: str, encoding: str = "utf-8", header_row: int = None):
    """Preview uploaded CSV file with bank-aware header detection"""
    print(f"‍ Preview request for file_id: {file_id}, header_row: {header_row}")
    
    file_info = get_uploaded_file(file_id)
    if not file_info:
        print(f"[ERROR]  File {file_id} not found")
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = file_info["temp_path"]
    filename = file_info["original_name"]
    
    # Use preview service
    result = preview_service.preview_csv_file(file_path, filename, encoding, header_row)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return result


@parse_router.get("/detect-range/{file_id}", response_model=DetectRangeResponse)
async def detect_data_range(file_id: str, encoding: str = "utf-8"):
    """Auto-detect data range in CSV"""
    print(f" Detect range request for file_id: {file_id}")
    
    file_info = get_uploaded_file(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = file_info["temp_path"]
    
    # Use preview service for range detection
    result = preview_service.detect_data_range(file_path, encoding)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return result


@parse_router.post("/parse-range/{file_id}", response_model=ParseResponse)
async def parse_range(file_id: str, request: ParseRangeRequest):
    """Parse CSV with specified range and data cleaning"""
    print(f"‍ Parse range request for file_id: {file_id}")
    
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


@parse_router.post("/multi-csv/parse", response_model=MultiCSVParseResponse)
async def parse_multiple_csvs(
    request: MultiCSVParseRequest,
    use_pydantic: bool = Query(False, description="Return Pydantic models instead of dicts")
):
    """Parse multiple CSV files"""
    print(f"[START] Multi-CSV parse request for {len(request.file_ids)} files")
    
    try:
        # Validate all file IDs exist and add file_id to file_info
        file_infos = []
        for file_id in request.file_ids:
            file_info = get_uploaded_file(file_id)
            if not file_info:
                raise HTTPException(status_code=404, detail=f"File {file_id} not found")
            # Add file_id to the file_info structure
            file_info_with_id = file_info.copy()
            file_info_with_id['file_id'] = file_id
            file_infos.append(file_info_with_id)
        
        if len(request.file_ids) != len(request.parse_configs):
            raise HTTPException(status_code=400, detail="Number of file IDs must match number of parse configs")
        
        # Use multi-CSV service
        result = multi_csv_service.parse_multiple_files(
            file_infos=file_infos,
            parse_configs=request.parse_configs,
            enable_cleaning=request.enable_cleaning,
            use_pydantic=use_pydantic  # ADD this
        )
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR]  Multi-CSV parse exception: {str(e)}")
        import traceback
        print(f" Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
