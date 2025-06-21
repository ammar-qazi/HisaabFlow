import React from 'react';
import { ThemeProvider } from './theme/ThemeProvider';
import { Toaster } from 'react-hot-toast'; // <-- 1. Import Toaster
import ModernMultiCSVApp from './components/modern/ModernMultiCSVApp';
import './index.css';

function App() {
  return (
    <ThemeProvider>
      <ModernMultiCSVApp />
      <Toaster position="bottom-right" /> {/* <-- 2. Add the component here */}
    </ThemeProvider>
  );
}

export default App;