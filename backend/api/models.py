"""
Pydantic models for API requests and responses
Centralized definition of all data models used by the FastAPI endpoints
"""
from pydantic import BaseModel
from typing import Dict, List, Optional, Union, Any


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


class CategorizationRule(BaseModel):
    pattern: str
    category: str
    amount_threshold: Optional[float] = None
    currency: Optional[str] = None

class TransformRequest(BaseModel):
    data: List[Dict[str, Union[str, int, float]]]
    column_mapping: Dict[str, str]
    bank_name: str = ""
    categorization_rules: Optional[List[CategorizationRule]] = None
    default_category_rules: Optional[Dict[str, str]] = None
    account_mapping: Optional[Dict[str, str]] = None


class ParseConfig(BaseModel):
    start_row: int
    end_row: Optional[int] = None
    start_col: int = 0
    end_col: Optional[int] = None
    encoding: str = "utf-8"
    enable_cleaning: bool = True

class MultiCSVParseRequest(BaseModel):
    file_ids: List[str]
    parse_configs: List[ParseConfig]
    enable_cleaning: bool = True


class CSVDataItem(BaseModel):
    data: List[Dict[str, Union[str, int, float]]]
    bank_name: str
    file_id: str
    original_name: str

class MultiCSVTransformRequest(BaseModel):
    csv_data_list: List[CSVDataItem]
    enable_transfer_detection: bool = True


class SaveTemplateRequest(BaseModel):
    template_name: str
    config: Dict[str, Union[str, int, float, bool, List[str]]]


class UploadResponse(BaseModel):
    success: bool
    file_id: str
    original_name: str
    size: int


class CleaningSummary(BaseModel):
    original_rows: int
    final_rows: int
    rows_removed: int
    numeric_columns_cleaned: int
    date_columns_cleaned: int
    currency_column_added: bool
    quality_grade: str

class ParseResponse(BaseModel):
    success: bool
    headers: List[str]
    data: List[Dict[str, Union[str, int, float]]]
    row_count: int
    parser_used: Optional[str] = None
    cleaning_applied: Optional[bool] = False
    cleaning_summary: Optional[CleaningSummary] = None
    error: Optional[str] = None


class TransformResponse(BaseModel):
    success: bool
    data: List[Dict[str, Union[str, int, float]]]
    row_count: int
    error: Optional[str] = None


class TransferMatch(BaseModel):
    outgoing_transaction: Dict[str, Union[str, int, float]]
    incoming_transaction: Dict[str, Union[str, int, float]]
    confidence: float
    match_type: str
    # Frontend compatibility fields
    outgoing: Optional[Dict[str, Union[str, int, float]]] = None
    incoming: Optional[Dict[str, Union[str, int, float]]] = None

class TransferAnalysis(BaseModel):
    total_matches: int
    high_confidence_matches: int
    medium_confidence_matches: int
    low_confidence_matches: int
    matches: List[TransferMatch]
    # Frontend compatibility fields
    transfers: Optional[List[TransferMatch]] = None
    summary: Optional[Dict[str, Any]] = None
    potential_pairs: Optional[List[Dict[str, Any]]] = None
    potential_transfers: Optional[List[Dict[str, Any]]] = None
    conflicts: Optional[List[Dict[str, Any]]] = None
    flagged_transactions: Optional[List[Dict[str, Any]]] = None

class TransformationSummary(BaseModel):
    total_files: int
    total_rows: int
    successful_transformations: int
    failed_transformations: int
    banks_processed: List[str]
    # Frontend compatibility field
    total_transactions: Optional[int] = None

class FileResult(BaseModel):
    file_id: str
    original_name: str
    bank_name: str
    rows_processed: int
    success: bool
    error: Optional[str] = None

class ParsedFileResult(BaseModel):
    file_id: str
    filename: str
    success: bool
    bank_info: Dict[str, Union[str, float, List[str]]]
    parse_result: Dict[str, Union[bool, List[str], List[Dict], int]]
    config: ParseConfig

class MultiCSVParseResponse(BaseModel):
    success: bool
    parsed_csvs: List[ParsedFileResult]
    total_files: int

class MultiCSVResponse(BaseModel):
    success: bool
    transformed_data: List[Dict[str, Union[str, int, float]]]
    transfer_analysis: TransferAnalysis
    transformation_summary: TransformationSummary
    file_results: List[FileResult]


# Additional response models for uncovered endpoints
class ConfigListResponse(BaseModel):
    configurations: List[str]
    raw_bank_names: List[str]
    count: int


class DataCleaningConfig(BaseModel):
    enable_currency_addition: bool
    multi_currency: bool
    numeric_amount_conversion: bool
    date_standardization: bool
    remove_invalid_rows: bool
    default_currency: str


class ConfigResponse(BaseModel):
    success: bool
    config: Dict[str, Union[str, int, float, bool, Dict, None]]
    bank_name: str
    display_name: str
    source: str


class SaveConfigResponse(BaseModel):
    success: bool
    message: str
    config_file: str
    suggestion: str


class BankDetection(BaseModel):
    detected_bank: str
    confidence: float
    reasons: List[str]


class PreviewResponse(BaseModel):
    success: bool
    preview_data: List[Dict[str, Union[str, int, float]]]
    column_names: List[str]
    total_rows: int
    encoding_used: str
    parsing_info: Dict[str, Union[str, int, float, bool, Dict]]
    bank_detection: BankDetection
    error: Optional[str] = None


class DetectRangeResponse(BaseModel):
    success: bool
    suggested_header_row: int
    total_rows: int
    confidence: float
    error: Optional[str] = None


class CleanupResponse(BaseModel):
    success: bool


class ExportResponse(BaseModel):
    success: bool
    filename: str
    download_url: str
    row_count: int
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
