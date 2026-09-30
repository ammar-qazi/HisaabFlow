"""
Date parsing utilities for transfer detection
"""
from datetime import datetime
from typing import Optional, Union


class DateParser:
    """Utility class for parsing and comparing dates"""
    
    @staticmethod
    def parse_date(date_str: Union[str, datetime, None]) -> Optional[datetime]:
        """Parse date string to datetime object. Returns None if it can't be read."""
        if isinstance(date_str, datetime):
            return date_str
            
        # Empty or missing dates must not become "today": that made unrelated
        # transactions look like same-day transfers
        if date_str is None or str(date_str).strip() == '':
            return None
        
        date_formats = [
            '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y-%m-%d %H:%M:%S',
            '%m-%d-%y', '%d-%m-%y', '%y-%m-%d'  # 2-digit year formats (MM-DD-YY prioritized)
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str), fmt)
            except ValueError:
                continue
        
        try:
            return datetime.fromisoformat(str(date_str).strip())
        except ValueError:
            return None
    
    @staticmethod
    def format_date(date_str: Union[str, datetime, None], fmt: str = '%Y-%m-%d') -> str:
        """Parse and format a date, or return '' if it can't be read."""
        parsed = DateParser.parse_date(date_str)
        return parsed.strftime(fmt) if parsed else ''
    
    @staticmethod
    def dates_within_tolerance(date1: datetime, date2: datetime, tolerance_hours: int = 72) -> bool:
        """Check if two dates are within the tolerance period"""
        if date1 is None or date2 is None:
            return False
        try:
            delta = abs((date1 - date2).total_seconds() / 3600)
            return delta <= tolerance_hours
        except Exception:
            return False
    
    @staticmethod
    def same_day(date1: datetime, date2: datetime) -> bool:
        """Check if two dates are on the same day"""
        if date1 is None or date2 is None:
            return False
        try:
            return date1.date() == date2.date()
        except Exception:
            return False
