from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from datetime import datetime, timedelta
import re

class TransferDetector:
    """
    Advanced transfer detection system for multi-CSV processing
    Identifies matching transfer transactions across multiple CSV files
    """
    
    def __init__(self, user_name: str = "Ammar Qazi", date_tolerance_hours: int = 24):
        self.user_name = user_name
        self.date_tolerance_hours = date_tolerance_hours
        
        # Transfer description patterns - Enhanced with cross-bank patterns
        self.transfer_patterns = [
            r"converted\s+\w+",  # "Converted USD", "Converted EUR"
            rf"sent\s+(money\s+)?to\s+{re.escape(user_name.lower())}",  # "Sent money to Ammar Qazi", "Sent to Ammar Qazi"
            rf"transfer\s+to\s+{re.escape(user_name.lower())}",  # "Transfer to Ammar Qazi"
            rf"transfer\s+from\s+{re.escape(user_name.lower())}",  # "Transfer from Ammar Qazi"
            rf"incoming\s+fund\s+transfer\s+from\s+{re.escape(user_name.lower())}",  # "Incoming fund transfer from Ammar Qazi"
            r"transfer\s+to\s+\w+",  # "Transfer to account"
            r"transfer\s+from\s+\w+",  # "Transfer from account"
            r"incoming\s+fund\s+transfer",  # NayaPay pattern
            r"fund\s+transfer\s+from",  # Bank Alfalah pattern
        ]
    
    def detect_transfers(self, csv_data_list: List[Dict]) -> Dict[str, Any]:
        """
        Main transfer detection function
        
        Args:
            csv_data_list: List of parsed CSV data dictionaries
                Each dict should have: {'file_name', 'data', 'headers', 'template_config'}
        
        Returns:
            {
                'transfers': [list of detected transfer pairs],
                'potential_transfers': [transactions that might be transfers],
                'conflicts': [transactions with multiple potential matches],
                'flagged_transactions': [transactions needing manual review]
            }
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
        
        # Detect potential transfers by description patterns
        potential_transfers = self._find_transfer_candidates(all_transactions)
        
        # Match transfers by amount and date
        transfer_pairs = self._match_transfer_pairs(potential_transfers, all_transactions)
        
        # Detect conflicts (multiple potential matches)
        conflicts = self._detect_conflicts(transfer_pairs)
        
        # Flag transactions needing manual review
        flagged_transactions = self._flag_manual_review(all_transactions, transfer_pairs)
        
        return {
            'transfers': transfer_pairs,
            'potential_transfers': potential_transfers,
            'conflicts': conflicts,
            'flagged_transactions': flagged_transactions,
            'summary': {
                'total_transactions': len(all_transactions),
                'transfer_pairs_found': len(transfer_pairs),
                'potential_transfers': len(potential_transfers),
                'conflicts': len(conflicts),
                'flagged_for_review': len(flagged_transactions)
            }
        }
    
    def _find_transfer_candidates(self, transactions: List[Dict]) -> List[Dict]:
        """Find transactions that match transfer description patterns"""
        candidates = []
        
        for transaction in transactions:
            description = str(transaction.get('Description', '')).lower()
            
            # Check against transfer patterns
            for pattern in self.transfer_patterns:
                if re.search(pattern, description, re.IGNORECASE):
                    candidates.append({
                        **transaction,
                        '_transfer_pattern': pattern,
                        '_is_transfer_candidate': True
                    })
                    break
        
        return candidates
    
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
    
    def _match_transfer_pairs(self, potential_transfers: List[Dict], all_transactions: List[Dict]) -> List[Dict]:
        """Match outgoing and incoming transfers by amount and date"""
        transfer_pairs = []
        matched_transactions = set()
        
        for outgoing in potential_transfers:
            if outgoing['_transaction_index'] in matched_transactions:
                continue
                
            outgoing_amount = self._parse_amount(outgoing.get('Amount', '0'))
            outgoing_date = self._parse_date(outgoing.get('Date', ''))
            outgoing_exchange_to = self._parse_amount(outgoing.get('Exchange To Amount', '0'))
            
            # Skip if not a negative amount (outgoing)
            if outgoing_amount >= 0:
                continue
            
            # Look for matching incoming transaction
            for incoming in all_transactions:
                if incoming['_transaction_index'] in matched_transactions:
                    continue
                    
                incoming_amount = self._parse_amount(incoming.get('Amount', '0'))
                incoming_date = self._parse_date(incoming.get('Date', ''))
                
                # Skip if not a positive amount (incoming)
                if incoming_amount <= 0:
                    continue
                
                # Enhanced cross-bank matching for Wise->NayaPay
                cross_bank_match = self._is_cross_bank_transfer(outgoing, incoming)
                
                # Don't match within same CSV unless it's an internal transfer or cross-bank
                if (incoming['_csv_index'] == outgoing['_csv_index'] and 
                    not self._is_internal_conversion(outgoing, incoming) and 
                    not cross_bank_match):
                    continue
                
                # Check amount matching (use Exchange To Amount if available for cross-bank)
                amount_match = False
                if outgoing_exchange_to != 0:
                    # Match using exchange amount (for cross-bank transfers like Wise->NayaPay)
                    amount_match = abs(outgoing_exchange_to - incoming_amount) < 0.01
                else:
                    # Match using absolute amounts (for same-currency transfers)
                    amount_match = abs(abs(outgoing_amount) - incoming_amount) < 0.01
                
                # Check date proximity
                date_match = self._dates_within_tolerance(outgoing_date, incoming_date)
                
                if amount_match and date_match:
                    transfer_pair = {
                        'outgoing': outgoing,
                        'incoming': incoming,
                        'amount': abs(outgoing_amount),
                        'exchange_amount': outgoing_exchange_to if outgoing_exchange_to != 0 else None,
                        'date': outgoing_date,
                        'confidence': self._calculate_confidence(outgoing, incoming),
                        'pair_id': f"transfer_{len(transfer_pairs)}"
                    }
                    
                    transfer_pairs.append(transfer_pair)
                    matched_transactions.add(outgoing['_transaction_index'])
                    matched_transactions.add(incoming['_transaction_index'])
                    break
        
        return transfer_pairs
    
    def _is_cross_bank_transfer(self, outgoing: Dict, incoming: Dict) -> bool:
        """Check if this is a cross-bank transfer (like Wise->NayaPay)"""
        outgoing_desc = str(outgoing.get('Description', '')).lower()
        incoming_desc = str(incoming.get('Description', '')).lower()
        
        # Wise->NayaPay pattern
        if (outgoing.get('_bank_type') == 'wise' and 
            incoming.get('_bank_type') in ['nayapay', 'bank_alfalah', 'pakistani_bank']):
            
            # Check for "sent money" + user name in outgoing
            if ('sent money' in outgoing_desc and self.user_name.lower() in outgoing_desc):
                # Check for "incoming fund transfer" + user name in incoming
                if ('incoming fund transfer' in incoming_desc and self.user_name.lower() in incoming_desc):
                    return True
                elif ('fund transfer from' in incoming_desc and self.user_name.lower() in incoming_desc):
                    return True
        
        return False
    
    def _is_internal_conversion(self, outgoing: Dict, incoming: Dict) -> bool:
        """Check if this is an internal currency conversion (same bank, different currencies)"""
        outgoing_desc = str(outgoing.get('Description', '')).lower()
        incoming_desc = str(incoming.get('Description', '')).lower()
        
        # Both transactions should be from same bank type
        if outgoing.get('_bank_type') != incoming.get('_bank_type'):
            return False
            
        # Check for currency conversion patterns
        if ('converted' in outgoing_desc and 'converted' in incoming_desc):
            return True
            
        # Check for exchange patterns
        if (outgoing.get('Exchange To Amount', '0') != '0' and 
            'converted' in outgoing_desc and 
            ('balance' in incoming_desc or 'converted' in incoming_desc)):
            return True
            
        return False
    
    def _detect_conflicts(self, transfer_pairs: List[Dict]) -> List[Dict]:
        """Detect transactions that could match multiple partners"""
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
                    'requires_manual_review': True
                })
        
        return conflicts
    
    def _flag_manual_review(self, all_transactions: List[Dict], transfer_pairs: List[Dict]) -> List[Dict]:
        """Flag transactions that need manual review"""
        flagged = []
        
        # Get all matched transaction IDs
        matched_ids = set()
        for pair in transfer_pairs:
            matched_ids.add(pair['outgoing']['_transaction_index'])
            matched_ids.add(pair['incoming']['_transaction_index'])
        
        # Flag unmatched potential transfers
        for transaction in all_transactions:
            if transaction.get('_is_transfer_candidate') and transaction['_transaction_index'] not in matched_ids:
                flagged.append({
                    **transaction,
                    '_flag_reason': 'unmatched_transfer_candidate',
                    '_needs_manual_review': True
                })
        
        # Flag large amounts that might be transfers
        for transaction in all_transactions:
            amount = abs(self._parse_amount(transaction.get('Amount', '0')))
            if amount > 10000 and transaction['_transaction_index'] not in matched_ids:  # Configurable threshold
                description = str(transaction.get('Description', '')).lower()
                if any(word in description for word in ['transfer', 'convert', 'exchange', 'send']):
                    flagged.append({
                        **transaction,
                        '_flag_reason': 'large_amount_potential_transfer',
                        '_needs_manual_review': True
                    })
        
        return flagged
    
    def _calculate_confidence(self, outgoing: Dict, incoming: Dict) -> float:
        """Calculate confidence score for transfer pair matching"""
        confidence = 0.0
        
        # Base confidence for amount and date match
        confidence += 0.4
        
        # Higher confidence for cross-bank transfers (Wise->NayaPay)
        if self._is_cross_bank_transfer(outgoing, incoming):
            confidence += 0.4  # High confidence for cross-bank with name matching
        
        # Bonus for description pattern match
        if outgoing.get('_transfer_pattern'):
            confidence += 0.2
        
        # Bonus for same-day transactions
        outgoing_date = self._parse_date(outgoing.get('Date', ''))
        incoming_date = self._parse_date(incoming.get('Date', ''))
        if outgoing_date.date() == incoming_date.date():
            confidence += 0.2
        
        # Bonus for Exchange To Amount matching (cross-bank transfers)
        outgoing_exchange = self._parse_amount(outgoing.get('Exchange To Amount', '0'))
        incoming_amount = self._parse_amount(incoming.get('Amount', '0'))
        if outgoing_exchange > 0 and abs(outgoing_exchange - incoming_amount) < 0.01:
            confidence += 0.1
        
        # Bonus for exact amount match (same currency)
        outgoing_amount = abs(self._parse_amount(outgoing.get('Amount', '0')))
        if abs(outgoing_amount - incoming_amount) < 0.01:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float"""
        try:
            # Remove currency symbols, commas, spaces
            cleaned = re.sub(r'[^0-9.\-]', '', str(amount_str))
            return float(cleaned) if cleaned else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        try:
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y-%m-%d %H:%M:%S']:
                try:
                    return datetime.strptime(str(date_str), fmt)
                except ValueError:
                    continue
            
            # Fallback to current date if parsing fails
            return datetime.now()
        except Exception:
            return datetime.now()
    
    def _dates_within_tolerance(self, date1: datetime, date2: datetime) -> bool:
        """Check if two dates are within the tolerance period"""
        try:
            delta = abs((date1 - date2).total_seconds() / 3600)  # Convert to hours
            return delta <= self.date_tolerance_hours
        except Exception:
            return False
    
    def apply_transfer_categorization(self, csv_data_list: List[Dict], transfer_pairs: List[Dict]) -> List[Dict]:
        """Apply Balance Correction category to detected transfers using proper transaction matching"""
        
        # Create a comprehensive mapping of transfers by matching transaction details
        transfer_matches = []
        for pair in transfer_pairs:
            outgoing = pair['outgoing']
            incoming = pair['incoming']
            
            transfer_matches.append({
                'csv_index': outgoing['_csv_index'],
                'amount': str(self._parse_amount(outgoing.get('Amount', '0'))),
                'date': self._parse_date(outgoing.get('Date', '')).strftime('%Y-%m-%d'),
                'description': str(outgoing.get('Description', '')),
                'category': 'Balance Correction',
                'note': f"Transfer out - Pair ID: {pair['pair_id']}",
                'pair_id': pair['pair_id'],
                'transfer_type': 'outgoing'
            })
            
            transfer_matches.append({
                'csv_index': incoming['_csv_index'],
                'amount': str(self._parse_amount(incoming.get('Amount', '0'))),
                'date': self._parse_date(incoming.get('Date', '')).strftime('%Y-%m-%d'),
                'description': str(incoming.get('Description', '')),
                'category': 'Balance Correction',
                'note': f"Transfer in - Pair ID: {pair['pair_id']}",
                'pair_id': pair['pair_id'],
                'transfer_type': 'incoming'
            })
        
        return transfer_matches
