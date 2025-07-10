"""
Export formatting service for API response formatting and data type validation
"""
from typing import Dict, List, Any, Optional
from decimal import Decimal

from backend.shared.models.csv_models import CSVRow


class ExportFormattingService:
    """Service focused on export formatting and data validation"""
    
    def __init__(self):
        print(f"ℹ [ExportFormattingService] Initialized")
    
    def clean_transformed_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean transformed data to match API response model requirements
        
        Removes metadata fields and ensures all values are str, int, or float
        
        Args:
            data: List of transformed data dictionaries
            
        Returns:
            List of cleaned data dictionaries
        """
        print(f"ℹ [ExportFormattingService] Cleaning transformed data for API response...")
        
        cleaned_data = []
        metadata_fields_removed = []
        type_conversions = []
        
        for row_idx, row in enumerate(data):
            cleaned_row = {}
            
            for key, value in row.items():
                # Skip metadata fields (starting with _)
                if key.startswith('_'):
                    if key not in metadata_fields_removed:
                        metadata_fields_removed.append(key)
                    continue
                
                # Handle None values
                if value is None:
                    cleaned_row[key] = ""
                    type_conversions.append(f"Row {row_idx}: {key} None -> ''")
                    continue
                
                # Ensure value is one of the allowed types
                if isinstance(value, (str, int, float)):
                    cleaned_row[key] = value
                elif isinstance(value, bool):
                    # Convert bool to int (0/1)
                    cleaned_row[key] = int(value)
                    type_conversions.append(f"Row {row_idx}: {key} bool({value}) -> int({int(value)})")
                else:
                    # Convert other types to string
                    original_type = type(value).__name__
                    cleaned_row[key] = str(value)
                    type_conversions.append(f"Row {row_idx}: {key} {original_type}({value}) -> str('{str(value)}')")
            
            cleaned_data.append(cleaned_row)
        
        # Log debug information
        if metadata_fields_removed:
            print(f"   [DEBUG] Removed metadata fields: {metadata_fields_removed}")
        if type_conversions:
            print(f"   [DEBUG] Type conversions made: {len(type_conversions)}")
            # Show first few conversions as examples
            for conversion in type_conversions[:5]:
                print(f"      {conversion}")
            if len(type_conversions) > 5:
                print(f"      ... and {len(type_conversions) - 5} more")
        
        return cleaned_data
    
    def clean_single_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean a single transaction object to match model requirements
        
        Removes metadata fields and ensures all values are str, int, or float
        
        Args:
            transaction: Single transaction dictionary
            
        Returns:
            Cleaned transaction dictionary
        """
        print(f"[DEBUG] Original transaction keys: {list(transaction.keys()) if transaction else 'None'}")
        if transaction:
            print(f"[DEBUG] Original transaction sample: {dict(list(transaction.items())[:5])}")
        
        cleaned_transaction = {}
        essential_fields = ['Date', 'Account', 'Amount', 'Currency', 'Title', 'Description', 'Note']
        
        for key, value in transaction.items():
            # Skip metadata fields (starting with _)
            if key.startswith('_'):
                continue
            
            # Special handling for essential display fields
            if key in essential_fields:
                if key == 'Date':
                    # Ensure date is properly formatted
                    if value is None or value == '':
                        cleaned_transaction[key] = ""
                    else:
                        # Convert datetime objects to ISO string, preserve strings
                        try:
                            if hasattr(value, 'isoformat'):
                                cleaned_transaction[key] = value.isoformat()
                            else:
                                cleaned_transaction[key] = str(value)
                        except:
                            cleaned_transaction[key] = str(value)
                elif key == 'Amount':
                    # Ensure amount is numeric or convertible
                    if value is None or value == '':
                        cleaned_transaction[key] = "0"
                    else:
                        try:
                            # Try to preserve as float if possible
                            float_val = float(value)
                            cleaned_transaction[key] = value if isinstance(value, (int, float)) else str(value)
                        except:
                            cleaned_transaction[key] = str(value)
                else:
                    # For other essential fields, preserve as string
                    if value is None:
                        cleaned_transaction[key] = ""
                    else:
                        cleaned_transaction[key] = str(value)
            else:
                # Regular field processing for non-essential fields
                if value is None:
                    cleaned_transaction[key] = ""
                    continue
                
                # Ensure value is one of the allowed types
                if isinstance(value, (str, int, float)):
                    cleaned_transaction[key] = value
                elif isinstance(value, bool):
                    # Convert bool to int (0/1)
                    cleaned_transaction[key] = int(value)
                else:
                    # Convert other types to string
                    cleaned_transaction[key] = str(value)
        
        print(f"[DEBUG] Cleaned transaction keys: {list(cleaned_transaction.keys())}")
        essential_data = {k: v for k, v in cleaned_transaction.items() if k in essential_fields}
        print(f"[DEBUG] Cleaned essential fields: {essential_data}")
        
        return cleaned_transaction
    
    def format_transfer_analysis(self, transfer_analysis_raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format transfer analysis data to match API response model
        
        Args:
            transfer_analysis_raw: Raw transfer analysis data
            
        Returns:
            Formatted transfer analysis data
        """
        print(f"ℹ [ExportFormattingService] Formatting transfer analysis for API response...")
        
        transfers = transfer_analysis_raw.get('transfers', [])
        
        # Count matches by confidence level
        high_confidence_matches = 0
        medium_confidence_matches = 0
        low_confidence_matches = 0
        
        # Convert transfers to matches format
        formatted_matches = []
        for transfer in transfers:
            outgoing = transfer.get('outgoing', {})
            incoming = transfer.get('incoming', {})
            confidence = transfer.get('confidence', 0.0)
            match_type = transfer.get('match_strategy', 'unknown')
            
            # Count by confidence level
            if confidence >= 0.8:
                high_confidence_matches += 1
            elif confidence >= 0.6:
                medium_confidence_matches += 1
            else:
                low_confidence_matches += 1
            
            # Clean transactions to match model requirements
            clean_outgoing = self.clean_single_transaction(outgoing)
            clean_incoming = self.clean_single_transaction(incoming)
            
            # Debug: Log the exact structure being sent to frontend
            print(f"[DEBUG] Transfer Match Structure for Frontend:")
            print(f"  Original outgoing keys: {list(outgoing.keys()) if outgoing else 'None'}")
            print(f"  Original incoming keys: {list(incoming.keys()) if incoming else 'None'}")
            print(f"  Clean outgoing: {clean_outgoing}")
            print(f"  Clean incoming: {clean_incoming}")
            
            # Format as TransferMatch
            match = {
                # Pydantic model fields (required for validation)
                "outgoing_transaction": clean_outgoing,
                "incoming_transaction": clean_incoming,
                "confidence": confidence,
                "match_type": match_type,
                # Frontend compatibility fields (frontend expects these names)
                "outgoing": clean_outgoing,
                "incoming": clean_incoming
            }
            
            print(f"[DEBUG] Final match structure: {match}")
            formatted_matches.append(match)
        
        # Return formatted structure matching TransferAnalysis model
        return {
            # Pydantic model fields (required for validation)
            "total_matches": len(transfers),
            "high_confidence_matches": high_confidence_matches,
            "medium_confidence_matches": medium_confidence_matches,
            "low_confidence_matches": low_confidence_matches,
            "matches": formatted_matches,
            # Frontend compatibility fields
            "transfers": formatted_matches,  # Frontend expects this field
            # Keep additional fields for backward compatibility
            "summary": transfer_analysis_raw.get('summary', {}),
            "potential_transfers": transfer_analysis_raw.get('potential_transfers', []),
            "potential_pairs": transfer_analysis_raw.get('potential_pairs', []),
            "conflicts": transfer_analysis_raw.get('conflicts', []),
            "flagged_transactions": transfer_analysis_raw.get('flagged_transactions', [])
        }
    
    def format_transformation_summary(self, csv_data_list: List[Dict[str, Any]], 
                                     transformed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format transformation summary for API response
        
        Args:
            csv_data_list: Original CSV data list
            transformed_data: Transformed data
            
        Returns:
            Formatted transformation summary
        """
        print(f"ℹ [ExportFormattingService] Formatting transformation summary...")
        
        # Create file results for each CSV processed
        file_results = []
        for csv_data in csv_data_list:
            file_id = csv_data.get('file_id', 'unknown')
            original_name = csv_data.get('filename', csv_data.get('original_name', 'unknown.csv'))
            bank_info = csv_data.get('bank_info', {})
            detected_bank = bank_info.get('bank_name', bank_info.get('detected_bank', 'unknown'))
            csv_rows = len(csv_data.get('data', []))
            
            file_result = {
                "file_id": file_id,
                "original_name": original_name,
                "bank_name": detected_bank,
                "rows_processed": csv_rows,
                "success": True,
                "error": None
            }
            file_results.append(file_result)
        
        # Get list of processed banks
        banks_processed = list(set(fr["bank_name"] for fr in file_results if fr["bank_name"] != "unknown"))
        
        # Create transformation summary structure
        transformation_summary = {
            # Pydantic model fields (required for validation)
            "total_files": len(csv_data_list),
            "total_rows": len(transformed_data),
            "successful_transformations": len([fr for fr in file_results if fr["success"]]),
            "failed_transformations": len([fr for fr in file_results if not fr["success"]]),
            "banks_processed": banks_processed,
            # Frontend compatibility field
            "total_transactions": len(transformed_data)  # Frontend expects this field
        }
        
        return {
            "transformation_summary": transformation_summary,
            "file_results": file_results
        }
    
    def map_to_pydantic_rows(self, data_dicts: List[Dict[str, Any]], 
                           column_mapping: Dict[str, str]) -> List[CSVRow]:
        """
        Map a list of dictionaries to CSVRow Pydantic models
        
        Args:
            data_dicts: List of data dictionaries
            column_mapping: Column mapping dictionary
            
        Returns:
            List of CSVRow Pydantic models
        """
        print(f"ℹ [ExportFormattingService] Mapping {len(data_dicts)} rows to CSVRow models...")
        
        csv_rows: List[CSVRow] = []
        
        # Invert mapping for easier lookup
        target_to_source_map = {v: k for k, v in column_mapping.items()}
        
        for row_dict in data_dicts:
            try:
                # Find values from the source dict using the mapping
                date_val = row_dict.get(target_to_source_map.get('date'))
                desc_val = row_dict.get(target_to_source_map.get('description'), '')
                balance_val = row_dict.get(target_to_source_map.get('balance'))
                
                # Handle amount, which can be from 'amount', 'debit', or 'credit'
                amount_val = row_dict.get(target_to_source_map.get('amount'))
                if amount_val is None:
                    debit_val = row_dict.get(target_to_source_map.get('debit'))
                    credit_val = row_dict.get(target_to_source_map.get('credit'))
                    if debit_val is not None and isinstance(debit_val, (Decimal, int, float)):
                        amount_val = -Decimal(debit_val)  # Debits are negative
                    elif credit_val is not None and isinstance(credit_val, (Decimal, int, float)):
                        amount_val = Decimal(credit_val)
                
                # Create the Pydantic model
                csv_row = CSVRow(
                    date=date_val,
                    amount=amount_val,
                    description=str(desc_val),
                    balance=balance_val
                )
                csv_rows.append(csv_row)
            except Exception as e:
                print(f"[WARNING] Skipping row due to CSVRow conversion error: {e}. Row: {row_dict}")
                continue
        
        print(f"   Successfully mapped {len(csv_rows)} rows to CSVRow models")
        return csv_rows