"""
Configuration-driven cross-bank transfer matching
"""
import re
from typing import Dict, List, Set, Optional
from backend.core.transfer_detection.amount_parser import AmountParser
from backend.core.transfer_detection.date_parser import DateParser
from backend.core.transfer_detection.confidence_calculator import ConfidenceCalculator
from backend.infrastructure.config.unified_config_service import get_unified_config_service
import logging

logger = logging.getLogger(__name__)


class CrossBankMatcher:
    """Handles cross-bank transfer detection using configuration-driven rules"""
    
    def __init__(self, config_service=None):
        if config_service:
            self.config = config_service
        else:
            self.config = get_unified_config_service()
        self.date_tolerance_hours = self.config.get_date_tolerance()
        self.confidence_threshold = self.config.get_confidence_threshold()
        # self.currency_converter = CurrencyConverter() # Already initialized in main_detector
        
        self.confidence_calculator = ConfidenceCalculator()
        
        logger.debug(f" CrossBankMatcher: Banks: {', '.join(self.config.list_banks())}")
    
    def find_transfer_candidates(self, transactions: List[Dict]) -> List[Dict]:
        """Find transactions that match configured transfer patterns"""
        candidates = []
        
        for transaction in transactions:
            bank_type = transaction.get('_bank_type', 'unknown')
            original_description = self._get_description(transaction) # Keep original case for logging
            

            # Check outgoing patterns
            outgoing_patterns = self.config.get_transfer_patterns(bank_type, 'outgoing')
            for pattern in outgoing_patterns:
                extracted_name = self.config.extract_name_from_transfer_pattern(pattern, original_description) # Pass original_description
                
                # Check if pattern matches (either name extracted OR direct pattern match)
                pattern_matches = False
                if extracted_name is not None:
                    pattern_matches = True
                elif '{name}' not in pattern and '{user_name}' not in pattern:
                    # Pattern without placeholder - check direct match
                    if pattern.lower() in original_description.lower():
                        pattern_matches = True
                        extracted_name = "DIRECT_MATCH"  # Placeholder for patterns without names
                
                if pattern_matches:
                    candidates.append({
                        **transaction,
                        '_transfer_pattern': pattern,
                        '_is_transfer_candidate': True,
                        '_transfer_direction': 'outgoing'
                    })
                    break # Found an outgoing pattern, no need to check more for this transaction
                else:
                    pass
            
            # Check incoming patterns if not already matched
            if not any(t['_transaction_index'] == transaction['_transaction_index'] for t in candidates):
                incoming_patterns = self.config.get_transfer_patterns(bank_type, 'incoming')
                for pattern in incoming_patterns:
                    extracted_name = self.config.extract_name_from_transfer_pattern(pattern, original_description) # Pass original_description
                    
                    # Check if pattern matches (either name extracted OR direct pattern match)
                    pattern_matches = False
                    if extracted_name is not None:
                        pattern_matches = True
                    elif '{name}' not in pattern and '{user_name}' not in pattern:
                        # Pattern without placeholder - check direct match
                        if pattern.lower() in original_description.lower():
                            pattern_matches = True
                            extracted_name = "DIRECT_MATCH"  # Placeholder for patterns without names
                    
                    if pattern_matches:
                        candidates.append({
                            **transaction,
                            '_transfer_pattern': pattern,
                            '_is_transfer_candidate': True,
                            '_transfer_direction': 'incoming'
                        })
                        break # Found an incoming pattern
                    else:
                        pass
        
        return candidates
    
    def match_cross_bank_transfers(self, potential_transfers: List[Dict], 
                                 all_transactions: List[Dict], 
                                 existing_pairs: List[Dict]) -> List[Dict]:
        """Match cross-bank transfers using configuration-driven rules"""
        transfer_pairs = []
        self.potential_pairs = []  # Store potential pairs that failed name matching
        existing_transaction_ids: Set[int] = set()
        
        # Get IDs of already matched transactions
        for pair in existing_pairs:
            existing_transaction_ids.add(pair['outgoing']['_transaction_index'])
            existing_transaction_ids.add(pair['incoming']['_transaction_index'])
        
        logger.debug(f" MATCHING CROSS-BANK TRANSFERS...")
        
        # Filter available transactions
        available_outgoing = [t for t in potential_transfers 
                            if t['_transaction_index'] not in existing_transaction_ids and 
                               AmountParser.parse_amount(t.get('Amount', '0')) < 0]
        
        # for idx, ao_txn in enumerate(available_outgoing):

        for i, tx in enumerate(available_outgoing[:5]):
            pass

        available_incoming = [t for t in all_transactions 
                            if t['_transaction_index'] not in existing_transaction_ids and 
                               AmountParser.parse_amount(t.get('Amount', '0')) > 0]

        # Match each outgoing transaction
        for outgoing in available_outgoing:
            if outgoing['_transaction_index'] in existing_transaction_ids:
                continue
                
            # Debugging info: Show the contents of existing_transaction_ids
            
            
            best_match = self._find_best_match(outgoing, available_incoming, existing_transaction_ids)
            
            if best_match and best_match['confidence'] >= self.confidence_threshold:
                transfer_pair = self._create_transfer_pair(outgoing, best_match, len(transfer_pairs))
                
                
                transfer_pairs.append(transfer_pair)
                existing_transaction_ids.add(outgoing['_transaction_index'])
                existing_transaction_ids.add(best_match['incoming']['_transaction_index'])
        
        logger.debug(f"[SUCCESS] Created {len(transfer_pairs)} cross-bank transfer pairs")
        logger.debug(f"[INFO] Found {len(self.potential_pairs)} potential pairs (failed name matching)")
        return transfer_pairs
    
    def _find_best_match(self, outgoing: Dict, available_incoming: List[Dict], 
                        existing_transaction_ids: Set[int]) -> Optional[Dict]: # Return type can be None
        """Find the best matching incoming transaction using configuration"""

        outgoing_amount = abs(AmountParser.parse_amount(outgoing.get('Amount', '0')))
        exchange_amount = self._get_exchange_amount_from_csv(outgoing)
        exchange_currency = self._get_exchange_currency_from_csv(outgoing)

        # === Logging as per request ===

        if not available_incoming:
            # === Logging as per request ===
            return None # Explicitly return None if no candidates

        
        best_match = None
        best_confidence = 0.0
        
        # Corrected loop with enumerate and proper indentation for the body
        for incoming_idx, incoming in enumerate(available_incoming):
            # Check if already used or same CSV
            if (incoming['_transaction_index'] in existing_transaction_ids or
                incoming['_csv_index'] == outgoing['_csv_index']):  # Must be different CSV
                # === Logging as per request: Rejection reason ===
                logger.debug(f"  - Reason for rejection: Already used or same CSV file.")
                continue
            
            incoming_amount = AmountParser.parse_amount(incoming.get('Amount', '0'))
            
            # Check date tolerance first
            # === Logging as per request: Date tolerance check ===
            outgoing_date_obj = DateParser.parse_date(self._get_date_string(outgoing))
            incoming_date_obj = DateParser.parse_date(self._get_date_string(incoming))
            hours_diff = abs((outgoing_date_obj - incoming_date_obj).total_seconds() / 3600) if outgoing_date_obj and incoming_date_obj else float('inf')
            date_check_passed = self._check_date_tolerance(outgoing, incoming) # Uses internal parsing
            
            logger.debug(f"  - Outgoing date: {self._get_date_string(outgoing)}") # Already logged as part of Outgoing details
            pass # Use already fetched value
            logger.debug(f"  - Difference in hours: {hours_diff:.2f}")
            logger.debug(f"  - Date tolerance setting: {self.date_tolerance_hours} hours")
            logger.debug(f"  - Result: {'PASS' if date_check_passed else 'FAIL'}")

            if not date_check_passed:
                # === Logging as per request: Rejection reason ===
                logger.debug(f"  - Reason for rejection: Date mismatch (Diff: {hours_diff:.2f}h, Tolerance: {self.date_tolerance_hours}h)")
                continue

            # Check if this could be a cross-bank transfer using config
            # === Logging as per request: Cross-bank transfer validation (done inside _is_cross_bank_transfer) ===
            is_transfer_check_result, details = self._is_cross_bank_transfer(outgoing, incoming, debug=True)
            if not is_transfer_check_result:
                # === Logging as per request: Rejection reason ===
                # _is_cross_bank_transfer logs its own details when debug=True
                logger.debug(f"  - Reason for rejection: _is_cross_bank_transfer failed (Details logged above by _is_cross_bank_transfer)")
                
                # Check if this was a name mismatch - if so, validate amounts before storing as potential pair
                if details.get('names_match_result') is False:
                    # Check if amounts match using the same logic as _evaluate_matching_strategies
                    amounts_match = self._validate_amount_matching(outgoing, incoming, outgoing_amount, incoming_amount, exchange_amount, exchange_currency)
                    
                    if amounts_match:
                        potential_pair = {
                            'outgoing': outgoing,
                            'incoming': incoming,
                            'reason': 'name_mismatch',
                            'outgoing_name': details.get('outgoing_name'),
                            'incoming_name': details.get('incoming_name'),
                            'amount_match': True,
                            'date_match': True,
                            'date_diff_hours': hours_diff,
                            'confidence': 0.7  # High confidence except for name
                        }
                        self.potential_pairs.append(potential_pair)
                        logger.debug(f"  - CAPTURED POTENTIAL PAIR: Names don't match ('{details.get('outgoing_name')}' vs '{details.get('incoming_name')}') but amount/date do")
                    else:
                        logger.debug(f"  - NOT capturing potential pair: Names don't match AND amounts don't match")
                
                continue
            
            matches = self._evaluate_matching_strategies(
                outgoing, incoming, outgoing_amount, incoming_amount, 
                exchange_amount, exchange_currency
            )
            
            # Choose best match for this incoming transaction
            if matches:
                best_incoming_match = max(matches, key=lambda x: x['confidence'])
                
                if best_incoming_match['confidence'] > best_confidence:
                    best_confidence = best_incoming_match['confidence']
                    best_match = {
                        'incoming': incoming,
                        'incoming_amount': incoming_amount,
                        **best_incoming_match
                    }
                # No specific log if not better, to reduce noise
            else:
                pass
        
        if not best_match:
            pass
        else:
            pass
        return best_match
    
    def _is_cross_bank_transfer(self, outgoing: Dict, incoming: Dict, debug: bool = False) -> (bool, Dict):
        """Check if transactions form a cross-bank transfer using configuration"""
        outgoing_bank = outgoing.get('_bank_type', '')
        incoming_bank = incoming.get('_bank_type', '')
        
        # Must be different banks
        if outgoing_bank == incoming_bank:
            return False, {"reason": "Same bank"}

        outgoing_desc = self._get_description(outgoing)
        incoming_desc = self._get_description(incoming)
        
        outgoing_patterns = self.config.get_transfer_patterns(outgoing_bank, 'outgoing')
        incoming_patterns = self.config.get_transfer_patterns(incoming_bank, 'incoming')
        

        # Extract names from outgoing transaction
        outgoing_name = None
        for pattern in outgoing_patterns:
            extracted_name = self.config.extract_name_from_transfer_pattern(pattern, outgoing_desc)

        # Extract names from outgoing transaction
        outgoing_name = None
        for pattern in outgoing_patterns:
            extracted_name = self.config.extract_name_from_transfer_pattern(pattern, outgoing_desc)
            if extracted_name:
                outgoing_name = extracted_name
                break
        
        # Extract names from incoming transaction  
        incoming_name = None
        for pattern in incoming_patterns:
            extracted_name = self.config.extract_name_from_transfer_pattern(pattern, incoming_desc)
            if extracted_name:
                incoming_name = extracted_name
                break
        
        # If we found names in both transactions, check if they could match
        if outgoing_name and incoming_name:
            # Names should be similar (same person transferring)
            names_match_res = self._names_match(outgoing_name, incoming_name)
            if debug:
                logger.debug(f"  - Name match result: {str(names_match_res).upper()}") # Requested format
            return names_match_res, {"outgoing_name": outgoing_name, "incoming_name": incoming_name, "names_match_result": names_match_res}
        
        # Fallback to simple pattern matching if name extraction fails
        outgoing_matches = any(self._pattern_matches(pattern, outgoing_desc) for pattern in outgoing_patterns)
        incoming_matches = any(self._pattern_matches(pattern, incoming_desc) for pattern in incoming_patterns)
        
        return outgoing_matches and incoming_matches, {"reason": "Fallback pattern match", "outgoing_matches": outgoing_matches, "incoming_matches": incoming_matches}
    
    def _pattern_matches(self, pattern: str, description: str) -> bool:
        """Check if pattern matches description (simple version without name extraction)"""
        # Remove {name} placeholder and check if rest of pattern matches
        simple_pattern = pattern.replace('{name}', '').strip()
        return simple_pattern.lower() in description.lower()
    
    def _names_match(self, name1: str, name2: str) -> bool:
        """Check if two extracted names could refer to the same person"""
        if not name1 or not name2:
            return False
        
        name1_parts = re.findall(r'\w+', name1.lower())
        name2_parts = re.findall(r'\w+', name2.lower())
        if not name1_parts or not name2_parts:
            return False
        
        # Same words, or one name is a shorter form of the other ("John" vs "John Smith")
        set1, set2 = set(name1_parts), set(name2_parts)
        if set1 <= set2 or set2 <= set1:
            return True
        
        # Otherwise require two meaningful shared words. One shared word is not
        # enough: "Muhammad Ali" and "Muhammad Khan" are different people.
        shared = {word for word in set1 & set2 if len(word) >= 3}
        return len(shared) >= 2
    
    def _check_date_tolerance(self, outgoing: Dict, incoming: Dict) -> bool:
        """Check if dates are within tolerance"""
        outgoing_date_str = self._get_date_string(outgoing)
        incoming_date_str = self._get_date_string(incoming)
        
        return DateParser.dates_within_tolerance(
            DateParser.parse_date(outgoing_date_str),
            DateParser.parse_date(incoming_date_str),
            self.date_tolerance_hours
        )
    
    def _get_date_string(self, transaction: Dict) -> str:
        """Get date string from transaction"""
        return (
            transaction.get('Date', '') or 
            transaction.get('\ufeffDate', '') or 
            transaction.get('TIMESTAMP', '') or 
            transaction.get('TransactionDate', '')
        )
    
    def _evaluate_matching_strategies(self, outgoing: Dict, incoming: Dict,
                                    outgoing_amount: float, incoming_amount: float,
                                    exchange_amount: float, exchange_currency: str) -> List[Dict]:
        # Renamed for clarity: these are amounts in their original currencies
        outgoing_amount_orig_curr = outgoing_amount
        incoming_amount_orig_curr = incoming_amount

        """Evaluate all matching strategies and return matches"""
        matches = []

        outgoing_currency = outgoing.get('Currency', self.config.get_bank_config(outgoing.get('_bank_type')).currency_primary if outgoing.get('_bank_type') and self.config.get_bank_config(outgoing.get('_bank_type')) else None)
        incoming_currency = incoming.get('Currency', self.config.get_bank_config(incoming.get('_bank_type')).currency_primary if incoming.get('_bank_type') and self.config.get_bank_config(incoming.get('_bank_type')) else None)


        # Strategy 1: Exchange To Amount matching (PRIORITY for Wise-like transactions)
        if exchange_amount is not None and exchange_currency: # exchange_amount can be 0.0
            pass # Requested header

            currency_match_check = (exchange_currency == incoming_currency)

            if currency_match_check:
                # Only check amount if currency matches
                amount_match_check = AmountParser.amounts_match(exchange_amount, incoming_amount_orig_curr)
                

                if amount_match_check:
                    confidence = self.confidence_calculator.calculate_confidence(
                        outgoing, incoming, is_cross_bank=True, is_exchange_match=True
                    )
                    matches.append({
                        'type': 'exchange_amount',
                        'confidence': confidence,
                        'matched_amount': exchange_amount, # This is the amount in the target currency
                        'match_details': f"Exchange {exchange_amount} {exchange_currency}"
                    })
                    # Old log, replaced by "Strategy 1 final result..."
                else:
                    pass
                    # Old log, replaced by "Strategy 1 final result..."
            else:
                pass
                # This path is taken if currencies do not match. The reason is already logged by the currency comparison print.
        else: # exchange_amount or exchange_currency is None/empty
            pass

        # Strategy 2: Traditional amount matching (same currency only)
        if outgoing_currency == incoming_currency:
            if AmountParser.amounts_match(outgoing_amount_orig_curr, incoming_amount_orig_curr):
                confidence = self.confidence_calculator.calculate_confidence(
                    outgoing, incoming, is_cross_bank=True
                )
                matches.append({
                    'type': 'traditional_same_currency',
                    'confidence': confidence,
                    'matched_amount': outgoing_amount_orig_curr,
                    'match_details': f"Traditional {outgoing_amount_orig_curr} {outgoing_currency}"
                })
        else:
            pass
        
        if not matches:
            pass
        return matches
    
    def _create_transfer_pair(self, outgoing: Dict, best_match: Dict, pair_index: int) -> Dict:
        """Create a transfer pair from matched transactions"""
        outgoing_amount = abs(AmountParser.parse_amount(outgoing.get('Amount', '0')))
        incoming_amount = AmountParser.parse_amount(best_match['incoming'].get('Amount', '0'))
        
        # Set exchange_amount based on strategy
        if best_match['type'] == 'exchange_amount':
            exchange_amount = self._get_exchange_amount_from_csv(outgoing)
        else:
            exchange_amount = incoming_amount  # Default to incoming amount
        
        return {
            'outgoing': outgoing,
            'incoming': best_match['incoming'],
            'amount': outgoing_amount,
            'matched_amount': best_match['matched_amount'],
            'exchange_amount': exchange_amount,
            'date': DateParser.parse_date(outgoing.get('Date', '')),
            'confidence': best_match['confidence'],
            'pair_id': f"cross_bank_{pair_index}",
            'transfer_type': f"cross_bank_{best_match['type']}",
            'match_strategy': best_match['type'],
            'match_details': best_match['match_details']
        }
    
    def _get_description(self, transaction: Dict) -> str:
        """Get description from transaction with fallback fields"""
        return str(
            transaction.get('_original_title', '') or # Prioritize original title
            transaction.get('Description', '') or 
            transaction.get('Title', '') or 
            transaction.get('Note', '') or 
            transaction.get('DESCRIPTION', '') or 
            transaction.get('TYPE', '')
        )
    
    def _get_exchange_amount_from_csv(self, transaction: Dict) -> Optional[float]:
        """Get exchange amount from static CSV columns only"""
        exchange_amount_columns = [
            'Exchange To Amount',
            'Exchange_To_Amount', 
            'ExchangeToAmount',
            'exchange_to_amount',
            'exchangetoamount'
        ]
        
        for col in exchange_amount_columns:
            if col in transaction:
                exchange_value = transaction[col]
                if exchange_value and str(exchange_value).strip() not in ['', 'nan', 'NaN', 'null', 'None']:
                    try:
                        parsed_amount = AmountParser.parse_amount(str(exchange_value))
                        if parsed_amount != 0:
                            return abs(parsed_amount)
                    except (ValueError, TypeError):
                        continue
        return None
    
    def _get_exchange_currency_from_csv(self, transaction: Dict) -> Optional[str]:
        """Get exchange currency from static CSV columns only"""
        exchange_currency_columns = [
            'Exchange To',
            'Exchange_To',
            'ExchangeTo',
            'exchange_to',
            'exchangetocurrency'
        ]
        
        for col in exchange_currency_columns:
            if col in transaction:
                currency_value = transaction[col]
                if currency_value and str(currency_value).strip() not in ['', 'nan', 'NaN', 'null', 'None']:
                    val_str = str(currency_value).strip().upper()
                    if len(val_str) == 3 and val_str.isalpha():
                        return val_str
        return None
    
    def _validate_amount_matching(self, outgoing: Dict, incoming: Dict,
                                outgoing_amount: float, incoming_amount: float,
                                exchange_amount: float, exchange_currency: str) -> bool:
        """Validate if amounts match using the same logic as _evaluate_matching_strategies"""
        
        outgoing_currency = outgoing.get('Currency', self.config.get_bank_config(outgoing.get('_bank_type')).currency_primary if outgoing.get('_bank_type') and self.config.get_bank_config(outgoing.get('_bank_type')) else None)
        incoming_currency = incoming.get('Currency', self.config.get_bank_config(incoming.get('_bank_type')).currency_primary if incoming.get('_bank_type') and self.config.get_bank_config(incoming.get('_bank_type')) else None)
        
        
        # Strategy 1: Exchange To Amount matching (PRIORITY for Wise-like transactions)
        if exchange_amount is not None and exchange_currency:
            if exchange_currency == incoming_currency:
                amount_match = AmountParser.amounts_match(exchange_amount, incoming_amount)
                if amount_match:
                    return True
        
        # Strategy 2: Direct amount matching (same currency)
        if outgoing_currency == incoming_currency:
            amount_match = AmountParser.amounts_match(outgoing_amount, incoming_amount)
            if amount_match:
                return True
        
        # Strategy 3: Cross-currency matching (would need currency conversion rates)
        # For now, we'll skip this as it requires external currency conversion data
        # This could be added later if needed
        
        return False

    def get_potential_pairs(self) -> List[Dict]:
        """Get the potential pairs that failed name matching but passed amount/date checks"""
        return getattr(self, 'potential_pairs', [])
