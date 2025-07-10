"""
CSV Processing Domain Exceptions

Domain-specific exceptions for CSV processing operations.
These exceptions represent business rule violations and processing errors.
"""


class CSVProcessingError(Exception):
    """Base exception for CSV processing domain errors"""
    pass


class CSVParsingError(CSVProcessingError):
    """Raised when CSV parsing fails"""
    pass


class CSVPreprocessingError(CSVProcessingError):
    """Raised when CSV preprocessing fails"""
    pass


class EncodingDetectionError(CSVProcessingError):
    """Raised when encoding detection fails"""
    pass


class BankDetectionError(CSVProcessingError):
    """Raised when bank detection fails"""
    pass


class HeaderValidationError(CSVProcessingError):
    """Raised when header validation fails"""
    pass