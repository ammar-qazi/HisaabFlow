"""
Data Parser Module - Date and amount parsing utilities
"""
import re
from datetime import datetime
from typing import Dict

class DataParser:
    """Handles parsing of dates and amounts from CSV data"""
    
    def parse_date(self, date_str: str) -> str:
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
    
    def parse_amount(self, amount_str: str) -> str:
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
