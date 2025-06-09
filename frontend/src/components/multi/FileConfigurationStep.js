import React from 'react';

function BankDetectionDisplay({ bankDetection }) {
  if (!bankDetection) return null;
  
  return (
    <div className="bank-detection">
      <h5>🏦 Bank Detection</h5>
      <div className="detection-results">
        <span className={`bank-badge ${bankDetection.bankType.toLowerCase()}`}>
          {bankDetection.bankType}
        </span>
        {bankDetection.bankType !== 'Unknown' && (
          <span className="detection-note">
            Auto-configured: Start Row {bankDetection.defaultStartRow}, 
            Template: {bankDetection.suggestedTemplate}
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
  loading 
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
  if (!headers || headers.length === 0) return null;
  
  return (
    <div className="mapping-section">
      <h5>🔗 Column Mapping</h5>
      <div className="mapping-grid">
        {Object.keys(columnMapping).map(targetCol => (
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
          
          <BankDetectionDisplay bankDetection={file.bankDetection} />
          
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
          />

          <ParseConfiguration
            parseConfig={file.parseConfig}
            onConfigChange={(field, value) => updateFileConfig(index, `parseConfig.${field}`, value)}
          />

          <ColumnMapping
            columnMapping={file.columnMapping}
            headers={file.parsedData?.headers}
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
