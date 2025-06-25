import React from 'react';

function ParsedDataSummary({ parsedResults }) {
  return (
    <div className="parsed-summary">
      <h4>[DATA] Parsing Summary</h4>
      {parsedResults.length > 0 ? (
        <div className="summary-grid">
          {parsedResults.map((result, index) => (
            <div key={index} className="summary-card">
              <h5>{result.filename}</h5>
              {result.parse_result ? (
                <>
                  <p>[SUCCESS] {result.parse_result.row_count || 0} transactions</p>
                  <p> {result.parse_result.headers?.length || 0} columns</p>
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
  );
}

function ParsedDataTabs({ parsedResults, activeTab }) {
  return (
    <div className="parsed-data-tabs">
      {parsedResults.map((result, index) => (
        <div key={index} className={`parsed-tab ${activeTab === index ? 'active' : 'hidden'}`}>
          <h5> {result.filename} - Parsed Data</h5>
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
  );
}

function DataReviewStep({ 
  currentStep, 
  parsedResults, 
  activeTab, 
  loading, 
  transformAllFiles 
}) {
  if (currentStep < 3 || parsedResults.length === 0) return null;
  
  return (
    <div className="step">
      <div className="step-header">
        <div className="step-number">3</div>
        <h2 className="step-title">Review Parsed Data</h2>
      </div>
      
      <ParsedDataSummary parsedResults={parsedResults} />
      <ParsedDataTabs parsedResults={parsedResults} activeTab={activeTab} />
      
      <div className="step-actions">
        <button 
          className="btn btn-primary" 
          onClick={transformAllFiles}
          disabled={loading}
        >
          {loading ? ' Transforming...' : ' Transform & Detect Transfers'}
        </button>
      </div>
    </div>
  );
}

export default DataReviewStep;
