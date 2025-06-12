import { useCallback } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

/**
 * Custom hook for preview-related handlers
 * Handles file preview requests and auto-configuration processing
 */
export const usePreviewHandlers = ({
  uploadedFiles,
  setUploadedFiles,
  setLoading,
  setError,
  setSuccess,
  applyTemplate,
  processDetectionResult,
  generateSuccessMessage
}) => {

  const previewFileById = useCallback(async (fileId) => {
    const fileIndex = uploadedFiles.findIndex(f => f.fileId === fileId);
    if (fileIndex === -1) {
      setError('File not found');
      return;
    }
    
    await previewFile(fileIndex);
  }, [uploadedFiles, setError]);

  const previewFile = useCallback(async (fileIndex) => {
    const fileData = uploadedFiles[fileIndex];
    if (!fileData) {
      setError('File data not found');
      return;
    }

    setLoading(true);
    try {
      // Let backend handle bank-aware header detection automatically
      console.log(`🔍 DEBUG: Requesting bank-aware preview for ${fileData.fileName}`);
      const response = await axios.get(`${API_BASE}/preview/${fileData.fileId}`);
      
      console.log('🔍 DEBUG: Preview response:', response.data);
      
      // Store preview data with bank-detected information
      setUploadedFiles(prev => {
        const updated = [...prev];
        updated[fileIndex] = {
          ...updated[fileIndex],
          preview: {
            ...response.data,
            suggested_header_row: response.data.suggested_header_row,
            suggested_data_start_row: response.data.suggested_data_start_row
          }
        };
        return updated;
      });
      
      // Process auto-configuration based on backend bank detection
      const autoConfigResult = processDetectionResult(response.data.bank_detection);
      
      if (autoConfigResult.shouldApply) {
        const { detectedBank, confidence, configName } = autoConfigResult;
        const headerRow = response.data.suggested_header_row;
        const dataRow = response.data.suggested_data_start_row;
        
        console.log(`🏦 Bank detected: ${detectedBank} (${confidence.toFixed(2)} confidence)`);
        console.log(`📋 Headers at row ${headerRow}, data starts at row ${dataRow}`);
        
        // Update the selectedConfiguration immediately
        setUploadedFiles(prev => {
          const updated = [...prev];
          updated[fileIndex] = {
            ...updated[fileIndex],
            selectedConfiguration: configName
          };
          return updated;
        });
        
        // Apply the configuration after a short delay
        setTimeout(() => {
          applyTemplate(fileIndex, configName);
        }, 500);
        
        const successMessage = generateSuccessMessage(detectedBank, confidence, configName, headerRow, dataRow);
        setSuccess(successMessage);
        
      } else {
        if (autoConfigResult.configName) {
          setSuccess(autoConfigResult.message + ' Please select manually.');
        } else {
          console.log(`📝 Using manual configuration for ${fileData.fileName}`);
          setSuccess(`Preview loaded for ${fileData.fileName} - using manual configuration`);
        }
      }
      
    } catch (err) {
      console.error('❌ Preview error:', err);
      setError(`Preview failed for ${fileData.fileName}: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  }, [uploadedFiles, setUploadedFiles, setLoading, setError, setSuccess, applyTemplate, processDetectionResult, generateSuccessMessage]);

  return {
    previewFileById,
    previewFile
  };
};
