"""
Unified CSV Parser Module - Single source of truth for CSV parsing

This module provides a unified interface for parsing all CSV formats with automatic
detection of encoding, dialect, and structure.

Public Interface:
    UnifiedCSVParser: Main parser class with auto-detection
    CSVParsingError: Custom exception for parsing issues
    
Component Classes (for advanced usage):
    EncodingDetector: File encoding detection
    DialectDetector: CSV dialect detection
    ParsingStrategies: Multiple parsing approaches
    DataProcessor: Raw data processing
    StructureAnalyzer: CSV structure analysis
"""

from .unified_parser import UnifiedCSVParser
from .exceptions import CSVParsingError, EncodingDetectionError, DialectDetectionError, StructureDetectionError, DataExtractionError
from .encoding_detector import EncodingDetector
from .dialect_detector import DialectDetector
from .parsing_strategies import ParsingStrategies
from .data_processor import DataProcessor
from .structure_analyzer import StructureAnalyzer

__all__ = [
    'UnifiedCSVParser',
    'CSVParsingError', 
    'EncodingDetectionError',
    'DialectDetectionError',
    'StructureDetectionError',
    'DataExtractionError',
    'EncodingDetector',
    'DialectDetector', 
    'ParsingStrategies',
    'DataProcessor',
    'StructureAnalyzer'
]

__version__ = "1.0.0"
