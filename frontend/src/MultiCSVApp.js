import React, { useState, useRef } from 'react';
import axios from 'axios';
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

const API_BASE = 'http://127.0.0.1:8000';

// Configure axios
axios.defaults.timeout = 15000;
axios.defaults.headers.common['Content-Type'] = 'application/json';

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
  
  // Configurations (renamed from templates)
  const [templates, setTemplates] = useState([]); // Keep 'templates' name for backward compatibility
  
  const fileInputRef = useRef(null);

  // Clear messages
  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  // Load configurations on mount (UPDATED: Using new configuration system)
  React.useEffect(() => {
    const loadConfigurations = async () => {
      try {
        console.log('🔍 Loading bank configurations from /api/v3/configs');
        const response = await axios.get(`${API_BASE}/api/v3/configs`);
        console.log('✅ Configurations loaded:', response.data);
        setTemplates(response.data.configurations); // Keep 'templates' state name for now
      } catch (err) {
        console.error('❌ Failed to load configurations:', err);
        // Fallback to legacy templates if needed
        try {
          console.log('🔄 Falling back to legacy templates');
          const fallbackResponse = await axios.get(`${API_BASE}/templates`);
          setTemplates(fallbackResponse.data.templates);
        } catch (fallbackErr) {
          console.error('❌ Legacy template fallback also failed:', fallbackErr);
        }
      }
    };
    loadConfigurations();
  }, []);

  // Configuration and preview functions (UPDATED: Using new configuration system)
  const applyTemplate = async (fileIndex, configName) => {
    if (!configName) return;
    
    try {
      console.log(`🔍 Loading configuration: ${configName}`);
      const response = await axios.get(`${API_BASE}/api/v3/config/${encodeURIComponent(configName)}`);
      const config = response.data.config;
      
      console.log(`📋 Applying configuration ${configName}:`, config);
      
      setUploadedFiles(prev => {
        const updated = [...prev];
        updated[fileIndex] = {
          ...updated[fileIndex],
          selectedConfiguration: configName, // Updated field name
          config: config, // Store full config for transformation
          parseConfig: {
            start_row: config.start_row || 0,
            end_row: config.end_row || null,
            start_col: config.start_col || 0,
            end_col: config.end_col || null,
            encoding: 'utf-8'
          },
          columnMapping: config.column_mapping || {},
          bankName: config.bank_name || '',
          accountMapping: config.account_mapping || {}
        };
        return updated;
      });
      
      setSuccess(`Configuration "${configName}" applied to ${uploadedFiles[fileIndex].fileName}`);
      
    } catch (err) {
      console.error('❌ Configuration load failed:', err);
      // Fallback to legacy template system
      try {
        console.log('🔄 Falling back to legacy template system');
        const fallbackResponse = await axios.get(`${API_BASE}/template/${configName}`);
        const config = fallbackResponse.data.config;
        
        setUploadedFiles(prev => {
          const updated = [...prev];
          updated[fileIndex] = {
            ...updated[fileIndex],
            selectedTemplate: configName,
            parseConfig: {
              start_row: config.start_row || 0,
              end_row: config.end_row || null,
              start_col: config.start_col || 0,
              end_col: config.end_col || null,
              encoding: 'utf-8'
            },
            columnMapping: config.column_mapping || {}
          };
          return updated;
        });
        
        setSuccess(`Legacy template "${configName}" applied to ${uploadedFiles[fileIndex].fileName}`);
      } catch (fallbackErr) {
        setError(`Failed to apply configuration: ${err.response?.data?.detail || err.message}`);
      }
    }
  };

  const previewFile = async (fileIndex) => {
    const fileData = uploadedFiles[fileIndex];
    if (!fileData) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/preview/${fileData.fileId}`);
      
      setUploadedFiles(prev => {
        const updated = [...prev];
        updated[fileIndex] = {
          ...updated[fileIndex],
          preview: response.data
        };
        return updated;
      });
      
      // Auto-detect data range
      console.log(`🔍 Auto-detecting header row for ${fileData.fileName}`);
      const detectionResponse = await axios.get(`${API_BASE}/detect-range/${fileData.fileId}`);
      
      if (detectionResponse.data.success && detectionResponse.data.suggested_header_row !== null) {
        const detectedStartRow = detectionResponse.data.suggested_header_row;
        console.log(`📍 Detected start row: ${detectedStartRow} for ${fileData.fileName}`);
        
        setUploadedFiles(prev => {
          const updated = [...prev];
          updated[fileIndex] = {
            ...updated[fileIndex],
            parseConfig: {
              ...updated[fileIndex].parseConfig,
              start_row: detectedStartRow
            }
          };
          return updated;
        });
        
        setSuccess(`Smart detection: ${fileData.fileName} headers found at row ${detectedStartRow}`);
      }
      
    } catch (err) {
      setError(`Preview failed for ${fileData.fileName}: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

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
    previewFile
  };

  // Create handlers
  const { handleFileSelect, removeFile } = createFileHandlers(handlerState);
  const { parseAllFiles, transformAllFiles } = createProcessingHandlers(handlerState);
  const { updateFileConfig, updateColumnMapping } = createConfigHandlers(handlerState);

  // Start over function
  const handleStartOver = () => {
    setCurrentStep(1);
    setUploadedFiles([]);
    setParsedResults([]);
    setTransformedData(null);
    setTransferAnalysis(null);
    setActiveTab(0);
    clearMessages();
  };

  // Export wrapper
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
