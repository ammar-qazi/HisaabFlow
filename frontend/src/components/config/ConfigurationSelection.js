import React from 'react';

/**
 * Component for configuration selection and preview controls
 * Handles bank configuration dropdown and preview button
 */
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
      <h5> Bank Configuration</h5>
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
           Preview
        </button>
      </div>
      {isAutoConfigured && selectedConfiguration && (
        <div className="auto-config-notice">
          [SUCCESS] Auto-configured with "{selectedConfiguration}"
        </div>
      )}
    </div>
  );
}

export default ConfigurationSelection;
