from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from datetime import datetime, timedelta
import re

class TransferDetector:
    """
    Enhanced transfer detection system for multi-CSV processing
    ENHANCED: Added exchange amount matching for currency conversions
    """
    
    def __init__(self, user_name: str = "Ammar Qazi", date_tolerance_hours: int = 24):
        self.user_name = user_name
        self.date_tolerance_hours = date_tolerance_hours
        
        # Transfer description patterns - Enhanced with currency conversion patterns
        self.transfer_patterns = [
            # Currency conversion patterns (ENHANCED - more specific)
            r"converted\s+[\d,.]+\s+\w{3}\s+(from\s+\w{3}\s+balance\s+)?to\s+[\d,.]+\s*\w{3}",  # "Converted 565.24 USD to 200,000.00 HUF" or "from USD balance to"
            r"converted\s+[\d,.]+\s+\w{3}",  # "Converted 565.24 USD"
            r"balance\s+after\s+converting",  # "Balance after converting"
            r"exchange\s+from\s+\w{3}\s+to\s+\w{3}",  # "Exchange from USD to HUF"
            
            # User-specific patterns
            rf"sent\s+(money\s+)?to\s+{re.escape(user_name.lower())}",  # "Sent money to Ammar Qazi", "Sent to Ammar Qazi"
            rf"transfer\s+to\s+{re.escape(user_name.lower())}",  # "Transfer to Ammar Qazi"
            rf"transfer\s+from\s+{re.escape(user_name.lower())}",  # "Transfer from Ammar Qazi"
            rf"incoming\s+fund\s+transfer\s+from\s+{re.escape(user_name.lower())}",  # "Incoming fund transfer from Ammar Qazi"
            
            # Generic transfer patterns
            r"transfer\s+to\s+\w+",  # "Transfer to account"
            r"transfer\s+from\s+\w+",  # "Transfer from account"
            r"incoming\s+fund\s+transfer",  # NayaPay pattern
            r"fund\s+transfer\s+from",  # Bank Alfalah pattern
        ]
    
    def detect_transfers(self, csv_data_list: List[Dict]) -> Dict[str, Any]:
        """
        Main transfer detection function with ENHANCED currency conversion matching
        """
        
        print("\n🔍 STARTING ENHANCED CURRENCY CONVERSION DETECTION")
        print("=" * 70)
        
        # Flatten all transactions with source info
        all_transactions = []
        for csv_idx, csv_data in enumerate(csv_data_list):
            print(f"\n📁 Processing CSV {csv_idx}: {csv_data.get('file_name', f'CSV_{csv_idx}')}")
            print(f"   📊 Transaction count: {len(csv_data['data'])}")
            
            for trans_idx, transaction in enumerate(csv_data['data']):
                enhanced_transaction = {
                    **transaction,
                    '_csv_index': csv_idx,
                    '_transaction_index': trans_idx,
                    '_csv_name': csv_data.get('file_name', f'CSV_{csv_idx}'),
                    '_template_config': csv_data.get('template_config', {}),
                    '_bank_type': self._detect_bank_type(csv_data.get('file_name', ''), transaction),
                    '_raw_data': transaction  # Keep original data for exchange amount extraction
                }
                all_transactions.append(enhanced_transaction)
                
                # Log sample transactions
                if trans_idx < 2:
                    amount = self._parse_amount(transaction.get('Amount', '0'))
                    desc = str(transaction.get('Description', ''))[:60]
                    date = transaction.get('Date', '')
                    exchange_amount = self._get_exchange_amount(enhanced_transaction)
                    print(f"   🧾 Transaction {trans_idx}: Amount={amount}, Date={date}")
                    if exchange_amount:
                        print(f"      💱 Exchange Amount: {exchange_amount}")
                    print(f"      📝 Description: {desc}...")
        
        print(f"\n📊 TOTAL TRANSACTIONS LOADED: {len(all_transactions)}")
        
        # Detect potential transfers by description patterns
        print("\n🔍 FINDING TRANSFER CANDIDATES...")
        potential_transfers = self._find_transfer_candidates(all_transactions)
        print(f"   ✅ Found {len(potential_transfers)} potential transfer candidates")
        
        # ENHANCED: Special handling for currency conversions
        print("\n💱 ENHANCED CURRENCY CONVERSION MATCHING...")
        conversion_pairs = self._match_currency_conversions(all_transactions)
        print(f"   ✅ Found {len(conversion_pairs)} currency conversion pairs")
        
        # Match other types of transfers WITH EXCHANGE AMOUNT SUPPORT
        print("\n🔄 MATCHING OTHER TRANSFER TYPES (including exchange amounts)...")
        other_transfer_pairs = self._match_other_transfers(potential_transfers, all_transactions, conversion_pairs)
        print(f"   ✅ Found {len(other_transfer_pairs)} other transfer pairs")
        
        # Combine all transfer pairs
        all_transfer_pairs = conversion_pairs + other_transfer_pairs
        
        # Detect conflicts and flag manual review
        conflicts = self._detect_conflicts(all_transfer_pairs)
        flagged_transactions = self._flag_manual_review(all_transactions, all_transfer_pairs)
        
        print("\n📋 ENHANCED DETECTION SUMMARY:")
        print(f"   📊 Total transactions: {len(all_transactions)}")
        print(f"   🎯 Total transfer pairs: {len(all_transfer_pairs)}")
        print(f"   💱 Currency conversions: {len(conversion_pairs)}")
        print(f"   🔄 Other transfers: {len(other_transfer_pairs)}")
        print(f"   💭 Potential transfers: {len(potential_transfers)}")
        print(f"   ⚠️  Conflicts: {len(conflicts)}")
        print(f"   🚩 Flagged for review: {len(flagged_transactions)}")
        print("=" * 70)
        
        return {
            'transfers': all_transfer_pairs,
            'potential_transfers': potential_transfers,
            'conflicts': conflicts,
            'flagged_transactions': flagged_transactions,
            'summary': {
                'total_transactions': len(all_transactions),
                'transfer_pairs_found': len(all_transfer_pairs),
                'currency_conversions': len(conversion_pairs),
                'other_transfers': len(other_transfer_pairs),
                'potential_transfers': len(potential_transfers),
                'conflicts': len(conflicts),
                'flagged_for_review': len(flagged_transactions)
            }
        }
    
    def _get_exchange_amount(self, transaction: Dict) -> Optional[float]:
        """
        ENHANCED: Extract exchange amount from transaction data
        Looks for Exchange To Amount, Exchange Amount, or similar columns
        """
        # Common column names for exchange amounts in various bank CSV formats
        exchange_columns = [
            'Exchange To Amount',
            'Exchange Amount', 
            'Converted Amount',
            'Target Amount',
            'Exchange_To_Amount',
            'ExchangeToAmount',
            'exchange_to_amount'
        ]
        
        for col in exchange_columns:
            if col in transaction:
                exchange_value = transaction[col]
                if exchange_value and str(exchange_value).strip() not in ['', 'nan', 'NaN', 'null', 'None']:
                    try:
                        parsed_amount = self._parse_amount(str(exchange_value))
                        if parsed_amount != 0:
                            return abs(parsed_amount)  # Always return positive for matching
                    except (ValueError, TypeError):
                        continue
        
        return None
    
    def _match_other_transfers(self, potential_transfers: List[Dict], all_transactions: List[Dict], 
                              existing_pairs: List[Dict]) -> List[Dict]:
        """Match non-conversion transfers (cross-bank, etc.) INCLUDING exchange amount matching"""
        transfer_pairs = []
        existing_transaction_ids = set()
        
        # Get IDs of already matched transactions
        for pair in existing_pairs:
            existing_transaction_ids.add(pair['outgoing']['_transaction_index'])
            existing_transaction_ids.add(pair['incoming']['_transaction_index'])
        
        print(f"\n🔄 MATCHING OTHER TRANSFERS (including exchange amounts)...")
        print(f"   📊 Remaining potential transfers: {len([t for t in potential_transfers if t['_transaction_index'] not in existing_transaction_ids])}")
        
        # Match remaining potential transfers
        for idx, outgoing in enumerate(potential_transfers):
            if outgoing['_transaction_index'] in existing_transaction_ids:
                continue
                
            outgoing_amount = self._parse_amount(outgoing.get('Amount', '0'))
            
            # Skip if not negative (outgoing should be negative)
            if outgoing_amount >= 0:
                continue
            
            # ENHANCED: Get exchange amount if available (for Wise transactions)
            exchange_amount = self._get_exchange_amount(outgoing)
            
            print(f"\n   🔍 Processing outgoing transfer:")
            print(f"      💰 Main Amount: {outgoing_amount}")
            if exchange_amount:
                print(f"      💱 Exchange Amount: {exchange_amount}")
            print(f"      📝 Description: {str(outgoing.get('Description', ''))[:60]}...")
            
            # Look for cross-bank transfers
            for incoming in all_transactions:
                if (incoming['_transaction_index'] in existing_transaction_ids or
                    incoming['_csv_index'] == outgoing['_csv_index']):  # Different CSV only for cross-bank
                    continue
                
                incoming_amount = self._parse_amount(incoming.get('Amount', '0'))
                
                # Skip if not positive
                if incoming_amount <= 0:
                    continue
                
                # ENHANCED: Multiple matching strategies
                matches = []
                
                # Strategy 1: Traditional amount matching
                date_match = self._dates_within_tolerance(
                    self._parse_date(outgoing.get('Date', '')), 
                    self._parse_date(incoming.get('Date', ''))
                )
                traditional_amount_match = abs(abs(outgoing_amount) - incoming_amount) < 0.01
                
                # Strategy 2: ENHANCED - Exchange amount matching (for currency conversions)
                exchange_amount_match = False
                if exchange_amount:
                    exchange_amount_match = abs(exchange_amount - incoming_amount) < 0.01
                    if exchange_amount_match:
                        print(f"      ✅ EXCHANGE AMOUNT MATCH FOUND!")
                        print(f"         📤 Outgoing exchange: {exchange_amount}")
                        print(f"         📥 Incoming amount: {incoming_amount}")
                
                # Check if it's a cross-bank transfer with either matching strategy
                if self._is_cross_bank_transfer(outgoing, incoming) and date_match:
                    
                    if traditional_amount_match:
                        confidence = self._calculate_confidence(outgoing, incoming, is_cross_bank=True)
                        matches.append({
                            'type': 'traditional',
                            'confidence': confidence,
                            'matched_amount': abs(outgoing_amount)
                        })
                    
                    if exchange_amount_match:
                        # HIGHER confidence for exchange amount matches as they're more specific
                        confidence = self._calculate_confidence(outgoing, incoming, is_cross_bank=True, is_exchange_match=True)
                        matches.append({
                            'type': 'exchange_amount',
                            'confidence': confidence,
                            'matched_amount': exchange_amount
                        })
                
                # Choose the best match (highest confidence)
                if matches:
                    best_match = max(matches, key=lambda x: x['confidence'])
                    
                    transfer_pair = {
                        'outgoing': outgoing,
                        'incoming': incoming,
                        'amount': abs(outgoing_amount),
                        'matched_amount': best_match['matched_amount'],
                        'exchange_amount': exchange_amount if best_match['type'] == 'exchange_amount' else None,
                        'date': self._parse_date(outgoing.get('Date', '')),
                        'confidence': best_match['confidence'],
                        'pair_id': f"transfer_{len(transfer_pairs)}",
                        'transfer_type': f"cross_bank_{best_match['type']}",
                        'match_strategy': best_match['type']
                    }
                    
                    print(f"      ✅ TRANSFER PAIR MATCHED! Strategy: {best_match['type']}")
                    print(f"         📤 Outgoing: {outgoing['_csv_name']} | {outgoing_amount}")
                    print(f"         📥 Incoming: {incoming['_csv_name']} | {incoming_amount}")
                    print(f"         🎯 Confidence: {best_match['confidence']:.2f}")
                    print(f"         💰 Matched Amount: {best_match['matched_amount']}")
                    
                    transfer_pairs.append(transfer_pair)
                    existing_transaction_ids.add(outgoing['_transaction_index'])
                    existing_transaction_ids.add(incoming['_transaction_index'])
                    break
        
        print(f"\n   ✅ Found {len(transfer_pairs)} cross-bank transfer pairs")
        return transfer_pairs
    
    def _match_currency_conversions(self, all_transactions: List[Dict]) -> List[Dict]:
        """ENHANCED: Match currency conversions by extracting amounts and currencies from descriptions"""
        conversion_pairs = []
        matched_transactions = set()
        
        # Extract conversion information from descriptions
        conversion_candidates = []
        
        for transaction in all_transactions:
            if transaction['_transaction_index'] in matched_transactions:
                continue
                
            desc = str(transaction.get('Description', '')).lower()
            amount = self._parse_amount(transaction.get('Amount', '0'))
            date = self._parse_date(transaction.get('Date', ''))
            
            # Extract conversion details from description
            conversion_info = self._extract_conversion_info(desc, amount)
            
            if conversion_info:
                conversion_candidates.append({
                    **transaction,
                    '_conversion_info': conversion_info,
                    '_amount': amount,
                    '_date': date
                })
                
                print(f"\n💱 CONVERSION CANDIDATE: {transaction['_csv_name']}")
                print(f"   💰 Amount: {amount}")
                print(f"   📅 Date: {date.strftime('%Y-%m-%d')}")
                print(f"   📝 Description: {desc[:80]}...")
                print(f"   🔄 Conversion: {conversion_info['from_amount']} {conversion_info['from_currency']} → {conversion_info['to_amount']} {conversion_info['to_currency']}")
        
        print(f"\n🔍 MATCHING {len(conversion_candidates)} CONVERSION CANDIDATES...")
        
        # Match conversion pairs
        for i, candidate1 in enumerate(conversion_candidates):
            if candidate1['_transaction_index'] in matched_transactions:
                continue
                
            conv1 = candidate1['_conversion_info']
            
            # Look for matching conversion
            for j, candidate2 in enumerate(conversion_candidates):
                if (i >= j or 
                    candidate2['_transaction_index'] in matched_transactions or
                    candidate1['_csv_index'] == candidate2['_csv_index']):  # Must be different CSVs
                    continue
                
                conv2 = candidate2['_conversion_info']
                
                # Check if they represent the same conversion
                is_matching_conversion = self._is_matching_conversion(conv1, conv2, candidate1, candidate2)
                
                if is_matching_conversion:
                    # Determine which is outgoing/incoming based on amount sign
                    if candidate1['_amount'] < 0 and candidate2['_amount'] > 0:
                        outgoing, incoming = candidate1, candidate2
                    elif candidate1['_amount'] > 0 and candidate2['_amount'] < 0:
                        outgoing, incoming = candidate2, candidate1
                    else:
                        continue  # Both same sign, skip
                    
                    confidence = self._calculate_conversion_confidence(outgoing, incoming, conv1, conv2)
                    
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
                    
                    print(f"\n   ✅ CURRENCY CONVERSION MATCHED! Confidence: {confidence:.2f}")
                    print(f"      📤 Outgoing: {outgoing['_csv_name']} | {outgoing['_amount']} {conv1['from_currency']}")
                    print(f"      📥 Incoming: {incoming['_csv_name']} | {incoming['_amount']} {conv1['to_currency']}")
                    print(f"      🔄 Conversion: {conv1['from_amount']} {conv1['from_currency']} → {conv1['to_amount']} {conv1['to_currency']}")
                    
                    conversion_pairs.append(transfer_pair)
                    matched_transactions.add(outgoing['_transaction_index'])
                    matched_transactions.add(incoming['_transaction_index'])
                    break
        
        return conversion_pairs
    
    def _extract_conversion_info(self, description: str, amount: float) -> Optional[Dict]:
        """Extract currency conversion details from description"""
        
        # Pattern for "Converted X USD to Y EUR" or "Converted X USD from USD balance to Y EUR"
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
    
    def _is_matching_conversion(self, conv1: Dict, conv2: Dict, candidate1: Dict, candidate2: Dict) -> bool:
        """Check if two conversion records represent the same conversion"""
        
        # Same conversion amounts and currencies
        amounts_match = (
            abs(conv1['from_amount'] - conv2['from_amount']) < 0.01 and
            abs(conv1['to_amount'] - conv2['to_amount']) < 0.01 and
            conv1['from_currency'] == conv2['from_currency'] and
            conv1['to_currency'] == conv2['to_currency']
        )
        
        # Same date (within tolerance)
        date_match = self._dates_within_tolerance(candidate1['_date'], candidate2['_date'])
        
        # One should be negative (outgoing) and one positive (incoming)
        opposite_signs = (candidate1['_amount'] * candidate2['_amount']) < 0
        
        # Amount should match the conversion amounts
        amount1_matches = (
            abs(abs(candidate1['_amount']) - conv1['from_amount']) < 0.01 or
            abs(abs(candidate1['_amount']) - conv1['to_amount']) < 0.01
        )
        
        amount2_matches = (
            abs(abs(candidate2['_amount']) - conv2['from_amount']) < 0.01 or
            abs(abs(candidate2['_amount']) - conv2['to_amount']) < 0.01
        )
        
        return amounts_match and date_match and opposite_signs and amount1_matches and amount2_matches
    
    def _calculate_conversion_confidence(self, outgoing: Dict, incoming: Dict, conv1: Dict, conv2: Dict) -> float:
        """Calculate confidence for currency conversion matches"""
        confidence = 0.5  # Base confidence for conversions
        
        # Perfect amount match
        if (abs(abs(outgoing['_amount']) - conv1['from_amount']) < 0.01 and
            abs(abs(incoming['_amount']) - conv1['to_amount']) < 0.01):
            confidence += 0.3
        
        # Same date
        if outgoing['_date'].date() == incoming['_date'].date():
            confidence += 0.2
        
        # Both have conversion pattern in description
        if ('converted' in str(outgoing.get('Description', '')).lower() and
            'converted' in str(incoming.get('Description', '')).lower()):
            confidence += 0.2
        
        # Same conversion details
        if (conv1['from_amount'] == conv2['from_amount'] and
            conv1['to_amount'] == conv2['to_amount'] and
            conv1['from_currency'] == conv2['from_currency'] and
            conv1['to_currency'] == conv2['to_currency']):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    # Keep existing helper methods with minor updates
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
        
        if 'wise' in file_name_lower or 'transferwise' in file_name_lower:
            return 'wise'
        elif 'nayapay' in file_name_lower:
            return 'nayapay'
        elif 'bank alfalah' in file_name_lower:
            return 'bank_alfalah'
        else:
            return 'unknown'
    
    def _is_cross_bank_transfer(self, outgoing: Dict, incoming: Dict) -> bool:
        """Check if this is a cross-bank transfer (like Wise->NayaPay)"""
        outgoing_desc = str(outgoing.get('Description', '')).lower()
        incoming_desc = str(incoming.get('Description', '')).lower()
        
        # Wise->NayaPay pattern
        if (outgoing.get('_bank_type') == 'wise' and 
            incoming.get('_bank_type') in ['nayapay', 'bank_alfalah', 'pakistani_bank']):
            
            if ('sent money' in outgoing_desc and self.user_name.lower() in outgoing_desc):
                if ('incoming fund transfer' in incoming_desc and self.user_name.lower() in incoming_desc):
                    return True
        
        return False
    
    def _detect_conflicts(self, transfer_pairs: List[Dict]) -> List[Dict]:
        """Detect transactions that could match multiple partners"""
        return []  # Simplified for now
    
    def _flag_manual_review(self, all_transactions: List[Dict], transfer_pairs: List[Dict]) -> List[Dict]:
        """Flag transactions that need manual review"""
        return []  # Simplified for now
    
    def _calculate_confidence(self, outgoing: Dict, incoming: Dict, is_cross_bank: bool = False, is_exchange_match: bool = False) -> float:
        """Calculate confidence score for transfer pair matching"""
        confidence = 0.4  # Base confidence
        
        if is_cross_bank:
            confidence += 0.4
        
        # ENHANCED: Higher confidence for exchange amount matches
        if is_exchange_match:
            confidence += 0.3  # Exchange amount matches are very specific
        
        # Same day bonus
        outgoing_date = self._parse_date(outgoing.get('Date', ''))
        incoming_date = self._parse_date(incoming.get('Date', ''))
        if outgoing_date.date() == incoming_date.date():
            confidence += 0.2
        
        return min(confidence, 1.0)
    
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
    
    def apply_transfer_categorization(self, csv_data_list: List[Dict], transfer_pairs: List[Dict]) -> List[Dict]:
        """Apply Balance Correction category to detected transfers"""
        transfer_matches = []
        
        for pair in transfer_pairs:
            outgoing = pair['outgoing']
            incoming = pair['incoming']
            
            # Include exchange amount information in notes
            exchange_note = ""
            if pair.get('exchange_amount'):
                exchange_note = f" | Exchange Amount: {pair['exchange_amount']}"
            
            transfer_matches.append({
                'csv_index': outgoing['_csv_index'],
                'amount': str(self._parse_amount(outgoing.get('Amount', '0'))),
                'date': self._parse_date(outgoing.get('Date', '')).strftime('%Y-%m-%d'),
                'description': str(outgoing.get('Description', '')),
                'category': 'Balance Correction',
                'note': f"Transfer out - {pair['transfer_type']} - Pair ID: {pair['pair_id']}{exchange_note}",
                'pair_id': pair['pair_id'],
                'transfer_type': 'outgoing',
                'match_strategy': pair.get('match_strategy', 'traditional')
            })
            
            transfer_matches.append({
                'csv_index': incoming['_csv_index'],
                'amount': str(self._parse_amount(incoming.get('Amount', '0'))),
                'date': self._parse_date(incoming.get('Date', '')).strftime('%Y-%m-%d'),
                'description': str(incoming.get('Description', '')),
                'category': 'Balance Correction',
                'note': f"Transfer in - {pair['transfer_type']} - Pair ID: {pair['pair_id']}{exchange_note}",
                'pair_id': pair['pair_id'],
                'transfer_type': 'incoming',
                'match_strategy': pair.get('match_strategy', 'traditional')
            })
        
        return transfer_matches
