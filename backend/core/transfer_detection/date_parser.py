"""
Date parsing utilities for transfer detection
"""
from datetime import datetime
from typing import Union


class DateParser:
    """Utility class for parsing and comparing dates"""
    
    @staticmethod
    def parse_date(date_str: Union[str, datetime]) -> datetime:
        """Parse date string to datetime object"""
        try:
            if isinstance(date_str, datetime):
                return date_str
                
            # Handle empty or None dates
            if not date_str or date_str == '':
                return datetime.now()
            
            date_formats = [
                '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y-%m-%d %H:%M:%S',
                '%m-%d-%y', '%d-%m-%y', '%y-%m-%d'  # 2-digit year formats (MM-DD-YY prioritized)
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(str(date_str), fmt)
                except ValueError:
                    continue
            
            return datetime.now()
        except Exception:
            return datetime.now()
    
    @staticmethod
    def dates_within_tolerance(date1: datetime, date2: datetime, tolerance_hours: int = 72) -> bool:
        """Check if two dates are within the tolerance period"""
        try:
            delta = abs((date1 - date2).total_seconds() / 3600)
            return delta <= tolerance_hours
        except Exception:
            return False
    
    @staticmethod
    def same_day(date1: datetime, date2: datetime) -> bool:
        """Check if two dates are on the same day"""
        try:
            return date1.date() == date2.date()
        except Exception:
            return False
