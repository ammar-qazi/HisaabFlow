"""
File upload and management endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import os

file_router = APIRouter()

# Store uploaded files
uploaded_files = {}

@file_router.post("/upload")
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

@file_router.delete("/cleanup/{file_id}")
async def cleanup_file(file_id: str):
    """Remove uploaded file from temp storage"""
    if file_id in uploaded_files:
        try:
            os.unlink(uploaded_files[file_id]["temp_path"])
        except:
            pass
        del uploaded_files[file_id]
    return {"success": True}

def get_uploaded_file(file_id: str):
    """Get uploaded file info - helper function for other modules"""
    return uploaded_files.get(file_id)
