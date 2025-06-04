import React, { useState } from 'react';
import App from './App';
import MultiCSVApp from './MultiCSVApp';

function AppRouter() {
  const [currentApp, setCurrentApp] = useState('multi'); // Default to multi-CSV

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
        <div style={{ marginTop: '10px' }}>
          <button 
            className={`btn ${currentApp === 'single' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setCurrentApp('single')}
            style={{ marginRight: '10px' }}
          >
            📄 Single CSV
          </button>
          <button 
            className={`btn ${currentApp === 'multi' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setCurrentApp('multi')}
          >
            📄📄 Multi-CSV + Transfer Detection
          </button>
        </div>
      </div>
      
      {currentApp === 'single' ? <App /> : <MultiCSVApp />}
    </div>
  );
}

export default AppRouter;
