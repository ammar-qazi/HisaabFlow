"""
Bank detection module for dynamic bank identification
"""

from .bank_detector import BankDetector
from backend.infrastructure.config.unified_config_service import get_unified_config_service

# For backward compatibility, provide UnifiedConfigService as the default
def get_bank_config_manager():
    """Get the unified config service for bank detection"""
    return get_unified_config_service()

__all__ = ['BankDetector', 'get_bank_config_manager']
