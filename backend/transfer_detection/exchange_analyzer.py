"""
Exchange amount analysis for Wise transactions
"""
from typing import Dict, Optional
from .amount_parser import AmountParser


class ExchangeAnalyzer:
    """Handles exchange amount detection and currency analysis for Wise transactions"""
    
    def get_exchange_to_amount(self, transaction: Dict) -> Optional[float]:
        """Extract Exchange To Amount from Wise CSV (last column)"""
        # Check ALL possible column variations for Exchange To Amount
        exchange_amount_columns = [
            'Exchange To Amount',  # Standard format
            'Exchange_To_Amount',  # Underscore format
            'ExchangeToAmount',    # CamelCase format
            'exchange_to_amount',  # Lowercase
            'Exchange Amount',     # Without "To"
            'ExchangeAmount',      # Without "To" CamelCase
            'exchange_amount',     # Without "To" lowercase
            'Total',               # Sometimes labeled as Total
            'Total Amount',        # Total Amount
            'Converted Amount',    # Converted Amount
            'Target Amount',       # Target Amount
            'Destination Amount',  # Destination Amount
        ]
        
        # First check exact column names
        for col in exchange_amount_columns:
            if col in transaction:
                exchange_value = transaction[col]
                if exchange_value and str(exchange_value).strip() not in ['', 'nan', 'NaN', 'null', 'None']:
                    try:
                        parsed_amount = AmountParser.parse_amount(str(exchange_value))
                        if parsed_amount != 0:
                            return abs(parsed_amount)  # Always return positive
                    except (ValueError, TypeError):
                        continue
        
        # Fallback: Search for any column containing exchange/convert/total keywords
        exchange_keywords = ['exchange', 'convert', 'total', 'destination', 'target']
        amount_keywords = ['amount', 'value', 'sum']
        
        for col in transaction:
            col_lower = col.lower()
            # Check if column contains exchange/convert keywords AND amount keywords
            has_exchange_keyword = any(keyword in col_lower for keyword in exchange_keywords)
            has_amount_keyword = any(keyword in col_lower for keyword in amount_keywords)
            
            if has_exchange_keyword and has_amount_keyword:
                exchange_value = transaction[col]
                if exchange_value and str(exchange_value).strip() not in ['', 'nan', 'NaN', 'null', 'None']:
                    try:
                        parsed_amount = AmountParser.parse_amount(str(exchange_value))
                        if parsed_amount != 0:
                            return abs(parsed_amount)  # Always return positive
                    except (ValueError, TypeError):
                        continue
        
        # Final fallback: Check if there's a numeric column that could be exchange amount
        main_amount = abs(AmountParser.parse_amount(transaction.get('Amount', '0')))
        for col in transaction:
            if col not in ['Amount', 'Balance', 'Date', 'Description', 'Currency'] and col not in exchange_amount_columns:
                try:
                    value = transaction[col]
                    if value and str(value).strip() not in ['', 'nan', 'NaN', 'null', 'None']:
                        parsed_amount = AmountParser.parse_amount(str(value))
                        # If it's a different amount than the main amount, it might be exchange amount
                        if parsed_amount != 0 and abs(parsed_amount) != main_amount:
                            return abs(parsed_amount)
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def get_exchange_to_currency(self, transaction: Dict) -> Optional[str]:
        """Extract Exchange To currency from Wise CSV"""
        exchange_currency_columns = [
            'Exchange To',
            'Exchange_To',
            'ExchangeTo',
            'exchange_to'
        ]
        
        # First check exact column names
        for col in exchange_currency_columns:
            if col in transaction:
                currency_value = transaction[col]
                if currency_value and str(currency_value).strip() not in ['', 'nan', 'NaN', 'null', 'None']:
                    return str(currency_value).strip().upper()
        
        # Fallback mechanism: search for columns containing "Exchange" and "To"
        for col in transaction:
            if "exchange" in col.lower() and "to" in col.lower():
                currency_value = transaction[col]
                if currency_value and str(currency_value).strip() not in ['', 'nan', 'NaN', 'null', 'None']:
                    return str(currency_value).strip().upper()

        return None
    
    def currency_matches_bank(self, currency: str, transaction: Dict) -> bool:
        """
        Check if currency matches expected bank type
        PKR -> Pakistani banks (NayaPay, Meezan, etc.)
        EUR -> European Wise accounts
        USD -> USD Wise accounts
        """
        bank_type = transaction.get('_bank_type', '')
        
        if currency == 'PKR':
            return bank_type in ['nayapay', 'bank_alfalah', 'meezan', 'pakistani_bank']
        elif currency == 'EUR':
            return bank_type == 'wise' and 'eur' in transaction.get('_csv_name', '').lower()
        elif currency == 'USD':
            return bank_type == 'wise' and 'usd' in transaction.get('_csv_name', '').lower()
        
        return True  # If unsure, allow the match
