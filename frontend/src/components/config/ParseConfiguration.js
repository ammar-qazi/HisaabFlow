import React from 'react';

/**
 * Component for parse configuration controls
 * Handles start/end row settings for CSV parsing
 */
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

export default ParseConfiguration;
