import React, { useState } from 'react';
import { ThemeProvider } from './theme/ThemeProvider';
import MultiCSVApp from './MultiCSVApp';
import ModernizedPrototype from './ModernizedPrototype';
import ModernMultiCSVApp from './components/modern/ModernMultiCSVApp';
import './index.css';

function App() {
  const [showMode, setShowMode] = useState('current'); // 'current', 'prototype', 'modern'

  return (
    <ThemeProvider>
      <div>
        <div style={{ 
          position: 'fixed', 
          top: '10px', 
          right: '10px', 
          zIndex: 1000,
          display: 'flex',
          gap: '8px'
        }}>
          <button 
            onClick={() => setShowMode('current')}
            style={{
              padding: '8px 16px',
              backgroundColor: showMode === 'current' ? '#2E7D32' : '#ccc',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            Current App
          </button>
          <button 
            onClick={() => setShowMode('prototype')}
            style={{
              padding: '8px 16px',
              backgroundColor: showMode === 'prototype' ? '#2E7D32' : '#ccc',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            Prototype
          </button>
          <button 
            onClick={() => setShowMode('modern')}
            style={{
              padding: '8px 16px',
              backgroundColor: showMode === 'modern' ? '#2E7D32' : '#ccc',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            Modern Layout
          </button>
        </div>
        
        {showMode === 'current' && <MultiCSVApp />}
        {showMode === 'prototype' && <ModernizedPrototype />}
        {showMode === 'modern' && <ModernMultiCSVApp />}
      </div>
    </ThemeProvider>
  );
}

export default App;