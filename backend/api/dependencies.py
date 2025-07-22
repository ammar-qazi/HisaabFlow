"""
Dependency injection factory functions for FastAPI endpoints
"""
from functools import lru_cache
from backend.services.preview_service import PreviewService
from backend.services.parsing_service import ParsingService
from backend.services.multi_csv_service import MultiCSVService
from backend.services.transformation_service import TransformationService
from backend.services.export_service import ExportService
from backend.infrastructure.config.api_facade import APIConfigFacade


from backend.infrastructure.config.unified_config_service import get_unified_config_service

def get_preview_service() -> PreviewService:
    """Get a new PreviewService instance with the latest config"""
    config_service = get_unified_config_service()
    config_service.reload_all_configs()
    return PreviewService(config_service)


@lru_cache()
def get_parsing_service() -> ParsingService:
    """Get singleton ParsingService instance"""
    return ParsingService()


@lru_cache()
def get_multi_csv_service() -> MultiCSVService:
    """Get singleton MultiCSVService instance"""
    return MultiCSVService()


@lru_cache()
def get_transformation_service() -> TransformationService:
    """Get singleton TransformationService instance"""
    return TransformationService()


@lru_cache()
def get_export_service() -> ExportService:
    """Get singleton ExportService instance"""
    return ExportService()


@lru_cache()
def get_config_manager() -> APIConfigFacade:
    """Get singleton APIConfigFacade instance with proper path detection"""
    from backend.infrastructure.csv_parsing.utils import get_config_dir_for_manager
    import os
    
    user_config_dir = get_config_dir_for_manager()
    if user_config_dir:
        config_dir = user_config_dir
    else:
        # Fallback to relative path
        config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "configs"))
    
    return APIConfigFacade(config_dir)