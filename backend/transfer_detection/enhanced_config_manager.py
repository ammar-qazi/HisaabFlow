"""
Enhanced Configuration-based Bank Rules System
Manages loading and accessing bank configurations from .conf files
Now includes CSV parsing, data cleaning, and template functionality
"""
import configparser
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class CSVConfig:
    """CSV parsing configuration from config file"""
    has_header: bool = True
    skip_rows: int = 0
    date_format: str = "%Y-%m-%d"
    encoding: str = "utf-8"
    start_row: Optional[int] = None
    end_row: Optional[int] = None
    start_col: Optional[int] = None
    end_col: Optional[int] = None


@dataclass
class DataCleaningConfig:
    """Data cleaning configuration from config file"""
    enable_currency_addition: bool = False
    multi_currency: bool = False
    numeric_amount_conversion: bool = True
    date_standardization: bool = True
    remove_invalid_rows: bool = True
    default_currency: str = "USD"


@dataclass
class AmountParsingConfig:
    """Amount parsing configuration from config file"""
    format: str = "numeric"
    decimal_separator: str = "."
    thousand_separator: str = ","
    currency_symbol: str = "$"


@dataclass
class EnhancedBankConfig:
    """Enhanced bank configuration with CSV parsing support"""
    # Basic bank info
    name: str
    file_patterns: List[str]
    currency_primary: str
    cashew_account: str
    
    # CSV parsing configuration
    csv_config: CSVConfig
    column_mapping: Dict[str, str]
    account_mapping: Dict[str, str]
    data_cleaning: DataCleaningConfig
    date_formats: List[str]
    amount_parsing: AmountParsingConfig
    
    # Transfer detection
    outgoing_patterns: Dict[str, str]
    incoming_patterns: Dict[str, str]
    categorization_rules: Dict[str, str]
    
    # Default rules
    default_category_rules: Dict[str, str]


class EnhancedConfigurationManager:
    """Enhanced configuration manager with CSV parsing and template support"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.app_config = self._load_app_config()
        self.bank_configs: Dict[str, EnhancedBankConfig] = self._load_enhanced_bank_configs()
        
        print(f"🔧 Enhanced Configuration Manager initialized")
        print(f"📁 Config directory: {self.config_dir}")
        print(f"🏦 Loaded {len(self.bank_configs)} bank configurations")
    
    def _load_app_config(self) -> configparser.ConfigParser:
        """Load global app configuration"""
        config = configparser.ConfigParser()
        app_config_path = self.config_dir / "app.conf"
        
        if app_config_path.exists():
            config.read(app_config_path)
            print("✅ app.conf loaded")
        else:
            # Default configuration if file missing
            print("⚠️  app.conf not found. Using defaults")
            config['general'] = {
                'user_name': 'Ammar Qazi',
                'date_tolerance_hours': '72'
            }
            config['transfer_detection'] = {
                'confidence_threshold': '0.7'
            }
        return config
    
    def _load_enhanced_bank_configs(self) -> Dict[str, EnhancedBankConfig]:
        """Load all enhanced bank configuration files"""
        bank_configs = {}
        
        for config_file in self.config_dir.glob("*.conf"):
            if config_file.name == "app.conf":
                continue
                
            bank_name = config_file.stem
            config = configparser.ConfigParser()
            config.read(config_file)
            
            try:
                # Basic bank info
                name = config.get('bank_info', 'name', fallback=bank_name)
                file_patterns = [p.strip() for p in config.get('bank_info', 'file_patterns', fallback=bank_name).split(',')]
                currency_primary = config.get('bank_info', 'currency_primary', fallback='USD')
                cashew_account = config.get('bank_info', 'cashew_account', fallback=bank_name)
                
                # CSV configuration (with fallbacks for backward compatibility)
                csv_config = CSVConfig(
                    has_header=config.getboolean('csv_config', 'has_header', fallback=True) if config.has_section('csv_config') else True,
                    skip_rows=config.getint('csv_config', 'skip_rows', fallback=0) if config.has_section('csv_config') else 0,
                    date_format=config.get('csv_config', 'date_format', fallback='%Y-%m-%d') if config.has_section('csv_config') else '%Y-%m-%d',
                    encoding=config.get('csv_config', 'encoding', fallback='utf-8') if config.has_section('csv_config') else 'utf-8',
                    start_row=self._get_optional_int(config, 'csv_config', 'start_row') if config.has_section('csv_config') else None,
                    end_row=self._get_optional_int(config, 'csv_config', 'end_row') if config.has_section('csv_config') else None,
                    start_col=self._get_optional_int(config, 'csv_config', 'start_col') if config.has_section('csv_config') else None,
                    end_col=self._get_optional_int(config, 'csv_config', 'end_col') if config.has_section('csv_config') else None
                )
                
                # Column mapping
                column_mapping = dict(config.items('column_mapping')) if config.has_section('column_mapping') else {}
                
                # Account mapping
                account_mapping = dict(config.items('account_mapping')) if config.has_section('account_mapping') else {}
                
                # Data cleaning config (with fallbacks for backward compatibility)
                data_cleaning = DataCleaningConfig(
                    enable_currency_addition=config.getboolean('data_cleaning', 'enable_currency_addition', fallback=False) if config.has_section('data_cleaning') else False,
                    multi_currency=config.getboolean('data_cleaning', 'multi_currency', fallback=False) if config.has_section('data_cleaning') else False,
                    numeric_amount_conversion=config.getboolean('data_cleaning', 'numeric_amount_conversion', fallback=True) if config.has_section('data_cleaning') else True,
                    date_standardization=config.getboolean('data_cleaning', 'date_standardization', fallback=True) if config.has_section('data_cleaning') else True,
                    remove_invalid_rows=config.getboolean('data_cleaning', 'remove_invalid_rows', fallback=True) if config.has_section('data_cleaning') else True,
                    default_currency=config.get('data_cleaning', 'default_currency', fallback=currency_primary) if config.has_section('data_cleaning') else currency_primary
                )
                
                # Date formats
                date_formats = []
                if config.has_section('date_formats'):
                    for key, value in config.items('date_formats'):
                        date_formats.append(value)
                else:
                    date_formats = ['%Y-%m-%d']
                
                # Amount parsing config (with fallbacks for backward compatibility)
                amount_parsing = AmountParsingConfig(
                    format=config.get('amount_parsing', 'format', fallback='numeric') if config.has_section('amount_parsing') else 'numeric',
                    decimal_separator=config.get('amount_parsing', 'decimal_separator', fallback='.') if config.has_section('amount_parsing') else '.',
                    thousand_separator=config.get('amount_parsing', 'thousand_separator', fallback=',') if config.has_section('amount_parsing') else ',',
                    currency_symbol=config.get('amount_parsing', 'currency_symbol', fallback='$') if config.has_section('amount_parsing') else '$'
                )
                
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
                
                # Create enhanced bank config
                enhanced_config = EnhancedBankConfig(
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
                
                bank_configs[bank_name] = enhanced_config
                print(f"✅ Loaded enhanced {bank_name} config")
                
            except Exception as e:
                print(f"❌ Error loading enhanced {bank_name}.conf: {e}")
                import traceback
                traceback.print_exc()
        
        return bank_configs
    
    def _get_optional_int(self, config: configparser.ConfigParser, section: str, key: str) -> Optional[int]:
        """Get optional integer value from config"""
        try:
            value = config.get(section, key, fallback=None)
            if value and value.strip():
                return int(value)
            return None
        except (ValueError, configparser.NoSectionError, configparser.NoOptionError):
            return None
    
    # ========== Legacy Methods (for backward compatibility) ==========
    
    def get_user_name(self) -> str:
        """Get configured user name"""
        return self.app_config.get('general', 'user_name', fallback='Ammar Qazi')
    
    def get_date_tolerance(self) -> int:
        """Get date tolerance in hours"""
        return self.app_config.getint('general', 'date_tolerance_hours', fallback=72)
    
    def get_confidence_threshold(self) -> float:
        """Get minimum confidence threshold"""
        return self.app_config.getfloat('transfer_detection', 'confidence_threshold', fallback=0.7)
    
    def detect_bank_type(self, file_name: str) -> Optional[str]:
        """Detect bank type from filename using configuration with priority for longer matches"""
        file_name_lower = file_name.lower()
        
        # Collect all matches with their pattern length for prioritization
        matches = []
        
        for bank_name, config in self.bank_configs.items():
            for pattern in config.file_patterns:
                pattern_clean = pattern.strip().lower()
                if pattern_clean in file_name_lower:
                    # Store match with pattern length for prioritization
                    matches.append((bank_name, len(pattern_clean)))
        
        if not matches:
            return None
        
        # Return the bank with the longest matching pattern (most specific)
        best_match = max(matches, key=lambda x: x[1])
        return best_match[0]
    
    def get_bank_config(self, bank_name: str) -> Optional[EnhancedBankConfig]:
        """Get enhanced bank configuration by name"""
        return self.bank_configs.get(bank_name)
    
    def get_transfer_patterns(self, bank_name: str, direction: str) -> List[str]:
        """Get transfer patterns for a bank and direction (outgoing/incoming)"""
        config = self.bank_configs.get(bank_name)
        if not config:
            return []
        
        patterns = config.outgoing_patterns if direction == 'outgoing' else config.incoming_patterns
        user_name = self.get_user_name()
        
        # Replace {user_name} placeholder in patterns
        compiled_patterns = []
        for pattern in patterns.values():
            compiled_pattern = pattern.format(user_name=user_name)
            compiled_patterns.append(compiled_pattern)
        
        return compiled_patterns
    
    def categorize_merchant(self, bank_name: str, merchant: str) -> Optional[str]:
        """Get category for a merchant based on bank configuration"""
        config = self.bank_configs.get(bank_name)
        if not config:
            return None
        
        merchant_lower = merchant.lower()
        for merchant_pattern, category in config.categorization_rules.items():
            if merchant_pattern.lower() in merchant_lower:
                return category
        
        return None
    
    def list_configured_banks(self) -> List[str]:
        """Get list of configured bank names"""
        return list(self.bank_configs.keys())
    
    # ========== NEW CSV PARSING METHODS ==========
    
    def get_csv_config(self, bank_name: str) -> Optional[CSVConfig]:
        """Get CSV parsing configuration for a bank"""
        config = self.bank_configs.get(bank_name)
        return config.csv_config if config else None
    
    def get_column_mapping(self, bank_name: str) -> Dict[str, str]:
        """Get column mapping for a bank"""
        config = self.bank_configs.get(bank_name)
        return config.column_mapping if config else {}
    
    def get_account_mapping(self, bank_name: str) -> Dict[str, str]:
        """Get account mapping for a bank"""
        config = self.bank_configs.get(bank_name)
        return config.account_mapping if config else {}
    
    def get_data_cleaning_config(self, bank_name: str) -> Optional[DataCleaningConfig]:
        """Get data cleaning configuration for a bank"""
        config = self.bank_configs.get(bank_name)
        return config.data_cleaning if config else None
    
    def get_date_formats(self, bank_name: str) -> List[str]:
        """Get supported date formats for a bank"""
        config = self.bank_configs.get(bank_name)
        return config.date_formats if config else ['%Y-%m-%d']
    
    def get_amount_parsing_config(self, bank_name: str) -> Optional[AmountParsingConfig]:
        """Get amount parsing configuration for a bank"""
        config = self.bank_configs.get(bank_name)
        return config.amount_parsing if config else None
    
    def get_default_category_rules(self, bank_name: str) -> Dict[str, str]:
        """Get default category rules for a bank"""
        config = self.bank_configs.get(bank_name)
        return config.default_category_rules if config else {
            'positive_amount': 'Income',
            'negative_amount': 'Expense',
            'zero_amount': 'Transfer'
        }
