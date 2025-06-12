import React from 'react';

function BankDetectionDisplay({ bankDetection, preview, parsedData, loading }) {
  console.log('🔍 DEBUG: BankDetectionDisplay render with:', {
    bankDetection: bankDetection,
    preview: preview ? 'preview exists' : 'no preview',
    parsedData: parsedData ? 'parsedData exists' : 'no parsedData',
    loading: loading
  });
  
  // 🔧 FIX: Use backend bank detection when available, fallback to filename detection
  let displayInfo = null;
  let source = 'frontend';
  
  // Priority: parsed data > preview > filename detection
  if (parsedData?.bank_info && Object.keys(parsedData.bank_info).length > 0) {
    displayInfo = {
      bankType: parsedData.bank_info.bank_type || parsedData.bank_info.detected_bank || 'Unknown',
      confidence: parsedData.bank_info.confidence,
      source: 'Backend (Parse)'
    };
    source = 'backend';
    console.log('🏦 DEBUG: Using bank info from parsed data:', parsedData.bank_info);
  } else if (preview?.bank_detection && Object.keys(preview.bank_detection).length > 0) {
    // 🔧 CRITICAL FIX: Look for 'bank_detection' not 'bank_info' in preview response
    displayInfo = {
      bankType: preview.bank_detection.detected_bank || 'Unknown',
      confidence: preview.bank_detection.confidence,
      source: 'Backend (Preview)'
    };
    source = 'backend';
    console.log('🏦 DEBUG: Using bank_detection from preview:', preview.bank_detection);
  } else if (preview?.bank_info && Object.keys(preview.bank_info).length > 0) {
    // 🔧 FALLBACK: Keep original bank_info check for backward compatibility
    displayInfo = {
      bankType: preview.bank_info.bank_type || preview.bank_info.detected_bank || 'Unknown',
      confidence: preview.bank_info.confidence,
      source: 'Backend (Preview)'
    };
    source = 'backend';
    console.log('🏦 DEBUG: Using bank info from preview:', preview.bank_info);
  } else if (bankDetection) {
    displayInfo = {
      bankType: bankDetection.bankType || 'Unknown',
      confidence: null,
      source: 'Frontend (Filename)'
    };
    console.log('🏦 DEBUG: Using frontend bank detection:', bankDetection);
  } else {
    console.log('🏦 DEBUG: No bank detection data found anywhere');
  }
  
  // 🔧 LOADING STATE: Show detecting message when preview is loading
  if (!displayInfo && loading) {
    return (
      <div className="bank-detection">
        <h5>🏦 Bank Detection</h5>
        <div className="detection-results">
          <span className="bank-badge detecting">
            🔍 Detecting...
          </span>
          <span className="detection-source">
            (Analyzing file content)
          </span>
        </div>
      </div>
    );
  }
  
  if (!displayInfo) {
    return (
      <div className="bank-detection">
        <h5>🏦 Bank Detection</h5>
        <div className="detection-results">
          <span className="bank-badge unknown">
            UNKNOWN
          </span>
          <span className="detection-source">
            (Click Preview to detect)
          </span>
        </div>
      </div>
    );
  }
  
  // Format bank type for display
  const formatBankType = (bankType) => {
    if (!bankType || bankType === 'Unknown') return 'Unknown';
    
    // Handle backend bank types
    if (bankType === 'nayapay') return 'NayaPay';
    if (bankType === 'wise_usd') return 'Wise USD';
    if (bankType === 'wise_eur') return 'Wise EUR';
    if (bankType === 'wise_huf') return 'Wise HUF';
    
    // Handle frontend bank types
    if (bankType === 'Transferwise') return 'Wise';
    
    return bankType;
  };
  
  const displayBankType = formatBankType(displayInfo.bankType);
  const isDetected = displayBankType !== 'Unknown';
  
  return (
    <div className="bank-detection">
      <h5>🏦 Bank Detection</h5>
      <div className="detection-results">
        <span className={`bank-badge ${displayBankType.toLowerCase().replace(/\s+/g, '-')}`}>
          {displayBankType}
        </span>
        {displayInfo.confidence !== null && (
          <span className="confidence-score">
            {Math.round(displayInfo.confidence * 100)}% confidence
          </span>
        )}
        <span className="detection-source">
          ({displayInfo.source})
        </span>
        {isDetected && preview && (
          <span className="detection-note">
            ✅ Auto-configured: Headers Row {preview.suggested_header_row || 0}, Data Row {preview.suggested_data_start_row || 0}
          </span>
        )}
      </div>
    </div>
  );
}

function ConfigurationSelection({ 
  selectedConfiguration, 
  configurations, 
  onConfigurationChange, 
  onPreview, 
  loading,
  isAutoConfigured = false
}) {
  return (
    <div className="configuration-section">
      <h5>📋 Bank Configuration</h5>
      <div className="configuration-controls">
        <select 
          value={selectedConfiguration} 
          onChange={(e) => onConfigurationChange(e.target.value)}
        >
          <option value="">Select configuration...</option>
          {configurations.map(config => (
            <option key={config} value={config}>{config}</option>
          ))}
        </select>
        <button 
          className="btn btn-secondary" 
          onClick={onPreview}
          disabled={loading}
        >
          🔍 Preview
        </button>
      </div>
      {isAutoConfigured && selectedConfiguration && (
        <div className="auto-config-notice">
          ✅ Auto-configured with "{selectedConfiguration}"
        </div>
      )}
    </div>
  );
}

function ParseConfiguration({ parseConfig, onConfigChange }) {
  return (
    <div className="range-controls">
      <div className="control-group">
        <label>Start Row</label>
        <input
          type="number"
          value={parseConfig.start_row}
          onChange={(e) => onConfigChange('start_row', parseInt(e.target.value))}
          min="0"
        />
      </div>
      <div className="control-group">
        <label>End Row</label>
        <input
          type="number"
          value={parseConfig.end_row || ''}
          onChange={(e) => onConfigChange('end_row', e.target.value ? parseInt(e.target.value) : null)}
          placeholder="All"
        />
      </div>
    </div>
  );
}

function ColumnMapping({ columnMapping, headers, onMappingChange }) {
  // 🔍 DEBUG: Enhanced debugging for column mapping issue
  console.log('🔍 ColumnMapping Debug (Enhanced):');
  console.log('  - columnMapping:', columnMapping);
  console.log('  - columnMapping keys length:', Object.keys(columnMapping || {}).length);
  console.log('  - headers:', headers);
  console.log('  - headers type:', typeof headers);
  console.log('  - headers length:', headers ? headers.length : 'null/undefined');
  
  if (!headers || headers.length === 0) {
    console.log('  - ❌ NO HEADERS AVAILABLE - Component will not render');
    return (
      <div className="mapping-section">
        <h5>🔗 Column Mapping</h5>
        <div className="mapping-info">
          <span className="mapping-status manual-mapping">⚠️ No headers available - Preview file first</span>
        </div>
      </div>
    );
  }
  
  // Define standard Cashew fields that should always be available for mapping
  const standardCashewFields = ['Date', 'Amount', 'Title', 'Note', 'Account'];
  
  // Use column mapping if available, otherwise show standard fields
  const fieldsToMap = Object.keys(columnMapping || {}).length > 0 
    ? Object.keys(columnMapping) 
    : standardCashewFields;
    
  console.log('  - fieldsToMap (final):', fieldsToMap);
  console.log('  - standardCashewFields:', standardCashewFields);
  
  return (
    <div className="mapping-section">
      <h5>🔗 Column Mapping</h5>
      <div className="mapping-info">
        {Object.keys(columnMapping || {}).length > 0 ? (
          <span className="mapping-status config-applied">✅ Auto-mapped columns detected</span>
        ) : (
          <span className="mapping-status manual-mapping">📝 Manual Mapping (Standard Cashew Fields)</span>
        )}
      </div>
      <div className="mapping-grid">
        {fieldsToMap.map(targetCol => (
          <div key={targetCol} className="mapping-row">
            <label>{targetCol}:</label>
            <select
              value={columnMapping[targetCol] || ''}
              onChange={(e) => onMappingChange(targetCol, e.target.value)}
            >
              <option value="">-- Select Column --</option>
              {headers.map(header => (
                <option key={header} value={header}>{header}</option>
              ))}
            </select>
          </div>
        ))}
      </div>
    </div>
  );
}

function FileConfigurationStep({ 
  currentStep,
  uploadedFiles,
  activeTab,
  templates,
  loading,
  updateFileConfig,
  updateColumnMapping,
  applyTemplate,
  previewFile,
  parseAllFiles
}) {
  if (currentStep < 2 || uploadedFiles.length === 0) return null;
  
  return (
    <div className="step">
      <div className="step-header">
        <div className="step-number">2</div>
        <h2 className="step-title">Configure Files</h2>
      </div>
      
      {uploadedFiles.map((file, index) => (
        <div key={index} className={`file-config ${activeTab === index ? 'active' : 'hidden'}`}>
          <h4>🔧 Configure: {file.fileName}</h4>
          
          <BankDetectionDisplay 
            bankDetection={file.bankDetection}
            preview={file.preview}
            parsedData={file.parsedData}
            loading={loading}
          />
          
          <ConfigurationSelection
            selectedConfiguration={file.selectedConfiguration}
            configurations={templates}
            onConfigurationChange={(configName) => {
              updateFileConfig(index, 'selectedConfiguration', configName);
              if (configName) {
                applyTemplate(index, configName);
              }
            }}
            onPreview={() => previewFile(index)}
            loading={loading}
            isAutoConfigured={file.preview && file.preview.bank_detection && file.selectedConfiguration}
          />

          <ParseConfiguration
            parseConfig={file.parseConfig}
            onConfigChange={(field, value) => updateFileConfig(index, `parseConfig.${field}`, value)}
          />

          <ColumnMapping
            columnMapping={file.columnMapping}
            headers={file.preview?.column_names || file.parsedData?.headers || []}
            onMappingChange={(column, value) => updateColumnMapping(index, column, value)}
          />

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
  );
}

export default FileConfigurationStep;
