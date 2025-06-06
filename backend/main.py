from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import pandas as pd
import json
import os
import tempfile
from csv_parser import CSVParser
from enhanced_csv_parser import EnhancedCSVParser
from robust_csv_parser import RobustCSVParser
from data_cleaner import DataCleaner
from transfer_detector import TransferDetector
from transfer_detector_improved import ImprovedTransferDetector
from transfer_detector_enhanced_ammar import TransferDetector as EnhancedAmmarTransferDetector

app = FastAPI(title="Bank Statement Parser API", version="2.0.0")

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

# Initialize parsers and cleaner
parser = CSVParser()
enhanced_parser = EnhancedCSVParser()
robust_parser = RobustCSVParser()
data_cleaner = DataCleaner()

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
    enable_cleaning: bool = True  # NEW: Enable data cleaning step

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
    enable_cleaning: bool = True  # NEW: Enable data cleaning step

class MultiCSVTransformRequest(BaseModel):
    csv_data_list: List[Dict[str, Any]]
    user_name: str = "Ammar Qazi"
    enable_transfer_detection: bool = True
    date_tolerance_hours: int = 24
    bank_rules_settings: Optional[Dict[str, bool]] = None

class SaveTemplateRequest(BaseModel):
    template_name: str
    config: Dict[str, Any]

# Store uploaded files temporarily
uploaded_files = {}

@app.get("/")
async def root():
    return {"message": "Bank Statement Parser API with Enhanced Ammar Transfer Detection", "version": "2.0.0"}

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
        return result
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
    
    return result

@app.post("/parse-range/{file_id}")
async def parse_range(file_id: str, request: ParseRangeRequest):
    """Parse CSV with specified range - NOW WITH DATA CLEANING"""
    print(f"🕵️‍♂️ Parse range request for file_id: {file_id}")
    print(f"🔢 Parameters: start_row={request.start_row}, end_row={request.end_row}, start_col={request.start_col}, end_col={request.end_col}")
    print(f"🧹 Data cleaning enabled: {request.enable_cleaning}")
    
    if file_id not in uploaded_files:
        print(f"❌ File {file_id} not found in uploaded_files: {list(uploaded_files.keys())}")
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = uploaded_files[file_id]["temp_path"]
    print(f"📁 Processing file: {file_path}")
    
    try:
        # STEP 1: DATA PARSING
        print(f"\
🚀 STEP 1: DATA PARSING")
        
        # Try enhanced parser first, then robust parser as fallback
        enhanced_result = enhanced_parser.parse_with_range(
            file_path, 
            request.start_row, 
            request.end_row, 
            request.start_col, 
            request.end_col, 
            request.encoding
        )
        
        robust_result = robust_parser.parse_with_range(
            file_path, 
            request.start_row, 
            request.end_row, 
            request.start_col, 
            request.end_col, 
            request.encoding
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
        
        if not parse_result['success']:
            print(f"❌ Both parsers failed: {parse_result.get('error', 'Unknown error')}")
            error_detail = parse_result.get('error', 'Unknown parsing error')
            raise HTTPException(status_code=400, detail=f"Parsing failed: {error_detail}")
        
        print(f"✅ Parse successful using {parser_used} parser: {parse_result.get('row_count', 0)} rows")
        
        # STEP 2: DATA CLEANING (NEW)
        final_result = parse_result
        if request.enable_cleaning:
            print(f"\
🚀 STEP 2: DATA CLEANING")
            
            cleaning_result = data_cleaner.clean_parsed_data(parse_result)
            
            if cleaning_result['success']:
                # Replace parsed data with cleaned data
                final_result = {
                    'success': True,
                    'headers': [col for col in cleaning_result['data'][0].keys()] if cleaning_result['data'] else [],
                    'data': cleaning_result['data'],
                    'row_count': cleaning_result['row_count'],
                    'parser_used': parser_used,
                    'cleaning_applied': True,
                    'cleaning_summary': cleaning_result['cleaning_summary'],
                    'updated_column_mapping': cleaning_result.get('updated_column_mapping', {}),  # NEW: Include updated mapping
                    'original_headers': parse_result.get('headers', [])  # NEW: Keep original headers for reference
                }
                print(f"✅ Data cleaning successful: {cleaning_result['row_count']} clean rows")
            else:
                print(f"⚠️  Data cleaning failed: {cleaning_result.get('error', 'Unknown error')}")
                print(f"🔄 Continuing with uncleaned data...")
                final_result['cleaning_applied'] = False
                final_result['cleaning_error'] = cleaning_result.get('error', 'Unknown error')
        else:
            print(f"🚫 Data cleaning skipped")
            final_result['cleaning_applied'] = False
        
        print(f"🎉 Final result: {final_result.get('row_count', 0)} rows ready for transformation")
        return final_result
        
    except Exception as e:
        print(f"❌ Parse exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transform")
async def transform_data(request: TransformRequest):
    """Transform data to Cashew format with smart categorization"""
    try:
        # Use enhanced parser if categorization rules are provided
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

@app.post("/save-template")
async def save_template(request: SaveTemplateRequest):
    """Save parsing template"""
    try:
        os.makedirs("../templates", exist_ok=True)
        template_path = parser.save_template(
            request.template_name, 
            request.config, 
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
        
        return {
            "success": True,
            "config": config
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Template load error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading template: {str(e)}")

@app.post("/multi-csv/parse")
async def parse_multiple_csvs(request: MultiCSVParseRequest):
    """Parse multiple CSV files with individual configurations - NOW WITH DATA CLEANING"""
    try:
        print(f"🚀 Multi-CSV parse request received for {len(request.file_ids)} files")
        print(f"📋 File IDs: {request.file_ids}")
        print(f"🧹 Data cleaning enabled: {request.enable_cleaning}")
        
        # Simple validation first
        if not request.file_ids:
            raise HTTPException(status_code=400, detail="No file IDs provided")
        
        if len(request.file_ids) != len(request.parse_configs):
            raise HTTPException(status_code=400, detail="Number of file IDs must match number of parse configs")
        
        results = []
        
        # Test each file_id exists
        for file_id in request.file_ids:
            if file_id not in uploaded_files:
                raise HTTPException(status_code=404, detail=f"File {file_id} not found")
        
        # Process each file
        for i, file_id in enumerate(request.file_ids):
            print(f"📁 Processing file {i+1}/{len(request.file_ids)}: {file_id}")
            
            file_info = uploaded_files[file_id]
            file_path = file_info["temp_path"]
            config = request.parse_configs[i]
            
            print(f"📄 File: {file_info['original_name']} at {file_path}")
            print(f"🔧 Config: start_row={config.get('start_row', 0)}, encoding={config.get('encoding', 'utf-8')}")
            
            # STEP 1: Parse with enhanced parser
            try:
                parse_result = enhanced_parser.parse_with_range(
                    file_path,
                    config.get('start_row', 0),
                    config.get('end_row'),
                    config.get('start_col', 0),
                    config.get('end_col'),
                    config.get('encoding', 'utf-8')
                )
                
                print(f"✅ Parse result: success={parse_result.get('success', False)}, rows={parse_result.get('row_count', 0)}")
                
                if not parse_result['success']:
                    raise HTTPException(status_code=400, detail=f"Failed to parse {file_info['original_name']}: {parse_result.get('error', 'Unknown error')}")
                
                # STEP 2: Data cleaning (NEW)
                final_result = parse_result
                if request.enable_cleaning:
                    print(f"🧹 Applying data cleaning to {file_info['original_name']}...")
                    
                    # Get template config for cleaning hints
                    template_config = config.get('template_config', {})
                    
                    print(f"      DEBUG: Data before cleaning: {parse_result['data']}")
                    cleaning_result = data_cleaner.clean_parsed_data(parse_result, template_config)
                    print(f"      DEBUG: Data after cleaning: {cleaning_result['data']}")
                    if cleaning_result['success']:
                        final_result = {
                            'success': True,
                            'headers': [col for col in cleaning_result['data'][0].keys()] if cleaning_result['data'] else [],
                            'data': cleaning_result['data'],
                            'row_count': cleaning_result['row_count'],
                            'cleaning_applied': True,
                            'cleaning_summary': cleaning_result['cleaning_summary'],
                            'updated_column_mapping': cleaning_result.get('updated_column_mapping', {}),  # NEW: Include updated mapping
                            'original_headers': parse_result.get('headers', [])  # NEW: Keep original headers for reference
                        }
                        print(f"✅ Data cleaning successful: {cleaning_result['row_count']} clean rows")
                    else:
                        print(f"⚠️  Data cleaning failed for {file_info['original_name']}: {cleaning_result.get('error', 'Unknown error')}")
                        final_result['cleaning_applied'] = False
                        final_result['cleaning_error'] = cleaning_result.get('error', 'Unknown error')
                else:
                    final_result['cleaning_applied'] = False
                
                results.append({
                    "file_id": file_id,
                    "file_name": file_info["original_name"],
                    "parse_result": final_result,
                    "config": config,
                    "data": final_result['data'] # Add cleaned data
                })
                
            except Exception as parse_error:
                print(f"❌ Parse error for {file_id}: {str(parse_error)}")
                raise HTTPException(status_code=500, detail=f"Parse error for {file_info['original_name']}: {str(parse_error)}")
        
        print(f"🎉 Successfully parsed all {len(results)} files")
        return {
            "success": True,
            "parsed_csvs": results,
            "total_files": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 Unexpected error in multi-CSV parse: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        import traceback
        print(f"📚 Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/multi-csv/transform")
async def transform_multiple_csvs(request: MultiCSVTransformRequest):
    """Transform multiple CSVs with ENHANCED AMMAR TRANSFER DETECTION"""
    try:
        print(f"🚀 Multi-CSV transform request received for {len(request.csv_data_list)} files")
        print(f"👤 User: {request.user_name}, Transfer detection: {request.enable_transfer_detection}")
        
        # Log bank rules settings
        if request.bank_rules_settings:
            print(f"⚙️  Bank rules settings: {request.bank_rules_settings}")
        else:
            print(f"⚙️  Bank rules settings: Using defaults (all enabled)")
        
        # Transform each CSV individually first
        all_transformed_data = []
        transformation_results = []
        
        for i, csv_data in enumerate(request.csv_data_list):
            print(f"📁 Processing CSV: {csv_data.get('file_name', 'Unknown')}")
            csv_data['data'] = request.csv_data_list[i].get('data')
            # Get template configuration
            template_config = csv_data.get('template_config', {})
            column_mapping = template_config.get('column_mapping', {})
            bank_name = template_config.get('bank_name', csv_data.get('file_name', 'Unknown'))
            categorization_rules = template_config.get('categorization_rules', [])
            default_category_rules = template_config.get('default_category_rules')
            account_mapping = template_config.get('account_mapping')
            
            print(f"🏦 Bank: {bank_name}, Rules: {len(categorization_rules)}, Rows: {len(csv_data.get('data', []))}")
            
            # Check if data is already cleaned (has numeric amounts)
            sample_data = csv_data.get('data', [])
            if sample_data:
                sample_amount = None
                for row in sample_data[:3]:  # Check first 3 rows
                    for key, value in row.items():
                        if 'amount' in key.lower() and value is not None:
                            sample_amount = value
                            break
                    if sample_amount is not None:
                        break
                
                print(f"💰 Sample amount: {sample_amount} (type: {type(sample_amount)})")
                
                # If amounts are already numeric (cleaned), we can skip some processing
                if isinstance(sample_amount, (int, float)):
                    print(f"✅ Data appears to be already cleaned (numeric amounts)")
                else:
                    print(f"⚠️  Data appears to need cleaning (string amounts)")
            
            # Transform data
            try:
                transformed = enhanced_parser.transform_to_cashew(
                    csv_data['data'],
                    column_mapping,
                    bank_name,
                    categorization_rules,
                    default_category_rules,
                    account_mapping,
                    request.bank_rules_settings
                )
                
                print(f"✅ Transformed {len(transformed)} transactions for {csv_data.get('file_name')}")
                
                transformation_results.append({
                    "file_name": csv_data.get('file_name'),
                    "transactions": len(transformed),
                    "template_used": template_config.get('name', 'None')
                })
                
                all_transformed_data.extend(transformed)
                # Merge transformed data with original data
                for i, transformed_row in enumerate(transformed):
                    csv_data['data'][i].update(transformed_row)

            except Exception as transform_error:
                print(f"❌ Transform error for {csv_data.get('file_name')}: {str(transform_error)}")
                raise HTTPException(status_code=500, detail=f"Transform error for {csv_data.get('file_name')}: {str(transform_error)}")
        
        print(f"🎉 All transformations complete. Total transactions: {len(all_transformed_data)}")
        
        # Initialize transfer analysis with default values
        transfer_analysis = {
            'transfers': [],
            'summary': {
                'transfer_pairs_found': 0,
                'potential_transfers': 0,
                'conflicts': 0,
                'flagged_for_review': 0
            }
        }
        
        # Try transfer detection if enabled
        if request.enable_transfer_detection and len(request.csv_data_list) > 1:
            try:
                print(f"🔄 Starting ENHANCED AMMAR TRANSFER DETECTION between {len(request.csv_data_list)} CSVs...")
                print(f"💡 Features: Exchange To Amount matching, Ammar name-based detection, Currency-bank targeting")
                
                # AMMAR SPECS: Use Enhanced Ammar Transfer Detector as PRIORITY
                try:
                    transfer_detector = EnhancedAmmarTransferDetector(
                        user_name=request.user_name,
                        date_tolerance_hours=request.date_tolerance_hours
                    )
                    print("🚀 Using ENHANCED AMMAR Transfer Detector with Exchange Amount Support")
                    detector_used = "enhanced_ammar"
                except Exception as e1:
                    print(f"⚠️ Enhanced Ammar detector failed to initialize: {e1}")
                    # Fallback to improved detector
                    try:
                        transfer_detector = ImprovedTransferDetector(
                            user_name=request.user_name,
                            date_tolerance_hours=request.date_tolerance_hours
                        )
                        print("⚠️  Using Standard Improved Transfer Detector (Enhanced Ammar not available)")
                        detector_used = "improved"
                    except Exception as e2:
                        print(f"⚠️ Improved detector also failed: {e2}")
                        # Last fallback to basic detector
                        transfer_detector = TransferDetector(
                            user_name=request.user_name,
                            date_tolerance_hours=request.date_tolerance_hours
                        )
                        print("⚠️  Using Basic Transfer Detector (all enhanced detectors failed)")
                        detector_used = "basic"
                
                # Detect transfers
                print(f"🔍 Running transfer detection with {detector_used} detector...")
                transfer_analysis = transfer_detector.detect_transfers(request.csv_data_list)
                print(f"✅ Transfer detection complete: {transfer_analysis['summary']}")
                
                # Apply transfer categorization if transfers were detected
                if transfer_analysis and transfer_analysis['transfers']:
                    print(f"🔄 Applying transfer categorization to {len(transfer_analysis['transfers'])} pairs...")
                    
                    transfer_matches = transfer_detector.apply_transfer_categorization(
                        request.csv_data_list, 
                        transfer_analysis['transfers']
                    )
                    
                    print(f"📝 Created {len(transfer_matches)} transfer matches for balance correction")
                    
                    # Apply balance corrections with better matching due to cleaned data
                    balance_corrections_applied = 0
                    
                    for i, transaction in enumerate(all_transformed_data):
                        for match in transfer_matches:
                            # Improved matching with cleaned numeric amounts
                            trans_amount = float(transaction.get('Amount', '0'))
                            match_amount = float(match['amount'])
                            amount_match = abs(trans_amount - match_amount) < 0.01
                            date_match = transaction.get('Date', '').startswith(match['date'])
                            
                            if amount_match and date_match:
                                all_transformed_data[i]['Category'] = match['category']
                                all_transformed_data[i]['Note'] = match['note']
                                all_transformed_data[i]['_transfer_pair_id'] = match['pair_id']
                                all_transformed_data[i]['_transfer_type'] = match['transfer_type']
                                all_transformed_data[i]['_is_transfer'] = True
                                all_transformed_data[i]['_detector_used'] = detector_used
                                all_transformed_data[i]['_match_strategy'] = match.get('match_strategy', 'traditional')
                                balance_corrections_applied += 1
                                break
                    
                    print(f"✅ Transfer categorization applied - {balance_corrections_applied} balance corrections")
                    
                    # Log transfer detection results for Ammar
                    exchange_matches = len([t for t in transfer_analysis['transfers'] if t.get('match_strategy') == 'exchange_amount'])
                    traditional_matches = len([t for t in transfer_analysis['transfers'] if t.get('match_strategy') == 'traditional'])
                    
                    if exchange_matches > 0:
                        print(f"🎯 AMMAR SPEC SUCCESS: {exchange_matches} Exchange Amount matches detected!")
                    if traditional_matches > 0:
                        print(f"🎯 Traditional amount matches: {traditional_matches}")
                    
                    # Add transfer detection info to analysis
                    transfer_analysis['detector_used'] = detector_used
                    transfer_analysis['exchange_amount_matches'] = exchange_matches
                    transfer_analysis['traditional_matches'] = traditional_matches
                else:
                    print(f"⚠️  No transfers detected")
                
            except Exception as transfer_error:
                print(f"⚠️ Transfer detection failed: {str(transfer_error)}")
                print(f"🔄 Continuing without transfer detection...")
                import traceback
                print(f"📚 Full error traceback: {traceback.format_exc()}")
        else:
            print(f"🚫 Transfer detection skipped (not enabled or insufficient CSVs)")
        
        return {
            "success": True,
            "transformed_data": all_transformed_data,
            "transfer_analysis": transfer_analysis,
            "transformation_summary": {
                "total_transactions": len(all_transformed_data),
                "files_processed": len(request.csv_data_list),
                "transfers_detected": len(transfer_analysis['transfers']) if transfer_analysis else 0,
                "balance_corrections_applied": len([t for t in all_transformed_data if t.get('Category') == 'Balance Correction']),
                "detector_used": transfer_analysis.get('detector_used', 'none'),
                "exchange_amount_matches": transfer_analysis.get('exchange_amount_matches', 0),
                "traditional_matches": transfer_analysis.get('traditional_matches', 0)
            },
            "file_results": transformation_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 Unexpected transform error: {str(e)}")
        import traceback
        print(f"📚 Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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
    print("\n🌟 Starting Enhanced FastAPI server with Data Cleaning...")
    print("   📡 Backend will be available at: http://127.0.0.1:8000")
    print("   📋 API docs available at: http://127.0.0.1:8000/docs")
    print("   🧹 NEW: Data cleaning pipeline integrated")
    print("   💱 NEW: Automatic currency column addition")
    print("   📊 NEW: Numeric amount standardization")
    print("   💱 NEW: Enhanced Transfer Detection with Exchange Amount Support")
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
