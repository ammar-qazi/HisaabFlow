import React, { useState } from 'react';
import { useTheme } from '../../theme/ThemeProvider';

// Import layout components
import AppHeader from './AppHeader';
import MainLayout from './MainLayout';
import StepNavigation from './StepNavigation';
import ContentArea from './ContentArea';

// Import the main app logic
import ModernAppLogic from './ModernAppLogic';

function ModernMultiCSVApp() {
  const theme = useTheme();
  const [currentStep, setCurrentStep] = useState(1);

  return (
    <div style={{ 
      height: '100vh', 
      backgroundColor: theme.colors.background.default, 
      display: 'flex', 
      flexDirection: 'column' 
    }}>
      <AppHeader />
      <MainLayout 
        sidebar={<StepNavigation currentStep={currentStep} />} 
        fullHeight={false}
      >
        <ModernAppLogic 
          currentStep={currentStep} 
          setCurrentStep={setCurrentStep} 
        />
      </MainLayout>
    </div>
  );
}

export default ModernMultiCSVApp;