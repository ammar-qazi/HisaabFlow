"""
Data Cleaning Package
Modular data cleaning components for bank statement processing

This package provides focused, single-responsibility modules for:
- BOM character handling (proper encoding approach recommended)
- Column standardization and mapping
- Numeric data cleaning and parsing
- Date parsing and standardization
- Currency column management
- Data validation and filtering
- Quality assessment and reporting
"""

from .data_cleaner import DataCleaner
from .bom_cleaner import BOMCleaner
from .column_standardizer import ColumnStandardizer
from .numeric_cleaner import NumericCleaner
from .date_cleaner import DateCleaner
from .currency_handler import CurrencyHandler
from .data_validator import DataValidator
from .quality_checker import QualityChecker

__all__ = [
    'DataCleaner',
    'BOMCleaner',
    'ColumnStandardizer', 
    'NumericCleaner',
    'DateCleaner',
    'CurrencyHandler',
    'DataValidator',
    'QualityChecker'
]

__version__ = '1.0.0'
