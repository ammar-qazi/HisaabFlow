import React, { useState, useRef } from 'react';
import { useTheme } from '../../theme/ThemeProvider';
import toast from 'react-hot-toast';
import ContentArea from './ContentArea';
import ModernTransformAndExportStep from './ModernTransformAndExportStep';
import ModernFileUploadStep from './ModernFileUploadStep';
import ModernConfigureAndReviewStep from './ModernConfigureAndReviewStep';
import { createFileHandlers, createConfigHandlers, exportData } from '../../handlers/fileHandlers';
import { createProcessingHandlers } from '../../handlers/processingHandlers';
import { useAutoConfiguration } from '../../hooks/useAutoConfiguration';
import { usePreviewHandlers } from '../../hooks/usePreviewHandlers';
import { ConfigurationService } from '../../services/configurationService';

function ModernAppLogic({ currentStep, setCurrentStep }) {
  const theme = useTheme();
  
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [parsedResults, setParsedResults] = useState([]);
  const [transformedData, setTransformedData] = useState(null);
  const [transferAnalysis, setTransferAnalysis] = useState(null);
  const [manuallyConfirmedTransfers, setManuallyConfirmedTransfers] = useState([]);
  const [templates, setTemplates] = useState([]);
  
  const fileInputRef = useRef(null);
  const autoConfigHook = useAutoConfiguration();

  const clearMessages = () => { setError(null); };

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

  const applyTemplate = async (fileIndex, configName, showNotification = true) => {
    const result = await ConfigurationService.loadConfiguration(configName);
    if (result.success && result.config) {
      const processedConfig = ConfigurationService.processConfigurationForFile(result.config, uploadedFiles[fileIndex]?.fileName);
      setUploadedFiles(prev => {
        const updated = [...prev];
        updated[fileIndex] = { ...updated[fileIndex], selectedConfiguration: configName, ...processedConfig };
        return updated;
      });
      if (showNotification) {
        toast.success(`Configuration "${configName}" applied to ${uploadedFiles[fileIndex].fileName}`);
      }
    } else if (result.error) {
      setError(result.error);
    }
  };

  const { previewFile, previewFileById } = usePreviewHandlers(
    uploadedFiles, setUploadedFiles, setLoading, setError,
    applyTemplate, autoConfigHook.processDetectionResult, autoConfigHook.generateSuccessMessage
  );

  const handlerState = {
    uploadedFiles, setUploadedFiles, setLoading, setError,
    setParsedResults, setTransformedData, setTransferAnalysis, setCurrentStep,
    applyTemplate, previewFile, previewFileById, dynamicBankMapping: autoConfigHook.bankConfigMapping,
    manuallyConfirmedTransfers
  };

  const { handleFileSelect, removeFile } = createFileHandlers(handlerState);
  const { parseAllFiles, transformAllFiles } = createProcessingHandlers(handlerState);
  const { updateFileConfig, updateColumnMapping } = createConfigHandlers(handlerState);
  
  const parseAllFilesNoAdvance = async () => {
    const originalSetCurrentStep = handlerState.setCurrentStep;
    handlerState.setCurrentStep = (step) => { 
      console.log(`Modern workflow: setCurrentStep(${step}) call ignored during parseAllFilesNoAdvance`);
    };
    try {
      await parseAllFiles();
    } finally {
      handlerState.setCurrentStep = originalSetCurrentStep;
    }
  };

  const handleStartOver = () => {
    setCurrentStep(1); setUploadedFiles([]); setParsedResults([]);
    setTransformedData(null); setTransferAnalysis(null); setActiveTab(0); clearMessages();
    setManuallyConfirmedTransfers([]); // Reset manual confirmations
  };  const handleExport = () => exportData(transformedData, toast.success, setError);

  const messageStyles = {
    error: {
      backgroundColor: theme.colors.error + '20', color: theme.colors.error,
      border: `1px solid ${theme.colors.error}`, borderRadius: theme.borderRadius.md,
      padding: theme.spacing.md, marginBottom: theme.spacing.md, fontSize: '14px'
    },
  };

  const getStepInfo = () => {
    const steps = {
      1: { title: 'Upload Bank Statements', subtitle: 'Select CSV files from your bank to begin parsing' },
      2: { title: 'Configure & Review Data', subtitle: 'Auto-parse files and verify the extracted data' },
      3: { title: 'Export Results', subtitle: 'Download your processed data and transfer analysis' }
    };
    return steps[currentStep] || { title: 'HisaabFlow', subtitle: 'Smart Bank Statement Parser' };
  };

  const stepInfo = getStepInfo();

  return (
    <ContentArea title={stepInfo.title} subtitle={stepInfo.subtitle} padding="lg">

      {currentStep === 1 && (
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
      )}

      {currentStep === 2 && (
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
          parseAllFiles={parseAllFilesNoAdvance}
          parsedResults={parsedResults}
          transformAllFiles={transformAllFiles}
          setCurrentStep={setCurrentStep}
        />
      )}

      {currentStep === 3 && (
        <ModernTransformAndExportStep
          currentStep={currentStep}
          transformedData={transformedData}
          setTransformedData={setTransformedData}
          transferAnalysis={transferAnalysis}
          parsedResults={parsedResults}
          loading={loading}
          transformAllFiles={transformAllFiles}
          exportData={handleExport}
          onStartOver={handleStartOver}
          setCurrentStep={setCurrentStep}
          manuallyConfirmedTransfers={manuallyConfirmedTransfers}
          setManuallyConfirmedTransfers={setManuallyConfirmedTransfers}
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