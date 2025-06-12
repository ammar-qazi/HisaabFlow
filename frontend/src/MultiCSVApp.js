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

  // Load configurations on mount
  React.useEffect(() => {
    const loadConfigurations = async () => {
      try {
        console.log('🔍 Loading bank configurations from /api/v3/configs');
        const response = await axios.get(`${API_BASE}/api/v3/configs`);
        console.log('✅ Configurations loaded:', response.data);
        setTemplates(response.data.configurations);
      } catch (err) {
        console.error('❌ Failed to load configurations:', err);
        setError('Failed to load bank configurations. Please check if the backend is running.');
      }
    };
    loadConfigurations();
  }, []);

  // Configuration and preview functions (UPDATED: Using new configuration system)
  const applyTemplate = async (fileIndex, configName) => {
    if (!configName) {
      console.log('🔍 No configuration selected - user will use manual column mapping with standard Cashew fields');
      return;
    }
    
    try {
      console.log(`🔍 Loading configuration: ${configName}`);
      const response = await axios.get(`${API_BASE}/api/v3/config/${encodeURIComponent(configName)}`);
      const config = response.data.config;
      
      console.log(`📋 Applying configuration ${configName}:`, config);
      
      // 🔍 DEBUG: Log column mapping being applied for Option B testing
      console.log('🔍 Configuration Application Debug:');
      console.log('  - config.column_mapping:', config.column_mapping);
      console.log('  - Will set columnMapping to:', config.column_mapping || {});
      
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
      console.log('🔍 Configuration load failed - user will use manual column mapping with standard Cashew fields');
      setError(`Failed to load configuration "${configName}": ${err.response?.data?.detail || err.message}`);
    }
  };

  const previewFileById = async (fileId) => {
    console.log(`🔍 DEBUG: previewFileById called with fileId: ${fileId}`);
    
    setLoading(true);
    try {
      console.log(`🔍 DEBUG: Requesting preview for fileId: ${fileId}`);
      const response = await axios.get(`${API_BASE}/preview/${fileId}`);
      
      console.log('🔍 DEBUG: Preview response received:', response.data);
      
      // Find the file in uploadedFiles by fileId and update it
      setUploadedFiles(prev => {
        const updated = prev.map(file => {
          if (file.fileId === fileId) {
            console.log(`🔍 DEBUG: Updating preview data for ${file.fileName}`);
            return {
              ...file,
              preview: {
                ...response.data,
                suggested_header_row: response.data.suggested_header_row,
                suggested_data_start_row: response.data.suggested_data_start_row
              }
            };
          }
          return file;
        });
        return updated;
      });
      
      // Handle auto-configuration based on backend bank detection
      const backendBankDetection = response.data.bank_detection;
      if (backendBankDetection && backendBankDetection.detected_bank !== 'unknown') {
        const detectedBank = backendBankDetection.detected_bank;
        const confidence = backendBankDetection.confidence;
        
        console.log(`🏦 DEBUG: Backend detected bank: ${detectedBank} (${confidence.toFixed(2)} confidence)`);
        
        // Map backend bank names to configuration names
        const bankToConfigMap = {
          'nayapay': 'Nayapay Configuration',
          'wise_usd': 'Wise_Usd Configuration', 
          'wise_eur': 'Wise_Eur Configuration',
          'wise_huf': 'Wise_Huf Configuration'
        };
        
        const suggestedConfig = bankToConfigMap[detectedBank];
        
        if (suggestedConfig && confidence > 0.5) {
          console.log(`🔧 DEBUG: Auto-applying configuration: ${suggestedConfig}`);
          
          // Find the file index and apply configuration
          const fileIndex = uploadedFiles.findIndex(f => f.fileId === fileId);
          if (fileIndex !== -1) {
            setTimeout(() => {
              applyTemplate(fileIndex, suggestedConfig);
            }, 500);
          }
          
          setSuccess(`Smart detection: ${detectedBank} bank detected (${(confidence * 100).toFixed(0)}% confidence). Auto-applied "${suggestedConfig}".`);
        }
      }
      
    } catch (err) {
      console.error('❌ DEBUG: Preview error:', err);
      setError(`Preview failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const previewFile = async (fileIndex) => {
    console.log(`🔍 DEBUG: previewFile called with fileIndex: ${fileIndex}`);
    console.log(`🔍 DEBUG: uploadedFiles length: ${uploadedFiles.length}`);
    
    const fileData = uploadedFiles[fileIndex];
    if (!fileData) {
      console.error(`❌ DEBUG: No file data found at index ${fileIndex}`);
      return;
    }
    
    console.log(`🔍 DEBUG: Found file data:`, fileData.fileName, fileData.fileId);
    
    setLoading(true);
    try {
      // 🔧 CRITICAL FIX: Let backend handle bank-aware header detection automatically
      console.log(`🔍 DEBUG: Requesting bank-aware preview for ${fileData.fileName}`);
      const response = await axios.get(`${API_BASE}/preview/${fileData.fileId}`);
      
      console.log('🔍 DEBUG: Preview response:', response.data);
      
      // Store preview data with bank-detected information
      setUploadedFiles(prev => {
        const updated = [...prev];
        updated[fileIndex] = {
          ...updated[fileIndex],
          preview: {
            ...response.data,
            // Store bank-detected row information for parsing
            suggested_header_row: response.data.suggested_header_row,
            suggested_data_start_row: response.data.suggested_data_start_row
          }
        };
        return updated;
      });
      
      // 🔧 NEW: Auto-apply configuration based on backend bank detection
      const backendBankDetection = response.data.bank_detection;
      if (backendBankDetection && backendBankDetection.detected_bank !== 'unknown') {
        const detectedBank = backendBankDetection.detected_bank;
        const confidence = backendBankDetection.confidence;
        const headerRow = response.data.suggested_header_row;
        const dataRow = response.data.suggested_data_start_row;
        
        console.log(`🏦 Bank detected: ${detectedBank} (${confidence.toFixed(2)} confidence)`);
        console.log(`📋 Headers at row ${headerRow}, data starts at row ${dataRow}`);
        
        // Map backend bank names to frontend configuration names
        const bankToConfigMap = {
          'nayapay': 'Nayapay Configuration',
          'wise_usd': 'Wise_Usd Configuration', 
          'wise_eur': 'Wise_Eur Configuration',
          'wise_huf': 'Wise_Huf Configuration'
        };
        
        const suggestedConfig = bankToConfigMap[detectedBank];
        
        if (suggestedConfig && confidence > 0.5) {
          console.log(`🔧 Auto-applying configuration: ${suggestedConfig}`);
          
          // Update the selectedConfiguration immediately
          setUploadedFiles(prev => {
            const updated = [...prev];
            updated[fileIndex] = {
              ...updated[fileIndex],
              selectedConfiguration: suggestedConfig
            };
            return updated;
          });
          
          // Apply the configuration after a short delay
          setTimeout(() => {
            applyTemplate(fileIndex, suggestedConfig);
          }, 500);
          
          setSuccess(`Smart detection: ${detectedBank} bank detected (${(confidence * 100).toFixed(0)}% confidence). Auto-applied "${suggestedConfig}". Headers at row ${headerRow}, data starts at row ${dataRow}.`);
        } else {
          setSuccess(`Bank detected: ${detectedBank} (${(confidence * 100).toFixed(0)}% confidence), but confidence too low for auto-configuration. Please select manually.`);
        }
      } else {
        console.log(`📝 Using manual configuration for ${fileData.fileName}`);
        setSuccess(`Preview loaded for ${fileData.fileName} - using manual configuration`);
      }
      
    } catch (err) {
      console.error('❌ Preview error:', err);
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
    previewFile,
    previewFileById
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
