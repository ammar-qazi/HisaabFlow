"""
CSV structure analyzer for detecting patterns and validating data
Analyzes CSV structure, detects header rows, and estimates data types
"""
from typing import Dict, List, Optional, Tuple
from .utils import validate_csv_structure, estimate_data_types
from .exceptions import StructureDetectionError
import re
from dataclasses import dataclass
from backend.shared.amount_formats.amount_format_detector import AmountFormatDetector, AmountFormatAnalysis


@dataclass
class FieldMappingSuggestion:
    """Suggestion for mapping a CSV column to a standard field"""
    field_name: str
    suggested_columns: List[str]
    confidence_scores: Dict[str, float]
    best_match: Optional[str] = None


@dataclass 
class UnknownBankAnalysis:
    """Complete analysis results for unknown bank CSV"""
    filename: str
    encoding: str
    delimiter: str
    headers: List[str]
    header_row: int
    data_start_row: int
    amount_format_analysis: AmountFormatAnalysis
    field_mapping_suggestions: Dict[str, FieldMappingSuggestion]
    filename_patterns: List[str]
    sample_data: List[Dict[str, str]]
    structure_confidence: float


class StructureAnalyzer:
    """Analyze CSV structure and detect patterns"""
    
    def __init__(self):
        self.header_indicators = [
            'date', 'timestamp', 'time', 'amount', 'balance', 'description', 
            'type', 'category', 'account', 'reference', 'id', 'transaction',
            'currency', 'memo', 'payee', 'value', 'debit', 'credit', 'status'
        ]
        
        # Enhanced field mapping patterns for unknown bank support
        self.standard_field_patterns = {
            'date': {
                'keywords': ['date', 'timestamp', 'time', 'datetime', 'transaction_date', 'posting_date', 'value_date', 'process_date'],
                'patterns': [r'date', r'time', r'dt', r'.*date.*', r'.*time.*']
            },
            'amount': {
                'keywords': ['amount', 'value', 'sum', 'total', 'balance', 'transaction_amount', 'debit', 'credit'],
                'patterns': [r'amount', r'value', r'sum', r'total', r'balance', r'.*amount.*', r'debit', r'credit']
            },
            'title': {
                'keywords': ['description', 'title', 'memo', 'reference', 'payee', 'merchant', 'details', 'narrative', 'transaction_description'],
                'patterns': [r'desc.*', r'title', r'memo', r'ref.*', r'payee', r'merchant', r'details', r'narrative', r'.*description.*']
            },
            'note': {
                'keywords': ['note', 'type', 'category', 'code', 'class', 'transaction_type', 'payment_type'],
                'patterns': [r'note', r'type', r'category', r'code', r'class', r'.*type.*']
            },
            'currency': {
                'keywords': ['currency', 'curr', 'ccy', 'symbol', 'currency_code'],
                'patterns': [r'curr.*', r'ccy', r'symbol', r'.*currency.*']
            },
            'exchange_to': {
                'keywords': ['exchange_to', 'converted_amount', 'local_amount', 'home_amount', 'target_amount'],
                'patterns': [r'exchange.*', r'convert.*', r'local.*', r'home.*', r'target.*']
            },
            'exchange_to_currency': {
                'keywords': ['exchange_currency', 'target_currency', 'local_currency', 'home_currency'],
                'patterns': [r'exchange.*curr.*', r'target.*curr.*', r'local.*curr.*', r'home.*curr.*']
            }
        }
        
        # Initialize amount format detector
        self.amount_format_detector = AmountFormatDetector()
        
        self.date_patterns = [
            r'\d{4}[-/.]\d{1,2}[-/.]\d{1,2}',   # YYYY-MM-DD, YYYY.MM.DD
            r'\d{1,2}[-/.]\d{1,2}[-/.]\d{4}',   # MM-DD-YYYY, DD.MM.YYYY
            r'\d{1,2}[-/.]\d{1,2}[-/.]\d{2}',   # MM-DD-YY, DD.MM.YY
        ]
        
        self.amount_patterns = [
            r'-?\d+[,.]?\d*',                    # Basic numbers with optional decimal
            r'-?\d{1,3}(,\d{3})*(\.\d{2})?',   # US format: 1,234.56
            r'-?\d{1,3}(\.\d{3})*(,\d{2})?',   # EU format: 1.234,56
        ]
    
    def analyze_structure(self, sample_rows: List[List[str]]) -> Dict:
        """Analyze CSV structure comprehensively"""
        print(f" Analyzing structure of {len(sample_rows)} sample rows")
        
        try:
            if not sample_rows:
                return {'success': False, 'error': 'No sample rows provided for analysis'}
            
            # Basic structure info
            row_count = len(sample_rows)
            col_count = len(sample_rows[0]) if sample_rows else 0
            
            # Detect header row
            header_detection = self.detect_header_row(sample_rows)
            
            # Get headers and data for analysis
            suggested_header_row = header_detection.get('suggested_row', 0)
            data_start_row = suggested_header_row + 1 if suggested_header_row is not None else 0
            
            if data_start_row < len(sample_rows):
                data_rows = sample_rows[data_start_row:]
                headers = sample_rows[suggested_header_row] if suggested_header_row is not None else None
                type_estimates = self.estimate_data_types(data_rows, headers)
            else:
                data_rows = []
                type_estimates = {}
            
            # Validate structure
            headers = sample_rows[suggested_header_row] if suggested_header_row is not None else []
            validation = self.validate_structure(headers, data_rows)
            
            return {
                'success': True,
                'row_count': row_count,
                'column_count': col_count,
                'header_detection': header_detection,
                'type_estimates': type_estimates,
                'validation': validation,
                'suggested_header_row': suggested_header_row,
                'suggested_data_start_row': data_start_row
            }
            
        except Exception as e:
            print(f"[ERROR]  Structure analysis failed: {str(e)}")
            return {'success': False, 'error': f"Structure analysis failed: {str(e)}"}
    
    def detect_header_row(self, sample_rows: List[List[str]]) -> Dict:
        """Detect the most likely header row"""
        if not sample_rows:
            return {'suggested_row': None, 'confidence': 0.0, 'method': 'none'}
        
        scores = []
        
        # Analyze first few rows as potential headers
        for row_idx in range(min(3, len(sample_rows))):
            row = sample_rows[row_idx]
            score = 0
            
            # Score based on header indicators
            for cell in row:
                cell_lower = str(cell).lower().strip()
                for indicator in self.header_indicators:
                    if indicator in cell_lower:
                        score += 2
                        break
                else:
                    # Check for non-numeric content
                    if cell_lower and not cell_lower.replace('.', '').replace('-', '').replace(',', '').isdigit():
                        score += 1
            
            scores.append({'row_index': row_idx, 'score': score})
        
        # Find best scoring row
        if scores:
            best_entry = max(scores, key=lambda x: x['score'])
            confidence = min(best_entry['score'] / 10.0, 1.0) if best_entry['score'] > 0 else 0.1
            
            return {
                'suggested_row': best_entry['row_index'],
                'confidence': confidence,
                'method': 'pattern_analysis'
            }
        else:
            return {'suggested_row': 0, 'confidence': 0.1, 'method': 'fallback'}
    
    def estimate_data_types(self, data_rows: List[List[str]], headers: Optional[List[str]] = None) -> Dict:
        """Estimate data types for each column"""
        if not data_rows:
            return {}
        
        import re
        col_count = len(data_rows[0]) if data_rows else 0
        type_estimates = {}
        
        for col_idx in range(col_count):
            # Extract values for this column
            values = [row[col_idx].strip() for row in data_rows[:20] if col_idx < len(row) and row[col_idx].strip()]
            
            if not values:
                type_estimates[col_idx] = {'type': 'empty', 'confidence': 1.0}
                continue
            
            # Test for different types
            date_matches = sum(1 for v in values if re.match(r'\d{4}[-/.]\d{1,2}[-/.]\d{1,2}', v))
            numeric_matches = sum(1 for v in values if re.match(r'-?\d+[,.]?\d*', v.replace(' ', '')))
            
            if date_matches / len(values) > 0.7:
                type_estimates[col_idx] = {'type': 'date', 'confidence': date_matches / len(values)}
            elif numeric_matches / len(values) > 0.7:
                type_estimates[col_idx] = {'type': 'numeric', 'confidence': numeric_matches / len(values)}
            else:
                type_estimates[col_idx] = {'type': 'text', 'confidence': 0.8}
        
        return type_estimates
    
    def validate_structure(self, headers: List[str], data_rows: List[List[str]]) -> Dict:
        """Validate CSV structure using utility functions"""
        return validate_csv_structure(headers, data_rows)
    
    def analyze_unknown_csv(self, csv_data: str, filename: str, encoding: str = 'utf-8', delimiter: str = ',', header_row: Optional[int] = None) -> UnknownBankAnalysis:
        """
        Comprehensive analysis for unknown bank CSV files.
        
        Args:
            csv_data: Raw CSV content as string
            filename: Original filename for pattern generation
            encoding: Detected/specified encoding
            delimiter: Detected/specified delimiter
            header_row: Optional header row (1-based indexing). If None, auto-detect.
            
        Returns:
            UnknownBankAnalysis with complete analysis results
        """
        print(f" Analyzing unknown bank CSV: {filename}")
        
        try:
            # Parse CSV to rows
            import csv
            import io
            csv_reader = csv.reader(io.StringIO(csv_data), delimiter=delimiter)
            rows = [row for row in csv_reader]
            
            if not rows:
                raise StructureDetectionError("No data found in CSV")
            
            # Use specified header row or auto-detect
            if header_row is not None:
                # Convert from 1-based to 0-based indexing
                header_row_idx = header_row - 1
                if header_row_idx < 0 or header_row_idx >= len(rows):
                    raise StructureDetectionError(f"Header row {header_row} is out of range (1-{len(rows)})")
                print(f"  Using specified header row: {header_row} (1-based)")
            else:
                # Auto-detect header row
                header_detection = self.detect_header_row(rows)
                header_row_idx = header_detection.get('suggested_row', 0)
                print(f"  Auto-detected header row: {header_row_idx + 1} (1-based)")
            
            data_start_row = header_row_idx + 1
            
            # Extract headers and data
            headers = rows[header_row_idx] if header_row_idx < len(rows) else []
            data_rows = rows[data_start_row:data_start_row + 50]  # Sample first 50 data rows
            
            # Analyze amount format from data
            amount_samples = self._extract_amount_samples(data_rows, headers)
            amount_format_analysis = self.amount_format_detector.analyze_amount_column(amount_samples)
            
            # Generate field mapping suggestions
            field_mapping_suggestions = self.suggest_field_mappings(headers, data_rows)
            
            # Generate filename patterns
            filename_patterns = self._generate_filename_patterns(filename)
            
            # Extract sample data for preview
            sample_data = self._extract_sample_data(headers, data_rows[:10])
            
            # Calculate overall structure confidence
            # For manual header row selection, create a mock header_detection
            if header_row is not None:
                header_detection = {
                    'suggested_row': header_row_idx,
                    'confidence': 1.0,  # High confidence since user specified
                    'method': 'manual'
                }
            else:
                # Use the auto-detection result
                pass
            
            structure_confidence = self._calculate_structure_confidence(
                header_detection, amount_format_analysis, field_mapping_suggestions
            )
            
            return UnknownBankAnalysis(
                filename=filename,
                encoding=encoding,
                delimiter=delimiter,
                headers=headers,
                header_row=header_row_idx,  # Store 0-based index internally
                data_start_row=data_start_row,
                amount_format_analysis=amount_format_analysis,
                field_mapping_suggestions=field_mapping_suggestions,
                filename_patterns=filename_patterns,
                sample_data=sample_data,
                structure_confidence=structure_confidence
            )
            
        except Exception as e:
            print(f"[ERROR]  Unknown CSV analysis failed: {str(e)}")
            raise StructureDetectionError(f"Unknown CSV analysis failed: {str(e)}")
    
    def suggest_field_mappings(self, headers: List[str], data_rows: List[List[str]]) -> Dict[str, FieldMappingSuggestion]:
        """
        Suggest mappings for standard fields based on header analysis and data content.
        
        Args:
            headers: List of column headers
            data_rows: Sample data rows for content analysis
            
        Returns:
            Dictionary mapping standard field names to suggestions
        """
        print(f"  Suggesting field mappings for {len(headers)} headers")
        
        suggestions = {}
        
        for field_name, patterns in self.standard_field_patterns.items():
            # Score each header for this field
            header_scores = {}
            
            for i, header in enumerate(headers):
                score = self._score_header_for_field(header, patterns, data_rows, i)
                if score > 0:
                    header_scores[header] = score
            
            # Sort by score and create suggestion
            sorted_headers = sorted(header_scores.keys(), key=lambda h: header_scores[h], reverse=True)
            best_match = sorted_headers[0] if sorted_headers and header_scores[sorted_headers[0]] > 0.3 else None
            
            suggestions[field_name] = FieldMappingSuggestion(
                field_name=field_name,
                suggested_columns=sorted_headers[:3],  # Top 3 suggestions
                confidence_scores=header_scores,
                best_match=best_match
            )
        
        return suggestions
    
    def _score_header_for_field(self, header: str, patterns: Dict[str, List[str]], data_rows: List[List[str]], col_index: int) -> float:
        """Score how well a header matches a field type."""
        if not header:
            return 0.0
        
        header_lower = header.lower().strip()
        score = 0.0
        
        # Check exact keyword matches
        for keyword in patterns['keywords']:
            if keyword.lower() == header_lower:
                score += 1.0
                break
            elif keyword.lower() in header_lower:
                score += 0.7
        
        # Check pattern matches
        for pattern in patterns['patterns']:
            try:
                if re.search(pattern.lower(), header_lower):
                    score += 0.5
                    break
            except re.error:
                continue
        
        # Content-based scoring for specific field types
        if col_index < len(data_rows[0]) if data_rows else False:
            content_score = self._score_content_for_field(data_rows, col_index, patterns)
            score += content_score * 0.3
        
        return min(score, 1.0)
    
    def _score_content_for_field(self, data_rows: List[List[str]], col_index: int, patterns: Dict[str, List[str]]) -> float:
        """Score column content to determine field type."""
        if not data_rows or col_index >= len(data_rows[0]):
            return 0.0
        
        # Extract sample values
        values = [row[col_index].strip() for row in data_rows[:20] if col_index < len(row) and row[col_index].strip()]
        if not values:
            return 0.0
        
        field_name = patterns.get('field_name', '')
        
        # Date field scoring
        if any('date' in keyword or 'time' in keyword for keyword in patterns['keywords']):
            date_matches = sum(1 for v in values if re.match(r'\d{4}[-/.]\d{1,2}[-/.]\d{1,2}', v) or 
                             re.match(r'\d{1,2}[-/.]\d{1,2}[-/.]\d{4}', v))
            return date_matches / len(values)
        
        # Amount field scoring  
        elif any('amount' in keyword or 'value' in keyword for keyword in patterns['keywords']):
            amount_matches = sum(1 for v in values if re.match(r'-?\d+[,.]?\d*', v.replace(' ', '')))
            return amount_matches / len(values)
        
        # Currency field scoring
        elif any('currency' in keyword for keyword in patterns['keywords']):
            currency_matches = sum(1 for v in values if re.match(r'^[A-Z]{3}$', v.strip()))
            return currency_matches / len(values)
        
        return 0.0
    
    def _extract_amount_samples(self, data_rows: List[List[str]], headers: List[str]) -> List[str]:
        """Extract potential amount values for format detection."""
        amount_samples = []
        
        # Find columns that might contain amounts
        potential_amount_cols = []
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if any(keyword in header_lower for keyword in ['amount', 'value', 'sum', 'total', 'balance', 'debit', 'credit']):
                potential_amount_cols.append(i)
        
        # If no obvious amount columns, check content
        if not potential_amount_cols:
            for col_idx in range(len(headers)):
                if col_idx < len(data_rows[0]) if data_rows else False:
                    sample_values = [row[col_idx] for row in data_rows[:10] if col_idx < len(row)]
                    if self._looks_like_amounts(sample_values):
                        potential_amount_cols.append(col_idx)
        
        # Extract samples from potential amount columns
        for col_idx in potential_amount_cols:
            for row in data_rows[:50]:  # Sample first 50 rows
                if col_idx < len(row) and row[col_idx].strip():
                    amount_samples.append(row[col_idx].strip())
        
        return amount_samples
    
    def _looks_like_amounts(self, values: List[str]) -> bool:
        """Check if values look like monetary amounts."""
        if not values:
            return False
        
        numeric_count = 0
        for value in values[:10]:  # Check first 10 values
            if value and re.match(r'-?\d+[,.]?\d*', value.strip().replace(' ', '')):
                numeric_count += 1
        
        return numeric_count / len(values[:10]) > 0.6
    
    def _generate_filename_patterns(self, filename: str) -> List[str]:
        """Generate filename patterns for bank detection."""
        import os
        
        base_name = os.path.splitext(filename)[0].lower()
        patterns = []
        
        # Add exact filename pattern
        patterns.append(f"*{base_name}*")
        
        # Add patterns based on common bank naming conventions
        if 'statement' in base_name:
            patterns.append("*statement*")
        if 'export' in base_name:
            patterns.append("*export*")
        if 'transaction' in base_name:
            patterns.append("*transaction*")
        
        # Add pattern for just the bank name part (remove dates, numbers)
        clean_name = re.sub(r'\d+', '', base_name)
        clean_name = re.sub(r'[_-]+', '_', clean_name).strip('_-')
        if clean_name and clean_name != base_name:
            patterns.append(f"*{clean_name}*")
        
        return patterns
    
    def _extract_sample_data(self, headers: List[str], data_rows: List[List[str]]) -> List[Dict[str, str]]:
        """Extract sample data for preview."""
        sample_data = []
        
        for row in data_rows[:5]:  # First 5 data rows
            row_dict = {}
            for i, header in enumerate(headers):
                value = row[i] if i < len(row) else ""
                row_dict[header] = value
            sample_data.append(row_dict)
        
        return sample_data
    
    def _calculate_structure_confidence(self, header_detection: Dict, amount_format_analysis: AmountFormatAnalysis, 
                                      field_suggestions: Dict[str, FieldMappingSuggestion]) -> float:
        """Calculate overall confidence in structure detection."""
        # Header detection confidence
        header_conf = header_detection.get('confidence', 0.0)
        
        # Amount format confidence
        amount_conf = amount_format_analysis.confidence
        
        # Field mapping confidence (average of required fields)
        required_fields = ['date', 'amount', 'title']
        mapping_scores = []
        for field in required_fields:
            if field in field_suggestions and field_suggestions[field].best_match:
                best_score = max(field_suggestions[field].confidence_scores.values()) if field_suggestions[field].confidence_scores else 0.0
                mapping_scores.append(best_score)
            else:
                mapping_scores.append(0.0)
        
        mapping_conf = sum(mapping_scores) / len(mapping_scores) if mapping_scores else 0.0
        
        # Weighted average
        overall_conf = (header_conf * 0.3 + amount_conf * 0.3 + mapping_conf * 0.4)
        
        return overall_conf
    
    def validate_header_row(self, csv_data: str, header_row: int, delimiter: str = ',') -> Dict[str, any]:
        """
        Validate that a specified header row is reasonable for CSV parsing.
        Handles edge cases like empty rows, inconsistent column counts, etc.
        
        Args:
            csv_data: Raw CSV content as string
            header_row: Header row number (1-based indexing)
            delimiter: CSV delimiter
            
        Returns:
            Dictionary with validation results
        """
        try:
            import csv
            import io
            
            csv_reader = csv.reader(io.StringIO(csv_data), delimiter=delimiter)
            rows = [row for row in csv_reader]
            
            if not rows:
                return {
                    'valid': False,
                    'error': 'No data found in CSV',
                    'total_rows': 0
                }
            
            # Convert to 0-based indexing
            header_row_idx = header_row - 1
            
            # Check if header row is within bounds
            if header_row_idx < 0 or header_row_idx >= len(rows):
                return {
                    'valid': False,
                    'error': f'Header row {header_row} is out of range (1-{len(rows)})',
                    'total_rows': len(rows)
                }
            
            # Get the proposed header row
            headers = rows[header_row_idx]
            
            # Enhanced validation for empty rows and edge cases
            if not headers:
                return {
                    'valid': False,
                    'error': f'Row {header_row} is completely empty (no columns)',
                    'total_rows': len(rows),
                    'headers': []
                }
            
            # Check if all cells are empty or whitespace
            non_empty_headers = [cell.strip() for cell in headers if cell.strip()]
            if not non_empty_headers:
                return {
                    'valid': False,
                    'error': f'Row {header_row} contains only empty cells or whitespace',
                    'total_rows': len(rows),
                    'headers': headers
                }
            
            # Check for minimum number of meaningful headers
            if len(non_empty_headers) < 2:
                return {
                    'valid': False,
                    'error': f'Row {header_row} has too few meaningful headers ({len(non_empty_headers)}). Need at least 2.',
                    'total_rows': len(rows),
                    'headers': headers
                }
            
            # Find the next non-empty data row for validation
            data_start_row = header_row_idx + 1
            first_data_row = None
            data_rows_skipped = 0
            
            for i in range(data_start_row, min(data_start_row + 10, len(rows))):  # Check next 10 rows max
                row = rows[i]
                if row and any(cell.strip() for cell in row):  # Found non-empty row
                    first_data_row = row
                    data_rows_skipped = i - data_start_row
                    break
            
            if first_data_row is None:
                return {
                    'valid': False,
                    'error': f'No data rows found after header row {header_row}',
                    'total_rows': len(rows),
                    'headers': headers
                }
            
            # Check column count consistency between header and data
            header_col_count = len(headers)
            data_col_count = len(first_data_row)
            
            warnings = []
            if abs(header_col_count - data_col_count) > 1:  # Allow 1 column difference
                warnings.append(f'Column count mismatch: headers have {header_col_count} columns, first data row has {data_col_count}')
            
            # Check if headers look reasonable (not all numbers, not too long)
            suspicious_headers = []
            for i, header in enumerate(headers):
                header_str = str(header).strip()
                if len(header_str) > 100:  # Very long headers are suspicious
                    suspicious_headers.append(f'Column {i+1}: Header too long ({len(header_str)} chars)')
                elif header_str and header_str.replace('.', '').replace('-', '').replace(',', '').replace(' ', '').isdigit():
                    suspicious_headers.append(f'Column {i+1}: Header appears to be numeric data')
            
            warnings.extend(suspicious_headers)
            
            # Get sample of data rows for preview (skip empty rows)
            sample_data = []
            sample_count = 0
            for i in range(data_start_row, len(rows)):
                if sample_count >= 3:  # Get 3 sample rows
                    break
                    
                row = rows[i]
                if row and any(cell.strip() for cell in row):  # Skip empty rows
                    row_dict = {}
                    for j, header in enumerate(headers):
                        value = row[j] if j < len(row) else ""
                        row_dict[header] = value
                    sample_data.append(row_dict)
                    sample_count += 1
            
            # Calculate actual data rows available (excluding empty rows)
            actual_data_rows = 0
            for i in range(data_start_row, len(rows)):
                row = rows[i]
                if row and any(cell.strip() for cell in row):
                    actual_data_rows += 1
            
            return {
                'valid': True,
                'total_rows': len(rows),
                'headers': headers,
                'data_rows_available': actual_data_rows,
                'empty_rows_skipped': data_rows_skipped,
                'sample_data': sample_data,
                'warnings': warnings,
                'column_count': len(headers),
                'non_empty_headers': len(non_empty_headers)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Validation failed: {str(e)}',
                'total_rows': 0
            }
