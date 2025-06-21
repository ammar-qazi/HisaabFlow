import re
from decimal import Decimal
from datetime import date, datetime

class TypeConverter:
    def parse_amount(self, value: str) -> Decimal:
        cleaned = re.sub(r'[,\s]', '', value)
        return Decimal(cleaned)

    def parse_date(self, value: str) -> date:
        for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date: {value}")