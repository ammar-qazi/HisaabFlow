"""
Currency Handler
Manages currency column detection and addition for bank data
"""

from typing import List, Dict

class CurrencyHandler:
    """
    Handles currency column management for bank statements
    Adds currency columns when missing and determines appropriate defaults
    """
    
    def __init__(self):
        self.currency_mappings = {
            'nayapay': 'PKR',
            'easypaisa': 'PKR', 
            'jazzcash': 'PKR',
            'sadapay': 'PKR',
            'meezan': 'PKR',
            'hbl': 'PKR',
            'ubl': 'PKR',
            'wise': 'USD',  # Wise default, but they usually have currency columns
            'transferwise': 'USD',
            'revolut': 'EUR',
            'paypal': 'USD',
            'chase': 'USD',
            'wells fargo': 'USD',
            'bank of america': 'USD',
            'hsbc': 'GBP',
            'barclays': 'GBP',
            'lloyds': 'GBP'
        }
    
    def add_currency_column(self, data: List[Dict], template_config: Dict = None) -> List[Dict]:
        """
        Add currency column if missing
        
        Args:
            data: List of dictionaries potentially missing currency column
            template_config: Template configuration with bank information
            
        Returns:
            List[Dict]: Data with currency column added if needed
        """
        print(f"   💱 Step 3: Adding currency column if needed")
        
        if not data:
            return []
        
        # Check if currency column already exists
        if self._has_currency_column(data):
            print(f"      ✅ Currency column already exists, skipping...")
            return data
        
        # Determine default currency
        default_currency = self._determine_default_currency(template_config)
        print(f"      💰 Adding currency column with default: {default_currency}")
        
        # Add currency column to all rows
        currency_added_data = []
        for row in data:
            new_row = row.copy()
            new_row['Currency'] = default_currency  # Use Title case for consistency
            currency_added_data.append(new_row)
        
        print(f"      ✅ Currency column added: {default_currency}")
        return currency_added_data
    
    def _has_currency_column(self, data: List[Dict]) -> bool:
        """
        Check if data already has a currency column
        
        Args:
            data: Sample data to check
            
        Returns:
            bool: True if currency column exists
        """
        if not data:
            return False
        
        sample_row = data[0]
        return any('currency' in col.lower() for col in sample_row.keys())
    
    def _determine_default_currency(self, template_config: Dict = None) -> str:
        """
        Determine default currency based on template config or bank name
        
        Args:
            template_config: Template configuration
            
        Returns:
            str: Default currency code
        """
        if not template_config:
            return 'PKR'  # Default fallback
        
        # Check if template explicitly specifies currency
        if 'default_currency' in template_config:
            return template_config['default_currency']
        
        # Determine currency based on bank name
        bank_name = template_config.get('bank_name', '').lower()
        
        for bank_keyword, currency in self.currency_mappings.items():
            if bank_keyword in bank_name:
                return currency
        
        # Default fallback
        return 'PKR'
    
    def get_supported_currencies(self) -> List[str]:
        """
        Get list of supported currencies
        
        Returns:
            List[str]: Supported currency codes
        """
        return list(set(self.currency_mappings.values()))
    
    def add_bank_currency_mapping(self, bank_name: str, currency: str):
        """
        Add or update currency mapping for a bank
        
        Args:
            bank_name: Bank name or keyword
            currency: Currency code
        """
        self.currency_mappings[bank_name.lower()] = currency.upper()
        print(f"      ➕ Added currency mapping: {bank_name} → {currency}")
