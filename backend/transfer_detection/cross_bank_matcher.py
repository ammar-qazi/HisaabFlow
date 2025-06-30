"""
Configuration-driven cross-bank transfer matching
"""
from typing import Dict, List, Set, Optional # Added Optional
from .amount_parser import AmountParser
from .date_parser import DateParser
from .exchange_analyzer import ExchangeAnalyzer # Keep this
from .confidence_calculator import ConfidenceCalculator
from ..shared.config.unified_config_service import get_unified_config_service


class CrossBankMatcher:
    """Handles cross-bank transfer detection using configuration-driven rules"""
    
    def __init__(self, config_dir: str = "configs", config_service=None):
        if config_service:
            self.config = config_service
        else:
            self.config = get_unified_config_service(config_dir)
        self.date_tolerance_hours = self.config.get_date_tolerance()
        self.confidence_threshold = self.config.get_confidence_threshold()
        # self.currency_converter = CurrencyConverter() # Already initialized in main_detector
        
        self.exchange_analyzer = ExchangeAnalyzer()
        self.confidence_calculator = ConfidenceCalculator()
        
        print(f" CrossBankMatcher: Banks: {', '.join(self.config.list_banks())}")
    
    def find_transfer_candidates(self, transactions: List[Dict]) -> List[Dict]:
        """Find transactions that match configured transfer patterns"""
        candidates = []
        
        for transaction in transactions:
            bank_type = transaction.get('_bank_type', 'unknown')
            original_description = self._get_description(transaction) # Keep original case for logging
            description_for_matching = original_description.lower() # Use lower for matching
            
            print(f"DEBUG CBM find_candidates: Processing Tx from CSV '{transaction.get('_csv_name')}', BankType='{bank_type}', Desc='{original_description[:60]}...'")

            # Check outgoing patterns
            outgoing_patterns = self.config.get_transfer_patterns(bank_type, 'outgoing')
            for pattern in outgoing_patterns:
                print(f"DEBUG CBM find_candidates:   Checking OUT pattern '{pattern}' for desc '{original_description[:50]}...' (Bank: {bank_type})")
                extracted_name = self.config.extract_name_from_transfer_pattern(pattern, original_description) # Pass original_description
                if extracted_name is not None:
                    candidates.append({
                        **transaction,
                        '_transfer_pattern': pattern,
                        '_is_transfer_candidate': True,
                        '_transfer_direction': 'outgoing'
                    })
                    print(f"DEBUG CBM find_candidates:   -> ADDED OUTGOING Candidate: Desc='{original_description[:60]}...', Name='{extracted_name}', Amt='{transaction.get('Amount')}', Bank='{bank_type}', CSV='{transaction.get('_csv_name')}'")
                    break # Found an outgoing pattern, no need to check more for this transaction
                else:
                    print(f"DEBUG CBM find_candidates:     -> No outgoing name extracted with pattern '{pattern}' for desc '{original_description[:60]}...'")
            
            # Check incoming patterns if not already matched
            if not any(t['_transaction_index'] == transaction['_transaction_index'] for t in candidates):
                incoming_patterns = self.config.get_transfer_patterns(bank_type, 'incoming')
                for pattern in incoming_patterns:
                    print(f"DEBUG CBM find_candidates:   Checking IN pattern '{pattern}' for desc '{original_description[:50]}...' (Bank: {bank_type})")
                    extracted_name = self.config.extract_name_from_transfer_pattern(pattern, original_description) # Pass original_description
                    if extracted_name is not None:
                        candidates.append({
                            **transaction,
                            '_transfer_pattern': pattern,
                            '_is_transfer_candidate': True,
                            '_transfer_direction': 'incoming'
                        })
                        print(f"DEBUG CBM find_candidates:   -> ADDED INCOMING Candidate: Desc='{original_description[:60]}...', Name='{extracted_name}', Amt='{transaction.get('Amount')}', Bank='{bank_type}', CSV='{transaction.get('_csv_name')}'")
                        break # Found an incoming pattern
                    else:
                        print(f"DEBUG CBM find_candidates:     -> No incoming name extracted with pattern '{pattern}' for desc '{original_description[:60]}...'")
        
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
        
        print(f" MATCHING CROSS-BANK TRANSFERS...")
        
        # Filter available transactions
        available_outgoing = [t for t in potential_transfers 
                            if t['_transaction_index'] not in existing_transaction_ids and 
                               AmountParser.parse_amount(t.get('Amount', '0')) < 0]
        
        print(f"DEBUG CBM match_cross_bank_transfers: Total {len(available_outgoing)} available_outgoing transactions to process.")
        # for idx, ao_txn in enumerate(available_outgoing):
        #     print(f"DEBUG CBM match_cross_bank_transfers: Available Outgoing {idx}: Desc='{self._get_description(ao_txn)[:60]}...', Amt='{ao_txn.get('Amount')}', Bank='{ao_txn.get('_bank_type')}', CSV='{ao_txn.get('_csv_name')}'")

        print(f"DEBUG CBM match_cross_bank_transfers: Initial outgoing transaction processing order (first 5):")
        for i, tx in enumerate(available_outgoing[:5]):
            print(f"DEBUG CBM match_cross_bank_transfers:  {i+1}. {self._get_description(tx)[:50]}..., Amt={tx.get('Amount')}, Date={tx.get('Date')}, Bank={tx.get('_bank_type')}")
        print("DEBUG CBM match_cross_bank_transfers: ... (rest of outgoing transactions)")

        available_incoming = [t for t in all_transactions 
                            if t['_transaction_index'] not in existing_transaction_ids and 
                               AmountParser.parse_amount(t.get('Amount', '0')) > 0]

        # Match each outgoing transaction
        for outgoing in available_outgoing:
            if outgoing['_transaction_index'] in existing_transaction_ids:
                continue
                
            print(f"\nDEBUG CBM match_cross_bank_transfers: --- Processing OUTGOING: Desc='{self._get_description(outgoing)[:60]}...', Amt={outgoing.get('Amount')}, Date='{outgoing.get('Date')}', Bank='{outgoing.get('_bank_type')}', CSV='{outgoing.get('_csv_name')}'")
            # Debugging info: Show the contents of existing_transaction_ids
            print(f"DEBUG CBM match_cross_bank_transfers:   Current existing_transaction_ids: {sorted(list(existing_transaction_ids))}")
            
            
            best_match = self._find_best_match(outgoing, available_incoming, existing_transaction_ids)
            
            if best_match and best_match['confidence'] >= self.confidence_threshold:
                transfer_pair = self._create_transfer_pair(outgoing, best_match, len(transfer_pairs))
                
                print(f" PAIR: {outgoing['_csv_name']} | -{transfer_pair['amount']} → "
                      f"{best_match['incoming']['_csv_name']} | {best_match['incoming_amount']} "
                      f"({best_match['type']}, {best_match['confidence']:.2f})")
                
                transfer_pairs.append(transfer_pair)
                existing_transaction_ids.add(outgoing['_transaction_index'])
                existing_transaction_ids.add(best_match['incoming']['_transaction_index'])
        
        print(f"[SUCCESS] Created {len(transfer_pairs)} cross-bank transfer pairs")
        print(f"[INFO] Found {len(self.potential_pairs)} potential pairs (failed name matching)")
        return transfer_pairs
    
    def _find_best_match(self, outgoing: Dict, available_incoming: List[Dict], 
                        existing_transaction_ids: Set[int]) -> Optional[Dict]: # Return type can be None
        """Find the best matching incoming transaction using configuration"""
        print(f"\nDEBUG CBM _find_best_match: >>> Attempting to match OUTGOING: "
              f"Desc='{self._get_description(outgoing)[:60]}...', Amt={outgoing.get('Amount')}, Date='{outgoing.get('Date')}', "
              f"Bank='{outgoing.get('_bank_type')}', CSV='{outgoing.get('_csv_name')}'")

        outgoing_amount = abs(AmountParser.parse_amount(outgoing.get('Amount', '0')))
        exchange_amount = self.exchange_analyzer.get_exchange_to_amount(outgoing)
        exchange_currency = self.exchange_analyzer.get_exchange_to_currency(outgoing)

        # === Logging as per request ===
        print(f"\nDEBUG CBM _find_best_match: === EVALUATING INCOMING CANDIDATES ===")
        print(f"DEBUG CBM _find_best_match: Outgoing: Desc='{self._get_description(outgoing)[:60]}...', Amt={outgoing.get('Amount')}, Date='{self._get_date_string(outgoing)}', ExchAmt={exchange_amount}, ExchCurr={exchange_currency}")

        if not available_incoming:
            # === Logging as per request ===
            print("DEBUG CBM _find_best_match: CAUTION: available_incoming candidates list is EMPTY - filtering issue detected!")
            return None # Explicitly return None if no candidates

        print(f"DEBUG CBM _find_best_match:   Outgoing details - Amount: {outgoing_amount}, ExchAmt: {exchange_amount}, ExchCurr: {exchange_currency}")
        print(f"DEBUG CBM _find_best_match:   Number of available_incoming candidates: {len(available_incoming)}")
        
        best_match = None
        best_confidence = 0.0
        
        # Corrected loop with enumerate and proper indentation for the body
        for incoming_idx, incoming in enumerate(available_incoming):
            # === Logging as per request: Candidate details ===
            print(f"\nDEBUG CBM _find_best_match: Candidate {incoming_idx + 1}:")
            # Safely get bank_type and then bank_config to avoid errors if bank_type is None
            bank_type_for_currency = incoming.get('_bank_type')
            default_currency = "N/A"
            if bank_type_for_currency:
                bank_config_for_currency = self.config.get_bank_config(bank_type_for_currency)
                if bank_config_for_currency:
                    default_currency = bank_config_for_currency.currency_primary
            
            incoming_desc_full = self._get_description(incoming)
            incoming_amt_val = AmountParser.parse_amount(incoming.get('Amount', '0'))
            incoming_date_str_val = self._get_date_string(incoming)
            incoming_curr_val = incoming.get('Currency', default_currency)
            incoming_csv_val = incoming.get('_csv_name')

            print(f"  - Description: {incoming_desc_full}")
            print(f"  - Amount: {incoming_amt_val}")
            print(f"  - Date: {incoming_date_str_val}")
            print(f"  - Currency: {incoming_curr_val}")
            print(f"  - CSV: {incoming_csv_val}")

            # Check if already used or same CSV
            if (incoming['_transaction_index'] in existing_transaction_ids or
                incoming['_csv_index'] == outgoing['_csv_index']):  # Must be different CSV
                # === Logging as per request: Rejection reason ===
                print(f"  - Reason for rejection: Already used or same CSV file.")
                continue
            
            incoming_amount = AmountParser.parse_amount(incoming.get('Amount', '0'))
            
            # Check date tolerance first
            # === Logging as per request: Date tolerance check ===
            outgoing_date_obj = DateParser.parse_date(self._get_date_string(outgoing))
            incoming_date_obj = DateParser.parse_date(self._get_date_string(incoming))
            hours_diff = abs((outgoing_date_obj - incoming_date_obj).total_seconds() / 3600) if outgoing_date_obj and incoming_date_obj else float('inf')
            date_check_passed = self._check_date_tolerance(outgoing, incoming) # Uses internal parsing
            
            print(f"DEBUG CBM: Date tolerance check:")
            print(f"  - Outgoing date: {self._get_date_string(outgoing)}") # Already logged as part of Outgoing details
            print(f"  - Incoming date: {incoming_date_str_val}") # Use already fetched value
            print(f"  - Difference in hours: {hours_diff:.2f}")
            print(f"  - Date tolerance setting: {self.date_tolerance_hours} hours")
            print(f"  - Result: {'PASS' if date_check_passed else 'FAIL'}")

            if not date_check_passed:
                # === Logging as per request: Rejection reason ===
                print(f"  - Reason for rejection: Date mismatch (Diff: {hours_diff:.2f}h, Tolerance: {self.date_tolerance_hours}h)")
                continue

            # Check if this could be a cross-bank transfer using config
            # === Logging as per request: Cross-bank transfer validation (done inside _is_cross_bank_transfer) ===
            is_transfer_check_result, details = self._is_cross_bank_transfer(outgoing, incoming, debug=True)
            if not is_transfer_check_result:
                # === Logging as per request: Rejection reason ===
                # _is_cross_bank_transfer logs its own details when debug=True
                print(f"  - Reason for rejection: _is_cross_bank_transfer failed (Details logged above by _is_cross_bank_transfer)")
                
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
                        print(f"  - CAPTURED POTENTIAL PAIR: Names don't match ('{details.get('outgoing_name')}' vs '{details.get('incoming_name')}') but amount/date do")
                    else:
                        print(f"  - NOT capturing potential pair: Names don't match AND amounts don't match")
                
                continue
            
            matches = self._evaluate_matching_strategies(
                outgoing, incoming, outgoing_amount, incoming_amount, 
                exchange_amount, exchange_currency
            )
            
            # Choose best match for this incoming transaction
            if matches:
                best_incoming_match = max(matches, key=lambda x: x['confidence'])
                
                if best_incoming_match['confidence'] > best_confidence:
                    print(f"DEBUG CBM:         ==> NEW BEST for this OUTGOING: IN='{self._get_description(incoming)[:40]}...' with conf {best_incoming_match['confidence']:.2f} (Strategy: {best_incoming_match.get('type')})")
                    best_confidence = best_incoming_match['confidence']
                    best_match = {
                        'incoming': incoming,
                        'incoming_amount': incoming_amount,
                        **best_incoming_match
                    }
                # No specific log if not better, to reduce noise
            else:
                print(f"DEBUG CBM:         No matching strategies found for this IN candidate.")
        
        if not best_match:
            print(f"DEBUG CBM _find_best_match: <<< No suitable match ultimately found for OUTGOING: '{self._get_description(outgoing)[:60]}...'")
        else:
            print(f"DEBUG CBM _find_best_match: <<< FINAL BEST MATCH for OUT: '{self._get_description(outgoing)[:60]}...' is IN: '{self._get_description(best_match['incoming'])[:60]}...' with conf {best_match['confidence']:.2f}")
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
        
        if debug:
            print(f"DEBUG CBM _is_cross_bank_transfer: OutBank='{outgoing_bank}', OutDesc='{outgoing_desc[:50]}...', InBank='{incoming_bank}', InDesc='{incoming_desc[:50]}...'")
            # Requested format for name extraction logging
            print(f"DEBUG CBM _is_cross_bank_transfer: Name extraction and matching:")

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
        if debug: # Log extracted name as per request
            print(f"  - Outgoing name extracted: '{outgoing_name}' (using patterns: {outgoing_patterns})")
        
        # Extract names from incoming transaction  
        incoming_name = None
        for pattern in incoming_patterns:
            extracted_name = self.config.extract_name_from_transfer_pattern(pattern, incoming_desc)
            if extracted_name:
                incoming_name = extracted_name
                break
        if debug: # Log extracted name as per request
            print(f"  - Incoming name extracted: '{incoming_name}' (using patterns: {incoming_patterns})")
        
        # If we found names in both transactions, check if they could match
        if outgoing_name and incoming_name:
            # Names should be similar (same person transferring)
            names_match_res = self._names_match(outgoing_name, incoming_name)
            if debug:
                print(f"  - Name match result: {str(names_match_res).upper()}") # Requested format
            return names_match_res, {"outgoing_name": outgoing_name, "incoming_name": incoming_name, "names_match_result": names_match_res}
        
        # Fallback to simple pattern matching if name extraction fails
        outgoing_matches = any(self._pattern_matches(pattern, outgoing_desc) for pattern in outgoing_patterns)
        incoming_matches = any(self._pattern_matches(pattern, incoming_desc) for pattern in incoming_patterns)
        
        if debug:
            print(f"  - Fallback pattern match: Out={outgoing_matches}, In={incoming_matches}, Result: {str(outgoing_matches and incoming_matches).upper()}")
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
        
        name1_clean = name1.lower().strip()
        name2_clean = name2.lower().strip()
        
        # Exact match
        if name1_clean == name2_clean:
            return True
        
        # Check if one name is contained in the other (e.g., "John" vs "John Smith")
        if name1_clean in name2_clean or name2_clean in name1_clean:
            return True
        
        # Check for similar names with different formatting
        name1_parts = set(name1_clean.split())
        name2_parts = set(name2_clean.split())
        
        # If they share at least one common word, consider it a match
        if name1_parts.intersection(name2_parts):
            return True
        
        return False
    
    def detect_bank_type(self, file_name: str, transaction: Dict) -> str:
        """Detect bank type using configuration"""
        bank_type = self.config.detect_bank_type(file_name)
        if not bank_type:
            print(f"[WARNING]  Unknown bank type for file: {file_name}. Add configuration in configs/")
            return 'unknown'
        return bank_type
    
    def categorize_transaction(self, transaction: Dict) -> str:
        """Categorize transaction using bank-specific rules"""
        bank_type = transaction.get('_bank_type', '')
        description = self._get_description(transaction)
        
        category = self.config.categorize_merchant(bank_type, description)
        return category or 'Other'
    
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

        print(f"DEBUG CBM _eval_strat: Outgoing: {outgoing_amount_orig_curr} {outgoing_currency}, Incoming: {incoming_amount_orig_curr} {incoming_currency}, Exchange: {exchange_amount} {exchange_currency}")

        # Strategy 1: Exchange To Amount matching (PRIORITY for Wise-like transactions)
        if exchange_amount is not None and exchange_currency: # exchange_amount can be 0.0
            print(f"\nDEBUG CBM _eval_strat: === STRATEGY 1 (Exchange Amount) EVALUATION ===") # Requested header
            print(f"DEBUG CBM _eval_strat: Outgoing ExchangeToCurrency: '{exchange_currency}'")
            print(f"DEBUG CBM _eval_strat: Incoming Currency: '{incoming_currency}'")

            currency_match_check = (exchange_currency == incoming_currency)
            print(f"DEBUG CBM _eval_strat: Currency match result: {'PASS' if currency_match_check else 'FAIL'}")

            if currency_match_check:
                # Only check amount if currency matches
                amount_match_check = AmountParser.amounts_match(exchange_amount, incoming_amount_orig_curr)
                # Calculate difference directly as AmountParser.calculate_difference does not exist
                amount_diff = abs(exchange_amount - incoming_amount_orig_curr)
                
                print(f"DEBUG CBM _eval_strat: Outgoing ExchangeToAmount: {exchange_amount}")
                print(f"DEBUG CBM _eval_strat: Incoming Amount: {incoming_amount_orig_curr}")
                print(f"DEBUG CBM _eval_strat: Amount match result: {'PASS' if amount_match_check else 'FAIL'}")
                print(f"DEBUG CBM _eval_strat: Amount difference: {amount_diff:.2f}")

                if amount_match_check:
                    confidence = self.confidence_calculator.calculate_confidence(
                        outgoing, incoming, is_cross_bank=True, is_exchange_match=True
                    )
                    print(f"DEBUG CBM _eval_strat: Strategy 1 final result: PASS with confidence: {confidence:.2f}")
                    matches.append({
                        'type': 'exchange_amount',
                        'confidence': confidence,
                        'matched_amount': exchange_amount, # This is the amount in the target currency
                        'match_details': f"Exchange {exchange_amount} {exchange_currency}"
                    })
                    # Old log, replaced by "Strategy 1 final result..."
                    # print(f"DEBUG CBM _eval_strat: Strategy 1 (Exchange): MATCHED. Amount: {exchange_amount}, Currency: {exchange_currency}. Conf: {confidence:.2f}")
                else:
                    print(f"DEBUG CBM _eval_strat: Strategy 1 final result: FAIL (Amount mismatch)")
                    # Old log, replaced by "Strategy 1 final result..."
                    # print(f"DEBUG CBM _eval_strat: Strategy 1 (Exchange): REJECTED - Amounts do not match ({exchange_amount} vs {incoming_amount_orig_curr})")
            else:
                print(f"DEBUG CBM _eval_strat: Strategy 1 final result: FAIL (Currency mismatch)")
                # This path is taken if currencies do not match. The reason is already logged by the currency comparison print.
                pass
        else: # exchange_amount or exchange_currency is None/empty
            print(f"DEBUG CBM _eval_strat: Strategy 1 (Exchange Amount) SKIPPED - Missing exchange_amount ({exchange_amount}) or exchange_currency ({exchange_currency}) on outgoing tx.")

        # Strategy 2: Traditional amount matching (with currency conversion if needed)
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
                print(f"DEBUG CBM _eval_strat: Strategy 2 (Traditional Same Currency) MATCHED. Conf: {confidence:.2f}")
        else: # Different currencies, try to use ExchangeAnalyzer for potential conversion info
            print(f"DEBUG CBM _eval_strat: Strategy 2 (Traditional) - Currencies differ ({outgoing_currency} vs {incoming_currency}). Checking ExchangeAnalyzer.")
            
            # Check if the outgoing transaction has enough info to imply the incoming amount in its currency
            # This is where "Sent money to X, which was YYY PKR" would be useful if ExchangeAnalyzer could get YYY PKR.
            # For now, ExchangeAnalyzer primarily looks for "Exchange To Amount" and "Exchange To Currency" columns.
            # If the outgoing Wise transaction for "Sent money to USER" has "Exchange To Amount" (e.g., 50000)
            # and "Exchange To Currency" (e.g., PKR), then `exchange_amount` and `exchange_currency` would be set.
            # This case is already handled by Strategy 1.
            
            # If Strategy 1 didn't match (e.g., exchange_currency was not PKR, or exchange_amount was None),
            # we don't have a direct converted amount from the outgoing transaction's row to match the incoming.
            # Without an external currency conversion API or more detailed parsing from description for *this specific scenario*,
            # we cannot reliably match amounts across different currencies here.
            
            # The placeholder `self.currency_converter.convert_amount_for_matching` was removed as per user's request
            # to not rely on external APIs or historical data for this step.
            # The matching must rely on data present in the CSVs themselves (like "Exchange To Amount").

            # If we reach here, it means:
            # 1. Strategy 1 (direct exchange_amount match) failed.
            # 2. Currencies are different.
            # 3. We are not using an external API for conversion.
            # Therefore, we cannot match based on amount for this strategy if currencies differ
            # unless the `exchange_amount` and `exchange_currency` from the outgoing transaction
            # (used in Strategy 1) perfectly matched the incoming transaction's currency and amount.
            print(f"DEBUG CBM _eval_strat:   Strategy 2 (Traditional Different Currency) - Cannot match amounts without explicit conversion data in CSV or external API.")

        # Strategy 3: Flexible amount matching (Original fallback, if no other matches)
        # This was the original "Strategy 3: Flexible amount matching for currency conversion"
        # It's kept as a last resort but might be too loose.
        if not matches: # Only if no other strategies matched
            amount_diff_percentage = AmountParser.calculate_percentage_difference(outgoing_amount_orig_curr, incoming_amount_orig_curr)
            if amount_diff_percentage < 1.0: # Allows large difference, assuming it's due to currency
                confidence = self.confidence_calculator.calculate_confidence(outgoing, incoming, is_cross_bank=True) - 0.15 # Higher penalty
                matches.append({
                    'type': 'flexible_currency_fallback',
                    'confidence': max(0, confidence), # Ensure confidence is not negative
                    'matched_amount': incoming_amount_orig_curr,
                    'match_details': f"Flexible Fallback (diff: {amount_diff_percentage*100:.1f}%) {outgoing_amount_orig_curr} {outgoing_currency} vs {incoming_amount_orig_curr} {incoming_currency}"
                })
                print(f"DEBUG CBM _eval_strat: Strategy 3 (Flexible Fallback) considered. Conf: {confidence:.2f}")
        
        if not matches:
            print(f"DEBUG CBM _eval_strat: No matching strategies found for this pair.")
        return matches
    
    def _create_transfer_pair(self, outgoing: Dict, best_match: Dict, pair_index: int) -> Dict:
        """Create a transfer pair from matched transactions"""
        outgoing_amount = abs(AmountParser.parse_amount(outgoing.get('Amount', '0')))
        incoming_amount = AmountParser.parse_amount(best_match['incoming'].get('Amount', '0'))
        
        # Set exchange_amount based on strategy
        if best_match['type'] == 'exchange_amount':
            exchange_amount = self.exchange_analyzer.get_exchange_to_amount(outgoing)
        elif best_match['type'] == 'flexible_currency':
            exchange_amount = incoming_amount  # For currency conversion, the incoming amount is the exchange amount
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
    
    def _validate_amount_matching(self, outgoing: Dict, incoming: Dict,
                                outgoing_amount: float, incoming_amount: float,
                                exchange_amount: float, exchange_currency: str) -> bool:
        """Validate if amounts match using the same logic as _evaluate_matching_strategies"""
        
        outgoing_currency = outgoing.get('Currency', self.config.get_bank_config(outgoing.get('_bank_type')).currency_primary if outgoing.get('_bank_type') and self.config.get_bank_config(outgoing.get('_bank_type')) else None)
        incoming_currency = incoming.get('Currency', self.config.get_bank_config(incoming.get('_bank_type')).currency_primary if incoming.get('_bank_type') and self.config.get_bank_config(incoming.get('_bank_type')) else None)
        
        print(f"DEBUG CBM _validate_amount: Checking amounts - Outgoing: {outgoing_amount} {outgoing_currency}, Incoming: {incoming_amount} {incoming_currency}, Exchange: {exchange_amount} {exchange_currency}")
        
        # Strategy 1: Exchange To Amount matching (PRIORITY for Wise-like transactions)
        if exchange_amount is not None and exchange_currency:
            if exchange_currency == incoming_currency:
                amount_match = AmountParser.amounts_match(exchange_amount, incoming_amount)
                print(f"DEBUG CBM _validate_amount: Strategy 1 (Exchange): {exchange_amount} vs {incoming_amount} = {'MATCH' if amount_match else 'NO MATCH'}")
                if amount_match:
                    return True
        
        # Strategy 2: Direct amount matching (same currency)
        if outgoing_currency == incoming_currency:
            amount_match = AmountParser.amounts_match(outgoing_amount, incoming_amount)
            print(f"DEBUG CBM _validate_amount: Strategy 2 (Direct): {outgoing_amount} vs {incoming_amount} = {'MATCH' if amount_match else 'NO MATCH'}")
            if amount_match:
                return True
        
        # Strategy 3: Cross-currency matching (would need currency conversion rates)
        # For now, we'll skip this as it requires external currency conversion data
        # This could be added later if needed
        
        print(f"DEBUG CBM _validate_amount: No amount matching strategy succeeded")
        return False

    def get_potential_pairs(self) -> List[Dict]:
        """Get the potential pairs that failed name matching but passed amount/date checks"""
        return getattr(self, 'potential_pairs', [])
