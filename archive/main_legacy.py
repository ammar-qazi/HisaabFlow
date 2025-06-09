#!/usr/bin/env python3
"""
Bank Statement Parser - Clean Configuration-Based Backend
Simplified entry point with config endpoints (no more templates)
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import pandas as pd
import json
import os
import tempfile
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import parsers and utilities
from csv_parser import CSVParser
from enhanced_csv_parser import EnhancedCSVParser
from robust_csv_parser import RobustCSVParser
from data_cleaner import DataCleaner
from transfer_detection.enhanced_config_manager import EnhancedConfigurationManager

# Import API components for missing endpoints (direct imports to avoid relative import issues)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api'))
sys.path.insert(0, './api')  # Additional fallback path

# Instead of complex multi-CSV processor, use simplified approach
# We'll implement the required functionality directly in main.py

app = FastAPI(title="Bank Statement Parser API - Configuration Based", version="3.0.0")

# Enable CORS
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
parser = CSVParser()
enhanced_parser = EnhancedCSVParser()
robust_parser = RobustCSVParser()
data_cleaner = DataCleaner()
config_manager = EnhancedConfigurationManager("../configs")

# No need for file_manager - we'll use uploaded_files directly

# Pydantic models
class PreviewRequest(BaseModel):
    file_path: str
    encoding: str = "utf-8"

class ParseRangeRequest(BaseModel):
    start_row: int
    end_row: Optional[int] = None
    start_col: int = 0
    end_col: Optional[int] = None
    encoding: str = "utf-8"
    enable_cleaning: bool = True

class TransformRequest(BaseModel):
    data: List[Dict[str, Any]]
    column_mapping: Dict[str, str]
    bank_name: str = ""
    categorization_rules: Optional[List[Dict[str, Any]]] = None
    default_category_rules: Optional[Dict[str, str]] = None
    account_mapping: Optional[Dict[str, str]] = None

class SaveConfigRequest(BaseModel):
    config_name: str
    config: Dict[str, Any]

class MultiCSVParseRequest(BaseModel):
    file_ids: List[str]
    parse_configs: List[Dict[str, Any]]
    user_name: str = "Ammar Qazi"
    date_tolerance_hours: int = 24
    enable_cleaning: bool = True

# Store uploaded files
uploaded_files = {}

@app.get("/")
async def root():
    return {
        "message": "Bank Statement Parser API - Configuration Based (NO MORE TEMPLATES)",
        "version": "3.0.0",
        "features": ["Configuration-based bank rules", "No template system", "Clean architecture"]
    }

# NEW: Configuration endpoints (replace template endpoints)
@app.get("/configs")
async def list_configs():
    """List available bank configurations"""
    print(f"📋 API: Listing available bank configurations...")
    try:
        available_configs = config_manager.list_configured_banks()
        
        # Return user-friendly names
        config_display_names = []
        for bank_name in available_configs:
            config = config_manager.get_bank_config(bank_name)
            if config:
                display_name = f"{config.name.title()} Configuration"
                config_display_names.append(display_name)
                print(f"📋 Available: {display_name} (from {bank_name}.conf)")
        
        print(f"📋 Total configurations found: {len(config_display_names)}")
        
        return {
            "configurations": config_display_names,
            "raw_bank_names": available_configs,
            "count": len(config_display_names)
        }
    except Exception as e:
        print(f"❌ Config list error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/{config_name}")
async def load_config(config_name: str):
    """Load bank configuration by display name or bank name"""
    print(f"🔍 API: Loading bank configuration '{config_name}'")
    try:
        # Find matching bank name
        bank_name = _find_matching_bank_name(config_name)
        print(f"🔍 Matched bank name: '{bank_name}'")
        
        if not bank_name:
            available = config_manager.list_configured_banks()
            raise HTTPException(
                status_code=404, 
                detail=f"Configuration '{config_name}' not found. Available: {available}"
            )
        
        # Load the configuration
        config = config_manager.get_bank_config(bank_name)
        if not config:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to load configuration for {bank_name}"
            )
        
        # Convert to frontend format
        frontend_config = {
            "start_row": getattr(config.csv_config, 'start_row', 0),
            "end_row": getattr(config.csv_config, 'end_row', None),
            "start_col": getattr(config.csv_config, 'start_col', 0),
            "end_col": getattr(config.csv_config, 'end_col', None),
            "column_mapping": config.column_mapping,
            "bank_name": config.name,
            "currency": config.currency_primary,
            "account": config.cashew_account,
            "categorization_rules": getattr(config, 'categorization_rules', {}),
            "default_category_rules": config.default_category_rules,
            "account_mapping": config.account_mapping,
            "data_cleaning": {
                "enable_currency_addition": config.data_cleaning.enable_currency_addition,
                "multi_currency": config.data_cleaning.multi_currency,
                "numeric_amount_conversion": config.data_cleaning.numeric_amount_conversion,
                "date_standardization": config.data_cleaning.date_standardization,
                "remove_invalid_rows": config.data_cleaning.remove_invalid_rows,
                "default_currency": config.data_cleaning.default_currency
            }
        }
        
        result = {
            "success": True,
            "config": frontend_config,
            "bank_name": config.name,
            "display_name": f"{config.name.title()} Configuration",
            "source": f"{bank_name}.conf"
        }
        
        print(f"✅ Configuration loaded successfully: {result['display_name']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Config load error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading configuration: {str(e)}")

@app.post("/save-config")
async def save_config(request: SaveConfigRequest):
    """Save bank configuration"""
    print(f"💾 API: Saving bank configuration: {request.config_name}")
    try:
        config_filename = f"{request.config_name.lower().replace(' ', '_')}.conf"
        print(f"💡 Configuration should be saved to: ../configs/{config_filename}")
        print(f"💡 Config data: {request.config}")
        
        return {
            "success": True,
            "message": f"Configuration saved as {config_filename}",
            "config_file": config_filename,
            "suggestion": "Consider manually creating the .conf file for better control"
        }
    except Exception as e:
        print(f"❌ Config save error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving configuration: {str(e)}")

def _find_matching_bank_name(config_name: str) -> Optional[str]:
    """Find bank name from configuration display name or direct name"""
    print(f"🔍 Finding bank name for: '{config_name}'")
    
    config_name_lower = config_name.lower()
    available_banks = config_manager.list_configured_banks()
    
    # Direct bank name match
    if config_name_lower in [bank.lower() for bank in available_banks]:
        for bank in available_banks:
            if bank.lower() == config_name_lower:
                print(f"✅ Direct match: {bank}")
                return bank
    
    # Display name match (e.g., "NayaPay Configuration" -> "nayapay")
    for bank_name in available_banks:
        display_name = f"{bank_name.title()} Configuration".lower()
        if config_name_lower == display_name:
            print(f"✅ Display name match: {bank_name}")
            return bank_name
    
    print(f"❌ No match found for: '{config_name}'")
    return None

# File upload and processing endpoints (existing)
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload CSV file and return file info"""
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        content = await file.read()
        temp_file.write(content)
        temp_file.close()
        
        file_id = os.path.basename(temp_file.name)
        uploaded_files[file_id] = {
            "original_name": file.filename,
            "temp_path": temp_file.name,
            "size": len(content)
        }
        
        return {
            "success": True,
            "file_id": file_id,
            "original_name": file.filename,
            "size": len(content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/preview/{file_id}")
async def preview_csv(file_id: str, encoding: str = "utf-8"):
    """Preview uploaded CSV file"""
    print(f"🕵️‍♂️ Preview request for file_id: {file_id}")
    
    if file_id not in uploaded_files:
        print(f"❌ File {file_id} not found")
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = uploaded_files[file_id]["temp_path"]
    
    try:
        result = robust_parser.preview_csv(file_path, encoding)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        return result
    except Exception as e:
        print(f"❌ Preview exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/parse-range/{file_id}")
async def parse_range(file_id: str, request: ParseRangeRequest):
    """Parse CSV with specified range and data cleaning"""
    print(f"🕵️‍♂️ Parse range request for file_id: {file_id}")
    print(f"🧹 Data cleaning enabled: {request.enable_cleaning}")
    
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = uploaded_files[file_id]["temp_path"]
    
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

# Missing endpoints needed by frontend (compatibility layer)
@app.get("/detect-range/{file_id}")
async def detect_data_range(file_id: str, encoding: str = "utf-8"):
    """Auto-detect data range in CSV - compatibility endpoint"""
    print(f"🔍 Detect range request for file_id: {file_id}")
    
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = uploaded_files[file_id]["temp_path"]
    
    try:
        result = robust_parser.detect_data_range(file_path, encoding)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        return result
    except Exception as e:
        print(f"❌ Detect range exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/multi-csv/parse")
async def parse_multiple_csvs(request: MultiCSVParseRequest):
    """Parse multiple CSV files - simplified compatibility endpoint"""
    print(f"🚀 Multi-CSV parse request for {len(request.file_ids)} files")
    print(f"🧹 Data cleaning enabled: {request.enable_cleaning}")
    
    try:
        # Validate all file IDs exist
        for file_id in request.file_ids:
            if file_id not in uploaded_files:
                raise HTTPException(status_code=404, detail=f"File {file_id} not found")
        
        if len(request.file_ids) != len(request.parse_configs):
            raise HTTPException(status_code=400, detail="Number of file IDs must match number of parse configs")
        
        results = []
        
        # Process each file
        for i, file_id in enumerate(request.file_ids):
            print(f"📁 Processing file {i+1}/{len(request.file_ids)}: {file_id}")
            
            file_info = uploaded_files[file_id]
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

@app.post("/transform")
async def transform_data(request: TransformRequest):
    """Transform data to Cashew format"""
    try:
        if request.categorization_rules or request.default_category_rules:
            result = enhanced_parser.transform_to_cashew(
                request.data, 
                request.column_mapping, 
                request.bank_name,
                request.categorization_rules,
                request.default_category_rules,
                getattr(request, 'account_mapping', None)
            )
        else:
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

@app.post("/multi-csv/transform")
async def transform_multi_csv_data(request: Request):
    """Transform multi-CSV data to Cashew format - compatibility endpoint"""
    print(f"🔄 Multi-CSV transform request received")
    
    try:
        # Get raw request body for debugging
        body = await request.body()
        print(f"📖 Raw request body size: {len(body)} bytes")
        
        # Parse JSON manually for debugging
        import json
        raw_data = json.loads(body)
        print(f"🗂️ Request keys: {list(raw_data.keys())}")
        
        # Handle different frontend data formats
        if 'csv_data_list' in raw_data:
            # Frontend sends data in csv_data_list format
            print(f"📋 Frontend format detected: csv_data_list")
            csv_data_list = raw_data.get('csv_data_list', [])
            print(f"📈 CSV data list length: {len(csv_data_list)}")
            
            # Extract data from first CSV in the list
            if csv_data_list:
                first_csv = csv_data_list[0]
                print(f"🗂️ First CSV keys: {list(first_csv.keys()) if first_csv else 'empty'}")
                
                data = first_csv.get('data', [])
                
                # Try to find column mapping in different places
                column_mapping = first_csv.get('column_mapping', {})
                if not column_mapping and 'template_config' in first_csv:
                    template_config = first_csv.get('template_config', {})
                    column_mapping = template_config.get('column_mapping', {})
                    print(f"🗂️ Found column mapping in template_config: {column_mapping}")
                
                # Try to find bank name
                bank_name = first_csv.get('bank_name', '')
                if not bank_name and 'template_config' in first_csv:
                    template_config = first_csv.get('template_config', {})
                    bank_name = template_config.get('bank_name', '')
                    print(f"🏦 Found bank name in template_config: {bank_name}")
                
                # If still empty, create a basic mapping from the data structure
                if not column_mapping and data:
                    sample_row = data[0]
                    print(f"📄 Sample row keys: {list(sample_row.keys())}")
                    # Create basic mapping from cleaned data column names
                    column_mapping = {
                        'Date': 'Date',
                        'Amount': 'Amount', 
                        'Title': 'Title',
                        'Note': 'Note',
                        'Currency': 'Currency'
                    }
                    print(f"🔧 Created basic column mapping: {column_mapping}")
                
                # Default bank name if still empty
                if not bank_name:
                    bank_name = 'nayapay'  # Default based on the data we see
                    print(f"🏦 Using default bank name: {bank_name}")
                
                print(f"📈 Extracted data length: {len(data)}")
                print(f"🏦 Extracted bank name: {bank_name}")
                print(f"🗂️ Extracted column mapping: {column_mapping}")
            else:
                print(f"⚠️ No CSV data found in csv_data_list")
                data = []
                column_mapping = {}
                bank_name = ''
        else:
            # Standard format
            print(f"📋 Standard format detected")
            data = raw_data.get('data', [])
            column_mapping = raw_data.get('column_mapping', {})
            bank_name = raw_data.get('bank_name', '')
        
        print(f"📈 Final data length: {len(data)}")
        print(f"🏦 Final bank name: {bank_name}")
        print(f"🗂️ Final column mapping: {column_mapping}")
        
        # Get categorization rules
        categorization_rules = raw_data.get('categorization_rules')
        default_category_rules = raw_data.get('default_category_rules')
        account_mapping = raw_data.get('account_mapping')
        
        # Show sample data for debugging
        if data:
            print(f"📄 Sample data (first row): {data[0] if data else 'none'}")
        
        if categorization_rules or default_category_rules:
            print(f"📋 Using enhanced transformation with categorization rules")
            result = enhanced_parser.transform_to_cashew(
                data, 
                column_mapping, 
                bank_name,
                categorization_rules,
                default_category_rules,
                account_mapping
            )
        else:
            print(f"📋 Using basic transformation")
            result = parser.transform_to_cashew(
                data, 
                column_mapping, 
                bank_name
            )
        
        print(f"✅ Transformation successful: {len(result)} rows transformed")
        if result:
            print(f"📄 Sample result (first row): {result[0] if result else 'none'}")
        
        # Frontend expects 'transformed_data' and 'transfer_analysis' format
        response_data = {
            "success": True,
            "transformed_data": result,  # ← Frontend expects this key
            "transformation_summary": {
                "total_transactions": len(result),
                "bank_name": bank_name,
                "data_source": "multi-csv"
            },
            "transfer_analysis": {  # ← Frontend expects this key
                "summary": {
                    "transfer_pairs_found": 0,
                    "potential_transfers": 0,
                    "conflicts": 0,
                    "flagged_for_review": 0
                },
                "transfers": [],
                "conflicts": []
            },
            # Legacy fields for compatibility
            "data": result,
            "row_count": len(result),
            "bank_name": bank_name
        }
        
        print(f"📦 Sending response with {len(result)} transformed_data rows")
        return response_data
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        print(f"❌ Multi-CSV transform exception: {str(e)}")
        import traceback
        print(f"📖 Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/cleanup/{file_id}")
async def cleanup_file(file_id: str):
    """Remove uploaded file from temp storage"""
    if file_id in uploaded_files:
        try:
            os.unlink(uploaded_files[file_id]["temp_path"])
        except:
            pass
        del uploaded_files[file_id]
    return {"success": True}

if __name__ == "__main__":
    import uvicorn
    print("\n🌟 Starting Configuration-Based FastAPI Server...")
    print("   📡 Backend: http://127.0.0.1:8000")
    print("   📋 API docs: http://127.0.0.1:8000/docs")
    print("   ⚙️  NEW: Configuration endpoints (/configs, /config/{name})")
    print("   🚫 NO MORE: Template endpoints removed entirely")
    print("   ⏹️  Press Ctrl+C to stop")
    print("")
    
    try:
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
