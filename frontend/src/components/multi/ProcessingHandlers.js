import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

// Processing functions
export const createProcessingHandlers = (state) => {
  const { 
    uploadedFiles, 
    setUploadedFiles, 
    userName, 
    dateTolerance, 
    enableTransferDetection, 
    bankRulesSettings,
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
      const parseConfigs = uploadedFiles.map(f => f.parseConfig);
      
      console.log('Sending parse request:', { fileIds, parseConfigs });
      
      const response = await axios.post(`${API_BASE}/multi-csv/parse`, {
        file_ids: fileIds,
        parse_configs: parseConfigs,
        user_name: userName,
        date_tolerance_hours: dateTolerance
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
              cleaning_applied: parseResult.cleaning_applied || false
            };
            
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
        
        // Fallback to legacy template system
        if (file.selectedTemplate) {
          try {
            console.log(`🔄 Falling back to legacy template: ${file.selectedTemplate}`);
            const templateResponse = await axios.get(`${API_BASE}/template/${file.selectedTemplate}`);
            config = templateResponse.data.config;
          } catch (templateErr) {
            console.warn(`❌ Legacy template fallback failed:`, templateErr);
          }
        }
      }
    } else if (file.selectedTemplate) {
      // Legacy template support
      try {
        console.log(`🔄 Using legacy template: ${file.selectedTemplate}`);
        const templateResponse = await axios.get(`${API_BASE}/template/${file.selectedTemplate}`);
        config = templateResponse.data.config;
      } catch (err) {
        console.warn(`❌ Could not load legacy template ${file.selectedTemplate}:`, err);
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
        
        return {
          file_name: file.fileName,
          data: file.parsedData?.data || [],
          headers: file.parsedData?.headers || [],
          config: completeConfig, // **UPDATED: Use 'config' instead of 'template_config'**
          template_config: completeConfig, // Keep for backward compatibility
          bank_name: completeConfig.bank_name,
          column_mapping: completeConfig.column_mapping
        };
      }));
      
      const response = await axios.post(`${API_BASE}/multi-csv/transform`, {
        csv_data_list: csvDataList,
        user_name: userName,
        enable_transfer_detection: enableTransferDetection,
        date_tolerance_hours: dateTolerance,
        bank_rules_settings: bankRulesSettings
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
