import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re
import csv

class RobustCSVParser:
    def __init__(self):
        self.target_columns = ['Date', 'Amount', 'Category', 'Title', 'Note', 'Account']
    
    def read_csv_robust(self, file_path: str, encoding: str = 'utf-8', nrows: Optional[int] = None) -> pd.DataFrame:
        """Robustly read CSV file handling inconsistent column counts"""
        try:
            # First try standard pandas approach
            try:
                return pd.read_csv(
                    file_path, 
                    encoding=encoding, 
                    header=None,
                    nrows=nrows,
                    engine='python',
                    quoting=csv.QUOTE_MINIMAL,
                    skipinitialspace=True
                )
            except pd.errors.ParserError:
                pass
            
            # Fallback: Manual parsing with CSV module
            lines = []
            with open(file_path, 'r', encoding=encoding, newline='') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    if nrows and i >= nrows:
                        break
                    lines.append(row)
            
            if not lines:
                raise ValueError("No data found in file")
            
            # Find the maximum number of columns
            max_cols = max(len(line) for line in lines)
            
            # Pad all rows to have the same number of columns
            padded_lines = []
            for line in lines:
                padded_line = line + [''] * (max_cols - len(line))
                padded_lines.append(padded_line)
            
            return pd.DataFrame(padded_lines)
            
        except Exception as e:
            # Final fallback: Simple split-based parsing
            with open(file_path, 'r', encoding=encoding) as f:
                lines = []
                for i, line in enumerate(f):
                    if nrows and i >= nrows:
                        break
                    # Simple comma split with cleanup
                    parts = [part.strip().strip('"') for part in line.strip().split(',')]
                    lines.append(parts)
            
            if not lines:
                raise ValueError("No data could be parsed from file")
            
            max_cols = max(len(line) for line in lines) if lines else 0
            padded_lines = []
            for line in lines:
                padded_line = line + [''] * (max_cols - len(line))
                padded_lines.append(padded_line[:max_cols])
            
            return pd.DataFrame(padded_lines)
    
    def preview_csv(self, file_path: str, encoding: str = 'utf-8') -> Dict:
        """Preview CSV file and return basic info"""
        try:
            df_preview = self.read_csv_robust(file_path, encoding, nrows=20)
            
            # Replace NaN values with empty strings for JSON serialization
            df_preview = df_preview.fillna('')
            
            # Ensure all values are JSON serializable
            for col in df_preview.columns:
                df_preview[col] = df_preview[col].astype(str).replace('nan', '')
            
            return {
                'success': True,
                'total_rows': len(df_preview),
                'total_columns': len(df_preview.columns),
                'preview_data': df_preview.to_dict('records'),
                'column_names': [f"Column_{i}" for i in range(len(df_preview.columns))]
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def detect_data_range(self, file_path: str, encoding: str = 'utf-8') -> Dict:
        """Auto-detect where the actual data starts"""
        try:
            df = self.read_csv_robust(file_path, encoding)
            
            # Look for rows that might contain headers
            header_indicators = ['timestamp', 'date', 'amount', 'description', 'balance', 'type']
            data_start_row = None
            
            for idx, row in df.iterrows():
                row_text = ' '.join([str(cell).lower() for cell in row if pd.notna(cell) and str(cell).strip()])
                if any(indicator in row_text for indicator in header_indicators):
                    data_start_row = idx
                    break
            
            return {
                'success': True,
                'suggested_header_row': data_start_row,
                'total_rows': len(df)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def parse_with_range(self, file_path: str, start_row: int, end_row: Optional[int] = None, 
                        start_col: int = 0, end_col: Optional[int] = None, 
                        encoding: str = 'utf-8') -> Dict:
        """Parse CSV with specified range"""
        try:
            df_full = self.read_csv_robust(file_path, encoding)
            
            # Extract the specified range
            if end_row is None:
                end_row = len(df_full)
            if end_col is None:
                end_col = len(df_full.columns)
            
            # Extract data range
            df_range = df_full.iloc[start_row:end_row, start_col:end_col].copy()
            
            # Use first row as headers if it looks like headers
            if len(df_range) > 0:
                headers = df_range.iloc[0].tolist()
                df_range.columns = headers
                df_range = df_range.iloc[1:].reset_index(drop=True)
            
            # Replace NaN values with empty strings for JSON serialization
            df_range = df_range.fillna('')
            
            # Ensure all values are JSON serializable
            for col in df_range.columns:
                df_range[col] = df_range[col].astype(str).replace('nan', '')
            
            return {
                'success': True,
                'headers': df_range.columns.tolist(),
                'data': df_range.to_dict('records'),
                'row_count': len(df_range)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Test the robust parser
if __name__ == "__main__":
    parser = RobustCSVParser()
    
    # Test with problematic CSV
    file_path = "../test_inconsistent.csv"
    
    print("=== Testing Robust CSV Parser ===")
    preview = parser.preview_csv(file_path)
    print("Preview Result:")
    print(json.dumps(preview, indent=2))
    
    if preview['success']:
        print("\n=== Detection Result ===")
        detection = parser.detect_data_range(file_path)
        print(json.dumps(detection, indent=2))
        
        print("\n=== Parse Result ===")
        parse_result = parser.parse_with_range(file_path, start_row=7, end_col=5)
        print(json.dumps(parse_result, indent=2))
