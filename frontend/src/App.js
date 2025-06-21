import React from 'react';
import { ThemeProvider } from './theme/ThemeProvider';
import ModernMultiCSVApp from './components/modern/ModernMultiCSVApp';
import './index.css';

function App() {
  return (
    <ThemeProvider>
      <ModernMultiCSVApp />
    </ThemeProvider>
  );
}

export default App;