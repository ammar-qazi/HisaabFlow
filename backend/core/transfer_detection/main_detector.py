"""
Main transfer detector orchestrating all components
"""
from typing import Dict, List, Any
from backend.core.transfer_detection.cross_bank_matcher import CrossBankMatcher
from backend.core.transfer_detection.currency_converter import CurrencyConverter
from backend.core.transfer_detection.confidence_calculator import ConfidenceCalculator
from backend.infrastructure.config.unified_config_service import get_unified_config_service
import logging

logger = logging.getLogger(__name__)


class TransferDetector:
    """
    Enhanced transfer detection system with configurable specifications:
    1. Exchange To Amount matching for currency conversions
    2. Generic name-based cross-bank transfers (Sent money to {name} <-> Incoming from {name})
    3. Currency-based bank targeting (PKR for Pakistani banks, EUR for European accounts)
    4. 24-hour date tolerance with fallback to traditional amount matching
    """
    
    def __init__(self, config_service=None):
        if config_service:
            self.config = config_service
        else:
            self.config = get_unified_config_service()
            
        # Pass the unified config service to CrossBankMatcher
        self.cross_bank_matcher = CrossBankMatcher(config_service=self.config)
            
        self.date_tolerance_hours = self.config.get_date_tolerance()
        self.currency_converter = CurrencyConverter()
        self.confidence_calculator = ConfidenceCalculator()
    
    def detect_transfers(self, csv_data_list: List[Dict]) -> Dict[str, Any]:
        """Main transfer detection function with configurable specifications"""
        
        logger.debug("\n STARTING ENHANCED TRANSFER DETECTION (CONFIG-BASED)")
        logger.debug("=" * 70)
        logger.debug(f" Date tolerance: {self.date_tolerance_hours} hours")
        logger.debug(f" Configured banks: {', '.join(self.config.list_banks())}")
        logger.debug(f"Confidence threshold: {self.config.get_confidence_threshold()}")
        logger.debug("=" * 70)
        
        # Flatten all transactions with source info
        all_transactions = self._prepare_transactions(csv_data_list)
        
        logger.debug(f"\n[DATA] TOTAL TRANSACTIONS LOADED: {len(all_transactions)}")
        
        # Find potential transfers
        logger.debug("\n FINDING TRANSFER CANDIDATES...")
        potential_transfers = self.cross_bank_matcher.find_transfer_candidates(all_transactions)
        logger.debug(f"DEBUG MainDetector: Potential Transfer Candidates ({len(potential_transfers)}):")
        logger.debug(f"   [SUCCESS] Found {len(potential_transfers)} potential transfer candidates")
        
        # STEP 1: Match currency conversions (internal conversions)
        logger.debug("\n MATCHING CURRENCY CONVERSIONS...")
        conversion_pairs = self.currency_converter.match_currency_conversions(all_transactions)
        logger.debug(f"   [SUCCESS] Found {len(conversion_pairs)} currency conversion pairs")
        
        # STEP 2: Match cross-bank transfers using configured specifications
        logger.debug(" MATCHING CROSS-BANK TRANSFERS (CONFIGURED SPECS)...")
        cross_bank_pairs = self.cross_bank_matcher.match_cross_bank_transfers(
            potential_transfers, all_transactions, conversion_pairs
        )
        logger.debug(f"   [SUCCESS] Found {len(cross_bank_pairs)} cross-bank transfer pairs")
        
        # Get potential pairs that failed name matching
        potential_pairs = self.cross_bank_matcher.get_potential_pairs()
        logger.debug(f"   [INFO] Found {len(potential_pairs)} potential pairs (name mismatch)")
        
        # Combine all transfer pairs
        all_transfer_pairs = conversion_pairs + cross_bank_pairs
        
        # Conflict detection and manual-review flagging were never implemented
        conflicts = []
        flagged_transactions = []
        
        logger.debug("\n TRANSFER DETECTION SUMMARY:")
        logger.debug(f"   [DATA] Total transactions: {len(all_transactions)}")
        logger.debug(f"   Total transfer pairs: {len(all_transfer_pairs)}")
        logger.debug(f"    Currency conversions: {len(conversion_pairs)}")
        logger.debug(f"    Cross-bank transfers: {len(cross_bank_pairs)}")
        logger.debug(f"    Potential transfers: {len(potential_transfers)}")
        logger.debug(f"    Potential pairs (name mismatch): {len(potential_pairs)}")
        logger.debug(f"   [WARNING]  Conflicts: {len(conflicts)}")
        logger.debug(f"    Flagged for review: {len(flagged_transactions)}")
        logger.debug("=" * 70)
        
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
            logger.debug(f"\n Processing CSV {csv_idx}: {csv_data.get('file_name', f'CSV_{csv_idx}')}")
            logger.debug(f"   [DATA] Transaction count: {len(csv_data['data'])}")
            
            for trans_idx, transaction in enumerate(csv_data['data']):
                # Get bank type from CSV bank_info if available
                bank_type = 'unknown'
                bank_info = csv_data.get('bank_info', {})
                if bank_info:
                    detected_bank = bank_info.get('bank_name', bank_info.get('detected_bank'))
                    if detected_bank and detected_bank != 'unknown':
                        bank_type = detected_bank
                
                # Fall back to the row's own source bank (set during transformation)
                if bank_type == 'unknown':
                    bank_type = transaction.get('_source_bank') or 'unknown'
                
                # Ensure currency is set
                if 'Currency' not in transaction or not transaction['Currency']:
                    bank_config = self.config.get_bank_config(bank_type)
                    if bank_config and bank_config.currency_primary:
                        transaction['Currency'] = bank_config.currency_primary
                
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
    
