import React, { useState, useRef } from 'react';
import axios from 'axios';
import './index.css';

const API_BASE = 'http://127.0.0.1:8000';

// Configure axios
axios.defaults.timeout = 15000;
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Bank detection function
const detectBankFromFilename = (filename) => {
  const lowerFilename = filename.toLowerCase();
  
  // Bank detection patterns
  if (lowerFilename.includes('nayapay')) {
    return {
      bankType: 'NayaPay',
      suggestedTemplate: 'NayaPay_Enhanced_Template',
      cleanedTemplate: 'NayaPay_Cleaned_Template', // NEW: for when data cleaning is applied
      defaultStartRow: 13,
      defaultEncoding: 'utf-8'
    };
  }
  
  if (lowerFilename.includes('transferwise') || lowerFilename.includes('wise')) {
    return {
      bankType: 'Transferwise',
      suggestedTemplate: 'Wise_Universal_Template', 
      defaultStartRow: 0,
      defaultEncoding: 'utf-8'
    };
  }
  
  // Default for unknown banks
  return {
    bankType: 'Unknown',
    suggestedTemplate: '',
    defaultStartRow: 0,
    defaultEncoding: 'utf-8'
  };
};

function MultiCSVApp() {
  // Multi-CSV state
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  const [currentStep, setCurrentStep] = useState(1);
  
  // User settings
  const [userName, setUserName] = useState('Ammar Qazi');
  const [dateTolerance, setDateTolerance] = useState(24);
  const [enableTransferDetection, setEnableTransferDetection] = useState(true);
  
  // Bank-specific rules settings
  const [bankRulesSettings, setBankRulesSettings] = useState({
    enableNayaPayRules: true,
    enableTransferwiseRules: true,
    enableUniversalRules: true
  });
  
  // Processing state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Results
  const [parsedResults, setParsedResults] = useState([]);
  const [transformedData, setTransformedData] = useState(null);
  const [transferAnalysis, setTransferAnalysis] = useState(null);
  
  // Templates
  const [templates, setTemplates] = useState([]);
  
  const fileInputRef = useRef(null);

  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  // Load templates on component mount
  React.useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await axios.get(`${API_BASE}/templates`);
      setTemplates(response.data.templates);
    } catch (err) {
      console.error('Failed to load templates:', err);
    }
  };

  const handleFileSelect = async (selectedFiles) => {
    if (!selectedFiles || selectedFiles.length === 0) return;
    
    clearMessages();
    setLoading(true);
    
    try {
      const newFiles = [];
      
      // Upload each file
      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await axios.post(`${API_BASE}/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        // Detect bank from filename
        const bankDetection = detectBankFromFilename(file.name);
        
        newFiles.push({
          file: file,
          fileId: response.data.file_id,
          fileName: file.name,
          preview: null,
          parsedData: null,
          selectedTemplate: bankDetection.suggestedTemplate, // Auto-select template
          columnMapping: {}, // Start empty - will be filled by template
          parseConfig: {
            start_row: bankDetection.defaultStartRow, // Use bank-specific default
            end_row: null,
            start_col: 0,
            end_col: null,
            encoding: bankDetection.defaultEncoding
          },
          bankDetection: bankDetection // Store detection results
        });
      }
      
      setUploadedFiles(prev => [...prev, ...newFiles]);
      setSuccess(`Successfully uploaded ${selectedFiles.length} file(s) with bank auto-detection`);
      setCurrentStep(2);
      
      // Auto-apply templates for detected banks WITH a delay to ensure state is updated
      for (let i = 0; i < newFiles.length; i++) {
      const fileIndex = uploadedFiles.length + i;
      if (newFiles[i].selectedTemplate) {
      // Apply template after a short delay to ensure file is in state
        setTimeout(() => {
            applyTemplate(fileIndex, newFiles[i].selectedTemplate);
          }, 500 * (i + 1)); // Stagger the template applications
        }
      }
      
      // Auto-preview first file if it's the only one
      if (newFiles.length === 1) {
      setActiveTab(0);
      // Preview after template is applied
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

  const previewFile = async (fileIndex) => {
    const fileData = uploadedFiles[fileIndex];
    if (!fileData) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/preview/${fileData.fileId}`);
      
      // Update the specific file's preview
      setUploadedFiles(prev => {
        const updated = [...prev];
        updated[fileIndex] = {
          ...updated[fileIndex],
          preview: response.data
        };
        return updated;
      });
      
      // ALWAYS auto-detect data range for better accuracy, even with templates
      console.log(`🔍 Auto-detecting header row for ${fileData.fileName}`);
      const detectionResponse = await axios.get(`${API_BASE}/detect-range/${fileData.fileId}`);
      
      if (detectionResponse.data.success && detectionResponse.data.suggested_header_row !== null) {
        const detectedStartRow = detectionResponse.data.suggested_header_row;
        console.log(`📍 Detected start row: ${detectedStartRow} for ${fileData.fileName}`);
        
        // 🔧 SMART OVERRIDE LOGIC: Only override template if detection seems more reliable
        const currentStartRow = uploadedFiles[fileIndex].parseConfig.start_row;
        const templateApplied = uploadedFiles[fileIndex].selectedTemplate;
        
        let finalStartRow = detectedStartRow;
        
        // For NayaPay files, trust the template over detection if they're close
        if (templateApplied && templateApplied.includes('NayaPay')) {
          const diff = Math.abs(currentStartRow - detectedStartRow);
          if (diff <= 3) {
            finalStartRow = currentStartRow; // Keep template value
            console.log(`🎯 NayaPay: Using template start_row ${currentStartRow} (detected: ${detectedStartRow}, diff: ${diff})`);
          } else {
            console.log(`⚠️ NayaPay: Large difference detected, using detected start_row ${detectedStartRow} (template: ${currentStartRow})`);
          }
        }
        
        setUploadedFiles(prev => {
          const updated = [...prev];
          updated[fileIndex] = {
            ...updated[fileIndex],
            parseConfig: {
              ...updated[fileIndex].parseConfig,
              start_row: finalStartRow
            }
          };
          return updated;
        });
        
        if (finalStartRow !== detectedStartRow) {
          setSuccess(`Smart detection: ${fileData.fileName} using template row ${finalStartRow} (detected: ${detectedStartRow})`);
        } else {
          setSuccess(`Smart detection: ${fileData.fileName} headers found at row ${detectedStartRow}`);
        }
      } else {
        console.warn(`⚠️ Could not auto-detect header row for ${fileData.fileName}, using template default`);
      }
      
    } catch (err) {
      setError(`Preview failed for ${fileData.fileName}: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const parseAllFiles = async () => {
    if (uploadedFiles.length === 0) return;
    
    clearMessages();
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
      
      // Update uploaded files with parsed data
      const results = response.data.parsed_csvs;
      
      // Debug: Log each result structure
      results.forEach((result, index) => {
        console.log(`Result ${index}:`, result);
        console.log(`Parse result structure:`, result.parse_result);
      });
      
      setUploadedFiles(prev => {
        return prev.map((file, index) => {
          const result = results.find(r => r.file_id === file.fileId);
          if (result) {
            // Ensure parse_result has the expected structure
            const parseResult = result.parse_result || {};
            const safeParseResult = {
              success: parseResult.success || false,
              headers: parseResult.headers || [],
              data: parseResult.data || [],
              row_count: parseResult.row_count || 0,
              cleaning_applied: parseResult.cleaning_applied || false
            };
            
            // AUTO-SWITCH TO CLEANED TEMPLATE if data cleaning was applied
            let updatedFile = {
              ...file,
              parsedData: safeParseResult
            };
            
            // Check if we should switch to cleaned template
            if (parseResult.cleaning_applied && file.bankDetection?.cleanedTemplate) {
              const cleanedTemplateName = file.bankDetection.cleanedTemplate;
              console.log(`🧽 Data cleaning detected for ${file.fileName}, switching to ${cleanedTemplateName}`);
              
              // Auto-apply cleaned template
              setTimeout(() => {
                applyTemplate(index, cleanedTemplateName);
              }, 1000 + index * 500); // Stagger the applications
              
              updatedFile.selectedTemplate = cleanedTemplateName;
            }
            
            return updatedFile;
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

  const transformAllFiles = async () => {
    if (uploadedFiles.length === 0) return;
    
    clearMessages();
    setLoading(true);
    
    try {
      // Prepare CSV data with COMPLETE template configurations
      const csvDataList = await Promise.all(uploadedFiles.map(async (file) => {
        let templateConfig = {};
        
        if (file.selectedTemplate) {
          try {
            const templateResponse = await axios.get(`${API_BASE}/template/${file.selectedTemplate}`);
            templateConfig = templateResponse.data.config;
            
            console.log(`📋 Loaded template ${file.selectedTemplate} for ${file.fileName}:`);
            console.log(`   - Bank name: ${templateConfig.bank_name}`);
            console.log(`   - Categorization rules: ${templateConfig.categorization_rules?.length || 0}`);
            console.log(`   - Default category rules: ${!!templateConfig.default_category_rules}`);
            
          } catch (err) {
            console.warn(`Could not load template ${file.selectedTemplate}:`, err);
          }
        }
        
      // 🔧 CRITICAL FIX: Smart column mapping merge
      let finalColumnMapping = {};
      
      if (templateConfig.column_mapping) {
        // Start with template mapping
        finalColumnMapping = { ...templateConfig.column_mapping };
        
        // Only override with user selections that are actually set (not empty)
        Object.keys(file.columnMapping || {}).forEach(key => {
          const userValue = file.columnMapping[key];
          if (userValue && userValue !== '' && userValue !== '-- Select Column --') {
            finalColumnMapping[key] = userValue;
          }
        });
      } else {
        // No template mapping, use user mapping
        finalColumnMapping = { ...file.columnMapping };
      }
      
      // Remove empty mappings
      Object.keys(finalColumnMapping).forEach(key => {
        if (!finalColumnMapping[key] || finalColumnMapping[key] === '' || finalColumnMapping[key] === '-- Select Column --') {
          delete finalColumnMapping[key];
        }
      });
        
        const completeTemplateConfig = {
          // ✅ Preserve ALL template properties
          ...templateConfig,
          // ✅ Use the smart merged column mapping
          column_mapping: finalColumnMapping,
          // ✅ Ensure bank name is set
          bank_name: templateConfig.bank_name || file.fileName.replace('.csv', '').replace(/[_-]/g, ' ')
        };
        
        console.log(`🔄 Final config for ${file.fileName}:`, {
          bank_name: completeTemplateConfig.bank_name,
          column_mapping: completeTemplateConfig.column_mapping,
          categorization_rules_count: completeTemplateConfig.categorization_rules?.length || 0,
          has_default_rules: !!completeTemplateConfig.default_category_rules,
          has_account_mapping: !!completeTemplateConfig.account_mapping
        });
        
        return {
          file_name: file.fileName,
          data: file.parsedData?.data || [],
          headers: file.parsedData?.headers || [],
          template_config: completeTemplateConfig  // ✅ Now includes ALL template properties
        };
      }));
      
      console.log('🚀 Sending complete template configurations to backend:', 
        csvDataList.map(csv => ({
          file: csv.file_name,
          rules: csv.template_config.categorization_rules?.length || 0,
          bank: csv.template_config.bank_name,
          columns: Object.keys(csv.template_config.column_mapping || {}).length
        }))
      );
      
      const response = await axios.post(`${API_BASE}/multi-csv/transform`, {
        csv_data_list: csvDataList,
        user_name: userName,
        enable_transfer_detection: enableTransferDetection,
        date_tolerance_hours: dateTolerance,
        bank_rules_settings: bankRulesSettings
      });
      
      setTransformedData(response.data.transformed_data);
      setTransferAnalysis(response.data.transfer_analysis);
      setSuccess(`Transformation complete! ${response.data.transformation_summary.total_transactions} transactions processed with categorization rules`);
      setCurrentStep(4);
      
    } catch (err) {
      setError(`Transformation failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const updateFileConfig = (fileIndex, field, value) => {
    setUploadedFiles(prev => {
      const updated = [...prev];
      if (field.includes('.')) {
        // Handle nested fields like parseConfig.start_row
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

  const applyTemplate = async (fileIndex, templateName) => {
    if (!templateName) return;
    
    try {
      const response = await axios.get(`${API_BASE}/template/${templateName}`);
      const config = response.data.config;
      
      console.log(`📋 Applying template ${templateName}:`, config);
      
      setUploadedFiles(prev => {
        const updated = [...prev];
        updated[fileIndex] = {
          ...updated[fileIndex],
          selectedTemplate: templateName,
          parseConfig: {
            start_row: config.start_row || 0,
            end_row: config.end_row || null,
            start_col: config.start_col || 0,
            end_col: config.end_col || null,
            encoding: 'utf-8'
          },
          // 🔧 FIX: Use template column mapping directly for auto-mapping
          columnMapping: config.column_mapping || {}
        };
        return updated;
      });
      
      setSuccess(`Template "${templateName}" applied to ${uploadedFiles[fileIndex].fileName} with categorization rules`);
      
    } catch (err) {
      setError(`Failed to apply template: ${err.response?.data?.detail || err.message}`);
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

  const removeFile = (fileIndex) => {
    setUploadedFiles(prev => prev.filter((_, index) => index !== fileIndex));
    if (activeTab >= uploadedFiles.length - 1) {
      setActiveTab(Math.max(0, uploadedFiles.length - 2));
    }
  };

  return (
    <div className="app">
      <div className="container">
        <div className="header">
          <h1>🚀 Multi-CSV Bank Statement Parser</h1>
          <p>Upload multiple CSV files, detect transfers, and export unified data</p>
        </div>
        
        <div className="main-content">
          {error && <div className="error">{error}</div>}
          {success && <div className="success">{success}</div>}

          {/* User Settings */}
          <div className="settings-section">
            <h3>⚙️ Transfer Detection Settings</h3>
            <div className="settings-grid">
              <div className="setting-item">
                <label>Your Name (for transfer matching)</label>
                <input
                  type="text"
                  value={userName}
                  onChange={(e) => setUserName(e.target.value)}
                  placeholder="Enter your full name"
                />
              </div>
              <div className="setting-item">
                <label>Date Tolerance (hours)</label>
                <input
                  type="number"
                  value={dateTolerance}
                  onChange={(e) => setDateTolerance(parseInt(e.target.value))}
                  min="1"
                  max="168"
                />
              </div>
              <div className="setting-item">
                <label>
                  <input
                    type="checkbox"
                    checked={enableTransferDetection}
                    onChange={(e) => setEnableTransferDetection(e.target.checked)}
                  />
                  Enable Transfer Detection
                </label>
              </div>
            </div>
          </div>
          
          {/* Bank-Specific Rules Settings */}
          <div className="settings-section">
            <h3>🏦 Bank-Specific Rules</h3>
            <p className="settings-description">
              Choose which bank-specific rules to apply during transformation. 
              This helps avoid conflicts and gives you control over categorization.
            </p>
            <div className="bank-rules-grid">
              <div className="bank-rule-item">
                <label>
                  <input
                    type="checkbox"
                    checked={bankRulesSettings.enableNayaPayRules}
                    onChange={(e) => setBankRulesSettings(prev => ({ 
                      ...prev, 
                      enableNayaPayRules: e.target.checked 
                    }))}
                  />
                  <span className="bank-logo">🇵🇰</span>
                  NayaPay Rules
                  <small>Ride-hailing detection, mobile recharges, Pakistani context</small>
                </label>
              </div>
              
              <div className="bank-rule-item">
                <label>
                  <input
                    type="checkbox"
                    checked={bankRulesSettings.enableTransferwiseRules}
                    onChange={(e) => setBankRulesSettings(prev => ({ 
                      ...prev, 
                      enableTransferwiseRules: e.target.checked 
                    }))}
                  />
                  <span className="bank-logo">🌍</span>
                  Transferwise Rules
                  <small>Card transaction cleaning, Hungarian merchants, EU context</small>
                </label>
              </div>
              
              <div className="bank-rule-item">
                <label>
                  <input
                    type="checkbox"
                    checked={bankRulesSettings.enableUniversalRules}
                    onChange={(e) => setBankRulesSettings(prev => ({ 
                      ...prev, 
                      enableUniversalRules: e.target.checked 
                    }))}
                  />
                  <span className="bank-logo">🌐</span>
                  Universal Rules
                  <small>Cross-bank categorization (groceries, travel, dining, etc.)</small>
                </label>
              </div>
            </div>
          </div>
          
          {/* Step 1: Multi-File Upload */}
          <div className="step">
            <div className="step-header">
              <div className="step-number">1</div>
              <h2 className="step-title">Upload Multiple CSV Files</h2>
            </div>
            
            <div 
              className="file-upload multi-file"
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="file-upload-icon">📁📁📁</div>
              <div className="file-upload-text">
                Click to select multiple CSV files (Ctrl/Cmd + Click)
              </div>
              <div className="file-upload-subtext">
                Upload CSVs from different accounts/currencies for transfer detection
              </div>
            </div>
            
            <input
              type="file"
              ref={fileInputRef}
              accept=".csv"
              multiple
              style={{ display: 'none' }}
              onChange={(e) => handleFileSelect(e.target.files)}
            />
            
            {uploadedFiles.length > 0 && (
              <div className="uploaded-files">
                <h4>📋 Uploaded Files ({uploadedFiles.length})</h4>
                <div className="file-tabs">
                  {uploadedFiles.map((file, index) => (
                    <div 
                      key={index}
                      className={`file-tab ${activeTab === index ? 'active' : ''}`}
                      onClick={() => setActiveTab(index)}
                    >
                      <span>{file.fileName}</span>
                      <button 
                        className="remove-file"
                        onClick={(e) => {
                          e.stopPropagation();
                          removeFile(index);
                        }}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Step 2: Configure Each File */}
          {currentStep >= 2 && uploadedFiles.length > 0 && (
            <div className="step">
              <div className="step-header">
                <div className="step-number">2</div>
                <h2 className="step-title">Configure Files</h2>
              </div>
              
              {uploadedFiles.map((file, index) => (
                <div key={index} className={`file-config ${activeTab === index ? 'active' : 'hidden'}`}>
                  <h4>🔧 Configure: {file.fileName}</h4>
                  
                  {/* Template Selection */}
                  {/* Bank Detection Results */}
                  {file.bankDetection && (
                    <div className="bank-detection">
                      <h5>🏦 Bank Detection</h5>
                      <div className="detection-results">
                        <span className={`bank-badge ${file.bankDetection.bankType.toLowerCase()}`}>
                          {file.bankDetection.bankType}
                        </span>
                        {file.bankDetection.bankType !== 'Unknown' && (
                          <span className="detection-note">
                            Auto-configured: Start Row {file.bankDetection.defaultStartRow}, 
                            Template: {file.bankDetection.suggestedTemplate}
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                  
                  <div className="template-section">
                    <h5>📋 Template</h5>
                    <div className="template-controls">
                      <select 
                        value={file.selectedTemplate} 
                        onChange={(e) => {
                          updateFileConfig(index, 'selectedTemplate', e.target.value);
                          if (e.target.value) {
                            applyTemplate(index, e.target.value);
                          }
                        }}
                      >
                        <option value="">Select template...</option>
                        {templates.map(template => (
                          <option key={template} value={template}>{template}</option>
                        ))}
                      </select>
                      <button 
                        className="btn btn-secondary" 
                        onClick={() => previewFile(index)}
                        disabled={loading}
                      >
                        🔍 Preview
                      </button>
                    </div>
                  </div>

                  {/* Parse Configuration */}
                  <div className="range-controls">
                    <div className="control-group">
                      <label>Start Row</label>
                      <input
                        type="number"
                        value={file.parseConfig.start_row}
                        onChange={(e) => updateFileConfig(index, 'parseConfig.start_row', parseInt(e.target.value))}
                        min="0"
                      />
                    </div>
                    <div className="control-group">
                      <label>End Row</label>
                      <input
                        type="number"
                        value={file.parseConfig.end_row || ''}
                        onChange={(e) => updateFileConfig(index, 'parseConfig.end_row', e.target.value ? parseInt(e.target.value) : null)}
                        placeholder="All"
                      />
                    </div>
                  </div>

                  {/* Column Mapping */}
                  {file.parsedData && file.parsedData.headers && file.parsedData.headers.length > 0 && (
                    <div className="mapping-section">
                      <h5>🔗 Column Mapping</h5>
                      <div className="mapping-grid">
                        {Object.keys(file.columnMapping).map(targetCol => (
                          <div key={targetCol} className="mapping-row">
                            <label>{targetCol}:</label>
                            <select
                              value={file.columnMapping[targetCol] || ''}
                              onChange={(e) => updateColumnMapping(index, targetCol, e.target.value)}
                            >
                              <option value="">-- Select Column --</option>
                              {file.parsedData.headers.map(header => (
                                <option key={header} value={header}>{header}</option>
                              ))}
                            </select>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Preview Data */}
                  {file.preview && (
                    <div className="data-preview">
                      <h5>👁️ Preview: {file.fileName}</h5>
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>Row</th>
                            {file.preview.column_names.slice(0, 6).map((col, idx) => (
                              <th key={idx}>{col}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {file.preview.preview_data.slice(0, 5).map((row, idx) => (
                            <tr key={idx}>
                              <td><strong>{idx}</strong></td>
                              {Object.values(row).slice(0, 6).map((cell, cellIdx) => (
                                <td key={cellIdx}>{cell || ''}</td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              ))}
              
              <div className="step-actions">
                <button 
                  className="btn btn-primary" 
                  onClick={parseAllFiles}
                  disabled={loading || uploadedFiles.length === 0}
                >
                  {loading ? '🔄 Parsing...' : '📊 Parse All Files'}
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Review Parsed Data */}
          {currentStep >= 3 && parsedResults.length > 0 && (
            <div className="step">
              <div className="step-header">
                <div className="step-number">3</div>
                <h2 className="step-title">Review Parsed Data</h2>
              </div>
              
              <div className="parsed-summary">
                <h4>📊 Parsing Summary</h4>
                {parsedResults.length > 0 ? (
                  <div className="summary-grid">
                    {parsedResults.map((result, index) => (
                      <div key={index} className="summary-card">
                        <h5>{result.file_name}</h5>
                        {result.parse_result ? (
                          <>
                            <p>✅ {result.parse_result.row_count || 0} transactions</p>
                            <p>📋 {result.parse_result.headers?.length || 0} columns</p>
                            {!result.parse_result.headers && (
                              <p className="error">Warning: No headers found</p>
                            )}
                          </>
                        ) : (
                          <p className="error">Parse failed for this file</p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="error">No parsing results available</div>
                )}
              </div>

              {/* Parsed Data Tabs */}
              <div className="parsed-data-tabs">
                {parsedResults.map((result, index) => (
                  <div key={index} className={`parsed-tab ${activeTab === index ? 'active' : 'hidden'}`}>
                    <h5>📋 {result.file_name} - Parsed Data</h5>
                    {result.parse_result && result.parse_result.headers && result.parse_result.data ? (
                      <table className="data-table">
                        <thead>
                          <tr>
                            {result.parse_result.headers.map(header => (
                              <th key={header}>{header}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {result.parse_result.data.slice(0, 10).map((row, idx) => (
                            <tr key={idx}>
                              {result.parse_result.headers.map(header => (
                                <td key={header}>{row[header] || ''}</td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <div className="error">No parsed data available for this file</div>
                    )}
                  </div>
                ))}
              </div>
              
              <div className="step-actions">
                <button 
                  className="btn btn-primary" 
                  onClick={transformAllFiles}
                  disabled={loading}
                >
                  {loading ? '🔄 Transforming...' : '🔄 Transform & Detect Transfers'}
                </button>
              </div>
            </div>
          )}

          {/* Step 4: Review Results & Transfer Detection */}
          {currentStep >= 4 && transformedData && (
            <div className="step">
              <div className="step-header">
                <div className="step-number">4</div>
                <h2 className="step-title">Results & Transfer Detection</h2>
              </div>
              
              {/* Transfer Analysis */}
              {transferAnalysis && (
                <div className="transfer-analysis">
                  <h4>🔄 Transfer Detection Results</h4>
                  <div className="transfer-summary">
                    <div className="summary-stats">
                      <div className="stat-card">
                        <span className="stat-number">{transferAnalysis.summary.transfer_pairs_found}</span>
                        <span className="stat-label">Transfer Pairs</span>
                      </div>
                      <div className="stat-card">
                        <span className="stat-number">{transferAnalysis.summary.potential_transfers}</span>
                        <span className="stat-label">Potential Transfers</span>
                      </div>
                      <div className="stat-card">
                        <span className="stat-number">{transferAnalysis.summary.conflicts}</span>
                        <span className="stat-label">Conflicts</span>
                      </div>
                      <div className="stat-card">
                        <span className="stat-number">{transferAnalysis.summary.flagged_for_review}</span>
                        <span className="stat-label">Flagged for Review</span>
                      </div>
                    </div>
                    
                    {/* Detected Transfers */}
                    {transferAnalysis.transfers && transferAnalysis.transfers.length > 0 && (
                      <div className="detected-transfers">
                        <h5>💸 Detected Transfer Pairs</h5>
                        {transferAnalysis.transfers.map((pair, index) => (
                          <div key={index} className="transfer-pair">
                            <div className="transfer-out">
                              <span className="transfer-label">📤 OUT:</span>
                              <span className="transfer-desc">{pair.outgoing.Description}</span>
                              <span className="transfer-amount">-{pair.amount}</span>
                              <span className="transfer-account">({pair.outgoing._csv_name})</span>
                            </div>
                            <div className="transfer-arrow">↓</div>
                            <div className="transfer-in">
                              <span className="transfer-label">📥 IN:</span>
                              <span className="transfer-desc">{pair.incoming.Description}</span>
                              <span className="transfer-amount">+{pair.incoming.Amount}</span>
                              <span className="transfer-account">({pair.incoming._csv_name})</span>
                            </div>
                            <div className="transfer-confidence">
                              Confidence: {(pair.confidence * 100).toFixed(0)}%
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {/* Conflicts */}
                    {transferAnalysis.conflicts && transferAnalysis.conflicts.length > 0 && (
                      <div className="transfer-conflicts">
                        <h5>⚠️ Transfer Conflicts</h5>
                        <p>These transactions have multiple potential matches and need manual review:</p>
                        {transferAnalysis.conflicts.map((conflict, index) => (
                          <div key={index} className="conflict-item">
                            <p><strong>Transaction:</strong> {conflict.outgoing_transaction.Description}</p>
                            <p><strong>Potential matches:</strong> {conflict.potential_matches.length}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              {/* Final Results */}
              <div className="final-results">
                <h4>📋 Final Converted Data</h4>
                <div className="results-summary">
                  <p>✅ Total transactions: <strong>{transformedData.length}</strong></p>
                  <p>🔄 Balance corrections: <strong>{transformedData.filter(t => t.Category === 'Balance Correction').length}</strong></p>
                  <p>📊 Regular transactions: <strong>{transformedData.filter(t => t.Category !== 'Balance Correction').length}</strong></p>
                </div>
                
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Type</th>
                      <th>Date</th>
                      <th>Amount</th>
                      <th>Category</th>
                      <th>Title</th>
                      <th>Account</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transformedData.slice(0, 20).map((row, idx) => (
                      <tr key={idx} className={row.Category === 'Balance Correction' ? 'transfer-row' : ''}>
                        <td>{row.Category === 'Balance Correction' ? '🔄' : '💰'}</td>
                        <td>{row.Date}</td>
                        <td>{row.Amount}</td>
                        <td>{row.Category}</td>
                        <td>{row.Title}</td>
                        <td>{row.Account}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              <div className="step-actions">
                <button 
                  className="btn btn-success" 
                  onClick={exportData}
                >
                  📥 Export Unified CSV
                </button>
                
                <button 
                  className="btn btn-secondary" 
                  onClick={() => {
                    setCurrentStep(1);
                    setUploadedFiles([]);
                    setParsedResults([]);
                    setTransformedData(null);
                    setTransferAnalysis(null);
                    setActiveTab(0);
                    clearMessages();
                  }}
                  style={{ marginLeft: '10px' }}
                >
                  🔄 Start Over
                </button>
              </div>
            </div>
          )}
          
          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              Processing multiple CSV files...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default MultiCSVApp;