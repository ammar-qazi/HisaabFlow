"""
Enhanced Configuration-based Bank Rules System
Manages loading and accessing bank configurations from .conf files
Now includes CSV parsing, data cleaning, and template functionality
"""
import configparser
from typing import Dict, List, Optional
from .config_models import CSVConfig, DataCleaningConfig, AmountParsingConfig, EnhancedBankConfig
from .config_loader import ConfigLoader


class EnhancedConfigurationManager:
    """Enhanced configuration manager with CSV parsing and template support"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_loader = ConfigLoader(config_dir)
        self.app_config = self.config_loader.load_app_config()
        self.bank_configs: Dict[str, EnhancedBankConfig] = self.config_loader.load_bank_configs()
        
        print(f"🔧 Enhanced Configuration Manager initialized")
        print(f"📁 Config directory: {config_dir}")
        print(f"🏦 Loaded {len(self.bank_configs)} bank configurations")
    
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
    
    # ========== CSV PARSING METHODS ==========
    
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
