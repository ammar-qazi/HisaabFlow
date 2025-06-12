"""
Configuration-driven cross-bank transfer matching
"""
import re
from typing import Dict, List, Set
from .amount_parser import AmountParser
from .date_parser import DateParser
from .exchange_analyzer import ExchangeAnalyzer
from .confidence_calculator import ConfidenceCalculator
from .config_manager import ConfigurationManager


class CrossBankMatcher:
    """Handles cross-bank transfer detection using configuration-driven rules"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config = ConfigurationManager(config_dir)
        self.user_name = self.config.get_user_name()
        self.date_tolerance_hours = self.config.get_date_tolerance()
        self.confidence_threshold = self.config.get_confidence_threshold()
        
        self.exchange_analyzer = ExchangeAnalyzer()
        self.confidence_calculator = ConfidenceCalculator(self.user_name)
        
        print(f"🔧 CrossBankMatcher: {self.user_name}, Banks: {', '.join(self.config.list_configured_banks())}")
    
    def find_transfer_candidates(self, transactions: List[Dict]) -> List[Dict]:
        """Find transactions that match configured transfer patterns"""
        candidates = []
        
        for transaction in transactions:
            bank_type = transaction.get('_bank_type', 'unknown')
            description = self._get_description(transaction).lower()
            
            # Check outgoing patterns
            outgoing_patterns = self.config.get_transfer_patterns(bank_type, 'outgoing')
            for pattern in outgoing_patterns:
                if pattern.lower() in description:
                    candidates.append({
                        **transaction,
                        '_transfer_pattern': pattern,
                        '_is_transfer_candidate': True,
                        '_transfer_direction': 'outgoing'
                    })
                    break
            
            # Check incoming patterns if not already matched
            if not any(t['_transaction_index'] == transaction['_transaction_index'] for t in candidates):
                incoming_patterns = self.config.get_transfer_patterns(bank_type, 'incoming')
                for pattern in incoming_patterns:
                    if pattern.lower() in description:
                        candidates.append({
                            **transaction,
                            '_transfer_pattern': pattern,
                            '_is_transfer_candidate': True,
                            '_transfer_direction': 'incoming'
                        })
                        break
        
        return candidates
    
    def match_cross_bank_transfers(self, potential_transfers: List[Dict], 
                                 all_transactions: List[Dict], 
                                 existing_pairs: List[Dict]) -> List[Dict]:
        """Match cross-bank transfers using configuration-driven rules"""
        transfer_pairs = []
        existing_transaction_ids: Set[int] = set()
        
        # Get IDs of already matched transactions
        for pair in existing_pairs:
            existing_transaction_ids.add(pair['outgoing']['_transaction_index'])
            existing_transaction_ids.add(pair['incoming']['_transaction_index'])
        
        print(f"🔄 MATCHING CROSS-BANK TRANSFERS...")
        
        # Filter available transactions
        available_outgoing = [t for t in potential_transfers 
                            if t['_transaction_index'] not in existing_transaction_ids and 
                               AmountParser.parse_amount(t.get('Amount', '0')) < 0]
        
        available_incoming = [t for t in all_transactions 
                            if t['_transaction_index'] not in existing_transaction_ids and 
                               AmountParser.parse_amount(t.get('Amount', '0')) > 0]
        
        # Match each outgoing transaction
        for outgoing in available_outgoing:
            if outgoing['_transaction_index'] in existing_transaction_ids:
                continue
                
            best_match = self._find_best_match(outgoing, available_incoming, existing_transaction_ids)
            
            if best_match and best_match['confidence'] >= self.confidence_threshold:
                transfer_pair = self._create_transfer_pair(outgoing, best_match, len(transfer_pairs))
                
                print(f"🎉 PAIR: {outgoing['_csv_name']} | -{transfer_pair['amount']} → "
                      f"{best_match['incoming']['_csv_name']} | {best_match['incoming_amount']} "
                      f"({best_match['type']}, {best_match['confidence']:.2f})")
                
                transfer_pairs.append(transfer_pair)
                existing_transaction_ids.add(outgoing['_transaction_index'])
                existing_transaction_ids.add(best_match['incoming']['_transaction_index'])
        
        print(f"✅ Created {len(transfer_pairs)} cross-bank transfer pairs")
        return transfer_pairs
    
    def _find_best_match(self, outgoing: Dict, available_incoming: List[Dict], 
                        existing_transaction_ids: Set[int]) -> Dict:
        """Find the best matching incoming transaction using configuration"""
        outgoing_amount = abs(AmountParser.parse_amount(outgoing.get('Amount', '0')))
        exchange_amount = self.exchange_analyzer.get_exchange_to_amount(outgoing)
        exchange_currency = self.exchange_analyzer.get_exchange_to_currency(outgoing)
        
        best_match = None
        best_confidence = 0.0
        
        for incoming in available_incoming:
            if (incoming['_transaction_index'] in existing_transaction_ids or
                incoming['_csv_index'] == outgoing['_csv_index']):  # Must be different CSV
                continue
            
            incoming_amount = AmountParser.parse_amount(incoming.get('Amount', '0'))
            
            # Check date tolerance first
            if not self._check_date_tolerance(outgoing, incoming):
                continue

            # Check if this could be a cross-bank transfer using config
            if not self._is_cross_bank_transfer(outgoing, incoming):
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
        
        return best_match
    
    def _is_cross_bank_transfer(self, outgoing: Dict, incoming: Dict) -> bool:
        """Check if transactions form a cross-bank transfer using configuration"""
        outgoing_bank = outgoing.get('_bank_type', '')
        incoming_bank = incoming.get('_bank_type', '')
        
        # Must be different banks
        if outgoing_bank == incoming_bank:
            return False

        outgoing_desc = self._get_description(outgoing).lower()
        incoming_desc = self._get_description(incoming).lower()
        
        # Check configured patterns
        outgoing_patterns = self.config.get_transfer_patterns(outgoing_bank, 'outgoing')
        incoming_patterns = self.config.get_transfer_patterns(incoming_bank, 'incoming')
        
        outgoing_matches = any(pattern.lower() in outgoing_desc for pattern in outgoing_patterns)
        incoming_matches = any(pattern.lower() in incoming_desc for pattern in incoming_patterns)
        
        return outgoing_matches and incoming_matches
    
    def detect_bank_type(self, file_name: str, transaction: Dict) -> str:
        """Detect bank type using configuration"""
        bank_type = self.config.detect_bank_type(file_name)
        if not bank_type:
            print(f"⚠️  Unknown bank type for file: {file_name}. Add configuration in configs/")
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
        """Evaluate all matching strategies and return matches"""
        matches = []

        # Strategy 1: Exchange To Amount matching (PRIORITY)
        if exchange_amount and exchange_currency:
            if self.exchange_analyzer.currency_matches_bank(exchange_currency, incoming):
                if AmountParser.amounts_match(exchange_amount, incoming_amount):
                    confidence = self.confidence_calculator.calculate_confidence(
                        outgoing, incoming, is_cross_bank=True, is_exchange_match=True
                    )
                    matches.append({
                        'type': 'exchange_amount',
                        'confidence': confidence,
                        'matched_amount': exchange_amount,
                        'match_details': f"Exchange {exchange_amount} {exchange_currency}"
                    })
        
        # Strategy 2: Traditional amount matching (FALLBACK)
        if AmountParser.amounts_match(outgoing_amount, incoming_amount):
            confidence = self.confidence_calculator.calculate_confidence(
                outgoing, incoming, is_cross_bank=True
            )
            matches.append({
                'type': 'traditional',
                'confidence': confidence,
                'matched_amount': outgoing_amount,
                'match_details': f"Traditional {outgoing_amount}"
            })
        
        # Strategy 3: Flexible amount matching for currency conversion
        if not matches:
            amount_diff_percentage = AmountParser.calculate_percentage_difference(
                outgoing_amount, incoming_amount
            )
            
            if amount_diff_percentage < 1.0:  # Allow up to 100% difference for currency conversion
                confidence = self.confidence_calculator.calculate_confidence(
                    outgoing, incoming, is_cross_bank=True
                ) - 0.1  # Slightly lower confidence
                min_confidence = max(confidence, 0.7)  # Higher minimum confidence
                matches.append({
                    'type': 'flexible_currency',
                    'confidence': min_confidence,
                    'matched_amount': incoming_amount,
                    'match_details': f"Currency conversion {outgoing_amount} → {incoming_amount}"
                })
        
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
            transaction.get('Description', '') or 
            transaction.get('Title', '') or 
            transaction.get('Note', '') or 
            transaction.get('DESCRIPTION', '') or 
            transaction.get('TYPE', '')
        )
