"""
Unified Configuration Service
Consolidates all configuration management into a single, well-designed service
Replaces 4 separate ConfigManager implementations with one unified interface
"""
import os
import configparser
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import csv
import sys

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@dataclass
class CSVConfig:
    """CSV parsing configuration"""
    delimiter: str = ","
    quote_char: str = '"'
    encoding: str = "utf-8"
    has_header: bool = True
    skip_rows: int = 0


@dataclass
class DataCleaningConfig:
    """Data cleaning configuration"""
    currency_symbols: List[str]
    date_formats: List[str]
    description_cleaning_rules: Dict[str, str]
    amount_decimal_separator: str = "."
    amount_thousand_separator: str = ","
    
    # Additional fields for API compatibility
    enable_currency_addition: bool = True
    multi_currency: bool = False
    numeric_amount_conversion: bool = True
    date_standardization: bool = True
    remove_invalid_rows: bool = True
    default_currency: str = "USD"


@dataclass
class BankDetectionInfo:
    """Bank detection information"""
    bank_name: str
    display_name: str
    content_signatures: List[str]
    required_headers: List[str]
    filename_patterns: List[str]
    confidence_weight: float = 1.0


@dataclass
class UnifiedBankConfig:
    """Complete bank configuration"""
    name: str
    display_name: str
    
    # Detection
    detection_info: BankDetectionInfo
    
    # CSV Processing
    csv_config: CSVConfig
    column_mapping: Dict[str, str]
    account_mapping: Dict[str, str]
    
    # Data Processing
    data_cleaning: DataCleaningConfig
    
    # Transfer Detection
    outgoing_patterns: List[str]
    incoming_patterns: List[str]
    
    # Categorization
    categorization_rules: Dict[str, str]
    default_category_rules: Dict[str, str]
    conditional_description_overrides: List[Dict[str, Any]]
    
    # Bank info (with defaults)
    currency_primary: str = "USD"
    cashew_account: str = ""


class UnifiedConfigService:
    """
    Unified Configuration Service
    Single source of truth for all configuration management
    """
    
    def __init__(self, config_dir: str = None):
        """Initialize with config directory"""
        self.config_dir = self._resolve_config_dir(config_dir)
        self._app_config: Optional[configparser.ConfigParser] = None
        self._bank_configs: Dict[str, UnifiedBankConfig] = {}
        self._detection_patterns: Dict[str, BankDetectionInfo] = {}
        
        # Load configurations on initialization
        self._load_app_config()
        self._load_all_bank_configs()
        
        print(f"[BUILD] [UnifiedConfigService] Initialized with {len(self._bank_configs)} bank configurations")
    
    def _resolve_config_dir(self, config_dir: Optional[str]) -> str:
        """Resolve configuration directory path"""
        if config_dir:
            return config_dir
            
        # Try to get config directory through utility function first
        try:
            from backend.csv_parser.utils import get_config_dir_for_manager
            user_config_dir = get_config_dir_for_manager()
            if user_config_dir:
                return user_config_dir
        except ImportError:
            pass
        
        # Default: project_root/configs
        # From backend/shared/config/ go up to project root
        current_dir = os.path.dirname(os.path.abspath(__file__))  # backend/shared/config/
        backend_dir = os.path.dirname(os.path.dirname(current_dir))  # backend/
        project_root = os.path.dirname(backend_dir)  # project root
        return os.path.join(project_root, 'configs')
    
    # ========== App Configuration ==========
    
    def _load_app_config(self) -> None:
        """Load application configuration"""
        self._app_config = configparser.ConfigParser()
        app_config_path = os.path.join(self.config_dir, "app.conf")
        
        if os.path.exists(app_config_path):
            self._app_config.read(app_config_path)
        else:
            print("[WARNING] [UnifiedConfigService] app.conf not found, using defaults")
            # Set defaults
            self._app_config['general'] = {
                'date_tolerance_hours': '72',
                'user_name': 'Your Name Here'
            }
            self._app_config['transfer_detection'] = {
                'confidence_threshold': '0.7'
            }
            self._app_config['transfer_categorization'] = {
                'default_pair_category': 'Balance Correction'
            }
    
    def get_user_name(self) -> str:
        """Get configured user name"""
        return self._app_config.get('general', 'user_name', fallback='Your Name Here')
    
    def get_date_tolerance(self) -> int:
        """Get date tolerance in hours"""
        return self._app_config.getint('general', 'date_tolerance_hours', fallback=72)
    
    def get_confidence_threshold(self) -> float:
        """Get minimum confidence threshold for transfer detection"""
        return self._app_config.getfloat('transfer_detection', 'confidence_threshold', fallback=0.7)
    
    def get_default_transfer_category(self) -> str:
        """Get default category for transfer pairs"""
        return self._app_config.get('transfer_categorization', 'default_pair_category', fallback='Balance Correction')
    
    # ========== Bank Configuration Loading ==========
    
    def _load_all_bank_configs(self) -> None:
        """Load all bank configurations from .conf files"""
        print(f"[BUILD] [UnifiedConfigService] Loading bank configurations from: {self.config_dir}")
        
        if not os.path.exists(self.config_dir):
            print(f"[ERROR] [UnifiedConfigService] Config directory not found: {self.config_dir}")
            return
        
        config_files = [f for f in os.listdir(self.config_dir) if f.endswith('.conf')]
        print(f"[BUILD] [UnifiedConfigService] Found .conf files: {config_files}")
        
        for config_file in config_files:
            if config_file == 'app.conf':  # Skip app config
                continue
                
            bank_name = config_file.replace('.conf', '')
            config_path = os.path.join(self.config_dir, config_file)
            
            try:
                bank_config = self._load_bank_config(config_path, bank_name)
                if bank_config:
                    self._bank_configs[bank_name] = bank_config
                    self._detection_patterns[bank_name] = bank_config.detection_info
                    print(f"[SUCCESS] [UnifiedConfigService] Loaded config for bank: {bank_name}")
            except Exception as e:
                print(f"[ERROR] [UnifiedConfigService] Failed to load {config_file}: {e}")
    
    def _load_bank_config(self, config_path: str, bank_name: str) -> Optional[UnifiedBankConfig]:
        """Load individual bank configuration"""
        config = configparser.ConfigParser()
        config.read(config_path)
        
        try:
            # Extract bank info
            bank_info = config['bank_info']
            display_name = bank_info.get('display_name', bank_name.title())
            currency_primary = bank_info.get('currency_primary', 'USD')
            cashew_account = bank_info.get('cashew_account', bank_name.title())
            
            # Build detection info
            detection_info = self._build_detection_info(config, bank_name, display_name)
            
            # Build CSV config
            csv_config = self._build_csv_config(config)
            
            # Build column mapping
            column_mapping = dict(config['column_mapping']) if 'column_mapping' in config else {}
            
            # Build account mapping
            account_mapping = dict(config['account_mapping']) if 'account_mapping' in config else {}
            
            # Build data cleaning config
            data_cleaning = self._build_data_cleaning_config(config)
            
            # Build transfer patterns
            outgoing_patterns = self._extract_transfer_patterns(config, 'outgoing_patterns')
            incoming_patterns = self._extract_transfer_patterns(config, 'incoming_patterns')
            
            # Build categorization rules
            categorization_rules = dict(config['categorization']) if 'categorization' in config else {}
            default_category_rules = dict(config['default_category_rules']) if 'default_category_rules' in config else {}
            
            # Build conditional overrides
            conditional_description_overrides = self._extract_conditional_overrides(config)
            
            return UnifiedBankConfig(
                name=bank_name,
                display_name=display_name,
                currency_primary=currency_primary,
                cashew_account=cashew_account,
                detection_info=detection_info,
                csv_config=csv_config,
                column_mapping=column_mapping,
                account_mapping=account_mapping,
                data_cleaning=data_cleaning,
                outgoing_patterns=outgoing_patterns,
                incoming_patterns=incoming_patterns,
                categorization_rules=categorization_rules,
                default_category_rules=default_category_rules,
                conditional_description_overrides=conditional_description_overrides
            )
            
        except KeyError as e:
            print(f"[ERROR] [UnifiedConfigService] Missing required section in {bank_name}: {e}")
            return None
        except Exception as e:
            print(f"[ERROR] [UnifiedConfigService] Error parsing config for {bank_name}: {e}")
            return None
    
    def _build_detection_info(self, config: configparser.ConfigParser, bank_name: str, display_name: str) -> BankDetectionInfo:
        """Build bank detection information from config"""
        bank_info = config['bank_info']
        
        # Extract content signatures
        content_signatures = []
        if 'detection_content_signatures' in bank_info:
            content_signatures = [sig.strip() for sig in bank_info['detection_content_signatures'].split(',')]
        
        # Extract required headers
        required_headers = []
        if 'expected_headers' in bank_info:
            required_headers = [header.strip() for header in bank_info['expected_headers'].split(',')]
        
        # Extract filename patterns
        filename_patterns = [bank_name.lower()]  # Default pattern
        
        # Add simple file patterns
        if 'file_patterns' in bank_info:
            patterns = [pattern.strip() for pattern in bank_info['file_patterns'].split(',')]
            filename_patterns.extend(patterns)
        
        # Add regex patterns
        if 'filename_regex_patterns' in bank_info:
            regex_patterns = [pattern.strip() for pattern in bank_info['filename_regex_patterns'].split(',')]
            filename_patterns.extend(regex_patterns)
        
        # Extract confidence weight
        confidence_weight = float(bank_info.get('confidence_weight', 1.0))
        
        return BankDetectionInfo(
            bank_name=bank_name,
            display_name=display_name,
            content_signatures=content_signatures,
            required_headers=required_headers,
            filename_patterns=filename_patterns,
            confidence_weight=confidence_weight
        )
    
    def _build_csv_config(self, config: configparser.ConfigParser) -> CSVConfig:
        """Build CSV configuration from config file"""
        if 'csv_config' in config:
            csv_section = config['csv_config']
            return CSVConfig(
                delimiter=csv_section.get('delimiter', ','),
                quote_char=csv_section.get('quote_char', '"'),
                encoding=csv_section.get('encoding', 'utf-8'),
                has_header=csv_section.getboolean('has_header', fallback=True),
                skip_rows=csv_section.getint('skip_rows', fallback=0)
            )
        else:
            # Return defaults if no csv_config section
            return CSVConfig()
    
    def _build_data_cleaning_config(self, config: configparser.ConfigParser) -> DataCleaningConfig:
        """Build data cleaning configuration"""
        # Default values
        currency_symbols = ['$', '€', '£', '₹', 'PKR', 'USD', 'EUR', 'GBP']
        date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d.%m.%Y']
        amount_decimal_separator = '.'
        amount_thousand_separator = ','
        description_cleaning_rules = {}
        
        # Extract from data_cleaning section if exists
        if 'data_cleaning' in config:
            cleaning_section = config['data_cleaning']
            
            if 'currency_symbols' in cleaning_section:
                currency_symbols = [sym.strip() for sym in cleaning_section['currency_symbols'].split(',')]
            
            if 'date_formats' in cleaning_section:
                date_formats = [fmt.strip() for fmt in cleaning_section['date_formats'].split(',')]
            
            amount_decimal_separator = cleaning_section.get('amount_decimal_separator', '.')
            amount_thousand_separator = cleaning_section.get('amount_thousand_separator', ',')
        
        # Extract description cleaning rules from separate section
        if 'description_cleaning' in config:
            description_cleaning_rules = dict(config['description_cleaning'])
        
        # Extract additional flags from data_cleaning section
        enable_currency_addition = True
        multi_currency = False
        numeric_amount_conversion = True
        date_standardization = True
        remove_invalid_rows = True
        default_currency = "USD"
        
        if 'data_cleaning' in config:
            cleaning_section = config['data_cleaning']
            enable_currency_addition = cleaning_section.getboolean('enable_currency_addition', fallback=True)
            multi_currency = cleaning_section.getboolean('multi_currency', fallback=False)
            numeric_amount_conversion = cleaning_section.getboolean('numeric_amount_conversion', fallback=True)
            date_standardization = cleaning_section.getboolean('date_standardization', fallback=True)
            remove_invalid_rows = cleaning_section.getboolean('remove_invalid_rows', fallback=True)
            default_currency = cleaning_section.get('default_currency', 'USD')
        
        return DataCleaningConfig(
            currency_symbols=currency_symbols,
            date_formats=date_formats,
            description_cleaning_rules=description_cleaning_rules,
            amount_decimal_separator=amount_decimal_separator,
            amount_thousand_separator=amount_thousand_separator,
            enable_currency_addition=enable_currency_addition,
            multi_currency=multi_currency,
            numeric_amount_conversion=numeric_amount_conversion,
            date_standardization=date_standardization,
            remove_invalid_rows=remove_invalid_rows,
            default_currency=default_currency
        )
    
    def _extract_transfer_patterns(self, config: configparser.ConfigParser, section_name: str) -> List[str]:
        """Extract transfer patterns from config section"""
        if section_name not in config:
            return []
        
        patterns = []
        for key, value in config[section_name].items():
            patterns.append(value.strip())
        
        return patterns
    
    def _extract_conditional_overrides(self, config: configparser.ConfigParser) -> List[Dict[str, Any]]:
        """Extract conditional override rules"""
        overrides = []
        
        # Look for conditional override sections
        for section_name in config.sections():
            if section_name.startswith('conditional_override_'):
                override_config = dict(config[section_name])
                override_config['name'] = section_name
                overrides.append(override_config)
        
        return overrides
    
    # ========== Public API Methods ==========
    
    def list_banks(self) -> List[str]:
        """List all available bank configurations"""
        return list(self._bank_configs.keys())
    
    def get_bank_config(self, bank_name: str) -> Optional[UnifiedBankConfig]:
        """Get bank configuration by name"""
        return self._bank_configs.get(bank_name)
    
    def get_detection_patterns(self) -> Dict[str, BankDetectionInfo]:
        """Get all bank detection patterns"""
        return self._detection_patterns.copy()
    
    def detect_bank(self, filename: str, content_sample: str = None) -> Optional[str]:
        """
        Detect bank from filename and optionally content
        Returns bank name or None if not detected
        """
        import re
        
        filename_lower = filename.lower()
        
        # Collect matches with confidence scores
        matches = []
        
        for bank_name, detection_info in self._detection_patterns.items():
            confidence = 0.0
            
            # Check filename patterns
            for pattern in detection_info.filename_patterns:
                pattern_lower = pattern.lower()
                
                # Check if it's a regex pattern (starts with ^)
                if pattern.startswith('^') or pattern.startswith('.*'):
                    try:
                        if re.match(pattern, filename) or re.match(pattern, filename_lower):
                            confidence += 100 * detection_info.confidence_weight  # Higher score for regex match
                    except re.error:
                        # If regex is invalid, fall back to substring match
                        if pattern_lower in filename_lower:
                            confidence += len(pattern) * detection_info.confidence_weight
                else:
                    # Simple substring match
                    if pattern_lower in filename_lower:
                        confidence += len(pattern) * detection_info.confidence_weight
            
            # Check content signatures if content provided
            if content_sample and detection_info.content_signatures:
                content_lower = content_sample.lower()
                for signature in detection_info.content_signatures:
                    if signature.lower() in content_lower:
                        confidence += 50 * detection_info.confidence_weight
            
            if confidence > 0:
                matches.append((bank_name, confidence))
        
        # Return highest confidence match
        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            return matches[0][0]
        
        return None
    
    def get_csv_config(self, bank_name: str) -> Optional[CSVConfig]:
        """Get CSV configuration for bank"""
        bank_config = self._bank_configs.get(bank_name)
        return bank_config.csv_config if bank_config else None
    
    def get_column_mapping(self, bank_name: str) -> Dict[str, str]:
        """Get column mapping for bank"""
        bank_config = self._bank_configs.get(bank_name)
        return bank_config.column_mapping if bank_config else {}
    
    def get_account_mapping(self, bank_name: str) -> Dict[str, str]:
        """Get account mapping for bank"""
        bank_config = self._bank_configs.get(bank_name)
        return bank_config.account_mapping if bank_config else {}
    
    def get_transfer_patterns(self, bank_name: str, direction: str) -> List[str]:
        """Get transfer patterns for bank and direction (outgoing/incoming)"""
        bank_config = self._bank_configs.get(bank_name)
        if not bank_config:
            return []
        
        if direction.lower() == 'outgoing':
            return bank_config.outgoing_patterns
        elif direction.lower() == 'incoming':
            return bank_config.incoming_patterns
        else:
            return []
    
    def categorize_merchant(self, bank_name: str, merchant: str) -> Optional[str]:
        """Categorize merchant using bank-specific rules"""
        bank_config = self._bank_configs.get(bank_name)
        if not bank_config:
            return None
        
        merchant_lower = merchant.lower()
        
        # Check categorization rules
        for pattern, category in bank_config.categorization_rules.items():
            if pattern.lower() in merchant_lower:
                return category
        
        # Check default category rules
        for pattern, category in bank_config.default_category_rules.items():
            if pattern.lower() in merchant_lower:
                return category
        
        return None
    
    def apply_description_cleaning(self, bank_name: str, description: str) -> str:
        """Apply bank-specific description cleaning rules"""
        bank_config = self._bank_configs.get(bank_name)
        if not bank_config or not bank_config.data_cleaning or not bank_config.data_cleaning.description_cleaning_rules:
            return description
        
        cleaned_description = description
        
        # Apply each cleaning rule
        for rule_name, rule_pattern in bank_config.data_cleaning.description_cleaning_rules.items():
            import re
            try:
                # Check if it's a regex replacement pattern (contains |)
                if '|' in rule_pattern:
                    # Format: pattern|replacement (split from right to handle pipes in pattern)
                    pattern, replacement = rule_pattern.rsplit('|', 1)
                    pattern = pattern.strip()
                    replacement = replacement.strip()
                    cleaned_description = re.sub(pattern, replacement, cleaned_description, flags=re.IGNORECASE)
                else:
                    # Simple replacement using rule name as pattern
                    cleaned_description = cleaned_description.replace(rule_name, rule_pattern)
            except re.error:
                # If regex fails, do simple replacement
                cleaned_description = cleaned_description.replace(rule_name, rule_pattern)
        
        return cleaned_description
    
    def get_data_cleaning_config(self, bank_name: str) -> Optional[DataCleaningConfig]:
        """Get data cleaning configuration for bank"""
        bank_config = self._bank_configs.get(bank_name)
        return bank_config.data_cleaning if bank_config else None
    
    # ========== Configuration Save/Load API ==========
    
    def save_bank_config(self, bank_name: str, config_data: Dict[str, Any]) -> bool:
        """Save bank configuration to file"""
        try:
            config_path = os.path.join(self.config_dir, f"{bank_name}.conf")
            
            # Convert config_data to ConfigParser format
            config = configparser.ConfigParser()
            
            for section_name, section_data in config_data.items():
                config[section_name] = {}
                for key, value in section_data.items():
                    if isinstance(value, (list, tuple)):
                        config[section_name][key] = ', '.join(str(v) for v in value)
                    else:
                        config[section_name][key] = str(value)
            
            # Write to file
            with open(config_path, 'w') as config_file:
                config.write(config_file)
            
            # Reload configuration
            self._load_all_bank_configs()
            
            print(f"[SUCCESS] [UnifiedConfigService] Saved configuration for {bank_name}")
            return True
            
        except Exception as e:
            print(f"[ERROR] [UnifiedConfigService] Failed to save config for {bank_name}: {e}")
            return False
    
    # ========== Legacy Compatibility Methods ==========
    
    def detect_bank_type(self, file_name: str) -> Optional[str]:
        """Legacy method for transfer detection compatibility"""
        return self.detect_bank(file_name)
    
    def extract_name_from_transfer_pattern(self, pattern: str, description: str) -> Optional[str]:
        """Extract name from transfer description using pattern with {name} placeholder"""
        import re
        if '{name}' not in pattern and '{user_name}' not in pattern:
            return None

        # Find the placeholder (e.g., {name}, {user_name})
        placeholder_match = re.search(r'\{(\w+)\}', pattern)
        if not placeholder_match:
            return None

        placeholder_text = placeholder_match.group(0)  # e.g., "{name}" or "{user_name}"
        
        # Create a regex pattern by escaping the original pattern and replacing placeholder
        escaped_pattern = re.escape(pattern)
        name_regex = escaped_pattern.replace(re.escape(placeholder_text), r'(.+?)')
        
        try:
            match = re.search(name_regex, description, re.IGNORECASE)
            if match:
                extracted_name = match.group(1).strip()
                return extracted_name if extracted_name else None
        except re.error:
            pass
        
        return None


# Singleton instance for global access
_unified_config_service: Optional[UnifiedConfigService] = None


def get_unified_config_service(config_dir: str = None) -> UnifiedConfigService:
    """Get singleton instance of unified config service"""
    global _unified_config_service
    
    if _unified_config_service is None:
        _unified_config_service = UnifiedConfigService(config_dir)
    
    return _unified_config_service


def reset_unified_config_service():
    """Reset singleton instance (for testing)"""
    global _unified_config_service
    _unified_config_service = None