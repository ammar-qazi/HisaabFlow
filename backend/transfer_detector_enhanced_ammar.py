from typing import Dict, List, Optional, Any, Tuple
# import pandas as pd  # Not needed for basic functionality
from datetime import datetime, timedelta
import re

class TransferDetector:
    """
    Enhanced transfer detection system with Ammar's specifications:
    1. Exchange To Amount matching for currency conversions
    2. Ammar name-based cross-bank transfers (Sent money to Ammar <-> Incoming from Ammar)
    3. Currency-based bank targeting (PKR for Pakistani banks, EUR for European accounts)
    4. 24-hour date tolerance with fallback to traditional amount matching
    """
    
    def __init__(self, user_name: str = "Ammar Qazi", date_tolerance_hours: int = 72):
        self.user_name = user_name
        self.date_tolerance_hours = date_tolerance_hours
        
        # Transfer description patterns
        self.transfer_patterns = [
            # Currency conversion patterns
            r"converted\s+[\d,.]+\s+\w{3}\s+(from\s+\w{3}\s+balance\s+)?to\s+[\d,.]+\s*\w{3}",
            r"converted\s+[\d,.]+\s+\w{3}",
            r"balance\s+after\s+converting",
            r"exchange\s+from\s+\w{3}\s+to\s+\w{3}",
            
            # User-specific patterns - AMMAR SPECIFICATIONS
            rf"sent\s+(money\s+)?to\s+{re.escape(user_name.lower())}",  # "Sent money to Ammar Qazi"
            rf"transfer\s+to\s+{re.escape(user_name.lower())}",  # "Transfer to Ammar Qazi"
            rf"transfer\s+from\s+{re.escape(user_name.lower())}",  # "Transfer from Ammar Qazi"
            rf"incoming.*transfer\s+from\s+{re.escape(user_name.lower())}",  # "Incoming fund transfer from Ammar Qazi"

            # Generic transfer patterns
            r"transfer\s+to\s+\w+",
            r"transfer\s+from\s+\w+",
            r"incoming\s+fund\s+transfer",
            r"fund\s+transfer\s+from",
        ]
    
    def detect_transfers(self, csv_data_list: List[Dict]) -> Dict[str, Any]:
        """Main transfer detection function with Ammar's specifications"""
        
        print("\n🔍 STARTING ENHANCED TRANSFER DETECTION (AMMAR SPECS)")
        print("=" * 70)
        
        # Flatten all transactions with source info
        all_transactions = []
        for csv_idx, csv_data in enumerate(csv_data_list):
            print(f"\n📁 Processing CSV {csv_idx}: {csv_data.get('file_name', f'CSV_{csv_idx}')}")
            print(f"   📊 Transaction count: {len(csv_data['data'])}")
            
            # DEBUG: Check CSV data structure
            if csv_data['data']:
                sample_transaction = csv_data['data'][0]
                print(f"   🔍 Available columns: {list(sample_transaction.keys())}")
                # if 'nayapay' in csv_data.get('file_name', '').lower():
                #     print(f"   🐛 DEBUG NayaPay sample transaction: {sample_transaction}")
            
            for trans_idx, transaction in enumerate(csv_data['data']):
                enhanced_transaction = {
                    **transaction,
                    '_csv_index': csv_idx,
                    '_transaction_index': trans_idx,
                    '_csv_name': csv_data.get('file_name', f'CSV_{csv_idx}'),
                    '_template_config': csv_data.get('template_config', {}),
                    '_bank_type': self._detect_bank_type(csv_data.get('file_name', ''), transaction),
                    '_raw_data': transaction
                }
                all_transactions.append(enhanced_transaction)
                
                # Log sample transactions with exchange info
                # if trans_idx < 2:
                #     amount = self._parse_amount(transaction.get('Amount', '0'))
                #     desc = str(transaction.get('Description', ''))[:60]
                #     date = transaction.get('Date', '')
                #     exchange_amount = self._get_exchange_to_amount(enhanced_transaction)
                #     exchange_currency = self._get_exchange_to_currency(enhanced_transaction)
                #     
                #     print(f"   🧾 Transaction {trans_idx}: Amount={amount}, Date={date}")
                #     if exchange_amount:
                #         print(f"      💱 Exchange To Amount: {exchange_amount} {exchange_currency}")
                #     print(f"      📝 Description: {desc}...")
        
        print(f"\n📊 TOTAL TRANSACTIONS LOADED: {len(all_transactions)}")
        
        # Find potential transfers
        print("\n🔍 FINDING TRANSFER CANDIDATES...")
        potential_transfers = self._find_transfer_candidates(all_transactions)
        print(f"   ✅ Found {len(potential_transfers)} potential transfer candidates")
        
        # STEP 1: Match currency conversions (internal conversions)
        print("\n💱 MATCHING CURRENCY CONVERSIONS...")
        conversion_pairs = self._match_currency_conversions(all_transactions)
        print(f"   ✅ Found {len(conversion_pairs)} currency conversion pairs")
        
        # STEP 2: Match cross-bank transfers using AMMAR SPECIFICATIONS
        print("\n🔄 MATCHING CROSS-BANK TRANSFERS (AMMAR SPECS)...")
        cross_bank_pairs = self._match_cross_bank_transfers(potential_transfers, all_transactions, conversion_pairs)
        print(f"   ✅ Found {len(cross_bank_pairs)} cross-bank transfer pairs")
        
        # Combine all transfer pairs
        all_transfer_pairs = conversion_pairs + cross_bank_pairs
        
        # Detect conflicts and flag manual review
        conflicts = self._detect_conflicts(all_transfer_pairs)
        flagged_transactions = self._flag_manual_review(all_transactions, all_transfer_pairs)
        
        print("\n📋 TRANSFER DETECTION SUMMARY:")
        print(f"   📊 Total transactions: {len(all_transactions)}")
        print(f"   🎯 Total transfer pairs: {len(all_transfer_pairs)}")
        print(f"   💱 Currency conversions: {len(conversion_pairs)}")
        print(f"   🔄 Cross-bank transfers: {len(cross_bank_pairs)}")
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
                'other_transfers': len(cross_bank_pairs),
                'potential_transfers': len(potential_transfers),
                'conflicts': len(conflicts),
                'flagged_for_review': len(flagged_transactions)
            }
        }
    
    def _get_exchange_to_amount(self, transaction: Dict) -> Optional[float]:
        """Extract Exchange To Amount from Wise CSV (last column)"""
        # Debug: Show all available columns
        # print(f"         DEBUG: All columns in transaction: {list(transaction.keys())}")
        
        # Check ALL possible column variations for Exchange To Amount
        exchange_amount_columns = [
            'Exchange To Amount',  # Standard format
            'Exchange_To_Amount',  # Underscore format
            'ExchangeToAmount',    # CamelCase format
            'exchange_to_amount',  # Lowercase
            'Exchange Amount',     # Without "To"
            'ExchangeAmount',      # Without "To" CamelCase
            'exchange_amount',     # Without "To" lowercase
            'Total',               # Sometimes labeled as Total
            'Total Amount',        # Total Amount
            'Converted Amount',    # Converted Amount
            'Target Amount',       # Target Amount
            'Destination Amount',  # Destination Amount
        ]
        
        # First check exact column names
        for col in exchange_amount_columns:
            if col in transaction:
                exchange_value = transaction[col]
                # print(f"         DEBUG: Found exact column '{col}' with value: '{exchange_value}'")
                if exchange_value and str(exchange_value).strip() not in ['', 'nan', 'NaN', 'null', 'None']:
                    try:
                        parsed_amount = self._parse_amount(str(exchange_value))
                        if parsed_amount != 0:
                            # print(f"         DEBUG: Successfully parsed Exchange To Amount: {abs(parsed_amount)}")
                            return abs(parsed_amount)  # Always return positive
                    except (ValueError, TypeError):
                        continue
        
        # Fallback: Search for any column containing exchange/convert/total keywords
        exchange_keywords = ['exchange', 'convert', 'total', 'destination', 'target']
        amount_keywords = ['amount', 'value', 'sum']
        
        for col in transaction:
            col_lower = col.lower()
            # Check if column contains exchange/convert keywords AND amount keywords
            has_exchange_keyword = any(keyword in col_lower for keyword in exchange_keywords)
            has_amount_keyword = any(keyword in col_lower for keyword in amount_keywords)
            
            if has_exchange_keyword and has_amount_keyword:
                exchange_value = transaction[col]
                # print(f"         DEBUG: Found keyword-based column '{col}' with value: '{exchange_value}'")
                if exchange_value and str(exchange_value).strip() not in ['', 'nan', 'NaN', 'null', 'None']:
                    try:
                        parsed_amount = self._parse_amount(str(exchange_value))
                        if parsed_amount != 0:
                            # print(f"         DEBUG: Successfully parsed Exchange To Amount (keyword): {abs(parsed_amount)}")
                            return abs(parsed_amount)  # Always return positive
                    except (ValueError, TypeError):
                        continue
        
        # Final fallback: Check if there's a numeric column that could be exchange amount
        # (Last resort - look for any numeric column that's different from the main Amount)
        main_amount = abs(self._parse_amount(transaction.get('Amount', '0')))
        for col in transaction:
            if col not in ['Amount', 'Balance', 'Date', 'Description', 'Currency'] and col not in exchange_amount_columns:
                try:
                    value = transaction[col]
                    if value and str(value).strip() not in ['', 'nan', 'NaN', 'null', 'None']:
                        parsed_amount = self._parse_amount(str(value))
                        # If it's a different amount than the main amount, it might be exchange amount
                        if parsed_amount != 0 and abs(parsed_amount) != main_amount:
                            # print(f"         DEBUG: Found potential exchange amount in column '{col}': {abs(parsed_amount)}")
                            return abs(parsed_amount)
                except (ValueError, TypeError):
                    continue
        
        # print(f"         DEBUG: No Exchange To Amount found")
        return None
    
    def _get_exchange_to_currency(self, transaction: Dict) -> Optional[str]:
        """Extract Exchange To currency from Wise CSV"""
        exchange_currency_columns = [
            'Exchange To',
            'Exchange_To',
            'ExchangeTo',
            'exchange_to'
        ]
        
        # First check exact column names
        for col in exchange_currency_columns:
            if col in transaction:
                currency_value = transaction[col]
                if currency_value and str(currency_value).strip() not in ['', 'nan', 'NaN', 'null', 'None']:
                    return str(currency_value).strip().upper()
        
        # Fallback mechanism: search for columns containing "Exchange" and "To"
        for col in transaction:
            if "exchange" in col.lower() and "to" in col.lower():
                currency_value = transaction[col]
                if currency_value and str(currency_value).strip() not in ['', 'nan', 'NaN', 'null', 'None']:
                    return str(currency_value).strip().upper()

        # If no specific column is found, return None
        return None
    
    def _match_cross_bank_transfers(self, potential_transfers: List[Dict], all_transactions: List[Dict], 
                                   existing_pairs: List[Dict]) -> List[Dict]:
        """
        Match cross-bank transfers using AMMAR SPECIFICATIONS:
        1. Exchange To Amount matching (primary)
        2. Traditional amount matching (fallback)
        3. Ammar name-based matching for Wise <-> Pakistani banks
        4. Currency-based bank targeting
        """
        transfer_pairs = []
        existing_transaction_ids = set()
        
        # Get IDs of already matched transactions
        for pair in existing_pairs:
            existing_transaction_ids.add(pair['outgoing']['_transaction_index'])
            existing_transaction_ids.add(pair['incoming']['_transaction_index'])
        
        print(f"\n🔄 MATCHING CROSS-BANK TRANSFERS...")
        # print(f"   📊 Available potential transfers: {len(potential_transfers)}")
        
        # Filter out already matched transactions
        available_outgoing = [
            t for t in potential_transfers 
            if t['_transaction_index'] not in existing_transaction_ids and 
               self._parse_amount(t.get('Amount', '0')) < 0  # Must be negative (outgoing)
        ]
        
        available_incoming = [
            t for t in all_transactions 
            if t['_transaction_index'] not in existing_transaction_ids and 
               self._parse_amount(t.get('Amount', '0')) > 0  # Must be positive (incoming)
        ]
        
        # print(f"   📤 Available outgoing: {len(available_outgoing)}")
        # print(f"   📥 Available incoming: {len(available_incoming)}")
        
        # Match each outgoing transaction
        for outgoing in available_outgoing:
            if outgoing['_transaction_index'] in existing_transaction_ids:
                continue
                
            outgoing_amount = abs(self._parse_amount(outgoing.get('Amount', '0')))
            exchange_amount = self._get_exchange_to_amount(outgoing)
            exchange_currency = self._get_exchange_to_currency(outgoing)
            
            # print(f"\n   🔍 Processing outgoing transfer:")
            # print(f"      💰 Amount: -{outgoing_amount}")
            # print(f"      📝 Description: {str(outgoing.get('Description', ''))[:50]}...")
            # print(f"      🏦 Bank: {outgoing.get('_bank_type', 'unknown')}")
            # if exchange_amount and exchange_currency:
            #     print(f"      💱 Exchange To: {exchange_amount} {exchange_currency}")
            
            # Look for matching incoming transactions
            best_match = None
            best_confidence = 0.0
            
            for incoming in available_incoming:
                if (incoming['_transaction_index'] in existing_transaction_ids or
                    incoming['_csv_index'] == outgoing['_csv_index']):  # Must be different CSV
                    continue
                
                incoming_amount = self._parse_amount(incoming.get('Amount', '0'))
                
                # print(f"      🔄 Checking incoming: {incoming.get('_bank_type')} | {incoming_amount} | {str(incoming.get('Description', '') or incoming.get('Title', ''))[:50]}...")
                
                # Check date tolerance first
                outgoing_date_str = (
                    outgoing.get('Date', '') or 
                    outgoing.get('\ufeffDate', '') or 
                    outgoing.get('TIMESTAMP', '') or 
                    outgoing.get('TransactionDate', '')
                )
                incoming_date_str = (
                    incoming.get('Date', '') or 
                    incoming.get('\ufeffDate', '') or 
                    incoming.get('TIMESTAMP', '') or 
                    incoming.get('TransactionDate', '')
                )
                
                # print(f"         DEBUG: Outgoing date string: '{outgoing_date_str}'")
                # print(f"         DEBUG: Incoming date string: '{incoming_date_str}'")
                
                if not self._dates_within_tolerance(
                    self._parse_date(outgoing_date_str),
                    self._parse_date(incoming_date_str)
                ):
                    # print(f"         ❌ Date tolerance failed")
                    continue

                # AMMAR SPEC: Check if this could be a cross-bank transfer
                if not self._is_ammar_cross_bank_transfer(outgoing, incoming):
                    # print(f"         ❌ Not Ammar cross-bank transfer")
                    continue
                
                # Initialize matches for this incoming transaction
                matches = []

                # Strategy 1: Exchange To Amount matching (PRIORITY)
                if exchange_amount and exchange_currency:
                    # Check if incoming bank matches exchange currency
                    if self._currency_matches_bank(exchange_currency, incoming):
                        exchange_match = abs(exchange_amount - incoming_amount) < 0.01
                        if exchange_match:
                            confidence = self._calculate_confidence(outgoing, incoming,
                                                                 is_cross_bank=True, 
                                                                 is_exchange_match=True)
                            matches.append({
                                'type': 'exchange_amount',
                                'confidence': confidence,
                                'matched_amount': exchange_amount,
                                'match_details': f"Exchange {exchange_amount} {exchange_currency}"
                            })
                            
                            # print(f"      ✅ EXCHANGE AMOUNT MATCH!")
                            # print(f"         💱 Exchange: {exchange_amount} {exchange_currency}")
                            # print(f"         📥 Incoming: {incoming_amount}")
                            # print(f"         🎯 Confidence: {confidence:.2f}")
                
                # Strategy 2: Traditional amount matching (FALLBACK) - ENHANCED for Ammar transfers
                traditional_match = abs(outgoing_amount - incoming_amount) < 0.01
                if traditional_match:
                    confidence = self._calculate_confidence(outgoing, incoming, is_cross_bank=True)
                    matches.append({
                        'type': 'traditional',
                        'confidence': confidence,
                        'matched_amount': outgoing_amount,
                        'match_details': f"Traditional {outgoing_amount}"
                    })
                    
                    # print(f"      ✅ TRADITIONAL AMOUNT MATCH!")
                    # print(f"         💰 Amount: {outgoing_amount}")
                    # print(f"         🎯 Confidence: {confidence:.2f}")
                
                # Strategy 3: Ammar-specific transfer with relaxed amount matching (NEW)
                if not matches:
                    # For Ammar transfers, be more lenient with amount differences due to fees
                    amount_diff_percentage = abs(outgoing_amount - incoming_amount) / max(outgoing_amount, incoming_amount)
                    
                    # print(f"      DEBUG: Ammar flexible matching - outgoing: {outgoing_amount}, incoming: {incoming_amount}")
                    # print(f"      DEBUG: Amount difference percentage: {amount_diff_percentage:.1%}")
                    
                    if amount_diff_percentage < 1.0:  # Allow up to 100% difference for currency conversion
                        confidence = self._calculate_confidence(outgoing, incoming, is_cross_bank=True) - 0.1  # Slightly lower confidence
                        min_confidence = max(confidence, 0.7)  # Higher minimum confidence for Ammar transfers
                        matches.append({
                            'type': 'ammar_flexible',
                            'confidence': min_confidence,
                            'matched_amount': incoming_amount,  # Use incoming amount as reference
                            'match_details': f"Ammar transfer with currency conversion {outgoing_amount} USD → {incoming_amount} PKR"
                        })
                        
                        # print(f"      ✅ AMMAR FLEXIBLE MATCH!")
                        # print(f"         💰 Outgoing: {outgoing_amount} USD")
                        # print(f"         💰 Incoming: {incoming_amount} PKR")
                        # print(f"         📊 Difference: {amount_diff_percentage:.1%}")
                        # print(f"         🎯 Confidence: {min_confidence:.2f}")
                
                # Choose best match for this incoming transaction
                if matches:
                    best_incoming_match = max(matches, key=lambda x: x['confidence'])
                    
                    # Keep track of overall best match
                    if best_incoming_match['confidence'] > best_confidence:
                        best_confidence = best_incoming_match['confidence']
                        best_match = {
                            'incoming': incoming,
                            'incoming_amount': incoming_amount,
                            **best_incoming_match
                        }
            
            # If we found a match, create the transfer pair
            if best_match and best_confidence >= 0.7:  # Minimum confidence threshold
                transfer_pair = {
                    'outgoing': outgoing,
                    'incoming': best_match['incoming'],
                    'amount': outgoing_amount,
                    'matched_amount': best_match['matched_amount'],
                    'exchange_amount': exchange_amount if best_match['type'] == 'exchange_amount' else None,
                    'date': self._parse_date(outgoing.get('Date', '')),
                    'confidence': best_match['confidence'],
                    'pair_id': f"cross_bank_{len(transfer_pairs)}",
                    'transfer_type': f"cross_bank_{best_match['type']}",
                    'match_strategy': best_match['type'],
                    'match_details': best_match['match_details']
                }
                
                print(f"\n      🎉 TRANSFER PAIR CREATED!")
                print(f"         📤 Outgoing: {outgoing['_csv_name']} | -{outgoing_amount}")
                print(f"         📥 Incoming: {best_match['incoming']['_csv_name']} | {best_match['incoming_amount']}")
                print(f"         🔧 Strategy: {best_match['type']}")
                print(f"         🎯 Confidence: {best_match['confidence']:.2f}")
                print(f"         💰 Matched Amount: {best_match['matched_amount']}")
                
                transfer_pairs.append(transfer_pair)
                existing_transaction_ids.add(outgoing['_transaction_index'])
                existing_transaction_ids.add(best_match['incoming']['_transaction_index'])
            else:
                pass
                # print(f"      ❌ No suitable match found (best confidence: {best_confidence:.2f})")
        
        print(f"\n   ✅ Created {len(transfer_pairs)} cross-bank transfer pairs")
        return transfer_pairs
    
    def _is_ammar_cross_bank_transfer(self, outgoing: Dict, incoming: Dict) -> bool:
        """
        Check if transactions form an Ammar-based cross-bank transfer
        AMMAR SPEC: "Sent money to Ammar" <-> "Incoming fund transfer from Ammar"
        """
        # Get descriptions from multiple possible fields (different banks use different fields)
        # Try Description, Title, Note, and any other text fields
        outgoing_desc = str(
            outgoing.get('Description', '') or 
            outgoing.get('Title', '') or 
            outgoing.get('Note', '') or 
            outgoing.get('DESCRIPTION', '') or 
            outgoing.get('TYPE', '')
        ).lower()
        
        incoming_desc = str(
            incoming.get('Description', '') or 
            incoming.get('Title', '') or 
            incoming.get('Note', '') or 
            incoming.get('DESCRIPTION', '') or 
            incoming.get('TYPE', '')
        ).lower()
        user_name_lower = self.user_name.lower()
        
        # print(f"      DEBUG AMMAR CHECK:")
        # print(f"         Outgoing desc: '{outgoing_desc[:100]}{'...' if len(outgoing_desc) > 100 else ''}'")
        # print(f"         Incoming desc: '{incoming_desc[:100]}{'...' if len(incoming_desc) > 100 else ''}'")
        # print(f"         User name: '{user_name_lower}'")
        # print(f"         Outgoing bank: {outgoing.get('_bank_type')}, Incoming bank: {incoming.get('_bank_type')}")
        
        # Must be different bank types
        outgoing_bank = outgoing.get('_bank_type', '')
        incoming_bank = incoming.get('_bank_type', '')
        
        # print(f"      DEBUG: outgoing_bank={outgoing_bank}, incoming_bank={incoming_bank}")
        if outgoing_bank == incoming_bank:
            # print(f"         DEBUG: Same bank types, skipping")
            return False

        # AMMAR SPEC: Wise -> Pakistani bank pattern
        if (outgoing_bank == 'wise' and
            incoming_bank in ['nayapay', 'bank_alfalah', 'meezan', 'pakistani_bank']):
            # print(f"         DEBUG: Wise -> Pakistani bank pattern")
            
            # Check for Ammar-specific patterns with more flexible matching
            sent_to_ammar = ('sent money to' in outgoing_desc and user_name_lower in outgoing_desc)
            
            # Debug incoming transaction details
            # print(f"         DEBUG: Full incoming description: '{incoming_desc}'")
            # print(f"         DEBUG: Looking for name variations of: '{user_name_lower}'")
            
            # More flexible Ammar matching for incoming transactions
            transfer_from_ammar = ('transfer from' in incoming_desc and user_name_lower in incoming_desc)
            incoming_fund_from_ammar = ('incoming fund transfer from' in incoming_desc and user_name_lower in incoming_desc)
            
            # Also check for variations in name format
            ammar_variations = ['ammar qazi', 'ammar', 'qazi', 'ammar q']
            # print(f"         DEBUG: Checking name variations: {ammar_variations}")
            
            transfer_from_ammar_var = any(('transfer from' in incoming_desc and variation in incoming_desc) for variation in ammar_variations)
            incoming_fund_from_ammar_var = any(('incoming fund transfer from' in incoming_desc and variation in incoming_desc) for variation in ammar_variations)
            
            incoming_from_ammar = transfer_from_ammar or incoming_fund_from_ammar or transfer_from_ammar_var or incoming_fund_from_ammar_var
            
            # print(f"         DEBUG: sent_to_ammar={sent_to_ammar}, transfer_from_ammar={transfer_from_ammar}, incoming_fund_from_ammar={incoming_fund_from_ammar}, incoming_from_ammar={incoming_from_ammar}")
            # print(f"         DEBUG: Name variation matches: transfer_from_ammar_var={transfer_from_ammar_var}, incoming_fund_from_ammar_var={incoming_fund_from_ammar_var}")
            
            if sent_to_ammar and incoming_from_ammar:
                # print(f"         ✅ AMMAR CROSS-BANK TRANSFER DETECTED!")
                return True
        # print(f"         DEBUG: Not Ammar cross-bank transfer")
        # AMMAR SPEC: Pakistani bank -> Wise pattern (reverse)
        if (outgoing_bank in ['nayapay', 'bank_alfalah', 'meezan', 'pakistani_bank'] and
            incoming_bank == 'wise'):
            
            outgoing_to_ammar = ('transfer to' in outgoing_desc and user_name_lower in outgoing_desc)
            wise_from_ammar = ('received money from' in incoming_desc and user_name_lower in incoming_desc)
            
            if outgoing_to_ammar and wise_from_ammar:
                return True
        
        return False
    
    def _currency_matches_bank(self, currency: str, transaction: Dict) -> bool:
        """
        AMMAR SPEC: Check if currency matches expected bank type
        PKR -> Pakistani banks (NayaPay, Meezan, etc.)
        EUR -> European Wise accounts
        USD -> USD Wise accounts
        """
        bank_type = transaction.get('_bank_type', '')
        
        if currency == 'PKR':
            return bank_type in ['nayapay', 'bank_alfalah', 'meezan', 'pakistani_bank']
        elif currency == 'EUR':
            return bank_type == 'wise' and 'eur' in transaction.get('_csv_name', '').lower()
        elif currency == 'USD':
            return bank_type == 'wise' and 'usd' in transaction.get('_csv_name', '').lower()
        
        return True  # If unsure, allow the match
    
    def _match_currency_conversions(self, all_transactions: List[Dict]) -> List[Dict]:
        """Match internal currency conversions"""
        conversion_pairs = []
        matched_transactions = set()
        
        conversion_candidates = []
        
        for transaction in all_transactions:
            if transaction['_transaction_index'] in matched_transactions:
                continue
                
            desc = str(transaction.get('Description', '')).lower()
            amount = self._parse_amount(transaction.get('Amount', '0'))
            date = self._parse_date(transaction.get('Date', ''))
            
            conversion_info = self._extract_conversion_info(desc, amount)
            
            if conversion_info:
                conversion_candidates.append({
                    **transaction,
                    '_conversion_info': conversion_info,
                    '_amount': amount,
                    '_date': date
                })
                
                # print(f"\n💱 CONVERSION CANDIDATE: {transaction['_csv_name']}")
                # print(f"   💰 Amount: {amount}")
                # print(f"   📅 Date: {date.strftime('%Y-%m-%d')}")
                # print(f"   📝 Description: {desc[:80]}...")
                # print(f"   🔄 Conversion: {conversion_info['from_amount']} {conversion_info['from_currency']} → {conversion_info['to_amount']} {conversion_info['to_currency']}")
        
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
                
                if self._is_matching_conversion(conv1, conv2, candidate1, candidate2):
                    if candidate1['_amount'] < 0 and candidate2['_amount'] > 0:
                        outgoing, incoming = candidate1, candidate2
                    elif candidate1['_amount'] > 0 and candidate2['_amount'] < 0:
                        outgoing, incoming = candidate2, candidate1
                    else:
                        continue
                    
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
                    
                    # print(f"\n   ✅ CURRENCY CONVERSION MATCHED! Confidence: {confidence:.2f}")
                    # print(f"      📤 Outgoing: {outgoing['_csv_name']} | {outgoing['_amount']} {conv1['from_currency']}")
                    # print(f"      📥 Incoming: {incoming['_csv_name']} | {incoming['_amount']} {conv1['to_currency']}")
                    
                    conversion_pairs.append(transfer_pair)
                    matched_transactions.add(outgoing['_transaction_index'])
                    matched_transactions.add(incoming['_transaction_index'])
                    break
        
        return conversion_pairs
    
    # Helper methods
    def _find_transfer_candidates(self, transactions: List[Dict]) -> List[Dict]:
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
                    # Debug: Log found transfer candidates
                    # bank_type = transaction.get('_bank_type', 'unknown')
                    # amount = self._parse_amount(transaction.get('Amount', '0'))
                    # print(f"   🎯 TRANSFER CANDIDATE: {bank_type} | {amount} | {description[:60]}...")
                    
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
    
    def _extract_conversion_info(self, description: str, amount: float) -> Optional[Dict]:
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
    
    def _is_matching_conversion(self, conv1: Dict, conv2: Dict, candidate1: Dict, candidate2: Dict) -> bool:
        """Check if two conversion records represent the same conversion"""
        amounts_match = (
            abs(conv1['from_amount'] - conv2['from_amount']) < 0.01 and
            abs(conv1['to_amount'] - conv2['to_amount']) < 0.01 and
            conv1['from_currency'] == conv2['from_currency'] and
            conv1['to_currency'] == conv2['to_currency']
        )
        
        date_match = self._dates_within_tolerance(candidate1['_date'], candidate2['_date'])
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
    
    def _calculate_conversion_confidence(self, outgoing: Dict, incoming: Dict, conv1: Dict, conv2: Dict) -> float:
        """Calculate confidence for currency conversion matches"""
        confidence = 0.5
        
        if (abs(abs(outgoing['_amount']) - conv1['from_amount']) < 0.01 and
            abs(abs(incoming['_amount']) - conv1['to_amount']) < 0.01):
            confidence += 0.3
        
        if outgoing['_date'].date() == incoming['_date'].date():
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
    
    def _calculate_confidence(self, outgoing: Dict, incoming: Dict, is_cross_bank: bool = False, is_exchange_match: bool = False) -> float:
        """Calculate confidence score for transfer pair matching"""
        confidence = 0.5  # Base confidence
        
        if is_cross_bank:
            confidence += 0.2
        
        # AMMAR SPEC: Higher confidence for exchange amount matches
        if is_exchange_match:
            confidence += 0.3  # Exchange matches are very reliable
        
        # Same day bonus
        outgoing_date = self._parse_date(outgoing.get('Date', ''))
        incoming_date = self._parse_date(incoming.get('Date', ''))
        if outgoing_date.date() == incoming_date.date():
            confidence += 0.2
        
        # Ammar name match bonus
        outgoing_desc = str(outgoing.get('Description', '')).lower()
        incoming_desc = str(incoming.get('Description', '')).lower()
        if (self.user_name.lower() in outgoing_desc and self.user_name.lower() in incoming_desc):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _detect_conflicts(self, transfer_pairs: List[Dict]) -> List[Dict]:
        """Detect transactions that could match multiple partners"""
        return []
    
    def _flag_manual_review(self, all_transactions: List[Dict], transfer_pairs: List[Dict]) -> List[Dict]:
        """Flag transactions that need manual review"""
        return []
    
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
            # Handle empty or None dates
            if not date_str or date_str == '':
                # print(f"         DEBUG: Empty date string, returning current date")
                return datetime.now()
            
            date_formats = [
                '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y-%m-%d %H:%M:%S',
                '%d-%m-%y', '%m-%d-%y', '%y-%m-%d'  # Add 2-digit year formats
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(str(date_str), fmt)
                    # print(f"         DEBUG: Successfully parsed date '{date_str}' as {parsed_date.strftime('%Y-%m-%d')}")
                    return parsed_date
                except ValueError:
                    continue
            
            # print(f"         DEBUG: Could not parse date '{date_str}', returning current date")
            return datetime.now()
        except Exception as e:
            # print(f"         DEBUG: Date parsing error for '{date_str}': {e}")
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
