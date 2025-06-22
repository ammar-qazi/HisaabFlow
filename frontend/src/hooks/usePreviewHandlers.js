import { useCallback } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE = window.BACKEND_URL || 'http://localhost:8000';
const API_V1_BASE = `${API_BASE}/api/v1`;

/**
 * Custom hook for preview-related handlers
 * Handles file preview requests and auto-configuration processing
 */
export const usePreviewHandlers = (
  uploadedFiles,
  setUploadedFiles,
  setLoading,
  setError,
  applyTemplate,
  processDetectionResult,
  generateSuccessMessage
) => {

  const previewFile = useCallback(async (fileIndex) => {
    const fileData = uploadedFiles[fileIndex];
    if (!fileData) {
      setError('File data not found');
      return;
    }

    setLoading(true);
    try {
      console.log(`🔍 DEBUG: Requesting bank-aware preview for ${fileData.fileName}`);
      
      // CORRECTED API ENDPOINT
      const response = await axios.get(`${API_V1_BASE}/preview/${fileData.fileId}`);
      
      console.log('🔍 DEBUG: Preview response:', response.data);
      
      setUploadedFiles(prev => {
        const updated = [...prev];
        updated[fileIndex] = {
          ...updated[fileIndex],
          preview: {
            ...response.data,
            suggested_header_row: response.data.suggested_header_row,
            suggested_data_start_row: response.data.suggested_data_start_row
          },
          bankDetection: response.data.bank_detection
        };
        return updated;
      });
      
      if (response.data.bank_detection) {
        const autoConfigResult = processDetectionResult(response.data.bank_detection);
        
        if (autoConfigResult.shouldApply) {
          const { detectedBank, confidence, configName } = autoConfigResult;
          const headerRow = response.data.suggested_header_row;
          const dataRow = response.data.suggested_data_start_row;
          
          console.log(`🏦 Bank detected: ${detectedBank} (${confidence.toFixed(2)} confidence)`);
          console.log(`📋 Headers at row ${headerRow}, data starts at row ${dataRow}`);
          
          setUploadedFiles(prev => {
            const updated = [...prev];
            updated[fileIndex] = {
              ...updated[fileIndex],
              selectedConfiguration: configName,
              confidence: confidence, // Add this line
              detectedBank: detectedBank,   // Add this line
            };
            return updated;
          });
          
          setTimeout(() => {
            applyTemplate(fileIndex, configName, false); // Pass false to suppress the toast
          }, 500);
          
          const successMessage = generateSuccessMessage(detectedBank, confidence, configName, headerRow, dataRow);
          return successMessage; // <-- Add this line
          
        } else {
          // This case will not return a message for the consolidated toast
        }
      } else {
        // This case will not return a message for the consolidated toast
      }
      
    } catch (err) {
      console.error('❌ Preview error:', err);
      setError(`Preview failed for ${fileData.fileName}: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
    // Ensure a return value even if no success message is generated for auto-config
    // This allows Promise.all to resolve without errors for all files
    return null;
  }, [uploadedFiles, setUploadedFiles, setLoading, setError, applyTemplate, processDetectionResult, generateSuccessMessage]);

  const previewFileById = useCallback(async (fileId) => {
    const fileIndex = uploadedFiles.findIndex(f => f.fileId === fileId);
    if (fileIndex === -1) {
      setError('File not found');
      return;
    }
    
    await previewFile(fileIndex);
  }, [uploadedFiles, setError, previewFile]);

  return {
    previewFileById,
    previewFile
  };
};