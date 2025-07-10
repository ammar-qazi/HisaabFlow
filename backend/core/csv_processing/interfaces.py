"""
CSV Processing Domain Interfaces (Ports)

These interfaces define the contracts for CSV processing operations.
Infrastructure implementations will adapt to these interfaces.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple


class CSVParserPort(ABC):
    """Domain interface for CSV parsing operations"""
    
    @abstractmethod
    def parse_csv(self, file_path: str, encoding: str = None, 
                  header_row: int = None, start_row: int = None, 
                  max_rows: int = None) -> Dict[str, Any]:
        """Parse CSV file and return structured data"""
        pass


class CSVPreprocessorPort(ABC):
    """Domain interface for CSV preprocessing operations"""
    
    @abstractmethod
    def preprocess_csv(self, file_path: str, bank_type: str, 
                      encoding: str, skip_empty_row_removal: bool = False) -> Dict[str, Any]:
        """Preprocess CSV file to handle format issues"""
        pass


class EncodingDetectorPort(ABC):
    """Domain interface for encoding detection operations"""
    
    @abstractmethod
    def detect_encoding(self, file_path: str) -> Dict[str, Any]:
        """Detect file encoding and return detection result"""
        pass


class DialectDetectorPort(ABC):
    """Domain interface for CSV dialect detection operations"""
    
    @abstractmethod
    def detect_dialect(self, file_path: str, encoding: str) -> Dict[str, Any]:
        """Detect CSV dialect (delimiter, quoting, etc.)"""
        pass


class StructureAnalyzerPort(ABC):
    """Domain interface for CSV structure analysis operations"""
    
    @abstractmethod
    def analyze_structure(self, file_path: str, encoding: str) -> Dict[str, Any]:
        """Analyze CSV structure and return analysis result"""
        pass