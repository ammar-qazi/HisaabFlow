import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from '../ui/CoreIcons';
import { ConfigurationService } from '../../services/configurationService';
import { useTheme } from '../../theme/ThemeProvider';
import InteractiveDataTable from '../transform-export/InteractiveDataTable';

const STANDARD_FIELDS = [
  { value: 'date', label: 'Date', required: true },
  { value: 'amount', label: 'Amount', required: true, columnType: 'amount' },
  { value: 'debit', label: 'Debit', required: false, columnType: 'debit_credit' },
  { value: 'credit', label: 'Credit', required: false, columnType: 'debit_credit' },
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
    currencyPrimary: '',
    cashewAccount: '',
    headerRow: 1,  // 1-based indexing for user display
    columnType: 'amount',  // 'amount' or 'debit_credit'
    dateFormat: '',  // Custom date format pattern
    isMultiCurrency: false,  // Toggle for multi-currency support
    accountMappings: {}  // For multi-currency: currency -> account name
  });
  const [validationResult, setValidationResult] = useState(null);

  // Effect to select a file when the list changes or a file is removed
  useEffect(() => {
    if (unknownFiles.length > 0) {
      const isSelectedFileStillInList = selectedFile && unknownFiles.some(f => (f.fileName || f.name) === (selectedFile.fileName || selectedFile.name));
      if (!isSelectedFileStillInList) {
        setSelectedFile(unknownFiles[0]);
      }
    } else {
      setSelectedFile(null);
    }
  }, [unknownFiles]);

  // Effect to analyze the selected file and reset state
  useEffect(() => {
    if (selectedFile) {
      // Reset state before analyzing a new file
      setAnalysis(null);
      setBankConfig({
        bankName: '',
        displayName: '',
        filenamePatterns: [],
        expected_headers: [],
        detection_content_signatures: '',
        columnMappings: {},
        amountFormat: 'american',
        currencyPrimary: '',
        cashewAccount: '',
        headerRow: 1,
        columnType: 'amount',
        dateFormat: '',
        isMultiCurrency: false,
        accountMappings: {}
      });
      setValidationResult(null);
      analyzeUnknownCSV(selectedFile);
    } else {
      // Clear state if no file is selected
      setAnalysis(null);
      setBankConfig({
        bankName: '',
        displayName: '',
        filenamePatterns: [],
        expected_headers: [],
        detection_content_signatures: '',
        columnMappings: {},
        amountFormat: 'american',
        currencyPrimary: '',
        cashewAccount: '',
        headerRow: 1,
        columnType: 'amount',
        dateFormat: '',
        isMultiCurrency: false,
        accountMappings: {}
      });
      setValidationResult(null);
    }
  }, [selectedFile]);

  const analyzeUnknownCSV = async (file, headerRow = null) => {
    setAnalysisLoading(true);
    try {
      const actualFile = file.file || file;
      const result = await ConfigurationService.analyzeUnknownCSV(actualFile, headerRow);

      if (result.success) {
        console.log('DEBUG: Frontend - Analysis result received:', result.analysis);
        console.log('DEBUG: Frontend - Analysis encoding:', result.analysis?.encoding);
        console.log('DEBUG: Frontend - Sample data being set:', result.analysis?.sample_data);
        console.log('DEBUG: Frontend - Headers received:', result.analysis?.headers);
        console.log('DEBUG: Frontend - Auto-detected header row:', result.analysis?.header_row);
        setAnalysis(result.analysis);
        setBankConfig(prev => ({
          ...prev,
          bankName: generateBankName(file.fileName || file.name),
          displayName: generateDisplayName(file.fileName || file.name),
          filenamePatterns: result.analysis.filename_patterns || [generateFilenamePattern(file.fileName || file.name)],
          expected_headers: result.analysis.headers || [],
          amountFormat: mapDetectedFormat(result.analysis.amount_format_analysis?.detected_format),
          currencyPrimary: detectCurrency(result.analysis.sample_data),
          headerRow: headerRow || result.analysis.header_row || prev.headerRow,  // Use manual override, then auto-detected, then previous value
          columnType: detectColumnType(result.analysis.headers || []),
          dateFormat: result.analysis?.date_format_detection?.detected_format || ''
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

  const detectColumnType = (headers) => {
    const lowercaseHeaders = headers.map(h => h.toLowerCase());
    const hasDebit = lowercaseHeaders.some(h => h.includes('debit'));
    const hasCredit = lowercaseHeaders.some(h => h.includes('credit'));

    // If both debit and credit columns exist, suggest debit_credit mode
    if (hasDebit && hasCredit) {
      return 'debit_credit';
    }

    // Default to amount mode
    return 'amount';
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
      amountFormat: '',
      currencyPrimary: '',
      cashewAccount: '',
      columnType: 'amount',
      dateFormat: '',
      isMultiCurrency: false,
      accountMappings: {},
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
    const hasBasicFields = config.bankName &&
      config.displayName &&
      config.columnMappings.date &&
      config.columnMappings.title;

    // Check amount fields based on column type
    let hasAmountFields = false;
    if (config.columnType === 'amount') {
      hasAmountFields = config.columnMappings.amount;
    } else if (config.columnType === 'debit_credit') {
      // For debit/credit, at least one of them should be mapped
      hasAmountFields = config.columnMappings.debit || config.columnMappings.credit;
    }

    // Check account configuration based on multi-currency setting
    let hasValidAccountConfig = false;
    if (config.isMultiCurrency) {
      // For multi-currency, need at least one valid currency->account mapping
      const validMappings = Object.entries(config.accountMappings).filter(([currency, account]) =>
        currency && currency.trim() && account && account.trim()
      );
      hasValidAccountConfig = validMappings.length > 0;
    } else {
      // For single currency, need cashew account
      hasValidAccountConfig = config.cashewAccount && config.cashewAccount.trim();
    }

    return hasBasicFields && hasAmountFields && hasValidAccountConfig;
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
        if (!config.columnMappings.title) validation.errors.push('Title/Description column mapping is required');

        // Validate amount fields based on column type
        if (config.columnType === 'amount') {
          if (!config.columnMappings.amount) validation.errors.push('Amount column mapping is required');
        } else if (config.columnType === 'debit_credit') {
          if (!config.columnMappings.debit && !config.columnMappings.credit) {
            validation.errors.push('At least one of Debit or Credit column mapping is required');
          }
        }

        setValidationResult(validation);
      }
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };

  const saveConfiguration = async (config) => {
    try {
      console.log('DEBUG: Frontend - saveConfiguration - analysis:', analysis);
      console.log('DEBUG: Frontend - saveConfiguration - analysis.encoding:', analysis?.encoding);
      const finalEncoding = analysis?.encoding || 'utf-8';
      console.log('DEBUG: Frontend - saveConfiguration - finalEncoding being used:', finalEncoding);
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
          encoding: finalEncoding,
          delimiter: ',',
          header_row: config.headerRow,  // Use the configured header row (1-based)
          has_header: true,
          skip_rows: 0,
          date_format: config.dateFormat || null
        },
        column_mapping: config.columnMappings,
        data_cleaning: {
          amount_format: getAmountFormatConfig(config.amountFormat),
          auto_detect_format: false,
          currency_handling: config.isMultiCurrency ? 'multi_currency' : 'standard'
        },
        // Add account_mapping section for multi-currency support
        ...(config.isMultiCurrency && Object.keys(config.accountMappings).length > 0 && {
          account_mapping: config.accountMappings
        }),
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

  // Mapping fields for the form - filter based on column type
  const mappingFields = STANDARD_FIELDS.filter(field => {
    if (field.columnType === 'amount' && bankConfig.columnType !== 'amount') {
      return false;
    }
    if (field.columnType === 'debit_credit' && bankConfig.columnType !== 'debit_credit') {
      return false;
    }
    return true;
  });

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
            {!bankConfig.isMultiCurrency && (
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
            )}
            {!bankConfig.isMultiCurrency && (
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
            )}
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

          {/* Header Row Configuration */}
          <div style={{ marginTop: theme.spacing.md }}>
            <label style={labelStyle}>
              Header Row <span style={{ color: theme.colors.error }}>*</span>
            </label>
            <div style={{ display: 'flex', gap: theme.spacing.sm, alignItems: 'center' }}>
              <input
                type="number"
                min="1"
                value={bankConfig.headerRow}
                onChange={(e) => setBankConfig(prev => ({ ...prev, headerRow: parseInt(e.target.value) || 1 }))}
                style={{ ...inputStyle, flex: 1 }}
              />
              <button
                onClick={() => analyzeUnknownCSV(selectedFile, bankConfig.headerRow)}
                disabled={!selectedFile || analysisLoading}
                style={{
                  padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
                  backgroundColor: theme.colors.primary,
                  color: 'white',
                  border: 'none',
                  borderRadius: theme.borderRadius.md,
                  cursor: (!selectedFile || analysisLoading) ? 'not-allowed' : 'pointer',
                  opacity: (!selectedFile || analysisLoading) ? 0.5 : 1,
                  fontSize: '12px',
                  whiteSpace: 'nowrap'
                }}
              >
                {analysisLoading ? 'Analyzing...' : 'Re-analyze'}
              </button>
            </div>
            <div style={{
              fontSize: '12px',
              color: theme.colors.text.secondary,
              marginTop: theme.spacing.xs
            }}>
              Row number where column headers are located (e.g., for NayaPay use row 13). Click "Re-analyze" to update the preview.
            </div>
          </div>

          {/* Column Type Selection */}
          <div style={{ marginTop: theme.spacing.md }}>
            <label style={labelStyle}>
              Amount Column Type <span style={{ color: theme.colors.error }}>*</span>
            </label>
            <div style={{ display: 'flex', gap: theme.spacing.md, marginBottom: theme.spacing.sm }}>
              <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="columnType"
                  value="amount"
                  checked={bankConfig.columnType === 'amount'}
                  onChange={(e) => setBankConfig(prev => ({ ...prev, columnType: e.target.value }))}
                  style={{ marginRight: theme.spacing.xs }}
                />
                Single Amount Column
              </label>
              <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="columnType"
                  value="debit_credit"
                  checked={bankConfig.columnType === 'debit_credit'}
                  onChange={(e) => setBankConfig(prev => ({ ...prev, columnType: e.target.value }))}
                  style={{ marginRight: theme.spacing.xs }}
                />
                Separate Debit/Credit Columns
              </label>
            </div>
            <div style={{
              fontSize: '12px',
              color: theme.colors.text.secondary,
              marginTop: theme.spacing.xs
            }}>
              {bankConfig.columnType === 'amount'
                ? 'Use when the CSV has one column for amounts (positive/negative values)'
                : 'Use when the CSV has separate columns for debits and credits'
              }
            </div>
          </div>

          {/* Amount Format Selection */}
          <div style={{ marginTop: theme.spacing.md }}>
            <label style={labelStyle}>
              Amount Format <span style={{ color: theme.colors.error }}>*</span>
            </label>
            <select
              value={bankConfig.amountFormat}
              onChange={(e) => setBankConfig(prev => ({ ...prev, amountFormat: e.target.value }))}
              style={inputStyle}
            >
              {AMOUNT_FORMATS.map((format) => (
                <option key={format.value} value={format.value}>
                  {format.label}
                </option>
              ))}
            </select>
            <div style={{
              fontSize: '12px',
              color: theme.colors.text.secondary,
              marginTop: theme.spacing.xs
            }}>
              Example: {AMOUNT_FORMATS.find(f => f.value === bankConfig.amountFormat)?.example}
            </div>
          </div>

          {/* Date Format Configuration */}
          <div style={{ marginTop: theme.spacing.md }}>
            <label style={labelStyle}>
              Date Format
            </label>
            <input
              type="text"
              value={bankConfig.dateFormat}
              onChange={(e) => setBankConfig(prev => ({ ...prev, dateFormat: e.target.value }))}
              placeholder="e.g. %Y-%m-%d, %d/%m/%Y, %m/%d/%Y"
              style={inputStyle}
            />
            <div style={{
              fontSize: '12px',
              color: theme.colors.text.secondary,
              marginTop: theme.spacing.xs
            }}>
              Leave empty for auto-detection. Examples: %Y-%m-%d for "2024-01-15", %d/%m/%Y for "15/01/2024"
              {analysis?.date_format_detection?.detected_format && (
                <div style={{ marginTop: theme.spacing.xs, color: theme.colors.primary }}>
                  Detected: {analysis.date_format_detection.detected_format}
                </div>
              )}
            </div>
          </div>

          {/* Multi-Currency Support Toggle */}
          <div style={{ marginTop: theme.spacing.md }}>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={bankConfig.isMultiCurrency}
                onChange={(e) => setBankConfig(prev => ({
                  ...prev,
                  isMultiCurrency: e.target.checked,
                  // Clear account mappings when toggling off
                  accountMappings: e.target.checked ? prev.accountMappings : {}
                }))}
                style={{ marginRight: theme.spacing.sm }}
              />
              <span style={labelStyle}>Multi-Currency Support</span>
            </label>
            <div style={{
              fontSize: '12px',
              color: theme.colors.text.secondary,
              marginTop: theme.spacing.xs
            }}>
              Enable for banks like Wise that handle multiple currencies with separate accounts
            </div>
          </div>

          {/* Multi-Currency Account Mappings */}
          {bankConfig.isMultiCurrency && (
            <div style={{ marginTop: theme.spacing.md }}>
              <label style={labelStyle}>
                Currency to Account Mappings
              </label>
              <div style={{
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.md,
                padding: theme.spacing.md,
                backgroundColor: theme.colors.background.elevated
              }}>
                {Object.entries(bankConfig.accountMappings).map(([currency, account], index) => (
                  <div key={index} style={{
                    display: 'flex',
                    gap: theme.spacing.sm,
                    marginBottom: theme.spacing.sm,
                    alignItems: 'center'
                  }}>
                    <input
                      type="text"
                      placeholder="Currency (e.g. USD)"
                      value={currency}
                      onChange={(e) => {
                        const newMappings = { ...bankConfig.accountMappings };
                        delete newMappings[currency];
                        newMappings[e.target.value] = account;
                        setBankConfig(prev => ({ ...prev, accountMappings: newMappings }));
                      }}
                      style={{ ...inputStyle, flex: 1 }}
                    />
                    <span style={{ color: theme.colors.text.secondary }}>→</span>
                    <input
                      type="text"
                      placeholder="Account Name (e.g. Wise USD)"
                      value={account}
                      onChange={(e) => {
                        setBankConfig(prev => ({
                          ...prev,
                          accountMappings: {
                            ...prev.accountMappings,
                            [currency]: e.target.value
                          }
                        }));
                      }}
                      style={{ ...inputStyle, flex: 2 }}
                    />
                    <button
                      onClick={() => {
                        const newMappings = { ...bankConfig.accountMappings };
                        delete newMappings[currency];
                        setBankConfig(prev => ({ ...prev, accountMappings: newMappings }));
                      }}
                      style={{
                        padding: theme.spacing.xs,
                        backgroundColor: theme.colors.error,
                        color: 'white',
                        border: 'none',
                        borderRadius: theme.borderRadius.sm,
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      Remove
                    </button>
                  </div>
                ))}
                <button
                  onClick={() => {
                    setBankConfig(prev => ({
                      ...prev,
                      accountMappings: {
                        ...prev.accountMappings,
                        '': ''
                      }
                    }));
                  }}
                  style={{
                    padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
                    backgroundColor: theme.colors.primary,
                    color: 'white',
                    border: 'none',
                    borderRadius: theme.borderRadius.md,
                    cursor: 'pointer',
                    fontSize: '12px'
                  }}
                >
                  Add Currency Mapping
                </button>
                <div style={{
                  fontSize: '12px',
                  color: theme.colors.text.secondary,
                  marginTop: theme.spacing.sm
                }}>
                  Example: USD → Wise USD, EUR → Wise EUR, GBP → Wise GBP
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Sample Data Preview */}
        {analysis && analysis.sample_data && analysis.sample_data.length > 0 && (
          <div style={{ marginBottom: theme.spacing.xl }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: theme.colors.primary,
              // marginBottom: theme.spacing.md
            }}>
              Sample Data Preview
            </h2>
            <div>
              {console.log('DEBUG: Frontend - Rendering InteractiveDataTable with data:', analysis.sample_data)}
              <InteractiveDataTable
                data={analysis.sample_data}
                isReviewMode={true}
                showToolbar={false}
                showPagination={true}
                showTitle={false}
                defaultItemsPerPage={10}
                disableSorting={true}
              />
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
            gap: theme.spacing.md,
            marginBottom: theme.spacing.md
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
              {!bankConfig.isMultiCurrency && (
                <div>cashew_account = {bankConfig.cashewAccount || bankConfig.bankName || 'unknown_bank'}</div>
              )}
              <div>content_signatures = {bankConfig.detection_content_signatures || ''}</div>

              <div style={{ color: theme.colors.primary, marginTop: theme.spacing.md, marginBottom: theme.spacing.sm }}>[csv_config]</div>
              <div>header_row = {bankConfig.headerRow || 1}</div>
              <div>encoding = {analysis?.encoding || 'utf-8'}</div>
              <div>delimiter = ,</div>
              <div>has_header = true</div>
              {bankConfig.dateFormat && <div>date_format = {bankConfig.dateFormat}</div>}

              <div style={{ color: theme.colors.primary, marginTop: theme.spacing.md, marginBottom: theme.spacing.sm }}>[column_mapping]</div>
              {Object.entries(bankConfig.columnMappings).filter(([key, value]) => value).map(([key, value]) => (
                <div key={key}>{key} = {value}</div>
              ))}

              <div style={{ color: theme.colors.primary, marginTop: theme.spacing.md, marginBottom: theme.spacing.sm }}>[amount_format]</div>
              <div>format = {bankConfig.amountFormat || 'american'}</div>

              {bankConfig.isMultiCurrency && Object.keys(bankConfig.accountMappings).length > 0 && (
                <>
                  <div style={{ color: theme.colors.primary, marginTop: theme.spacing.md, marginBottom: theme.spacing.sm }}>[account_mapping]</div>
                  {Object.entries(bankConfig.accountMappings).filter(([currency, account]) => currency && account).map(([currency, account]) => (
                    <div key={currency}>{currency} = {account}</div>
                  ))}
                </>
              )}
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
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.md,
              cursor: (!selectedFile || analysisLoading) ? 'not-allowed' : 'pointer',
              opacity: (!selectedFile || analysisLoading) ? 0.5 : 1,
              transition: 'all 0.2s'
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