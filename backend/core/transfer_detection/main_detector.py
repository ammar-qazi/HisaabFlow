"""
Main transfer detector orchestrating all components
"""
from typing import Dict, List, Any, Optional
from backend.core.transfer_detection.amount_parser import AmountParser
from backend.core.transfer_detection.date_parser import DateParser
from backend.core.transfer_detection.cross_bank_matcher import CrossBankMatcher
from backend.core.transfer_detection.currency_converter import CurrencyConverter
from backend.core.transfer_detection.confidence_calculator import ConfidenceCalculator
from backend.infrastructure.config.unified_config_service import get_unified_config_service


class TransferDetector:
    """
    Enhanced transfer detection system with configurable specifications:
    1. Exchange To Amount matching for currency conversions
    2. Generic name-based cross-bank transfers (Sent money to {name} <-> Incoming from {name})
    3. Currency-based bank targeting (PKR for Pakistani banks, EUR for European accounts)
    4. 24-hour date tolerance with fallback to traditional amount matching
    """
    
    def __init__(self, config_dir: str = "configs", config_service=None):
        if config_service:
            self.config = config_service
        else:
            self.config = get_unified_config_service(config_dir)
            
        # Pass the unified config service to CrossBankMatcher
        self.cross_bank_matcher = CrossBankMatcher(config_service=self.config)
            
        self.date_tolerance_hours = self.config.get_date_tolerance()
        self.currency_converter = CurrencyConverter()
        self.confidence_calculator = ConfidenceCalculator()
    
    def detect_transfers(self, csv_data_list: List[Dict]) -> Dict[str, Any]:
        """Main transfer detection function with configurable specifications"""
        
        print("\n STARTING ENHANCED TRANSFER DETECTION (CONFIG-BASED)")
        print("=" * 70)
        print(f" Date tolerance: {self.date_tolerance_hours} hours")
        print(f" Configured banks: {', '.join(self.config.list_banks())}")
        print(f"Confidence threshold: {self.config.get_confidence_threshold()}")
        print("=" * 70)
        
        # Flatten all transactions with source info
        all_transactions = self._prepare_transactions(csv_data_list)
        
        print(f"\n[DATA] TOTAL TRANSACTIONS LOADED: {len(all_transactions)}")
        
        # Find potential transfers
        print("\n FINDING TRANSFER CANDIDATES...")
        potential_transfers = self.cross_bank_matcher.find_transfer_candidates(all_transactions)
        print(f"DEBUG MainDetector: Potential Transfer Candidates ({len(potential_transfers)}):")
        for pt_idx, pt in enumerate(potential_transfers):
            print(f"  PT {pt_idx}: Desc='{pt.get('Description', pt.get('Title', ''))[:60]}...', Amt={pt.get('Amount')}, Date={pt.get('Date')}, Bank={pt.get('_bank_type')}, Dir={pt.get('_transfer_direction')}, CSV='{pt.get('_csv_name')}'")
        print(f"   [SUCCESS] Found {len(potential_transfers)} potential transfer candidates")
        
        # STEP 1: Match currency conversions (internal conversions)
        print("\n MATCHING CURRENCY CONVERSIONS...")
        conversion_pairs = self.currency_converter.match_currency_conversions(all_transactions)
        print(f"   [SUCCESS] Found {len(conversion_pairs)} currency conversion pairs")
        
        # STEP 2: Match cross-bank transfers using configured specifications
        print(" MATCHING CROSS-BANK TRANSFERS (CONFIGURED SPECS)...")
        cross_bank_pairs = self.cross_bank_matcher.match_cross_bank_transfers(
            potential_transfers, all_transactions, conversion_pairs
        )
        print(f"   [SUCCESS] Found {len(cross_bank_pairs)} cross-bank transfer pairs")
        
        # Get potential pairs that failed name matching
        potential_pairs = self.cross_bank_matcher.get_potential_pairs()
        print(f"   [INFO] Found {len(potential_pairs)} potential pairs (name mismatch)")
        
        # Combine all transfer pairs
        all_transfer_pairs = conversion_pairs + cross_bank_pairs
        
        # Detect conflicts and flag manual review
        conflicts = self._detect_conflicts(all_transfer_pairs)
        flagged_transactions = self._flag_manual_review(all_transactions, all_transfer_pairs)
        
        print("\n TRANSFER DETECTION SUMMARY:")
        print(f"   [DATA] Total transactions: {len(all_transactions)}")
        print(f"   Total transfer pairs: {len(all_transfer_pairs)}")
        print(f"    Currency conversions: {len(conversion_pairs)}")
        print(f"    Cross-bank transfers: {len(cross_bank_pairs)}")
        print(f"    Potential transfers: {len(potential_transfers)}")
        print(f"    Potential pairs (name mismatch): {len(potential_pairs)}")
        print(f"   [WARNING]  Conflicts: {len(conflicts)}")
        print(f"    Flagged for review: {len(flagged_transactions)}")
        print("=" * 70)
        
        return {
            'processed_transactions': all_transactions, # Return the transactions with _transaction_index
            'transfers': all_transfer_pairs,
            'potential_transfers': potential_transfers,
            'potential_pairs': potential_pairs,  # Add potential pairs to response
            'conflicts': conflicts,
            'flagged_transactions': flagged_transactions,
            'summary': {
                'total_transactions': len(all_transactions),
                'transfer_pairs_found': len(all_transfer_pairs),
                'currency_conversions': len(conversion_pairs),
                'other_transfers': len(cross_bank_pairs),
                'potential_transfers': len(potential_transfers),
                'potential_pairs': len(potential_pairs),  # Add to summary
                'conflicts': len(conflicts),
                'flagged_for_review': len(flagged_transactions)
            }
        }
    
    def _prepare_transactions(self, csv_data_list: List[Dict]) -> List[Dict]:
        """Flatten all transactions with source info and metadata"""
        all_transactions = []
        global_transaction_counter = 0 # Initialize a global counter
        
        for csv_idx, csv_data in enumerate(csv_data_list):
            print(f"\n Processing CSV {csv_idx}: {csv_data.get('file_name', f'CSV_{csv_idx}')}")
            print(f"   [DATA] Transaction count: {len(csv_data['data'])}")
            
            # DEBUG: Check CSV data structure
            if csv_data['data']:
                sample_transaction = csv_data['data'][0]
                print(f"    Available columns: {list(sample_transaction.keys())}")
            
            for trans_idx, transaction in enumerate(csv_data['data']):
                # Get bank type from CSV bank_info if available
                bank_type = 'unknown'
                bank_info = csv_data.get('bank_info', {})
                if bank_info:
                    detected_bank = bank_info.get('bank_name', bank_info.get('detected_bank'))
                    if detected_bank and detected_bank != 'unknown':
                        bank_type = detected_bank
                
                # Fallback to filename detection if bank info not available
                if bank_type == 'unknown':
                    bank_type = self.config.detect_bank_type(csv_data.get('file_name', ''))
                
                enhanced_transaction = {
                    **transaction,
                    '_csv_index': csv_idx,
                    '_transaction_index': global_transaction_counter, # Use global counter
                    '_csv_name': csv_data.get('file_name', ''),
                    '_bank_type': bank_type,
                    '_raw_data': transaction
                }
                all_transactions.append(enhanced_transaction)
                global_transaction_counter += 1 # Increment global counter
        
        return all_transactions
    
    def _detect_conflicts(self, transfer_pairs: List[Dict]) -> List[Dict]:
        """Detect transactions that could match multiple partners"""
        return []
    
    def _flag_manual_review(self, all_transactions: List[Dict], transfer_pairs: List[Dict]) -> List[Dict]:
        """Flag transactions that need manual review"""
        return []
    
    def apply_transfer_categorization(self, csv_data_list: List[Dict], transfer_pairs: List[Dict]) -> List[Dict]:
        """Apply Balance Correction category to detected transfers"""
        transfer_matches = []
        
        for pair in transfer_pairs:
            outgoing = pair['outgoing']
            incoming = pair['incoming']
            
            # Include exchange amount information in notes
            exchange_note = ""
            if pair.get('exchange_amount'):
                exchange_note = f" | Exchange Amount: {pair['exchange_amount']}"
            
            transfer_matches.append({
                'csv_index': outgoing['_csv_index'],
                'amount': str(AmountParser.parse_amount(outgoing.get('Amount', '0'))),
                'date': DateParser.parse_date(outgoing.get('Date', '')).strftime('%Y-%m-%d'),
                'description': str(outgoing.get('Description', '')),
                'category': 'Balance Correction',
                'note': f"Transfer out - {pair['transfer_type']} - Pair ID: {pair['pair_id']}{exchange_note}",
                'pair_id': pair['pair_id'],
                'transfer_type': 'outgoing',
                'match_strategy': pair.get('match_strategy', 'traditional')
            })
            
            transfer_matches.append({
                'csv_index': incoming['_csv_index'],
                'amount': str(AmountParser.parse_amount(incoming.get('Amount', '0'))),
                'date': DateParser.parse_date(incoming.get('Date', '')).strftime('%Y-%m-%d'),
                'description': str(incoming.get('Description', '')),
                'category': 'Balance Correction',
                'note': f"Transfer in - {pair['transfer_type']} - Pair ID: {pair['pair_id']}{exchange_note}",
                'pair_id': pair['pair_id'],
                'transfer_type': 'incoming',
                'match_strategy': pair.get('match_strategy', 'traditional')
            })
        
        return transfer_matches
