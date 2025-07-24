import axios from 'axios';

const API_BASE = window.BACKEND_URL || 'http://127.0.0.1:8000';
const API_V1_BASE = `${API_BASE}/api/v1`;

// Configure axios defaults
axios.defaults.timeout = 15000;
axios.defaults.headers.common['Content-Type'] = 'application/json';

/**
 * Service for handling configuration-related API calls
 */
export class ConfigurationService {
  /**
   * Loads all available bank configurations
   */
  static async loadConfigurations() {
    try {
      console.log(' Loading bank configurations from /api/v1/configs');
      const response = await axios.get(`${API_V1_BASE}/configs`);
      console.log('[SUCCESS] Configurations loaded:', response.data);
      return {
        success: true,
        configurations: response.data.configurations,
        raw_bank_names: response.data.raw_bank_names || []
      };
    } catch (err) {
      console.error('[ERROR]  Failed to load configurations:', err);
      return {
        success: false,
        error: 'Failed to load bank configurations. Please check if the backend is running.',
        configurations: [],
        raw_bank_names: []
      };
    }
  }

  /**
   * Loads a specific configuration by name
   */
  static async loadConfiguration(configName) {
    if (!configName) {
      console.log(' No configuration selected - user will use manual column mapping with standard Cashew fields');
      return {
        success: true,
        config: null,
        message: 'No configuration selected'
      };
    }
    
    try {
      console.log(` Loading configuration: ${configName}`);
      const response = await axios.get(`${API_V1_BASE}/config/${encodeURIComponent(configName)}`);
      const config = response.data.config;
      
      console.log(` Configuration ${configName} loaded:`, config);
      
      // Debug column mapping
      console.log(' Configuration Load Debug:');
      console.log('  - config.column_mapping:', config.column_mapping);
      console.log('  - Will set columnMapping to:', config.column_mapping || {});
      
      return {
        success: true,
        config,
        message: `Configuration "${configName}" loaded successfully`
      };
      
    } catch (err) {
      console.error('[ERROR]  Configuration load failed:', err);
      console.log(' Configuration load failed - user will use manual column mapping with standard Cashew fields');
      return {
        success: false,
        config: null,
        error: `Failed to load configuration "${configName}": ${err.response?.data?.detail || err.message}`
      };
    }
  }

  /**
   * Processes configuration data for file application
   */
  static processConfigurationForFile(config, fileName) {
    if (!config) {
      return {
        selectedConfiguration: null,
        config: null,
        parseConfig: {
          start_row: 0,
          end_row: null,
          start_col: 0,
          end_col: null,
          encoding: 'utf-8'
        },
        columnMapping: {},
        bankName: '',
        accountMapping: {}
      };
    }

    return {
      config: config,
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
  }

  /**
   * Unknown Bank Configuration API Functions
   * These functions support the unknown bank workflow
   */

  /**
   * Analyzes an unknown CSV file for automatic configuration generation
   */
  static async analyzeUnknownCSV(file, headerRow = null) {
    try {
      console.log(' Analyzing unknown CSV file:', file.name);
      
      const formData = new FormData();
      formData.append('file', file);
      if (headerRow !== null) {
        console.log(' Adding header_row to request:', headerRow);
        formData.append('header_row', headerRow.toString());
      }
      
      const response = await axios.post(`${API_V1_BASE}/unknown-bank/analyze-csv`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('[SUCCESS] CSV analysis completed:', response.data);
      return {
        success: true,
        analysis: response.data
      };
    } catch (err) {
      console.error('[ERROR] CSV analysis failed:', err);
      return {
        success: false,
        error: `Failed to analyze CSV: ${err.response?.data?.detail || err.message}`
      };
    }
  }

  /**
   * Generates bank configuration from analysis and user input
   */
  static async generateBankConfig(configRequest) {
    try {
      console.log(' Generating bank configuration:', configRequest);
      
      const response = await axios.post(`${API_V1_BASE}/unknown-bank/generate-config`, configRequest);
      
      console.log('[SUCCESS] Bank configuration generated:', response.data);
      return {
        success: true,
        config: response.data.config
      };
    } catch (err) {
      console.error('[ERROR] Configuration generation failed:', err);
      return {
        success: false,
        error: `Failed to generate configuration: ${err.response?.data?.detail || err.message}`
      };
    }
  }

  /**
   * Validates a generated bank configuration
   */
  static async validateBankConfig(validationRequest) {
    try {
      console.log(' Validating bank configuration:', validationRequest);
      
      const response = await axios.post(`${API_V1_BASE}/unknown-bank/validate-config`, validationRequest);
      
      console.log('[SUCCESS] Configuration validation completed:', response.data);
      return {
        success: true,
        validation: response.data
      };
    } catch (err) {
      console.error('[ERROR] Configuration validation failed:', err);
      return {
        success: false,
        error: `Failed to validate configuration: ${err.response?.data?.detail || err.message}`
      };
    }
  }

  /**
   * Saves a new bank configuration and reloads configs
   */
  static async saveBankConfig(saveRequest) {
    try {
      console.log(' Saving bank configuration:', saveRequest.bankName);
      
      const response = await axios.post(`${API_V1_BASE}/unknown-bank/save-config`, saveRequest);
      
      console.log('[SUCCESS] Configuration saved successfully:', response.data);
      return {
        success: true,
        message: response.data.message
      };
    } catch (err) {
      console.error('[ERROR] Configuration save failed:', err);
      return {
        success: false,
        error: `Failed to save configuration: ${err.response?.data?.detail || err.message}`
      };
    }
  }

  /**
   * Reloads all bank configurations (useful after creating new config)
   */
  static async reloadConfigurations() {
    try {
      console.log(' Reloading all bank configurations');
      
      const response = await axios.post(`${API_V1_BASE}/reload`);
      
      console.log('[SUCCESS] Configurations reloaded:', response.data);
      return {
        success: true,
        message: 'Bank configurations reloaded successfully'
      };
    } catch (err) {
      console.error('[ERROR] Configuration reload failed:', err);
      return {
        success: false,
        error: `Failed to reload configurations: ${err.response?.data?.detail || err.message}`
      };
    }
  }
}
