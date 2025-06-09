from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from datetime import datetime, timedelta
import re

class TransferDetector:
    """
    Enhanced transfer detection system for multi-CSV processing
    Identifies matching transfer transactions across multiple CSV files
    ENHANCED: Better currency conversion detection
    """
    
    def __init__(self, user_name: str = "Ammar Qazi", date_tolerance_hours: int = 24):
        self.user_name = user_name
        self.date_tolerance_hours = date_tolerance_hours
        
        # Transfer description patterns - Enhanced with currency conversion patterns
        self.transfer_patterns = [
            # Currency conversion patterns (NEW - highest priority)
            r"converted\s+[\d,.]+\s+\w{3}\s+to\s+[\d,.]+\s+\w{3}",  # "Converted 565.24 USD to 200,000.00 HUF"
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
        
        print("\n🔍 STARTING ENHANCED TRANSFER DETECTION")
        print("=" * 60)
        
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
                
                # Log first few transactions for debugging
                if trans_idx < 3:
                    amount = self._parse_amount(transaction.get('Amount', '0'))
                    desc = str(transaction.get('Description', ''))[:50]
                    date = transaction.get('Date', '')
                    bank_type = enhanced_transaction['_bank_type']
                    print(f"   🧾 Transaction {trans_idx}: Amount={amount}, Date={date}, Bank={bank_type}")
                    print(f"      📝 Description: {desc}...")
        
        print(f"\n📊 TOTAL TRANSACTIONS LOADED: {len(all_transactions)}")
        
        # Detect potential transfers by description patterns
        print("\n🔍 FINDING TRANSFER CANDIDATES...")
        potential_transfers = self._find_transfer_candidates(all_transactions)
        print(f"   ✅ Found {len(potential_transfers)} potential transfer candidates")
        
        # Match transfers by amount and date
        print("\n🔄 MATCHING TRANSFER PAIRS...")
        transfer_pairs = self._match_transfer_pairs(potential_transfers, all_transactions)
        print(f"   ✅ Found {len(transfer_pairs)} confirmed transfer pairs")
        
        # Detect conflicts (multiple potential matches)
        conflicts = self._detect_conflicts(transfer_pairs)
        
        # Flag transactions needing manual review
        flagged_transactions = self._flag_manual_review(all_transactions, transfer_pairs)
        
        print("\n📋 ENHANCED TRANSFER DETECTION SUMMARY:")
        print(f"   📊 Total transactions: {len(all_transactions)}")
        print(f"   🎯 Transfer pairs found: {len(transfer_pairs)}")
        print(f"   💭 Potential transfers: {len(potential_transfers)}")
        print(f"   ⚠️  Conflicts: {len(conflicts)}")
        print(f"   🚩 Flagged for review: {len(flagged_transactions)}")
        print("=" * 60)
        
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
        
        print("\n🔍 ANALYZING TRANSACTIONS FOR TRANSFER PATTERNS")
        print(f"   📋 Available patterns: {len(self.transfer_patterns)}")
        
        for i, transaction in enumerate(transactions):
            description = str(transaction.get('Description', '')).lower()
            amount = self._parse_amount(transaction.get('Amount', '0'))
            bank_type = transaction.get('_bank_type', 'unknown')
            csv_name = transaction.get('_csv_name', 'unknown')
            
            # Check against transfer patterns
            matched_pattern = None
            for pattern_idx, pattern in enumerate(self.transfer_patterns):
                if re.search(pattern, description, re.IGNORECASE):
                    matched_pattern = pattern
                    candidates.append({
                        **transaction,
                        '_transfer_pattern': pattern,
                        '_is_transfer_candidate': True
                    })
                    print(f"   ✅ CANDIDATE {len(candidates)}: {csv_name} | Amount={amount} | Bank={bank_type}")
                    print(f"      📝 Description: {description[:80]}...")
                    print(f"      🎯 Matched Pattern {pattern_idx+1}: {pattern}")
                    break
            
            # Log interesting transactions that didn't match
            if not matched_pattern and ('transfer' in description or 'sent' in description or 'incoming' in description or 'converted' in description):
                print(f"   ❌ NO MATCH: {csv_name} | Amount={amount} | Bank={bank_type}")
                print(f"      📝 Description: {description[:80]}...")
        
        print(f"\n📊 TRANSFER CANDIDATE SUMMARY:")
        print(f"   ✅ Total candidates found: {len(candidates)}")
        
        # Group by bank type
        by_bank = {}
        for candidate in candidates:
            bank = candidate.get('_bank_type', 'unknown')
            if bank not in by_bank:
                by_bank[bank] = []
            by_bank[bank].append(candidate)
        
        for bank, bank_candidates in by_bank.items():
            print(f"   🏦 {bank}: {len(bank_candidates)} candidates")
        
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
        """Match outgoing and incoming transfers by amount and date - ENHANCED for currency conversions"""
        transfer_pairs = []
        matched_transactions = set()
        
        print("\n🔄 STARTING ENHANCED TRANSFER PAIR MATCHING")
        print(f"   📊 Potential transfers to analyze: {len(potential_transfers)}")
        print(f"   📊 Total transactions to search: {len(all_transactions)}")
        
        # Enhanced matching: Check all potential transfers against all transactions
        for idx, candidate in enumerate(potential_transfers):
            if candidate['_transaction_index'] in matched_transactions:
                continue
                
            candidate_amount = self._parse_amount(candidate.get('Amount', '0'))
            candidate_date = self._parse_date(candidate.get('Date', ''))
            candidate_desc = str(candidate.get('Description', ''))[:50]
            candidate_bank = candidate.get('_bank_type', 'unknown')
            
            print(f"\n🔍 ANALYZING CANDIDATE #{idx+1}: {candidate.get('_csv_name', 'unknown')}")
            print(f"   💰 Amount: {candidate_amount}")
            print(f"   📅 Date: {candidate_date.strftime('%Y-%m-%d')}")
            print(f"   🏦 Bank: {candidate_bank}")
            print(f"   📝 Description: {candidate_desc}...")
            
            # Look for matching transaction
            potential_matches = []
            for other in all_transactions:
                if (other['_transaction_index'] in matched_transactions or
                    other['_transaction_index'] == candidate['_transaction_index']):
                    continue
                
                other_amount = self._parse_amount(other.get('Amount', '0'))
                other_date = self._parse_date(other.get('Date', ''))
                other_desc = str(other.get('Description', ''))[:50]
                other_bank = other.get('_bank_type', 'unknown')
                
                # Check if this is an internal conversion (same CSV)
                internal_conversion = (candidate['_csv_index'] == other['_csv_index'] and 
                                     self._is_internal_conversion(candidate, other))
                
                # Check if this is a cross-bank transfer (different CSV)
                cross_bank_match = (candidate['_csv_index'] != other['_csv_index'] and
                                   self._is_cross_bank_transfer(candidate, other))
                
                # Skip if not internal conversion and same CSV
                if (candidate['_csv_index'] == other['_csv_index'] and not internal_conversion):
                    continue
                
                # Check date proximity
                date_match = self._dates_within_tolerance(candidate_date, other_date)
                date_diff_hours = abs((candidate_date - other_date).total_seconds() / 3600)
                
                # Check amount matching
                amount_match = False
                amount_diff = 0
                
                if internal_conversion:
                    # For internal conversions, amounts might be exact opposites
                    amount_diff = abs(abs(candidate_amount) - abs(other_amount))
                    amount_match = amount_diff < 0.01
                elif cross_bank_match:
                    # For cross-bank, use exchange amounts if available
                    candidate_exchange = self._parse_amount(candidate.get('Exchange To Amount', '0'))
                    other_exchange = self._parse_amount(other.get('Exchange To Amount', '0'))
                    
                    if candidate_exchange > 0:
                        amount_diff = abs(candidate_exchange - abs(other_amount))
                    elif other_exchange > 0:
                        amount_diff = abs(other_exchange - abs(candidate_amount))
                    else:
                        amount_diff = abs(abs(candidate_amount) - abs(other_amount))
                    
                    amount_match = amount_diff < 0.01
                else:
                    # Regular amount matching
                    amount_diff = abs(abs(candidate_amount) - abs(other_amount))
                    amount_match = amount_diff < 0.01
                
                # Log potential matches for debugging
                if internal_conversion or cross_bank_match or (amount_match and date_match):
                    potential_matches.append({
                        'other': other,
                        'amount_match': amount_match,
                        'date_match': date_match,
                        'internal_conversion': internal_conversion,
                        'cross_bank_match': cross_bank_match,
                        'amount_diff': amount_diff,
                        'date_diff_hours': date_diff_hours
                    })
                
                # Enhanced matching conditions
                should_match = False
                match_type = 'standard'
                
                if internal_conversion and date_match:
                    should_match = True
                    match_type = 'internal_conversion'
                elif cross_bank_match and amount_match and date_match:
                    should_match = True
                    match_type = 'cross_bank'
                elif amount_match and date_match and candidate['_csv_index'] != other['_csv_index']:
                    should_match = True
                    match_type = 'standard'
                
                if should_match:
                    # Determine which is outgoing/incoming
                    if candidate_amount < 0 and other_amount > 0:
                        outgoing, incoming = candidate, other
                    elif candidate_amount > 0 and other_amount < 0:
                        outgoing, incoming = other, candidate
                    else:
                        continue  # Both same sign, skip
                    
                    confidence = self._calculate_confidence(outgoing, incoming, 
                                                          is_internal_conversion=(match_type == 'internal_conversion'),
                                                          is_cross_bank=(match_type == 'cross_bank'))
                    
                    transfer_pair = {
                        'outgoing': outgoing,
                        'incoming': incoming,
                        'amount': abs(self._parse_amount(outgoing.get('Amount', '0'))),
                        'exchange_amount': self._parse_amount(outgoing.get('Exchange To Amount', '0')) or None,
                        'date': self._parse_date(outgoing.get('Date', '')),
                        'confidence': confidence,
                        'pair_id': f"transfer_{len(transfer_pairs)}",
                        'transfer_type': match_type
                    }
                    
                    print(f"   ✅ {match_type.upper().replace('_', ' ')} MATCH FOUND! Confidence: {confidence:.2f}")
                    print(f"      📤 Outgoing: {outgoing.get('Amount')} {outgoing.get('Currency', 'N/A')}")
                    print(f"      📥 Incoming: {incoming.get('Amount')} {incoming.get('Currency', 'N/A')}")
                    print(f"      🏦 Banks: {outgoing.get('_bank_type')} → {incoming.get('_bank_type')}")
                    
                    transfer_pairs.append(transfer_pair)
                    matched_transactions.add(outgoing['_transaction_index'])
                    matched_transactions.add(incoming['_transaction_index'])
                    break
            
            # Log potential matches that didn't make it
            if len(potential_matches) > 0 and candidate['_transaction_index'] not in matched_transactions:
                print(f"   💭 Found {len(potential_matches)} potential matches but none confirmed:")
                for i, match in enumerate(potential_matches[:3]):  # Show top 3
                    other = match['other']
                    print(f"      🤔 Match {i+1}: Amount={self._parse_amount(other.get('Amount', '0'))} ")
                    print(f"         Amount✓={match['amount_match']} Date✓={match['date_match']} Internal✓={match['internal_conversion']} CrossBank✓={match['cross_bank_match']}")
                    print(f"         AmountDiff={match['amount_diff']:.2f} DateDiff={match['date_diff_hours']:.1f}h")
            elif len(potential_matches) == 0:
                print(f"   ❌ NO POTENTIAL MATCHES FOUND")
        
        print(f"\n📊 ENHANCED PAIR MATCHING COMPLETE:")
        print(f"   ✅ Successfully matched pairs: {len(transfer_pairs)}")
        
        for i, pair in enumerate(transfer_pairs):
            transfer_type = pair.get('transfer_type', 'standard')
            print(f"   🎯 Pair {i+1} [{transfer_type.upper()}]: {pair['outgoing']['_csv_name']} → {pair['incoming']['_csv_name']}")
            print(f"      💰 Amount: {pair['amount']} | Exchange: {pair.get('exchange_amount', 'N/A')}")
            print(f"      🎖️  Confidence: {pair['confidence']:.2f}")
        
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
    
    def _is_internal_conversion(self, transaction1: Dict, transaction2: Dict) -> bool:
        """Check if this is an internal currency conversion (same bank, different currencies)"""
        desc1 = str(transaction1.get('Description', '')).lower()
        desc2 = str(transaction2.get('Description', '')).lower()
        
        # Both transactions should be from same bank type (usually Wise)
        if transaction1.get('_bank_type') != transaction2.get('_bank_type'):
            return False
            
        # Enhanced currency conversion detection
        conversion_patterns = [
            # Exact match conversions (same description)
            lambda: desc1 == desc2 and 'converted' in desc1,
            
            # Both contain "converted" keyword
            lambda: 'converted' in desc1 and 'converted' in desc2,
            
            # Exchange patterns with amounts
            lambda: (transaction1.get('Exchange To Amount', '0') != '0' and 
                    'converted' in desc1),
            
            # Balance adjustment after conversion
            lambda: ('converted' in desc1 and 
                    ('balance' in desc2 or 'converted' in desc2)),
            
            # Same-date opposite amounts with conversion keywords
            lambda: (transaction1.get('Date') == transaction2.get('Date') and
                    ('exchange' in desc1 or 'exchange' in desc2 or 'converted' in desc1 or 'converted' in desc2)),
                    
            # Currency codes in descriptions (USD, EUR, HUF, etc.)
            lambda: (any(curr in desc1 for curr in ['usd', 'eur', 'huf', 'gbp']) and
                    any(curr in desc2 for curr in ['usd', 'eur', 'huf', 'gbp'])),
        ]
        
        # Test each pattern
        for pattern in conversion_patterns:
            try:
                if pattern():
                    return True
            except Exception:
                continue
                
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
    
    def _calculate_confidence(self, outgoing: Dict, incoming: Dict, is_internal_conversion: bool = False, is_cross_bank: bool = False) -> float:
        """Calculate confidence score for transfer pair matching"""
        confidence = 0.0
        
        # Base confidence for amount and date match
        confidence += 0.3
        
        # Higher confidence for internal conversions (currency exchanges)
        if is_internal_conversion:
            confidence += 0.5  # Very high confidence for internal conversions
            
            # Extra bonus for exact description match
            outgoing_desc = str(outgoing.get('Description', '')).lower()
            incoming_desc = str(incoming.get('Description', '')).lower()
            if outgoing_desc == incoming_desc:
                confidence += 0.2
        
        # Higher confidence for cross-bank transfers (Wise->NayaPay)
        elif is_cross_bank:
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
            
        # Bonus for conversion-specific keywords
        if is_internal_conversion:
            outgoing_desc = str(outgoing.get('Description', '')).lower()
            if any(keyword in outgoing_desc for keyword in ['converted', 'exchange', 'balance after']):
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
                'note': f"Transfer out - Pair ID: {pair['pair_id']} - Type: {pair.get('transfer_type', 'standard')}",
                'pair_id': pair['pair_id'],
                'transfer_type': 'outgoing'
            })
            
            transfer_matches.append({
                'csv_index': incoming['_csv_index'],
                'amount': str(self._parse_amount(incoming.get('Amount', '0'))),
                'date': self._parse_date(incoming.get('Date', '')).strftime('%Y-%m-%d'),
                'description': str(incoming.get('Description', '')),
                'category': 'Balance Correction',
                'note': f"Transfer in - Pair ID: {pair['pair_id']} - Type: {pair.get('transfer_type', 'standard')}",
                'pair_id': pair['pair_id'],
                'transfer_type': 'incoming'
            })
        
        return transfer_matches
