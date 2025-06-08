"""
FastAPI route handlers
Centralized endpoint definitions using the modular components
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Dict, List, Any
import pandas as pd
import tempfile
from .models import *
from .file_manager import FileManager
from .csv_processor import CSVProcessor
from .multi_csv_processor import MultiCSVProcessor
from .config_manager import ConfigManager
from ..csv_parser import CSVParser


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(title="Bank Statement Parser API", version="2.0.0")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        print(f"🔍 {request.method} {request.url} - Origin: {request.headers.get('origin', 'None')}")
        response = await call_next(request)
        print(f"📤 Response: {response.status_code}")
        return response
    
    # Initialize components
    file_manager = FileManager()
    csv_processor = CSVProcessor()
    multi_csv_processor = MultiCSVProcessor(file_manager)
    config_manager = ConfigManager()
    parser = CSVParser()  # For transform endpoint
    
    # Basic endpoints
    @app.get("/")
    async def root():
        return {"message": "Bank Statement Parser API with Enhanced Transfer Detection", "version": "2.0.0"}
    
    # File management endpoints
    @app.post("/upload")
    async def upload_file(file: UploadFile = File(...)):
        """Upload CSV file and return file info"""
        return await file_manager.upload_file(file)
    
    @app.delete("/cleanup/{file_id}")
    async def cleanup_file(file_id: str):
        """Remove uploaded file from temp storage"""
        file_manager.cleanup_file(file_id)
        return {"success": True}
    
    # CSV processing endpoints
    @app.get("/preview/{file_id}")
    async def preview_csv(file_id: str, encoding: str = "utf-8"):
        """Preview uploaded CSV file"""
        print(f"🕵️‍♂️ Preview request for file_id: {file_id}")
        file_path = file_manager.get_file_path(file_id)
        return csv_processor.preview_csv(file_path, encoding)
    
    @app.get("/detect-range/{file_id}")
    async def detect_data_range(file_id: str, encoding: str = "utf-8"):
        """Auto-detect data range in CSV"""
        file_path = file_manager.get_file_path(file_id)
        return csv_processor.detect_data_range(file_path, encoding)
    
    @app.post("/parse-range/{file_id}")
    async def parse_range(file_id: str, request: ParseRangeRequest):
        """Parse CSV with specified range and optional data cleaning"""
        print(f"🕵️‍♂️ Parse range request for file_id: {file_id}")
        file_path = file_manager.get_file_path(file_id)
        return csv_processor.parse_range(file_path, request)
    
    # Multi-CSV endpoints
    @app.post("/multi-csv/parse")
    async def parse_multiple_csvs(request: MultiCSVParseRequest):
        """Parse multiple CSV files with individual configurations"""
        return multi_csv_processor.parse_multiple_csvs(request)
    
    @app.post("/multi-csv/transform")
    async def transform_multiple_csvs(request: MultiCSVTransformRequest):
        """Transform multiple CSVs with enhanced transfer detection"""
        return multi_csv_processor.transform_multiple_csvs(request)
    
    # Single CSV transformation (legacy support)
    @app.post("/transform")
    async def transform_data(request: TransformRequest):
        """Transform data to Cashew format with smart categorization"""
        try:
            # Use enhanced parser if categorization rules are provided
            if request.categorization_rules or request.default_category_rules:
                from ..enhanced_csv_parser import EnhancedCSVParser
                enhanced_parser = EnhancedCSVParser()
                result = enhanced_parser.transform_to_cashew(
                    request.data, 
                    request.column_mapping, 
                    request.bank_name,
                    request.categorization_rules,
                    request.default_category_rules,
                    getattr(request, 'account_mapping', None)
                )
            else:
                # Fall back to basic parser
                result = parser.transform_to_cashew(
                    request.data, 
                    request.column_mapping, 
                    request.bank_name
                )
            return {
                "success": True,
                "data": result,
                "row_count": len(result)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Export endpoint
    @app.post("/export")
    async def export_data(data: List[Dict[str, Any]], filename: str = "export.csv"):
        """Export transformed data as CSV"""
        try:
            df = pd.DataFrame(data)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
            df.to_csv(temp_file.name, index=False)
            
            return FileResponse(
                temp_file.name,
                media_type="text/csv",
                filename=filename
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Bank Configuration management endpoints
    @app.post("/save-config")
    async def save_config(request: SaveTemplateRequest):
        """Save bank configuration"""
        print(f"💾 API: Saving bank configuration: {request.template_name}")
        return config_manager.save_config(request)
    
    @app.get("/configs")
    async def list_configs():
        """List available bank configurations"""
        print(f"📋 API: Listing available bank configurations...")
        result = config_manager.list_configs()
        print(f"📋 API: Found {len(result.get('configurations', []))} configurations")
        print(f"📋 API: Configurations = {result.get('configurations', [])}")
        return result
    
    @app.get("/config/{config_name}")
    async def load_config(config_name: str):
        """Load bank configuration"""
        print(f"🔍 API: Loading bank configuration '{config_name}'")
        result = config_manager.load_config(config_name)
        print(f"🔍 API: Configuration load success = {result.get('success', False)}")
        if result.get('success'):
            print(f"🔍 API: Loaded bank = '{result.get('bank_name', 'UNKNOWN')}'")
        return result
    
    return app
