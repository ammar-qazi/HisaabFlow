import React from 'react';
import MultiCSVApp from './MultiCSVApp';

function AppRouter() {
  return (
    <div>
      <div style={{ 
        backgroundColor: '#f0f0f0', 
        padding: '10px', 
        textAlign: 'center', 
        borderBottom: '2px solid #ddd',
        marginBottom: '20px'
      }}>
        <h3>🏦 Bank Statement Parser</h3>
        <p style={{ margin: '5px 0', color: '#666' }}>
          Upload single or multiple CSV files for processing and transfer detection
        </p>
      </div>
      
      <MultiCSVApp />
    </div>
  );
}

export default AppRouter;
