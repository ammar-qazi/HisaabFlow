from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import re

# Import the existing improved transfer detector as our base
from transfer_detector_improved import ImprovedTransferDetector

class EnhancedUniversalTransferDetector(ImprovedTransferDetector):
    """
    Enhanced Universal Transfer Detection System
    
    EXTENDS ImprovedTransferDetector with:
    - Enhanced exchange amount detection from multiple column patterns
    - Multiple matching strategies with smart prioritization
    - Achieves 1.00 confidence for EUR->PKR Wise->NayaPay scenarios
    - Verbose debugging for development and testing
    - 100% backward compatibility (extends existing class)
    
    NEW ENHANCEMENTS:
    1. Exchange Amount Extractor - detects various column name patterns
    2. Multiple Matching Strategies - traditional + exchange amount + hybrid
    3. Smart Prioritization System - prevents false matches
    4. Verbose Debug Logging - track exactly what's happening
    """
    
    def __init__(self, user_name: str = "Ammar Qazi", date_tolerance_hours: int = 24, debug: bool = True):
        # Initialize parent class (maintains backward compatibility)
        super().__init__(user_name, date_tolerance_hours)
        
        self.debug = debug
        
        # ENHANCED: Multiple exchange amount column patterns
        self.exchange_amount_columns = [
            # Direct column names (most common)
            'Exchange To Amount',
            'Exchange Amount', 
            'Converted Amount',
            'Target Amount',
            'Destination Amount',
            
            # Case variations
            'exchange_to_amount',
            'exchange_amount',
            'converted_amount', 
            'target_amount',
            'destination_amount',
            
            # Alternative naming patterns  
            'ExchangeToAmount',
            'ExchangeAmount',
            'ConvertedAmount',
            'TargetAmount',
            'DestinationAmount',
            
            # Banking specific patterns
            'Exchange Rate Amount',
            'Converted Value',
            'Target Currency Amount',
            'Destination Currency Value'
        ]
        
        # Enhanced configuration
        self.enhanced_config = {
            'enable_exchange_matching': True,
            'confidence_thresholds': {
                'exchange_exact': 1.00,        # Perfect exchange amount match
                'exchange_approximate': 0.95,  # Close exchange amount match
                'traditional': 0.80,           # Traditional amount matching  
                'person_transfer': 0.85,       # Person-to-person transfers
                'description_only': 0.30       # Description pattern only
            },
            'debug_verbose': debug
        }
    
    def detect_transfers(self, csv_data_list: List[Dict]) -> Dict[str, Any]:
        """
        ENHANCED DETECTION with verbose debugging
        
        Extends the parent detect_transfers method with:
        1. Exchange amount detection (HIGHEST PRIORITY)
        2. Enhanced cross-bank transfer detection 
        3. Verbose debugging output
        4. Maintains backward compatibility
        """
        
        if self.debug:
            print("\\n🔍 STARTING ENHANCED UNIVERSAL TRANSFER DETECTION")
            print("=" * 70)
            print("🎯 TARGET: Wise EUR->PKR transfers via Exchange To Amount")
            print("🔧 EXTENDS: ImprovedTransferDetector with exchange amount matching")
            print("📊 COMPATIBILITY: 100% backward compatible")
            print("=" * 70)
        
        # PHASE 1: Prepare enhanced transactions with exchange amount detection
        all_transactions = self._prepare_enhanced_transactions(csv_data_list)
        
        if self.debug:
            exchange_count = sum(1 for t in all_transactions if t.get('_has_exchange_data'))
            print(f"\\n📊 ENHANCED TRANSACTION ANALYSIS:")
            print(f"   Total transactions: {len(all_transactions)}")
            print(f"   Transactions with exchange amounts: {exchange_count}")
        
        # PHASE 2: Enhanced Exchange Amount Matching (NEW - HIGHEST PRIORITY)
        if self.debug:
            print("\\n💱 PHASE 1: ENHANCED EXCHANGE AMOUNT MATCHING (Priority 1)...")
        
        exchange_pairs = self._match_exchange_amounts_enhanced(all_transactions)
        
        if self.debug:
            print(f"   ✅ Found {len(exchange_pairs)} exchange amount matches")
            
            # Show details of exchange matches
            for i, pair in enumerate(exchange_pairs):
                print(f"\\n   📌 EXCHANGE PAIR {i+1}: {pair['pair_id']}")
                print(f"      Strategy: {pair.get('match_strategy')}")
                print(f"      Confidence: {pair['confidence']:.2f}")
                print(f"      Exchange Amount: {pair.get('exchange_amount')}")
                print(f"      Matched Amount: {pair.get('matched_amount')}")
                print(f"      Amount Difference: {pair.get('amount_difference', 0):.2f}")
                print(f"      Cross-bank: {pair.get('is_cross_bank', False)}")
        
        # PHASE 3: Call parent class detection for remaining transactions
        if self.debug:
            print("\\n🔄 PHASE 2: RUNNING EXISTING DETECTION METHODS...")
        
        # Get already matched transaction IDs
        matched_transaction_ids = set()
        for pair in exchange_pairs:
            matched_transaction_ids.add(pair['outgoing']['_transaction_index'])
            matched_transaction_ids.add(pair['incoming']['_transaction_index'])
        
        # Filter out already matched transactions before calling parent
        remaining_csv_data = self._filter_matched_transactions(csv_data_list, matched_transaction_ids)
        
        # Call parent class detection on remaining transactions
        parent_results = super().detect_transfers(remaining_csv_data)
        
        # PHASE 4: Combine results with priority ordering
        if self.debug:
            print(f"\\n🔗 PHASE 3: COMBINING RESULTS...")
            print(f"   Exchange matches (priority 1): {len(exchange_pairs)}")
            print(f"   Traditional matches (priority 2): {len(parent_results['transfers'])}")
        
        # Combine transfer pairs (exchange pairs have higher priority)
        all_transfer_pairs = exchange_pairs + parent_results['transfers']
        
        # Update summary with enhanced information
        enhanced_summary = {
            **parent_results['summary'],
            'exchange_exact_matches': len(exchange_pairs),
            'traditional_matches': len(parent_results['transfers']),
            'total_enhanced_pairs': len(all_transfer_pairs),
            'target_scenario_achieved': any(
                p.get('match_strategy') == 'exchange_exact' and p.get('confidence', 0) >= 1.00 
                for p in exchange_pairs
            )
        }
        
        # Final results
        results = {
            'transfers': all_transfer_pairs,
            'potential_transfers': parent_results.get('potential_transfers', []),
            'conflicts': parent_results.get('conflicts', []),
            'flagged_transactions': parent_results.get('flagged_transactions', []),
            'summary': enhanced_summary
        }
        
        if self.debug:
            print("\\n📋 ENHANCED DETECTION SUMMARY:")
            print(f"   🎯 Total transfer pairs: {len(all_transfer_pairs)}")
            print(f"   💱 Exchange amount matches: {len(exchange_pairs)}")
            print(f"   🔄 Traditional matches: {len(parent_results['transfers'])}")
            print(f"   📊 Potential transfers: {len(parent_results.get('potential_transfers', []))}")
            
            # Check for target scenario success
            target_achieved = enhanced_summary['target_scenario_achieved']
            if target_achieved:
                print(f"   🎉 SUCCESS: Target EUR->PKR scenario achieved!")
            else:
                print(f"   📝 INFO: Target scenario not detected in this batch")
            
            print("=" * 70)
        
        return results
    
    def _prepare_enhanced_transactions(self, csv_data_list: List[Dict]) -> List[Dict]:
        """Prepare transactions with enhanced metadata including exchange amounts"""
        all_transactions = []
        
        for csv_idx, csv_data in enumerate(csv_data_list):
            if self.debug:
                print(f"\\n📁 Processing CSV {csv_idx}: {csv_data.get('file_name', f'CSV_{csv_idx}')}")
                print(f"   📊 Transaction count: {len(csv_data['data'])}")
            
            for trans_idx, transaction in enumerate(csv_data['data']):
                # Extract exchange amount using enhanced detection
                exchange_amount = self._extract_exchange_amount(transaction)
                exchange_currency = self._extract_exchange_currency(transaction)
                
                enhanced_transaction = {
                    **transaction,
                    '_csv_index': csv_idx,
                    '_transaction_index': trans_idx,
                    '_csv_name': csv_data.get('file_name', f'CSV_{csv_idx}'),
                    '_template_config': csv_data.get('template_config', {}),
                    '_bank_type': self._detect_bank_type(csv_data.get('file_name', ''), transaction),
                    '_exchange_amount': exchange_amount,
                    '_exchange_currency': exchange_currency,
                    '_has_exchange_data': exchange_amount is not None
                }
                all_transactions.append(enhanced_transaction)
                
                # Debug logging for sample transactions
                if self.debug and trans_idx < 2:
                    amount = self._parse_amount(transaction.get('Amount', '0'))
                    desc = str(transaction.get('Description', ''))[:60]
                    date = transaction.get('Date', '')
                    print(f"   🧾 Transaction {trans_idx}: Amount={amount}, Date={date}")
                    if exchange_amount:
                        print(f"      💱 Exchange Amount: {exchange_amount} {exchange_currency or ''}")
                        # Show which column was detected
                        detected_col = self._get_detected_exchange_column(transaction)
                        print(f"      🔍 Detected from column: '{detected_col}'")
                    else:
                        print(f"      💱 Exchange Amount: Not detected")
                    print(f"      📝 Description: {desc}...")
        
        return all_transactions
    
    def _extract_exchange_amount(self, transaction: Dict) -> Optional[float]:
        """ENHANCED: Extract exchange amount from various column patterns"""
        for col_pattern in self.exchange_amount_columns:
            # Try exact column name match (case sensitive)
            if col_pattern in transaction:
                value = transaction[col_pattern]
                if value and str(value).strip() not in ['', 'nan', 'NaN', 'null', 'None', '0', '0.0', '0.00']:
                    try:
                        parsed_amount = self._parse_amount(str(value))
                        if parsed_amount != 0:
                            return abs(parsed_amount)  # Always return positive for matching
                    except (ValueError, TypeError):
                        continue
            
            # Try case-insensitive match
            for actual_col in transaction.keys():
                if actual_col.lower() == col_pattern.lower():
                    value = transaction[actual_col]
                    if value and str(value).strip() not in ['', 'nan', 'NaN', 'null', 'None', '0', '0.0', '0.00']:
                        try:
                            parsed_amount = self._parse_amount(str(value))
                            if parsed_amount != 0:
                                return abs(parsed_amount)
                        except (ValueError, TypeError):
                            continue
        
        return None
    
    def _get_detected_exchange_column(self, transaction: Dict) -> Optional[str]:
        """Debug helper: Get which column was used for exchange amount detection"""
        for col_pattern in self.exchange_amount_columns:
            if col_pattern in transaction:
                value = transaction[col_pattern]
                if value and str(value).strip() not in ['', 'nan', 'NaN', 'null', 'None', '0', '0.0', '0.00']:
                    try:
                        parsed_amount = self._parse_amount(str(value))
                        if parsed_amount != 0:
                            return col_pattern
                    except (ValueError, TypeError):
                        continue
            
            for actual_col in transaction.keys():
                if actual_col.lower() == col_pattern.lower():
                    value = transaction[actual_col]
                    if value and str(value).strip() not in ['', 'nan', 'NaN', 'null', 'None', '0', '0.0', '0.00']:
                        try:
                            parsed_amount = self._parse_amount(str(value))
                            if parsed_amount != 0:
                                return actual_col
                        except (ValueError, TypeError):
                            continue
        return None
    
    def _extract_exchange_currency(self, transaction: Dict) -> Optional[str]:
        """Extract the target currency for exchange amounts"""
        currency_columns = [
            'Exchange To Currency', 'Exchange To', 'Target Currency', 
            'Destination Currency', 'Converted To Currency'
        ]
        
        for col_pattern in currency_columns:
            if col_pattern in transaction:
                currency = transaction[col_pattern]
                if currency and str(currency).strip():
                    return str(currency).strip().upper()
            
            for actual_col in transaction.keys():
                if actual_col.lower() == col_pattern.lower():
                    currency = transaction[actual_col]
                    if currency and str(currency).strip():
                        return str(currency).strip().upper()
        
        # Try to extract from main currency column if it looks like a conversion
        main_currency = transaction.get('Currency', '')
        if main_currency and 'to' in str(main_currency).lower():
            match = re.search(r'to\\s+(\\w{3})', str(main_currency), re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        return None
    
    def _match_exchange_amounts_enhanced(self, all_transactions: List[Dict]) -> List[Dict]:
        """
        ENHANCED: Match transfers using exact exchange amounts (HIGHEST PRIORITY)
        
        This is the key enhancement for the Wise EUR->PKR scenario:
        - Wise: -108.99 EUR with Exchange To Amount: 30,000 PKR
        - NayaPay: +30,000 PKR 
        - Should match with 1.00 confidence
        """
        exchange_pairs = []
        matched_transactions = set()
        
        if self.debug:
            print(f"   🔍 Scanning for transactions with exchange amounts...")
        
        # Find transactions with exchange amounts (potential outgoing transfers)
        exchange_candidates = [t for t in all_transactions if t['_has_exchange_data']]
        
        if self.debug:
            print(f"   📊 Found {len(exchange_candidates)} transactions with exchange amounts")
        
        for outgoing in exchange_candidates:
            if outgoing['_transaction_index'] in matched_transactions:
                continue
            
            outgoing_amount = self._parse_amount(outgoing.get('Amount', '0'))
            
            # Must be negative (outgoing)
            if outgoing_amount >= 0:
                continue
            
            exchange_amount = outgoing['_exchange_amount']
            if not exchange_amount:
                continue
            
            if self.debug:
                print(f"\\n   💸 EXCHANGE OUTGOING CANDIDATE:")
                print(f"      💰 Main Amount: {outgoing_amount}")
                print(f"      💱 Exchange Amount: {exchange_amount}")
                print(f"      📝 Description: {str(outgoing.get('Description', ''))[:60]}...")
                print(f"      🏦 Bank: {outgoing['_bank_type']}")
            
            # Look for matching incoming transfers in different CSVs
            for incoming in all_transactions:
                if (incoming['_transaction_index'] in matched_transactions or
                    incoming['_csv_index'] == outgoing['_csv_index']):
                    continue
                
                incoming_amount = self._parse_amount(incoming.get('Amount', '0'))
                
                # Must be positive (incoming)
                if incoming_amount <= 0:
                    continue
                
                # EXACT EXCHANGE AMOUNT MATCH
                amount_difference = abs(exchange_amount - incoming_amount)
                is_exact_match = amount_difference < 0.01  # Allow 1 cent tolerance
                
                if not is_exact_match:
                    continue
                
                # Date proximity check
                outgoing_date = self._parse_date(outgoing.get('Date', ''))
                incoming_date = self._parse_date(incoming.get('Date', ''))
                date_match = self._dates_within_tolerance(outgoing_date, incoming_date)
                
                if not date_match:
                    continue
                
                # Enhanced cross-bank detection
                is_cross_bank = self._is_cross_bank_transfer_enhanced(outgoing, incoming)
                
                # Calculate confidence (aiming for 1.00 for perfect matches)
                confidence = self._calculate_exchange_exact_confidence(
                    outgoing, incoming, exchange_amount, is_cross_bank
                )
                
                if self.debug:
                    print(f"\\n      ✅ EXACT EXCHANGE MATCH FOUND!")
                    print(f"         📥 Incoming: {incoming['_csv_name']} | {incoming_amount}")
                    print(f"         💱 Exchange match: {exchange_amount} ≈ {incoming_amount} (diff: {amount_difference:.2f})")
                    print(f"         📅 Date match: {date_match}")
                    print(f"         🏦 Cross-bank: {is_cross_bank}")
                    print(f"         🎯 Confidence: {confidence:.2f}")
                
                transfer_pair = {
                    'outgoing': outgoing,
                    'incoming': incoming,
                    'amount': abs(outgoing_amount),
                    'exchange_amount': exchange_amount,
                    'matched_amount': incoming_amount,
                    'amount_difference': amount_difference,
                    'date': outgoing_date,
                    'confidence': confidence,
                    'pair_id': f"exchange_exact_{len(exchange_pairs)}",
                    'transfer_type': 'cross_bank_exchange_exact',
                    'match_strategy': 'exchange_exact',
                    'is_cross_bank': is_cross_bank,
                    'exchange_currency': outgoing['_exchange_currency']
                }
                
                exchange_pairs.append(transfer_pair)
                matched_transactions.add(outgoing['_transaction_index'])
                matched_transactions.add(incoming['_transaction_index'])
                break  # Found exact match, no need to continue for this outgoing
        
        if self.debug:
            print(f"\\n   🎉 Exchange exact matching complete: {len(exchange_pairs)} pairs found")
        
        return exchange_pairs
    
    def _is_cross_bank_transfer_enhanced(self, outgoing: Dict, incoming: Dict) -> bool:
        """Enhanced cross-bank transfer detection"""
        # Use parent class method as base
        is_cross_bank_basic = super()._is_cross_bank_transfer(outgoing, incoming)
        
        if is_cross_bank_basic:
            return True
        
        # Enhanced detection for exchange amount scenarios
        outgoing_desc = str(outgoing.get('Description', '')).lower()
        incoming_desc = str(incoming.get('Description', '')).lower()
        user_name_lower = self.user_name.lower()
        
        # Enhanced: Wise->NayaPay pattern (primary target)
        if (outgoing.get('_bank_type') == 'wise' and 
            incoming.get('_bank_type') in ['nayapay', 'bank_alfalah']):
            
            # Check for user name in descriptions
            if user_name_lower in outgoing_desc and user_name_lower in incoming_desc:
                return True
            
            # Check for transfer patterns with exchange amounts
            if (outgoing.get('_has_exchange_data') and 
                ('sent money' in outgoing_desc or 'transfer' in outgoing_desc)):
                if ('incoming fund transfer' in incoming_desc or 'ibft' in incoming_desc):
                    return True
        
        # Enhanced: Different CSV sources with exchange amounts
        if (outgoing['_csv_index'] != incoming['_csv_index'] and 
            outgoing.get('_has_exchange_data')):
            outgoing_bank = outgoing.get('_bank_type', 'unknown')
            incoming_bank = incoming.get('_bank_type', 'unknown')
            if outgoing_bank != incoming_bank and outgoing_bank != 'unknown' and incoming_bank != 'unknown':
                return True
        
        return False
    
    def _calculate_exchange_exact_confidence(self, outgoing: Dict, incoming: Dict, 
                                           exchange_amount: float, is_cross_bank: bool) -> float:
        """Calculate confidence for exact exchange amount matches"""
        confidence = 0.6  # Base confidence for exchange matches
        
        # Perfect amount match bonus
        incoming_amount = self._parse_amount(incoming.get('Amount', '0'))
        if abs(exchange_amount - incoming_amount) < 0.01:
            confidence += 0.3  # Major bonus for exact match
        
        # Cross-bank transfer bonus (Wise->NayaPay is common pattern)
        if is_cross_bank:
            confidence += 0.2
        
        # Same day bonus
        outgoing_date = self._parse_date(outgoing.get('Date', ''))
        incoming_date = self._parse_date(incoming.get('Date', ''))
        if outgoing_date.date() == incoming_date.date():
            confidence += 0.1
        
        # User name matching bonus
        outgoing_desc = str(outgoing.get('Description', '')).lower()
        incoming_desc = str(incoming.get('Description', '')).lower()
        user_name_lower = self.user_name.lower()
        
        if (user_name_lower in outgoing_desc and user_name_lower in incoming_desc):
            confidence += 0.1
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def _filter_matched_transactions(self, csv_data_list: List[Dict], matched_transaction_ids: set) -> List[Dict]:
        """Filter out already matched transactions for parent class processing"""
        filtered_csv_data = []
        
        for csv_data in csv_data_list:
            filtered_data = []
            for trans_idx, transaction in enumerate(csv_data['data']):
                # Create a temporary transaction with index for checking
                temp_trans = {**transaction, '_transaction_index': trans_idx}
                if trans_idx not in matched_transaction_ids:
                    filtered_data.append(transaction)
            
            filtered_csv_data.append({
                **csv_data,
                'data': filtered_data
            })
        
        return filtered_csv_data
    
    # Enhanced apply_transfer_categorization with exchange amount info
    def apply_transfer_categorization(self, csv_data_list: List[Dict], transfer_pairs: List[Dict]) -> List[Dict]:
        """
        Apply Balance Correction category to detected transfers
        ENHANCED: Include exchange amount information and match strategy details
        """
        transfer_matches = []
        
        for pair in transfer_pairs:
            outgoing = pair['outgoing']
            incoming = pair['incoming']
            
            # Enhanced note with strategy and exchange amount info
            strategy = pair.get('match_strategy', 'unknown')
            exchange_note = ""
            if pair.get('exchange_amount'):
                exchange_note = f" | Exchange: {pair['exchange_amount']}"
            
            confidence_note = f" | Confidence: {pair['confidence']:.2f}"
            
            transfer_matches.append({
                'csv_index': outgoing['_csv_index'],
                'amount': str(self._parse_amount(outgoing.get('Amount', '0'))),
                'date': self._parse_date(outgoing.get('Date', '')).strftime('%Y-%m-%d'),
                'description': str(outgoing.get('Description', '')),
                'category': 'Balance Correction',
                'note': f"Transfer out - {pair['transfer_type']} - Strategy: {strategy} - Pair: {pair['pair_id']}{exchange_note}{confidence_note}",
                'pair_id': pair['pair_id'],
                'transfer_type': 'outgoing',
                'match_strategy': strategy,
                'confidence': pair['confidence']
            })
            
            transfer_matches.append({
                'csv_index': incoming['_csv_index'],
                'amount': str(self._parse_amount(incoming.get('Amount', '0'))),
                'date': self._parse_date(incoming.get('Date', '')).strftime('%Y-%m-%d'),
                'description': str(incoming.get('Description', '')),
                'category': 'Balance Correction',
                'note': f"Transfer in - {pair['transfer_type']} - Strategy: {strategy} - Pair: {pair['pair_id']}{exchange_note}{confidence_note}",
                'pair_id': pair['pair_id'],
                'transfer_type': 'incoming',
                'match_strategy': strategy,
                'confidence': pair['confidence']
            })
        
        return transfer_matches
