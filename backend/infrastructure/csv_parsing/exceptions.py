"""
Custom exceptions for CSV parsing operations
"""

class CSVParsingError(Exception):
    """Base exception for CSV parsing failures"""
    def __init__(self, message: str, file_path: str = None, line_number: int = None):
        self.file_path = file_path
        self.line_number = line_number
        super().__init__(message)


class EncodingDetectionError(CSVParsingError):
    """Exception raised when file encoding cannot be detected"""
    pass


class DialectDetectionError(CSVParsingError):
    """Exception raised when CSV dialect cannot be determined"""
    pass


class StructureDetectionError(CSVParsingError):
    """Exception raised when CSV structure cannot be analyzed"""
    pass


class DataExtractionError(CSVParsingError):
    """Exception raised during data extraction phase"""
    pass
