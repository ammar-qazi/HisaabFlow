"""
Bank configuration manager for loading and managing bank-specific configurations
"""
import os
import configparser
from typing import Dict, List, Optional, Any
import sys

class BankConfigManager:
    """Manages loading and caching of bank configurations"""
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            # Default to configs directory relative to backend
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.config_dir = os.path.join(os.path.dirname(backend_dir), 'configs')
        else:
            self.config_dir = config_dir
            
        self._bank_configs = {}
        self._detection_patterns = {}
        self.load_all_configs()
        
        print(f"🏗️ BankConfigManager initialized with config_dir: {self.config_dir}")
    
    def load_all_configs(self):
        """Load all bank configuration files"""
        print(f"📂 Loading bank configurations from: {self.config_dir}")
        
        if not os.path.exists(self.config_dir):
            print(f"❌ Config directory not found: {self.config_dir}")
            return
            
        config_files = [f for f in os.listdir(self.config_dir) if f.endswith('.conf')]
        print(f"📋 Found config files: {config_files}")
        
        for config_file in config_files:
            if config_file == 'app.conf':  # Skip app config
                continue
                
            bank_name = config_file.replace('.conf', '')
            config_path = os.path.join(self.config_dir, config_file)
            
            try:
                config = self._load_config_file(config_path)
                self._bank_configs[bank_name] = config
                
                # Extract detection patterns
                detection_info = self._extract_detection_info(config, bank_name)
                self._detection_patterns[bank_name] = detection_info
                
                print(f"✅ Loaded config for bank: {bank_name}")
                
            except Exception as e:
                print(f"❌ Error loading config {config_file}: {str(e)}")
    
    def _load_config_file(self, config_path: str) -> configparser.ConfigParser:
        """Load a single configuration file"""
        config = configparser.ConfigParser()
        config.optionxform = str  # Preserve case sensitivity
        config.read(config_path)
        return config
    
    def _extract_detection_info(self, config: configparser.ConfigParser, bank_name: str) -> Dict[str, Any]:
        """Extract detection patterns from configuration"""
        detection_info = {
            'bank_name': bank_name,
            'display_name': bank_name.title(),
            'content_signatures': [],
            'required_headers': [],
            'filename_patterns': [bank_name],
            'confidence_weight': 1.0
        }
        
        # Get bank info
        if config.has_section('bank_info'):
            bank_info = dict(config['bank_info'])
            detection_info['display_name'] = bank_info.get('name', bank_name).title()
            if 'file_patterns' in bank_info:
                patterns = bank_info['file_patterns'].split(',')
                detection_info['filename_patterns'] = [p.strip().lower() for p in patterns]
        
        # Add basic content signatures based on bank type
        if 'wise' in bank_name.lower():
            detection_info['content_signatures'] = [
                'TransferwiseId', 'Payment Reference', 'Exchange From', 'Exchange To'
            ]
            detection_info['required_headers'] = [
                'Date', 'Amount', 'Currency', 'Description'
            ]
        elif 'nayapay' in bank_name.lower():
            detection_info['content_signatures'] = [
                'NayaPay ID', 'NayaPay Account Number', 'Customer Name'
            ]
            detection_info['required_headers'] = [
                'TIMESTAMP', 'TYPE', 'DESCRIPTION', 'AMOUNT', 'BALANCE'
            ]
        
        print(f"🔍 Detection info for {bank_name}: {detection_info}")
        return detection_info
    
    def get_bank_config(self, bank_name: str) -> Optional[configparser.ConfigParser]:
        """Get configuration for a specific bank"""
        return self._bank_configs.get(bank_name)
    
    def get_detection_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get all detection patterns"""
        return self._detection_patterns
    
    def get_available_banks(self) -> List[str]:
        """Get list of available bank names"""
        return list(self._bank_configs.keys())
    
    def get_column_mapping(self, bank_name: str) -> Dict[str, str]:
        """Get column mapping for a specific bank"""
        config = self.get_bank_config(bank_name)
        if not config or not config.has_section('column_mapping'):
            return {}
            
        return dict(config['column_mapping'])
    
    def get_bank_info(self, bank_name: str) -> Dict[str, str]:
        """Get bank information"""
        config = self.get_bank_config(bank_name)
        if not config or not config.has_section('bank_info'):
            return {'name': bank_name}
            
        return dict(config['bank_info'])
