import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

// Processing functions
export const createProcessingHandlers = (state) => {
  const { 
    uploadedFiles, 
    setUploadedFiles, 
    setLoading, 
    setError, 
    setSuccess,
    setParsedResults,
    setTransformedData,
    setTransferAnalysis,
    setCurrentStep
  } = state;

  const parseAllFiles = async () => {
    if (uploadedFiles.length === 0) return;
    
    setError(null);
    setSuccess(null);
    setLoading(true);
    
    try {
      const fileIds = uploadedFiles.map(f => f.fileId);
      
      // 🔧 CRITICAL FIX: Use bank-detected row configuration instead of manual parseConfig
      const parseConfigs = await Promise.all(uploadedFiles.map(async (file) => {
        let finalConfig = { ...file.parseConfig };
        
        // Check if file has bank-detected header/data row information from preview
        if (file.preview && file.preview.suggested_data_start_row !== undefined) {
          console.log(`🔧 Using bank-detected data_start_row=${file.preview.suggested_data_start_row} for ${file.fileName}`);
          finalConfig.start_row = file.preview.suggested_data_start_row;
        } else if (file.preview && file.preview.suggested_header_row !== undefined) {
          // If we have header row but not data start row, use header_row + 1
          const dataStartRow = file.preview.suggested_header_row + 1;
          console.log(`🔧 Using calculated data_start_row=${dataStartRow} (header_row + 1) for ${file.fileName}`);
          finalConfig.start_row = dataStartRow;
        } else {
          console.log(`📝 Using manual parseConfig start_row=${finalConfig.start_row} for ${file.fileName}`);
        }
        
        return finalConfig;
      }));
      
      console.log('🚀 Sending parse request with bank-aware configs:', { fileIds, parseConfigs });
      
      const response = await axios.post(`${API_BASE}/multi-csv/parse`, {
        file_ids: fileIds,
        parse_configs: parseConfigs
      });
      
      console.log('Parse response:', response.data);
      
      const results = response.data.parsed_csvs;
      
      setUploadedFiles(prev => {
        return prev.map((file, index) => {
          const result = results.find(r => r.file_id === file.fileId);
          if (result) {
            const parseResult = result.parse_result || {};
            const safeParseResult = {
              success: parseResult.success || false,
              headers: parseResult.headers || [],
              data: parseResult.data || [],
              row_count: parseResult.row_count || 0,
              cleaning_applied: parseResult.cleaning_applied || false,
              bank_info: parseResult.bank_info || {}  // 🏦 STORE BANK INFO FROM PARSE RESPONSE
            };
            
            console.log(`🏦 Storing bank_info for ${file.fileName}:`, parseResult.bank_info);
            
            return {
              ...file,
              parsedData: safeParseResult
            };
          }
          return file;
        });
      });
      
      setParsedResults(results);
      setSuccess(`Successfully parsed ${results.length} CSV files`);
      setCurrentStep(3);
      
    } catch (err) {
      console.error('Parse error:', err);
      setError(`Parsing failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const prepareConfig = async (file) => {
    let config = {};
    
    // **UPDATED: Check for new configuration system first**
    if (file.selectedConfiguration) {
      try {
        console.log(`🔍 Loading configuration: ${file.selectedConfiguration}`);
        const configResponse = await axios.get(`${API_BASE}/api/v3/config/${encodeURIComponent(file.selectedConfiguration)}`);
        config = configResponse.data.config;
        console.log(`✅ Configuration loaded:`, config);
      } catch (err) {
        console.warn(`⚠️  Could not load configuration ${file.selectedConfiguration}:`, err);
        
        // No fallback needed - all templates have been migrated to configurations
        console.warn(`⚠️ Configuration '${file.selectedConfiguration}' not found - may need to refresh configurations list`);
        config = {}; // Use empty config and rely on manual column mapping
      }
    } else if (file.selectedTemplate) {
      // Legacy template support - convert to new configuration format
      try {
        console.log(`🔄 Converting legacy template to configuration: ${file.selectedTemplate}`);
        const configResponse = await axios.get(`${API_BASE}/api/v3/config/${encodeURIComponent(file.selectedTemplate)}`);
        config = configResponse.data.config;
        console.log(`✅ Legacy template converted to configuration:`, config);
      } catch (err) {
        console.warn(`❌ Could not convert legacy template ${file.selectedTemplate} to configuration:`, err);
      }
    } else if (file.config) {
      // Use stored configuration from file object
      console.log(`📁 Using stored configuration from file object`);
      config = file.config;
    }
    
    let finalColumnMapping = {};
    
    if (config.column_mapping) {
      finalColumnMapping = { ...config.column_mapping };
      
      // Override with user-selected mappings
      Object.keys(file.columnMapping || {}).forEach(key => {
        const userValue = file.columnMapping[key];
        if (userValue && userValue !== '' && userValue !== '-- Select Column --') {
          finalColumnMapping[key] = userValue;
        }
      });
    } else {
      finalColumnMapping = { ...file.columnMapping };
    }
    
    // Remove empty mappings
    Object.keys(finalColumnMapping).forEach(key => {
      if (!finalColumnMapping[key] || finalColumnMapping[key] === '' || finalColumnMapping[key] === '-- Select Column --') {
        delete finalColumnMapping[key];
      }
    });
    
    console.log(`🗺️  Final column mapping for ${file.fileName}:`, finalColumnMapping);
    console.log(`🏦 Bank name: ${config.bank_name || file.bankName || file.fileName.replace('.csv', '').replace(/[_-]/g, ' ')}`);
    
    return {
      ...config,
      column_mapping: finalColumnMapping,
      bank_name: config.bank_name || file.bankName || file.fileName.replace('.csv', '').replace(/[_-]/g, ' ')
    };
  };

  const transformAllFiles = async () => {
    if (uploadedFiles.length === 0) return;
    
    setError(null);
    setSuccess(null);
    setLoading(true);
    
    try {
      const csvDataList = await Promise.all(uploadedFiles.map(async (file) => {
        const completeConfig = await prepareConfig(file);
        const bankInfo = file.parsedData?.bank_info || {};  // 🏦 GET BANK INFO FROM PARSE DATA
        
        console.log(`🏦 Including bank_info for ${file.fileName}:`, bankInfo);
        
        return {
          filename: file.fileName,  // 🔍 Use 'filename' to match backend expectation
          data: file.parsedData?.data || [],
          headers: file.parsedData?.headers || [],
          config: completeConfig, // **UPDATED: Use 'config' instead of 'template_config'**
          template_config: completeConfig, // Keep for backward compatibility
          bank_name: completeConfig.bank_name,
          column_mapping: completeConfig.column_mapping,
          bank_info: bankInfo  // 🏦 PASS BANK INFO TO TRANSFORM ENDPOINT
        };
      }));
      
      const response = await axios.post(`${API_BASE}/multi-csv/transform`, {
        csv_data_list: csvDataList
      });
      
      setTransformedData(response.data.transformed_data);
      setTransferAnalysis(response.data.transfer_analysis);
      setSuccess(`Transformation complete! ${response.data.transformation_summary.total_transactions} transactions processed`);
      setCurrentStep(4);
      
    } catch (err) {
      setError(`Transformation failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return { parseAllFiles, transformAllFiles };
};
