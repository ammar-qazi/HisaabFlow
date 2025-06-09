import React, { useState, useRef } from 'react';
import axios from 'axios';
import './index.css';

const API_BASE = 'http://127.0.0.1:8000';

// Add axios defaults for better error handling
axios.defaults.timeout = 10000; // 10 second timeout
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Add request interceptor for debugging
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

// Add response interceptor for debugging
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
  
  // Configuration management (renamed from template management)
  const [configName, setConfigName] = useState('');
  const [configurations, setConfigurations] = useState([]);
  const [selectedConfig, setSelectedConfig] = useState('');
  
  const fileInputRef = useRef(null);

  const clearMessages = () => {
    setError(null);
    setSuccess(null);
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
      
      // Auto-preview the file
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
      
      // Auto-detect data range
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
      console.log('📊 File ID:', fileId);
      
      const response = await axios.post(`${API_BASE}/parse-range/${fileId}`, requestData, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log('📊 Parse response:', response.data);
      
      setParsedData(response.data);
      setSuccess(`Parsed ${response.data.row_count} rows successfully${response.data.cleaning_applied ? ' with data cleaning' : ''}`);
      setCurrentStep(3);
      
      // Auto-populate column mapping based on headers
      // Use cleaned headers if cleaning was applied, otherwise use original headers
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
      console.error('📊 Parse error full details:', err);
      
      let errorMessage = 'Unknown parsing error';
      
      if (err.response?.data?.detail) {
        // Handle both string and object error details
        if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail;
        } else {
          errorMessage = JSON.stringify(err.response.data.detail);
        }
      } else if (err.response?.data) {
        errorMessage = JSON.stringify(err.response.data);
      } else {
        errorMessage = err.message;
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
      // Get configuration data if a bank configuration is selected
      let categorizationRules = null;
      let defaultCategoryRules = null;
      let accountMapping = null;
      let bankName = file?.name?.split('.')[0] || 'Unknown Bank';
      
      if (selectedConfig) {
        try {
          console.log('⚙️ Loading configuration rules from:', selectedConfig);
          const configResponse = await axios.get(`${API_BASE}/config/${selectedConfig}`);
          const configData = configResponse.data.config;
          
          // Extract advanced configuration data
          categorizationRules = configData.categorization_rules;
          defaultCategoryRules = configData.default_category_rules;
          accountMapping = configData.account_mapping;
          
          // Use bank name from configuration if available
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
        template_name: configName, // Using template_name for backward compatibility with SaveTemplateRequest
        config: config
      });
      
      setSuccess(`Bank Configuration \"${configName}\" saved successfully`);
      setConfigName('');
      loadConfigurations();
      
    } catch (err) {
      console.error('💾 Save config error:', err);
      setError(`Save configuration failed: ${err.response?.data?.detail || err.message}`);
    }
  };

  const loadConfigurations = async () => {
    try {
      console.log('📋 Loading available bank configurations...');
      const response = await axios.get(`${API_BASE}/configs`);
      setConfigurations(response.data.configurations || []);
      console.log('📋 Loaded configurations:', response.data.configurations);
    } catch (err) {
      console.error('📋 Failed to load configurations:', err);
      // If the new endpoint fails, fall back to old templates endpoint temporarily
      try {
        console.log('📋 Falling back to templates endpoint...');
        const fallbackResponse = await axios.get(`${API_BASE}/templates`);
        setConfigurations(fallbackResponse.data.templates || []);
      } catch (fallbackErr) {
        console.error('📋 Fallback also failed:', fallbackErr);
      }
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
      
      // Update selected configuration if we used an override
      if (configNameOverride) {
        setSelectedConfig(configNameOverride);
      }
      
      setSuccess(`Bank Configuration \"${configToApply}\" applied successfully`);
      
    } catch (err) {
      console.error('⚙️ Apply config error:', err);
      // If the new endpoint fails, fall back to old template endpoint temporarily
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

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === 'text/csv') {
      handleFileSelect(droppedFile);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  React.useEffect(() => {
    loadConfigurations();
  }, []);

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
          <div className="step">
            <div className="step-header">
              <div className="step-number">1</div>
              <h2 className="step-title">Upload CSV File</h2>
            </div>
            
            <div 
              className="file-upload"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="file-upload-icon">📁</div>
              <div className="file-upload-text">
                {file ? `Selected: ${file.name}` : 'Click to select CSV file or drag & drop'}
              </div>
              <div className="file-upload-subtext">
                Supported formats: .csv
              </div>
            </div>
            
            <input
              type="file"
              ref={fileInputRef}
              accept=".csv"
              style={{ display: 'none' }}
              onChange={(e) => handleFileSelect(e.target.files[0])}
            />
            
            <div style={{ marginTop: '20px', textAlign: 'center' }}>
              <button 
                className="btn btn-secondary" 
                onClick={testConnection}
                disabled={loading}
              >
                {loading ? '🔄 Testing...' : '🔌 Test Backend Connection'}
              </button>
            </div>
          </div>

          {/* Step 2: Preview and Range Selection */}
          {currentStep >= 2 && (
            <div className="step">
              <div className="step-header">
                <div className="step-number">2</div>
                <h2 className="step-title">Define Data Range</h2>
              </div>
              
              {/* Bank Configuration Controls */}
              <div className="template-section">
                <h3>🏦 Quick Setup with Bank Configurations</h3>
                <div className="template-controls">
                  <select 
                    value={selectedConfig} 
                    onChange={(e) => setSelectedConfig(e.target.value)}
                  >
                    <option value="">Select bank configuration...</option>
                    {configurations.map(config => (
                      <option key={config} value={config}>{config}</option>
                    ))}
                  </select>
                  <button 
                    className="btn btn-secondary" 
                    onClick={applyConfig}
                    disabled={!selectedConfig}
                  >
                    Apply Configuration
                  </button>
                </div>
              </div>
              
              <div className="range-controls">
                <div className="control-group">
                  <label>Start Row</label>
                  <input
                    type="number"
                    value={startRow}
                    onChange={(e) => setStartRow(e.target.value)}
                    min="0"
                  />
                </div>
                <div className="control-group">
                  <label>End Row (optional)</label>
                  <input
                    type="number"
                    value={endRow}
                    onChange={(e) => setEndRow(e.target.value)}
                    placeholder="Leave empty for all"
                  />
                </div>
                <div className="control-group">
                  <label>Start Column</label>
                  <input
                    type="number"
                    value={startCol}
                    onChange={(e) => setStartCol(e.target.value)}
                    min="0"
                  />
                </div>
                <div className="control-group">
                  <label>End Column (optional)</label>
                  <input
                    type="number"
                    value={endCol}
                    onChange={(e) => setEndCol(e.target.value)}
                    placeholder="Leave empty for all"
                  />
                </div>
              </div>
              
              <button 
                className="btn" 
                onClick={parseWithRange}
                disabled={loading || !fileId}
              >
                {loading ? <>🔄 Parsing...</> : <>📊 Parse Data Range</>}
              </button>
              
              {preview && (
                <div className="data-preview">
                  <h4>File Preview (first 20 rows)</h4>
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Row</th>
                        {preview.column_names.map((col, idx) => (
                          <th key={idx}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {preview.preview_data.map((row, idx) => (
                        <tr key={idx}>
                          <td><strong>{idx}</strong></td>
                          {Object.values(row).map((cell, cellIdx) => (
                            <td key={cellIdx}>{cell || ''}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Step 3: Column Mapping */}
          {currentStep >= 3 && parsedData && (
            <div className="step">
              <div className="step-header">
                <div className="step-number">3</div>
                <h2 className="step-title">Map Columns</h2>
              </div>
              
              <div className="info">
                Map your CSV columns to the target format. Available columns: {parsedData.headers.join(', ')}
              </div>
              
              <div className="mapping-section">
                <div className="mapping-grid">
                  {Object.keys(columnMapping).map(targetCol => (
                    <div key={targetCol} className="mapping-row">
                      <label>{targetCol}:</label>
                      <select
                        value={columnMapping[targetCol]}
                        onChange={(e) => setColumnMapping({
                          ...columnMapping,
                          [targetCol]: e.target.value
                        })}
                      >
                        <option value="">-- Select Column --</option>
                        {parsedData.headers.map(header => (
                          <option key={header} value={header}>{header}</option>
                        ))}
                      </select>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Save Bank Configuration */}
              <div className="template-section">
                <h3>💾 Save as Bank Configuration</h3>
                <div className="template-controls">
                  <input
                    type="text"
                    placeholder="Configuration name (e.g., 'My Bank Setup')"
                    value={configName}
                    onChange={(e) => setConfigName(e.target.value)}
                  />
                  <button 
                    className="btn btn-secondary" 
                    onClick={saveConfig}
                    disabled={!configName}
                  >
                    Save Configuration
                  </button>
                </div>
              </div>
              
              <button 
                className="btn" 
                onClick={transformData}
                disabled={loading || !columnMapping.Date || !columnMapping.Amount}
              >
                {loading ? <>🔄 Transforming...</> : <>🔄 Transform Data</>}
              </button>
              
              {/* Preview parsed data */}
              <div className="data-preview">
                <h4>Parsed Data Preview ({parsedData.row_count} rows)</h4>
                <table className="data-table">
                  <thead>
                    <tr>
                      {parsedData.headers.map(header => (
                        <th key={header}>{header}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {parsedData.data.slice(0, 5).map((row, idx) => (
                      <tr key={idx}>
                        {parsedData.headers.map(header => (
                          <td key={header}>{row[header] || ''}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Step 4: Review and Export */}
          {currentStep >= 4 && transformedData && (
            <div className="step">
              <div className="step-header">
                <div className="step-number">4</div>
                <h2 className="step-title">Review & Export</h2>
              </div>
              
              <div className="success">
                ✅ Successfully converted {transformedData.length} transactions to Cashew format!
                {selectedConfig && (
                  <div style={{ marginTop: '10px', fontSize: '14px' }}>
                    🎯 Used configuration: <strong>{selectedConfig}</strong> for smart categorization
                  </div>
                )}
              </div>
              
              <div className="data-preview">
                <h4>Converted Data Preview</h4>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Amount</th>
                      <th>Category</th>
                      <th>Title</th>
                      <th>Note</th>
                      <th>Account</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transformedData.slice(0, 10).map((row, idx) => (
                      <tr key={idx}>
                        <td>{row.Date}</td>
                        <td>{row.Amount}</td>
                        <td>{row.Category}</td>
                        <td>{row.Title}</td>
                        <td>{row.Note}</td>
                        <td>{row.Account}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              <button 
                className="btn btn-success" 
                onClick={exportData}
              >
                📥 Download Converted CSV
              </button>
              
              <button 
                className="btn btn-secondary" 
                onClick={() => {
                  setCurrentStep(1);
                  setFile(null);
                  setFileId(null);
                  setPreview(null);
                  setParsedData(null);
                  setTransformedData(null);
                  clearMessages();
                }}
                style={{ marginLeft: '10px' }}
              >
                🔄 Process Another File
              </button>
            </div>
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
