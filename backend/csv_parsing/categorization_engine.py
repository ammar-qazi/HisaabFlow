"""
Categorization Engine Module - Rule-based transaction categorization
"""
import re
import pandas as pd
from typing import Dict, List

class CategorizationEngine:
    """Handles rule-based categorization of transactions"""
    
    def apply_categorization_rules(self, cashew_row: Dict, original_row: Dict, 
                                   categorization_rules: List[Dict] = None,
                                   default_category_rules: Dict = None) -> Dict:
        """Apply categorization rules to determine category and title"""
        
        if not categorization_rules:
            return self.apply_default_categorization(cashew_row, default_category_rules)
        
        # Sort rules by priority (lower number = higher priority)
        sorted_rules = sorted(categorization_rules, key=lambda x: x.get('priority', 999))
        
        for rule in sorted_rules:
            if self.check_rule_conditions(original_row, rule.get('conditions', {})):
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
                        extracted_name = self.extract_name(original_row, actions['extract_name'])
                        cashew_row['Title'] = template.format(extract_name=extracted_name)
                    else:
                        cashew_row['Title'] = template
                elif 'clean_description' in actions:
                    # Clean and shorten the description using regex pattern
                    clean_config = actions['clean_description']
                    cleaned_desc = self.clean_description(original_row, clean_config)
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
            cashew_row = self.apply_default_categorization(cashew_row, default_category_rules)
        
        return cashew_row
    
    def check_rule_conditions(self, row: Dict, conditions: Dict) -> bool:
        """Check if a row matches the given conditions"""
        if not conditions:
            return False
        
        # Handle old-style conditions
        if 'and' in conditions:
            return all(self.check_single_condition(row, cond) for cond in conditions['and'])
        elif 'or' in conditions:
            return any(self.check_single_condition(row, cond) for cond in conditions['or'])
        else:
            return self.check_single_condition(row, conditions)
    
    def check_single_condition(self, row: Dict, condition: Dict) -> bool:
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
                cleaned_field = self._parse_amount_for_comparison(field_value)
                return float(cleaned_field) > float(value)
            except (ValueError, TypeError):
                return False
        elif operator == 'less_than':
            try:
                # Clean the field value for numeric comparison
                cleaned_field = self._parse_amount_for_comparison(field_value)
                return float(cleaned_field) < float(value)
            except (ValueError, TypeError):
                return False
        elif operator == 'range':
            try:
                # Clean the field value for numeric comparison
                cleaned_field = self._parse_amount_for_comparison(field_value)
                field_num = float(cleaned_field)
                min_val = condition.get('min', float('-inf'))
                max_val = condition.get('max', float('inf'))
                return min_val <= field_num <= max_val
            except (ValueError, TypeError):
                return False
        
        return False
    
    def extract_name(self, row: Dict, extract_config: Dict) -> str:
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
    
    def clean_description(self, row: Dict, clean_config: Dict) -> str:
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
    
    def apply_default_categorization(self, cashew_row: Dict, default_rules: Dict = None) -> Dict:
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
    
    def _parse_amount_for_comparison(self, amount_str: str) -> str:
        """Parse amount string for numeric comparison (reused from data_parser logic)"""
        try:
            if not amount_str or str(amount_str).strip() == '' or str(amount_str).lower() == 'nan':
                return '0'
            
            amount_str = str(amount_str).strip()
            amount_str = amount_str.strip('"').strip("'")
            cleaned = re.sub(r'[^0-9.\-+]', '', amount_str)
            
            is_negative = False
            if (amount_str.startswith('-') or amount_str.startswith('(') or 
                amount_str.endswith(')') or '(' in amount_str):
                is_negative = True
            elif amount_str.startswith('+'):
                is_negative = False
            
            cleaned = cleaned.lstrip('+-')
            
            if is_negative and not cleaned.startswith('-'):
                cleaned = '-' + cleaned
            
            if cleaned:
                return str(float(cleaned))
            else:
                return '0'
        except Exception:
            return '0'
