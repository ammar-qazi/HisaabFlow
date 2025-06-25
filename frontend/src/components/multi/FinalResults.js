import React from 'react';

function ResultsSummary({ transformedData }) {
  const totalTransactions = transformedData.length;
  const balanceCorrections = transformedData.filter(t => t.Category === 'Balance Correction').length;
  const regularTransactions = totalTransactions - balanceCorrections;
  
  return (
    <div className="results-summary">
      <p>[SUCCESS] Total transactions: <strong>{totalTransactions}</strong></p>
      <p> Balance corrections: <strong>{balanceCorrections}</strong></p>
      <p>[DATA] Regular transactions: <strong>{regularTransactions}</strong></p>
    </div>
  );
}

function ResultsTable({ transformedData }) {
  return (
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
            <td>{row.Category === 'Balance Correction' ? '' : ''}</td>
            <td>{row.Date}</td>
            <td>{row.Amount}</td>
            <td>{row.Category}</td>
            <td>{row.Title}</td>
            <td>{row.Account}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function ResultsActions({ exportData, onStartOver }) {
  return (
    <div className="step-actions">
      <button 
        className="btn btn-success" 
        onClick={exportData}
      >
        [IN] Export Unified CSV
      </button>
      
      <button 
        className="btn btn-secondary" 
        onClick={onStartOver}
        style={{ marginLeft: '10px' }}
      >
         Start Over
      </button>
    </div>
  );
}

function FinalResults({ transformedData, exportData, onStartOver }) {
  return (
    <div className="final-results">
      <h4> Final Converted Data</h4>
      <ResultsSummary transformedData={transformedData} />
      <ResultsTable transformedData={transformedData} />
      <ResultsActions exportData={exportData} onStartOver={onStartOver} />
    </div>
  );
}

export default FinalResults;
