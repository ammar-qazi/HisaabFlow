"""
Configuration data classes and structures
"""
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class CSVConfig:
    """CSV parsing configuration from config file"""
    has_header: bool = True
    skip_rows: int = 0
    date_format: str = "%Y-%m-%d"
    encoding: str = "utf-8"
    start_row: Optional[int] = None
    end_row: Optional[int] = None
    start_col: Optional[int] = None
    end_col: Optional[int] = None


@dataclass
class DataCleaningConfig:
    """Data cleaning configuration from config file"""
    enable_currency_addition: bool = False
    multi_currency: bool = False
    numeric_amount_conversion: bool = True
    date_standardization: bool = True
    remove_invalid_rows: bool = True
    default_currency: str = "USD"


@dataclass
class AmountParsingConfig:
    """Amount parsing configuration from config file"""
    format: str = "numeric"
    decimal_separator: str = "."
    thousand_separator: str = ","
    currency_symbol: str = "$"


@dataclass
class EnhancedBankConfig:
    """Enhanced bank configuration with CSV parsing support"""
    # Basic bank info
    name: str
    file_patterns: List[str]
    currency_primary: str
    cashew_account: str
    
    # CSV parsing configuration
    csv_config: CSVConfig
    column_mapping: Dict[str, str]
    account_mapping: Dict[str, str]
    data_cleaning: DataCleaningConfig
    date_formats: List[str]
    amount_parsing: AmountParsingConfig
    
    # Transfer detection
    outgoing_patterns: Dict[str, str]
    incoming_patterns: Dict[str, str]
    categorization_rules: Dict[str, str]
    
    # Default rules
    default_category_rules: Dict[str, str]
