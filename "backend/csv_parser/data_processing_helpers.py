from typing import Dict, List, Optional

def _extract_headers(normalized_rows: List[List[str]], header_row: Optional[int], header_indicators: List[str]) -> Dict:
    """
    Extract headers from normalized rows
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
        if 0 &lt;= header_row &lt; len(normalized_rows):
            raw_headers = normalized_rows[header_row]
            headers = [clean_header(h) for h in raw_headers]
            
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
            print(f"   ⚠️ Invalid header row {header_row}, falling back to auto-detection")
    
    best_row = 0
    best_score = 0
    best_confidence = 0.0
    
    for row_idx in range(min(5, len(normalized_rows))):
        row = normalized_rows[row_idx]
        score = 0
        
        for cell in row:
            cell_lower = str(cell).lower().strip()
            for indicator in header_indicators:
                if indicator in cell_lower:
                    score += 2
                    break
            else:
                if cell_lower and not cell_lower.replace('.', '').replace('-', '').replace(',', '').isdigit():
                    score += 1
        
        confidence = score / len(row) if row else 0
        
        if score > best_score:
            best_score = score
            best_row = row_idx
            best_confidence = confidence
    
    if best_row &lt; len(normalized_rows):
        raw_headers = normalized_rows[best_row]
        headers = [clean_header(h) for h in raw_headers]
        
        for i, header in enumerate(headers):
            if not header:
                headers[i] = f"Column_{i}"
    else:
        headers = generate_column_names(col_count)
        best_row = None
    
    return {
        'headers': headers,
        'header_row_used': best_row,
        'method': 'auto_detected',
        'confidence': best_confidence,
        'scores_tested': best_score
    }

def _extract_data_rows(normalized_rows: List[List[str]], header_row: Optional[int]) -> Dict:
    """
    Extract data rows (excluding header row)
    """
    if not normalized_rows:
        return {
            'data_rows': [],
            'skipped_header': False,
            'empty_rows_filtered': 0
        }
    
    data_start_row = 0
    skipped_header = False
    
    if header_row is not None and header_row >= 0:
        data_start_row = header_row + 1
        skipped_header = True
    
    raw_data_rows = normalized_rows[data_start_row:]
    
    data_rows = []
    empty_rows_filtered = 0
    
    for row in raw_data_rows:
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

def _convert_to_dictionaries(headers: List[str], data_rows: List[List[str]]) -> List[Dict]:
    """
    Convert data rows to list of dictionaries using headers
    """
    if not headers or not data_rows:
        return []
    
    data_dicts = []
    
    for row in data_rows:
        row_dict = {}
        for i, header in enumerate(headers):
            value = row[i] if i &lt; len(row) else ''
            row_dict[header] = value
        
        data_dicts.append(row_dict)
    
    print(f"   🔄 Converted {len(data_dicts)} rows to dictionaries")
    return data_dicts

def clean_header(header):
    return str(header).strip()

def generate_column_names(count):
    return [f"Column_{i+1}" for i in range(count)]