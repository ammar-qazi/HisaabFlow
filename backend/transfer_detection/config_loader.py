"""
Configuration loader for bank configurations
"""
import configparser
from pathlib import Path
from typing import Dict, Optional
from .config_models import (
    CSVConfig, DataCleaningConfig, AmountParsingConfig, EnhancedBankConfig
)


class ConfigLoader:
    """Handles loading configuration files"""
    
    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)
    
    def load_app_config(self) -> configparser.ConfigParser:
        """Load global app configuration"""
        config = configparser.ConfigParser()
        app_config_path = self.config_dir / "app.conf"
        
        if app_config_path.exists():
            config.read(app_config_path)
            print("[SUCCESS] app.conf loaded")
        else:
            # Default configuration if file missing
            print("[WARNING]  app.conf not found. Using defaults")
            config['general'] = {
                'user_name': 'Your Name Here',
                'date_tolerance_hours': '72'
            }
            config['transfer_detection'] = {
                'confidence_threshold': '0.7'
            }
        return config
    
    def load_bank_configs(self) -> Dict[str, EnhancedBankConfig]:
        """Load all enhanced bank configuration files"""
        bank_configs = {}
        
        for config_file in self.config_dir.glob("*.conf"):
            if config_file.name == "app.conf":
                continue
                
            bank_name = config_file.stem
            config = configparser.ConfigParser()
            
            # Preserve case for option names (keys)
            config.optionxform = str
            
            config.read(config_file)
            
            try:
                enhanced_config = self._parse_bank_config(config, bank_name)
                bank_configs[bank_name] = enhanced_config
                print(f"[SUCCESS] Loaded enhanced {bank_name} config")
                
            except Exception as e:
                print(f"[ERROR]  Error loading enhanced {bank_name}.conf: {e}")
                import traceback
                traceback.print_exc()
        
        return bank_configs
    
    def _parse_bank_config(self, config: configparser.ConfigParser, bank_name: str) -> EnhancedBankConfig:
        """Parse a single bank configuration file"""
        # Basic bank info
        name = config.get('bank_info', 'name', fallback=bank_name)
        file_patterns = [p.strip() for p in config.get('bank_info', 'file_patterns', fallback=bank_name).split(',')]
        currency_primary = config.get('bank_info', 'currency_primary', fallback='USD')
        cashew_account = config.get('bank_info', 'cashew_account', fallback=bank_name)
        
        # CSV configuration
        csv_config = self._parse_csv_config(config)
        
        # Column mapping
        column_mapping = dict(config.items('column_mapping')) if config.has_section('column_mapping') else {}
        
        # Account mapping
        account_mapping = dict(config.items('account_mapping')) if config.has_section('account_mapping') else {}
        
        # Data cleaning config
        data_cleaning = self._parse_data_cleaning_config(config, currency_primary)
        
        # Date formats
        date_formats = self._parse_date_formats(config)
        
        # Amount parsing config
        amount_parsing = self._parse_amount_parsing_config(config)
        
        # Transfer patterns
        outgoing_patterns = dict(config.items('outgoing_patterns')) if config.has_section('outgoing_patterns') else {}
        incoming_patterns = dict(config.items('incoming_patterns')) if config.has_section('incoming_patterns') else {}
        
        # Categorization rules
        categorization_rules = dict(config.items('categorization')) if config.has_section('categorization') else {}
        
        # Default category rules
        default_category_rules = dict(config.items('default_category_rules')) if config.has_section('default_category_rules') else {
            'positive_amount': 'Income',
            'negative_amount': 'Expense',
            'zero_amount': 'Transfer'
        }
        
        return EnhancedBankConfig(
            name=name,
            file_patterns=file_patterns,
            currency_primary=currency_primary,
            cashew_account=cashew_account,
            csv_config=csv_config,
            column_mapping=column_mapping,
            account_mapping=account_mapping,
            data_cleaning=data_cleaning,
            date_formats=date_formats,
            amount_parsing=amount_parsing,
            outgoing_patterns=outgoing_patterns,
            incoming_patterns=incoming_patterns,
            categorization_rules=categorization_rules,
            default_category_rules=default_category_rules
        )
    
    def _parse_csv_config(self, config: configparser.ConfigParser) -> CSVConfig:
        """Parse CSV configuration section"""
        return CSVConfig(
            has_header=config.getboolean('csv_config', 'has_header', fallback=True) if config.has_section('csv_config') else True,
            skip_rows=config.getint('csv_config', 'skip_rows', fallback=0) if config.has_section('csv_config') else 0,
            date_format=config.get('csv_config', 'date_format', fallback='%Y-%m-%d') if config.has_section('csv_config') else '%Y-%m-%d',
            encoding=config.get('csv_config', 'encoding', fallback='utf-8') if config.has_section('csv_config') else 'utf-8',
            start_row=self._get_optional_int(config, 'csv_config', 'start_row') if config.has_section('csv_config') else None,
            end_row=self._get_optional_int(config, 'csv_config', 'end_row') if config.has_section('csv_config') else None,
            start_col=self._get_optional_int(config, 'csv_config', 'start_col') if config.has_section('csv_config') else None,
            end_col=self._get_optional_int(config, 'csv_config', 'end_col') if config.has_section('csv_config') else None
        )
    
    def _parse_data_cleaning_config(self, config: configparser.ConfigParser, currency_primary: str) -> DataCleaningConfig:
        """Parse data cleaning configuration section"""
        return DataCleaningConfig(
            enable_currency_addition=config.getboolean('data_cleaning', 'enable_currency_addition', fallback=False) if config.has_section('data_cleaning') else False,
            multi_currency=config.getboolean('data_cleaning', 'multi_currency', fallback=False) if config.has_section('data_cleaning') else False,
            numeric_amount_conversion=config.getboolean('data_cleaning', 'numeric_amount_conversion', fallback=True) if config.has_section('data_cleaning') else True,
            date_standardization=config.getboolean('data_cleaning', 'date_standardization', fallback=True) if config.has_section('data_cleaning') else True,
            remove_invalid_rows=config.getboolean('data_cleaning', 'remove_invalid_rows', fallback=True) if config.has_section('data_cleaning') else True,
            default_currency=config.get('data_cleaning', 'default_currency', fallback=currency_primary) if config.has_section('data_cleaning') else currency_primary
        )
    
    def _parse_date_formats(self, config: configparser.ConfigParser) -> list:
        """Parse date formats section"""
        date_formats = []
        if config.has_section('date_formats'):
            for key, value in config.items('date_formats'):
                date_formats.append(value)
        else:
            date_formats = ['%Y-%m-%d']
        return date_formats
    
    def _parse_amount_parsing_config(self, config: configparser.ConfigParser) -> AmountParsingConfig:
        """Parse amount parsing configuration section"""
        return AmountParsingConfig(
            format=config.get('amount_parsing', 'format', fallback='numeric') if config.has_section('amount_parsing') else 'numeric',
            decimal_separator=config.get('amount_parsing', 'decimal_separator', fallback='.') if config.has_section('amount_parsing') else '.',
            thousand_separator=config.get('amount_parsing', 'thousand_separator', fallback=',') if config.has_section('amount_parsing') else ',',
            currency_symbol=config.get('amount_parsing', 'currency_symbol', fallback='$') if config.has_section('amount_parsing') else '$'
        )
    
    def _get_optional_int(self, config: configparser.ConfigParser, section: str, key: str) -> Optional[int]:
        """Get optional integer value from config"""
        try:
            value = config.get(section, key, fallback=None)
            if value and value.strip():
                return int(value)
            return None
        except (ValueError, configparser.NoSectionError, configparser.NoOptionError):
            return None
