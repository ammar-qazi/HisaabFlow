"""
Data processor for converting raw CSV rows into structured format
Handles header detection, data row extraction, and dictionary conversion
"""
from typing import Dict, List, Optional
from .utils import normalize_column_count, clean_header, generate_column_names, sanitize_for_json, validate_csv_structure, estimate_data_types
from .exceptions import DataExtractionError

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
        print(f"📊 Processing {len(raw_rows)} raw rows")
        
        try:
            if not raw_rows:
                return {
                    'success': False,
                    'headers': [],
                    'data': [],
                    'row_count': 0,
                    'error': 'No raw data to process'
                }
            
            # Normalize column counts across all rows
            normalized_rows = normalize_column_count(raw_rows)
            print(f"   📏 Normalized to {len(normalized_rows[0]) if normalized_rows else 0} columns per row")
            
            # Extract headers
            headers_result = self._extract_headers(normalized_rows, header_row)
            headers = headers_result['headers']
            actual_header_row = headers_result['header_row_used']
            
            print(f"   📋 Extracted {len(headers)} headers from row {actual_header_row}")
            
            # Extract data rows
            data_rows_result = self._extract_data_rows(normalized_rows, actual_header_row)
            data_rows = data_rows_result['data_rows']
            
            print(f"   📊 Extracted {len(data_rows)} data rows")
            
            # Convert to dictionaries
            data_dicts = self._convert_to_dictionaries(headers, data_rows)
            
            # Apply JSON sanitization
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
                'data_rows_info': data_rows_result
            }
            
            return {
                'success': True,
                'headers': headers,
                'data': sanitized_data,
                'row_count': len(sanitized_data),
                'processing_info': processing_info
            }
            
        except Exception as e:
            print(f"❌ Data processing failed: {str(e)}")
            return {
                'success': False,
                'headers': [],
                'data': [],
                'row_count': 0,
                'error': f"Data processing failed: {str(e)}"
            }
    
    def _extract_headers(self, normalized_rows: List[List[str]], header_row: Optional[int]) -> Dict:
        """
        Extract headers from normalized rows
        
        Args:
            normalized_rows: Rows with consistent column counts
            header_row: Optional explicit header row index
            
        Returns:
            dict: Headers extraction result with metadata
        """
        if not normalized_rows:
            return {
                'headers': [],
                'header_row_used': None,
                'method': 'none',
                'confidence': 0.0
            }
        
        col_count = len(normalized_rows[0])
        
        if header_row is not None:
            # Use explicit header row
            if 0 <= header_row < len(normalized_rows):
                raw_headers = normalized_rows[header_row]
                headers = [clean_header(h) for h in raw_headers]
                
                # Generate names for empty headers
                for i, header in enumerate(headers):
                    if not header:
                        headers[i] = f"Column_{i}"
                
                return {
                    'headers': headers,
                    'header_row_used': header_row,
                    'method': 'explicit',
                    'confidence': 1.0
                }
            else:
                # Invalid header row, fall back to auto-detection
                print(f"   ⚠️ Invalid header row {header_row}, falling back to auto-detection")
        
        # Auto-detect header row
        best_row = 0
        best_score = 0
        best_confidence = 0.0
        
        # Check first few rows for header patterns
        for row_idx in range(min(5, len(normalized_rows))):
            row = normalized_rows[row_idx]
            score = 0
            
            # Score based on header indicators
            for cell in row:
                cell_lower = str(cell).lower().strip()
                for indicator in self.header_indicators:
                    if indicator in cell_lower:
                        score += 2  # Strong match
                        break
                else:
                    # Check for header-like patterns
                    if cell_lower and not cell_lower.replace('.', '').replace('-', '').replace(',', '').isdigit():
                        score += 1  # Non-numeric text
            
            # Calculate confidence
            confidence = score / len(row) if row else 0
            
            if score > best_score:
                best_score = score
                best_row = row_idx
                best_confidence = confidence
        
        # Extract headers from best row
        if best_row < len(normalized_rows):
            raw_headers = normalized_rows[best_row]
            headers = [clean_header(h) for h in raw_headers]
            
            # Generate names for empty headers
            for i, header in enumerate(headers):
                if not header:
                    headers[i] = f"Column_{i}"
        else:
            # Fallback to generic headers
            headers = generate_column_names(col_count)
            best_row = None
        
        return {
            'headers': headers,
            'header_row_used': best_row,
            'method': 'auto_detected',
            'confidence': best_confidence,
            'scores_tested': best_score
        }
    
    def _extract_data_rows(self, normalized_rows: List[List[str]], header_row: Optional[int]) -> Dict:
        """
        Extract data rows (excluding header row)
        
        Args:
            normalized_rows: Rows with consistent column counts
            header_row: Header row index to skip
            
        Returns:
            dict: Data rows extraction result with metadata
        """
        if not normalized_rows:
            return {
                'data_rows': [],
                'skipped_header': False,
                'empty_rows_filtered': 0
            }
        
        # Determine data start row
        data_start_row = 0
        skipped_header = False
        
        if header_row is not None and header_row >= 0:
            data_start_row = header_row + 1
            skipped_header = True
        
        # Extract data rows
        raw_data_rows = normalized_rows[data_start_row:]
        
        # Filter out empty rows
        data_rows = []
        empty_rows_filtered = 0
        
        for row in raw_data_rows:
            # Check if row has any non-empty content
            if any(cell.strip() for cell in row):
                data_rows.append(row)
            else:
                empty_rows_filtered += 1
        
        return {
            'data_rows': data_rows,
            'data_start_row': data_start_row,
            'skipped_header': skipped_header,
            'empty_rows_filtered': empty_rows_filtered,
            'original_data_rows': len(raw_data_rows),
            'final_data_rows': len(data_rows)
        }
    
    def _convert_to_dictionaries(self, headers: List[str], data_rows: List[List[str]]) -> List[Dict]:
        """
        Convert data rows to list of dictionaries using headers
        
        Args:
            headers: Column headers
            data_rows: Data rows to convert
            
        Returns:
            List[Dict]: List of row dictionaries
        """
        if not headers or not data_rows:
            return []
        
        data_dicts = []
        
        for row in data_rows:
            # Create dictionary mapping headers to row values
            row_dict = {}
            for i, header in enumerate(headers):
                value = row[i] if i < len(row) else ''
                row_dict[header] = value
            
            data_dicts.append(row_dict)
        
        print(f"   🔄 Converted {len(data_dicts)} rows to dictionaries")
        return data_dicts
