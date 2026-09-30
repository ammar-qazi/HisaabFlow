"""
API Facade for Unified Config Service
Maintains backward compatibility with existing API config manager interface
"""
from typing import List
from .unified_config_service import get_unified_config_service

# Mock classes for compatibility
class APIConfigFacade:
    """
    Facade that adapts UnifiedConfigService to the existing API ConfigManager interface
    Maintains 100% backward compatibility during migration
    """
    
    def __init__(self, config_dir: str = None):
        self.unified_service = get_unified_config_service(config_dir)
    
    # Additional methods for backward compatibility with current API endpoints
    def list_configured_banks(self) -> List[str]:
        """Get list of configured bank names (backward compatibility)"""
        return self.unified_service.list_banks()
    
    def get_bank_config(self, bank_name: str):
        """Get bank configuration (backward compatibility)"""
        return self.unified_service.get_bank_config(bank_name)