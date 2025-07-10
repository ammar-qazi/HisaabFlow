"""
Dependency Injection Configuration

This module provides factory functions for creating service instances with their dependencies.
It follows the dependency injection pattern for clean architecture.
"""

from backend.core.csv_processing.csv_processing_service import CSVProcessingService
from backend.infrastructure.csv_parsing.adapters import (
    UnifiedCSVParserAdapter, CSVPreprocessorAdapter, EncodingDetectorAdapter
)


def create_csv_processing_service() -> CSVProcessingService:
    """
    Factory function to create CSVProcessingService with injected dependencies
    
    Returns:
        CSVProcessingService: Configured service instance
    """
    # Create infrastructure adapters
    csv_parser = UnifiedCSVParserAdapter()
    csv_preprocessor = CSVPreprocessorAdapter()
    encoding_detector = EncodingDetectorAdapter()
    
    # Inject dependencies into service
    return CSVProcessingService(
        csv_parser=csv_parser,
        csv_preprocessor=csv_preprocessor,
        encoding_detector=encoding_detector
    )


# Singleton instance for backward compatibility
_csv_processing_service = None


def get_csv_processing_service() -> CSVProcessingService:
    """
    Get singleton instance of CSVProcessingService
    
    Returns:
        CSVProcessingService: Singleton service instance
    """
    global _csv_processing_service
    if _csv_processing_service is None:
        _csv_processing_service = create_csv_processing_service()
    return _csv_processing_service