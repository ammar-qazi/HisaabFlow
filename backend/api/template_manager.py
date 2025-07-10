"""
Configuration-based Template Manager
Replaces template files with configuration-based bank parsing
"""
import os
from fastapi import HTTPException
from typing import Dict, List, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.shared.config.unified_config_service import get_unified_config_service

try:
    from api.models import SaveTemplateRequest
except ImportError:
    # Fallback model definition
    class SaveTemplateRequest:
        def __init__(self, template_name, config):
            self.template_name = template_name
            self.config = config


class TemplateManager:
    """Manages bank configurations (no more template files)"""
    
    def __init__(self, template_dir: str = "../templates", config_dir: str = None):
        self.template_dir = template_dir  # Keep for backward compatibility
        
        # Use Nuitka-aware config detection if no config_dir provided
        if config_dir is None:
            from backend.infrastructure.csv_parsing.utils import get_config_dir_for_manager
            import os
            
            user_config_dir = get_config_dir_for_manager()
            if user_config_dir:
                self.config_dir = user_config_dir
            else:
                # Fallback to relative path
                self.config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "configs"))
        else:
            self.config_dir = config_dir
            
        self.config_service = get_unified_config_service(self.config_dir)
        
        print(f" TemplateManager (config-based) initialized")
        print(f"  Config dir: {config_dir}")
        print(f" Available configs: {self.config_service.list_banks()}")
        print(f" Templates are now configuration-based - no more .json files needed!")
    
    def save_template(self, request: SaveTemplateRequest) -> Dict[str, any]:
        """Save parsing template (now saves as config suggestion)"""
        print(f" Template save requested: {request.template_name}")
        print(f" Consider creating a config file instead: configs/{request.template_name.lower()}.conf")
        
        # For now, return success but suggest using configs
        return {
            "success": True,
            "message": f"Consider creating configs/{request.template_name.lower()}.conf instead of template",
            "suggestion": "Templates are replaced by configuration files"
        }
    
    def list_templates(self) -> Dict[str, List[str]]:
        """List available configurations (replaces templates)"""
        try:
            # Return available bank configurations
            available_configs = self.config_service.list_banks()
            
            # Also check for legacy template files
            legacy_templates = []
            if os.path.exists(self.template_dir):
                for file in os.listdir(self.template_dir):
                    if file.endswith('.json'):
                        template_name = file[:-5]  # Remove .json extension
                        legacy_templates.append(f"{template_name} (legacy)")
            
            all_available = available_configs + legacy_templates
            
            return {
                "templates": all_available,
                "message": "Configurations replace templates. Legacy templates shown for reference.",
                "available_configs": available_configs
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    def load_template(self, template_name: str) -> Dict[str, any]:
        """Load configuration (replaces template loading)"""
        print(f" Loading template/config: {template_name}")
        print(f" DEBUG: Input template_name = '{template_name}' (type: {type(template_name)})")
        
        try:
            # Find matching bank configuration
            print(f" DEBUG: Searching for matching bank config for: '{template_name}'")
            bank_name = self._find_matching_bank_config(template_name)
            print(f" DEBUG: Found bank_name = '{bank_name}'")
            
            if bank_name:
                print(f"[SUCCESS] Found matching bank config: {bank_name}")
                print(f" DEBUG: Getting config for bank_name = '{bank_name}'")
                config = self.config_service.get_bank_config(bank_name)
                print(f" DEBUG: Retrieved config = {config is not None}")
                
                # Convert to template-style format for backward compatibility
                template_style_config = self._convert_config_to_template_format(config)
                
                result = {
                    "success": True,
                    "config": template_style_config,
                    "source": "configuration",
                    "bank_name": bank_name,
                    "message": f"Loaded from config: {bank_name}.conf"
                }
                print(f" DEBUG: Returning template result with bank_name = '{result['bank_name']}'")
                return result
            
            # No matching config found
            print(f"[ERROR]  No matching config found for: {template_name}")
            available_configs = self.config_service.list_banks()
            print(f" Available configs: {available_configs}")
            
            raise HTTPException(
                status_code=404, 
                detail=f"No configuration found for '{template_name}'. Available configs: {available_configs}"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"[ERROR]  Config load error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error loading configuration: {str(e)}")
    
    def _find_matching_bank_config(self, template_name: str) -> Optional[str]:
        """Find matching bank configuration for template name"""
        print(f" DEBUG: _find_matching_bank_config called with: '{template_name}'")
        template_name_lower = template_name.lower()
        print(f" DEBUG: template_name_lower = '{template_name_lower}'")
        
        available_banks = self.config_service.list_banks()
        print(f" DEBUG: Available banks = {available_banks}")
        
        # Direct name match first
        print(f" DEBUG: Trying direct name match...")
        for bank_name in available_banks:
            print(f" DEBUG: Checking direct match: '{bank_name.lower()}' == '{template_name_lower}'")
            if bank_name.lower() == template_name_lower:
                print(f" DEBUG: Direct match found: {bank_name}")
                return bank_name
        
        # Pattern matching - check if template name contains bank patterns
        print(f" DEBUG: Trying pattern matching...")
        for bank_name in available_banks:
            bank_config = self.config_service.get_bank_config(bank_name)
            if bank_config:
                print(f" DEBUG: Bank {bank_name} patterns: {bank_config.detection_info.filename_patterns}")
                for pattern in bank_config.detection_info.filename_patterns:
                    print(f" DEBUG: Checking pattern: '{pattern.lower()}' in '{template_name_lower}'")
                    if pattern.lower() in template_name_lower:
                        print(f" DEBUG: Pattern match found: {bank_name} (pattern: {pattern})")
                        return bank_name
        
        # Fuzzy matching for common template names
        print(f" DEBUG: Trying fuzzy matching...")
        fuzzy_matches = {
            'wise': 'wise_usd',
            'transferwise': 'wise_usd', 
            'wise_universal': 'wise_usd',
            'nayapay': 'nayapay',
            'naya_pay': 'nayapay',
            'nayapay_universal': 'nayapay',
            'nayapay_cleaned': 'nayapay'
        }
        print(f" DEBUG: Fuzzy match dictionary: {fuzzy_matches}")
        
        for fuzzy_name, bank_name in fuzzy_matches.items():
            print(f" DEBUG: Checking fuzzy: '{fuzzy_name}' in '{template_name_lower}'")
            if fuzzy_name in template_name_lower:
                print(f" DEBUG: Fuzzy match found for '{fuzzy_name}' -> '{bank_name}'")
                if bank_name in available_banks:
                    print(f" DEBUG: Fuzzy match confirmed: {bank_name}")
                    return bank_name
                else:
                    print(f" DEBUG: Fuzzy match '{bank_name}' not in available banks")
        
        print(f" DEBUG: No match found for '{template_name}'")
        return None
    
    def _convert_config_to_template_format(self, config) -> Dict[str, any]:
        """Convert bank config to template-style format for backward compatibility"""
        if not config:
            return {}
        
        template_format = {
            "name": f"{config.name} Configuration",
            "bank_name": config.name,
            "description": f"Configuration-based settings for {config.name}",
            "csv_config": {
                "has_header": config.csv_config.has_header,
                "skip_rows": config.csv_config.skip_rows,
                "encoding": config.csv_config.encoding
            },
            "column_mapping": config.column_mapping,
            "account_mapping": config.account_mapping,
            "data_cleaning_config": {
                "enable_currency_addition": config.data_cleaning.enable_currency_addition,
                "multi_currency": config.data_cleaning.multi_currency,
                "numeric_amount_conversion": config.data_cleaning.numeric_amount_conversion,
                "date_standardization": config.data_cleaning.date_standardization,
                "remove_invalid_rows": config.data_cleaning.remove_invalid_rows,
                "default_currency": config.data_cleaning.default_currency
            },
            "date_formats": config.data_cleaning.date_formats,
            "amount_parsing": {
                "decimal_separator": config.data_cleaning.amount_decimal_separator,
                "thousand_separator": config.data_cleaning.amount_thousand_separator
            },
            "default_category_rules": config.default_category_rules,
            "version": "4.0",
            "source": "configuration_system"
        }
        
        return template_format
