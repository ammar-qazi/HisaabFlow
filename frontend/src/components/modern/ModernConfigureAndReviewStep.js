import React, { useState, useEffect } from 'react';
import { useTheme } from '../../theme/ThemeProvider';
import { Card, Button } from '../ui';
import { ChevronLeft, ChevronRight } from '../ui/Icons';

// Import modular components
import AutoParseHandler from './configure-review/AutoParseHandler';
import ConfidenceDashboard from './configure-review/ConfidenceDashboard';
import AdvancedConfigPanel from './configure-review/AdvancedConfigPanel';
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

  // Add this new useEffect hook
  useEffect(() => {
    // DEBUG: Log to confirm the effect runs and see the state of uploadedFiles.
    console.log('⚙️ Configure step effect running. Checking files for auto-preview.', uploadedFiles);
    // Automatically run bank detection for any file that hasn't been previewed yet
    uploadedFiles.forEach((file, index) => {
      // DEBUG: Log the state of each file to see why preview might be skipped.
      // CORRECTED LOGIC: Check for the specific 'confidence' property, not just 'preview'.
      console.log(`🔎 Checking file ${index}: ${file.fileName}`, { hasConfidence: file.confidence !== undefined, fileObject: file });
      if (file.confidence === undefined) { // If confidence isn't set, we need to run the full preview handler.
        console.log(`🤖 Triggering preview for ${file.fileName} because confidence score is missing.`);
        previewFile(index);
      }
    });
  }, [uploadedFiles, previewFile]); // Add dependencies to avoid stale closures. The `if` condition prevents re-running on already previewed files.

  if (currentStep < 2 || uploadedFiles.length === 0) return null;

  // Use parsedResults from parent state instead of local autoParseResults
  const autoParseResults = parsedResults;
  
  // Debug logging
  console.log('🔍 ModernConfigureAndReviewStep - parsedResults:', parsedResults);
  console.log('🔍 ModernConfigureAndReviewStep - autoParseResults:', autoParseResults);

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
      {showAdvancedConfig && (
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

      {/* Transaction Review - Data viewing with multiple modes */}
      {autoParseResults && (
        <TransactionReview
        autoParseResults={autoParseResults}
        uploadedFiles={uploadedFiles} // Add this prop
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
          disabled={loading}
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