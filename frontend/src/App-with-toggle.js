import React, { useState } from 'react';
import MultiCSVApp from './MultiCSVApp';
import ModernizedPrototype from './ModernizedPrototype';
import './index.css';

function App() {
  const [showPrototype, setShowPrototype] = useState(false);

  return (
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
          onClick={() => setShowPrototype(false)}
          style={{
            padding: '8px 16px',
            backgroundColor: !showPrototype ? '#2E7D32' : '#ccc',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Current App
        </button>
        <button 
          onClick={() => setShowPrototype(true)}
          style={{
            padding: '8px 16px',
            backgroundColor: showPrototype ? '#2E7D32' : '#ccc',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Modernized Prototype
        </button>
      </div>
      
      {showPrototype ? <ModernizedPrototype /> : <MultiCSVApp />}
    </div>
  );
}

export default App;