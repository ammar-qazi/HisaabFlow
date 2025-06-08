"""
File upload and management functionality
Handles temporary file storage and cleanup for uploaded CSV files
"""
import tempfile
import os
from typing import Dict
from fastapi import UploadFile, HTTPException


class FileManager:
    """Manages uploaded file storage and cleanup"""
    
    def __init__(self):
        self.uploaded_files: Dict[str, Dict] = {}
    
    async def upload_file(self, file: UploadFile) -> Dict[str, any]:
        """Upload CSV file and return file info"""
        try:
            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            
            # Store file info
            file_id = os.path.basename(temp_file.name)
            self.uploaded_files[file_id] = {
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
    
    def get_file_path(self, file_id: str) -> str:
        """Get file path for given file ID"""
        if file_id not in self.uploaded_files:
            raise HTTPException(status_code=404, detail="File not found")
        return self.uploaded_files[file_id]["temp_path"]
    
    def get_file_info(self, file_id: str) -> Dict[str, any]:
        """Get file info for given file ID"""
        if file_id not in self.uploaded_files:
            raise HTTPException(status_code=404, detail="File not found")
        return self.uploaded_files[file_id]
    
    def cleanup_file(self, file_id: str) -> bool:
        """Remove uploaded file from temp storage"""
        if file_id in self.uploaded_files:
            try:
                os.unlink(self.uploaded_files[file_id]["temp_path"])
            except:
                pass
            del self.uploaded_files[file_id]
            return True
        return False
    
    def validate_file_ids(self, file_ids: list) -> None:
        """Validate that all file IDs exist"""
        for file_id in file_ids:
            if file_id not in self.uploaded_files:
                raise HTTPException(status_code=404, detail=f"File {file_id} not found")
