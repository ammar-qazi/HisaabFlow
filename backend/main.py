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

# Initialize parser
parser = CSVParser()

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
        result = parser.preview_csv(file_path, encoding)
        
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
    result = parser.detect_data_range(file_path, encoding)
    
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
        result = parser.parse_with_range(
            file_path, 
            request.start_row, 
            request.end_row, 
            request.start_col, 
            request.end_col, 
            request.encoding
        )
        
        if not result['success']:
            print(f"❌ Parse failed: {result.get('error', 'Unknown error')}")
            raise HTTPException(status_code=400, detail=result['error'])
        
        print(f"✅ Parse successful: {result.get('row_count', 0)} rows")
        return result
    except Exception as e:
        print(f"❌ Parse exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transform")
async def transform_data(request: TransformRequest):
    """Transform data to Cashew format"""
    try:
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
    try:
        config = parser.load_template(template_name, "../templates")
        return {
            "success": True,
            "config": config
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Template not found")

# Cleanup endpoint
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
