"""
Currency conversion detection and matching
"""
import re
from typing import Dict, List, Optional, Set
from .amount_parser import AmountParser
from .date_parser import DateParser


class CurrencyConverter:
    """Handles currency conversion detection and matching"""
    
    def match_currency_conversions(self, all_transactions: List[Dict]) -> List[Dict]:
        """Match internal currency conversions"""
        conversion_pairs = []
        matched_transactions: Set[int] = set()
        
        conversion_candidates = []
        
        for transaction in all_transactions:
            if transaction['_transaction_index'] in matched_transactions:
                continue
                
            desc = str(transaction.get('Description', '')).lower()
            amount = AmountParser.parse_amount(transaction.get('Amount', '0'))
            date = DateParser.parse_date(transaction.get('Date', ''))
            
            conversion_info = self.extract_conversion_info(desc, amount)
            
            if conversion_info:
                conversion_candidates.append({
                    **transaction,
                    '_conversion_info': conversion_info,
                    '_amount': amount,
                    '_date': date
                })
        
        # Match conversion pairs
        for i, candidate1 in enumerate(conversion_candidates):
            if candidate1['_transaction_index'] in matched_transactions:
                continue
                
            conv1 = candidate1['_conversion_info']
            
            for j, candidate2 in enumerate(conversion_candidates):
                if (i >= j or 
                    candidate2['_transaction_index'] in matched_transactions or
                    candidate1['_csv_index'] == candidate2['_csv_index']):
                    continue
                
                conv2 = candidate2['_conversion_info']
                
                if self.is_matching_conversion(conv1, conv2, candidate1, candidate2):
                    if candidate1['_amount'] < 0 and candidate2['_amount'] > 0:
                        outgoing, incoming = candidate1, candidate2
                    elif candidate1['_amount'] > 0 and candidate2['_amount'] < 0:
                        outgoing, incoming = candidate2, candidate1
                    else:
                        continue
                    
                    confidence = self.calculate_conversion_confidence(outgoing, incoming, conv1, conv2)
                    
                    transfer_pair = {
                        'outgoing': outgoing,
                        'incoming': incoming,
                        'amount': abs(outgoing['_amount']),
                        'exchange_amount': abs(incoming['_amount']),
                        'date': outgoing['_date'],
                        'confidence': confidence,
                        'pair_id': f"conversion_{len(conversion_pairs)}",
                        'transfer_type': 'currency_conversion',
                        'conversion_details': {
                            'from_currency': conv1['from_currency'],
                            'to_currency': conv1['to_currency'],
                            'from_amount': conv1['from_amount'],
                            'to_amount': conv1['to_amount']
                        }
                    }
                    
                    conversion_pairs.append(transfer_pair)
                    matched_transactions.add(outgoing['_transaction_index'])
                    matched_transactions.add(incoming['_transaction_index'])
                    break
        
        return conversion_pairs
    
    def extract_conversion_info(self, description: str, amount: float) -> Optional[Dict]:
        """Extract currency conversion details from description"""
        patterns = [
            r"converted\s+([\d,.]+)\s+(\w{3})\s+(?:from\s+\w{3}\s+balance\s+)?to\s+([\d,.]+)\s*(\w{3})",
            r"converted\s+([\d,.]+)\s+(\w{3}).*?to\s+([\d,.]+)\s*(\w{3})",
            r"converted\s+([\d,.]+)\s+(\w{3})\s+from\s+\w{3}\s+balance\s+to\s+([\d,.]+)\s*(\w{3})"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                from_amount = float(match.group(1).replace(',', ''))
                from_currency = match.group(2).upper()
                to_amount = float(match.group(3).replace(',', ''))
                to_currency = match.group(4).upper()
                
                return {
                    'from_amount': from_amount,
                    'from_currency': from_currency,
                    'to_amount': to_amount,
                    'to_currency': to_currency
                }
        
        return None
    
    def is_matching_conversion(self, conv1: Dict, conv2: Dict, 
                             candidate1: Dict, candidate2: Dict) -> bool:
        """Check if two conversion records represent the same conversion"""
        amounts_match = (
            abs(conv1['from_amount'] - conv2['from_amount']) < 0.01 and
            abs(conv1['to_amount'] - conv2['to_amount']) < 0.01 and
            conv1['from_currency'] == conv2['from_currency'] and
            conv1['to_currency'] == conv2['to_currency']
        )
        
        date_match = DateParser.dates_within_tolerance(candidate1['_date'], candidate2['_date'])
        opposite_signs = (candidate1['_amount'] * candidate2['_amount']) < 0
        
        amount1_matches = (
            abs(abs(candidate1['_amount']) - conv1['from_amount']) < 0.01 or
            abs(abs(candidate1['_amount']) - conv1['to_amount']) < 0.01
        )
        
        amount2_matches = (
            abs(abs(candidate2['_amount']) - conv2['from_amount']) < 0.01 or
            abs(abs(candidate2['_amount']) - conv2['to_amount']) < 0.01
        )
        
        return amounts_match and date_match and opposite_signs and amount1_matches and amount2_matches
    
    def calculate_conversion_confidence(self, outgoing: Dict, incoming: Dict, 
                                      conv1: Dict, conv2: Dict) -> float:
        """Calculate confidence for currency conversion matches"""
        confidence = 0.5
        
        if (abs(abs(outgoing['_amount']) - conv1['from_amount']) < 0.01 and
            abs(abs(incoming['_amount']) - conv1['to_amount']) < 0.01):
            confidence += 0.3
        
        outgoing_date = DateParser.parse_date(outgoing.get('Date', ''))
        incoming_date = DateParser.parse_date(incoming.get('Date', ''))
        if DateParser.same_day(outgoing_date, incoming_date):
            confidence += 0.2
        
        if ('converted' in str(outgoing.get('Description', '')).lower() and
            'converted' in str(incoming.get('Description', '')).lower()):
            confidence += 0.2
        
        if (conv1['from_amount'] == conv2['from_amount'] and
            conv1['to_amount'] == conv2['to_amount'] and
            conv1['from_currency'] == conv2['from_currency'] and
            conv1['to_currency'] == conv2['to_currency']):
            confidence += 0.1
        
        return min(confidence, 1.0)
