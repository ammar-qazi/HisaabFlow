"""
Cross-bank transfer matching with Ammar's specifications
"""
import re
from typing import Dict, List, Set
from .amount_parser import AmountParser
from .date_parser import DateParser
from .exchange_analyzer import ExchangeAnalyzer
from .confidence_calculator import ConfidenceCalculator


class CrossBankMatcher:
    """Handles cross-bank transfer detection and matching"""
    
    def __init__(self, user_name: str = "Ammar Qazi", date_tolerance_hours: int = 72):
        self.user_name = user_name
        self.date_tolerance_hours = date_tolerance_hours
        self.exchange_analyzer = ExchangeAnalyzer()
        self.confidence_calculator = ConfidenceCalculator(user_name)
        
        # Transfer description patterns
        self.transfer_patterns = [
            # Currency conversion patterns
            r"converted\s+[\d,.]+\s+\w{3}\s+(from\s+\w{3}\s+balance\s+)?to\s+[\d,.]+\s*\w{3}",
            r"converted\s+[\d,.]+\s+\w{3}",
            r"balance\s+after\s+converting",
            r"exchange\s+from\s+\w{3}\s+to\s+\w{3}",
            
            # User-specific patterns - AMMAR SPECIFICATIONS
            rf"sent\s+(money\s+)?to\s+{re.escape(user_name.lower())}",
            rf"transfer\s+to\s+{re.escape(user_name.lower())}",
            rf"transfer\s+from\s+{re.escape(user_name.lower())}",
            rf"incoming.*transfer\s+from\s+{re.escape(user_name.lower())}",

            # Generic transfer patterns
            r"transfer\s+to\s+\w+",
            r"transfer\s+from\s+\w+",
            r"incoming\s+fund\s+transfer",
            r"fund\s+transfer\s+from",
        ]
    
    def find_transfer_candidates(self, transactions: List[Dict]) -> List[Dict]:
        """Find transactions that match transfer description patterns"""
        candidates = []
        
        for transaction in transactions:
            # Check multiple possible description fields
            description = str(
                transaction.get('Description', '') or 
                transaction.get('Title', '') or 
                transaction.get('Note', '')
            ).lower()

            for pattern in self.transfer_patterns:
                match = re.search(pattern, description, re.IGNORECASE)
                if match:
                    candidates.append({
                        **transaction,
                        '_transfer_pattern': pattern,
                        '_is_transfer_candidate': True
                    })
                    break
        
        return candidates
    
    def match_cross_bank_transfers(self, potential_transfers: List[Dict], 
                                 all_transactions: List[Dict], 
                                 existing_pairs: List[Dict]) -> List[Dict]:
        """
        Match cross-bank transfers using AMMAR SPECIFICATIONS:
        1. Exchange To Amount matching (primary)
        2. Traditional amount matching (fallback)
        3. Ammar name-based matching for Wise <-> Pakistani banks
        4. Currency-based bank targeting
        """
        transfer_pairs = []
        existing_transaction_ids: Set[int] = set()
        
        # Get IDs of already matched transactions
        for pair in existing_pairs:
            existing_transaction_ids.add(pair['outgoing']['_transaction_index'])
            existing_transaction_ids.add(pair['incoming']['_transaction_index'])
        
        print(f"\n🔄 MATCHING CROSS-BANK TRANSFERS...")
        
        # Filter out already matched transactions
        available_outgoing = [
            t for t in potential_transfers 
            if t['_transaction_index'] not in existing_transaction_ids and 
               AmountParser.parse_amount(t.get('Amount', '0')) < 0  # Must be negative (outgoing)
        ]
        
        available_incoming = [
            t for t in all_transactions 
            if t['_transaction_index'] not in existing_transaction_ids and 
               AmountParser.parse_amount(t.get('Amount', '0')) > 0  # Must be positive (incoming)
        ]
        
        # Match each outgoing transaction
        for outgoing in available_outgoing:
            if outgoing['_transaction_index'] in existing_transaction_ids:
                continue
                
            best_match = self._find_best_match(outgoing, available_incoming, existing_transaction_ids)
            
            if best_match and best_match['confidence'] >= 0.7:
                transfer_pair = self._create_transfer_pair(outgoing, best_match, len(transfer_pairs))
                
                print(f"\n      🎉 TRANSFER PAIR CREATED!")
                print(f"         📤 Outgoing: {outgoing['_csv_name']} | -{transfer_pair['amount']}")
                print(f"         📥 Incoming: {best_match['incoming']['_csv_name']} | {best_match['incoming_amount']}")
                print(f"         🔧 Strategy: {best_match['type']}")
                print(f"         🎯 Confidence: {best_match['confidence']:.2f}")
                
                transfer_pairs.append(transfer_pair)
                existing_transaction_ids.add(outgoing['_transaction_index'])
                existing_transaction_ids.add(best_match['incoming']['_transaction_index'])
        
        print(f"\n   ✅ Created {len(transfer_pairs)} cross-bank transfer pairs")
        return transfer_pairs
    
    def _find_best_match(self, outgoing: Dict, available_incoming: List[Dict], 
                        existing_transaction_ids: Set[int]) -> Dict:
        """Find the best matching incoming transaction for an outgoing transfer"""
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

            # Check if this could be a cross-bank transfer
            if not self._is_ammar_cross_bank_transfer(outgoing, incoming):
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
        
        # Strategy 3: Ammar-specific transfer with relaxed amount matching
        if not matches:
            amount_diff_percentage = AmountParser.calculate_percentage_difference(
                outgoing_amount, incoming_amount
            )
            
            if amount_diff_percentage < 1.0:  # Allow up to 100% difference for currency conversion
                confidence = self.confidence_calculator.calculate_confidence(
                    outgoing, incoming, is_cross_bank=True
                ) - 0.1  # Slightly lower confidence
                min_confidence = max(confidence, 0.7)  # Higher minimum confidence for Ammar transfers
                matches.append({
                    'type': 'ammar_flexible',
                    'confidence': min_confidence,
                    'matched_amount': incoming_amount,  # Use incoming amount as reference
                    'match_details': f"Ammar transfer with currency conversion {outgoing_amount} USD → {incoming_amount} PKR"
                })
        
        return matches
    
    def _is_ammar_cross_bank_transfer(self, outgoing: Dict, incoming: Dict) -> bool:
        """
        Check if transactions form an Ammar-based cross-bank transfer
        AMMAR SPEC: "Sent money to Ammar" <-> "Incoming fund transfer from Ammar"
        """
        # Get descriptions from multiple possible fields
        outgoing_desc = self._get_description(outgoing).lower()
        incoming_desc = self._get_description(incoming).lower()
        user_name_lower = self.user_name.lower()
        
        # Must be different bank types
        outgoing_bank = outgoing.get('_bank_type', '')
        incoming_bank = incoming.get('_bank_type', '')
        
        if outgoing_bank == incoming_bank:
            return False

        # AMMAR SPEC: Wise -> Pakistani bank pattern
        if (outgoing_bank == 'wise' and
            incoming_bank in ['nayapay', 'bank_alfalah', 'meezan', 'pakistani_bank']):
            
            # Check for Ammar-specific patterns with more flexible matching
            sent_to_ammar = ('sent money to' in outgoing_desc and user_name_lower in outgoing_desc)
            
            # More flexible Ammar matching for incoming transactions
            ammar_variations = ['ammar qazi', 'ammar', 'qazi', 'ammar q']
            
            transfer_from_ammar = ('transfer from' in incoming_desc and user_name_lower in incoming_desc)
            incoming_fund_from_ammar = ('incoming fund transfer from' in incoming_desc and user_name_lower in incoming_desc)
            
            transfer_from_ammar_var = any(('transfer from' in incoming_desc and variation in incoming_desc) for variation in ammar_variations)
            incoming_fund_from_ammar_var = any(('incoming fund transfer from' in incoming_desc and variation in incoming_desc) for variation in ammar_variations)
            
            incoming_from_ammar = transfer_from_ammar or incoming_fund_from_ammar or transfer_from_ammar_var or incoming_fund_from_ammar_var
            
            if sent_to_ammar and incoming_from_ammar:
                return True
        
        # AMMAR SPEC: Pakistani bank -> Wise pattern (reverse)
        if (outgoing_bank in ['nayapay', 'bank_alfalah', 'meezan', 'pakistani_bank'] and
            incoming_bank == 'wise'):
            
            outgoing_to_ammar = ('transfer to' in outgoing_desc and user_name_lower in outgoing_desc)
            wise_from_ammar = ('received money from' in incoming_desc and user_name_lower in incoming_desc)
            
            if outgoing_to_ammar and wise_from_ammar:
                return True
        
        return False
    
    def _get_description(self, transaction: Dict) -> str:
        """Get description from transaction with fallback fields"""
        return str(
            transaction.get('Description', '') or 
            transaction.get('Title', '') or 
            transaction.get('Note', '') or 
            transaction.get('DESCRIPTION', '') or 
            transaction.get('TYPE', '')
        )
    
    def _create_transfer_pair(self, outgoing: Dict, best_match: Dict, pair_index: int) -> Dict:
        """Create a transfer pair from matched transactions"""
        outgoing_amount = abs(AmountParser.parse_amount(outgoing.get('Amount', '0')))
        exchange_amount = self.exchange_analyzer.get_exchange_to_amount(outgoing) if best_match['type'] == 'exchange_amount' else None
        
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
    
    def detect_bank_type(self, file_name: str, transaction: Dict) -> str:
        """Detect bank type from filename and transaction patterns"""
        file_name_lower = file_name.lower()
        
        if 'wise' in file_name_lower or 'transferwise' in file_name_lower:
            return 'wise'
        elif 'nayapay' in file_name_lower:
            return 'nayapay'
        elif 'bank alfalah' in file_name_lower or 'alfalah' in file_name_lower:
            return 'bank_alfalah'
        elif 'meezan' in file_name_lower:
            return 'meezan'
        else:
            # Try to detect from transaction patterns
            desc = str(transaction.get('Description', '')).lower()
            if 'incoming fund transfer' in desc or 'outgoing fund transfer' in desc:
                return 'pakistani_bank'
            return 'unknown'
