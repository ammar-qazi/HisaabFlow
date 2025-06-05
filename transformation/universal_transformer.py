import json
import os
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

class UniversalTransformer:
    """
    Universal transformation engine that works across all banks
    Uses modular rules system for consistent categorization
    """
    
    def __init__(self, rules_dir: str = None):
        # Auto-detect rules directory based on current working directory
        if rules_dir is None:
            # Try multiple possible paths
            possible_paths = [
                "transformation/rules",  # When running from project root
                "../transformation/rules",  # When running from backend/
                os.path.join(os.path.dirname(__file__), 'rules'),  # Relative to this file
                os.path.join(os.path.dirname(__file__), '..', 'rules')  # Parent directory
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    rules_dir = path
                    break
            
            if rules_dir is None:
                # Default fallback
                rules_dir = "transformation/rules"
        
        self.rules_dir = rules_dir
        self.universal_rules = []
        self.bank_overrides = {}
        self.default_category_rules = {}
        
        print(f"🗂️  Universal Transformer rules directory: {self.rules_dir}")
        
        # Load rules on initialization
        self._load_universal_rules()
        self._load_bank_overrides()
    
    def _load_universal_rules(self):
        """Load universal categorization rules"""
        try:
            universal_rules_path = os.path.join(self.rules_dir, "universal_rules.json")
            if os.path.exists(universal_rules_path):
                with open(universal_rules_path, 'r') as f:
                    rules_data = json.load(f)
                    self.universal_rules = rules_data.get('rules', [])
                    self.default_category_rules = rules_data.get('default_category_rules', {
                        "positive_amount": "Income",
                        "negative_amount": "Expense", 
                        "zero_amount": "Transfer"
                    })
                print(f"✅ Loaded {len(self.universal_rules)} universal rules")
            else:
                print(f"⚠️  Universal rules file not found: {universal_rules_path}")
        except Exception as e:
            print(f"❌ Error loading universal rules: {e}")
    
    def _load_bank_overrides(self):
        """Load bank-specific rule overrides"""
        try:
            overrides_dir = os.path.join(self.rules_dir, "bank_overrides")
            if os.path.exists(overrides_dir):
                for filename in os.listdir(overrides_dir):
                    if filename.endswith('_rules.json'):
                        bank_name = filename.replace('_rules.json', '')
                        filepath = os.path.join(overrides_dir, filename)
                        
                        with open(filepath, 'r') as f:
                            override_data = json.load(f)
                            self.bank_overrides[bank_name] = override_data
                
                print(f"✅ Loaded overrides for banks: {list(self.bank_overrides.keys())}")
            else:
                print(f"⚠️  Bank overrides directory not found: {overrides_dir}")
        except Exception as e:
            print(f"❌ Error loading bank overrides: {e}")
    
    def transform_to_cashew(self, data: List[Dict], column_mapping: Dict[str, str], 
                           bank_name: str = "", account_mapping: Dict = None,
                           bank_rules_settings: Dict[str, bool] = None) -> List[Dict]:
        """
        Universal transformation to Cashew format
        
        Args:
            data: Cleaned data rows
            column_mapping: Maps Cashew columns to source columns
            bank_name: Bank identifier for specific overrides
            account_mapping: Currency to account name mapping
            
        Returns:
            List of Cashew-formatted transactions
        """
        print(f"\n🚀 UNIVERSAL TRANSFORMATION")
        print(f"   🏦 Bank: {bank_name}")
        print(f"   📊 Input rows: {len(data)}")
        print(f"   🗺️  Column mapping: {column_mapping}")
        
        # Log bank rules settings
        if bank_rules_settings:
            print(f"   ⚙️  Bank rules settings: {bank_rules_settings}")
        
        cashew_data = []
        bank_key = bank_name.lower() if bank_name else ""
        
        # Get bank-specific overrides with rule filtering
        bank_override_rules = self._get_bank_override_rules(bank_key, bank_rules_settings)
        
        for idx, row in enumerate(data):
            # Step 1: Map columns to Cashew format
            cashew_row = self._map_to_cashew_format(row, column_mapping, bank_name, account_mapping)
            
            # Step 2: Apply transformation rules (universal + bank-specific)
            cashew_row = self._apply_transformation_rules(cashew_row, row, bank_override_rules)
            
            # Step 3: Apply default categorization if still uncategorized
            if not cashew_row.get('Category'):
                cashew_row = self._apply_default_categorization(cashew_row)
            
            # Debug first few rows
            if idx < 3:
                print(f"   📋 Row {idx}: Date='{cashew_row['Date']}', Amount={cashew_row['Amount']}, Category='{cashew_row['Category']}', Title='{cashew_row['Title'][:50]}...'")
            
            # Only include rows with valid amounts
            if cashew_row['Amount'] and cashew_row['Amount'] != 0:
                cashew_data.append(cashew_row)
            else:
                if idx < 5:
                    print(f"   ⚠️  Skipping row {idx}: Invalid/zero amount")
        
        print(f"   ✅ Transformation complete: {len(cashew_data)} valid transactions")
        return cashew_data
    
    def _map_to_cashew_format(self, row: Dict, column_mapping: Dict[str, str], 
                             bank_name: str, account_mapping: Dict = None) -> Dict:
        """Map source row to Cashew format using column mapping"""
        cashew_row = {
            'Date': '',
            'Amount': 0,
            'Category': '',
            'Title': '', 
            'Note': '',
            'Account': bank_name
        }
        
        # Map each Cashew column using the mapping
        for cashew_col, source_col in column_mapping.items():
            if source_col and source_col in row and row[source_col] is not None:
                value = row[source_col]
                
                if cashew_col == 'Date':
                    cashew_row[cashew_col] = self._standardize_date(value)
                elif cashew_col == 'Amount':
                    cashew_row[cashew_col] = self._standardize_amount(value)
                elif cashew_col == 'Account' and account_mapping:
                    # Use currency-based account mapping if available
                    currency = str(value)
                    cashew_row[cashew_col] = account_mapping.get(currency, bank_name)
                else:
                    cashew_row[cashew_col] = str(value) if value is not None else ''
        
        return cashew_row
    
    def _get_bank_override_rules(self, bank_key: str, bank_rules_settings: Dict[str, bool] = None) -> List[Dict]:
        """Get combined rules for a specific bank (universal + overrides) with filtering"""
        all_rules = []
        
        # Default settings if not provided
        if bank_rules_settings is None:
            bank_rules_settings = {
                'enableNayaPayRules': True,
                'enableTransferwiseRules': True, 
                'enableUniversalRules': True
            }
        
        # Add bank-specific overrides FIRST (higher priority) if enabled
        bank_rules_enabled = False
        
        # Check if current bank's rules are enabled
        if bank_key == 'nayapay' and bank_rules_settings.get('enableNayaPayRules', True):
            bank_rules_enabled = True
        elif bank_key == 'transferwise' and bank_rules_settings.get('enableTransferwiseRules', True):
            bank_rules_enabled = True
        elif bank_key not in ['nayapay', 'transferwise']:  # Other banks default to enabled
            bank_rules_enabled = True
            
        if bank_rules_enabled and bank_key in self.bank_overrides:
            bank_data = self.bank_overrides[bank_key]
            
            # Check both 'overrides' structure and direct structure
            overrides = bank_data.get('overrides', bank_data)
            
            # Add all override categories
            for category_name, rules_list in overrides.items():
                if isinstance(rules_list, list) and category_name not in ['currency_handling', 'date_formats']:
                    print(f"   🔧 Adding {len(rules_list)} {category_name} rules for {bank_key}")
                    all_rules.extend(rules_list)
        elif not bank_rules_enabled:
            print(f"   🚫 Bank-specific rules disabled for {bank_key}")
        
        # Then add universal rules if enabled
        if bank_rules_settings.get('enableUniversalRules', True):
            all_rules.extend(self.universal_rules)
            print(f"   🌐 Universal rules enabled ({len(self.universal_rules)} rules)")
        else:
            print(f"   🚫 Universal rules disabled")
        
        # Sort by priority (lower number = higher priority)
        sorted_rules = sorted(all_rules, key=lambda x: x.get('priority', 999))
        
        bank_rule_count = len(sorted_rules) - (len(self.universal_rules) if bank_rules_settings.get('enableUniversalRules', True) else 0)
        universal_rule_count = len(self.universal_rules) if bank_rules_settings.get('enableUniversalRules', True) else 0
        
        print(f"   📋 Total rules loaded: {len(sorted_rules)} (bank: {bank_rule_count}, universal: {universal_rule_count})")
        return sorted_rules
    
    def _apply_transformation_rules(self, cashew_row: Dict, original_row: Dict, 
                                   rules: List[Dict]) -> Dict:
        """Apply transformation rules to categorize and clean data"""
        
        rules_applied = 0
        for i, rule in enumerate(rules):
            rule_name = rule.get('rule_name', f'Rule_{i}')
            
            if self._check_rule_conditions(cashew_row, original_row, rule.get('conditions', {})):
                rules_applied += 1
                
                # Apply the rule actions
                actions = rule.get('actions', {})
                
                # Apply description cleaning FIRST
                if 'clean_description' in actions:
                    original_title = cashew_row.get('Title', '')
                    cleaned_desc = self._clean_description(
                        cashew_row, original_row, actions['clean_description']
                    )
                    if cleaned_desc and cleaned_desc != original_title:
                        cashew_row['Title'] = cleaned_desc
                        if rules_applied <= 3:  # Debug first few
                            print(f"     🧹 {rule_name}: '{original_title[:30]}...' → '{cleaned_desc[:30]}...'")
                
                # Set category
                if 'set_category' in actions:
                    old_category = cashew_row.get('Category', '')
                    cashew_row['Category'] = actions['set_category']
                    if rules_applied <= 3:  # Debug first few
                        print(f"     📂 {rule_name}: Category '{old_category}' → '{actions['set_category']}'")
                
                # Set title (after cleaning)
                if 'set_title' in actions:
                    old_title = cashew_row.get('Title', '')
                    cashew_row['Title'] = actions['set_title']
                    if rules_applied <= 3:  # Debug first few
                        print(f"     🏷️  {rule_name}: Title '{old_title[:20]}...' → '{actions['set_title']}'")
                
                # Check if we should continue processing more rules
                if not actions.get('continue_processing', False):
                    break
        
        return cashew_row
    
    def _check_rule_conditions(self, cashew_row: Dict, original_row: Dict, conditions: Dict) -> bool:
        """Check if a row matches the given conditions"""
        if not conditions:
            return False
        
        # Handle compound conditions
        if 'and' in conditions:
            return all(self._check_single_condition(cashew_row, original_row, cond) 
                      for cond in conditions['and'])
        elif 'or' in conditions:
            return any(self._check_single_condition(cashew_row, original_row, cond) 
                      for cond in conditions['or'])
        else:
            return self._check_single_condition(cashew_row, original_row, conditions)
    
    def _check_single_condition(self, cashew_row: Dict, original_row: Dict, condition: Dict) -> bool:
        """Check a single condition against a row"""
        field = condition.get('field')
        operator = condition.get('operator')
        value = condition.get('value')
        case_sensitive = condition.get('case_sensitive', True)
        
        # Look for field in both cashew_row and original_row
        field_value = None
        if field in cashew_row:
            field_value = cashew_row[field]
        elif field in original_row:
            field_value = original_row[field]
        
        if field_value is None:
            return False
        
        # Convert to string for text operations
        field_str = str(field_value)
        if not case_sensitive:
            field_str = field_str.lower()
            value = str(value).lower() if value is not None else ''
        
        # Apply the operator
        if operator == 'equals':
            return field_str == str(value)
        elif operator == 'contains':
            return str(value) in field_str
        elif operator == 'starts_with':
            return field_str.startswith(str(value))
        elif operator == 'ends_with':
            return field_str.endswith(str(value))
        elif operator == 'regex':
            return bool(re.search(str(value), field_str, re.IGNORECASE if not case_sensitive else 0))
        elif operator == 'greater_than':
            try:
                return float(field_value) > float(value)
            except (ValueError, TypeError):
                return False
        elif operator == 'less_than':
            try:
                return float(field_value) < float(value)
            except (ValueError, TypeError):
                return False
        elif operator == 'range':
            try:
                field_num = float(field_value)
                min_val = condition.get('min', float('-inf'))
                max_val = condition.get('max', float('inf'))
                return min_val <= field_num <= max_val
            except (ValueError, TypeError):
                return False
        
        return False
    
    def _clean_description(self, cashew_row: Dict, original_row: Dict, clean_config: Dict) -> str:
        """Clean and transform transaction descriptions"""
        from_field = clean_config.get('from_field', 'Title')
        rules = clean_config.get('rules', [])
        default = clean_config.get('default', '')
        
        # Get the source text
        source_text = ''
        if from_field in cashew_row:
            source_text = str(cashew_row[from_field])
        elif from_field in original_row:
            source_text = str(original_row[from_field])
        
        if not source_text:
            return default
        
        try:
            # Apply cleaning rules
            cleaned_text = source_text
            for rule in rules:
                pattern = rule.get('pattern', '')
                replacement = rule.get('replacement', '')
                if pattern:
                    cleaned_text = re.sub(pattern, replacement, cleaned_text, flags=re.IGNORECASE | re.MULTILINE)
            
            # Clean up whitespace
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            
            return cleaned_text if cleaned_text else default
        except Exception as e:
            print(f"⚠️  Description cleaning error: {e}")
            return source_text
    
    def _apply_default_categorization(self, cashew_row: Dict) -> Dict:
        """Apply default categorization based on amount"""
        try:
            amount = float(cashew_row['Amount'])
            if amount > 0:
                cashew_row['Category'] = self.default_category_rules.get('positive_amount', 'Income')
            elif amount < 0:
                cashew_row['Category'] = self.default_category_rules.get('negative_amount', 'Expense')
            else:
                cashew_row['Category'] = self.default_category_rules.get('zero_amount', 'Transfer')
        except (ValueError, TypeError):
            cashew_row['Category'] = 'Uncategorized'
        
        return cashew_row
    
    def _standardize_date(self, date_value: Any) -> str:
        """Standardize date to ISO format"""
        if not date_value:
            return ''
        
        date_str = str(date_value).strip()
        
        # If already in ISO format, return as-is
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str
        
        # Try various date formats
        date_formats = [
            '%d %b %Y %I:%M %p',    # 02 Feb 2025 11:17 PM
            '%d %b %Y',             # 02 Feb 2025
            '%Y-%m-%d',             # 2025-02-03
            '%d/%m/%Y',             # 02/03/2025
            '%m/%d/%Y',             # 03/02/2025
            '%d-%m-%Y',             # 02-03-2025
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return date_str  # Return original if can't parse
    
    def _standardize_amount(self, amount_value: Any) -> float:
        """Standardize amount to float"""
        if amount_value is None:
            return 0.0
        
        # If already a number, return as-is
        if isinstance(amount_value, (int, float)):
            return float(amount_value)
        
        try:
            # Clean string representation
            amount_str = str(amount_value).strip()
            
            # Remove currency symbols, quotes, commas
            cleaned = re.sub(r'[$€£¥₹PKR USD EUR GBP\s"\']', '', amount_str)
            
            # Handle parentheses (negative)
            is_negative_paren = cleaned.startswith('(') and cleaned.endswith(')')
            if is_negative_paren:
                cleaned = cleaned[1:-1]
            
            # Remove commas and extra spaces
            cleaned = cleaned.replace(',', '').replace(' ', '')
            
            # Handle +/- signs
            is_negative_sign = cleaned.startswith('-')
            is_positive_sign = cleaned.startswith('+')
            
            if is_positive_sign:
                cleaned = cleaned[1:]
            
            # Parse the number
            if cleaned:
                number = float(cleaned)
                if is_negative_paren or is_negative_sign:
                    number = -abs(number)
                return number
            else:
                return 0.0
                
        except (ValueError, TypeError):
            return 0.0


# Test function
def test_universal_transformer():
    """Test the universal transformer with sample data"""
    print("🧪 Testing Universal Transformer")
    
    # Initialize transformer
    transformer = UniversalTransformer()
    
    # Test with NayaPay data
    nayapay_data = [
        {
            'Date': '2025-02-02',
            'Amount': -15000.0,  # Changed to trigger "less than -5000" rule
            'Title': 'Outgoing fund transfer to Someone',
            'Note': 'Raast Out',
            'Currency': 'PKR'
        },
        {
            'Date': '2025-02-03',
            'Amount': -800.0,
            'Title': 'Card transaction issued by Uber',
            'Note': 'Travel',
            'Currency': 'PKR'
        }
    ]
    
    column_mapping = {
        'Date': 'Date',
        'Amount': 'Amount',
        'Title': 'Title',
        'Note': 'Note',
        'Account': ''
    }
    
    result = transformer.transform_to_cashew(nayapay_data, column_mapping, "NayaPay")
    
    print(f"\n📊 Test Results:")
    for i, row in enumerate(result):
        print(f"   Row {i}: {row['Category']} - {row['Title']} ({row['Amount']})")

if __name__ == "__main__":
    test_universal_transformer()
