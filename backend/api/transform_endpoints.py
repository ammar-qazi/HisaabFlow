"""
Data transformation endpoints - Refactored to use services
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import json
import os
import sys

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import services
try:
    from services.transformation_service import TransformationService
    from services.export_service import ExportService
except ImportError:
    # Fallback path for import issues
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    services_path = os.path.join(backend_path, 'services')
    sys.path.insert(0, services_path)
    from transformation_service import TransformationService
    from export_service import ExportService

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
    print(f"🔄 Multi-CSV transform request received")
    
    try:
        # Get raw request body for debugging
        body = await request.body()
        print(f"📖 Raw request body size: {len(body)} bytes")
        
        # Parse JSON manually for debugging
        raw_data = json.loads(body)
        
        # Use transformation service
        result = transformation_service.transform_multi_csv_data(raw_data)
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        print(f"❌ Multi-CSV transform exception: {str(e)}")
        import traceback
        print(f"📖 Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@transform_router.post("/export")
async def export_csv_data(request: Request):
    """Export transformed data as CSV file"""
    print(f"📥 Export request received")
    
    try:
        # Parse the request body
        body = await request.body()
        data = json.loads(body)
        
        # Use export service
        return export_service.export_to_csv(data)
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        print(f"❌ Export error: {str(e)}")
        import traceback
        print(f"📖 Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
