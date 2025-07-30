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


class NoHeadersFoundError(CSVParsingError):
    """Raised when CSV file has no detectable headers"""
    
    def __init__(self, file_path: str, message: str = None):
        self.file_path = file_path
        default_message = f"No headers detected in CSV file: {file_path}"
        super().__init__(message or default_message, file_path)


class HeaderlessCSVDetected(Exception):
    """Not an error - indicates CSV has data but no headers (informational exception)"""
    
    def __init__(self, file_path: str, suggested_columns: list, total_columns: int = None):
        self.file_path = file_path
        self.suggested_columns = suggested_columns
        self.total_columns = total_columns or len(suggested_columns)
        message = f"Headerless CSV detected: {file_path} ({self.total_columns} columns)"
        super().__init__(message)
