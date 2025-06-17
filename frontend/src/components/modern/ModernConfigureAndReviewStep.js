import React, { useState, useEffect } from 'react';
import { useTheme } from '../../theme/ThemeProvider';
import { Card, Button } from '../ui';
import { ChevronLeft, ChevronRight } from '../ui/Icons';

// Import modular components
import AutoParseHandler from './configure-review/AutoParseHandler';
import ConfidenceDashboard from './configure-review/ConfidenceDashboard';
import AdvancedConfigPanel from './configure-review/AdvancedConfigPanel';
import ValidationChecklist from './configure-review/ValidationChecklist';
import TransactionReview from './configure-review/TransactionReview';

function ModernConfigureAndReviewStep({ 
  currentStep,
  uploadedFiles,
  activeTab,
  setActiveTab,
  templates,
  loading,
  updateFileConfig,
  updateColumnMapping,
  applyTemplate,
  previewFile,
  parseAllFiles,
  transformAllFiles,
  setCurrentStep,
  parsedResults  // Add this prop to get the parsed results
}) {
  const theme = useTheme();
  const [showAdvancedConfig, setShowAdvancedConfig] = useState(false);
  const [validationChecklist, setValidationChecklist] = useState({
    largeTransactions: false,
    dateRange: false,
    categories: false,
    dataQuality: false
  });

  if (currentStep < 2 || uploadedFiles.length === 0) return null;

  // Use parsedResults from parent state instead of local autoParseResults
  const autoParseResults = parsedResults;
  
  // Debug logging
  console.log('🔍 ModernConfigureAndReviewStep - parsedResults:', parsedResults);
  console.log('🔍 ModernConfigureAndReviewStep - autoParseResults:', autoParseResults);

  // Calculate validation progress
  const validationProgress = Object.values(validationChecklist).filter(Boolean).length / 
    Object.keys(validationChecklist).length * 100;
  const allValidated = validationProgress === 100;

  const updateValidationItem = (item, checked) => {
    setValidationChecklist(prev => ({
      ...prev,
      [item]: checked
    }));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.lg }}>
      {/* Auto-parse Handler - Manages the parsing logic */}
      <AutoParseHandler
        uploadedFiles={uploadedFiles}
        parseAllFiles={parseAllFiles}
        autoParseResults={autoParseResults}
        setShowAdvancedConfig={setShowAdvancedConfig}
        loading={loading}
      />

      {/* Confidence Dashboard - Shows parsed results metrics */}
      {autoParseResults && (
        <ConfidenceDashboard
          autoParseResults={autoParseResults}
          uploadedFiles={uploadedFiles}
          showAdvancedConfig={showAdvancedConfig}
          setShowAdvancedConfig={setShowAdvancedConfig}
        />
      )}

      {/* Advanced Configuration Panel - Conditional low-confidence config */}
      {showAdvancedConfig && autoParseResults && (
        <AdvancedConfigPanel
          uploadedFiles={uploadedFiles}
          autoParseResults={autoParseResults}
          templates={templates}
          updateFileConfig={updateFileConfig}
          applyTemplate={applyTemplate}
          previewFile={previewFile}
          loading={loading}
        />
      )}

      {/* Validation Checklist - Interactive validation tracking */}
      {autoParseResults && (
        <ValidationChecklist
          validationChecklist={validationChecklist}
          updateValidationItem={updateValidationItem}
          validationProgress={validationProgress}
          autoParseResults={autoParseResults}
        />
      )}

      {/* Transaction Review - Data viewing with multiple modes */}
      {autoParseResults && (
        <TransactionReview
          autoParseResults={autoParseResults}
        />
      )}

      {/* Navigation */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginTop: theme.spacing.xl,
        paddingTop: theme.spacing.lg,
        borderTop: `1px solid ${theme.colors.border}`,
      }}>
        <Button
          variant="secondary"
          size="large"
          onClick={() => setCurrentStep(1)}
          leftIcon={<ChevronLeft size={18} />}
        >
          Back to Upload
        </Button>
        
        <Button
          variant="primary"
          size="large"
          disabled={loading || !allValidated}
          onClick={transformAllFiles}
          rightIcon={loading ? null : <ChevronRight size={18} />}
          loading={loading}
        >
          {loading ? 'Generating Report...' : 'Generate Financial Report'}
        </Button>
      </div>
    </div>
  );
}

export default ModernConfigureAndReviewStep;