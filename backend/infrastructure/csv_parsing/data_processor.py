"""
Data processor for converting raw CSV rows into structured format
Handles header detection, data row extraction, and dictionary conversion
"""
from typing import Dict, List, Optional
from .utils import normalize_column_count, sanitize_for_json, validate_csv_structure, estimate_data_types
from .data_processing_helpers import _extract_headers, _extract_data_rows, _convert_to_dictionaries
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """Process raw CSV data into structured format"""
    
    def __init__(self):
        self.header_indicators = [
            'date', 'timestamp', 'time', 'amount', 'balance', 'description', 
            'type', 'category', 'account', 'reference', 'id', 'transaction',
            'currency', 'memo', 'payee', 'value', 'debit', 'credit'
        ]
    
    def process_raw_data(self, raw_rows: List[List[str]], header_row: Optional[int] = None) -> Dict:
        """
        Process raw CSV data into structured format
        
        Args:
            raw_rows: Raw rows from CSV parsing
            header_row: Optional header row index
            
        Returns:
            dict: {
                'success': bool,
                'headers': List[str],
                'data': List[Dict],
                'row_count': int,
                'processing_info': dict
            }
        """
        logger.debug(f"[DATA] Processing {len(raw_rows)} raw rows")
        
        try:
            if not raw_rows:
                return {
                    'success': False,
                    'headers': [],
                    'data': [],
                    'row_count': 0,
                    'error': 'No raw data to process'
                }
            
            # Normalize column counts across all rows and clean headers
            normalized_rows = normalize_column_count(raw_rows)
            logger.debug(f"    Normalized to {len(normalized_rows[0]) if normalized_rows else 0} columns per row")
            
            # Extract headers using helper
            headers_result = _extract_headers(normalized_rows, header_row, self.header_indicators)
            headers = headers_result['headers']
            actual_header_row = headers_result['header_row_used']
            
            logger.debug(f"    Extracted {len(headers)} headers from row {actual_header_row}")
            
            # Extract data rows
            data_rows_result = _extract_data_rows(normalized_rows, actual_header_row)
            data_rows = data_rows_result['data_rows']
            
            logger.debug(f"   [DATA] Extracted {len(data_rows)} data rows")
            
            # Convert to dictionaries
            data_dicts = _convert_to_dictionaries(headers, data_rows)
            
            # Values stay as text here: dates and amounts are parsed later by
            # the bank-aware DateCleaner and NumericCleaner
            sanitized_data = sanitize_for_json(data_dicts)
            
            # Validate structure
            validation = validate_csv_structure(headers, data_rows)
            
            # Estimate data types
            type_estimates = estimate_data_types(data_rows)
            
            processing_info = {
                'header_row_used': actual_header_row,
                'data_start_row': actual_header_row + 1 if actual_header_row is not None else 0,
                'original_row_count': len(raw_rows),
                'normalized_row_count': len(normalized_rows),
                'final_data_count': len(sanitized_data),
                'validation': validation,
                'type_estimates': type_estimates,
                'headers_info': headers_result,
                'data_rows_info': data_rows_result,
                'row_mapping': data_rows_result.get('row_mapping', {}),
                'empty_rows_filtered': data_rows_result.get('empty_rows_filtered', 0)
            }
            
            return {
                'success': True,
                'headers': headers,
                'data': sanitized_data, # This is now List[Dict[str, Any]]
                'row_count': len(sanitized_data),
                'processing_info': processing_info,
                'data_type': 'dict' # Explicitly state we are returning dicts
            }
            
        except Exception as e:
            logger.error(f"[ERROR]  Data processing failed: {str(e)}")
            return {
                'success': False,
                'headers': [],
                'data': [],
                'row_count': 0,
                'error': f"Data processing failed: {str(e)}"
            }
    
