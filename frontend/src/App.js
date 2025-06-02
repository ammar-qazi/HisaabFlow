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
    console.log('Making request to:', config.url);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging
axios.interceptors.response.use(
  (response) => {
    console.log('Response received:', response.status);
    return response;
  },
  (error) => {
    console.error('Response error:', error.response?.status, error.message);
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
  
  // Template management
  const [templateName, setTemplateName] = useState('');
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  
  const fileInputRef = useRef(null);

  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  const testConnection = async () => {
    setLoading(true);
    clearMessages();
    
    try {
      console.log('Testing connection to:', `${API_BASE}/`);
      const response = await axios.get(`${API_BASE}/`);
      setSuccess(`✅ Backend connected! Version: ${response.data.version}`);
      console.log('Backend response:', response.data);
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
      setError(`Upload failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const previewFile = async (id = fileId) => {
    if (!id) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/preview/${id}`);
      setPreview(response.data);
      
      // Auto-detect data range
      const detectionResponse = await axios.get(`${API_BASE}/detect-range/${id}`);
      if (detectionResponse.data.success && detectionResponse.data.suggested_header_row !== null) {
        setStartRow(detectionResponse.data.suggested_header_row);
      }
      
    } catch (err) {
      setError(`Preview failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const parseWithRange = async () => {
    if (!fileId) return;
    
    clearMessages();
    setLoading(true);
    
    try {
      const response = await axios.post(`${API_BASE}/parse-range/${fileId}`, {
        start_row: parseInt(startRow),
        end_row: endRow ? parseInt(endRow) : null,
        start_col: parseInt(startCol),
        end_col: endCol ? parseInt(endCol) : null
      });
      
      setParsedData(response.data);
      setSuccess(`Parsed ${response.data.row_count} rows successfully`);
      setCurrentStep(3);
      
      // Auto-populate column mapping based on headers
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
      setError(`Parsing failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const transformData = async () => {
    if (!parsedData) return;
    
    clearMessages();
    setLoading(true);
    
    try {
      const response = await axios.post(`${API_BASE}/transform`, {
        data: parsedData.data,
        column_mapping: columnMapping,
        bank_name: file?.name?.split('.')[0] || 'Unknown Bank'
      });
      
      setTransformedData(response.data.data);
      setSuccess(`Transformed ${response.data.row_count} transactions successfully`);
      setCurrentStep(4);
      
    } catch (err) {
      setError(`Transformation failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const exportData = async () => {
    if (!transformedData) return;
    
    try {
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
      setError(`Export failed: ${err.response?.data?.detail || err.message}`);
    }
  };

  const saveTemplate = async () => {
    if (!templateName || !parsedData) return;
    
    try {
      const config = {
        start_row: parseInt(startRow),
        end_row: endRow ? parseInt(endRow) : null,
        start_col: parseInt(startCol),
        end_col: endCol ? parseInt(endCol) : null,
        column_mapping: columnMapping,
        bank_name: file?.name?.split('.')[0] || 'Unknown Bank'
      };
      
      await axios.post(`${API_BASE}/save-template`, {
        template_name: templateName,
        config: config
      });
      
      setSuccess(`Template "${templateName}" saved successfully`);
      setTemplateName('');
      loadTemplates();
      
    } catch (err) {
      setError(`Save template failed: ${err.response?.data?.detail || err.message}`);
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await axios.get(`${API_BASE}/templates`);
      setTemplates(response.data.templates);
    } catch (err) {
      console.error('Failed to load templates:', err);
    }
  };

  const applyTemplate = async () => {
    if (!selectedTemplate || !fileId) return;
    
    try {
      const response = await axios.get(`${API_BASE}/template/${selectedTemplate}`);
      const config = response.data.config;
      
      setStartRow(config.start_row);
      setEndRow(config.end_row || '');
      setStartCol(config.start_col);
      setEndCol(config.end_col || '');
      setColumnMapping(config.column_mapping);
      
      setSuccess(`Template "${selectedTemplate}" applied successfully`);
      
    } catch (err) {
      setError(`Apply template failed: ${err.response?.data?.detail || err.message}`);
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
    loadTemplates();
  }, []);

  return (
    <div className="app">
      <div className="container">
        <div className="header">
          <h1>Bank Statement Parser</h1>
          <p>Convert your bank CSV statements to the desired format</p>
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
              
              {/* Template Controls */}
              <div className="template-section">
                <h3>🔧 Quick Setup with Templates</h3>
                <div className="template-controls">
                  <select 
                    value={selectedTemplate} 
                    onChange={(e) => setSelectedTemplate(e.target.value)}
                  >
                    <option value="">Select saved template...</option>
                    {templates.map(template => (
                      <option key={template} value={template}>{template}</option>
                    ))}
                  </select>
                  <button 
                    className="btn btn-secondary" 
                    onClick={applyTemplate}
                    disabled={!selectedTemplate}
                  >
                    Apply Template
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
              
              {/* Save Template */}
              <div className="template-section">
                <h3>💾 Save Configuration as Template</h3>
                <div className="template-controls">
                  <input
                    type="text"
                    placeholder="Template name (e.g., 'NayaPay_Format')"
                    value={templateName}
                    onChange={(e) => setTemplateName(e.target.value)}
                  />
                  <button 
                    className="btn btn-secondary" 
                    onClick={saveTemplate}
                    disabled={!templateName}
                  >
                    Save Template
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
