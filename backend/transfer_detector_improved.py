from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from datetime import datetime, timedelta
import re

class ImprovedTransferDetector:
    """
    Enhanced transfer detection system with better person-to-person matching
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
            r"sent\s+(money\s+)?to\s+[\w\s]+",  # "Sent money to [anyone]"
            r"transfer\s+to\s+[\w\s]+",  # "Transfer to [anyone]"
            r"transfer\s+from\s+[\w\s]+",  # "Transfer from [anyone]"
            r"incoming\s+fund\s+transfer\s+from\s+[\w\s]+",  # "Incoming fund transfer from [anyone]"
            r"outgoing\s+fund\s+transfer\s+to\s+[\w\s]+",  # "Outgoing fund transfer to [anyone]"
            r"fund\s+transfer\s+from",  # Bank Alfalah pattern
        ]
    
    def detect_transfers(self, csv_data_list: List[Dict]) -> Dict[str, Any]:
        """
        Main transfer detection function with ENHANCED person-to-person matching
        """
        
        print("\n🔍 STARTING IMPROVED TRANSFER DETECTION")
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
                    '_bank_type': self._detect_bank_type(csv_data.get('file_name', ''), transaction)
                }
                all_transactions.append(enhanced_transaction)
                
                # Log sample transactions
                if trans_idx < 2:
                    amount = self._parse_amount(transaction.get('Amount', '0'))
                    desc = str(transaction.get('Description', ''))[:60]
                    date = transaction.get('Date', '')
                    print(f"   🧾 Transaction {trans_idx}: Amount={amount}, Date={date}")
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
        
        # NEW: Enhanced person-to-person transfer matching
        print("\n👥 IMPROVED PERSON-TO-PERSON TRANSFER MATCHING...")
        person_transfer_pairs = self._match_person_to_person_transfers(potential_transfers, all_transactions, conversion_pairs)
        print(f"   ✅ Found {len(person_transfer_pairs)} person-to-person transfer pairs")
        
        # Combine all transfer pairs
        all_transfer_pairs = conversion_pairs + person_transfer_pairs
        
        # Detect conflicts and flag manual review
        conflicts = self._detect_conflicts(all_transfer_pairs)
        flagged_transactions = self._flag_manual_review(all_transactions, all_transfer_pairs)
        
        print("\n📋 IMPROVED DETECTION SUMMARY:")
        print(f"   📊 Total transactions: {len(all_transactions)}")
        print(f"   🎯 Total transfer pairs: {len(all_transfer_pairs)}")
        print(f"   💱 Currency conversions: {len(conversion_pairs)}")
        print(f"   👥 Person-to-person transfers: {len(person_transfer_pairs)}")
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
                'person_to_person_transfers': len(person_transfer_pairs),
                'potential_transfers': len(potential_transfers),
                'conflicts': len(conflicts),
                'flagged_for_review': len(flagged_transactions)
            }
        }
    
    def _match_person_to_person_transfers(self, potential_transfers: List[Dict], all_transactions: List[Dict], 
                                         existing_pairs: List[Dict]) -> List[Dict]:
        """Enhanced person-to-person transfer matching"""
        transfer_pairs = []
        existing_transaction_ids = set()
        
        # Get IDs of already matched transactions
        for pair in existing_pairs:
            existing_transaction_ids.add(pair['outgoing']['_transaction_index'])
            existing_transaction_ids.add(pair['incoming']['_transaction_index'])
        
        # Match remaining potential transfers
        for idx, outgoing_candidate in enumerate(potential_transfers):
            if outgoing_candidate['_transaction_index'] in existing_transaction_ids:
                continue
                
            outgoing_amount = self._parse_amount(outgoing_candidate.get('Amount', '0'))
            
            # Skip if not negative (outgoing should be negative)
            if outgoing_amount >= 0:
                continue
            
            # Extract person name from outgoing transaction
            recipient_name = self._extract_person_name_from_outgoing(outgoing_candidate)
            if not recipient_name:
                continue
            
            print(f"\n💸 OUTGOING TRANSFER CANDIDATE:")
            print(f"   💰 Amount: {outgoing_amount}")
            print(f"   📅 Date: {self._parse_date(outgoing_candidate.get('Date', '')).strftime('%Y-%m-%d')}")
            print(f"   👤 Recipient: {recipient_name}")
            print(f"   📝 Description: {str(outgoing_candidate.get('Description', ''))[:80]}...")
            
            # Look for matching incoming transfers from the same person
            for incoming_candidate in all_transactions:
                if (incoming_candidate['_transaction_index'] in existing_transaction_ids or
                    incoming_candidate['_csv_index'] == outgoing_candidate['_csv_index']):  # Different CSV only
                    continue
                
                incoming_amount = self._parse_amount(incoming_candidate.get('Amount', '0'))
                
                # Skip if not positive
                if incoming_amount <= 0:
                    continue
                
                # Extract person name from incoming transaction
                sender_name = self._extract_person_name_from_incoming(incoming_candidate)
                if not sender_name:
                    continue
                
                # Check if names match (allowing for variations)
                if not self._names_match(recipient_name, sender_name):
                    continue
                
                outgoing_date = self._parse_date(outgoing_candidate.get('Date', ''))
                incoming_date = self._parse_date(incoming_candidate.get('Date', ''))
                
                # Check date and amount matching
                date_match = self._dates_within_tolerance(outgoing_date, incoming_date)
                amount_match = abs(abs(outgoing_amount) - incoming_amount) < 0.01
                
                print(f"\n   💰 INCOMING TRANSFER CANDIDATE:")
                print(f"      💰 Amount: {incoming_amount}")
                print(f"      📅 Date: {incoming_date.strftime('%Y-%m-%d')}")
                print(f"      👤 Sender: {sender_name}")
                print(f"      📝 Description: {str(incoming_candidate.get('Description', ''))[:80]}...")
                print(f"      🔍 Names match: {self._names_match(recipient_name, sender_name)}")
                print(f"      📅 Date match: {date_match}")
                print(f"      💰 Amount match: {amount_match}")
                
                if date_match and amount_match:
                    confidence = self._calculate_person_transfer_confidence(outgoing_candidate, incoming_candidate, recipient_name, sender_name)
                    
                    transfer_pair = {
                        'outgoing': outgoing_candidate,
                        'incoming': incoming_candidate,
                        'amount': abs(outgoing_amount),
                        'date': outgoing_date,
                        'confidence': confidence,
                        'pair_id': f"transfer_{len(transfer_pairs)}",
                        'transfer_type': 'person_to_person',
                        'person_name': recipient_name
                    }
                    
                    print(f"\n   ✅ PERSON-TO-PERSON TRANSFER MATCHED! Confidence: {confidence:.2f}")
                    print(f"      📤 Outgoing: {outgoing_candidate['_csv_name']} | {outgoing_amount}")
                    print(f"      📥 Incoming: {incoming_candidate['_csv_name']} | {incoming_amount}")
                    print(f"      👤 Person: {recipient_name}")
                    
                    transfer_pairs.append(transfer_pair)
                    existing_transaction_ids.add(outgoing_candidate['_transaction_index'])
                    existing_transaction_ids.add(incoming_candidate['_transaction_index'])
                    break
        
        return transfer_pairs
    
    def _extract_person_name_from_outgoing(self, transaction: Dict) -> Optional[str]:
        """Extract person name from outgoing transaction description"""
        desc = str(transaction.get('Description', '')).lower()
        
        # Patterns for outgoing transfers
        patterns = [
            r"sent\s+money\s+to\s+([\w\s]+?)(?:\s|$|\.|,)",  # "Sent money to Ammar Qazi"
            r"transfer\s+to\s+([\w\s]+?)(?:\s|$|\.|,)",  # "Transfer to Ammar Qazi"
            r"outgoing\s+fund\s+transfer\s+to\s+([\w\s]+?)(?:\s|$|\.|,)",  # "Outgoing fund transfer to Ammar Qazi"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, desc, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up common suffixes
                name = re.sub(r'\s+(bank|ltd|llc|inc|corp).*$', '', name, flags=re.IGNORECASE)
                name = re.sub(r'\s+\([^)]+\).*$', '', name)  # Remove parentheses content
                name = re.sub(r'\s+\|.*$', '', name)  # Remove pipe content
                if len(name) > 2:  # Must be at least 3 characters
                    return name.title()
        
        return None
    
    def _extract_person_name_from_incoming(self, transaction: Dict) -> Optional[str]:
        """Extract person name from incoming transaction description"""
        desc = str(transaction.get('Description', '')).lower()
        
        # Patterns for incoming transfers
        patterns = [
            r"incoming\s+fund\s+transfer\s+from\s+([\w\s]+?)(?:\s|$|\.|,)",  # "Incoming fund transfer from Ammar Qazi"
            r"received\s+money\s+from\s+([\w\s]+?)(?:\s|$|\.|,)",  # "Received money from Ammar Qazi"
            r"transfer\s+from\s+([\w\s]+?)(?:\s|$|\.|,)",  # "Transfer from Ammar Qazi"
            r"fund\s+transfer\s+from\s+([\w\s]+?)(?:\s|$|\.|,)",  # "Fund transfer from Ammar Qazi"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, desc, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up common suffixes
                name = re.sub(r'\s+(bank|ltd|llc|inc|corp).*$', '', name, flags=re.IGNORECASE)
                name = re.sub(r'\s+\([^)]+\).*$', '', name)  # Remove parentheses content
                name = re.sub(r'\s+\|.*$', '', name)  # Remove pipe content
                if len(name) > 2:  # Must be at least 3 characters
                    return name.title()
        
        return None
    
    def _names_match(self, name1: str, name2: str) -> bool:
        """Check if two names match, allowing for variations"""
        if not name1 or not name2:
            return False
        
        name1_clean = name1.lower().strip()
        name2_clean = name2.lower().strip()
        
        # Exact match
        if name1_clean == name2_clean:
            return True
        
        # Split into parts and check if all parts of shorter name are in longer name
        parts1 = name1_clean.split()
        parts2 = name2_clean.split()
        
        # If one name is subset of another
        if len(parts1) <= len(parts2):
            return all(part in parts2 for part in parts1)
        else:
            return all(part in parts1 for part in parts2)
    
    def _calculate_person_transfer_confidence(self, outgoing: Dict, incoming: Dict, 
                                            recipient_name: str, sender_name: str) -> float:
        """Calculate confidence for person-to-person transfer matches"""
        confidence = 0.5  # Base confidence
        
        # Exact name match
        if recipient_name.lower() == sender_name.lower():
            confidence += 0.3
        elif self._names_match(recipient_name, sender_name):
            confidence += 0.2
        
        # Same day bonus
        outgoing_date = self._parse_date(outgoing.get('Date', ''))
        incoming_date = self._parse_date(incoming.get('Date', ''))
        if outgoing_date.date() == incoming_date.date():
            confidence += 0.2
        
        # Same amount bonus
        outgoing_amount = abs(self._parse_amount(outgoing.get('Amount', '0')))
        incoming_amount = self._parse_amount(incoming.get('Amount', '0'))
        if abs(outgoing_amount - incoming_amount) < 0.01:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    # Copy existing methods from original detector with minor improvements
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
    
    # Keep existing helper methods
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
    
    def _detect_conflicts(self, transfer_pairs: List[Dict]) -> List[Dict]:
        """Detect transactions that could match multiple partners"""
        return []  # Simplified for now
    
    def _flag_manual_review(self, all_transactions: List[Dict], transfer_pairs: List[Dict]) -> List[Dict]:
        """Flag transactions that need manual review"""
        return []  # Simplified for now
    
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
            
            transfer_matches.append({
                'csv_index': outgoing['_csv_index'],
                'amount': str(self._parse_amount(outgoing.get('Amount', '0'))),
                'date': self._parse_date(outgoing.get('Date', '')).strftime('%Y-%m-%d'),
                'description': str(outgoing.get('Description', '')),
                'category': 'Balance Correction',
                'note': f"Transfer out - {pair['transfer_type']} - Pair ID: {pair['pair_id']}",
                'pair_id': pair['pair_id'],
                'transfer_type': 'outgoing'
            })
            
            transfer_matches.append({
                'csv_index': incoming['_csv_index'],
                'amount': str(self._parse_amount(incoming.get('Amount', '0'))),
                'date': self._parse_date(incoming.get('Date', '')).strftime('%Y-%m-%d'),
                'description': str(incoming.get('Description', '')),
                'category': 'Balance Correction',
                'note': f"Transfer in - {pair['transfer_type']} - Pair ID: {pair['pair_id']}",
                'pair_id': pair['pair_id'],
                'transfer_type': 'incoming'
            })
        
        return transfer_matches
