"""
Transfer processing service for orchestrating transfer detection and categorization
"""
from typing import Dict, List, Any, Optional
from pathlib import Path

from backend.transfer_detection.main_detector import TransferDetector
from backend.shared.config.unified_config_service import get_unified_config_service


class TransferProcessingService:
    """Service focused on transfer detection and processing"""
    
    def __init__(self):
        # Determine config directory path
        current_file_dir = Path(__file__).resolve().parent
        project_root = current_file_dir.parent.parent.parent
        config_dir_path = project_root / "configs"
        config_dir_path_str = str(config_dir_path)
        
        # Create unified config service instance for transfer detection
        self.config_service = get_unified_config_service(config_dir_path_str)
        self.transfer_detector = TransferDetector(config_service=self.config_service)
        
        print(f"ℹ [TransferProcessingService] Initialized with TransferDetector")
    
    def run_transfer_detection(self, data: List[Dict[str, Any]], 
                              csv_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run transfer detection on processed data
        
        Args:
            data: List of processed transaction data
            csv_data_list: Original CSV data list with bank info
            
        Returns:
            dict: Transfer detection results
        """
        print(f"ℹ [TransferProcessingService] Running transfer detection...")
        print(f"   [DATA] Input data rows: {len(data)}")
        
        # DEBUG: Show sample data structure
        if data:
            print(f"      Sample row keys: {list(data[0].keys())}")
            print(f"      Sample row: {data[0]}")
        
        # Group data by account/bank for transfer detection
        accounts = {}
        for row in data:
            account = row.get('Account', 'Unknown')
            if account not in accounts:
                accounts[account] = []
            accounts[account].append(row)
        
        print(f"      Accounts found: {list(accounts.keys())}")
        
        # Create csv_data_list format for transfer detector with bank info
        csv_data_for_detector = []
        
        for account, rows in accounts.items():
            # Find the matching CSV data for this account to get bank info
            bank_info = self._find_bank_info_for_account(account, csv_data_list)
            
            csv_data = {
                'data': rows,
                'file_name': f'{account}.csv',
                'bank_info': bank_info,
                'template_config': {}
            }
            csv_data_for_detector.append(csv_data)
            print(f"         Account '{account}': {len(rows)} transactions")
        
        print(f"      Prepared {len(csv_data_for_detector)} CSV data items for transfer detection")
        
        try:
            # Run transfer detection
            print(f"      Calling TransferDetector.detect_transfers()...")
            detection_result = self.transfer_detector.detect_transfers(csv_data_for_detector)
            
            print(f"   [DATA] Transfer detection results:")
            print(f"         Summary: {detection_result.get('summary', {})}")
            print(f"         Transfer pairs: {len(detection_result.get('transfers', []))}")
            print(f"         Potential transfers: {len(detection_result.get('potential_transfers', []))}")
            
            return {
                "summary": detection_result.get('summary', {}),
                "transfers": detection_result.get('transfers', []),
                "potential_transfers": detection_result.get('potential_transfers', []),
                "potential_pairs": detection_result.get('potential_pairs', []),
                "processed_transactions": detection_result.get('processed_transactions', data),
                "conflicts": detection_result.get('conflicts', []),
                "flagged_transactions": detection_result.get('flagged_transactions', [])
            }
        except Exception as e:
            print(f"[WARNING] Transfer detection error: {e}")
            import traceback
            print(f"   Transfer detection traceback: {traceback.format_exc()}")
            return {
                "summary": {
                    "transfer_pairs_found": 0,
                    "potential_transfers": 0,
                    "potential_pairs": 0,
                    "conflicts": 0,
                    "flagged_for_review": 0
                },
                "transfers": [],
                "processed_transactions": data,
                "potential_transfers": [],
                "potential_pairs": [],
                "conflicts": [],
                "flagged_transactions": []
            }
    
    def apply_transfer_categorization(self, data: List[Dict[str, Any]], 
                                    transfer_analysis: Dict[str, Any],
                                    manually_confirmed_pairs: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Apply configured category to detected transfers and update notes
        
        Args:
            data: List of transaction data
            transfer_analysis: Transfer analysis results
            manually_confirmed_pairs: User-confirmed transfer pairs
            
        Returns:
            List of transactions with updated categories
        """
        print(f"ℹ [TransferProcessingService] Applying transfer categorization...")
        
        # Combine auto-detected and manually confirmed transfer pairs
        auto_detected_pairs = transfer_analysis.get('transfers', [])
        manually_confirmed_pairs = manually_confirmed_pairs or []
        
        # Combine all transfer pairs for categorization
        all_transfer_pairs = auto_detected_pairs + manually_confirmed_pairs
        
        print(f"   Auto-detected pairs: {len(auto_detected_pairs)}")
        print(f"   Manually confirmed pairs: {len(manually_confirmed_pairs)}")
        print(f"   Total pairs to categorize: {len(all_transfer_pairs)}")
        
        # Get the configured category for transfers
        transfer_category = self.config_service.get_default_transfer_category()
        print(f"   Using category '{transfer_category}' for transfer pairs")
        
        if not all_transfer_pairs:
            print("   No transfer pairs found to categorize")
            return data
        
        # Create a lookup for transfer transactions by their _transaction_index
        transfer_details_by_index = {}
        for pair in all_transfer_pairs:
            outgoing_tx = pair.get('outgoing')
            incoming_tx = pair.get('incoming')
            pair_id = pair.get('pair_id', 'manual_pair' if pair.get('manual') else 'unknown_pair')
            match_strategy = pair.get('match_strategy', 'manual_confirmation' if pair.get('manual') else 'unknown_strategy')
            
            if outgoing_tx and '_transaction_index' in outgoing_tx:
                transfer_details_by_index[outgoing_tx['_transaction_index']] = {
                    'type': 'outgoing',
                    'pair_id': pair_id,
                    'match_strategy': match_strategy
                }
            if incoming_tx and '_transaction_index' in incoming_tx:
                transfer_details_by_index[incoming_tx['_transaction_index']] = {
                    'type': 'incoming',
                    'pair_id': pair_id,
                    'match_strategy': match_strategy
                }
        
        if not transfer_details_by_index:
            print("   No transactions with _transaction_index found in transfer pairs")
            return data
        
        matches_applied = 0
        for row in data:
            row_transaction_index = row.get('_transaction_index')
            if row_transaction_index is not None and row_transaction_index in transfer_details_by_index:
                details = transfer_details_by_index[row_transaction_index]
                row['Category'] = transfer_category
                
                current_note = row.get('Note', '')
                note_suffix = f" | Transfer {details['type']} (Pair: {details['pair_id']}, Strategy: {details['match_strategy']})"
                
                # Avoid appending if already present
                if note_suffix not in current_note:
                    row['Note'] = (current_note + note_suffix).strip().lstrip(" | ")
                
                matches_applied += 1
        
        print(f"   [SUCCESS] Applied '{transfer_category}' category and updated notes for {matches_applied} transactions")
        return data
    
    def apply_transfer_categorization_only(self, transformed_data: List[Dict[str, Any]],
                                          manually_confirmed_pairs: List[Dict[str, Any]],
                                          transfer_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply transfer categorization to existing transformed data (lightweight operation)
        
        Args:
            transformed_data: Existing transformed data
            manually_confirmed_pairs: User-confirmed transfer pairs
            transfer_analysis: Existing transfer analysis
            
        Returns:
            dict: Updated transformed data with proper categorization
        """
        print(f"ℹ [TransferProcessingService] Applying transfer categorization only...")
        
        try:
            print(f"   Transformed data rows: {len(transformed_data)}")
            print(f"   Manually confirmed pairs: {len(manually_confirmed_pairs)}")
            print(f"   Existing transfer pairs: {len(transfer_analysis.get('transfers', []))}")
            
            if not transformed_data:
                return {
                    "success": False,
                    "error": "No transformed data provided"
                }
            
            # Apply transfer categorization with manual confirmations
            updated_data = self.apply_transfer_categorization(
                transformed_data.copy(),
                transfer_analysis,
                manually_confirmed_pairs
            )
            
            # Calculate how many transactions were updated
            updated_count = 0
            transfer_category = self.config_service.get_default_transfer_category()
            for row in updated_data:
                if row.get('Category') == transfer_category:
                    # Check if this is from a transfer (has transfer note)
                    note = row.get('Note', '')
                    if 'Transfer' in note:
                        updated_count += 1
            
            print(f"   [SUCCESS] Updated categories for {updated_count} transactions")
            
            return {
                "success": True,
                "transformed_data": updated_data,
                "updated_transactions": updated_count,
                "category_applied": transfer_category
            }
            
        except Exception as e:
            print(f"[ERROR] Transfer categorization error: {str(e)}")
            import traceback
            print(f"   Full traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _find_bank_info_for_account(self, account: str, csv_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find bank info for a specific account from CSV data list"""
        for csv_item in csv_data_list:
            csv_bank_info = csv_item.get('bank_info', {})
            if csv_bank_info:
                detected_bank = csv_bank_info.get('bank_name', csv_bank_info.get('detected_bank'))
                if detected_bank and detected_bank != 'unknown':
                    try:
                        bank_config = self.config_service.get_bank_config(detected_bank)
                        if bank_config:
                            cashew_account = bank_config.cashew_account or ''
                            if cashew_account == account:
                                return csv_bank_info
                    except:
                        continue
        return {}