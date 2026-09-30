"""
Format Validation Logic

Provides validation capabilities for amount formats and parsed values.
"""

import re
from typing import Optional
from .regional_formats import AmountFormat


class FormatValidator:
    """
    Validates amount formats and provides validation results with detailed feedback.
    """
    
    def __init__(self):
        self.currency_pattern = re.compile(r'[₹$€£¥₩₪₨₦₡₵₴₸₽¢₮₰₱₲₭₼₾₺]|USD|EUR|GBP|JPY|CHF|CAD|AUD|SEK|NOK|DKK|PLN|CZK|HUF|RON|BGN|HRK|RUB|CNY|INR|KRW|SGD|THB|MYR|IDR|PHP|VND|BRL|ARS|MXN|CLP|COP|PEN|UYU|ZAR|EGP|TRY|ILS|AED|SAR|QAR|KWD|BHD|OMR|JOD')
    
    def parse_amount_with_format(self, amount_str: str, format_obj: AmountFormat) -> Optional[float]:
        """
        Parse an amount string using the specified format.
        
        Args:
            amount_str: String representation of amount
            format_obj: AmountFormat to use for parsing
            
        Returns:
            Parsed float value or None if parsing fails
        """
        if not amount_str or amount_str.strip() == "":
            return None
        
        try:
            # Convert to string and clean
            cleaned = str(amount_str).strip()
            
            # Remove currency symbols
            cleaned = self.currency_pattern.sub('', cleaned).strip()
            
            # Handle negative styles and positive signs
            is_negative = False
            if format_obj.negative_style == "parentheses":
                if cleaned.startswith('(') and cleaned.endswith(')'):
                    is_negative = True
                    cleaned = cleaned[1:-1].strip()
            elif format_obj.negative_style == "minus":
                if cleaned.startswith('-'):
                    is_negative = True
                    cleaned = cleaned[1:].strip()
            elif format_obj.negative_style == "suffix":
                if cleaned.endswith('-'):
                    is_negative = True
                    cleaned = cleaned[:-1].strip()
            
            # Handle positive signs (remove them)
            if cleaned.startswith('+'):
                cleaned = cleaned[1:].strip()
            
            # Remove thousand separators
            if format_obj.thousand_separator:
                cleaned = cleaned.replace(format_obj.thousand_separator, '')
            
            # Handle decimal separator
            if format_obj.decimal_separator != '.':
                # Only replace the last occurrence (rightmost decimal separator)
                parts = cleaned.rsplit(format_obj.decimal_separator, 1)
                if len(parts) == 2:
                    cleaned = parts[0] + '.' + parts[1]
            
            # Remove any remaining whitespace
            cleaned = re.sub(r'\s+', '', cleaned)
            
            # Validate the result looks like a number
            if not re.match(r'^-?\d*\.?\d+$', cleaned):
                return None
            
            # Convert to float
            value = float(cleaned)
            
            # Apply negative if needed
            if is_negative:
                value = -value
            
            return value
            
        except (ValueError, AttributeError, TypeError):
            return None
    
