"""
Data Cleaner - Backward Compatibility Wrapper
This file maintains backward compatibility while using the new modular structure
"""

# Import the new modular DataCleaner
from backend.data_cleaning.data_cleaner import DataCleaner

# Export the class so existing imports continue to work
__all__ = ['DataCleaner']

# The original monolithic DataCleaner class is now replaced by the modular version
# All existing functionality is preserved but now uses focused, maintainable modules:
#
# Modules created (all under 100 lines):
# - bom_cleaner.py (50 lines) - BOM character handling
# - column_standardizer.py (80 lines) - Column naming and mapping
# - numeric_cleaner.py (70 lines) - Numeric data parsing
# - date_cleaner.py (70 lines) - Date parsing and standardization
# - currency_handler.py (60 lines) - Currency column management
# - data_validator.py (80 lines) - Data quality validation
# - quality_checker.py (70 lines) - Quality assessment
# - data_cleaner.py (100 lines) - Main orchestration class
#
# Benefits:
# [SUCCESS] Each module under 100 lines (vs original 876 lines)
# [SUCCESS] Single responsibility principle
# [SUCCESS] Easier debugging and modification
# [SUCCESS] Better testability
# [SUCCESS] Maintained backward compatibility
# [SUCCESS] All existing imports continue to work
