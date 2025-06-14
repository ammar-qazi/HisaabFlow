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
        
        tx_desc_snippet = transaction.get('Title', transaction.get('Description', ''))[:30]

        # First check exact column names
        print(f"DEBUG EA get_exchange_to_amount: Tx Keys for '{tx_desc_snippet}': {list(transaction.keys())}") # ADD THIS LINE
        for col in exchange_amount_columns:
            if col in transaction:
                exchange_value = transaction[col]
                print(f"DEBUG EA get_exchange_to_amount: Checking exact column '{col}', value: '{exchange_value}' for Tx: {tx_desc_snippet}")
                if exchange_value and str(exchange_value).strip() not in ['', 'nan', 'NaN', 'null', 'None']:
                    try:
                        parsed_amount = AmountParser.parse_amount(str(exchange_value))
                        if parsed_amount != 0:
                            print(f"DEBUG EA get_exchange_to_amount:   -> Parsed exact column '{col}' to amount: {abs(parsed_amount)}")
                            return abs(parsed_amount)  # Always return positive
                    except (ValueError, TypeError):
                        print(f"DEBUG EA get_exchange_to_amount:   -> Failed to parse amount from exact column '{col}', value: '{exchange_value}'")
                        continue
        
        # Fallback: Search for any column containing exchange/convert/total keywords
        exchange_keywords = ['exchange', 'convert', 'total', 'destination', 'target']
        amount_keywords = ['amount', 'value', 'sum']
        
        print(f"DEBUG EA get_exchange_to_amount: Fallback search for Tx: {tx_desc_snippet}")
        for col in transaction:
            col_lower = col.lower()
            # Check if column contains exchange/convert keywords AND amount keywords
            has_exchange_keyword = any(keyword in col_lower for keyword in exchange_keywords)
            has_amount_keyword = any(keyword in col_lower for keyword in amount_keywords)
            
            if has_exchange_keyword and has_amount_keyword:
                exchange_value = transaction[col]
                print(f"DEBUG EA get_exchange_to_amount:   Checking fallback column '{col}' (keywords matched), value: '{exchange_value}'")
                if exchange_value and str(exchange_value).strip() not in ['', 'nan', 'NaN', 'null', 'None']:
                    try:
                        parsed_amount = AmountParser.parse_amount(str(exchange_value))
                        if parsed_amount != 0:
                            print(f"DEBUG EA get_exchange_to_amount:     -> Parsed fallback column '{col}' to amount: {abs(parsed_amount)}")
                            return abs(parsed_amount)  # Always return positive
                    except (ValueError, TypeError):
                        print(f"DEBUG EA get_exchange_to_amount:     -> Failed to parse amount from fallback column '{col}', value: '{exchange_value}'")
                        continue
        
        # Final fallback: Check if there's a numeric column that could be exchange amount
        main_amount = abs(AmountParser.parse_amount(transaction.get('Amount', '0')))
        print(f"DEBUG EA get_exchange_to_amount: Final fallback (numeric diff from main amount {main_amount}) for Tx: {tx_desc_snippet}")
        
        # Define a set of known non-amount fields to exclude from this fallback
        excluded_fields_for_fallback = {
            'Amount', 'Balance', 'Date', 'Description', 'Currency', 'Title', 'Note', 'Category',
            '_csv_index', '_transaction_index', '_csv_name', '_bank_type', 
            '_original_title', '_transfer_pattern', '_is_transfer_candidate', 
            '_transfer_direction', '_raw_data', '_conversion_info', '_amount', '_date' 
        }
        excluded_fields_for_fallback.update(exchange_amount_columns) # Also exclude columns already checked by exact/keyword match
        
        for col in transaction:
            if col not in excluded_fields_for_fallback:
                try:
                    value = transaction[col]
                    print(f"DEBUG EA get_exchange_to_amount:   Checking final fallback column '{col}', value: '{value}'")
                    if value and str(value).strip() not in ['', 'nan', 'NaN', 'null', 'None']:
                        parsed_amount = AmountParser.parse_amount(str(value))
                        # If it's a different amount than the main amount, it might be exchange amount
                        if parsed_amount != 0 and abs(parsed_amount) != main_amount:
                            print(f"DEBUG EA get_exchange_to_amount:     -> Parsed final fallback column '{col}' to amount: {abs(parsed_amount)}")
                            return abs(parsed_amount)
                except (ValueError, TypeError):
                    print(f"DEBUG EA get_exchange_to_amount:     -> Failed to parse amount from final fallback column '{col}', value: '{value}'")
                    continue
        
        print(f"DEBUG EA get_exchange_to_amount: No exchange to amount field found for Tx: {tx_desc_snippet}")
        return None
    
    def get_exchange_to_currency(self, transaction: Dict) -> Optional[str]:
        """Extract Exchange To currency from Wise CSV"""
        exchange_currency_columns = [
            'Exchange To',
            'Exchange_To',
            'ExchangeTo',
            'exchange_to',
            'Target Currency', 
            'Destination Currency',
            'To Currency',
            'Currency To', # Added more variations
            'Currency_To',
            'CurrencyTo'
        ]
        
        tx_desc_snippet = transaction.get('Title', transaction.get('Description', ''))[:30]

        # First check exact column names
        print(f"DEBUG EA get_exchange_to_currency: Tx Keys for '{tx_desc_snippet}': {list(transaction.keys())}") # ADD THIS LINE
        for col in exchange_currency_columns:
            if col in transaction:
                currency_value = transaction[col]
                print(f"DEBUG EA get_exchange_to_currency: Checking exact column '{col}', value: '{currency_value}' for Tx: {tx_desc_snippet}")
                if currency_value and str(currency_value).strip() not in ['', 'nan', 'NaN', 'null', 'None']:
                    print(f"DEBUG EA get_exchange_to_currency:   -> Found currency '{str(currency_value).strip().upper()}' in exact column '{col}'")
                    return str(currency_value).strip().upper()
        
        # Fallback mechanism: search for columns containing relevant keywords
        print(f"DEBUG EA get_exchange_to_currency: Fallback search for Tx: {tx_desc_snippet}")
        for col in transaction:
            col_lower = col.lower()
            is_exchange_to = "exchange" in col_lower and "to" in col_lower
            is_target_currency = ("target" in col_lower or "destination" in col_lower or "to" in col_lower) and "currency" in col_lower
            
            if is_exchange_to or is_target_currency:
                currency_value = transaction[col]
                print(f"DEBUG EA get_exchange_to_currency:   Checking fallback column '{col}' (keywords matched), value: '{currency_value}'")
                if currency_value and str(currency_value).strip() not in ['', 'nan', 'NaN', 'null', 'None']:
                    # Basic validation for 3-letter currency code
                    val_str = str(currency_value).strip().upper()
                    if len(val_str) == 3 and val_str.isalpha():
                        print(f"DEBUG EA get_exchange_to_currency:     -> Found currency '{val_str}' in fallback column '{col}'")
                        return val_str
                    else:
                        print(f"DEBUG EA get_exchange_to_currency:     -> Value '{val_str}' in fallback column '{col}' is not a valid 3-letter currency code.")
                        
        print(f"DEBUG EA get_exchange_to_currency: No exchange to currency field found for Tx: {tx_desc_snippet}")
        return None
    
    def currency_matches_bank(self, currency: str, transaction: Dict) -> bool:
        """
        Check if the provided currency matches the transaction's own currency.
        The transaction's 'Currency' field should be set based on its bank's
        primary currency from the configuration.
        """
        transaction_currency = transaction.get('Currency', '').upper()
        if not transaction_currency:
            # If the transaction itself has no currency defined, we can't be sure.
            # This might happen if the CSV doesn't have a currency column or it wasn't mapped.
            print(f"DEBUG EA currency_matches_bank: Transaction has no 'Currency' field. Tx: {transaction.get('Title', transaction.get('Description', ''))[:30]}. Allowing match by default.")
            return True # Default to true to not block matching unnecessarily.
                        # Other logic (like amount matching) will still apply.
        
        match = currency.upper() == transaction_currency
        print(f"DEBUG EA currency_matches_bank: Comparing '{currency.upper()}' with transaction currency '{transaction_currency}'. Match: {match}. Tx: {transaction.get('Title', transaction.get('Description', ''))[:30]}")
        return match
