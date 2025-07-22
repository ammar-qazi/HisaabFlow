import React, { useState, useEffect, useRef } from 'react';
import { useTheme } from '../../theme/ThemeProvider';
import { Card, Button } from '../ui';
import { ChevronLeft, ChevronRight } from '../ui/Icons';
import toast from 'react-hot-toast';
import { shouldTriggerUnknownBankWorkflow, getUnknownBankFiles } from '../../utils/bankDetection';

// Import modular components
import AutoParseHandler from '../configure-review/AutoParseHandler';
import ConfidenceDashboard from '../configure-review/ConfidenceDashboard';
import AdvancedConfigPanel from '../configure-review/AdvancedConfigPanel';
import TransactionReview from '../configure-review/TransactionReview';
import UnknownBankPanel from '../configure-review/UnknownBankPanel';

function ConfigureAndReviewStep({ 
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

  // Clear processed file IDs when step changes or uploadedFiles change significantly
  useEffect(() => {
    if (currentStep !== 2) {
      processedFileIds.current.clear();
    }
  }, [currentStep]);

  // Reset processed IDs when the number of files decreases (indicates going back/starting fresh)
  useEffect(() => {
    const currentFileIds = new Set(uploadedFiles.map(f => f.fileId));
    const processedIds = Array.from(processedFileIds.current);
    const staleProcesedIds = processedIds.filter(id => !currentFileIds.has(id));
    
    if (staleProcesedIds.length > 0) {
      console.log('[DEBUG] Clearing stale processed file IDs:', staleProcesedIds);
      staleProcesedIds.forEach(id => processedFileIds.current.delete(id));
    }
    
    // Also log current state for debugging
    console.log('[DEBUG] Current file IDs:', Array.from(currentFileIds));
    console.log('[DEBUG] Processed file IDs:', Array.from(processedFileIds.current));
  }, [uploadedFiles]);

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
      console.log('[DEBUG] Processing new files for preview:', filesToProcess.map(f => f.fileName));
      
      // Immediately add their IDs to our ref to "lock" them and prevent re-processing.
      filesToProcess.forEach(file => processedFileIds.current.add(file.fileId));
      
      // Add a small delay to avoid conflicting with auto-detection
      setTimeout(() => {
        runAllPreviews(filesToProcess);
      }, 500);
    }

  }, [uploadedFiles, previewFile]);

  if (currentStep < 2 || uploadedFiles.length === 0) return null;

  // Filter parsedResults to only include files that are currently uploaded
  // This ensures the Config & Review page stays in sync when files are removed
  const currentFileIds = new Set(uploadedFiles.map(f => f.fileId));
  const autoParseResults = parsedResults ? parsedResults.filter(result => 
    currentFileIds.has(result.file_id)
  ) : [];
  
  // Debug logging
  console.log('[DEBUG] ConfigureAndReviewStep - All parsedResults:', parsedResults?.length || 0);
  console.log('[DEBUG] ConfigureAndReviewStep - Current uploadedFiles:', uploadedFiles.length);
  console.log('[DEBUG] ConfigureAndReviewStep - Filtered autoParseResults:', autoParseResults?.length || 0);
  console.log('[DEBUG] ConfigureAndReviewStep - File IDs match:', 
    autoParseResults?.map(r => r.file_id) || []);

  // Check for unknown banks that need configuration
  const hasUnknownFiles = shouldTriggerUnknownBankWorkflow(uploadedFiles);
  const unknownFiles = getUnknownBankFiles(uploadedFiles);

  const handleConfigCreated = async (newConfig) => {
    console.log('[DEBUG] New bank configuration created:', newConfig);
    toast.success(`Created configuration for ${newConfig.displayName}`);

    // Re-run bank detection on the files that were unknown
    const unknownFiles = getUnknownBankFiles(uploadedFiles);
    if (unknownFiles.length > 0) {
      toast.loading('Applying new configuration...', { id: 're-detect' });
      const previewPromises = unknownFiles.map(file => {
        const fileIndex = uploadedFiles.findIndex(f => f.fileId === file.fileId);
        if (fileIndex !== -1) {
          return previewFile(fileIndex);
        }
        return Promise.resolve(null);
      });

      try {
        await Promise.all(previewPromises);
        toast.success('Successfully applied new configuration!', { id: 're-detect' });
        
        // Re-parse all files with the new configuration to refresh data completely
        toast.loading('Re-processing data with new configuration...', { id: 'reparse' });
        try {
          await parseAllFiles();
          toast.success('Data refreshed with new configuration!', { id: 'reparse' });
        } catch (error) {
          toast.error('Failed to re-process data with new configuration.', { id: 'reparse' });
          console.error('Error re-parsing files:', error);
        }
      } catch (error) {
        toast.error('Failed to apply new configuration.', { id: 're-detect' });
        console.error('Error re-running previews:', error);
      }
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.lg }}>
      {/* Unknown Bank Panel - Shows when files need manual configuration */}
      {hasUnknownFiles && (
        <UnknownBankPanel 
          unknownFiles={unknownFiles}
          onConfigCreated={handleConfigCreated}
          loading={loading}
        />
      )}

      {/* Auto-parse Handler - Manages the parsing logic */}
      <AutoParseHandler
        uploadedFiles={uploadedFiles}
        parseAllFiles={parseAllFiles}
        autoParseResults={autoParseResults}
        setShowAdvancedConfig={setShowAdvancedConfig}
        loading={loading}
      />

      {/* Confidence Dashboard - Shows parsed results metrics */}
      {autoParseResults && autoParseResults.length > 0 && (
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
      {autoParseResults && autoParseResults.length > 0 && (
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

export default ConfigureAndReviewStep;