"""
Backward compatibility wrapper for the refactored TransferDetector
Maintains the same API as the original transfer_detector_enhanced_ammar.py
"""

# Import the new modular TransferDetector
from .transfer_detection import TransferDetector

# Re-export for backward compatibility
__all__ = ['TransferDetector']

# This file maintains the same interface as the original 858-line file
# but now uses the modular implementation under the hood
