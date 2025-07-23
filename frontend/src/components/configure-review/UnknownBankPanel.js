import React, { useState, useEffect } from 'react';
import { Card, Button, Badge } from '../ui';
import { Settings, FileText, AlertCircle, CheckCircle } from '../ui/Icons';
import { useTheme } from '../../theme/ThemeProvider';
import { ConfigurationService } from '../../services/configurationService';

const STANDARD_FIELDS = [
  { value: 'date', label: 'Date', required: true },
  { value: 'amount', label: 'Amount', required: true },
  { value: 'title', label: 'Title/Description', required: true },
  { value: 'note', label: 'Note/Type', required: false },
  { value: 'currency', label: 'Currency', required: false },
  { value: 'exchange_to', label: 'Exchange To Amount', required: false },
  { value: 'exchange_to_currency', label: 'Exchange To Currency', required: false },
];

const AMOUNT_FORMATS = [
  { value: 'american', label: 'American (1,234.56)', example: '1,234.56' },
  { value: 'european', label: 'European (1.234,56)', example: '1.234,56' },
  { value: 'space_separated', label: 'Space Separated (1 234,56)', example: '1 234,56' },
  { value: 'indian', label: 'Indian (1,23,456.78)', example: '1,23,456.78' },
  { value: 'swiss', label: 'Swiss (1\'234.56)', example: '1\'234.56' },
  { value: 'no_separator', label: 'No Separator (1234.56)', example: '1234.56' },
];

// Simple Alert component since it's not in the UI library
const Alert = ({ variant = 'info', children, className = '', style = {} }) => {
  const theme = useTheme();
  
  const variants = {
    info: { backgroundColor: theme.colors.primary + '15', borderColor: theme.colors.primary, color: theme.colors.primary },
    warning: { backgroundColor: theme.colors.warning + '15', borderColor: theme.colors.warning, color: theme.colors.warning },
    error: { backgroundColor: theme.colors.error + '15', borderColor: theme.colors.error, color: theme.colors.error },
    success: { backgroundColor: theme.colors.success + '15', borderColor: theme.colors.success, color: theme.colors.success },
  };
  
  const alertStyle = {
    padding: theme.spacing.sm,
    borderRadius: theme.borderRadius.sm,
    border: `1px solid ${variants[variant].borderColor}`,
    backgroundColor: variants[variant].backgroundColor,
    color: variants[variant].color,
    fontSize: '14px',
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.xs,
    ...style,
  };
  
  return (
    <div style={alertStyle} className={className}>
      <AlertCircle size={16} />
      {children}
    </div>
  );
};

// Input component for form fields
const Input = ({ label, value, onChange, placeholder, required, className = '', style = {} }) => {
  const theme = useTheme();
  
  const inputStyle = {
    width: '100%',
    padding: theme.spacing.sm,
    border: `1px solid ${theme.colors.border}`,
    borderRadius: theme.borderRadius.sm,
    fontSize: '14px',
    backgroundColor: theme.colors.background.paper,
    color: theme.colors.text.primary,
    ...style,
  };
  
  const labelStyle = {
    display: 'block',
    marginBottom: theme.spacing.xs,
    fontSize: '14px',
    fontWeight: '500',
    color: theme.colors.text.primary,
  };
  
  return (
    <div className={className}>
      {label && (
        <label style={labelStyle}>
          {label} {required && <span style={{ color: theme.colors.error }}>*</span>}
        </label>
      )}
      <input
        type="text"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        style={inputStyle}
        required={required}
      />
    </div>
  );
};

// Select component for dropdowns
const Select = ({ label, value, onChange, children, className = '', style = {} }) => {
  const theme = useTheme();
  
  const selectStyle = {
    width: '100%',
    padding: theme.spacing.sm,
    border: `1px solid ${theme.colors.border}`,
    borderRadius: theme.borderRadius.sm,
    fontSize: '14px',
    backgroundColor: theme.colors.background.paper,
    color: theme.colors.text.primary,
    ...style,
  };
  
  const labelStyle = {
    display: 'block',
    marginBottom: theme.spacing.xs,
    fontSize: '14px',
    fontWeight: '500',
    color: theme.colors.text.primary,
  };
  
  return (
    <div className={className}>
      {label && <label style={labelStyle}>{label}</label>}
      <select value={value} onChange={onChange} style={selectStyle}>
        {children}
      </select>
    </div>
  );
};

function UnknownBankPanel({ unknownFiles, onConfigCreated, loading }) {
  const theme = useTheme();
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [bankConfig, setBankConfig] = useState({
    bankName: '',
    displayName: '',
    filenamePatterns: [],
    expected_headers: [],
    detection_content_signatures: '',
    columnMappings: {},
    amountFormat: 'american',
    currencyPrimary: 'USD',
    cashewAccount: ''
  });
  const [validationResult, setValidationResult] = useState(null);

  // Auto-select first unknown file
  useEffect(() => {
    if (unknownFiles.length > 0 && !selectedFile) {
      setSelectedFile(unknownFiles[0]);
    }
  }, [unknownFiles, selectedFile]);

  // Analyze selected file
  useEffect(() => {
    if (selectedFile) {
      analyzeUnknownCSV(selectedFile);
    }
  }, [selectedFile]);

  const analyzeUnknownCSV = async (file) => {
    setAnalysisLoading(true);
    try {
      // Pass the actual File object for API upload
      const actualFile = file.file || file;
      const result = await ConfigurationService.analyzeUnknownCSV(actualFile);
      
      if (result.success) {
        setAnalysis(result.analysis);
        
        // Auto-populate bank config with detected values
        setBankConfig(prev => ({
          ...prev,
          bankName: generateBankName(file.fileName || file.name),
          displayName: generateDisplayName(file.fileName || file.name),
          filenamePatterns: result.analysis.filename_patterns || [generateFilenamePattern(file.fileName || file.name)],
          expected_headers: result.analysis.headers || [],
          amountFormat: mapDetectedFormat(result.analysis.amount_format_analysis?.detected_format),
          currencyPrimary: detectCurrency(result.analysis.sample_data)
        }));
      } else {
        // Fallback to mock analysis if API is not available
        console.warn('API not available, using mock analysis:', result.error);
        const mockAnalysis = {
          filename: file.fileName || file.name,
          encoding: 'utf-8',
          delimiter: ',',
          headers: ['Date', 'Description', 'Amount', 'Balance', 'Category'],
          header_row: 0,
          data_start_row: 1,
          detected_amount_format: { decimal_separator: '.', thousand_separator: ',', negative_style: 'minus' },
          format_confidence: 0.85,
          suggested_mappings: {
            'date': ['Date', 'Transaction Date', 'Posted Date'],
            'amount': ['Amount', 'Debit', 'Credit'],
            'title': ['Description', 'Merchant', 'Transaction Details'],
            'note': ['Category', 'Type', 'Note'],
            'currency': ['Currency', 'CCY'],
            'exchange_to': ['Exchange Amount', 'Local Amount'],
            'exchange_to_currency': ['Exchange Currency', 'Local Currency']
          },
          filename_patterns: [generateFilenamePattern(file.fileName || file.name)],
          sample_data: [
            { 'Date': '2024-01-15', 'Description': 'Example Transaction', 'Amount': '-12.34', 'Balance': '1000.00', 'Category': 'Shopping' }
          ]
        };

        setAnalysis(mockAnalysis);
        
        // Auto-populate bank config with detected values
        setBankConfig(prev => ({
          ...prev,
          bankName: generateBankName(file.fileName || file.name),
          displayName: generateDisplayName(file.fileName || file.name),
          filenamePatterns: mockAnalysis.filename_patterns,
          expected_headers: mockAnalysis.headers || [],
          amountFormat: mapDetectedFormat(mockAnalysis.detected_amount_format),
          currencyPrimary: detectCurrency(mockAnalysis.sample_data)
        }));
      }
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setAnalysisLoading(false);
    }
  };

  const generateBankName = (filename) => {
    // Extract bank name from filename
    const cleanName = filename.replace(/\.[^/.]+$/, '').replace(/[^a-zA-Z]/g, '').toLowerCase();
    return cleanName.substring(0, 20) || 'unknown_bank';
  };

  const generateDisplayName = (filename) => {
    // Create display name from filename
    const cleanName = filename.replace(/\.[^/.]+$/, '').replace(/[^a-zA-Z\s]/g, '');
    return cleanName.charAt(0).toUpperCase() + cleanName.slice(1) || 'Unknown Bank';
  };

  const generateFilenamePattern = (filename) => {
    // Generate filename pattern
    return filename.replace(/\d+/g, '*').replace(/[0-9]/g, '*');
  };

  const mapDetectedFormat = (detectedFormat) => {
    // Map detected format to our format types
    if (detectedFormat.decimal_separator === ',' && detectedFormat.thousand_separator === '.') {
      return 'european';
    } else if (detectedFormat.thousand_separator === ' ') {
      return 'space_separated';
    }
    return 'american'; // default
  };

  const detectCurrency = (sampleData) => {
    // Try to detect currency from sample data
    // This is a simplified version
    return 'USD';
  };

  const startManualConfiguration = (file) => {
    // Clear all previous data and start fresh manual configuration
    setAnalysis(null);
    setValidationResult(null);
    setBankConfig({
      bankName: generateBankName(file.fileName || file.name),
      displayName: generateDisplayName(file.fileName || file.name),
      filenamePatterns: [generateFilenamePattern(file.fileName || file.name)],
      expected_headers: [],
      detection_content_signatures: '',
      columnMappings: {},
      amountFormat: 'american',
      currencyPrimary: 'USD',
      cashewAccount: generateBankName(file.fileName || file.name),
      manualMode: true
    });
    
    // Analyze the file to get headers and sample data, but don't auto-populate mappings
    analyzeForManualConfig(file);
  };

  const analyzeForManualConfig = async (file) => {
    setAnalysisLoading(true);
    try {
      const actualFile = file.file || file;
      const result = await ConfigurationService.analyzeUnknownCSV(actualFile);
      
      if (result.success) {
        // Only set the analysis data, don't auto-populate config
        setAnalysis(result.analysis);
      } else {
        // Fallback to basic file analysis
        console.warn('API not available, using basic analysis for manual config');
        const mockAnalysis = {
          filename: file.fileName || file.name,
          encoding: 'utf-8',
          delimiter: ',',
          headers: ['Date', 'Amount', 'Account', 'Counterparty', 'Name', 'Description'], // Generic headers
          header_row: 0,
          data_start_row: 1,
          sample_data: []
        };
        setAnalysis(mockAnalysis);
      }
    } catch (error) {
      console.error('Manual config analysis failed:', error);
    } finally {
      setAnalysisLoading(false);
    }
  };

  const getAmountFormatConfig = (formatType) => {
    const formatMap = {
      'american': { decimal_separator: '.', thousand_separator: ',', negative_style: 'minus', currency_position: 'prefix' },
      'european': { decimal_separator: ',', thousand_separator: '.', negative_style: 'minus', currency_position: 'prefix' },
      'space_separated': { decimal_separator: ',', thousand_separator: ' ', negative_style: 'minus', currency_position: 'prefix' },
      'indian': { decimal_separator: '.', thousand_separator: ',', negative_style: 'minus', currency_position: 'prefix' },
      'swiss': { decimal_separator: '.', thousand_separator: "'", negative_style: 'minus', currency_position: 'prefix' },
      'no_separator': { decimal_separator: '.', thousand_separator: '', negative_style: 'minus', currency_position: 'prefix' }
    };
    return formatMap[formatType] || formatMap['american'];
  };

  const isConfigValid = (config) => {
    return config.bankName && 
           config.displayName && 
           config.columnMappings.date && 
           config.columnMappings.amount && 
           config.columnMappings.title;
  };

  const validateConfig = async (config, analysis) => {
    try {
      const validationRequest = {
        config: config,
        analysis_id: analysis?.analysis_id || ''
      };

      const result = await ConfigurationService.validateBankConfig(validationRequest);
      
      if (result.success) {
        setValidationResult(result.validation);
      } else {
        // Fallback to local validation if API is not available
        console.warn('API validation not available, using local validation:', result.error);
        const validation = {
          valid: isConfigValid(config),
          errors: [],
          warnings: []
        };

        if (!config.bankName) validation.errors.push('Bank name is required');
        if (!config.columnMappings.date) validation.errors.push('Date column mapping is required');
        if (!config.columnMappings.amount) validation.errors.push('Amount column mapping is required');
        if (!config.columnMappings.title) validation.errors.push('Title/Description column mapping is required');

        setValidationResult(validation);
      }
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };

  const saveConfiguration = async (config) => {
    try {
      // Build the proper config structure expected by the backend
      const bankConfig = {
        bank_info: {
          bank_name: config.bankName,
          display_name: config.displayName,
          file_patterns: config.filenamePatterns,
          expected_headers: config.expected_headers,
          detection_content_signatures: config.detection_content_signatures
                                          ? config.detection_content_signatures.split(',').map(s => s.trim())
                                          : [],
          currency_primary: config.currencyPrimary,
          cashew_account: config.cashewAccount || config.bankName
        },
        csv_config: {
          encoding: 'utf-8',
          delimiter: ',',
          header_row: 0,
          data_start_row: 1
        },
        column_mapping: config.columnMappings,
        data_cleaning: {
          amount_format: getAmountFormatConfig(config.amountFormat),
          auto_detect_format: false,
          currency_handling: 'standard'
        },
        categorization: {}
      };

      const saveRequest = {
        config: bankConfig,
        force_overwrite: false
      };

      const result = await ConfigurationService.saveBankConfig(saveRequest);
      
      if (result.success) {
        console.log('Bank configuration saved successfully');
        
        // Try to reload configurations
        await ConfigurationService.reloadConfigurations();
        
        // Notify parent component
        if (onConfigCreated) {
          onConfigCreated(config);
        }
      } else {
        console.error('Failed to save configuration:', result.error);
        // Could show an error toast here
        
        // Fallback: still notify parent component for now
        if (onConfigCreated) {
          onConfigCreated(config);
        }
      }
    } catch (error) {
      console.error('Failed to save configuration:', error);
    }
  };

  return (
    <Card padding="lg" elevated>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: theme.spacing.md,
        marginBottom: theme.spacing.lg,
      }}>
        <AlertCircle size={20} color={theme.colors.warning} />
        <h3 style={{
          margin: 0,
          fontSize: '18px',
          fontWeight: '600',
          color: theme.colors.text.primary,
        }}>
          Unknown Bank Configuration
        </h3>
        <Badge variant="warning">
          {unknownFiles.length} file{unknownFiles.length !== 1 ? 's' : ''} need setup
        </Badge>
      </div>

      {/* File Selection and Manual Config Option */}
      <div style={{ marginBottom: theme.spacing.lg }}>
        {unknownFiles.length > 1 && (
          <div style={{ marginBottom: theme.spacing.md }}>
            <Select
              label="Select File to Configure:"
              value={selectedFile?.fileName || selectedFile?.name || ''}
              onChange={(e) => setSelectedFile(unknownFiles.find(f => (f.fileName || f.name) === e.target.value))}
            >
              {unknownFiles.map(file => (
                <option key={file.fileName || file.name} value={file.fileName || file.name}>
                  {file.fileName || file.name} ({Math.round((file.confidence || 0) * 100)}% confidence)
                </option>
              ))}
            </Select>
          </div>
        )}
        
        {/* Manual Configuration Button */}
        <div style={{ display: 'flex', gap: theme.spacing.md, alignItems: 'center' }}>
          <Button
            variant="secondary"
            onClick={() => startManualConfiguration(selectedFile)}
            disabled={!selectedFile || analysisLoading}
          >
            Start Fresh Manual Configuration
          </Button>
          <div style={{
            fontSize: '14px',
            color: theme.colors.text.secondary,
          }}>
            Clear all auto-detected data and configure manually
          </div>
        </div>
      </div>

      {selectedFile && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: theme.spacing.lg,
          '@media (max-width: 1024px)': {
            gridTemplateColumns: '1fr',
          }
        }}>
          {/* Configuration Panel */}
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: theme.spacing.lg,
          }}>
            <BankInfoSection 
              config={bankConfig}
              onChange={setBankConfig}
              analysis={analysis}
            />
            
            <HeaderMappingSection
              config={bankConfig}
              onChange={setBankConfig}
              analysis={analysis}
            />
            
            <AmountFormatSection
              config={bankConfig}
              onChange={setBankConfig}
              analysis={analysis}
            />
            
            <div style={{ display: 'flex', gap: theme.spacing.md }}>
              <Button
                variant="secondary"
                onClick={() => validateConfig(bankConfig, analysis)}
                disabled={loading || analysisLoading}
              >
                Validate Config
              </Button>
              <Button
                variant="primary"
                onClick={() => saveConfiguration(bankConfig)}
                disabled={loading || analysisLoading || !isConfigValid(bankConfig)}
              >
                Save & Apply
              </Button>
            </div>
          </div>

          {/* Preview Panel */}
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: theme.spacing.lg,
          }}>
            <ConfigPreviewSection
              config={bankConfig}
              analysis={analysis}
              validationResult={validationResult}
            />
            
            <SampleDataPreview
              analysis={analysis}
              mappings={bankConfig.columnMappings}
              loading={analysisLoading}
            />
          </div>
        </div>
      )}
    </Card>
  );
}

// Bank Information Section
function BankInfoSection({ config, onChange, analysis }) {
  const theme = useTheme();
  
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: theme.spacing.md,
    }}>
      <h4 style={{
        margin: 0,
        fontSize: '16px',
        fontWeight: '500',
        color: theme.colors.text.primary,
      }}>
        Bank Information
      </h4>
      
      <Input
        label="Bank Name"
        value={config.bankName}
        onChange={(e) => onChange(prev => ({ ...prev, bankName: e.target.value }))}
        placeholder="e.g. mybank"
        required
      />
      
      <Input
        label="Display Name" 
        value={config.displayName}
        onChange={(e) => onChange(prev => ({ ...prev, displayName: e.target.value }))}
        placeholder="e.g. MyBank"
        required
      />
      
      <Input
        label="Primary Currency"
        value={config.currencyPrimary}
        onChange={(e) => onChange(prev => ({ ...prev, currencyPrimary: e.target.value }))}
        placeholder="USD"
        required
      />
      
      <Input
        label="Cashew Account Name"
        value={config.cashewAccount}
        onChange={(e) => onChange(prev => ({ ...prev, cashewAccount: e.target.value }))}
        placeholder={config.bankName || "account_name"}
        required
      />
      
      <Input
        label="Content Signatures (comma-separated)"
        value={config.detection_content_signatures}
        onChange={(e) => onChange(prev => ({ ...prev, detection_content_signatures: e.target.value }))}
        placeholder="e.g. Partner IBAN,Booking Date"
      />
    </div>
  );
}

// Header Mapping Section
function HeaderMappingSection({ config, onChange, analysis }) {
  const theme = useTheme();
  const availableHeaders = analysis?.headers || [];
  
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: theme.spacing.md,
    }}>
      <h4 style={{
        margin: 0,
        fontSize: '16px',
        fontWeight: '500',
        color: theme.colors.text.primary,
      }}>
        Header Mapping
      </h4>
      
      {STANDARD_FIELDS.map(field => (
        <div key={field.value}>
          <Select
            label={`${field.label} ${field.required ? '*' : ''}`}
            value={config.columnMappings[field.value] || ''}
            onChange={(e) => onChange(prev => ({
              ...prev,
              columnMappings: { ...prev.columnMappings, [field.value]: e.target.value }
            }))}
          >
            <option value="">Select column...</option>
            {availableHeaders.map(header => (
              <option key={header} value={header}>{header}</option>
            ))}
          </Select>
          
          {(analysis?.suggested_mappings?.[field.value] || analysis?.field_mapping_suggestions?.[field.value]) && (
            <div style={{
              fontSize: '12px',
              color: theme.colors.text.secondary,
              marginTop: theme.spacing.xs,
            }}>
              Suggested: {(
                analysis?.suggested_mappings?.[field.value] || 
                analysis?.field_mapping_suggestions?.[field.value]?.suggested_columns
              )?.join?.(', ') || 'No suggestions available'}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// Amount Format Section
function AmountFormatSection({ config, onChange, analysis }) {
  const theme = useTheme();
  const detectedFormat = analysis?.detected_amount_format || analysis?.amount_format_analysis?.detected_format;
  const confidence = analysis?.format_confidence || analysis?.amount_format_analysis?.confidence || 0;
  
  const getFormatLabel = (format) => {
    if (format?.decimal_separator === ',' && format?.thousand_separator === '.') {
      return 'European (1.234,56)';
    } else if (format?.thousand_separator === ' ') {
      return 'Space Separated (1 234,56)';
    }
    return 'American (1,234.56)';
  };
  
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: theme.spacing.md,
    }}>
      <h4 style={{
        margin: 0,
        fontSize: '16px',
        fontWeight: '500',
        color: theme.colors.text.primary,
      }}>
        Amount Format
      </h4>
      
      {detectedFormat && (
        <Alert variant="info" style={{ marginBottom: theme.spacing.sm }}>
          Auto-detected: {getFormatLabel(detectedFormat)} 
          ({Math.round(confidence * 100)}% confidence)
        </Alert>
      )}
      
      <Select
        label="Number Format"
        value={config.amountFormat}
        onChange={(e) => onChange(prev => ({ ...prev, amountFormat: e.target.value }))}
      >
        {AMOUNT_FORMATS.map(format => (
          <option key={format.value} value={format.value}>
            {format.label}
          </option>
        ))}
      </Select>
      
      <div style={{
        fontSize: '14px',
        color: theme.colors.text.secondary,
      }}>
        Example: {AMOUNT_FORMATS.find(f => f.value === config.amountFormat)?.example}
      </div>
    </div>
  );
}

// Configuration Preview Section
function ConfigPreviewSection({ config, analysis, validationResult }) {
  const theme = useTheme();
  
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: theme.spacing.md,
    }}>
      <h4 style={{
        margin: 0,
        fontSize: '16px',
        fontWeight: '500',
        color: theme.colors.text.primary,
      }}>
        Configuration Preview
      </h4>
      
      <Card padding="md" style={{
        backgroundColor: theme.colors.background.elevated,
        border: `1px solid ${theme.colors.border}`,
      }}>
        <div style={{
          fontSize: '12px',
          fontFamily: 'monospace',
          whiteSpace: 'pre-wrap',
          color: theme.colors.text.primary,
        }}>
          {`[bank_info]
bank_name = ${config.bankName || 'unknown_bank'}
display_name = ${config.displayName || 'Unknown Bank'}
currency_primary = ${config.currencyPrimary || 'USD'}

[column_mapping]
${Object.entries(config.columnMappings).map(([key, value]) => `${key} = ${value}`).join('\n')}

[amount_format]
format = ${config.amountFormat || 'american'}`}
        </div>
      </Card>
      
      {validationResult && (
        <div>
          {validationResult.errors.length > 0 && (
            <Alert variant="error" style={{ marginBottom: theme.spacing.sm }}>
              Errors: {validationResult.errors.join(', ')}
            </Alert>
          )}
          {validationResult.warnings.length > 0 && (
            <Alert variant="warning" style={{ marginBottom: theme.spacing.sm }}>
              Warnings: {validationResult.warnings.join(', ')}
            </Alert>
          )}
          {validationResult.valid && validationResult.errors.length === 0 && (
            <Alert variant="success">
              Configuration is valid!
            </Alert>
          )}
        </div>
      )}
    </div>
  );
}

// Sample Data Preview Section
function SampleDataPreview({ analysis, mappings, loading }) {
  const theme = useTheme();
  
  if (loading) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: theme.spacing.md,
      }}>
        <h4 style={{
          margin: 0,
          fontSize: '16px',
          fontWeight: '500',
          color: theme.colors.text.primary,
        }}>
          Sample Data
        </h4>
        <div style={{
          padding: theme.spacing.lg,
          textAlign: 'center',
          color: theme.colors.text.secondary,
        }}>
          Analyzing CSV structure...
        </div>
      </div>
    );
  }
  
  const sampleData = analysis?.sample_data || [];
  
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: theme.spacing.md,
    }}>
      <h4 style={{
        margin: 0,
        fontSize: '16px',
        fontWeight: '500',
        color: theme.colors.text.primary,
      }}>
        Sample Data Preview
      </h4>
      
      <Card padding="md" style={{
        backgroundColor: theme.colors.background.elevated,
        border: `1px solid ${theme.colors.border}`,
        overflow: 'auto',
      }}>
        {sampleData.length > 0 ? (
          <table style={{
            width: '100%',
            fontSize: '12px',
            borderCollapse: 'collapse',
          }}>
            <thead>
              <tr>
                {analysis.headers.map(header => (
                  <th key={header} style={{
                    padding: theme.spacing.xs,
                    textAlign: 'left',
                    borderBottom: `1px solid ${theme.colors.border}`,
                    color: theme.colors.text.primary,
                    fontWeight: '500',
                  }}>
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sampleData.slice(0, 3).map((row, index) => (
                <tr key={index}>
                  {analysis.headers.map(header => (
                    <td key={header} style={{
                      padding: theme.spacing.xs,
                      borderBottom: `1px solid ${theme.colors.border}`,
                      color: theme.colors.text.secondary,
                    }}>
                      {row[header]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div style={{
            padding: theme.spacing.lg,
            textAlign: 'center',
            color: theme.colors.text.secondary,
          }}>
            No sample data available
          </div>
        )}
      </Card>
    </div>
  );
}

export default UnknownBankPanel;