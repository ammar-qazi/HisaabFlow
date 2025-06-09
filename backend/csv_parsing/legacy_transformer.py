"""
Legacy Transformer Module - Fallback transformation when Universal Transformer unavailable
"""
import pandas as pd
from typing import Dict, List
from .data_parser import DataParser
from .categorization_engine import CategorizationEngine

class LegacyTransformer:
    """Handles legacy transformation logic as fallback"""
    
    def __init__(self):
        self.data_parser = DataParser()
        self.categorization_engine = CategorizationEngine()
    
    def transform_to_cashew(self, data: List[Dict], column_mapping: Dict[str, str], 
                           bank_name: str = "", categorization_rules: List[Dict] = None,
                           default_category_rules: Dict = None, account_mapping: Dict = None,
                           bank_rules_settings: Dict[str, bool] = None) -> List[Dict]:
        """Transform parsed data to Cashew format with smart categorization (legacy version)"""
        
        print(f"\n🔄 USING LEGACY TRANSFORMATION")
        cashew_data = []
        
        print(f"   🏦 Bank: {bank_name}")
        print(f"   📋 Input rows: {len(data)}")
        print(f"   🗺️ Column mapping: {column_mapping}")
        
        for idx, row in enumerate(data):
            cashew_row = {
                'Date': '',
                'Amount': '',
                'Category': '',
                'Title': '',
                'Note': '',
                'Account': bank_name
            }
            
            # Map columns based on mapping
            for cashew_col, source_col in column_mapping.items():
                if source_col in row and pd.notna(row[source_col]):
                    if cashew_col == 'Date':
                        # Parse and format date
                        cashew_row[cashew_col] = self.data_parser.parse_date(str(row[source_col]))
                    elif cashew_col == 'Amount':
                        # Clean and format amount
                        original_amount = str(row[source_col])
                        parsed_amount = self.data_parser.parse_amount(original_amount)
                        cashew_row[cashew_col] = parsed_amount
                        
                        # Debug amount parsing for first few rows
                        if idx < 3:
                            print(f"   💰 Row {idx} Amount: '{original_amount}' → '{parsed_amount}'")
                    elif cashew_col == 'Account' and account_mapping:
                        # Use currency-based account mapping
                        currency = str(row[source_col])
                        cashew_row[cashew_col] = account_mapping.get(currency, bank_name)
                    else:
                        cashew_row[cashew_col] = str(row[source_col])
            
            # Debug first few rows
            if idx < 3:
                print(f"   📋 Row {idx}: Date='{cashew_row['Date']}', Amount='{cashew_row['Amount']}', Title='{cashew_row['Title'][:50]}...'")
            
            # Only process rows with valid amount
            if cashew_row['Amount'] and cashew_row['Amount'] != '0':
                # Apply categorization rules
                cashew_row = self.categorization_engine.apply_categorization_rules(
                    cashew_row, row, categorization_rules, default_category_rules
                )
                cashew_data.append(cashew_row)
            else:
                if idx < 5:  # Log first few skipped rows
                    print(f"   ⚠️  Skipping row {idx}: Invalid/zero amount '{cashew_row['Amount']}'")
        
        print(f"   ✅ Transformation complete: {len(cashew_data)} valid rows")
        return cashew_data
