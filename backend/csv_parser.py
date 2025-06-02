import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re

class CSVParser:
    def __init__(self):
        self.target_columns = ['Date', 'Amount', 'Category', 'Title', 'Note', 'Account']
    
    def preview_csv(self, file_path: str, encoding: str = 'utf-8') -> Dict:
        """Preview CSV file and return basic info"""
        try:
            # Read first 20 rows to identify structure
            df_preview = pd.read_csv(file_path, encoding=encoding, nrows=20, header=None)
            
            # Replace NaN values with empty strings for JSON serialization
            df_preview = df_preview.fillna('')
            
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
            df = pd.read_csv(file_path, encoding=encoding, header=None)
            
            # Look for rows that might contain headers
            header_indicators = ['timestamp', 'date', 'amount', 'description', 'balance', 'type']
            data_start_row = None
            
            for idx, row in df.iterrows():
                row_text = ' '.join([str(cell).lower() for cell in row if pd.notna(cell)])
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
            # Read the full file first
            df_full = pd.read_csv(file_path, encoding=encoding, header=None)
            
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
    
    def transform_to_cashew(self, data: List[Dict], column_mapping: Dict[str, str], 
                           bank_name: str = "") -> List[Dict]:
        """Transform parsed data to Cashew format"""
        cashew_data = []
        
        for row in data:
            cashew_row = {
                'Date': '',
                'Amount': '',
                'Category': '',
                'Title': '',
                'Note': '',
                'Account': bank_name
            }
            
            # Map columns based on mapping
            for cashew_col, source_col in column_mapping.items():
                if source_col in row and pd.notna(row[source_col]):
                    if cashew_col == 'Date':
                        # Parse and format date
                        cashew_row[cashew_col] = self._parse_date(str(row[source_col]))
                    elif cashew_col == 'Amount':
                        # Clean and format amount
                        cashew_row[cashew_col] = self._parse_amount(str(row[source_col]))
                    else:
                        cashew_row[cashew_col] = str(row[source_col])
            
            # Only add rows with valid amount
            if cashew_row['Amount']:
                cashew_data.append(cashew_row)
        
        return cashew_data
    
    def _parse_date(self, date_str: str) -> str:
        """Parse various date formats and return ISO format"""
        date_str = date_str.strip()
        
        # Common date patterns
        patterns = [
            r'(\d{2}) (\w{3}) (\d{4}) (\d{1,2}):(\d{2}) (AM|PM)',  # "02 Feb 2025 11:17 PM"
            r'(\d{4}-\d{2}-\d{2})',  # "2025-02-02"
            r'(\d{2}/\d{2}/\d{4})',  # "02/02/2025"
            r'(\d{2}-\d{2}-\d{4})',  # "02-02-2025"
        ]
        
        try:
            # Pattern for "02 Feb 2025 11:17 PM"
            if re.match(r'\d{2} \w{3} \d{4} \d{1,2}:\d{2} (AM|PM)', date_str):
                dt = datetime.strptime(date_str, '%d %b %Y %I:%M %p')
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Try other common formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue
            
            return date_str  # Return original if can't parse
        except Exception:
            return date_str
    
    def _parse_amount(self, amount_str: str) -> str:
        """Parse amount string and return clean number"""
        try:
            # Remove currency symbols, commas, spaces
            cleaned = re.sub(r'[^\d.-+]', '', amount_str.replace(',', ''))
            
            # Handle negative signs
            if amount_str.startswith('-') or amount_str.startswith('('):
                if not cleaned.startswith('-'):
                    cleaned = '-' + cleaned.lstrip('+-')
            elif amount_str.startswith('+'):
                cleaned = cleaned.lstrip('+-')
            
            # Convert to float and back to string to standardize
            return str(float(cleaned))
        except Exception:
            return amount_str
    
    def save_template(self, template_name: str, config: Dict, template_dir: str = "templates"):
        """Save parsing template for reuse"""
        template_path = f"{template_dir}/{template_name}.json"
        with open(template_path, 'w') as f:
            json.dump(config, f, indent=2)
        return template_path
    
    def load_template(self, template_name: str, template_dir: str = "templates"):
        """Load saved parsing template"""
        template_path = f"{template_dir}/{template_name}.json"
        with open(template_path, 'r') as f:
            return json.load(f)


# Test with NayaPay statement
if __name__ == "__main__":
    parser = CSVParser()
    
    # Test with the NayaPay file
    file_path = "../nayapay_statement.csv"
    
    print("=== CSV Preview ===")
    preview = parser.preview_csv(file_path)
    if preview['success']:
        print(f"Rows: {preview['total_rows']}, Columns: {preview['total_columns']}")
    
    print("\n=== Auto-detect Data Range ===")
    detection = parser.detect_data_range(file_path)
    if detection['success']:
        print(f"Suggested header row: {detection['suggested_header_row']}")
    
    print("\n=== Parse Data Range ===")
    # Based on the NayaPay format, data starts at row 14
    parsed = parser.parse_with_range(file_path, start_row=14, start_col=0, end_col=5)
    if parsed['success']:
        print(f"Headers: {parsed['headers']}")
        print(f"Rows parsed: {parsed['row_count']}")
        print("First few rows:")
        for i, row in enumerate(parsed['data'][:3]):
            print(f"  {i+1}: {row}")
    
    print("\n=== Transform to Cashew Format ===")
    # Define column mapping for NayaPay
    nayapay_mapping = {
        'Date': 'TIMESTAMP',
        'Amount': 'AMOUNT', 
        'Title': 'DESCRIPTION',
        'Note': 'TYPE',
        'Category': '',  # Will be empty for now
    }
    
    if parsed['success']:
        cashew_data = parser.transform_to_cashew(parsed['data'], nayapay_mapping, "NayaPay")
        print(f"Converted {len(cashew_data)} transactions")
        print("First few converted rows:")
        for i, row in enumerate(cashew_data[:3]):
            print(f"  {i+1}: {row}")
        
        # Save as CSV
        df_cashew = pd.DataFrame(cashew_data)
        output_path = "../converted_nayapay.csv"
        df_cashew.to_csv(output_path, index=False)
        print(f"\nSaved converted data to: {output_path}")
