import React, { useState, useRef } from 'react';
import './index.css';

// Import modular components
import UserSettings from './components/multi/UserSettings';
import BankRulesSettings from './components/multi/BankRulesSettings';
import FileUploadStep from './components/multi/FileUploadStep';
import FileConfigurationStep from './components/multi/FileConfigurationStep';
import DataReviewStep from './components/multi/DataReviewStep';
import ResultsStep from './components/multi/ResultsStep';

// Import handlers
import { 
  createFileHandlers, 
  createConfigHandlers,
  exportData 
} from './components/multi/FileHandlers';
import { createProcessingHandlers } from './components/multi/ProcessingHandlers';

// Import hooks and services
import { useAutoConfiguration } from './hooks/useAutoConfiguration';
import { usePreviewHandlers } from './hooks/usePreviewHandlers';
import { ConfigurationService } from './services/configurationService';

function MultiCSVApp() {
  // Multi-CSV state
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  const [currentStep, setCurrentStep] = useState(1);
  
  // User settings
  const [userName, setUserName] = useState('Ammar Qazi');
  const [dateTolerance, setDateTolerance] = useState(24);
  const [enableTransferDetection, setEnableTransferDetection] = useState(true);
  
  // Bank-specific rules settings
  const [bankRulesSettings, setBankRulesSettings] = useState({
    enableNayaPayRules: true,
    enableTransferwiseRules: true,
    enableUniversalRules: true
  });
  
  // Processing state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Results
  const [parsedResults, setParsedResults] = useState([]);
  const [transformedData, setTransformedData] = useState(null);
  const [transferAnalysis, setTransferAnalysis] = useState(null);
  
  // Configurations
  const [templates, setTemplates] = useState([]);
  
  const fileInputRef = useRef(null);

  // Initialize hooks
  const autoConfigHook = useAutoConfiguration();

  // Clear messages
  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  // Load configurations on mount
  React.useEffect(() => {
    const loadConfigurations = async () => {
      const result = await ConfigurationService.loadConfigurations();
      if (result.success) {
        setTemplates(result.configurations);
        
        // Update dynamic bank mapping with loaded configurations
        if (result.configurations && result.raw_bank_names) {
          autoConfigHook.updateBankConfigMapping(result.configurations, result.raw_bank_names);
        }
      } else {
        setError(result.error);
      }
    };
    loadConfigurations();
  }, []); // Remove autoConfigHook dependency to prevent loop

  // Configuration application function
  const applyTemplate = async (fileIndex, configName) => {
    const result = await ConfigurationService.loadConfiguration(configName);
    
    if (result.success && result.config) {
      const processedConfig = ConfigurationService.processConfigurationForFile(result.config, uploadedFiles[fileIndex]?.fileName);
      
      setUploadedFiles(prev => {
        const updated = [...prev];
        updated[fileIndex] = {
          ...updated[fileIndex],
          selectedConfiguration: configName,
          ...processedConfig
        };
        return updated;
      });
      
      setSuccess(`Configuration "${configName}" applied to ${uploadedFiles[fileIndex].fileName}`);
    } else if (result.error) {
      setError(result.error);
    }
  };

  // Initialize preview handlers
  const { previewFile, previewFileById } = usePreviewHandlers(
    uploadedFiles,
    setUploadedFiles,
    setLoading,
    setError,
    setSuccess,
    applyTemplate,
    autoConfigHook.processDetectionResult,
    autoConfigHook.generateSuccessMessage
  );

  // Create state object for handlers
  const handlerState = {
    uploadedFiles,
    setUploadedFiles,
    userName,
    dateTolerance,
    enableTransferDetection,
    bankRulesSettings,
    setLoading,
    setError,
    setSuccess,
    setParsedResults,
    setTransformedData,
    setTransferAnalysis,
    setCurrentStep,
    applyTemplate,
    previewFile,
    previewFileById,
    dynamicBankMapping: autoConfigHook.bankConfigMapping  // Pass dynamic mapping
  };

  // Create handlers
  const { handleFileSelect, removeFile } = createFileHandlers(handlerState);
  const { parseAllFiles, transformAllFiles } = createProcessingHandlers(handlerState);
  const { updateFileConfig, updateColumnMapping } = createConfigHandlers(handlerState);

  // Utility functions
  const handleStartOver = () => {
    setCurrentStep(1);
    setUploadedFiles([]);
    setParsedResults([]);
    setTransformedData(null);
    setTransferAnalysis(null);
    setActiveTab(0);
    clearMessages();
  };

  const handleExport = () => {
    exportData(transformedData, setSuccess, setError);
  };

  return (
    <div className="app">
      <div className="container">
        <div className="header">
          <h1>🚀 Multi-CSV Bank Statement Parser</h1>
          <p>Upload multiple CSV files, detect transfers, and export unified data</p>
        </div>
        
        <div className="main-content">
          {error && <div className="error">{error}</div>}
          {success && <div className="success">{success}</div>}

          {/* User Settings */}
          <UserSettings
            userName={userName}
            setUserName={setUserName}
            dateTolerance={dateTolerance}
            setDateTolerance={setDateTolerance}
            enableTransferDetection={enableTransferDetection}
            setEnableTransferDetection={setEnableTransferDetection}
          />
          
          {/* Bank Rules Settings */}
          <BankRulesSettings
            bankRulesSettings={bankRulesSettings}
            setBankRulesSettings={setBankRulesSettings}
          />
          
          {/* File Upload Step */}
          <FileUploadStep
            fileInputRef={fileInputRef}
            handleFileSelect={handleFileSelect}
            uploadedFiles={uploadedFiles}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            removeFile={removeFile}
          />

          {/* File Configuration Step */}
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

          {/* Data Review Step */}
          <DataReviewStep
            currentStep={currentStep}
            parsedResults={parsedResults}
            activeTab={activeTab}
            loading={loading}
            transformAllFiles={transformAllFiles}
          />

          {/* Results Step */}
          <ResultsStep
            currentStep={currentStep}
            transformedData={transformedData}
            transferAnalysis={transferAnalysis}
            exportData={handleExport}
            onStartOver={handleStartOver}
          />
          
          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              Processing multiple CSV files...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default MultiCSVApp;
