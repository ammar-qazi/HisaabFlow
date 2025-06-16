"""
Configuration-based Bank Rules System
Manages loading and accessing bank configurations from .conf files
"""
import configparser
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
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
    conditional_description_overrides: List[Dict[str, Any]]


class ConfigurationManager:
    """Manages loading and accessing bank configurations"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.app_config = self._load_app_config()
        self.family_configs: Dict[str, configparser.ConfigParser] = self._load_family_configs()
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
    
    def _load_family_configs(self) -> Dict[str, configparser.ConfigParser]:
        """Load family configuration files (e.g., wise_family.conf)"""
        family_configs = {}
        
        for config_file in self.config_dir.glob("*_family.conf"):
            family_name = config_file.stem.replace('_family', '')
            config = configparser.ConfigParser()
            config.read(config_file)
            
            family_configs[family_name] = config
            print(f"✅ Loaded {family_name}_family.conf")
        
        return family_configs
    
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
                
                # Load conditional description overrides
                conditional_overrides = []
                for section_name in config.sections():
                    if section_name.startswith('conditional_override_'):
                        rule_details = dict(config.items(section_name))
                        # Convert numeric fields if they exist
                        for k_num in ['if_amount_min', 'if_amount_max', 'if_amount_equals', 'if_amount_less_than', 'if_amount_greater_than']:
                            if k_num in rule_details:
                                try:
                                    rule_details[k_num] = float(rule_details[k_num])
                                except ValueError:
                                    print(f"⚠️  Warning: Invalid number for {k_num} in rule {section_name} for {bank_name}. Skipping this condition field.")
                                    del rule_details[k_num] # Remove invalid field
                        conditional_overrides.append(rule_details)

                
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
                    description_cleaning_rules=dict(config.items('description_cleaning')) if config.has_section('description_cleaning') else {},
                    conditional_description_overrides=conditional_overrides
                )
                
                bank_configs[bank_name] = bank_config
                print(f"✅ Loaded {bank_name} config")
                
            except Exception as e:
                print(f"❌ Error loading {bank_name}.conf: {e}")
        
        return bank_configs
    
    def get_date_tolerance(self) -> int:
        """Get date tolerance in hours"""
        return self.app_config.getint('general', 'date_tolerance_hours', fallback=72)
    
    def get_user_name(self) -> str:
        """Get user name for transfer detection"""
        return self.app_config.get('general', 'user_name', fallback='Your Name Here')
    
    def get_confidence_threshold(self) -> float:
        """Get minimum confidence threshold"""
        return self.app_config.getfloat('transfer_detection', 'confidence_threshold', fallback=0.7)
    
    def get_default_transfer_category(self) -> str:
        """Gets the default category to be applied to transfer pairs from app.conf."""
        if self.app_config and self.app_config.has_section('transfer_categorization'):
            return self.app_config.get('transfer_categorization', 'default_pair_category', fallback='Balance Correction')
        # Fallback if the section or key is missing
        return 'Balance Correction'

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
        """Get category for a merchant based on family and bank configuration"""
        merchant_lower = merchant.lower()
        
        # Step 1: Check family categorization rules first
        family_name = self._get_family_name(bank_name)
        if family_name and family_name in self.family_configs:
            family_config = self.family_configs[family_name]
            if family_config.has_section('categorization'):
                family_rules = dict(family_config.items('categorization'))
                for merchant_pattern, category in family_rules.items():
                    if re.search(merchant_pattern, merchant_lower, re.IGNORECASE):
                        return category
        
        # Step 2: Check bank-specific categorization rules (can override family)
        config = self.bank_configs.get(bank_name)
        if config:
            for merchant_pattern, category in config.categorization_rules.items():
                if re.search(merchant_pattern, merchant_lower, re.IGNORECASE):
                    return category
        
        return None
    
    def apply_description_cleaning(self, bank_name: str, description: str) -> str:
        """Apply family and bank-specific description cleaning rules"""
        cleaned_description = description
        
        # Step 1: Apply family rules first (e.g., wise_family.conf)
        family_name = self._get_family_name(bank_name)
        if family_name and family_name in self.family_configs:
            family_config = self.family_configs[family_name]
            if family_config.has_section('description_cleaning'):
                family_rules = dict(family_config.items('description_cleaning'))
                cleaned_description = self._apply_cleaning_rules(cleaned_description, family_rules)
        
        # Step 2: Apply bank-specific rules (can override family rules)
        config = self.bank_configs.get(bank_name)
        if config and config.description_cleaning_rules:
            cleaned_description = self._apply_cleaning_rules(cleaned_description, config.description_cleaning_rules)
        
        return cleaned_description.strip()
    
    def _get_family_name(self, bank_name: str) -> Optional[str]:
        """Determine family name for a bank (e.g., wise_usd -> wise)"""
        if bank_name.startswith('wise_'):
            return 'wise'
        # Add other families as needed
        return None
    
    def _apply_cleaning_rules(self, description: str, rules: Dict[str, str]) -> str:
        """Apply a set of cleaning rules to description"""
        cleaned_description = description
        
        for rule_name, rule_pattern in rules.items():
            if '|' in rule_pattern:
                # Pattern|replacement format for regex replacement
                pattern, replacement = rule_pattern.rsplit('|', 1)
                pattern = pattern.strip()
                replacement = replacement.strip()
                try:
                    cleaned_description = re.sub(pattern, replacement, cleaned_description, flags=re.IGNORECASE)
                except re.error:
                    # If regex fails, treat as simple string replacement
                    cleaned_description = re.sub(re.escape(pattern), replacement, cleaned_description, flags=re.IGNORECASE)
            else:
                # Simple string replacement (for backward compatibility)
                cleaned_description = cleaned_description.replace(rule_pattern, '')
        
        return cleaned_description
    
    def extract_name_from_transfer_pattern(self, pattern: str, description: str) -> Optional[str]:
        """Extract name from transfer description using pattern with {name} placeholder"""
        if '{name}' not in pattern:
            return None

        # Find the placeholder (e.g., {name}, {user_name})
        placeholder_match = re.search(r'\{(\w+)\}', pattern)
        if not placeholder_match:
            return None # No placeholder found in the expected format
        
        placeholder_text = placeholder_match.group(0) # e.g., "{name}" or "{user_name}"
        
        # Convert pattern to regex by replacing the dynamic placeholder with a capture group
        # Adjusted to be less greedy and stop before common delimiters like '|' or ' - '
        regex_pattern = re.escape(pattern).replace(re.escape(placeholder_text), r'([^,;.!?\|-]+)')
        
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
