"""
Parse loosely formatted amount text ("PKR -1,234.50", "500-", "(12,50)")
into a Decimal.

Used by the Cashew transformer and transfer detection, which receive values
that may or may not have gone through the bank-aware AmountFormat cleaning.
"""
import re
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

_KEEP = re.compile(r'[^0-9.,\-+()]')
_NUMBER = re.compile(r'^\d+(\.\d+)?$')


def parse_amount_text(value: Any) -> Optional[Decimal]:
    """Return the amount as a Decimal, or None if it cannot be read."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float, Decimal)):
        try:
            result = Decimal(str(value))
        except InvalidOperation:
            return None
        return result if result.is_finite() else None

    text = str(value).strip().strip('"').strip("'").strip()
    if not text or text.lower() == 'nan':
        return None

    # Drop currency codes/symbols and spaces, keep digits, separators and signs
    text = _KEEP.sub('', text)
    negative = (
        text.startswith('-')
        or text.endswith('-')
        or (text.startswith('(') and text.endswith(')'))
    )
    digits = text.strip('+-()')
    if not digits or any(c in digits for c in '+-()'):
        return None

    digits = _normalise_separators(digits)
    if digits is None or not _NUMBER.match(digits):
        return None

    result = Decimal(digits)
    return -result if negative else result


def _normalise_separators(digits: str) -> Optional[str]:
    """Turn '1.234,56', '1,234.56', '6,325' and '12,5' into plain '1234.56' style."""
    has_comma, has_dot = ',' in digits, '.' in digits

    if has_comma and has_dot:
        # Whichever separator comes last is the decimal point
        if digits.rfind(',') > digits.rfind('.'):
            return digits.replace('.', '').replace(',', '.')
        return digits.replace(',', '')

    if has_comma:
        groups = digits.split(',')
        if len(groups) == 2 and len(groups[1]) != 3:
            return digits.replace(',', '.')  # decimal comma: "12,5", "12,50"
        if all(len(g) == 3 for g in groups[1:]):
            return digits.replace(',', '')   # thousands: "6,325", "1,234,567"
        return None

    if has_dot and digits.count('.') > 1:
        groups = digits.split('.')
        if all(len(g) == 3 for g in groups[1:]):
            return digits.replace('.', '')   # thousands: "1.234.567"
        return None

    return digits


def format_amount(amount: Decimal) -> str:
    """Format like the previous float-based output ("-250.0"), without float drift."""
    if amount == 0:
        return '0'
    return str(float(amount))
