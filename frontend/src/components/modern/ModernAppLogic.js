import React, { useState, useRef } from 'react';
import { useTheme } from '../../theme/ThemeProvider';
import ContentArea from './ContentArea';
import ModernTransformAndExportStep from './ModernTransformAndExportStep';

// Import existing components - preserve all functionality
import FileUploadStep from '../multi/FileUploadStep';
import FileConfigurationStep from '../multi/FileConfigurationStep';
import DataReviewStep from '../multi/DataReviewStep';
import ResultsStep from '../multi/ResultsStep';

// Import modern components
import ModernFileUploadStep from './ModernFileUploadStep';
import ModernConfigureAndReviewStep from './ModernConfigureAndReviewStep';

// Import handlers - preserve all business logic
import { createFileHandlers, createConfigHandlers, exportData } from '../multi/FileHandlers';
import { createProcessingHandlers } from '../multi/ProcessingHandlers';

// Import hooks and services
import { useAutoConfiguration } from '../../hooks/useAutoConfiguration';
import { usePreviewHandlers } from '../../hooks/usePreviewHandlers';
import { ConfigurationService } from '../../services/configurationService';

function ModernAppLogic({ currentStep, setCurrentStep }) {
  const theme = useTheme();
  
  // Modern component toggle system - Phase 3 implementation
  const [useModernComponents, setUseModernComponents] = useState(true);
  
  // State - PRESERVE ALL EXISTING STATE
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [parsedResults, setParsedResults] = useState([]);
  const [transformedData, setTransformedData] = useState(null);
  const [transferAnalysis, setTransferAnalysis] = useState(null);
  const [templates, setTemplates] = useState([]);
  
  const fileInputRef = useRef(null);
  const autoConfigHook = useAutoConfiguration();

  const clearMessages = () => { setError(null); setSuccess(null); };

  // Load configurations on mount
  React.useEffect(() => {
    const loadConfigurations = async () => {
      const result = await ConfigurationService.loadConfigurations();
      if (result.success) {
        setTemplates(result.configurations);
        if (result.configurations && result.raw_bank_names) {
          autoConfigHook.updateBankConfigMapping(result.configurations, result.raw_bank_names);
        }
      } else {
        setError(result.error);
      }
    };
    loadConfigurations();
  }, []);

  // Apply template function
  const applyTemplate = async (fileIndex, configName) => {
    const result = await ConfigurationService.loadConfiguration(configName);
    if (result.success && result.config) {
      const processedConfig = ConfigurationService.processConfigurationForFile(result.config, uploadedFiles[fileIndex]?.fileName);
      setUploadedFiles(prev => {
        const updated = [...prev];
        updated[fileIndex] = { ...updated[fileIndex], selectedConfiguration: configName, ...processedConfig };
        return updated;
      });
      setSuccess(`Configuration "${configName}" applied to ${uploadedFiles[fileIndex].fileName}`);
    } else if (result.error) {
      setError(result.error);
    }
  };

  // Preview handlers
  const { previewFile, previewFileById } = usePreviewHandlers(
    uploadedFiles, setUploadedFiles, setLoading, setError, setSuccess,
    applyTemplate, autoConfigHook.processDetectionResult, autoConfigHook.generateSuccessMessage
  );

  // Handler state
  const handlerState = {
    uploadedFiles, setUploadedFiles, setLoading, setError, setSuccess,
    setParsedResults, setTransformedData, setTransferAnalysis, setCurrentStep,
    applyTemplate, previewFile, previewFileById, dynamicBankMapping: autoConfigHook.bankConfigMapping
  };

  // Create handlers
  const { handleFileSelect, removeFile } = createFileHandlers(handlerState);
  const { parseAllFiles, transformAllFiles } = createProcessingHandlers(handlerState);
  const { updateFileConfig, updateColumnMapping } = createConfigHandlers(handlerState);
  
  // Create a modified parseAllFiles for modern workflow that doesn't auto-advance
  const parseAllFilesNoAdvance = async () => {
    const originalSetCurrentStep = handlerState.setCurrentStep;
    
    // Temporarily replace setCurrentStep with a no-op for modern workflow
    if (useModernComponents) {
      handlerState.setCurrentStep = (step) => { 
        console.log(`Modern workflow: setCurrentStep(${step}) call ignored during parseAllFilesNoAdvance`);
      };
    }
    
    try {
      await parseAllFiles();
    } finally {
      // Restore original setCurrentStep
      handlerState.setCurrentStep = originalSetCurrentStep;
    }
  };

  // Utility functions
  const handleStartOver = () => {
    setCurrentStep(1); setUploadedFiles([]); setParsedResults([]);
    setTransformedData(null); setTransferAnalysis(null); setActiveTab(0); clearMessages();
  };
  const handleExport = () => exportData(transformedData, setSuccess, setError);

  // Clear success messages when navigating to step 3 to avoid misleading banners
  React.useEffect(() => {
    if (currentStep === 3 && !transformedData && success) {
      console.log('🧹 Clearing success message when entering step 3 without transformed data');
      setSuccess(null);
    }
  }, [currentStep, transformedData, success]);

  // Message styles
  const messageStyles = {
    error: {
      backgroundColor: theme.colors.error + '20', color: theme.colors.error,
      border: `1px solid ${theme.colors.error}`, borderRadius: theme.borderRadius.md,
      padding: theme.spacing.md, marginBottom: theme.spacing.md, fontSize: '14px'
    },
    success: {
      backgroundColor: theme.colors.success + '20', color: theme.colors.success,
      border: `1px solid ${theme.colors.success}`, borderRadius: theme.borderRadius.md,
      padding: theme.spacing.md, marginBottom: theme.spacing.md, fontSize: '14px'
    }
  };

  // Step info
  const getStepInfo = () => {
    if (useModernComponents) {
      // Modern 3-step workflow
      const steps = {
        1: { title: 'Upload Bank Statements', subtitle: 'Select CSV files from your bank to begin parsing' },
        2: { title: 'Configure & Review Data', subtitle: 'Auto-parse files and verify the extracted data' },
        3: { title: 'Export Results', subtitle: 'Download your processed data and transfer analysis' }
      };
      return steps[currentStep] || { title: 'HisaabFlow', subtitle: 'Smart Bank Statement Parser' };
    } else {
      // Legacy 4-step workflow
      const steps = {
        1: { title: 'Upload Bank Statements', subtitle: 'Select CSV files from your bank to begin parsing' },
        2: { title: 'Configure Parsing Rules', subtitle: 'Map columns and apply templates for accurate data extraction' },
        3: { title: 'Review Parsed Data', subtitle: 'Verify the extracted data before final processing' },
        4: { title: 'Export Results', subtitle: 'Download your processed data and transfer analysis' }
      };
      return steps[currentStep] || { title: 'HisaabFlow', subtitle: 'Smart Bank Statement Parser' };
    }
  };

  const stepInfo = getStepInfo();

  return (
    <ContentArea title={stepInfo.title} subtitle={stepInfo.subtitle} padding="lg">
      {error && <div style={messageStyles.error}>{error}</div>}
      {success && <div style={messageStyles.success}>{success}</div>}

      {/* Development Toggle - Phase 3 Testing */}
      <div style={{
        position: 'fixed',
        top: '80px',
        right: '20px',
        zIndex: 100,
        backgroundColor: theme.colors.background.paper,
        padding: theme.spacing.sm,
        borderRadius: theme.borderRadius.md,
        border: `1px solid ${theme.colors.border}`,
        boxShadow: theme.shadows.md,
      }}>
        <label style={{ 
          fontSize: '12px', 
          color: theme.colors.text.secondary,
          display: 'flex',
          alignItems: 'center',
          gap: theme.spacing.xs,
          cursor: 'pointer'
        }}>
          <input
            type="checkbox"
            checked={useModernComponents}
            onChange={(e) => setUseModernComponents(e.target.checked)}
            style={{ marginRight: '4px' }}
          />
          Modern UI {useModernComponents ? '✨' : ''}
        </label>
      </div>

      {/* Step-based Conditional Rendering - Only show current step */}
      {currentStep === 1 && (
        useModernComponents ? (
          <ModernFileUploadStep
            fileInputRef={fileInputRef} 
            handleFileSelect={handleFileSelect}
            uploadedFiles={uploadedFiles} 
            activeTab={activeTab} 
            setActiveTab={setActiveTab} 
            removeFile={removeFile}
            currentStep={currentStep}
            setCurrentStep={setCurrentStep}
          />
        ) : (
          <FileUploadStep
            fileInputRef={fileInputRef} 
            handleFileSelect={handleFileSelect}
            uploadedFiles={uploadedFiles} 
            activeTab={activeTab} 
            setActiveTab={setActiveTab} 
            removeFile={removeFile}
          />
        )
      )}

      {currentStep === 2 && (
        useModernComponents ? (
          <ModernConfigureAndReviewStep
            currentStep={currentStep}
            uploadedFiles={uploadedFiles}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            templates={templates}
            loading={loading}
            updateFileConfig={updateFileConfig}
            updateColumnMapping={updateColumnMapping}
            applyTemplate={applyTemplate}
            previewFile={previewFile}
            parseAllFiles={useModernComponents ? parseAllFilesNoAdvance : parseAllFiles}
            parsedResults={parsedResults}
            transformAllFiles={transformAllFiles}
            setCurrentStep={setCurrentStep}
          />
        ) : (
          <FileConfigurationStep
            currentStep={currentStep} 
            uploadedFiles={uploadedFiles} 
            activeTab={activeTab}
            templates={templates} 
            loading={loading} 
            updateFileConfig={updateFileConfig}
            updateColumnMapping={updateColumnMapping} 
            applyTemplate={applyTemplate}
            previewFile={previewFile} 
            parseAllFiles={parseAllFiles}
          />
        )
      )}

      {currentStep === 3 && (
        useModernComponents ? (
          <ModernTransformAndExportStep
            currentStep={currentStep}
            transformedData={transformedData}
            transferAnalysis={transferAnalysis}
            parsedResults={parsedResults}
            loading={loading}
            transformAllFiles={transformAllFiles}
            exportData={handleExport}
            onStartOver={handleStartOver}
            setCurrentStep={setCurrentStep}
          />
        ) : (
          <DataReviewStep
            currentStep={currentStep} parsedResults={parsedResults}
            activeTab={activeTab} loading={loading} transformAllFiles={transformAllFiles}
          />
        )
      )}

      {currentStep === 4 && !useModernComponents && ( // ResultsStep only for legacy step 4
        <ResultsStep
          currentStep={currentStep} transformedData={transformedData}
          transferAnalysis={transferAnalysis} exportData={handleExport} onStartOver={handleStartOver}
        />
      )}
      
      {loading && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
          <div style={{
            backgroundColor: theme.colors.background.paper, padding: theme.spacing.xl,
            borderRadius: theme.borderRadius.lg, textAlign: 'center',
            color: theme.colors.text.primary, boxShadow: theme.shadows.xl
          }}>
            <div style={{
              width: '40px', height: '40px', border: `4px solid ${theme.colors.divider}`,
              borderTop: `4px solid ${theme.colors.primary}`, borderRadius: '50%',
              animation: 'spin 1s linear infinite', margin: '0 auto 16px'
            }} />
            Processing multiple CSV files...
          </div>
        </div>
      )}
    </ContentArea>
  );
}

export default ModernAppLogic;