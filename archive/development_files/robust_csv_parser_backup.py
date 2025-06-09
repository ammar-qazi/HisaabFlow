    def _parse_nayapay_specific(self, content: str, nrows: Optional[int] = None) -> pd.DataFrame:
        """NayaPay-specific parsing for files with multiline transaction descriptions"""
        # Split by lines and process
        raw_lines = content.split('\n')
        print(f"📊 Raw lines count: {len(raw_lines)}")
        
        # Look for the header row to understand the structure
        header_row_idx = None
        for i, line in enumerate(raw_lines):
            if 'TIMESTAMP,TYPE,DESCRIPTION,AMOUNT,BALANCE' in line.upper():
                header_row_idx = i
                break
        
        processed_lines = []
        
        if header_row_idx is not None:
            print(f"📋 Header found at line {header_row_idx}")
            
            # Process lines before header normally (metadata)
            for i in range(header_row_idx + 1):
                if i < len(raw_lines):
                    # Split by comma and pad to ensure consistent columns
                    parts = raw_lines[i].split(',')
                    # Pad to at least 9 columns to match February format
                    while len(parts) < 9:
                        parts.append('')
                    processed_lines.append(parts[:9])  # Take first 9 columns
            
            # Process transaction lines after header with special multiline handling
            i = header_row_idx + 1
            while i < len(raw_lines) and (nrows is None or len(processed_lines) < nrows):
                line = raw_lines[i].strip()
                if not line:  # Skip empty lines
                    i += 1
                    continue
                
                # Check if this looks like a transaction start (has a date pattern)
                if re.match(r'^\d{2}\s+\w{3}\s+\d{4}', line):  # "05 Mar 2025" pattern
                    # This is a transaction line - collect multiline description
                    full_transaction = line
                    
                    # Look ahead for continuation lines until we find a complete transaction
                    j = i + 1
                    while j < len(raw_lines):
                        next_line = raw_lines[j].strip()
                        if not next_line:
                            j += 1
                            continue
                        
                        # If next line starts with a date, we've found the next transaction
                        if re.match(r'^\d{2}\s+\w{3}\s+\d{4}', next_line):
                            break
                            
                        # This is a continuation line - append it to description
                        full_transaction += ' ' + next_line
                        j += 1
                    
                    # Parse the complete transaction
                    # Split carefully - timestamp, type, description (quoted), amount, balance
                    parts = []
                    current_part = ''
                    in_quotes = False
                    
                    for char in full_transaction:
                        if char == '"':
                            in_quotes = not in_quotes
                            current_part += char
                        elif char == ',' and not in_quotes:
                            parts.append(current_part.strip())
                            current_part = ''
                        else:
                            current_part += char
                    
                    # Add the last part
                    if current_part:
                        parts.append(current_part.strip())
                    
                    # Ensure we have at least 5 columns (timestamp, type, description, amount, balance)
                    while len(parts) < 9:
                        parts.append('')
                    
                    processed_lines.append(parts[:9])
                    i = j  # Move to next transaction
                else:
                    # This shouldn't happen, but skip problematic lines
                    i += 1
        else:
            # No header found, process all lines normally
            for line in raw_lines:
                if nrows and len(processed_lines) >= nrows:
                    break
                parts = line.split(',')
                while len(parts) < 9:
                    parts.append('')
                processed_lines.append(parts[:9])
        
        # Create DataFrame
        df = pd.DataFrame(processed_lines)
        df.columns = range(len(df.columns))
        print(f"✅ NayaPay-specific parsing successful: {df.shape}")
        return dfimport pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re
import csv
import io

class RobustCSVParser:
    def __init__(self):
        self.target_columns = ['Date', 'Amount', 'Category', 'Title', 'Note', 'Account']
    
    def read_csv_robust(self, file_path: str, encoding: str = 'utf-8', nrows: Optional[int] = None) -> pd.DataFrame:
        """Robustly read CSV file handling inconsistent column counts and multiline descriptions"""
        try:
            print(f"🔍 Starting robust CSV read for {file_path}")
            
            # First try: Enhanced manual parsing for problematic NayaPay files
            try:
                with open(file_path, 'r', encoding=encoding, newline='') as f:
                    content = f.read()
                
                # Split by lines and process
                raw_lines = content.split('\n')
                print(f"📊 Raw lines count: {len(raw_lines)}")
                
                # Look for the header row to understand the structure
                header_row_idx = None
                for i, line in enumerate(raw_lines):
                    if 'TIMESTAMP,TYPE,DESCRIPTION,AMOUNT,BALANCE' in line.upper():
                        header_row_idx = i
                        break
                
                processed_lines = []
                
                if header_row_idx is not None:
                    print(f"📋 Header found at line {header_row_idx}")
                    
                    # Process lines before header normally (metadata)
                    for i in range(header_row_idx + 1):
                        if i < len(raw_lines):
                            # Split by comma and pad to ensure consistent columns
                            parts = raw_lines[i].split(',')
                            # Pad to at least 9 columns to match February format
                            while len(parts) < 9:
                                parts.append('')
                            processed_lines.append(parts[:9])  # Take first 9 columns
                    
                    # Process transaction lines after header with special multiline handling
                    i = header_row_idx + 1
                    while i < len(raw_lines) and (nrows is None or len(processed_lines) < nrows):
                        line = raw_lines[i].strip()
                        if not line:  # Skip empty lines
                            i += 1
                            continue
                        
                        # Check if this looks like a transaction start (has a date pattern)
                        if re.match(r'^\d{2}\s+\w{3}\s+\d{4}', line):  # "05 Mar 2025" pattern
                            # This is a transaction line - collect multiline description
                            full_transaction = line
                            
                            # Look ahead for continuation lines until we find a complete transaction
                            j = i + 1
                            while j < len(raw_lines):
                                next_line = raw_lines[j].strip()
                                if not next_line:
                                    j += 1
                                    continue
                                
                                # If next line starts with a date, we've found the next transaction
                                if re.match(r'^\d{2}\s+\w{3}\s+\d{4}', next_line):
                                    break
                                    
                                # This is a continuation line - append it to description
                                full_transaction += ' ' + next_line
                                j += 1
                            
                            # Parse the complete transaction
                            # Split carefully - timestamp, type, description (quoted), amount, balance
                            parts = []
                            current_part = ''
                            in_quotes = False
                            
                            for char in full_transaction:
                                if char == '"':
                                    in_quotes = not in_quotes
                                    current_part += char
                                elif char == ',' and not in_quotes:
                                    parts.append(current_part.strip())
                                    current_part = ''
                                else:
                                    current_part += char
                            
                            # Add the last part
                            if current_part:
                                parts.append(current_part.strip())
                            
                            # Ensure we have at least 5 columns (timestamp, type, description, amount, balance)
                            while len(parts) < 9:
                                parts.append('')
                            
                            processed_lines.append(parts[:9])
                            i = j  # Move to next transaction
                        else:
                            # This shouldn't happen, but skip problematic lines
                            i += 1
                else:
                    # No header found, process all lines normally
                    for line in raw_lines:
                        if nrows and len(processed_lines) >= nrows:
                            break
                        parts = line.split(',')
                        while len(parts) < 9:
                            parts.append('')
                        processed_lines.append(parts[:9])
                
                # Create DataFrame
                df = pd.DataFrame(processed_lines)
                df.columns = range(len(df.columns))
                print(f"✅ Enhanced parsing successful: {df.shape}")
                return df
                
            except Exception as enhanced_error:
                print(f"⚠️ Enhanced parsing failed: {enhanced_error}, trying standard methods...")
                pass
            
            # Method 2: Try pandas with better multiline handling
            try:
                df = pd.read_csv(
                    file_path, 
                    encoding=encoding, 
                    header=None,
                    nrows=nrows,
                    engine='python',
                    quoting=csv.QUOTE_MINIMAL,
                    skipinitialspace=True,
                    on_bad_lines='skip',
                    sep=',',
                    doublequote=True,
                    escapechar=None
                )
                df.columns = range(len(df.columns))
                print(f"✅ Enhanced pandas parsing successful: {df.shape}")
                return df
                
            except Exception as pandas_error:
                print(f"⚠️ Enhanced pandas failed: {pandas_error}")
                pass
            
            # Method 3: Fallback to NayaPay-specific parsing for special cases
            try:
                with open(file_path, 'r', encoding=encoding, newline='') as f:
                    content = f.read()
                
                # Check if this looks like a NayaPay file
                if 'TIMESTAMP,TYPE,DESCRIPTION,AMOUNT,BALANCE' in content.upper():
                    return self._parse_nayapay_specific(content, nrows)
                
            except Exception as nayapay_error:
                print(f"⚠️ NayaPay-specific parsing failed: {nayapay_error}")
                pass
            
            # Method 4: CSV module with proper multiline handling
            try:
                lines = []
                with open(file_path, 'r', encoding=encoding, newline='') as f:
                    reader = csv.reader(f, quoting=csv.QUOTE_MINIMAL)
                    for i, row in enumerate(reader):
                        if nrows and i >= nrows:
                            break
                        lines.append(row)
                
                if not lines:
                    raise ValueError("No data found in file")
                
                # Find the maximum number of columns
                max_cols = max(len(line) for line in lines) if lines else 0
                
                # Pad all rows to have the same number of columns
                padded_lines = []
                for line in lines:
                    padded_line = line + [''] * (max_cols - len(line))
                    padded_lines.append(padded_line)
                
                df = pd.DataFrame(padded_lines)
                # Ensure integer column names
                df.columns = range(len(df.columns))
                print(f"✅ CSV module parsing successful: {df.shape}")
                return df
                
            except Exception as csv_error:
                print(f"⚠️ CSV module failed: {csv_error}")
                pass
            
            raise ValueError("All parsing methods failed")
            
        except Exception as e:
            print(f"❌ CSV parsing completely failed: {str(e)}")
            raise ValueError(f"CSV parsing completely failed: {str(e)}")
    
    def preview_csv(self, file_path: str, encoding: str = 'utf-8') -> Dict:
        """Preview CSV file and return basic info"""
        try:
            df_preview = self.read_csv_robust(file_path, encoding, nrows=20)
            
            # Replace NaN values with empty strings for JSON serialization
            df_preview = df_preview.fillna('')
            
            # Ensure all values are JSON serializable - extra protection
            for col in df_preview.columns:
                df_preview[col] = df_preview[col].astype(str)
                df_preview[col] = df_preview[col].replace(['nan', 'NaN', 'NAN'], '')
            
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
        """Auto-detect where the actual data starts with enhanced NayaPay support"""
        try:
            df = self.read_csv_robust(file_path, encoding)
            
            # Enhanced header detection for NayaPay and other banks
            # Look for specific patterns that indicate header rows
            nayapay_headers = ['timestamp', 'type', 'description', 'amount', 'balance']
            transferwise_headers = ['date', 'amount', 'description', 'balance']
            general_headers = ['date', 'amount', 'description', 'balance', 'transaction']
            
            data_start_row = None
            best_match_score = 0
            
            print(f"🔍 Detecting headers in {file_path} ({len(df)} rows)")
            
            for idx, row in df.iterrows():
                # Get row text and clean it
                row_cells = [str(cell).lower().strip() for cell in row if pd.notna(cell) and str(cell).strip()]
                row_text = ' '.join(row_cells)
                
                # Skip obviously non-header rows (empty, customer info, etc.)
                if not row_text or len(row_cells) < 3:
                    continue
                    
                if any(skip_word in row_text for skip_word in ['customer name', 'customer address', 'account number', 'opening balance', 'closing balance']):
                    continue
                
                # Calculate match score for different header patterns
                nayapay_score = sum(1 for header in nayapay_headers if header in row_text)
                transferwise_score = sum(1 for header in transferwise_headers if header in row_text)
                general_score = sum(1 for header in general_headers if header in row_text)
                
                current_score = max(nayapay_score, transferwise_score, general_score)
                
                print(f"📋 Row {idx}: '{row_text[:100]}...' - Score: {current_score}")
                
                # NayaPay specific: look for exact header pattern
                if 'timestamp,type,description,amount,balance' in row_text.replace(' ', '').replace('\t', ','):
                    print(f"🎯 Perfect NayaPay header match at row {idx}")
                    data_start_row = idx
                    break
                
                # TransferWise specific patterns
                if 'date' in row_text and 'amount' in row_text and 'description' in row_text:
                    if current_score > best_match_score:
                        best_match_score = current_score
                        data_start_row = idx
                        print(f"📍 Better header candidate at row {idx} (score: {current_score})")
                
                # General fallback
                if current_score >= 3 and current_score > best_match_score:
                    best_match_score = current_score
                    data_start_row = idx
                    print(f"📍 General header candidate at row {idx} (score: {current_score})")
            
            if data_start_row is not None:
                print(f"✅ Header row detected at: {data_start_row}")
            else:
                print(f"⚠️ No clear header row found, defaulting to row 0")
                data_start_row = 0
            
            return {
                'success': True,
                'suggested_header_row': data_start_row,
                'total_rows': len(df),
                'detection_confidence': best_match_score
            }
        except Exception as e:
            print(f"❌ Header detection error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def parse_with_range(self, file_path: str, start_row: int, end_row: Optional[int] = None, 
                        start_col: int = 0, end_col: Optional[int] = None, 
                        encoding: str = 'utf-8') -> Dict:
        """Parse CSV with specified range"""
        try:
            print(f"🔍 Robust parser: Reading file {file_path}")
            df_full = self.read_csv_robust(file_path, encoding)
            print(f"📊 Full dataframe shape: {df_full.shape}")
            
            # Extract the specified range
            if end_row is None:
                end_row = len(df_full)
            if end_col is None:
                end_col = len(df_full.columns)
            
            print(f"🎯 Extracting range: rows {start_row}:{end_row}, cols {start_col}:{end_col}")
            
            # Extract data range using integer-based indexing
            df_range = df_full.iloc[start_row:end_row, start_col:end_col].copy()
            print(f"📏 Range dataframe shape: {df_range.shape}")
            
            # Reset index to ensure clean integer indexing
            df_range = df_range.reset_index(drop=True)
            
            # Use first row as headers if we have data
            if len(df_range) > 0:
                try:
                    # Get the first row as headers using integer indexing
                    headers = df_range.iloc[0].tolist()
                    print(f"📋 Detected headers: {headers}")
                    
                    # Clean up headers - replace empty or NaN headers
                    clean_headers = []
                    for i, header in enumerate(headers):
                        if pd.isna(header) or str(header).strip() == '' or str(header).lower() in ['nan', 'none']:
                            clean_headers.append(f'Column_{i}')
                        else:
                            clean_headers.append(str(header).strip())
                    
                    # Set column names and remove the header row
                    df_range.columns = clean_headers
                    df_range = df_range.iloc[1:].reset_index(drop=True)
                    
                    print(f"🔄 After header extraction, data rows: {len(df_range)}")
                    print(f"📋 Final headers: {list(df_range.columns)}")
                    
                except Exception as header_error:
                    print(f"⚠️ Header extraction failed: {header_error}")
                    # Fallback: use default column names
                    df_range.columns = [f'Column_{i}' for i in range(len(df_range.columns))]
                    print(f"📋 Using default headers: {list(df_range.columns)}")
            else:
                print("❌ No data in range")
                return {
                    'success': False,
                    'error': 'No data found in specified range',
                    'headers': [],
                    'data': [],
                    'row_count': 0
                }
            
            # Replace NaN values with empty strings for JSON serialization
            df_range = df_range.fillna('')
            
            # Ensure all values are JSON serializable - extra protection
            for col in df_range.columns:
                df_range[col] = df_range[col].astype(str)
                df_range[col] = df_range[col].replace(['nan', 'NaN', 'NAN'], '')
            
            # Get clean headers and data
            result_headers = [str(h) for h in df_range.columns.tolist()]
            result_data = df_range.to_dict('records')
            
            print(f"✅ Parsing successful: {len(result_headers)} headers, {len(result_data)} rows")
            
            return {
                'success': True,
                'headers': result_headers,
                'data': result_data,
                'row_count': len(result_data)
            }
        except Exception as e:
            print(f"❌ Robust parser error: {str(e)}")
            import traceback
            print(f"🔍 Full error traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': str(e),
                'headers': [],
                'data': [],
                'row_count': 0
            }

# Test the robust parser
if __name__ == "__main__":
    parser = RobustCSVParser()
    
    # Test with problematic CSV
    file_path = "../test_inconsistent.csv"
    
    print("=== Testing Enhanced Robust CSV Parser ===")
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
