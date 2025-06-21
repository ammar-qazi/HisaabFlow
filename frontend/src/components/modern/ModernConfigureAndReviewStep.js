import React, { useState, useEffect, useRef } from 'react';
import { useTheme } from '../../theme/ThemeProvider';
import { Card, Button } from '../ui';
import { ChevronLeft, ChevronRight } from '../ui/Icons';
import toast from 'react-hot-toast';

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
  // Add this ref to track which files have been sent for processing
  const processedFileIds = useRef(new Set());

  useEffect(() => {
    // This function will run all previews and then show a single toast.
    const runAllPreviews = async (filesToProcess) => {
      // 1. Create a list of preview promises for the new files.
      const previewPromises = filesToProcess.map((file, index) => 
        previewFile(uploadedFiles.findIndex(f => f.fileId === file.fileId))
      );

      // 2. Wait for all the new previews to complete.
      if (previewPromises.length > 0) {
        const results = await Promise.all(previewPromises);
        
        // 3. Count successes.
        const successfulConfigCount = results.filter(msg => msg !== null).length;

        // 4. Show a single, consolidated toast notification.
        if (successfulConfigCount > 0) {
          toast.success(
            `Successfully applied configurations to ${successfulConfigCount} file(s) based on bank detection.`
          );
        }
      }
    };

    // Find files that are new and haven't been processed yet.
    const filesToProcess = uploadedFiles.filter(
      file => !processedFileIds.current.has(file.fileId)
    );

    // If there are new files to process, run the logic.
    if (filesToProcess.length > 0) {
      // Immediately add their IDs to our ref to "lock" them and prevent re-processing.
      filesToProcess.forEach(file => processedFileIds.current.add(file.fileId));
      runAllPreviews(filesToProcess);
    }

  }, [uploadedFiles, previewFile]);

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