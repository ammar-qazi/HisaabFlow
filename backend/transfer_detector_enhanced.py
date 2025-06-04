from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from datetime import datetime, timedelta
import re

class EnhancedTransferDetector:
    """
    Enhanced transfer detection system with support for:
    1. Cross-account currency conversions (Wise USD->EUR)
    2. Cross-bank transfers (Wise->NayaPay, Wise->Bank Alfalah) 
    3. Internal account transfers
    4. Manual transfer pattern detection
    """
    
    def __init__(self, user_name: str = "Ammar Qazi", date_tolerance_hours: int = 24):
        self.user_name = user_name
        self.date_tolerance_hours = date_tolerance_hours
        
        # Enhanced transfer description patterns with cross-bank support
        self.transfer_patterns = {
            # Wise patterns
            'wise_sent_money': rf"sent\s+money\s+to\s+{re.escape(user_name.lower())}",
            'wise_transfer_to': rf"transfer\s+to\s+{re.escape(user_name.lower())}",
            'wise_converted': r"converted\s+[\d,.]+ \w{3}",  # "Converted 108.99 USD"
            
            # NayaPay/Bank patterns  
            'incoming_fund_transfer': rf"incoming\s+fund\s+transfer\s+from\s+{re.escape(user_name.lower())}",
            'fund_transfer_from': rf"fund\s+transfer\s+from\s+{re.escape(user_name.lower())}",
            'transfer_from_user': rf"transfer\s+from\s+{re.escape(user_name.lower())}",
            
            # General patterns
            'transfer_to': r"transfer\s+to\s+\w+",
            'transfer_from': r"transfer\s+from\s+\w+",
            'conversion': r"conversion|convert|exchange",
            'sent_to': r"sent\s+to\s+\w+",
            'received_from': r"received\s+from\s+\w+"
        }
        
        # Bank-specific patterns for better detection
        self.bank_patterns = {
            'wise': [
                r"sent\s+money",
                r"converted\s+\w+",
                r"exchange\s+to\s+amount",
                r"transfer\s+to"
            ],
            'nayapay': [
                r"incoming\s+fund\s+transfer",
                r"fund\s+transfer\s+from",
                r"transaction\s+id\s+\d+"
            ],
            'bank_alfalah': [
                r"bank\s+alfalah",
                r"transaction\s+id\s+\d+"
            ]
        }
    
    def detect_transfers(self, csv_data_list: List[Dict]) -> Dict[str, Any]:
        """
        Enhanced transfer detection with cross-bank support
        
        Args:
            csv_data_list: List of parsed CSV data dictionaries
        
        Returns:
            Enhanced transfer analysis with cross-bank detection
        """
        
        # Flatten all transactions with source info
        all_transactions = []
        for csv_idx, csv_data in enumerate(csv_data_list):
            for trans_idx, transaction in enumerate(csv_data['data']):
                enhanced_transaction = {
                    **transaction,
                    '_csv_index': csv_idx,
                    '_transaction_index': trans_idx,
                    '_csv_name': csv_data.get('file_name', f'CSV_{csv_idx}'),
                    '_template_config': csv_data.get('template_config', {}),
                    '_bank_type': self._detect_bank_type(csv_data.get('file_name', ''), transaction)
                }
                all_transactions.append(enhanced_transaction)
        
        # Enhanced transfer detection strategies
        transfer_pairs = []
        
        # Strategy 1: Cross-bank transfers (Wise->NayaPay)
        cross_bank_transfers = self._detect_cross_bank_transfers(all_transactions)
        transfer_pairs.extend(cross_bank_transfers)
        
        # Strategy 2: Currency conversion transfers (same bank, different currencies)
        currency_transfers = self._detect_currency_conversions(all_transactions)
        transfer_pairs.extend(currency_transfers)
        
        # Strategy 3: Traditional same-day amount matching
        traditional_transfers = self._detect_traditional_transfers(all_transactions, transfer_pairs)
        transfer_pairs.extend(traditional_transfers)
        
        # Detect potential unmatched transfers
        potential_transfers = self._find_unmatched_transfer_candidates(all_transactions, transfer_pairs)
        
        # Detect conflicts and flagged transactions
        conflicts = self._detect_conflicts(transfer_pairs)
        flagged_transactions = self._flag_manual_review(all_transactions, transfer_pairs)
        
        return {
            'transfers': transfer_pairs,
            'potential_transfers': potential_transfers,
            'conflicts': conflicts,
            'flagged_transactions': flagged_transactions,
            'detection_strategies': {
                'cross_bank_transfers': len(cross_bank_transfers),
                'currency_conversions': len(currency_transfers), 
                'traditional_transfers': len(traditional_transfers)
            },
            'summary': {
                'total_transactions': len(all_transactions),
                'transfer_pairs_found': len(transfer_pairs),
                'potential_transfers': len(potential_transfers),
                'conflicts': len(conflicts),
                'flagged_for_review': len(flagged_transactions)
            }
        }
    
    def _detect_bank_type(self, file_name: str, transaction: Dict) -> str:
        """Detect bank type from filename and transaction patterns"""
        file_name_lower = file_name.lower()
        description = str(transaction.get('Description', '')).lower()
        
        if 'wise' in file_name_lower or 'transferwise' in file_name_lower:
            return 'wise'
        elif 'nayapay' in file_name_lower:
            return 'nayapay'
        elif 'bank alfalah' in description or 'alfalah' in file_name_lower:
            return 'bank_alfalah'
        elif any(pattern in description for pattern in ['raast', 'ibft', 'p2p']):
            return 'pakistani_bank'
        else:
            return 'unknown'
    
    def _detect_cross_bank_transfers(self, transactions: List[Dict]) -> List[Dict]:
        """
        Detect cross-bank transfers like Wise->NayaPay
        
        Patterns:
        - Wise: "Sent money to Ammar Qazi" with Exchange To Amount
        - NayaPay: "Incoming fund transfer from Ammar Qazi Bank Alfalah-2050"
        """
        cross_bank_pairs = []
        matched_transactions = set()
        
        # Find Wise outgoing transactions 
        wise_outgoing = [t for t in transactions 
                        if t['_bank_type'] == 'wise' 
                        and self._parse_amount(t.get('Amount', '0')) < 0
                        and t['_transaction_index'] not in matched_transactions]
        
        # Find potential incoming transactions from other banks
        other_incoming = [t for t in transactions 
                         if t['_bank_type'] in ['nayapay', 'bank_alfalah', 'pakistani_bank']
                         and self._parse_amount(t.get('Amount', '0')) > 0
                         and t['_transaction_index'] not in matched_transactions]
        
        for wise_out in wise_outgoing:
            wise_description = str(wise_out.get('Description', '')).lower()
            wise_amount = abs(self._parse_amount(wise_out.get('Amount', '0')))
            wise_exchange_amount = self._parse_amount(wise_out.get('Exchange To Amount', '0'))
            wise_date = self._parse_date(wise_out.get('Date', ''))
            
            # Check if this looks like a "sent money" transaction
            if not any(pattern in wise_description for pattern in ['sent money', 'transfer to', 'sent to']):
                continue
                
            # Look for matching incoming transaction
            for other_in in other_incoming:
                if other_in['_transaction_index'] in matched_transactions:
                    continue
                    
                other_description = str(other_in.get('Description', '')).lower()
                other_amount = self._parse_amount(other_in.get('Amount', '0'))
                other_date = self._parse_date(other_in.get('Date', ''))
                
                # Check if description suggests incoming transfer from user
                incoming_patterns = [
                    'incoming fund transfer',
                    'fund transfer from',
                    'transfer from',
                    'received from'
                ]
                
                if not any(pattern in other_description for pattern in incoming_patterns):
                    continue
                
                # Amount matching logic
                amount_match = False
                amount_used = wise_amount
                
                # If Wise has Exchange To Amount, use that for matching
                if wise_exchange_amount > 0:
                    amount_match = abs(wise_exchange_amount - other_amount) < 0.01
                    amount_used = wise_exchange_amount
                else:
                    # Direct amount matching (same currency)
                    amount_match = abs(wise_amount - other_amount) < 0.01
                
                # Date matching (within tolerance)
                date_match = self._dates_within_tolerance(wise_date, other_date)
                
                # Enhanced name matching
                user_name_match = (
                    self.user_name.lower() in wise_description and 
                    self.user_name.lower() in other_description
                )
                
                if amount_match and date_match and user_name_match:
                    confidence = self._calculate_cross_bank_confidence(wise_out, other_in)
                    
                    pair = {
                        'outgoing': wise_out,
                        'incoming': other_in,
                        'amount': wise_amount,
                        'exchange_amount': wise_exchange_amount if wise_exchange_amount > 0 else None,
                        'date': wise_date,
                        'confidence': confidence,
                        'pair_id': f"cross_bank_{len(cross_bank_pairs)}",
                        'transfer_type': 'cross_bank',
                        'from_bank': wise_out['_bank_type'],
                        'to_bank': other_in['_bank_type']
                    }
                    
                    cross_bank_pairs.append(pair)
                    matched_transactions.add(wise_out['_transaction_index'])
                    matched_transactions.add(other_in['_transaction_index'])
                    break
        
        return cross_bank_pairs
    
    def _detect_currency_conversions(self, transactions: List[Dict]) -> List[Dict]:
        """
        Detect currency conversion transfers within same bank (e.g., Wise USD->EUR)
        """
        conversion_pairs = []
        matched_transactions = set()
        
        # Group transactions by bank
        bank_groups = {}
        for transaction in transactions:
            bank_type = transaction['_bank_type']
            if bank_type not in bank_groups:
                bank_groups[bank_type] = []
            bank_groups[bank_type].append(transaction)
        
        # Look for conversions within each bank
        for bank_type, bank_transactions in bank_groups.items():
            if bank_type == 'wise':  # Wise typically has currency conversions
                conversion_pairs.extend(
                    self._detect_wise_conversions(bank_transactions, matched_transactions)
                )
        
        return conversion_pairs
    
    def _detect_wise_conversions(self, wise_transactions: List[Dict], matched_transactions: set) -> List[Dict]:
        """Detect Wise internal currency conversions"""
        conversion_pairs = []
        
        # Find outgoing conversion transactions
        outgoing_conversions = [
            t for t in wise_transactions 
            if self._parse_amount(t.get('Amount', '0')) < 0
            and t['_transaction_index'] not in matched_transactions
            and ('converted' in str(t.get('Description', '')).lower() or 
                 self._parse_amount(t.get('Exchange To Amount', '0')) > 0)
        ]
        
        # Find incoming conversions
        incoming_conversions = [
            t for t in wise_transactions 
            if self._parse_amount(t.get('Amount', '0')) > 0
            and t['_transaction_index'] not in matched_transactions
            and 'converted' in str(t.get('Description', '')).lower()
        ]
        
        for outgoing in outgoing_conversions:
            out_amount = abs(self._parse_amount(outgoing.get('Amount', '0')))
            out_exchange = self._parse_amount(outgoing.get('Exchange To Amount', '0'))
            out_date = self._parse_date(outgoing.get('Date', ''))
            
            for incoming in incoming_conversions:
                if incoming['_transaction_index'] in matched_transactions:
                    continue
                    
                in_amount = self._parse_amount(incoming.get('Amount', '0'))
                in_date = self._parse_date(incoming.get('Date', ''))
                
                # Amount matching
                amount_match = False
                if out_exchange > 0:
                    amount_match = abs(out_exchange - in_amount) < 0.01
                else:
                    amount_match = abs(out_amount - in_amount) < 0.01
                
                # Date matching (same day for conversions)
                date_match = out_date.date() == in_date.date()
                
                if amount_match and date_match:
                    pair = {
                        'outgoing': outgoing,
                        'incoming': incoming,
                        'amount': out_amount,
                        'exchange_amount': out_exchange if out_exchange > 0 else None,
                        'date': out_date,
                        'confidence': 0.9,  # High confidence for same-bank conversions
                        'pair_id': f"conversion_{len(conversion_pairs)}",
                        'transfer_type': 'currency_conversion',
                        'from_bank': 'wise',
                        'to_bank': 'wise'
                    }
                    
                    conversion_pairs.append(pair)
                    matched_transactions.add(outgoing['_transaction_index'])
                    matched_transactions.add(incoming['_transaction_index'])
                    break
        
        return conversion_pairs
    
    def _detect_traditional_transfers(self, transactions: List[Dict], existing_pairs: List[Dict]) -> List[Dict]:
        """Traditional transfer detection for any remaining unmatched transfers"""
        traditional_pairs = []
        
        # Get already matched transaction IDs
        matched_transactions = set()
        for pair in existing_pairs:
            matched_transactions.add(pair['outgoing']['_transaction_index'])
            matched_transactions.add(pair['incoming']['_transaction_index'])
        
        # Find unmatched transfer candidates
        transfer_candidates = []
        for transaction in transactions:
            if transaction['_transaction_index'] in matched_transactions:
                continue
                
            description = str(transaction.get('Description', '')).lower()
            
            # Check against all transfer patterns
            for pattern_name, pattern in self.transfer_patterns.items():
                if re.search(pattern, description, re.IGNORECASE):
                    transfer_candidates.append({
                        **transaction,
                        '_transfer_pattern': pattern_name,
                        '_is_transfer_candidate': True
                    })
                    break
        
        # Match remaining candidates using traditional logic
        for outgoing in transfer_candidates:
            if outgoing['_transaction_index'] in matched_transactions:
                continue
                
            outgoing_amount = self._parse_amount(outgoing.get('Amount', '0'))
            if outgoing_amount >= 0:  # Only outgoing (negative) amounts
                continue
                
            outgoing_date = self._parse_date(outgoing.get('Date', ''))
            
            for incoming in transactions:
                if incoming['_transaction_index'] in matched_transactions:
                    continue
                    
                # Don't match within same CSV unless internal transfer
                if incoming['_csv_index'] == outgoing['_csv_index']:
                    continue
                
                incoming_amount = self._parse_amount(incoming.get('Amount', '0'))
                if incoming_amount <= 0:  # Only incoming (positive) amounts
                    continue
                    
                incoming_date = self._parse_date(incoming.get('Date', ''))
                
                # Amount and date matching
                amount_match = abs(abs(outgoing_amount) - incoming_amount) < 0.01
                date_match = self._dates_within_tolerance(outgoing_date, incoming_date)
                
                if amount_match and date_match:
                    pair = {
                        'outgoing': outgoing,
                        'incoming': incoming,
                        'amount': abs(outgoing_amount),
                        'exchange_amount': None,
                        'date': outgoing_date,
                        'confidence': self._calculate_confidence(outgoing, incoming),
                        'pair_id': f"traditional_{len(traditional_pairs)}",
                        'transfer_type': 'traditional',
                        'from_bank': outgoing['_bank_type'],
                        'to_bank': incoming['_bank_type']
                    }
                    
                    traditional_pairs.append(pair)
                    matched_transactions.add(outgoing['_transaction_index'])
                    matched_transactions.add(incoming['_transaction_index'])
                    break
        
        return traditional_pairs
    
    def _calculate_cross_bank_confidence(self, wise_transaction: Dict, other_transaction: Dict) -> float:
        """Calculate confidence for cross-bank transfer matches"""
        confidence = 0.5  # Base confidence
        
        wise_desc = str(wise_transaction.get('Description', '')).lower()
        other_desc = str(other_transaction.get('Description', '')).lower()
        
        # High confidence indicators
        if 'sent money' in wise_desc and 'incoming fund transfer' in other_desc:
            confidence += 0.3
            
        if self.user_name.lower() in wise_desc and self.user_name.lower() in other_desc:
            confidence += 0.2
            
        # Same day transaction
        wise_date = self._parse_date(wise_transaction.get('Date', ''))
        other_date = self._parse_date(other_transaction.get('Date', ''))
        if wise_date.date() == other_date.date():
            confidence += 0.2
            
        # Exchange amount present
        if self._parse_amount(wise_transaction.get('Exchange To Amount', '0')) > 0:
            confidence += 0.1
            
        return min(confidence, 1.0)
    
    def _find_unmatched_transfer_candidates(self, transactions: List[Dict], transfer_pairs: List[Dict]) -> List[Dict]:
        """Find potential transfers that weren't matched"""
        matched_transactions = set()
        for pair in transfer_pairs:
            matched_transactions.add(pair['outgoing']['_transaction_index'])
            matched_transactions.add(pair['incoming']['_transaction_index'])
        
        candidates = []
        for transaction in transactions:
            if transaction['_transaction_index'] in matched_transactions:
                continue
                
            description = str(transaction.get('Description', '')).lower()
            
            # Check for transfer-like descriptions
            transfer_indicators = [
                'transfer', 'sent', 'received', 'convert', 'exchange',
                'fund transfer', 'money transfer', 'raast', 'ibft'
            ]
            
            if any(indicator in description for indicator in transfer_indicators):
                candidates.append({
                    **transaction,
                    '_unmatched_reason': 'potential_transfer_pattern',
                    '_needs_manual_review': True
                })
        
        return candidates
    
    def _detect_conflicts(self, transfer_pairs: List[Dict]) -> List[Dict]:
        """Enhanced conflict detection"""
        conflicts = []
        
        # Group by outgoing transaction to find multiple potential matches
        outgoing_groups = {}
        for pair in transfer_pairs:
            outgoing_id = pair['outgoing']['_transaction_index']
            if outgoing_id not in outgoing_groups:
                outgoing_groups[outgoing_id] = []
            outgoing_groups[outgoing_id].append(pair)
        
        # Find groups with multiple matches
        for outgoing_id, pairs in outgoing_groups.items():
            if len(pairs) > 1:
                conflicts.append({
                    'outgoing_transaction': pairs[0]['outgoing'],
                    'potential_matches': [p['incoming'] for p in pairs],
                    'conflict_type': 'multiple_incoming_matches',
                    'confidence_scores': [p['confidence'] for p in pairs],
                    'requires_manual_review': True
                })
        
        return conflicts
    
    def _flag_manual_review(self, transactions: List[Dict], transfer_pairs: List[Dict]) -> List[Dict]:
        """Enhanced manual review flagging"""
        flagged = []
        
        matched_ids = set()
        for pair in transfer_pairs:
            matched_ids.add(pair['outgoing']['_transaction_index'])
            matched_ids.add(pair['incoming']['_transaction_index'])
        
        for transaction in transactions:
            if transaction['_transaction_index'] in matched_ids:
                continue
                
            amount = abs(self._parse_amount(transaction.get('Amount', '0')))
            description = str(transaction.get('Description', '')).lower()
            
            # Flag large amounts with transfer keywords
            if amount > 5000 and any(word in description for word in ['transfer', 'sent', 'received']):
                flagged.append({
                    **transaction,
                    '_flag_reason': 'large_amount_with_transfer_keywords',
                    '_needs_manual_review': True
                })
            
            # Flag Wise transactions with Exchange To Amount but no match
            elif (transaction['_bank_type'] == 'wise' and 
                  self._parse_amount(transaction.get('Exchange To Amount', '0')) > 0):
                flagged.append({
                    **transaction,
                    '_flag_reason': 'wise_exchange_amount_unmatched',
                    '_needs_manual_review': True
                })
        
        return flagged
    
    # Utility methods (keeping existing implementations)
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float"""
        try:
            cleaned = re.sub(r'[^0-9.\-]', '', str(amount_str))
            return float(cleaned) if cleaned else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        try:
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y-%m-%d %H:%M:%S']:
                try:
                    return datetime.strptime(str(date_str), fmt)
                except ValueError:
                    continue
            return datetime.now()
        except Exception:
            return datetime.now()
    
    def _dates_within_tolerance(self, date1: datetime, date2: datetime) -> bool:
        """Check if two dates are within the tolerance period"""
        try:
            delta = abs((date1 - date2).total_seconds() / 3600)
            return delta <= self.date_tolerance_hours
        except Exception:
            return False
    
    def _calculate_confidence(self, outgoing: Dict, incoming: Dict) -> float:
        """Calculate confidence score for transfer pair matching"""
        confidence = 0.4  # Base confidence
        
        # Bonus for description pattern match
        if outgoing.get('_transfer_pattern'):
            confidence += 0.3
        
        # Same-day bonus
        outgoing_date = self._parse_date(outgoing.get('Date', ''))
        incoming_date = self._parse_date(incoming.get('Date', ''))
        if outgoing_date.date() == incoming_date.date():
            confidence += 0.2
        
        # Exact amount match bonus
        outgoing_amount = abs(self._parse_amount(outgoing.get('Amount', '0')))
        incoming_amount = self._parse_amount(incoming.get('Amount', '0'))
        if abs(outgoing_amount - incoming_amount) < 0.01:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def apply_transfer_categorization(self, csv_data_list: List[Dict], transfer_pairs: List[Dict]) -> List[Dict]:
        """Apply Balance Correction category to detected transfers with enhanced matching"""
        
        transfer_matches = []
        for pair in transfer_pairs:
            outgoing = pair['outgoing']
            incoming = pair['incoming']
            
            # Enhanced transfer matching with cross-bank support
            transfer_matches.append({
                'csv_index': outgoing['_csv_index'],
                'amount': str(self._parse_amount(outgoing.get('Amount', '0'))),
                'date': self._parse_date(outgoing.get('Date', '')).strftime('%Y-%m-%d'),
                'description': str(outgoing.get('Description', '')),
                'category': 'Balance Correction',
                'note': f"{pair['transfer_type'].title()} transfer out - {pair['from_bank']} to {pair['to_bank']} - Pair ID: {pair['pair_id']}",
                'pair_id': pair['pair_id'],
                'transfer_type': 'outgoing',
                'bank_transfer_type': pair['transfer_type'],
                'exchange_amount': pair.get('exchange_amount')
            })
            
            transfer_matches.append({
                'csv_index': incoming['_csv_index'],
                'amount': str(self._parse_amount(incoming.get('Amount', '0'))),
                'date': self._parse_date(incoming.get('Date', '')).strftime('%Y-%m-%d'),
                'description': str(incoming.get('Description', '')),
                'category': 'Balance Correction',
                'note': f"{pair['transfer_type'].title()} transfer in - {pair['from_bank']} to {pair['to_bank']} - Pair ID: {pair['pair_id']}",
                'pair_id': pair['pair_id'],
                'transfer_type': 'incoming',
                'bank_transfer_type': pair['transfer_type'],
                'exchange_amount': pair.get('exchange_amount')
            })
        
        return transfer_matches
