from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import pandas as pd
import json
import os
import tempfile
import math
import numpy as np
from csv_parser import CSVParser
from enhanced_csv_parser import EnhancedCSVParser
from robust_csv_parser import RobustCSVParser
from transfer_detector import TransferDetector

def sanitize_for_json(obj):
    """
    Comprehensively sanitize data to be JSON-serializable
    Handles all possible NaN/infinity sources from pandas and numpy
    """
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, tuple):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, set):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, (np.float32, np.float64)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    elif pd.isna(obj):
        return None
    elif hasattr(obj, 'isnull') and obj.isnull():
        return None
    elif str(obj).lower() in ['nan', 'na', 'null', 'none', 'inf', '-inf']:
        return None
    elif obj is None:
        return None
    elif isinstance(obj, (pd.Timestamp, pd.DatetimeIndex)):
        try:
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return None
    elif hasattr(obj, 'dtype') and 'datetime' in str(obj.dtype):
        try:
            return pd.to_datetime(obj).strftime('%Y-%m-%d %H:%M:%S')
        except:
            return None
    else:
        # Convert to string and check for problematic values
        str_obj = str(obj)
        if str_obj.lower() in ['nan', 'na', 'null', 'none', 'inf', '-inf']:
            return None
        return str_obj

def safe_parse_with_range(parser, file_path, start_row, end_row, start_col, end_col, encoding):
    """Safely parse CSV with comprehensive sanitization"""
    try:
        result = parser.parse_with_range(file_path, start_row, end_row, start_col, end_col, encoding)
        
        # Extra sanitization layer for parse results
        if result.get('success') and result.get('data'):
            # Sanitize each row of data
            sanitized_data = []
            for row in result['data']:
                sanitized_row = {}
                for key, value in row.items():
                    sanitized_row[str(key)] = sanitize_for_json(value)
                sanitized_data.append(sanitized_row)
            
            result['data'] = sanitized_data
            result['headers'] = [str(h) for h in result.get('headers', [])]
        
        return sanitize_for_json(result)
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'data': [],
            'headers': [],
            'row_count': 0
        }

def safe_transform_to_cashew(parser, data, column_mapping, bank_name, categorization_rules, default_category_rules, account_mapping):
    """Safely transform data with comprehensive sanitization"""
    try:
        # First sanitize input data
        sanitized_input_data = sanitize_for_json(data)
        
        # Perform transformation
        result = parser.transform_to_cashew(
            sanitized_input_data,
            column_mapping,
            bank_name,
            categorization_rules,
            default_category_rules,
            account_mapping
        )
        
        # Sanitize the result
        return sanitize_for_json(result)
    except Exception as e:
        print(f"Transform error: {e}")
        return []

def safe_detect_transfers(transfer_detector, csv_data_list):
    """Safely detect transfers with comprehensive sanitization"""
    try:
        # Sanitize input first
        sanitized_csv_data = sanitize_for_json(csv_data_list)
        
        # Perform detection
        result = transfer_detector.detect_transfers(sanitized_csv_data)
        
        # Sanitize the result
        return sanitize_for_json(result)
    except Exception as e:
        print(f"Transfer detection error: {e}")
        return {
            'transfers': [],
            'potential_transfers': [],
            'conflicts': [],
            'flagged_transactions': [],
            'summary': {
                'total_transactions': 0,
                'transfer_pairs_found': 0,
                'potential_transfers': 0,
                'conflicts': 0,
                'flagged_for_review': 0
            }
        }

def safe_apply_transfer_categorization(transfer_detector, transformed_data, transfers):
    """Safely apply transfer categorization with comprehensive sanitization"""
    try:
        # Sanitize inputs
        sanitized_data = sanitize_for_json(transformed_data)
        sanitized_transfers = sanitize_for_json(transfers)
        
        # Apply categorization
        result = transfer_detector.apply_transfer_categorization(sanitized_data, sanitized_transfers)
        
        # Sanitize the result
        return sanitize_for_json(result)
    except Exception as e:
        print(f"Transfer categorization error: {e}")
        return sanitize_for_json(transformed_data)  # Return original data if error

app = FastAPI(title="Bank Statement Parser API", version="1.0.0")

# Enable CORS for frontend communication - MUST be first middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware for debugging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"🔍 {request.method} {request.url} - Origin: {request.headers.get('origin', 'None')}")
    response = await call_next(request)
    print(f"📤 Response: {response.status_code}")
    return response

# Initialize parsers
parser = CSVParser()
enhanced_parser = EnhancedCSVParser()
robust_parser = RobustCSVParser()

# Pydantic models for request/response
class PreviewRequest(BaseModel):
    file_path: str
    encoding: str = "utf-8"

class ParseRangeRequest(BaseModel):
    start_row: int
    end_row: Optional[int] = None
    start_col: int = 0
    end_col: Optional[int] = None
    encoding: str = "utf-8"

class TransformRequest(BaseModel):
    data: List[Dict[str, Any]]
    column_mapping: Dict[str, str]
    bank_name: str = ""
    categorization_rules: Optional[List[Dict[str, Any]]] = None
    default_category_rules: Optional[Dict[str, str]] = None
    account_mapping: Optional[Dict[str, str]] = None

class MultiCSVParseRequest(BaseModel):
    file_ids: List[str]
    parse_configs: List[Dict[str, Any]]  # Individual parse config for each CSV
    user_name: str = "Ammar Qazi"  # For transfer detection
    date_tolerance_hours: int = 24

class MultiCSVTransformRequest(BaseModel):
    csv_data_list: List[Dict[str, Any]]
    user_name: str = "Ammar Qazi"
    enable_transfer_detection: bool = True
    date_tolerance_hours: int = 24

class SaveTemplateRequest(BaseModel):
    template_name: str
    config: Dict[str, Any]

# Store uploaded files temporarily
uploaded_files = {}

@app.get("/")
async def root():
    return {"message": "Bank Statement Parser API", "version": "1.0.0"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload CSV file and return file info"""
    try:
        # Create temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        content = await file.read()
        temp_file.write(content)
        temp_file.close()
        
        # Store file info
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
        print(f"❌ File {file_id} not found in uploaded_files: {list(uploaded_files.keys())}")
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = uploaded_files[file_id]["temp_path"]
    print(f"📁 Reading file: {file_path}")
    
    try:
        # Use robust parser for better CSV handling
        result = robust_parser.preview_csv(file_path, encoding)
        
        if not result['success']:
            print(f"❌ Preview failed: {result.get('error', 'Unknown error')}")
            raise HTTPException(status_code=400, detail=result['error'])
        
        print(f"✅ Preview successful: {result.get('total_rows', 0)} rows")
        return sanitize_for_json(result)
    except Exception as e:
        print(f"❌ Preview exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/detect-range/{file_id}")
async def detect_data_range(file_id: str, encoding: str = "utf-8"):
    """Auto-detect data range in CSV"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = uploaded_files[file_id]["temp_path"]
    result = robust_parser.detect_data_range(file_path, encoding)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return sanitize_for_json(result)

@app.post("/parse-range/{file_id}")
async def parse_range(file_id: str, request: ParseRangeRequest):
    """Parse CSV with specified range"""
    print(f"🕵️‍♂️ Parse range request for file_id: {file_id}")
    print(f"🔢 Parameters: start_row={request.start_row}, end_row={request.end_row}, start_col={request.start_col}, end_col={request.end_col}")
    
    if file_id not in uploaded_files:
        print(f"❌ File {file_id} not found in uploaded_files: {list(uploaded_files.keys())}")
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = uploaded_files[file_id]["temp_path"]
    print(f"📁 Processing file: {file_path}")
    
    try:
        # Try enhanced parser first, then robust parser as fallback
        enhanced_result = safe_parse_with_range(
            enhanced_parser, file_path, 
            request.start_row, request.end_row, 
            request.start_col, request.end_col, 
            request.encoding
        )
        
        robust_result = safe_parse_with_range(
            robust_parser, file_path,
            request.start_row, request.end_row,
            request.start_col, request.end_col,
            request.encoding
        )
        
        # Choose the better result (robust parser if it has more data)
        result = enhanced_result
        parser_used = "enhanced"
        
        if (robust_result['success'] and 
            robust_result.get('row_count', 0) > enhanced_result.get('row_count', 0)):
            result = robust_result
            parser_used = "robust"
        elif not enhanced_result['success'] and robust_result['success']:
            result = robust_result
            parser_used = "robust (fallback)"
        
        if not result['success']:
            print(f"❌ Both parsers failed: {result.get('error', 'Unknown error')}")
            error_detail = result.get('error', 'Unknown parsing error')
            raise HTTPException(status_code=400, detail=f"Parsing failed: {error_detail}")
        
        print(f"✅ Parse successful using {parser_used} parser: {result.get('row_count', 0)} rows")
        return sanitize_for_json(result)
    except Exception as e:
        print(f"❌ Parse exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transform")
async def transform_data(request: TransformRequest):
    """Transform data to Cashew format with smart categorization"""
    try:
        # Use enhanced parser if categorization rules are provided
        if request.categorization_rules or request.default_category_rules:
            result = safe_transform_to_cashew(
                enhanced_parser,
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
            result = sanitize_for_json(result)
        
        return sanitize_for_json({
            "success": True,
            "data": result,
            "row_count": len(result)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export")
async def export_data(data: List[Dict[str, Any]], filename: str = "export.csv"):
    """Export transformed data as CSV"""
    try:
        sanitized_data = sanitize_for_json(data)
        df = pd.DataFrame(sanitized_data)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        df.to_csv(temp_file.name, index=False)
        
        return FileResponse(
            temp_file.name,
            media_type="text/csv",
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-template")
async def save_template(request: SaveTemplateRequest):
    """Save parsing template"""
    try:
        os.makedirs("../templates", exist_ok=True)
        sanitized_config = sanitize_for_json(request.config)
        template_path = parser.save_template(
            request.template_name, 
            sanitized_config, 
            "../templates"
        )
        return {
            "success": True,
            "template_path": template_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/templates")
async def list_templates():
    """List available templates"""
    try:
        template_dir = "../templates"
        if not os.path.exists(template_dir):
            return {"templates": []}
        
        templates = []
        for file in os.listdir(template_dir):
            if file.endswith('.json'):
                template_name = file[:-5]  # Remove .json extension
                templates.append(template_name)
        
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/template/{template_name}")
async def load_template(template_name: str):
    """Load saved template"""
    print(f"🔍 Loading template: {template_name}")
    template_path = f"../templates/{template_name}.json"
    print(f"📁 Template path: {template_path}")
    
    try:
        # Check if file exists
        if not os.path.exists(template_path):
            print(f"❌ Template file not found: {template_path}")
            available_files = os.listdir("../templates") if os.path.exists("../templates") else []
            print(f"📂 Available templates: {available_files}")
            raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
        
        # Try enhanced parser first, then fall back to basic parser
        try:
            config = enhanced_parser.load_template(template_name, "../templates")
            print(f"✅ Template loaded successfully with enhanced parser")
        except Exception as e1:
            print(f"⚠️ Enhanced parser failed: {e1}, trying basic parser...")
            try:
                config = parser.load_template(template_name, "../templates")
                print(f"✅ Template loaded successfully with basic parser")
            except Exception as e2:
                print(f"❌ Both parsers failed: {e2}")
                raise e2
        
        return sanitize_for_json({
            "success": True,
            "config": config
        })
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Template load error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading template: {str(e)}")

@app.post("/multi-csv/parse")
async def parse_multiple_csvs(request: MultiCSVParseRequest):
    """Parse multiple CSV files with individual configurations"""
    try:
        results = []
        
        for i, file_id in enumerate(request.file_ids):
            if file_id not in uploaded_files:
                raise HTTPException(status_code=404, detail=f"File {file_id} not found")
            
            file_path = uploaded_files[file_id]["temp_path"]
            config = request.parse_configs[i] if i < len(request.parse_configs) else {}
            
            # Try robust parser first for better CSV handling, then enhanced parser
            robust_result = safe_parse_with_range(
                robust_parser, file_path,
                config.get('start_row', 0),
                config.get('end_row'),
                config.get('start_col', 0),
                config.get('end_col'),
                config.get('encoding', 'utf-8')
            )
            
            enhanced_result = safe_parse_with_range(
                enhanced_parser, file_path,
                config.get('start_row', 0),
                config.get('end_row'),
                config.get('start_col', 0),
                config.get('end_col'),
                config.get('encoding', 'utf-8')
            )
            
            # Choose the better result (robust parser if it has more data)
            parse_result = enhanced_result
            parser_used = "enhanced"
            
            if (robust_result['success'] and 
                robust_result.get('row_count', 0) > enhanced_result.get('row_count', 0)):
                parse_result = robust_result
                parser_used = "robust"
            elif not enhanced_result['success'] and robust_result['success']:
                parse_result = robust_result
                parser_used = "robust (fallback)"
            
            print(f"📊 Used {parser_used} parser for {uploaded_files[file_id]['original_name']}: {parse_result.get('row_count', 0)} rows")
            
            if not parse_result['success']:
                raise HTTPException(status_code=400, detail=f"Failed to parse {file_id}: {parse_result['error']}")
            
            results.append({
                "file_id": file_id,
                "file_name": uploaded_files[file_id]["original_name"],
                "parse_result": parse_result,
                "config": config
            })
        
        return sanitize_for_json({
            "success": True,
            "parsed_csvs": results,
            "total_files": len(results)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/multi-csv/transform")
async def transform_multiple_csvs(request: MultiCSVTransformRequest):
    """Transform multiple CSVs with transfer detection"""
    try:
        # Initialize transfer detector
        transfer_detector = TransferDetector(
            user_name=request.user_name,
            date_tolerance_hours=request.date_tolerance_hours
        )
        
        # Detect transfers if enabled
        transfer_analysis = None
        if request.enable_transfer_detection:
            transfer_analysis = safe_detect_transfers(transfer_detector, request.csv_data_list)
        
        # Transform each CSV individually
        all_transformed_data = []
        transformation_results = []
        
        for csv_data in request.csv_data_list:
            # Get template configuration
            template_config = csv_data.get('template_config', {})
            column_mapping = template_config.get('column_mapping', {})
            bank_name = template_config.get('bank_name', csv_data.get('file_name', 'Unknown'))
            categorization_rules = template_config.get('categorization_rules', [])
            default_category_rules = template_config.get('default_category_rules')
            account_mapping = template_config.get('account_mapping')
            
            # Transform data
            transformed = safe_transform_to_cashew(
                enhanced_parser,
                csv_data['data'],
                column_mapping,
                bank_name,
                categorization_rules,
                default_category_rules,
                account_mapping
            )
            
            transformation_results.append({
                "file_name": csv_data.get('file_name'),
                "transactions": len(transformed),
                "template_used": template_config.get('name', 'None')
            })
            
            all_transformed_data.extend(transformed)
        
        # Apply transfer categorization if transfers were detected
        if transfer_analysis and transfer_analysis['transfers']:
            all_transformed_data = safe_apply_transfer_categorization(
                transfer_detector, 
                all_transformed_data, 
                transfer_analysis['transfers']
            )
        
        return sanitize_for_json({
            "success": True,
            "transformed_data": all_transformed_data,
            "transfer_analysis": transfer_analysis,
            "transformation_summary": {
                "total_transactions": len(all_transformed_data),
                "files_processed": len(request.csv_data_list),
                "transfers_detected": len(transfer_analysis['transfers']) if transfer_analysis else 0,
                "balance_corrections_applied": len([t for t in all_transformed_data if t.get('Category') == 'Balance Correction'])
            },
            "file_results": transformation_results
        })
        
    except Exception as e:
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
    print("\n🌟 Starting FastAPI server...")
    print("   📡 Backend will be available at: http://127.0.0.1:8000")
    print("   📋 API docs available at: http://127.0.0.1:8000/docs")
    print("   ⏹️  Press Ctrl+C to stop")
    print("")
    
    try:
        uvicorn.run(
            "main:app",  # Use import string instead of app object
            host="127.0.0.1", 
            port=8000, 
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        print("   💡 Try: python main.py")
        print("   💡 Or: uvicorn main:app --host 127.0.0.1 --port 8000 --reload")
