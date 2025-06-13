"""
Confidence calculation for transfer matches
"""
from typing import Dict
from .date_parser import DateParser


class ConfidenceCalculator:
    """Calculates confidence scores for transfer pair matching"""
    
    def __init__(self):
        pass
    
    def calculate_confidence(self, outgoing: Dict, incoming: Dict, 
                           is_cross_bank: bool = False, 
                           is_exchange_match: bool = False) -> float:
        """Calculate confidence score for transfer pair matching"""
        confidence = 0.5  # Base confidence
        
        if is_cross_bank:
            confidence += 0.2
        
        # Higher confidence for exchange amount matches
        if is_exchange_match:
            confidence += 0.3  # Exchange matches are very reliable
        
        # Same day bonus
        outgoing_date = DateParser.parse_date(outgoing.get('Date', ''))
        incoming_date = DateParser.parse_date(incoming.get('Date', ''))
        if DateParser.same_day(outgoing_date, incoming_date):
            confidence += 0.2
        
        # Name match bonus (flexible name detection)
        outgoing_desc = str(outgoing.get('Description', '')).lower()
        incoming_desc = str(incoming.get('Description', '')).lower()
        
        # Look for common name patterns in transfer descriptions
        if ('transfer to' in outgoing_desc and 'from' in incoming_desc) or \
           ('sent to' in outgoing_desc and 'received from' in incoming_desc):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def calculate_conversion_confidence(self, outgoing: Dict, incoming: Dict, 
                                      conv1: Dict, conv2: Dict) -> float:
        """Calculate confidence for currency conversion matches"""
        confidence = 0.5
        
        if (abs(abs(outgoing.get('_amount', 0)) - conv1['from_amount']) < 0.01 and
            abs(abs(incoming.get('_amount', 0)) - conv1['to_amount']) < 0.01):
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
