"""
Configuration-based Bank Rules System
Manages loading and accessing bank configurations from .conf files
"""
import configparser
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class BankConfig:
    """Bank configuration loaded from .conf file"""
    name: str
    file_patterns: List[str]
    currency_primary: str
    cashew_account: str
    outgoing_patterns: Dict[str, str]
    incoming_patterns: Dict[str, str]
    categorization_rules: Dict[str, str]
    description_cleaning_rules: Dict[str, str]


class ConfigurationManager:
    """Manages loading and accessing bank configurations"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.app_config = self._load_app_config()
        self.bank_configs: Dict[str, BankConfig] = self._load_bank_configs()
    
    def _load_app_config(self) -> configparser.ConfigParser:
        """Load global app configuration"""
        config = configparser.ConfigParser()
        app_config_path = self.config_dir / "app.conf"
        
        if app_config_path.exists():
            config.read(app_config_path)
        else:
            # Default configuration if file missing
            print("⚠️  app.conf not found. Creating default configuration.")
            config['general'] = {
                'date_tolerance_hours': '72'
            }
            config['transfer_detection'] = {
                'confidence_threshold': '0.7'
            }
        return config
    
    def _load_bank_configs(self) -> Dict[str, BankConfig]:
        """Load all bank configuration files"""
        bank_configs = {}
        
        for config_file in self.config_dir.glob("*.conf"):
            if config_file.name == "app.conf":
                continue
                
            bank_name = config_file.stem
            config = configparser.ConfigParser()
            config.read(config_file)
            
            try:
                # Load transfer patterns (support both old and new format)
                outgoing_patterns = {}
                incoming_patterns = {}
                
                # New format: [transfer_patterns] section
                if config.has_section('transfer_patterns'):
                    transfer_patterns = dict(config.items('transfer_patterns'))
                    for key, pattern in transfer_patterns.items():
                        if 'outgoing' in key.lower() or 'out' in key.lower() or 'send' in key.lower():
                            outgoing_patterns[key] = pattern
                        elif 'incoming' in key.lower() or 'in' in key.lower() or 'receive' in key.lower():
                            incoming_patterns[key] = pattern
                
                # Old format: separate sections (for backward compatibility)
                if config.has_section('outgoing_patterns'):
                    outgoing_patterns.update(dict(config.items('outgoing_patterns')))
                if config.has_section('incoming_patterns'):
                    incoming_patterns.update(dict(config.items('incoming_patterns')))
                
                bank_config = BankConfig(
                    name=config.get('bank_info', 'name', fallback=bank_name),
                    file_patterns=[p.strip() for p in config.get('bank_info', 'file_patterns', fallback=bank_name).split(',')],
                    currency_primary=config.get('bank_info', 'currency_primary', fallback='USD'),
                    cashew_account=config.get('bank_info', 'cashew_account', fallback=bank_name),
                    outgoing_patterns=outgoing_patterns,
                    incoming_patterns=incoming_patterns,
                    categorization_rules=dict(config.items('categorization')) if config.has_section('categorization') else {},
                    description_cleaning_rules=dict(config.items('description_cleaning')) if config.has_section('description_cleaning') else {}
                )
                
                bank_configs[bank_name] = bank_config
                print(f"✅ Loaded {bank_name} config")
                
            except Exception as e:
                print(f"❌ Error loading {bank_name}.conf: {e}")
        
        return bank_configs
    
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
    
    def get_bank_config(self, bank_name: str) -> Optional[BankConfig]:
        """Get bank configuration by name"""
        return self.bank_configs.get(bank_name)
    
    def get_transfer_patterns(self, bank_name: str, direction: str) -> List[str]:
        """Get transfer patterns for a bank and direction (outgoing/incoming)"""
        config = self.bank_configs.get(bank_name)
        if not config:
            return []
        
        patterns = config.outgoing_patterns if direction == 'outgoing' else config.incoming_patterns
        
        # Return patterns as-is with {name} placeholder for flexible matching
        return list(patterns.values())
    
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
    
    def apply_description_cleaning(self, bank_name: str, description: str) -> str:
        """Apply bank-specific description cleaning rules"""
        config = self.bank_configs.get(bank_name)
        if not config or not config.description_cleaning_rules:
            return description
        
        cleaned_description = description
        
        for rule_name, rule_pattern in config.description_cleaning_rules.items():
            if '|' in rule_pattern:
                # Pattern|replacement format for regex replacement
                pattern, replacement = rule_pattern.split('|', 1)
                try:
                    cleaned_description = re.sub(pattern, replacement, cleaned_description)
                except re.error:
                    # If regex fails, treat as simple string replacement
                    cleaned_description = cleaned_description.replace(pattern, replacement)
            else:
                # Simple string replacement (for backward compatibility)
                cleaned_description = cleaned_description.replace(rule_pattern, '')
        
        return cleaned_description.strip()
    
    def extract_name_from_transfer_pattern(self, pattern: str, description: str) -> Optional[str]:
        """Extract name from transfer description using pattern with {name} placeholder"""
        if '{name}' not in pattern:
            return None
        
        # Convert pattern to regex by replacing {name} with capture group
        # Use more permissive capture group to get full names
        regex_pattern = re.escape(pattern).replace(r'\{name\}', r'([^,;.!?]+)')
        
        try:
            match = re.search(regex_pattern, description, re.IGNORECASE)
            if match:
                extracted_name = match.group(1).strip()
                # Clean up the extracted name (remove extra spaces, etc.)
                return ' '.join(extracted_name.split())
        except re.error:
            pass
        
        return None
    
    def list_configured_banks(self) -> List[str]:
        """Get list of configured bank names"""
        return list(self.bank_configs.keys())
