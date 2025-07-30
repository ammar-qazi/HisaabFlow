"""
Infrastructure adapters for CSV processing

These adapters implement the domain interfaces using the concrete infrastructure implementations.
They serve as the bridge between the domain layer and infrastructure layer.
"""

from typing import Dict, Any, Optional
from backend.core.csv_processing.interfaces import (
    CSVParserPort, CSVPreprocessorPort, EncodingDetectorPort, 
    DialectDetectorPort, StructureAnalyzerPort
)
from .unified_parser import UnifiedCSVParser
from .encoding_detector import EncodingDetector
from .dialect_detector import DialectDetector
from .structure_analyzer import StructureAnalyzer
from ..preprocessing.csv_preprocessor import CSVPreprocessor


class UnifiedCSVParserAdapter(CSVParserPort):
    """Adapter for UnifiedCSVParser infrastructure component"""
    
    def __init__(self):
        self._parser = UnifiedCSVParser()
    
    def parse_csv(self, file_path: str, encoding: Optional[str] = None, 
                  header_row: int = None, start_row: int = None, 
                  max_rows: int = None) -> Dict[str, Any]:
        """Parse CSV file using UnifiedCSVParser infrastructure"""
        return self._parser.parse_csv(
            file_path=file_path,
            encoding=encoding,
            header_row=header_row,
            start_row=start_row,
            max_rows=max_rows
        )


class CSVPreprocessorAdapter(CSVPreprocessorPort):
    """Adapter for CSVPreprocessor infrastructure component"""
    
    def __init__(self):
        self._preprocessor = CSVPreprocessor()
    
    def preprocess_csv(self, file_path: str, bank_type: str, 
                      encoding: str, skip_empty_row_removal: bool = False) -> Dict[str, Any]:
        """Preprocess CSV file using CSVPreprocessor infrastructure"""
        return self._preprocessor.preprocess_csv(
            file_path=file_path,
            bank_type=bank_type,
            encoding=encoding,
            skip_empty_row_removal=skip_empty_row_removal
        )


class EncodingDetectorAdapter(EncodingDetectorPort):
    """Adapter for EncodingDetector infrastructure component"""
    
    def __init__(self):
        self._detector = EncodingDetector()
    
    def detect_encoding(self, file_path: str) -> Dict[str, Any]:
        """Detect file encoding using EncodingDetector infrastructure"""
        return self._detector.detect_encoding(file_path)


class DialectDetectorAdapter(DialectDetectorPort):
    """Adapter for DialectDetector infrastructure component"""
    
    def __init__(self):
        self._detector = DialectDetector()
    
    def detect_dialect(self, file_path: str, encoding: str) -> Dict[str, Any]:
        """Detect CSV dialect using DialectDetector infrastructure"""
        return self._detector.detect_dialect(file_path, encoding)


class StructureAnalyzerAdapter(StructureAnalyzerPort):
    """Adapter for StructureAnalyzer infrastructure component"""
    
    def __init__(self):
        self._analyzer = StructureAnalyzer()
    
    def analyze_structure(self, file_path: str, encoding: str) -> Dict[str, Any]:
        """Analyze CSV structure using StructureAnalyzer infrastructure"""
        return self._analyzer.analyze_structure(file_path, encoding)