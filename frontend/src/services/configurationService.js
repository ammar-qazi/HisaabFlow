import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

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
      console.log('🔍 Loading bank configurations from /api/v1/configs');
      const response = await axios.get(`${API_BASE}/api/v1/configs`);
      console.log('✅ Configurations loaded:', response.data);
      return {
        success: true,
        configurations: response.data.configurations,
        raw_bank_names: response.data.raw_bank_names || []
      };
    } catch (err) {
      console.error('❌ Failed to load configurations:', err);
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
      console.log('🔍 No configuration selected - user will use manual column mapping with standard Cashew fields');
      return {
        success: true,
        config: null,
        message: 'No configuration selected'
      };
    }
    
    try {
      console.log(`🔍 Loading configuration: ${configName}`);
      const response = await axios.get(`${API_BASE}/api/v1/config/${encodeURIComponent(configName)}`);
      const config = response.data.config;
      
      console.log(`📋 Configuration ${configName} loaded:`, config);
      
      // Debug column mapping
      console.log('🔍 Configuration Load Debug:');
      console.log('  - config.column_mapping:', config.column_mapping);
      console.log('  - Will set columnMapping to:', config.column_mapping || {});
      
      return {
        success: true,
        config,
        message: `Configuration "${configName}" loaded successfully`
      };
      
    } catch (err) {
      console.error('❌ Configuration load failed:', err);
      console.log('🔍 Configuration load failed - user will use manual column mapping with standard Cashew fields');
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
}
