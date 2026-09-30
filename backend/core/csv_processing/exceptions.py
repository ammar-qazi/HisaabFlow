"""
CSV Processing Domain Exceptions

Domain-specific exceptions for CSV processing operations.
These exceptions represent business rule violations and processing errors.
"""


class CSVProcessingError(Exception):
    """Base exception for CSV processing domain errors"""


class CSVParsingError(CSVProcessingError):
    """Raised when CSV parsing fails"""


class CSVPreprocessingError(CSVProcessingError):
    """Raised when CSV preprocessing fails"""


class EncodingDetectionError(CSVProcessingError):
    """Raised when encoding detection fails"""


class BankDetectionError(CSVProcessingError):
    """Raised when bank detection fails"""


class HeaderValidationError(CSVProcessingError):
    """Raised when header validation fails"""
