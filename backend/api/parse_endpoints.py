"""
CSV parsing endpoints with preprocessing layer - Refactored to use services
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional

from backend.api.dependencies import get_preview_service, get_multi_csv_service
from backend.api.file_endpoints import get_uploaded_file

# Import models from centralized location
from backend.api.models import (
    MultiCSVParseRequest,
    PreviewResponse,
    MultiCSVParseResponse
)
import logging

logger = logging.getLogger(__name__)

parse_router = APIRouter()

# Services are now injected via dependencies


@parse_router.get("/preview/{file_id}", response_model=PreviewResponse)
async def preview_csv(
    file_id: str, 
    encoding: Optional[str] = None, 
    header_row: int = None,
    preview_service = Depends(get_preview_service)
):
    """Preview uploaded CSV file with bank-aware header detection"""
    logger.debug(f"‍ Preview request for file_id: {file_id}, header_row: {header_row}")
    
    file_info = get_uploaded_file(file_id)
    if not file_info:
        logger.error(f"[ERROR]  File {file_id} not found")
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = file_info["temp_path"]
    filename = file_info["original_name"]
    
    # Use preview service
    result = preview_service.preview_csv_file(file_path, filename, encoding, header_row)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return result


@parse_router.post("/multi-csv/parse", response_model=MultiCSVParseResponse)
async def parse_multiple_csvs(
    request: MultiCSVParseRequest,
    use_pydantic: bool = Query(False, description="Return Pydantic models instead of dicts"),
    multi_csv_service = Depends(get_multi_csv_service)
):
    """Parse multiple CSV files"""
    logger.debug(f"[START] Multi-CSV parse request for {len(request.file_ids)} files")
    
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
        logger.error(f"[ERROR]  Multi-CSV parse exception: {str(e)}")
        import traceback
        logger.error(f" Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
