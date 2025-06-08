"""
Pydantic models for API requests and responses
Centralized definition of all data models used by the FastAPI endpoints
"""
from pydantic import BaseModel
from typing import Dict, List, Optional, Any


class PreviewRequest(BaseModel):
    file_path: str
    encoding: str = "utf-8"


class ParseRangeRequest(BaseModel):
    start_row: int
    end_row: Optional[int] = None
    start_col: int = 0
    end_col: Optional[int] = None
    encoding: str = "utf-8"
    enable_cleaning: bool = True


class TransformRequest(BaseModel):
    data: List[Dict[str, Any]]
    column_mapping: Dict[str, str]
    bank_name: str = ""
    categorization_rules: Optional[List[Dict[str, Any]]] = None
    default_category_rules: Optional[Dict[str, str]] = None
    account_mapping: Optional[Dict[str, str]] = None


class MultiCSVParseRequest(BaseModel):
    file_ids: List[str]
    parse_configs: List[Dict[str, Any]]
    user_name: str = "Ammar Qazi"
    date_tolerance_hours: int = 24
    enable_cleaning: bool = True


class MultiCSVTransformRequest(BaseModel):
    csv_data_list: List[Dict[str, Any]]
    user_name: str = "Ammar Qazi"
    enable_transfer_detection: bool = True
    date_tolerance_hours: int = 24
    bank_rules_settings: Optional[Dict[str, bool]] = None


class SaveTemplateRequest(BaseModel):
    template_name: str
    config: Dict[str, Any]


class UploadResponse(BaseModel):
    success: bool
    file_id: str
    original_name: str
    size: int


class ParseResponse(BaseModel):
    success: bool
    headers: List[str]
    data: List[Dict[str, Any]]
    row_count: int
    parser_used: Optional[str] = None
    cleaning_applied: Optional[bool] = False
    cleaning_summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TransformResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    row_count: int
    error: Optional[str] = None


class MultiCSVResponse(BaseModel):
    success: bool
    transformed_data: List[Dict[str, Any]]
    transfer_analysis: Dict[str, Any]
    transformation_summary: Dict[str, Any]
    file_results: List[Dict[str, Any]]
