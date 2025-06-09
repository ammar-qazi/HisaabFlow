import React, { useState, useRef } from 'react';
import axios from 'axios';
import './index.css';

// Import modular components
import FileUploadStep from './components/single/FileUploadStep';
import DataRangeStep from './components/single/DataRangeStep';
import ColumnMappingStep from './components/single/ColumnMappingStep';
import ReviewExportStep from './components/single/ReviewExportStep';

const API_BASE = 'http://127.0.0.1:8000';

// Configure axios
axios.defaults.timeout = 10000;
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Add request/response interceptors for debugging
axios.interceptors.request.use(
  (config) => {
    console.log('🌐 Making request to:', config.url);
    return config;
  },
  (error) => {
    console.error('🚨 Request error:', error);
    return Promise.reject(error);
  }
);

axios.interceptors.response.use(
  (response) => {
    console.log('✅ Response received:', response.status);
    return response;
  },
  (error) => {
    console.error('🚨 Response error:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

function App() {
  // Core state
  const [currentStep, setCurrentStep] = useState(1);
  const [file, setFile] = useState(null);
  const [fileId, setFileId] = useState(null);
  const [preview, setPreview] = useState(null);
  const [parsedData, setParsedData] = useState(null);
  const [transformedData, setTransformedData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Range controls
  const [startRow, setStartRow] = useState(0);
  const [endRow, setEndRow] = useState('');
  const [startCol, setStartCol] = useState(0);
  const [endCol, setEndCol] = useState('');
  
  // Column mapping
  const [columnMapping, setColumnMapping] = useState({
    Date: '',
    Amount: '',
    Category: '',
    Title: '',
    Note: '',
    Account: ''
  });
  
  // Configuration management
  const [configName, setConfigName] = useState('');
  const [configurations, setConfigurations] = useState([]);
  const [selectedConfig, setSelectedConfig] = useState('');
  
  const fileInputRef = useRef(null);

  // Utility functions
  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  const resetApp = () => {
    setCurrentStep(1);
    setFile(null);
    setFileId(null);
    setPreview(null);
    setParsedData(null);
    setTransformedData(null);
    clearMessages();
  };

  // Load configurations on mount
  React.useEffect(() => {
    const loadConfigurations = async () => {
      try {
        console.log('📋 Loading available bank configurations...');
        const response = await axios.get(`${API_BASE}/configs`);
        setConfigurations(response.data.configurations || []);
        console.log('📋 Loaded configurations:', response.data.configurations);
      } catch (err) {
        console.error('📋 Failed to load configurations:', err);
        try {
          console.log('📋 Falling back to templates endpoint...');
          const fallbackResponse = await axios.get(`${API_BASE}/templates`);
          setConfigurations(fallbackResponse.data.templates || []);
        } catch (fallbackErr) {
          console.error('📋 Fallback also failed:', fallbackErr);
        }
      }
    };
    loadConfigurations();
  }, []);

  // API handlers
  const handleFileSelect = async (selectedFile) => {
    if (!selectedFile) return;
    
    clearMessages();
    setLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      console.log('📤 Uploading file:', selectedFile.name);
      const response = await axios.post(`${API_BASE}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setFile(selectedFile);
      setFileId(response.data.file_id);
      setSuccess(`File uploaded successfully: ${selectedFile.name}`);
      setCurrentStep(2);
      
      await previewFile(response.data.file_id);
      
    } catch (err) {
      console.error('📤 Upload error details:', err.response?.data);
      let errorMessage = err.response?.data?.detail || err.message;
      if (typeof errorMessage === 'object') {
        errorMessage = JSON.stringify(errorMessage);
      }
      setError(`Upload failed: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const previewFile = async (id = fileId) => {
    if (!id) return;
    
    setLoading(true);
    try {
      console.log('👀 Previewing file:', id);
      const response = await axios.get(`${API_BASE}/preview/${id}`);
      setPreview(response.data);
      
      const detectionResponse = await axios.get(`${API_BASE}/detect-range/${id}`);
      if (detectionResponse.data.success && detectionResponse.data.suggested_header_row !== null) {
        setStartRow(detectionResponse.data.suggested_header_row);
      }
      
    } catch (err) {
      console.error('👀 Preview error details:', err.response?.data);
      let errorMessage = err.response?.data?.detail || err.message;
      if (typeof errorMessage === 'object') {
        errorMessage = JSON.stringify(errorMessage);
      }
      setError(`Preview failed: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const parseWithRange = async () => {
    if (!fileId) return;
    
    clearMessages();
    setLoading(true);
    
    try {
      const requestData = {
        start_row: parseInt(startRow) || 0,
        end_row: endRow ? parseInt(endRow) : null,
        start_col: parseInt(startCol) || 0,
        end_col: endCol ? parseInt(endCol) : null,
        encoding: 'utf-8'
      };
      
      console.log('📊 Parse request data:', requestData);
      
      const response = await axios.post(`${API_BASE}/parse-range/${fileId}`, requestData);
      
      console.log('📊 Parse response:', response.data);
      
      setParsedData(response.data);
      setSuccess(`Parsed ${response.data.row_count} rows successfully${response.data.cleaning_applied ? ' with data cleaning' : ''}`);
      setCurrentStep(3);
      
      // Auto-populate column mapping
      const headers = response.data.headers;
      const newMapping = { ...columnMapping };
      
      headers.forEach(header => {
        const lowerHeader = header.toLowerCase();
        if (lowerHeader.includes('date') || lowerHeader.includes('time')) {
          newMapping.Date = header;
        } else if (lowerHeader.includes('amount') || lowerHeader.includes('value')) {
          newMapping.Amount = header;
        } else if (lowerHeader.includes('description') || lowerHeader.includes('title')) {
          newMapping.Title = header;
        } else if (lowerHeader.includes('type') || lowerHeader.includes('category')) {
          newMapping.Note = header;
        }
      });
      
      setColumnMapping(newMapping);
      
    } catch (err) {
      console.error('📊 Parse error:', err);
      let errorMessage = err.response?.data?.detail || err.message;
      if (typeof errorMessage === 'object') {
        errorMessage = JSON.stringify(errorMessage);
      }
      setError(`Parsing failed: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const transformData = async () => {
    if (!parsedData) return;
    
    clearMessages();
    setLoading(true);
    
    try {
      let categorizationRules = null;
      let defaultCategoryRules = null;
      let accountMapping = null;
      let bankName = file?.name?.split('.')[0] || 'Unknown Bank';
      
      if (selectedConfig) {
        try {
          console.log('⚙️ Loading configuration rules from:', selectedConfig);
          const configResponse = await axios.get(`${API_BASE}/config/${selectedConfig}`);
          const configData = configResponse.data.config;
          
          categorizationRules = configData.categorization_rules;
          defaultCategoryRules = configData.default_category_rules;
          accountMapping = configData.account_mapping;
          
          if (configData.bank_name) {
            bankName = configData.bank_name;
          }
          
          console.log('⚙️ Configuration rules loaded successfully');
        } catch (err) {
          console.warn('⚙️ Could not load configuration rules:', err);
        }
      }
      
      console.log('🔄 Transforming data for bank:', bankName);
      const response = await axios.post(`${API_BASE}/transform`, {
        data: parsedData.data,
        column_mapping: columnMapping,
        bank_name: bankName,
        categorization_rules: categorizationRules,
        default_category_rules: defaultCategoryRules,
        account_mapping: accountMapping
      });
      
      setTransformedData(response.data.data);
      const rulesApplied = categorizationRules ? ' with smart categorization' : '';
      setSuccess(`Transformed ${response.data.row_count} transactions successfully${rulesApplied}!`);
      setCurrentStep(4);
      
    } catch (err) {
      console.error('🔄 Transformation error:', err);
      setError(`Transformation failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const exportData = async () => {
    if (!transformedData) return;
    
    try {
      console.log('📥 Exporting data...');
      const response = await axios.post(`${API_BASE}/export`, transformedData, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `converted_${file?.name || 'export.csv'}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      setSuccess('File exported successfully');
      
    } catch (err) {
      console.error('📥 Export error:', err);
      setError(`Export failed: ${err.response?.data?.detail || err.message}`);
    }
  };

  const saveConfig = async () => {
    if (!configName || !parsedData) return;
    
    try {
      const config = {
        start_row: parseInt(startRow),
        end_row: endRow ? parseInt(endRow) : null,
        start_col: parseInt(startCol),
        end_col: endCol ? parseInt(endCol) : null,
        column_mapping: columnMapping,
        bank_name: file?.name?.split('.')[0] || 'Unknown Bank'
      };
      
      console.log('💾 Saving bank configuration:', configName);
      await axios.post(`${API_BASE}/save-config`, {
        template_name: configName,
        config: config
      });
      
      setSuccess(`Bank Configuration \"${configName}\" saved successfully`);
      setConfigName('');
      // Reload configurations
      const response = await axios.get(`${API_BASE}/configs`);
      setConfigurations(response.data.configurations || []);
      
    } catch (err) {
      console.error('💾 Save config error:', err);
      setError(`Save configuration failed: ${err.response?.data?.detail || err.message}`);
    }
  };

  const applyConfig = async (configNameOverride = null) => {
    const configToApply = configNameOverride || selectedConfig;
    if (!configToApply || !fileId) return;
    
    try {
      console.log('⚙️ Applying bank configuration:', configToApply);
      const response = await axios.get(`${API_BASE}/config/${configToApply}`);
      const config = response.data.config;
      
      console.log('⚙️ Configuration data:', config);
      
      setStartRow(config.start_row || 0);
      setEndRow(config.end_row || '');
      setStartCol(config.start_col || 0);
      setEndCol(config.end_col || '');
      setColumnMapping(config.column_mapping || {});
      
      if (configNameOverride) {
        setSelectedConfig(configNameOverride);
      }
      
      setSuccess(`Bank Configuration \"${configToApply}\" applied successfully`);
      
    } catch (err) {
      console.error('⚙️ Apply config error:', err);
      try {
        console.log('⚙️ Falling back to template endpoint...');
        const fallbackResponse = await axios.get(`${API_BASE}/template/${configToApply}`);
        const fallbackConfig = fallbackResponse.data.config;
        
        setStartRow(fallbackConfig.start_row || 0);
        setEndRow(fallbackConfig.end_row || '');
        setStartCol(fallbackConfig.start_col || 0);
        setEndCol(fallbackConfig.end_col || '');
        setColumnMapping(fallbackConfig.column_mapping || {});
        
        if (configNameOverride) {
          setSelectedConfig(configNameOverride);
        }
        
        setSuccess(`Configuration \"${configToApply}\" applied successfully (legacy)`);
      } catch (fallbackErr) {
        setError(`Apply configuration failed: ${err.response?.data?.detail || err.message}`);
      }
    }
  };

  const testConnection = async () => {
    setLoading(true);
    clearMessages();
    
    try {
      console.log('🔌 Testing connection to:', `${API_BASE}/`);
      const response = await axios.get(`${API_BASE}/`);
      setSuccess(`✅ Backend connected! Version: ${response.data.version}`);
      console.log('🔌 Backend response:', response.data);
    } catch (err) {
      console.error('Connection test failed:', err);
      setError(`❌ Cannot connect to backend at ${API_BASE}. Make sure the backend is running on port 8000. Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <div className="header">
          <h1>Bank Statement Parser</h1>
          <p>Convert your bank CSV statements with smart bank configurations</p>
        </div>
        
        <div className="main-content">
          {error && <div className="error">{error}</div>}
          {success && <div className="success">{success}</div>}
          
          {/* Step 1: File Upload */}
          <FileUploadStep
            file={file}
            fileInputRef={fileInputRef}
            onFileSelect={handleFileSelect}
            onTestConnection={testConnection}
            loading={loading}
          />

          {/* Step 2: Data Range */}
          {currentStep >= 2 && (
            <DataRangeStep
              configurations={configurations}
              selectedConfig={selectedConfig}
              setSelectedConfig={setSelectedConfig}
              onApplyConfig={applyConfig}
              startRow={startRow}
              setStartRow={setStartRow}
              endRow={endRow}
              setEndRow={setEndRow}
              startCol={startCol}
              setStartCol={setStartCol}
              endCol={endCol}
              setEndCol={setEndCol}
              onParseWithRange={parseWithRange}
              preview={preview}
              loading={loading}
              fileId={fileId}
            />
          )}

          {/* Step 3: Column Mapping */}
          {currentStep >= 3 && parsedData && (
            <ColumnMappingStep
              parsedData={parsedData}
              columnMapping={columnMapping}
              setColumnMapping={setColumnMapping}
              configName={configName}
              setConfigName={setConfigName}
              onSaveConfig={saveConfig}
              onTransformData={transformData}
              loading={loading}
            />
          )}

          {/* Step 4: Review & Export */}
          {currentStep >= 4 && transformedData && (
            <ReviewExportStep
              transformedData={transformedData}
              selectedConfig={selectedConfig}
              onExportData={exportData}
              onReset={resetApp}
            />
          )}
          
          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              Processing...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
