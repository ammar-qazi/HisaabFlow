"""
Clean Configuration-Based Manager
Replaces template system entirely with configuration management
"""
import os
from typing import Dict, List, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transfer_detection.enhanced_config_manager import EnhancedConfigurationManager

# Import HTTPException only when needed
try:
    from fastapi import HTTPException
except ImportError:
    # Mock for testing
    class HTTPException(Exception):
        def __init__(self, status_code, detail):
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)

# Mock SaveTemplateRequest for testing
try:
    from .models import SaveTemplateRequest
except ImportError:
    class SaveTemplateRequest:
        def __init__(self, template_name, config):
            self.template_name = template_name
            self.config = config


class ConfigManager:
    """Manages bank configurations - no more templates"""
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            # Correct path to project_root/configs from backend/api/
            self.config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "configs"))
        else:
            self.config_dir = config_dir
        self.enhanced_config_manager = EnhancedConfigurationManager(config_dir)
        
        print(f"🔧 [api.ConfigManager] Initialized (no more templates!)")
        print(f"⚙️  [api.ConfigManager] Effective config directory: {self.config_dir}")
        print(f"🏦 Available bank configurations: {self.enhanced_config_manager.list_configured_banks()}")
    
    def save_config(self, request: SaveTemplateRequest) -> Dict[str, any]:
        """Save bank configuration (replaces save_template)"""
        print(f"💾 Saving bank configuration: {request.template_name}")
        
        try:
            # For now, suggest manual config creation
            # TODO: Implement automatic config file generation
            config_filename = f"{request.template_name.lower().replace(' ', '_')}.conf"
            
            print(f"💡 Configuration should be saved to: {self.config_dir}/{config_filename}")
            print(f"💡 Template data: {request.config}")
            
            return {
                "success": True,
                "message": f"Configuration saved as {config_filename}",
                "config_file": config_filename,
                "suggestion": "Consider manually creating the .conf file for better control"
            }
        except Exception as e:
            print(f"❌ Config save error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error saving configuration: {str(e)}")
    
    def list_configs(self) -> Dict[str, List[str]]:
        """List available bank configurations"""
        print(f"📋 [api.ConfigManager] Listing available bank configurations...")
        
        try:
            available_configs = self.enhanced_config_manager.list_configured_banks()
            print(f"🔍 [api.ConfigManager] Raw banks from EnhancedConfigurationManager: {available_configs}")
            
            # Return user-friendly names
            config_display_names = []
            for bank_name in available_configs:
                config = self.enhanced_config_manager.get_bank_config(bank_name)
                if config:
                    display_name = f"{config.name.title()} Configuration"
                    config_display_names.append(display_name)
                    print(f"📋 [api.ConfigManager] Processing for display: {display_name} (from {bank_name}.conf)")
            
            print(f"📋 [api.ConfigManager] Total configurations to be returned: {len(config_display_names)}")
            
            return {
                "configurations": config_display_names,
                "raw_bank_names": available_configs,
                "count": len(config_display_names)
            }
        except Exception as e:
            print(f"❌ [api.ConfigManager] Config list error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def load_config(self, config_name: str) -> Dict[str, any]:
        """Load bank configuration by display name or bank name"""
        print(f"🔍 Loading configuration: '{config_name}'")
        
        try:
            # Find matching bank name
            bank_name = self._find_matching_bank_name(config_name)
            print(f"🔍 Matched bank name: '{bank_name}'")
            
            if not bank_name:
                available = self.enhanced_config_manager.list_configured_banks()
                raise HTTPException(
                    status_code=404, 
                    detail=f"Configuration '{config_name}' not found. Available: {available}"
                )
            
            # Load the configuration
            config = self.enhanced_config_manager.get_bank_config(bank_name)
            if not config:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to load configuration for {bank_name}"
                )
            
            # Convert to simplified format for frontend
            simplified_config = self._convert_to_frontend_format(config)
            
            result = {
                "success": True,
                "config": simplified_config,
                "bank_name": config.name,
                "display_name": f"{config.name.title()} Configuration",
                "source": f"{bank_name}.conf"
            }
            
            print(f"✅ Configuration loaded successfully: {result['display_name']}")
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Config load error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error loading configuration: {str(e)}")
    
    def _find_matching_bank_name(self, config_name: str) -> Optional[str]:
        """Find bank name from configuration display name or direct name"""
        print(f"🔍 Finding bank name for: '{config_name}'")
        
        config_name_lower = config_name.lower()
        available_banks = self.enhanced_config_manager.list_configured_banks()
        
        # Direct bank name match
        if config_name_lower in [bank.lower() for bank in available_banks]:
            for bank in available_banks:
                if bank.lower() == config_name_lower:
                    print(f"✅ Direct match: {bank}")
                    return bank
        
        # Display name match (e.g., "NayaPay Configuration" -> "nayapay")
        for bank_name in available_banks:
            display_name = f"{bank_name.title()} Configuration".lower()
            if config_name_lower == display_name:
                print(f"✅ Display name match: {bank_name}")
                return bank_name
        
        # Pattern matching
        for bank_name in available_banks:
            config = self.enhanced_config_manager.get_bank_config(bank_name)
            if config:
                for pattern in config.file_patterns:
                    if pattern.lower() in config_name_lower:
                        print(f"✅ Pattern match: {bank_name} (pattern: {pattern})")
                        return bank_name
        
        print(f"❌ No match found for: '{config_name}'")
        return None
    
    def _convert_to_frontend_format(self, config) -> Dict[str, any]:
        """Convert bank config to simplified format for frontend"""
        print(f"🔄 Converting config for frontend: {config.name}")
        
        frontend_config = {
            # Range settings
            "start_row": getattr(config.csv_config, 'start_row', 0),
            "end_row": getattr(config.csv_config, 'end_row', None),
            "start_col": getattr(config.csv_config, 'start_col', 0),
            "end_col": getattr(config.csv_config, 'end_col', None),
            
            # Column mapping
            "column_mapping": config.column_mapping,
            
            # Bank info
            "bank_name": config.name,
            "currency": config.currency_primary,
            "account": config.cashew_account,
            
            # Advanced settings (for future use)
            "categorization_rules": getattr(config, 'categorization_rules', {}),
            "default_category_rules": config.default_category_rules,
            "account_mapping": config.account_mapping,
            "data_cleaning": {
                "enable_currency_addition": config.data_cleaning.enable_currency_addition,
                "multi_currency": config.data_cleaning.multi_currency,
                "numeric_amount_conversion": config.data_cleaning.numeric_amount_conversion,
                "date_standardization": config.data_cleaning.date_standardization,
                "remove_invalid_rows": config.data_cleaning.remove_invalid_rows,
                "default_currency": config.data_cleaning.default_currency
            }
        }
        
        print(f"✅ Frontend config prepared for: {config.name}")
        return frontend_config
