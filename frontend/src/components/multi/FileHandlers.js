import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

// Bank detection function
export const detectBankFromFilename = (filename) => {
  const lowerFilename = filename.toLowerCase();
  
  if (lowerFilename.includes('nayapay')) {
    return {
      bankType: 'NayaPay',
      suggestedTemplate: 'Nayapay Configuration',
      cleanedTemplate: 'Nayapay Configuration',
      defaultStartRow: 13,
      defaultEncoding: 'utf-8'
    };
  }
  
  if (lowerFilename.includes('transferwise') || lowerFilename.includes('wise')) {
    // Determine specific Wise configuration based on filename
    if (lowerFilename.includes('usd')) {
      return {
        bankType: 'Transferwise',
        suggestedTemplate: 'Wise_Usd Configuration',
        defaultStartRow: 0,
        defaultEncoding: 'utf-8'
      };
    } else if (lowerFilename.includes('huf')) {
      return {
        bankType: 'Transferwise',
        suggestedTemplate: 'Wise_Huf Configuration',
        defaultStartRow: 0,
        defaultEncoding: 'utf-8'
      };
    } else {
      // Default to EUR for generic Wise files
      return {
        bankType: 'Transferwise',
        suggestedTemplate: 'Wise_Eur Configuration',
        defaultStartRow: 0,
        defaultEncoding: 'utf-8'
      };
    }
  }
  
  return {
    bankType: 'Unknown',
    suggestedTemplate: '',
    defaultStartRow: 0,
    defaultEncoding: 'utf-8'
  };
};

// File handling functions
export const createFileHandlers = (state) => {
  const { 
    uploadedFiles, 
    setUploadedFiles, 
    setSuccess, 
    setError, 
    setLoading, 
    setCurrentStep, 
    applyTemplate, 
    previewFile,
    previewFileById
  } = state;

  // Auto-configuration function
  const autoConfigureFile = async (fileId, bankDetection, previewData) => {
    console.log(`🔧 DEBUG: autoConfigureFile called for fileId: ${fileId}`);
    console.log(`🔧 DEBUG: bankDetection:`, bankDetection);
    console.log(`🔧 DEBUG: previewData headers:`, previewData.column_names);
    
    const detectedBank = bankDetection.detected_bank;
    const confidence = bankDetection.confidence;
    const suggestedHeaderRow = previewData.suggested_header_row || 0;
    const suggestedDataRow = previewData.suggested_data_start_row || 0;
    
    // Map backend bank names to configuration names
    const bankToConfigMap = {
      'nayapay': 'Nayapay Configuration',
      'wise_usd': 'Wise_Usd Configuration', 
      'wise_eur': 'Wise_Eur Configuration',
      'wise_huf': 'Wise_Huf Configuration'
    };
    
    const configName = bankToConfigMap[detectedBank];
    
    if (!configName || confidence < 0.1) {
      console.log(`🔧 DEBUG: Skipping auto-configuration - no config or low confidence`);
      return;
    }
    
    try {
      // Load the configuration
      console.log(`🔧 DEBUG: Loading configuration: ${configName}`);
      const configResponse = await axios.get(`${API_BASE}/api/v3/config/${encodeURIComponent(configName)}`);
      const config = configResponse.data.config;
      
      // Auto-map columns based on detected headers
      const autoColumnMapping = {};
      const headers = previewData.column_names || [];
      
      // Smart column mapping based on header names
      headers.forEach(header => {
        const headerLower = header.toLowerCase();
        if (headerLower.includes('timestamp') || headerLower.includes('date')) {
          autoColumnMapping['Date'] = header;
        } else if (headerLower.includes('amount') || headerLower.includes('balance')) {
          if (!autoColumnMapping['Amount'] && headerLower.includes('amount')) {
            autoColumnMapping['Amount'] = header;
          }
        } else if (headerLower.includes('description') || headerLower.includes('title') || headerLower.includes('note')) {
          autoColumnMapping['Title'] = header;
        } else if (headerLower.includes('type') || headerLower.includes('category')) {
          autoColumnMapping['Note'] = header;
        }
      });
      
      console.log(`🔧 DEBUG: Auto-generated column mapping:`, autoColumnMapping);
      
      // Update the file with auto-configuration
      setUploadedFiles(prev => {
        const updated = prev.map(file => {
          if (file.fileId === fileId) {
            console.log(`🔧 DEBUG: Auto-configuring file: ${file.fileName}`);
            return {
              ...file,
              selectedConfiguration: configName,
              config: config,
              preview: previewData,
              parseConfig: {
                start_row: suggestedDataRow,
                end_row: null,
                start_col: 0,
                end_col: null,
                encoding: 'utf-8'
              },
              columnMapping: {
                ...config.column_mapping,
                ...autoColumnMapping // Merge config mapping with auto-detected mapping
              },
              bankName: config.bank_name || detectedBank,
              accountMapping: config.account_mapping || {}
            };
          }
          return file;
        });
        return updated;
      });
      
      setSuccess(`✅ Auto-configured: ${detectedBank} detected (${Math.round(confidence * 100)}% confidence). Configuration "${configName}" applied with auto-mapped columns.`);
      
    } catch (error) {
      console.error(`❌ DEBUG: Auto-configuration failed:`, error);
      setError(`Auto-configuration failed for ${detectedBank}: ${error.message}`);
    }
  };

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
        
        // 🔧 AUTO-DETECTION: Trigger bank detection and auto-configuration
        setTimeout(async () => {
          console.log(`🔧 DEBUG: setTimeout triggered - starting auto-detection for ${newFiles.length} newly uploaded files`);
          
          for (let i = 0; i < newFiles.length; i++) {
            const newFile = newFiles[i];
            console.log(`🔍 DEBUG: Auto-detecting for: ${newFile.fileName} with fileId: ${newFile.fileId}`);
            
            try {
              // Call backend detection API
              const detectionResponse = await axios.get(`${API_BASE}/preview/${newFile.fileId}`);
              console.log(`✅ DEBUG: Detection response for ${newFile.fileName}:`, detectionResponse.data);
              
              const backendDetection = detectionResponse.data.bank_detection;
              if (backendDetection && backendDetection.detected_bank !== 'unknown') {
                console.log(`🏦 DEBUG: Bank detected: ${backendDetection.detected_bank} (confidence: ${backendDetection.confidence})`);
                
                // Auto-configure the file
                await autoConfigureFile(newFile.fileId, backendDetection, detectionResponse.data);
              }
            } catch (error) {
              console.error(`❌ DEBUG: Auto-detection failed for ${newFile.fileName}:`, error);
            }
            
            // Small delay between detections
            if (i < newFiles.length - 1) {
              await new Promise(resolve => setTimeout(resolve, 500));
            }
          }
          console.log(`🔧 DEBUG: All auto-detections completed`);
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

// Configuration functions
export const createConfigHandlers = (state) => {
  const { setUploadedFiles } = state;

  const updateFileConfig = (fileIndex, field, value) => {
    setUploadedFiles(prev => {
      const updated = [...prev];
      if (field.includes('.')) {
        const [parent, child] = field.split('.');
        updated[fileIndex] = {
          ...updated[fileIndex],
          [parent]: {
            ...updated[fileIndex][parent],
            [child]: value
          }
        };
      } else {
        updated[fileIndex] = {
          ...updated[fileIndex],
          [field]: value
        };
      }
      return updated;
    });
  };

  const updateColumnMapping = (fileIndex, column, value) => {
    setUploadedFiles(prev => {
      const updated = [...prev];
      updated[fileIndex] = {
        ...updated[fileIndex],
        columnMapping: {
          ...updated[fileIndex].columnMapping,
          [column]: value
        }
      };
      return updated;
    });
  };

  return { updateFileConfig, updateColumnMapping };
};

// Export function
export const exportData = async (transformedData, setSuccess, setError) => {
  if (!transformedData) return;
  
  try {
    const response = await axios.post(`${API_BASE}/export`, transformedData, {
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `multi_csv_converted_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    setSuccess('Multi-CSV export completed successfully');
    
  } catch (err) {
    setError(`Export failed: ${err.response?.data?.detail || err.message}`);
  }
};
