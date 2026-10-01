"""
Amount parsing utilities for transfer detection
"""
from typing import Union

from backend.shared.utils.amount_text import parse_amount_text


class AmountParser:
    """Utility class for parsing and handling monetary amounts"""
    
    @staticmethod
    def parse_amount(amount_str: Union[str, float, int]) -> float:
        """Parse amount string to float"""
        # Unreadable amounts become 0.0, which transfer matching already skips
        # (candidates are filtered by sign before matching)
        amount = parse_amount_text(amount_str)
        return float(amount) if amount is not None else 0.0
    
    @staticmethod
    def amounts_match(amount1: float, amount2: float, tolerance: float = 0.01) -> bool:
        """Check if two amounts match within tolerance"""
        return abs(amount1 - amount2) < tolerance
    
