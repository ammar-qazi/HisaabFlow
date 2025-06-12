import React from 'react';

// Import sub-components
import BankDetectionDisplay from '../bank/BankDetectionDisplay';
import ConfigurationSelection from '../config/ConfigurationSelection';
import ParseConfiguration from '../config/ParseConfiguration';
import ColumnMapping from '../bank/ColumnMapping';

/**
 * Main file configuration step component
 * Orchestrates bank detection, configuration selection, and column mapping
 */
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
