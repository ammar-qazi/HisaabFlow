"""
Amount parsing utilities for transfer detection
"""
import re
from typing import Union


class AmountParser:
    """Utility class for parsing and handling monetary amounts"""
    
    @staticmethod
    def parse_amount(amount_str: Union[str, float, int]) -> float:
        """Parse amount string to float"""
        try:
            if isinstance(amount_str, (int, float)):
                return float(amount_str)
            
            cleaned = re.sub(r'[^0-9.\-]', '', str(amount_str))
            return float(cleaned) if cleaned else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def amounts_match(amount1: float, amount2: float, tolerance: float = 0.01) -> bool:
        """Check if two amounts match within tolerance"""
        return abs(amount1 - amount2) < tolerance
    
    @staticmethod
    def calculate_percentage_difference(amount1: float, amount2: float) -> float:
        """Calculate percentage difference between two amounts"""
        if max(amount1, amount2) == 0:
            return 0.0
        return abs(amount1 - amount2) / max(amount1, amount2)
