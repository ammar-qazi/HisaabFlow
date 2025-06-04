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
from transfer_detector import TransferDetector

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
        return result
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
    """Parse multiple CSV files with individual configurations"""
    try:
        print(f"🚀 Multi-CSV parse request received for {len(request.file_ids)} files")
        print(f"📋 File IDs: {request.file_ids}")
        
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
            
            # Parse with enhanced parser
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
                
                results.append({
                    "file_id": file_id,
                    "file_name": file_info["original_name"],
                    "parse_result": parse_result,
                    "config": config
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
    """Transform multiple CSVs with transfer detection"""
    try:
        print(f"🚀 Multi-CSV transform request received for {len(request.csv_data_list)} files")
        print(f"👤 User: {request.user_name}, Transfer detection: {request.enable_transfer_detection}")
        
        # Transform each CSV individually first
        all_transformed_data = []
        transformation_results = []
        
        for csv_data in request.csv_data_list:
            print(f"📁 Processing CSV: {csv_data.get('file_name', 'Unknown')}")
            
            # Get template configuration
            template_config = csv_data.get('template_config', {})
            column_mapping = template_config.get('column_mapping', {})
            bank_name = template_config.get('bank_name', csv_data.get('file_name', 'Unknown'))
            categorization_rules = template_config.get('categorization_rules', [])
            default_category_rules = template_config.get('default_category_rules')
            account_mapping = template_config.get('account_mapping')
            
            print(f"🏦 Bank: {bank_name}, Rules: {len(categorization_rules)}, Rows: {len(csv_data.get('data', []))}")
            
            # Transform data
            try:
                transformed = enhanced_parser.transform_to_cashew(
                    csv_data['data'],
                    column_mapping,
                    bank_name,
                    categorization_rules,
                    default_category_rules,
                    account_mapping
                )
                
                print(f"✅ Transformed {len(transformed)} transactions for {csv_data.get('file_name')}")
                
                transformation_results.append({
                    "file_name": csv_data.get('file_name'),
                    "transactions": len(transformed),
                    "template_used": template_config.get('name', 'None')
                })
                
                all_transformed_data.extend(transformed)
                
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
        
        # FIXED: Try transfer detection if enabled
        if request.enable_transfer_detection and len(request.csv_data_list) > 1:
            try:
                print(f"🔄 Starting transfer detection between {len(request.csv_data_list)} CSVs...")
                
                # Initialize transfer detector
                transfer_detector = TransferDetector(
                    user_name=request.user_name,
                    date_tolerance_hours=request.date_tolerance_hours
                )
                
                # DEBUG: Print sample data for debugging
                for idx, csv_data in enumerate(request.csv_data_list):
                    print(f"   📊 CSV {idx+1} ({csv_data.get('file_name', 'Unknown')}):") 
                    sample_transactions = csv_data.get('data', [])[:2]  # First 2 transactions
                    for trans in sample_transactions:
                        print(f"     - Amount: {trans.get('Amount', 'N/A')}, Desc: {trans.get('Description', 'N/A')[:50]}...")
                
                # Detect transfers
                transfer_analysis = transfer_detector.detect_transfers(request.csv_data_list)
                print(f"✅ Transfer detection complete: {transfer_analysis['summary']}")
                
                # Apply transfer categorization if transfers were detected
                if transfer_analysis and transfer_analysis['transfers']:
                    print(f"🔄 Applying transfer categorization to {len(transfer_analysis['transfers'])} pairs...")
                    transfer_matches = transfer_detector.apply_transfer_categorization(
                        request.csv_data_list, 
                        transfer_analysis['transfers']
                    )
                    
                    # FIXED: Apply balance corrections with enhanced matching
                    balance_corrections_applied = 0
                    
                    for i, transaction in enumerate(all_transformed_data):
                        for match in transfer_matches:
                            # Enhanced matching logic
                            amount_match = abs(float(transaction.get('Amount', '0')) - float(match['amount'])) < 0.01
                            date_match = transaction.get('Date', '').startswith(match['date'])
                            
                            if amount_match and date_match:
                                # Enhanced matching for transfer detection override
                                trans_desc = str(transaction.get('Title', '')).lower()
                                match_desc = str(match['description']).lower()
                                
                                # Simple but effective matching for transfers
                                desc_match = False
                                
                                # Direct key phrase matching (most reliable)
                                if 'sent money' in match_desc and 'sent money' in trans_desc:
                                    desc_match = True
                                elif 'incoming fund transfer' in match_desc and 'incoming fund transfer' in trans_desc:
                                    desc_match = True
                                elif 'converted' in match_desc and 'converted' in trans_desc:
                                    desc_match = True
                                else:
                                    # Fallback: check if at least 2 significant words match
                                    desc_words_trans = [word for word in trans_desc.split() if len(word) > 3]
                                    desc_words_match = [word for word in match_desc.split() if len(word) > 3]
                                    
                                    # More lenient matching for transfer override
                                    desc_match = (len(desc_words_trans) == 0 or len(desc_words_match) == 0 or 
                                                any(word in trans_desc for word in desc_words_match) or 
                                                any(word in match_desc for word in desc_words_trans))
                                
                                if desc_match:
                                    print(f"🎯 OVERRIDE: '{transaction['Category']}' → 'Balance Correction' for {trans_desc[:30]}...")
                                    all_transformed_data[i]['Category'] = match['category']
                                    all_transformed_data[i]['Note'] = match['note']
                                    all_transformed_data[i]['_transfer_pair_id'] = match['pair_id']
                                    all_transformed_data[i]['_transfer_type'] = match['transfer_type']
                                    all_transformed_data[i]['_is_transfer'] = True
                                    balance_corrections_applied += 1
                                    break
                                else:
                                    print(f"⚠️  NO MATCH: '{trans_desc[:30]}...' vs '{match_desc[:30]}...'")
                    
                    print(f"✅ Transfer categorization applied")
                else:
                    print(f"⚠️  No transfers detected - check your data patterns")
                
            except Exception as transfer_error:
                print(f"⚠️ Transfer detection failed: {str(transfer_error)}")
                print(f"📚 Transfer error traceback:")
                import traceback
                print(traceback.format_exc())
                # Continue without transfer detection rather than failing
                print(f"🔄 Continuing without transfer detection...")
        else:
            print(f"🚫 Transfer detection skipped (enabled: {request.enable_transfer_detection}, files: {len(request.csv_data_list)})")
        
        return {
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
