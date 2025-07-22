"""
Data processor for converting raw CSV rows into structured format
Handles header detection, data row extraction, and dictionary conversion
"""
from typing import Any, Dict, List, Optional
from .utils import normalize_column_count, sanitize_for_json, validate_csv_structure, estimate_data_types, clean_header, generate_column_names
from .exceptions import DataExtractionError
from .data_processing_helpers import _extract_headers, _extract_data_rows, _convert_to_dictionaries
import re
from decimal import Decimal, InvalidOperation # Keep InvalidOperation
from datetime import date, datetime

class DataProcessor:
    """Process raw CSV data into structured format"""
    
    def __init__(self):
        self.header_indicators = [
            'date', 'timestamp', 'time', 'amount', 'balance', 'description', 
            'type', 'category', 'account', 'reference', 'id', 'transaction',
            'currency', 'memo', 'payee', 'value', 'debit', 'credit'
        ]
    
    def parse_amount(self, value: str) -> Decimal:
        cleaned = re.sub(r'[,\s]', '', value)
        if not cleaned:
            raise ValueError("Cannot parse empty string as amount")
        return Decimal(cleaned)

    def parse_date(self, value: str) -> date:
        # Multiple format support
        for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%b-%Y', '%d-%B-%Y']:
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date: {value}")
    
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
        print(f"[DATA] Processing {len(raw_rows)} raw rows")
        
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
            print(f"    Normalized to {len(normalized_rows[0]) if normalized_rows else 0} columns per row")
            
            # Extract headers using helper
            headers_result = _extract_headers(normalized_rows, header_row, self.header_indicators)
            headers = headers_result['headers']
            actual_header_row = headers_result['header_row_used']
            
            print(f"    Extracted {len(headers)} headers from row {actual_header_row}")
            
            # Extract data rows
            data_rows_result = _extract_data_rows(normalized_rows, actual_header_row)
            data_rows = data_rows_result['data_rows']
            
            print(f"   [DATA] Extracted {len(data_rows)} data rows")
            
            # Convert to dictionaries
            data_dicts = _convert_to_dictionaries(headers, data_rows)
            
            # Apply type conversion to dates and amounts
            typed_data = self._apply_type_conversion(data_dicts)
            
            # Apply JSON sanitization
            sanitized_data = sanitize_for_json(typed_data)
            
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
            print(f"[ERROR]  Data processing failed: {str(e)}")
            return {
                'success': False,
                'headers': [],
                'data': [],
                'row_count': 0,
                'error': f"Data processing failed: {str(e)}"
            }
    
    def _apply_type_conversion(self, data_dicts: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Apply type conversion to known fields like date and amount based on header names.
        This is a critical step for type safety, converting strings to typed objects.
        """
        converted_data = []
        print(f"    Applying type conversion to {len(data_dicts)} rows...")
        for row_dict in data_dicts:
            new_row = row_dict.copy()
            for key, value in row_dict.items():
                if not isinstance(value, str) or not value.strip():
                    continue

                key_lower = key.lower()

                if 'date' in key_lower:
                    try:
                        new_row[key] = self.parse_date(value)
                    except ValueError:
                        # If parsing fails, keep the original string and log a warning
                        print(f"   [WARNING]  Could not parse date '{value}' in column '{key}'. Keeping as string.")
                        pass
                elif 'amount' in key_lower or 'balance' in key_lower or 'debit' in key_lower or 'credit' in key_lower:
                    # We will not parse the amount here. It will be handled by the bank-specific cleaner.
                    pass
            converted_data.append(new_row)
        return converted_data