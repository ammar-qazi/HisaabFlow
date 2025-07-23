import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from '../ui/CoreIcons';
import { ConfigurationService } from '../../services/configurationService';
import { useTheme } from '../../theme/ThemeProvider';

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

function UnknownBankPanel({ unknownFiles, onConfigCreated, loading }) {
  const theme = useTheme();
  const [currentPage, setCurrentPage] = useState(1);
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
      const actualFile = file.file || file;
      const result = await ConfigurationService.analyzeUnknownCSV(actualFile);

      if (result.success) {
        setAnalysis(result.analysis);
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
    const cleanName = filename.replace(/\.[^/.]+$/, '').replace(/[^a-zA-Z]/g, '').toLowerCase();
    return cleanName.substring(0, 20) || 'unknown_bank';
  };

  const generateDisplayName = (filename) => {
    const cleanName = filename.replace(/\.[^/.]+$/, '').replace(/[^a-zA-Z\s]/g, '');
    return cleanName.charAt(0).toUpperCase() + cleanName.slice(1) || 'Unknown Bank';
  };

  const generateFilenamePattern = (filename) => {
    return filename.replace(/\d+/g, '*').replace(/[0-9]/g, '*');
  };

  const mapDetectedFormat = (detectedFormat) => {
    if (detectedFormat?.decimal_separator === ',' && detectedFormat?.thousand_separator === '.') {
      return 'european';
    } else if (detectedFormat?.thousand_separator === ' ') {
      return 'space_separated';
    }
    return 'american';
  };

  const detectCurrency = (sampleData) => {
    return 'USD';
  };

  const startManualConfiguration = (file) => {
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
    analyzeForManualConfig(file);
  };

  const analyzeForManualConfig = async (file) => {
    setAnalysisLoading(true);
    try {
      const actualFile = file.file || file;
      const result = await ConfigurationService.analyzeUnknownCSV(actualFile);

      if (result.success) {
        setAnalysis(result.analysis);
      } else {
        console.warn('API not available, using basic analysis for manual config');
        const mockAnalysis = {
          filename: file.fileName || file.name,
          encoding: 'utf-8',
          delimiter: ',',
          headers: ['Date', 'Amount', 'Account', 'Counterparty', 'Name', 'Description'],
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
        await ConfigurationService.reloadConfigurations();
        if (onConfigCreated) {
          onConfigCreated(config);
        }
      } else {
        console.error('Failed to save configuration:', result.error);
        if (onConfigCreated) {
          onConfigCreated(config);
        }
      }
    } catch (error) {
      console.error('Failed to save configuration:', error);
    }
  };

  // Get sample data for preview with pagination
  const sampleData = analysis?.sample_data || [];
  const totalPages = Math.ceil(sampleData.length / 5);
  const startIndex = (currentPage - 1) * 5;
  const currentData = sampleData.slice(startIndex, startIndex + 5);

  // Header options for mapping dropdowns
  const headerOptions = ['Select column...', ...(analysis?.headers || [])];

  // Mapping fields for the form
  const mappingFields = STANDARD_FIELDS;

  // Common input style
  const inputStyle = {
    width: '100%',
    backgroundColor: theme.colors.background.elevated,
    border: `1px solid ${theme.colors.border}`,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.sm,
    color: theme.colors.text.primary,
    fontSize: '14px'
  };

  const labelStyle = {
    display: 'block',
    fontSize: '14px',
    fontWeight: '500',
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.sm
  };

  return (
    <div style={{
      backgroundColor: theme.colors.background.paper,
      color: theme.colors.text.primary,
      borderRadius: theme.borderRadius.md,
      overflow: 'hidden',
      border: `1px solid ${theme.colors.border}`
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: theme.spacing.lg,
        borderBottom: `1px solid ${theme.colors.border}`
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.md }}>
          <button style={{
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing.sm,
            color: theme.colors.text.secondary,
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            transition: 'color 0.2s'
          }}>
            <ChevronLeft size={20} />
            Go Back
          </button>
          <div style={{ height: '24px', width: '1px', backgroundColor: theme.colors.border }}></div>
          <h1 style={{ fontSize: '20px', fontWeight: '600', margin: 0, color: theme.colors.text.primary }}>Configure Unknown Bank</h1>
        </div>
        <div style={{ fontSize: '14px', color: theme.colors.text.secondary }}>
          Bank 1 of {unknownFiles.length} • Processing: {selectedFile?.fileName || selectedFile?.name || 'No file selected'}
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: theme.spacing.lg }}>
        {/* File Selection */}
        <div style={{ marginBottom: theme.spacing.xl }}>
          <label style={labelStyle}>
            Select File to Configure
          </label>
          <select
            value={selectedFile?.fileName || selectedFile?.name || ''}
            onChange={(e) => setSelectedFile(unknownFiles.find(f => (f.fileName || f.name) === e.target.value))}
            style={inputStyle}
          >
            {unknownFiles.map(file => (
              <option key={file.fileName || file.name} value={file.fileName || file.name}>
                {file.fileName || file.name} ({Math.round((file.confidence || 0) * 100)}% confidence)
              </option>
            ))}
          </select>
        </div>

        {/* Bank Information */}
        <div style={{ marginBottom: theme.spacing.xl }}>
          <h2 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: theme.colors.primary,
            marginBottom: theme.spacing.md
          }}>
            Bank Information
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: theme.spacing.md,
            marginBottom: theme.spacing.md
          }}>
            <div>
              <label style={labelStyle}>
                Bank Name <span style={{ color: theme.colors.error }}>*</span>
              </label>
              <input
                type="text"
                value={bankConfig.bankName}
                onChange={(e) => setBankConfig(prev => ({ ...prev, bankName: e.target.value }))}
                style={inputStyle}
              />
            </div>
            <div>
              <label style={labelStyle}>
                Display Name <span style={{ color: theme.colors.error }}>*</span>
              </label>
              <input
                type="text"
                value={bankConfig.displayName}
                onChange={(e) => setBankConfig(prev => ({ ...prev, displayName: e.target.value }))}
                style={inputStyle}
              />
            </div>
            <div>
              <label style={labelStyle}>
                Primary Currency <span style={{ color: theme.colors.error }}>*</span>
              </label>
              <input
                type="text"
                value={bankConfig.currencyPrimary}
                onChange={(e) => setBankConfig(prev => ({ ...prev, currencyPrimary: e.target.value }))}
                style={inputStyle}
              />
            </div>
            <div>
              <label style={labelStyle}>
                Cashew Account Name <span style={{ color: theme.colors.error }}>*</span>
              </label>
              <input
                type="text"
                value={bankConfig.cashewAccount}
                onChange={(e) => setBankConfig(prev => ({ ...prev, cashewAccount: e.target.value }))}
                style={inputStyle}
              />
            </div>
          </div>
          <div>
            <label style={labelStyle}>
              Content Signatures (comma-separated)
            </label>
            <input
              type="text"
              value={bankConfig.detection_content_signatures}
              onChange={(e) => setBankConfig(prev => ({ ...prev, detection_content_signatures: e.target.value }))}
              placeholder="e.g. Partner IBAN,Booking Date"
              style={inputStyle}
            />
          </div>
        </div>

        {/* Sample Data Preview */}
        {analysis && (
          <div style={{ marginBottom: theme.spacing.xl }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: theme.colors.primary,
              marginBottom: theme.spacing.md
            }}>
              Sample Data Preview
            </h2>
            <div style={{
              backgroundColor: theme.colors.background.elevated,
              borderRadius: theme.borderRadius.md,
              border: `1px solid ${theme.colors.border}`,
              overflow: 'hidden'
            }}>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: `1px solid ${theme.colors.border}` }}>
                      {analysis.headers?.map(header => (
                        <th key={header} style={{
                          textAlign: 'left',
                          padding: theme.spacing.sm,
                          fontSize: '14px',
                          fontWeight: '500',
                          color: theme.colors.text.primary
                        }}>
                          {header}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {currentData.map((row, index) => (
                      <tr key={index} style={{
                        backgroundColor: index % 2 === 0 ? theme.colors.background.elevated : theme.colors.background.paper
                      }}>
                        {analysis.headers?.map(header => (
                          <td key={header} style={{
                            padding: theme.spacing.sm,
                            fontSize: '14px',
                            color: theme.colors.text.secondary
                          }}>
                            {String(row[header] || '')}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: theme.spacing.sm,
                  borderTop: `1px solid ${theme.colors.border}`
                }}>
                  <div style={{ fontSize: '14px', color: theme.colors.text.secondary }}>
                    Showing {startIndex + 1} to {Math.min(startIndex + 5, sampleData.length)} of {sampleData.length} rows
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.sm }}>
                    <button
                      onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                      disabled={currentPage === 1}
                      style={{
                        padding: '4px',
                        borderRadius: theme.borderRadius.sm,
                        border: `1px solid ${theme.colors.border}`,
                        backgroundColor: 'transparent',
                        color: theme.colors.text.primary,
                        cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                        opacity: currentPage === 1 ? 0.5 : 1
                      }}
                    >
                      <ChevronLeft size={16} />
                    </button>
                    <span style={{ fontSize: '14px', color: theme.colors.text.primary }}>
                      {currentPage} of {totalPages}
                    </span>
                    <button
                      onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                      disabled={currentPage === totalPages}
                      style={{
                        padding: '4px',
                        borderRadius: theme.borderRadius.sm,
                        border: `1px solid ${theme.colors.border}`,
                        backgroundColor: 'transparent',
                        color: theme.colors.text.primary,
                        cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
                        opacity: currentPage === totalPages ? 0.5 : 1
                      }}
                    >
                      <ChevronRight size={16} />
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Header Mapping */}
        <div style={{ marginBottom: theme.spacing.xl }}>
          <h2 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: theme.colors.primary,
            marginBottom: theme.spacing.md
          }}>
            Header Mapping
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: theme.spacing.md
          }}>
            {mappingFields.map((field, index) => (
              <div key={index}>
                <label style={labelStyle}>
                  {field.label} {field.required && <span style={{ color: theme.colors.error }}>*</span>}
                </label>
                <select
                  value={bankConfig.columnMappings[field.value] || ''}
                  onChange={(e) => setBankConfig(prev => ({
                    ...prev,
                    columnMappings: { ...prev.columnMappings, [field.value]: e.target.value }
                  }))}
                  style={inputStyle}
                >
                  {headerOptions.map((option, optIndex) => (
                    <option key={optIndex} value={option === 'Select column...' ? '' : option}>
                      {option}
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>
        </div>

        {/* Configuration Preview */}
        <div style={{ marginBottom: theme.spacing.xl }}>
          <h2 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: theme.colors.primary,
            marginBottom: theme.spacing.md
          }}>
            Configuration Preview
          </h2>
          <div style={{
            backgroundColor: theme.colors.background.elevated,
            borderRadius: theme.borderRadius.md,
            border: `1px solid ${theme.colors.border}`,
            padding: theme.spacing.md
          }}>
            <pre style={{
              fontSize: '14px',
              color: theme.colors.text.primary,
              fontFamily: 'monospace',
              lineHeight: '1.5',
              margin: 0
            }}>
              <div style={{ color: theme.colors.primary, marginBottom: theme.spacing.sm }}>[bank_info]</div>
              <div>bank_name = {bankConfig.bankName || 'unknown_bank'}</div>
              <div>display_name = {bankConfig.displayName || 'Unknown Bank'}</div>
              <div>currency_primary = {bankConfig.currencyPrimary || 'USD'}</div>

              <div style={{ color: theme.colors.primary, marginTop: theme.spacing.md, marginBottom: theme.spacing.sm }}>[column_mapping]</div>
              {Object.entries(bankConfig.columnMappings).map(([key, value]) => (
                <div key={key}>{key} = {value}</div>
              ))}

              <div style={{ color: theme.colors.primary, marginTop: theme.spacing.md, marginBottom: theme.spacing.sm }}>[amount_format]</div>
              <div>format = {bankConfig.amountFormat || 'american'}</div>
            </pre>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          paddingTop: theme.spacing.lg,
          borderTop: `1px solid ${theme.colors.border}`
        }}>
          <button
            onClick={() => startManualConfiguration(selectedFile)}
            disabled={!selectedFile || analysisLoading}
            style={{
              padding: `${theme.spacing.sm} ${theme.spacing.md}`,
              color: theme.colors.text.secondary,
              backgroundColor: 'transparent',
              border: 'none',
              cursor: (!selectedFile || analysisLoading) ? 'not-allowed' : 'pointer',
              opacity: (!selectedFile || analysisLoading) ? 0.5 : 1,
              transition: 'color 0.2s'
            }}
          >
            Start Fresh Manual Configuration
          </button>
          <button
            onClick={() => saveConfiguration(bankConfig)}
            disabled={loading || analysisLoading || !isConfigValid(bankConfig)}
            style={{
              padding: `${theme.spacing.sm} ${theme.spacing.lg}`,
              backgroundColor: theme.colors.primary,
              color: 'white',
              border: 'none',
              borderRadius: theme.borderRadius.md,
              fontWeight: '500',
              cursor: (loading || analysisLoading || !isConfigValid(bankConfig)) ? 'not-allowed' : 'pointer',
              opacity: (loading || analysisLoading || !isConfigValid(bankConfig)) ? 0.5 : 1,
              transition: 'background-color 0.2s'
            }}
          >
            Save Configuration
          </button>
        </div>
      </div>
    </div>
  );
}

export default UnknownBankPanel;