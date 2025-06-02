import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re

class EnhancedCSVParser:
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
                           bank_name: str = "", categorization_rules: List[Dict] = None,
                           default_category_rules: Dict = None) -> List[Dict]:
        """Transform parsed data to Cashew format with smart categorization"""
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
            
            # Only process rows with valid amount
            if cashew_row['Amount']:
                # Apply categorization rules
                cashew_row = self._apply_categorization_rules(
                    cashew_row, row, categorization_rules, default_category_rules
                )
                cashew_data.append(cashew_row)
        
        return cashew_data
    
    def _apply_categorization_rules(self, cashew_row: Dict, original_row: Dict, 
                                   categorization_rules: List[Dict] = None,
                                   default_category_rules: Dict = None) -> Dict:
        """Apply categorization rules to determine category and title"""
        
        if not categorization_rules:
            return self._apply_default_categorization(cashew_row, default_category_rules)
        
        # Sort rules by priority (lower number = higher priority)
        sorted_rules = sorted(categorization_rules, key=lambda x: x.get('priority', 999))
        
        for rule in sorted_rules:
            if self._check_rule_conditions(original_row, rule.get('conditions', {})):
                # Apply the rule actions
                actions = rule.get('actions', {})
                
                # Set category
                if 'set_category' in actions:
                    cashew_row['Category'] = actions['set_category']
                
                # Set title
                if 'set_title' in actions:
                    cashew_row['Title'] = actions['set_title']
                elif 'set_title_template' in actions:
                    # Handle template with name extraction
                    template = actions['set_title_template']
                    if 'extract_name' in actions:
                        extracted_name = self._extract_name(original_row, actions['extract_name'])
                        cashew_row['Title'] = template.format(extract_name=extracted_name)
                    else:
                        cashew_row['Title'] = template
                elif not actions.get('keep_original_title', False):
                    # Keep original title if not specified otherwise
                    pass
                
                # Rule matched, stop processing further rules
                break
        
        # Apply default categorization if no category was set
        if not cashew_row['Category']:
            cashew_row = self._apply_default_categorization(cashew_row, default_category_rules)
        
        return cashew_row
    
    def _check_rule_conditions(self, row: Dict, conditions: Dict) -> bool:
        """Check if a row matches the given conditions"""
        if not conditions:
            return False
        
        if 'and' in conditions:
            return all(self._check_single_condition(row, cond) for cond in conditions['and'])
        elif 'or' in conditions:
            return any(self._check_single_condition(row, cond) for cond in conditions['or'])
        else:
            return self._check_single_condition(row, conditions)
    
    def _check_single_condition(self, row: Dict, condition: Dict) -> bool:
        """Check a single condition against a row"""
        field = condition.get('field')
        operator = condition.get('operator')
        value = condition.get('value')
        case_sensitive = condition.get('case_sensitive', True)
        
        if field not in row:
            return False
        
        field_value = str(row[field])
        if not case_sensitive:
            field_value = field_value.lower()
            value = str(value).lower() if value is not None else ''
        
        if operator == 'equals':
            return field_value == str(value)
        elif operator == 'contains':
            return str(value) in field_value
        elif operator == 'starts_with':
            return field_value.startswith(str(value))
        elif operator == 'ends_with':
            return field_value.endswith(str(value))
        elif operator == 'regex':
            return bool(re.search(str(value), field_value))
        elif operator == 'greater_than':
            try:
                # Clean the field value for numeric comparison
                cleaned_field = self._parse_amount(field_value)
                return float(cleaned_field) > float(value)
            except (ValueError, TypeError):
                return False
        elif operator == 'less_than':
            try:
                # Clean the field value for numeric comparison
                cleaned_field = self._parse_amount(field_value)
                return float(cleaned_field) < float(value)
            except (ValueError, TypeError):
                return False
        elif operator == 'range':
            try:
                # Clean the field value for numeric comparison
                cleaned_field = self._parse_amount(field_value)
                field_num = float(cleaned_field)
                min_val = condition.get('min', float('-inf'))
                max_val = condition.get('max', float('inf'))
                return min_val <= field_num <= max_val
            except (ValueError, TypeError):
                return False
        
        return False
    
    def _extract_name(self, row: Dict, extract_config: Dict) -> str:
        """Extract name using regex pattern"""
        from_field = extract_config.get('from_field')
        pattern = extract_config.get('pattern')
        group = extract_config.get('group', 0)
        default = extract_config.get('default', 'Unknown')
        
        if not from_field or from_field not in row:
            return default
        
        try:
            match = re.search(pattern, str(row[from_field]), re.IGNORECASE)
            if match:
                extracted = match.group(group).strip()
                return extracted if extracted else default
            return default
        except Exception:
            return default
    
    def _apply_default_categorization(self, cashew_row: Dict, default_rules: Dict = None) -> Dict:
        """Apply default categorization based on amount"""
        if not default_rules:
            default_rules = {
                "positive_amount": "Income",
                "negative_amount": "Expense",
                "zero_amount": "Transfer"
            }
        
        try:
            amount = float(cashew_row['Amount'])
            if amount > 0:
                cashew_row['Category'] = default_rules.get('positive_amount', 'Income')
            elif amount < 0:
                cashew_row['Category'] = default_rules.get('negative_amount', 'Expense')
            else:
                cashew_row['Category'] = default_rules.get('zero_amount', 'Transfer')
        except (ValueError, TypeError):
            cashew_row['Category'] = 'Uncategorized'
        
        return cashew_row
    
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
            # Remove currency symbols, commas, spaces - keep only digits, decimal points, and minus signs
            cleaned = re.sub(r'[^0-9.\-]', '', amount_str)
            
            # Handle negative signs and parentheses
            if amount_str.startswith('-') or amount_str.startswith('(') or amount_str.endswith(')'):
                if not cleaned.startswith('-'):
                    cleaned = '-' + cleaned.lstrip('-')
            elif amount_str.startswith('+'):
                cleaned = cleaned.lstrip('-')
            
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


# Example usage and testing
if __name__ == "__main__":
    parser = EnhancedCSVParser()
    
    # Load enhanced template
    template = {
        "start_row": 13,
        "end_row": None,
        "start_col": 0,
        "end_col": 5,
        "column_mapping": {
            "Date": "TIMESTAMP",
            "Amount": "AMOUNT",
            "Category": "",
            "Title": "DESCRIPTION", 
            "Note": "TYPE",
            "Account": ""
        },
        "bank_name": "NayaPay",
        "categorization_rules": [
            {
                "rule_name": "Ride Hailing Services",
                "priority": 1,
                "conditions": {
                    "and": [
                        {
                            "field": "TYPE",
                            "operator": "contains",
                            "value": "Raast Out",
                            "case_sensitive": False
                        },
                        {
                            "field": "AMOUNT",
                            "operator": "range",
                            "min": -2000,
                            "max": 0
                        }
                    ]
                },
                "actions": {
                    "set_category": "Travel",
                    "set_title": "Ride Hailing App"
                }
            }
        ],
        "default_category_rules": {
            "positive_amount": "Income",
            "negative_amount": "Expense", 
            "zero_amount": "Transfer"
        }
    }
    
    print("Enhanced CSV Parser with Categorization Rules")
    print("Template-based smart categorization system ready!")
