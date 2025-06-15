"""
CSV structure analyzer for detecting patterns and validating data
Analyzes CSV structure, detects header rows, and estimates data types
"""
from typing import Dict, List, Optional, Tuple
from .utils import validate_csv_structure, estimate_data_types
from .exceptions import StructureDetectionError

class StructureAnalyzer:
    """Analyze CSV structure and detect patterns"""
    
    def __init__(self):
        self.header_indicators = [
            'date', 'timestamp', 'time', 'amount', 'balance', 'description', 
            'type', 'category', 'account', 'reference', 'id', 'transaction',
            'currency', 'memo', 'payee', 'value', 'debit', 'credit', 'status'
        ]
        
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
        print(f"🔍 Analyzing structure of {len(sample_rows)} sample rows")
        
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
            print(f"❌ Structure analysis failed: {str(e)}")
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
