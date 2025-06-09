import React from 'react';
import TransferAnalysis from './TransferAnalysis';
import FinalResults from './FinalResults';

function ResultsStep({ 
  currentStep, 
  transformedData, 
  transferAnalysis, 
  exportData, 
  onStartOver 
}) {
  if (currentStep < 4 || !transformedData) return null;
  
  return (
    <div className="step">
      <div className="step-header">
        <div className="step-number">4</div>
        <h2 className="step-title">Results & Transfer Detection</h2>
      </div>
      
      <TransferAnalysis transferAnalysis={transferAnalysis} />
      <FinalResults 
        transformedData={transformedData} 
        exportData={exportData} 
        onStartOver={onStartOver} 
      />
    </div>
  );
}

export default ResultsStep;
