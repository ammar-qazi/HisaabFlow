"""
Enhanced CSV Parser - Backward compatibility wrapper
This file provides backward compatibility for existing imports while using the new modular structure.
"""

import sys
import os

# Add current directory to path for relative imports
sys.path.insert(0, os.path.dirname(__file__))

# Import the modular version
from csv_parsing.csv_parser_core import EnhancedCSVParser

# Re-export for backward compatibility
__all__ = ['EnhancedCSVParser']

# Print migration info (only in debug mode)
if __name__ == "__main__":
    print("✅ Enhanced CSV Parser: Using new modular architecture (backward compatible)")
