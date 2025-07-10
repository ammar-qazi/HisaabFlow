"""
Utility functions for CSV parsing operations
"""
import re
from typing import List, Dict, Any, Optional

def clean_header(header: str) -> str:
    """Clean header text by removing BOM and extra whitespace"""
    if not header:
        return ""
    
    # Remove BOM character
    clean = header.replace('\ufeff', '')
    
    # Strip whitespace
    clean = clean.strip()
    
    # Replace problematic characters
    clean = clean.replace('\x00', '')  # NULL bytes
    
    return clean

def normalize_column_count(rows: List[List[str]], max_cols: Optional[int] = None) -> List[List[str]]:
    """Normalize all rows to have the same number of columns"""
    if not rows:
        return []
    
    # Determine target column count
    if max_cols is None:
        max_cols = max(len(row) for row in rows) if rows else 0
    
    # Pad all rows to target column count
    normalized = []
    for row in rows:
        padded_row = row[:max_cols]  # Truncate if too long
        padded_row.extend([''] * (max_cols - len(padded_row)))  # Pad if too short
        normalized.append(padded_row)
    
    return normalized

def detect_empty_columns(rows: List[List[str]], threshold: float = 0.9) -> List[int]:
    """Detect columns that are mostly empty"""
    if not rows:
        return []
    
    col_count = len(rows[0]) if rows else 0
    empty_columns = []
    
    for col_idx in range(col_count):
        empty_count = 0
        total_count = 0
        
        for row in rows:
            if col_idx < len(row):
                total_count += 1
                if not row[col_idx] or not row[col_idx].strip():
                    empty_count += 1
        
        if total_count > 0 and (empty_count / total_count) >= threshold:
            empty_columns.append(col_idx)
    
    return empty_columns

def validate_csv_structure(headers: List[str], data_rows: List[List[str]]) -> Dict[str, Any]:
    """Validate CSV structure and return analysis"""
    issues = []
    warnings = []
    
    # Check headers
    if not headers:
        issues.append("No headers found")
    else:
        # Check for duplicate headers
        seen_headers = {}
        for i, header in enumerate(headers):
            clean = clean_header(header)
            if not clean:
                warnings.append(f"Empty header at column {i}")
            elif clean in seen_headers:
                warnings.append(f"Duplicate header '{clean}' at columns {seen_headers[clean]} and {i}")
            else:
                seen_headers[clean] = i
    
    # Check data consistency
    if data_rows:
        expected_cols = len(headers) if headers else 0
        inconsistent_rows = []
        
        for i, row in enumerate(data_rows[:10]):  # Check first 10 rows
            if len(row) != expected_cols:
                inconsistent_rows.append({
                    'row': i,
                    'expected': expected_cols,
                    'actual': len(row)
                })
        
        if inconsistent_rows:
            warnings.append(f"Inconsistent column counts in {len(inconsistent_rows)} rows")
    
    # Determine overall validity
    is_valid = len(issues) == 0
    
    return {
        'valid': is_valid,
        'issues': issues,
        'warnings': warnings,
        'header_count': len(headers) if headers else 0,
        'data_row_count': len(data_rows),
        'empty_columns': detect_empty_columns([headers] + data_rows) if headers and data_rows else []
    }

def sanitize_for_json(obj: Any) -> Any:
    """Sanitize data structure for JSON serialization"""
    if isinstance(obj, dict):
        return {key: sanitize_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, (int, float, bool, type(None))):
        return obj
    else:
        # Convert to string and handle NaN/None values
        str_val = str(obj)
        if str_val.lower() in ['nan', 'none', 'null']:
            return ''
        return str_val

def generate_column_names(count: int, prefix: str = "Column") -> List[str]:
    """Generate generic column names"""
    return [f"{prefix}_{i}" for i in range(count)]

def estimate_data_types(rows: List[List[str]], sample_size: int = 100) -> Dict[int, str]:
    """Estimate data types for each column"""
    if not rows:
        return {}
    
    col_count = len(rows[0]) if rows else 0
    type_estimates = {}
    
    # Sample rows for analysis
    sample_rows = rows[:sample_size]
    
    for col_idx in range(col_count):
        values = []
        for row in sample_rows:
            if col_idx < len(row) and row[col_idx].strip():
                values.append(row[col_idx].strip())
        
        if not values:
            type_estimates[col_idx] = 'text'
            continue
        
        # Test for numeric types
        numeric_count = 0
        date_count = 0
        
        for value in values[:20]:  # Test first 20 non-empty values
            # Test for numbers
            if re.match(r'^-?\d+(\.\d+)?$', value) or re.match(r'^-?\d{1,3}(,\d{3})*(\.\d+)?$', value):
                numeric_count += 1
            
            # Test for dates
            if re.match(r'^\d{4}[-./]\d{1,2}[-./]\d{1,2}$', value) or re.match(r'^\d{1,2}[-./]\d{1,2}[-./]\d{4}$', value):
                date_count += 1
        
        total_tested = len(values[:20])
        if total_tested == 0:
            type_estimates[col_idx] = 'text'
        elif numeric_count / total_tested > 0.7:
            type_estimates[col_idx] = 'numeric'
        elif date_count / total_tested > 0.7:
            type_estimates[col_idx] = 'date'
        else:
            type_estimates[col_idx] = 'text'
    
    return type_estimates

def is_nuitka_executable() -> bool:
    """Check if running in Nuitka compiled executable"""
    import sys
    
    # Nuitka sets __compiled__ attribute
    if hasattr(sys, '__compiled__'):
        return True
    
    # Check for common Nuitka executable indicators
    if hasattr(sys, 'frozen') and sys.frozen:
        return True
        
    # Check if executable name suggests Nuitka compilation
    if sys.executable and 'hisaabflow-backend' in sys.executable:
        return True
        
    return False

def get_nuitka_config_dir() -> Optional[str]:
    """Get config directory for Nuitka executable"""
    import os
    import sys
    
    # Try to find configs directory relative to executable
    if sys.executable:
        # Get the directory containing the executable
        exec_dir = os.path.dirname(os.path.abspath(sys.executable))
        
        # Check common Nuitka bundling locations
        possible_paths = [
            os.path.join(exec_dir, 'configs'),  # Same directory as executable
            os.path.join(exec_dir, '..', 'configs'),  # Parent directory
            os.path.join(exec_dir, 'backend', 'configs'),  # In backend subdirectory
        ]
        
        for config_path in possible_paths:
            abs_config_path = os.path.abspath(config_path)
            if os.path.exists(abs_config_path):
                print(f"[Nuitka] Found config directory: {abs_config_path}")
                return abs_config_path
        
        print(f"[WARNING] [Nuitka] Config directory not found. Checked: {possible_paths}")
    
    return None

def get_user_config_dir() -> Optional[str]:
    """Get user config directory from environment variable, fallback to default"""
    import os
    import sys
    
    # Check environment variable set by Electron launcher
    user_config_dir = os.environ.get('HISAABFLOW_CONFIG_DIR')
    if user_config_dir and os.path.exists(user_config_dir):
        return user_config_dir
    
    # Check if user directory exists
    user_dir = os.environ.get('HISAABFLOW_USER_DIR')
    if user_dir:
        config_path = os.path.join(user_dir, 'configs')
        if os.path.exists(config_path):
            return config_path
    
    # Check for Nuitka runtime environment
    if is_nuitka_executable():
        nuitka_config_dir = get_nuitka_config_dir()
        if nuitka_config_dir and os.path.exists(nuitka_config_dir):
            print(f"[START] [HisaabFlow] Using Nuitka bundled config directory: {nuitka_config_dir}")
            return nuitka_config_dir
    
    # Fallback to default (None means use default behavior)
    return None

def get_config_dir_for_manager() -> Optional[str]:
    """Get config directory for BankConfigManager with fallback"""
    user_config = get_user_config_dir()
    if user_config:
        print(f"[USER] [HisaabFlow] Using user config directory: {user_config}")
        return user_config
    
    print("[BUILD] [HisaabFlow] Using default config directory")
    return None