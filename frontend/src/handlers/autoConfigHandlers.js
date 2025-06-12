/**
 * Auto-configuration handlers
 * Manages automatic bank detection and configuration application
 */
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

/**
 * Auto-configures a file based on bank detection results
 */
export const autoConfigureFile = async (fileId, bankDetection, previewData, setUploadedFiles, setSuccess, setError) => {
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
    const autoColumnMapping = generateAutoColumnMapping(previewData.column_names || []);
    
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

/**
 * Generates automatic column mapping based on header names
 */
export const generateAutoColumnMapping = (headers) => {
  const autoColumnMapping = {};
  
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
  
  return autoColumnMapping;
};

/**
 * Triggers auto-detection and configuration for newly uploaded files
 */
export const triggerAutoDetection = async (newFiles, setUploadedFiles, setSuccess, setError) => {
  console.log(`🔧 DEBUG: Starting auto-detection for ${newFiles.length} newly uploaded files`);
  
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
        await autoConfigureFile(newFile.fileId, backendDetection, detectionResponse.data, setUploadedFiles, setSuccess, setError);
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
};
