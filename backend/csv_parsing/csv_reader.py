"""
CSV Reader Module - Manual CSV reading with robust parsing
"""
import csv
import pandas as pd
from typing import Dict, List, Optional

class CSVReader:
    """Handles reading CSV files with manual parsing for inconsistent structures"""
    
    def preview_csv(self, file_path: str, encoding: str = 'utf-8', header_row: int = None, 
                   bank_name: str = None, config_manager=None) -> Dict:
        """Preview CSV file and return basic info using robust CSV reading"""
        try:
            # Try utf-8-sig first to handle BOM characters properly
            if encoding == 'utf-8':
                encoding = 'utf-8-sig'
                print(f"      🔧 Using utf-8-sig encoding to handle BOM characters")
            
            # 🆕 HEADER DETECTION: Use bank-specific configuration if available
            detected_header_info = None
            if config_manager and bank_name:
                print(f"🔍 Using bank-specific header detection for {bank_name}")
                detected_header_info = config_manager.detect_header_row(file_path, bank_name, encoding)
                if detected_header_info['success']:
                    header_row = detected_header_info['header_row']
                    print(f"📋 Bank config detected headers at row {header_row}")
            
            # Use manual CSV reading for inconsistent structures
            lines = []
            with open(file_path, 'r', encoding=encoding, newline='') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    lines.append(row)
                    if i >= 19:  # Only preview first 20 rows
                        break
            
            if not lines:
                raise ValueError("No data found in file")
            
            # Find the maximum number of columns for preview
            max_cols = max(len(line) for line in lines) if lines else 0
            
            # Pad all rows to have the same number of columns for preview
            padded_lines = []
            for line in lines:
                padded_line = line + [''] * (max_cols - len(line))
                padded_lines.append(padded_line[:max_cols])
            
            # Convert to DataFrame for preview
            df_preview = pd.DataFrame(padded_lines)
            df_preview = df_preview.fillna('')
            
            # 🔧 FIX: Use actual header names if header_row is specified
            column_names = [f"Column_{i}" for i in range(len(df_preview.columns))]
            
            # If header_row is specified and valid, use actual headers
            if header_row is not None and 0 <= header_row < len(lines):
                actual_headers = lines[header_row][:max_cols]
                # Clean up headers (remove BOM, strip whitespace)
                cleaned_headers = []
                for header in actual_headers:
                    if header:
                        # Remove BOM character if present
                        clean_header = header.replace('\ufeff', '').strip()
                        cleaned_headers.append(clean_header)
                    else:
                        cleaned_headers.append(f"Column_{len(cleaned_headers)}")
                
                # Pad headers to match column count
                while len(cleaned_headers) < max_cols:
                    cleaned_headers.append(f"Column_{len(cleaned_headers)}")
                
                column_names = cleaned_headers[:max_cols]
                print(f"      📝 Using actual headers from row {header_row}: {column_names}")
            else:
                print(f"      📝 Using generic column names: {column_names[:5]}...")
            
            result = {
                'success': True,
                'total_rows': len(df_preview),
                'total_columns': len(df_preview.columns),
                'preview_data': df_preview.to_dict('records'),
                'column_names': column_names
            }
            
            # 🆕 Add header detection info to result if available
            if detected_header_info:
                result['header_detection'] = detected_header_info
                result['suggested_header_row'] = detected_header_info['header_row']
                result['suggested_data_start_row'] = detected_header_info['data_start_row']
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def read_csv_lines(self, file_path: str, encoding: str = 'utf-8') -> List[List[str]]:
        """Read CSV file as list of lines with manual parsing"""
        # Try utf-8-sig first to handle BOM characters properly
        if encoding == 'utf-8':
            encoding = 'utf-8-sig'
            print(f"      🔧 Using utf-8-sig encoding to handle BOM characters")
        
        lines = []
        with open(file_path, 'r', encoding=encoding, newline='') as f:
            reader = csv.reader(f, quotechar='"', skipinitialspace=True)
            for row in reader:
                lines.append(row)
        return lines
    
    def parse_with_range(self, file_path: str, start_row: int, end_row: Optional[int] = None, 
                        start_col: int = 0, end_col: Optional[int] = None, 
                        encoding: str = 'utf-8', header_row: Optional[int] = None) -> Dict:
        """Parse CSV with specified range using manual CSV reading for compatibility"""
        try:
            print(f"🔍 Parsing CSV: {file_path}")
            print(f"   📊 Range: start_row={start_row}, end_row={end_row}, start_col={start_col}, end_col={end_col}")
            print(f"   📋 Header row: {header_row}")
            
            # Try utf-8-sig first to handle BOM characters properly
            if encoding == 'utf-8':
                encoding = 'utf-8-sig'
                print(f"      🔧 Using utf-8-sig encoding to handle BOM characters")
            
            # Read all lines
            lines = self.read_csv_lines(file_path, encoding)
            
            if not lines:
                raise ValueError("No data could be parsed from file")
            
            print(f"   ✅ Successfully read CSV manually: {len(lines)} lines")
            
            # Extract the specified range
            if end_row is None:
                end_row = len(lines)
            # If end_col is None (not specified in the bank's .conf file),
            # it means we should parse all columns from start_col to the end of the line.
            # The Python slice [start:None] handles this行为 correctly, so no default needed here.
            # The previous default 'end_col = 5' was specific to NayaPay and caused issues for other banks.
            
            print(f"   🔄 Extracting range: rows {start_row}:{end_row}, cols {start_col}:{end_col}")
            
            # 🔧 CRITICAL FIX: Use separate header_row and data_start_row
            actual_header_row = header_row if header_row is not None else start_row
            actual_data_start_row = start_row
            
            print(f"   🔧 Using header_row={actual_header_row}, data_start_row={actual_data_start_row}")
            
            # Extract header row
            if actual_header_row >= len(lines):
                raise ValueError(f"Header row {actual_header_row} is beyond file length {len(lines)}")
            
            headers = lines[actual_header_row][start_col:end_col]
            print(f"   📋 Headers extracted from row {actual_header_row}: {headers}")
            
            # Debug BOM on headers - INLINE DEBUG
            if headers:
                first_header = headers[0]
                if '\ufeff' in first_header:
                    print(f"      ⚠️ BOM character detected in header: '{first_header}' (should be cleaned by utf-8-sig)")
                else:
                    print(f"      ✅ No BOM character in first header: '{first_header}'")
            
            # Extract data rows (starting from actual_data_start_row)
            data_rows = []
            for i in range(actual_data_start_row, min(end_row, len(lines))):
                # Check if the current line index is valid
                # and if the line has enough columns if end_col is specified.
                # If end_col is None, we parse all available columns from start_col.
                line_is_valid_for_slicing = (i < len(lines) and 
                                             (end_col is None or len(lines[i]) >= end_col))
                if line_is_valid_for_slicing:
                    row_data = lines[i][start_col:end_col]
                    # Only include rows with meaningful data
                    if any(cell.strip() for cell in row_data):
                        row_dict = dict(zip(headers, row_data))
                        data_rows.append(row_dict)
            
            print(f"   📊 Data rows extracted: {len(data_rows)}")
            
            # Debug: Show first few rows of parsed data
            print(f"   📋 First 3 parsed rows:")
            for i, row in enumerate(data_rows[:3]):
                timestamp = row.get('TIMESTAMP', 'N/A')
                amount = row.get('AMOUNT', 'N/A')
                trans_type = row.get('TYPE', 'N/A')
                # Also try Wise headers
                date = row.get('Date', 'N/A')
                wise_amount = row.get('Amount', 'N/A')
                description = row.get('Description', 'N/A')
                print(f"      Row {i}: {timestamp} | {amount} | {trans_type} | {date} | {wise_amount} | {description}")
            
            return {
                'success': True,
                'headers': headers,
                'data': data_rows,
                'row_count': len(data_rows)
            }
        except Exception as e:
            print(f"   ❌ Parse error: {str(e)}")
            import traceback
            print(f"   📚 Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': str(e)
            }
