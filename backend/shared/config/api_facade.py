"""
API Facade for Unified Config Service
Maintains backward compatibility with existing API config manager interface
"""
from typing import Dict, List, Optional, Any
from .unified_config_service import get_unified_config_service

# Mock classes for compatibility
class SaveTemplateRequest:
    def __init__(self, template_name: str, config: dict):
        self.template_name = template_name
        self.config = config


class APIConfigFacade:
    """
    Facade that adapts UnifiedConfigService to the existing API ConfigManager interface
    Maintains 100% backward compatibility during migration
    """
    
    def __init__(self, config_dir: str = None):
        self.unified_service = get_unified_config_service(config_dir)
    
    def save_config(self, request: SaveTemplateRequest) -> Dict[str, Any]:
        """Save bank configuration (API format)"""
        try:
            success = self.unified_service.save_bank_config(
                request.template_name, 
                request.config
            )
            
            if success:
                return {
                    "success": True,
                    "message": f"Configuration '{request.template_name}' saved successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to save configuration '{request.template_name}'"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_configs(self) -> Dict[str, List[str]]:
        """List available bank configurations (API format)"""
        try:
            banks = self.unified_service.list_banks()
            # Convert to API format with .conf extension
            configurations = [f"{bank}.conf" for bank in banks]
            
            return {
                "success": True,
                "configurations": configurations
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "configurations": []
            }
    
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """Load bank configuration (API format)"""
        try:
            # Remove .conf extension if present
            bank_name = config_name.replace('.conf', '')
            
            bank_config = self.unified_service.get_bank_config(bank_name)
            if not bank_config:
                available_banks = self.unified_service.list_banks()
                return {
                    "success": False,
                    "error": f"Configuration '{config_name}' not found. Available: {available_banks}"
                }
            
            # Convert to API format
            config_data = self._convert_to_frontend_format(bank_config)
            
            return {
                "success": True,
                "bank_name": bank_config.display_name,
                "config": config_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _convert_to_frontend_format(self, bank_config) -> Dict[str, Any]:
        """Convert UnifiedBankConfig to frontend format"""
        return {
            "bank_info": {
                "bank_name": bank_config.name,
                "display_name": bank_config.display_name,
                "file_patterns": bank_config.detection_info.filename_patterns,
                "detection_content_signatures": bank_config.detection_info.content_signatures,
                "expected_headers": bank_config.detection_info.required_headers,
                "confidence_weight": bank_config.detection_info.confidence_weight
            },
            "csv_config": {
                "delimiter": bank_config.csv_config.delimiter,
                "quote_char": bank_config.csv_config.quote_char,
                "encoding": bank_config.csv_config.encoding,
                "has_header": bank_config.csv_config.has_header,
                "skip_rows": bank_config.csv_config.skip_rows
            },
            "column_mapping": bank_config.column_mapping,
            "account_mapping": bank_config.account_mapping,
            "data_cleaning": {
                "currency_symbols": bank_config.data_cleaning.currency_symbols,
                "date_formats": bank_config.data_cleaning.date_formats,
                "amount_decimal_separator": bank_config.data_cleaning.amount_decimal_separator,
                "amount_thousand_separator": bank_config.data_cleaning.amount_thousand_separator,
                "description_cleaning_rules": bank_config.data_cleaning.description_cleaning_rules
            },
            "transfer_patterns": {
                "outgoing_patterns": bank_config.outgoing_patterns,
                "incoming_patterns": bank_config.incoming_patterns
            },
            "categorization": bank_config.categorization_rules,
            "default_category_rules": bank_config.default_category_rules,
            "conditional_overrides": bank_config.conditional_overrides
        }
    
    # Additional methods for backward compatibility with current API endpoints
    def list_configured_banks(self) -> List[str]:
        """Get list of configured bank names (backward compatibility)"""
        return self.unified_service.list_banks()
    
    def get_bank_config(self, bank_name: str):
        """Get bank configuration (backward compatibility)"""
        return self.unified_service.get_bank_config(bank_name)