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
    previewFile 
  } = state;

  const handleFileSelect = async (selectedFiles) => {
    if (!selectedFiles || selectedFiles.length === 0) return;
    
    setError(null);
    setSuccess(null);
    setLoading(true);
    
    try {
      const newFiles = [];
      
      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await axios.post(`${API_BASE}/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        const bankDetection = detectBankFromFilename(file.name);
        
        newFiles.push({
          file: file,
          fileId: response.data.file_id,
          fileName: file.name,
          preview: null,
          parsedData: null,
          selectedTemplate: bankDetection.suggestedTemplate,
          columnMapping: {},
          parseConfig: {
            start_row: bankDetection.defaultStartRow,
            end_row: null,
            start_col: 0,
            end_col: null,
            encoding: bankDetection.defaultEncoding
          },
          bankDetection: bankDetection
        });
      }
      
      setUploadedFiles(prev => [...prev, ...newFiles]);
      setSuccess(`Successfully uploaded ${selectedFiles.length} file(s) with bank auto-detection`);
      setCurrentStep(2);
      
      // Auto-apply templates with delay
      for (let i = 0; i < newFiles.length; i++) {
        const fileIndex = uploadedFiles.length + i;
        if (newFiles[i].selectedTemplate) {
          setTimeout(() => {
            applyTemplate(fileIndex, newFiles[i].selectedTemplate);
          }, 500 * (i + 1));
        }
      }
      
      // Auto-preview first file
      if (newFiles.length === 1) {
        setTimeout(() => {
          previewFile(0);
        }, 1000);
      }
      
    } catch (err) {
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
