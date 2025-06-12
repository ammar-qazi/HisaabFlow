import React from 'react';

function ColumnMapping({ headers, columnMapping, onMappingChange }) {
  console.log('🔗 ColumnMapping - Headers available:', headers?.length || 0);
  console.log('🔗 ColumnMapping - Column mapping:', columnMapping);
  
  // Early return if no headers are available
  if (!headers || headers.length === 0) {
    console.log('❌ NO HEADERS AVAILABLE - Component will not render');
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

export default ColumnMapping;
