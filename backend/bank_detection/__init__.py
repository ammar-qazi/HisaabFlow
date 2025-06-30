"""
Bank detection module for dynamic bank identification
"""

from .bank_detector import BankDetector
from ..shared.config.bank_detection_facade import BankDetectionFacade

# For backward compatibility, alias the facade as BankConfigManager
BankConfigManager = BankDetectionFacade

__all__ = ['BankDetector', 'BankConfigManager', 'BankDetectionFacade']
