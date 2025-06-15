/**
 * Core file handlers
 * Main file upload and management functionality
 */
import axios from 'axios';

// Import utilities and handlers
import { detectBankFromFilename } from '../../utils/bankDetection';
import { triggerAutoDetection } from '../../handlers/autoConfigHandlers';
import { createConfigHandlers } from '../../handlers/configurationHandlers';
import { exportData } from '../../utils/exportUtils';

const API_BASE = 'http://127.0.0.1:8000';

/**
 * Creates file upload and management handlers
 */
export const createFileHandlers = (state) => {
  const { 
    uploadedFiles, 
    setUploadedFiles, 
    setSuccess, 
    setError, 
    setLoading, 
    setCurrentStep,
    dynamicBankMapping  // Add this to get access to dynamic mapping
  } = state;

  const handleFileSelect = async (selectedFiles) => {
    console.log('🔍 DEBUG: handleFileSelect called with', selectedFiles?.length, 'files');
    
    if (!selectedFiles || selectedFiles.length === 0) {
      console.log('❌ DEBUG: No files selected, returning early');
      return;
    }
    
    setError(null);
    setSuccess(null);
    setLoading(true);
    
    try {
      const newFiles = [];
      
      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];
        console.log(`🔍 DEBUG: Processing file ${i + 1}/${selectedFiles.length}: ${file.name}`);
        
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await axios.post(`${API_BASE}/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        console.log(`✅ DEBUG: Upload response for ${file.name}:`, response.data);
        
        const bankDetection = detectBankFromFilename(file.name);
        console.log(`🏦 DEBUG: Frontend bank detection for ${file.name}:`, bankDetection);
        
        newFiles.push({
          file: file,
          fileId: response.data.file_id,
          fileName: file.name,
          preview: null,
          parsedData: null,
          selectedConfiguration: '', // Start empty - will be auto-selected after detection
          columnMapping: {}, // Will be auto-populated after detection
          parseConfig: {
            start_row: bankDetection.defaultStartRow,
            end_row: null,
            start_col: 0,
            end_col: null,
            encoding: bankDetection.defaultEncoding
          },
          bankDetection: bankDetection
        });
        
        console.log(`🔍 DEBUG: Created file object for ${file.name} with fileId: ${response.data.file_id}`);
      }
      
      console.log(`🔍 DEBUG: About to update uploadedFiles. Current length: ${uploadedFiles.length}, adding: ${newFiles.length}`);
      
      setUploadedFiles(prev => {
        console.log(`🔍 DEBUG: setUploadedFiles callback - prev length: ${prev.length}`);
        const updated = [...prev, ...newFiles];
        console.log(`🔍 DEBUG: setUploadedFiles callback - new length: ${updated.length}`);
        
        // Trigger auto-detection after a short delay
        setTimeout(() => {
          triggerAutoDetection(newFiles, setUploadedFiles, setSuccess, setError, dynamicBankMapping);
        }, 1000);
        
        return updated;
      });
      
      setSuccess(`Successfully uploaded ${selectedFiles.length} file(s) with bank auto-detection`);
      setCurrentStep(2);
      
    } catch (err) {
      console.error(`❌ DEBUG: Upload error:`, err);
      setError(`Upload failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const removeFile = (fileIndex) => {
    setUploadedFiles(prev => prev.filter((_, index) => index !== fileIndex));
  };

  return { handleFileSelect, removeFile };
};

// Re-export utilities for backward compatibility
export { createConfigHandlers, exportData };
