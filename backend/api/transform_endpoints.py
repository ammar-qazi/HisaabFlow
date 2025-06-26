"""
Data transformation endpoints - Refactored to use services
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import json

# Import services
from backend.services.transformation_service import TransformationService
from backend.services.export_service import ExportService

transform_router = APIRouter()

# Initialize services
transformation_service = TransformationService()
export_service = ExportService()


class TransformRequest(BaseModel):
    data: List[Dict[str, Any]]
    column_mapping: Dict[str, str]
    bank_name: str = ""
    categorization_rules: Optional[List[Dict[str, Any]]] = None
    default_category_rules: Optional[Dict[str, str]] = None
    account_mapping: Optional[Dict[str, str]] = None


@transform_router.post("/transform")
async def transform_data(request: TransformRequest):
    """Transform data to Cashew format"""
    try:
        # Use transformation service
        result = transformation_service.transform_single_data(
            data=request.data,
            column_mapping=request.column_mapping,
            bank_name=request.bank_name,
            categorization_rules=request.categorization_rules,
            default_category_rules=request.default_category_rules,
            account_mapping=getattr(request, 'account_mapping', None)
        )
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@transform_router.post("/multi-csv/transform")
async def transform_multi_csv_data(request: Request):
    """Transform multi-CSV data to Cashew format"""
    print(f" Multi-CSV transform request received")
    
    try:
        # Get raw request body for debugging
        body = await request.body()
        print(f" Raw request body size: {len(body)} bytes")
        
        # Parse JSON manually for debugging
        raw_data = json.loads(body)
        
        # Use transformation service
        result = transformation_service.transform_multi_csv_data(raw_data)
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"[ERROR]  JSON decode error: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        print(f"[ERROR]  Multi-CSV transform exception: {str(e)}")
        import traceback
        print(f" Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@transform_router.post("/apply-transfer-categorization")
async def apply_transfer_categorization(request: Request):
    """Apply transfer categorization to existing transformed data"""
    print(f" Transfer categorization request received")
    
    try:
        # Get raw request body
        body = await request.body()
        print(f" Raw request body size: {len(body)} bytes")
        
        # Parse JSON
        request_data = json.loads(body)
        
        # Use transformation service for categorization only
        result = transformation_service.apply_transfer_categorization_only(request_data)
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"[ERROR]  JSON decode error: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        print(f"[ERROR]  Transfer categorization exception: {str(e)}")
        import traceback
        print(f" Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@transform_router.post("/export")
async def export_csv_data(request: Request):
    """Export transformed data as CSV file"""
    print(f"[IN] Export request received")
    
    try:
        # Parse the request body
        body = await request.body()
        data = json.loads(body)
        
        # Use export service
        return export_service.export_to_csv(data)
        
    except json.JSONDecodeError as e:
        print(f"[ERROR]  JSON decode error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        print(f"[ERROR]  Export error: {str(e)}")
        import traceback
        print(f" Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
