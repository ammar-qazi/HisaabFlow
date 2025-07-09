"""
CSV parsing strategies with automatic fallbacks
Handles multiple parsing approaches for different CSV formats
"""
import csv
import io
import pandas as pd
from typing import Dict, List, Optional
from .exceptions import DataExtractionError

class ParsingStrategies:
    """Multiple parsing approaches with automatic fallbacks"""
    
    def __init__(self):
        self.strategy_names = ['pandas', 'csv_module', 'manual']
    
    def parse_with_fallbacks(self, file_path: str, encoding: str, dialect_result: Dict, 
                           header_row: Optional[int] = None, max_rows: Optional[int] = None, 
                           start_row: Optional[int] = None) -> Dict:
        """
        Try multiple parsing strategies with fallbacks
        
        Args:
            file_path: Path to CSV file
            encoding: Detected file encoding
            dialect_result: Dialect detection results
            header_row: Optional header row index
            max_rows: Optional limit on rows to parse
            start_row: Optional starting row index (skip rows before this)
            
        Returns:
            dict: {'success': bool, 'raw_rows': List[List[str]], 'error': str, 'strategy_used': str}
        """
        print(f" Trying parsing strategies for file: {file_path}")
        
        last_error = None
        
        # Strategy 1: Try Pandas first
        print("   [DATA] Strategy 1: Pandas")
        result = self._parse_with_pandas(file_path, encoding, dialect_result, header_row, max_rows, start_row)
        if result['success']:
            print(f"   [SUCCESS] Pandas parsing succeeded")
            result['strategy_used'] = 'pandas'
            return result
        else:
            print(f"   [ERROR]  Pandas failed: {result['error']}")
            last_error = result['error']
        
        # Strategy 2: Try CSV module
        print("    Strategy 2: CSV module")
        result = self._parse_with_csv_module(file_path, encoding, dialect_result, header_row, max_rows, start_row)
        if result['success']:
            print(f"   [SUCCESS] CSV module parsing succeeded")
            result['strategy_used'] = 'csv_module'
            return result
        else:
            print(f"   [ERROR]  CSV module failed: {result['error']}")
            last_error = result['error']
        
        # Strategy 3: Manual parsing as last resort
        print("    Strategy 3: Manual parsing")
        result = self._parse_manually(file_path, encoding, dialect_result, header_row, max_rows, start_row)
        if result['success']:
            print(f"   [SUCCESS] Manual parsing succeeded")
            result['strategy_used'] = 'manual'
            return result
        else:
            print(f"   [ERROR]  Manual parsing failed: {result['error']}")
            last_error = result['error']
        
        # All strategies failed
        return {
            'success': False,
            'raw_rows': [],
            'error': f"All parsing strategies failed. Last error: {last_error}",
            'strategy_used': None
        }
    
    def _parse_with_pandas(self, file_path: str, encoding: str, dialect_result: Dict, 
                          header_row: Optional[int], max_rows: Optional[int], 
                          start_row: Optional[int] = None) -> Dict:
        """Parse using pandas with detected dialect parameters"""
        try:
            # Prepare pandas parameters
            pandas_params = {
                'filepath_or_buffer': file_path,
                'encoding': encoding,
                'sep': dialect_result.get('delimiter', ','),
                'quotechar': dialect_result.get('quotechar', '"'),
                'header': None,  # Always read as raw data first
                'dtype': str,    # Keep everything as strings initially
                'keep_default_na': False,  # Don't convert to NaN
                'na_filter': False,        # Don't interpret NA values
            }
            
            # Handle quoting parameter
            quoting = dialect_result.get('quoting', csv.QUOTE_MINIMAL)
            if quoting == csv.QUOTE_ALL:
                pandas_params['quoting'] = csv.QUOTE_ALL
            elif quoting == csv.QUOTE_NONE:
                pandas_params['quoting'] = csv.QUOTE_NONE
            
            # Add row limit if specified
            if max_rows is not None:
                pandas_params['nrows'] = max_rows
            
            # Add skipinitialspace if detected
            if dialect_result.get('skipinitialspace', False):
                pandas_params['skipinitialspace'] = True
            
            # Read CSV
            df = pd.read_csv(**pandas_params)
            
            # Convert to list of lists
            raw_rows = df.values.tolist()
            
            # Convert any NaN values to empty strings
            for i, row in enumerate(raw_rows):
                raw_rows[i] = [str(cell) if pd.notna(cell) else '' for cell in row]
            
            print(f"      [DATA] Pandas read {len(raw_rows)} rows with {len(raw_rows[0]) if raw_rows else 0} columns")
            
            return {
                'success': True,
                'raw_rows': raw_rows,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'raw_rows': [],
                'error': f"Pandas parsing error: {str(e)}"
            }
    
    def _parse_with_csv_module(self, file_path: str, encoding: str, dialect_result: Dict, 
                              header_row: Optional[int], max_rows: Optional[int], 
                              start_row: Optional[int] = None) -> Dict:
        """Parse using Python's csv module with detected dialect"""
        try:
            raw_rows = []
            
            # Create custom dialect
            class CustomDialect(csv.excel):
                delimiter = dialect_result.get('delimiter', ',')
                quotechar = dialect_result.get('quotechar', '"')
                quoting = dialect_result.get('quoting', csv.QUOTE_MINIMAL)
                skipinitialspace = dialect_result.get('skipinitialspace', True)
                lineterminator = dialect_result.get('line_terminator', '\n')
            
            # Special handling for quote-all format (Forint Bank style)
            if dialect_result.get('quoting') == csv.QUOTE_ALL:
                print(f"      Detected quote-all format, using specialized handling")
                CustomDialect.quoting = csv.QUOTE_ALL
                CustomDialect.doublequote = True
            
            # Special handling when both header_row and start_row are specified
            header_row_data = None
            if header_row is not None and start_row is not None and header_row < start_row:
                # Read the header row separately first
                with open(file_path, 'r', encoding=encoding, newline='') as csvfile:
                    reader = csv.reader(csvfile, dialect=CustomDialect)
                    for row_num, row in enumerate(reader):
                        if row_num == header_row:
                            # Clean the header row
                            clean_header_row = []
                            for cell in row:
                                if isinstance(cell, str):
                                    clean_cell = cell.replace('\ufeff', '').strip()
                                    clean_header_row.append(clean_cell)
                                else:
                                    clean_header_row.append(str(cell))
                            header_row_data = clean_header_row
                            break
            
            # Read file with custom dialect
            with open(file_path, 'r', encoding=encoding, newline='') as csvfile:
                reader = csv.reader(csvfile, dialect=CustomDialect)
                
                rows_processed = 0
                for row_num, row in enumerate(reader):
                    # If we have separate header data, include it first
                    if header_row_data is not None and rows_processed == 0:
                        raw_rows.append(header_row_data)
                        rows_processed += 1
                    
                    # Skip rows before start_row if specified
                    if start_row is not None and row_num < start_row:
                        continue
                    
                    # Apply max_rows limit to processed rows (after start_row, excluding header)
                    if max_rows is not None and rows_processed - (1 if header_row_data else 0) >= max_rows:
                        break
                    
                    # Convert all cells to strings and handle encoding issues
                    clean_row = []
                    for cell in row:
                        if isinstance(cell, str):
                            # Clean any remaining encoding artifacts
                            clean_cell = cell.replace('\ufeff', '').strip()
                            clean_row.append(clean_cell)
                        else:
                            clean_row.append(str(cell))
                    
                    raw_rows.append(clean_row)
                    rows_processed += 1
            
            start_info = f" (starting from row {start_row})" if start_row is not None else ""
            print(f"       CSV module read {len(raw_rows)} rows with {len(raw_rows[0]) if raw_rows else 0} columns{start_info}")
            
            return {
                'success': True,
                'raw_rows': raw_rows,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'raw_rows': [],
                'error': f"CSV module parsing error: {str(e)}"
            }
    
    def _parse_manually(self, file_path: str, encoding: str, dialect_result: Dict, 
                       header_row: Optional[int], max_rows: Optional[int], 
                       start_row: Optional[int] = None) -> Dict:
        """Manual parsing as fallback for problematic files"""
        try:
            raw_rows = []
            delimiter = dialect_result.get('delimiter', ',')
            quotechar = dialect_result.get('quotechar', '"')
            quoting = dialect_result.get('quoting', csv.QUOTE_MINIMAL)
            
            with open(file_path, 'r', encoding=encoding) as f:
                for line_num, line in enumerate(f):
                    if max_rows is not None and line_num >= max_rows:
                        break
                    
                    # Remove line endings
                    line = line.rstrip('\r\n')
                    if not line.strip():
                        continue
                    
                    # Manual field parsing
                    if quoting == csv.QUOTE_ALL:
                        # Special handling for quote-all format
                        fields = self._parse_quote_all_line(line, delimiter, quotechar)
                    else:
                        # Standard field splitting
                        fields = self._parse_standard_line(line, delimiter, quotechar)
                    
                    raw_rows.append(fields)
            
            print(f"       Manual parsing read {len(raw_rows)} rows with {len(raw_rows[0]) if raw_rows else 0} columns")
            
            return {
                'success': True,
                'raw_rows': raw_rows,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'raw_rows': [],
                'error': f"Manual parsing error: {str(e)}"
            }
    
    def _parse_quote_all_line(self, line: str, delimiter: str, quotechar: str) -> List[str]:
        """Parse a line where all fields are quoted (Forint Bank style)"""
        fields = []
        current_field = ""
        in_quotes = False
        i = 0
        
        while i < len(line):
            char = line[i]
            
            if char == quotechar:
                if in_quotes:
                    # Check for escaped quote (double quote)
                    if i + 1 < len(line) and line[i + 1] == quotechar:
                        current_field += quotechar
                        i += 1  # Skip the next quote
                    else:
                        # End of quoted field
                        in_quotes = False
                else:
                    # Start of quoted field
                    in_quotes = True
            elif char == delimiter and not in_quotes:
                # Field separator found
                fields.append(current_field)
                current_field = ""
            else:
                # Regular character
                current_field += char
            
            i += 1
        
        # Add the last field
        fields.append(current_field)
        
        return fields
    
    def _parse_standard_line(self, line: str, delimiter: str, quotechar: str) -> List[str]:
        """Parse a line with standard CSV rules"""
        # Simple split for now - can be enhanced if needed
        if quotechar in line:
            # Has quotes, need careful parsing
            return self._parse_quote_all_line(line, delimiter, quotechar)
        else:
            # No quotes, simple split
            return line.split(delimiter)
