import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re
import csv
import os
import sys

# Add transformation directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'transformation'))

try:
    from universal_transformer import UniversalTransformer
    UNIVERSAL_TRANSFORMER_AVAILABLE = True
    print("✅ Universal Transformer imported successfully in enhanced_csv_parser")
except ImportError as e:
    print(f"❌ Universal Transformer import failed: {e}")
    UNIVERSAL_TRANSFORMER_AVAILABLE = False

class EnhancedCSVParser:
    def __init__(self):
        self.target_columns = ['Date', 'Amount', 'Category', 'Title', 'Note', 'Account']
        
        # Initialize Universal Transformer
        if UNIVERSAL_TRANSFORMER_AVAILABLE:
            try:
                self.universal_transformer = UniversalTransformer()
                print("✅ Universal Transformer initialized in enhanced_csv_parser")
            except Exception as e:
                print(f"❌ Universal Transformer initialization failed: {e}")
                self.universal_transformer = None
        else:
            print("⚠️  Universal Transformer not available, using legacy transformation")
            self.universal_transformer = None
    
    def preview_csv(self, file_path: str, encoding: str = 'utf-8') -> Dict:
        """Preview CSV file and return basic info using robust CSV reading"""
        try:
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
        """Auto-detect where the actual transaction data starts with improved NayaPay detection"""
        try:
            # Use manual CSV reading to handle inconsistent column counts
            lines = []
            with open(file_path, 'r', encoding=encoding, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    lines.append(row)
            
            if not lines:
                raise ValueError("No data found in file")
            
            print(f"🔍 Detecting data range in file with {len(lines)} lines")
            
            # Look for rows that contain transaction headers
            data_start_row = None
            
            for idx, row in enumerate(lines):
                # Convert row to lowercase string for searching
                row_text = ' '.join([str(cell).lower() for cell in row if cell])
                
                print(f"   Row {idx:2}: {len(row)} cols -> {row_text[:80]}..." if len(row_text) > 80 else f"   Row {idx:2}: {len(row)} cols -> {row_text}")
                
                # Enhanced NayaPay detection: look for the specific transaction header pattern
                # Must have exactly these 5 columns: TIMESTAMP, TYPE, DESCRIPTION, AMOUNT, BALANCE
                if (len(row) == 5 and 
                    any('timestamp' in str(cell).lower() for cell in row) and
                    any('type' in str(cell).lower() for cell in row) and
                    any('description' in str(cell).lower() for cell in row) and
                    any('amount' in str(cell).lower() for cell in row) and
                    any('balance' in str(cell).lower() for cell in row)):
                    
                    data_start_row = idx
                    print(f"   ✅ Found NayaPay transaction headers at row {idx}: {row}")
                    break
                
                # Skip problematic rows we know about
                if ('opening balance' in row_text and 'closing balance' in row_text):
                    print(f"   ⚠️  Skipping balance summary row {idx}")
                    continue
            
            if data_start_row is None:
                # Fallback: look for any row with transaction-like headers
                for idx, row in enumerate(lines):
                    row_text = ' '.join([str(cell).lower() for cell in row if cell])
                    if any(indicator in row_text for indicator in ['timestamp', 'date', 'amount', 'description']):
                        if not ('opening balance' in row_text or 'closing balance' in row_text):
                            data_start_row = idx
                            print(f"   🔄 Fallback: Found headers at row {idx}")
                            break
            
            print(f"   🎯 Final detection result: row {data_start_row}")
            
            return {
                'success': True,
                'suggested_header_row': data_start_row,
                'total_rows': len(lines)
            }
        except Exception as e:
            print(f"   ❌ Detection error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def parse_with_range(self, file_path: str, start_row: int, end_row: Optional[int] = None, 
                        start_col: int = 0, end_col: Optional[int] = None, 
                        encoding: str = 'utf-8') -> Dict:
        """Parse CSV with specified range using manual CSV reading for NayaPay compatibility"""
        try:
            print(f"🔍 Parsing CSV: {file_path}")
            print(f"   📊 Range: start_row={start_row}, end_row={end_row}, start_col={start_col}, end_col={end_col}")
            
            # Use manual CSV reading to handle inconsistent column counts
            lines = []
            with open(file_path, 'r', encoding=encoding, newline='') as f:
                reader = csv.reader(f, quotechar='"', skipinitialspace=True)
                for line_num, row in enumerate(reader):
                    lines.append(row)
            
            if not lines:
                raise ValueError("No data could be parsed from file")
            
            print(f"   ✅ Successfully read CSV manually: {len(lines)} lines")
            
            # Extract the specified range
            if end_row is None:
                end_row = len(lines)
            if end_col is None:
                end_col = 5  # Default to 5 for NayaPay
            
            print(f"   🔄 Extracting range: rows {start_row}:{end_row}, cols {start_col}:{end_col}")
            
            # Extract header row
            if start_row >= len(lines):
                raise ValueError(f"Start row {start_row} is beyond file length {len(lines)}")
            
            headers = lines[start_row][start_col:end_col]
            print(f"   📋 Headers extracted: {headers}")
            
            # Extract data rows (starting from the row after headers)
            data_rows = []
            for i in range(start_row + 1, min(end_row, len(lines))):
                if i < len(lines) and len(lines[i]) >= end_col:
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
                print(f"      Row {i}: {timestamp} | {amount} | {trans_type}")
            
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
    
    def transform_to_cashew(self, data: List[Dict], column_mapping: Dict[str, str], 
                           bank_name: str = "", categorization_rules: List[Dict] = None,
                           default_category_rules: Dict = None, account_mapping: Dict = None,
                           bank_rules_settings: Dict[str, bool] = None) -> List[Dict]:
        """Transform parsed data to Cashew format with smart categorization"""
        
        # Use Universal Transformer if available
        if self.universal_transformer:
            print(f"\n🌟 USING UNIVERSAL TRANSFORMER")
            return self.universal_transformer.transform_to_cashew(
                data, column_mapping, bank_name, account_mapping, bank_rules_settings
            )
        
        # Fallback to legacy transformation
        print(f"\n🔄 USING LEGACY TRANSFORMATION")
        cashew_data = []
        
        print(f"   🏦 Bank: {bank_name}")
        print(f"   📋 Input rows: {len(data)}")
        print(f"   🗺️ Column mapping: {column_mapping}")
        
        for idx, row in enumerate(data):
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
                        original_amount = str(row[source_col])
                        parsed_amount = self._parse_amount(original_amount)
                        cashew_row[cashew_col] = parsed_amount
                        
                        # Debug amount parsing for first few rows
                        if idx < 3:
                            print(f"   💰 Row {idx} Amount: '{original_amount}' → '{parsed_amount}'")
                    elif cashew_col == 'Account' and account_mapping:
                        # Use currency-based account mapping
                        currency = str(row[source_col])
                        cashew_row[cashew_col] = account_mapping.get(currency, bank_name)
                    else:
                        cashew_row[cashew_col] = str(row[source_col])
            
            # Debug first few rows
            if idx < 3:
                print(f"   📋 Row {idx}: Date='{cashew_row['Date']}', Amount='{cashew_row['Amount']}', Title='{cashew_row['Title'][:50]}...'")
            
            # Only process rows with valid amount
            if cashew_row['Amount'] and cashew_row['Amount'] != '0':
                # Apply categorization rules
                cashew_row = self._apply_categorization_rules(
                    cashew_row, row, categorization_rules, default_category_rules
                )
                cashew_data.append(cashew_row)
            else:
                if idx < 5:  # Log first few skipped rows
                    print(f"   ⚠️  Skipping row {idx}: Invalid/zero amount '{cashew_row['Amount']}'")
        
        print(f"   ✅ Transformation complete: {len(cashew_data)} valid rows")
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
                elif 'clean_description' in actions:
                    # Clean and shorten the description using regex pattern
                    clean_config = actions['clean_description']
                    cleaned_desc = self._clean_description(original_row, clean_config)
                    cashew_row['Title'] = cleaned_desc
                elif not actions.get('keep_original_title', False):
                    # Keep original title if not specified otherwise
                    pass
                
                # Rule matched - check if we should continue processing
                if not actions.get('continue_processing', False):
                    # Stop processing further rules unless explicitly told to continue
                    break
        
        # Apply default categorization if no category was set
        if not cashew_row['Category']:
            cashew_row = self._apply_default_categorization(cashew_row, default_category_rules)
        
        return cashew_row
    
    def _check_rule_conditions(self, row: Dict, conditions: Dict) -> bool:
        """Check if a row matches the given conditions"""
        if not conditions:
            return False
        
        # Handle old-style conditions
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
    
    def _clean_description(self, row: Dict, clean_config: Dict) -> str:
        """Clean and shorten transaction descriptions"""
        from_field = clean_config.get('from_field', 'DESCRIPTION')
        rules = clean_config.get('rules', [])
        default = clean_config.get('default', 'Transaction')
        
        if from_field not in row:
            return default
        
        description = str(row[from_field])
        
        try:
            for rule in rules:
                pattern = rule.get('pattern')
                replacement = rule.get('replacement', '')
                if pattern:
                    description = re.sub(pattern, replacement, description, flags=re.IGNORECASE | re.MULTILINE)
            
            # Clean up extra whitespace and newlines
            description = re.sub(r'\s+', ' ', description).strip()
            
            return description if description else default
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
        if not date_str or str(date_str).strip() == '' or str(date_str).lower() == 'nan':
            return ''
            
        date_str = str(date_str).strip()
        
        # Common date patterns
        try:
            # Pattern for "02 Feb 2025 11:17 PM"
            if re.match(r'\d{2} \w{3} \d{4} \d{1,2}:\d{2} (AM|PM)', date_str):
                dt = datetime.strptime(date_str, '%d %b %Y %I:%M %p')
                return dt.strftime('%Y-%m-%d')
            
            # Pattern for "05 Feb 2025 09:17 AM" (zero-padded hour)
            if re.match(r'\d{2} \w{3} \d{4} \d{2}:\d{2} (AM|PM)', date_str):
                dt = datetime.strptime(date_str, '%d %b %Y %I:%M %p')
                return dt.strftime('%Y-%m-%d')
            
            # Try other common formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%d-%m-%Y %H:%M:%S']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            return date_str  # Return original if can't parse
        except Exception as e:
            print(f"⚠️  Date parsing error for '{date_str}': {e}")
            return date_str
    
    def _parse_amount(self, amount_str: str) -> str:
        """Parse amount string and return clean number"""
        try:
            # Handle empty or null values
            if not amount_str or str(amount_str).strip() == '' or str(amount_str).lower() == 'nan':
                return '0'
            
            amount_str = str(amount_str).strip()
            
            # Remove quotes first
            amount_str = amount_str.strip('"').strip("'")
            
            # Remove currency symbols, commas, spaces - keep only digits, decimal points, and minus/plus signs
            cleaned = re.sub(r'[^0-9.\-+]', '', amount_str)
            
            # Handle negative signs and parentheses from original string
            is_negative = False
            if (amount_str.startswith('-') or amount_str.startswith('(') or 
                amount_str.endswith(')') or '(' in amount_str):
                is_negative = True
            elif amount_str.startswith('+'):
                is_negative = False
            
            # Clean up the number
            cleaned = cleaned.lstrip('+-')
            
            # Apply negative if needed
            if is_negative and not cleaned.startswith('-'):
                cleaned = '-' + cleaned
            
            # Convert to float and back to string to standardize
            if cleaned:
                return str(float(cleaned))
            else:
                return '0'
        except Exception as e:
            print(f"⚠️  Amount parsing error for '{amount_str}': {e}")
            return '0'
    
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
