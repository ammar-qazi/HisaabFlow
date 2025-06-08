"""
Main transfer detector orchestrating all components
"""
from typing import Dict, List, Any
from .amount_parser import AmountParser
from .date_parser import DateParser
from .exchange_analyzer import ExchangeAnalyzer
from .cross_bank_matcher import CrossBankMatcher
from .currency_converter import CurrencyConverter
from .confidence_calculator import ConfidenceCalculator
from .config_manager import ConfigurationManager


class TransferDetector:
    """
    Enhanced transfer detection system with Ammar's specifications:
    1. Exchange To Amount matching for currency conversions
    2. Ammar name-based cross-bank transfers (Sent money to Ammar <-> Incoming from Ammar)
    3. Currency-based bank targeting (PKR for Pakistani banks, EUR for European accounts)
    4. 24-hour date tolerance with fallback to traditional amount matching
    """
    
    def __init__(self, config_dir: str = "configs"):
        # Initialize configuration manager
        self.config = ConfigurationManager(config_dir)
        self.user_name = self.config.get_user_name()
        self.date_tolerance_hours = self.config.get_date_tolerance()
        
        # Initialize components with configuration
        self.cross_bank_matcher = CrossBankMatcher(config_dir)
        self.currency_converter = CurrencyConverter()
        self.confidence_calculator = ConfidenceCalculator(self.user_name)
    
    def detect_transfers(self, csv_data_list: List[Dict]) -> Dict[str, Any]:
        """Main transfer detection function with Ammar's specifications"""
        
        print("\n🔍 STARTING ENHANCED TRANSFER DETECTION (CONFIG-BASED)")
        print("=" * 70)
        print(f"👤 User: {self.user_name}")
        print(f"📅 Date tolerance: {self.date_tolerance_hours} hours")
        print(f"🏦 Configured banks: {', '.join(self.config.list_configured_banks())}")
        print(f"🎯 Confidence threshold: {self.config.get_confidence_threshold()}")
        print("=" * 70)
        
        # Flatten all transactions with source info
        all_transactions = self._prepare_transactions(csv_data_list)
        
        print(f"\n📊 TOTAL TRANSACTIONS LOADED: {len(all_transactions)}")
        
        # Find potential transfers
        print("\n🔍 FINDING TRANSFER CANDIDATES...")
        potential_transfers = self.cross_bank_matcher.find_transfer_candidates(all_transactions)
        print(f"   ✅ Found {len(potential_transfers)} potential transfer candidates")
        
        # STEP 1: Match currency conversions (internal conversions)
        print("\n💱 MATCHING CURRENCY CONVERSIONS...")
        conversion_pairs = self.currency_converter.match_currency_conversions(all_transactions)
        print(f"   ✅ Found {len(conversion_pairs)} currency conversion pairs")
        
        # STEP 2: Match cross-bank transfers using AMMAR SPECIFICATIONS
        print("\n🔄 MATCHING CROSS-BANK TRANSFERS (AMMAR SPECS)...")
        cross_bank_pairs = self.cross_bank_matcher.match_cross_bank_transfers(
            potential_transfers, all_transactions, conversion_pairs
        )
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
    
    def _prepare_transactions(self, csv_data_list: List[Dict]) -> List[Dict]:
        """Flatten all transactions with source info and metadata"""
        all_transactions = []
        
        for csv_idx, csv_data in enumerate(csv_data_list):
            print(f"\n📁 Processing CSV {csv_idx}: {csv_data.get('file_name', f'CSV_{csv_idx}')}")
            print(f"   📊 Transaction count: {len(csv_data['data'])}")
            
            # DEBUG: Check CSV data structure
            if csv_data['data']:
                sample_transaction = csv_data['data'][0]
                print(f"   🔍 Available columns: {list(sample_transaction.keys())}")
            
            for trans_idx, transaction in enumerate(csv_data['data']):
                enhanced_transaction = {
                    **transaction,
                    '_csv_index': csv_idx,
                    '_transaction_index': trans_idx,
                    '_csv_name': csv_data.get('file_name', f'CSV_{csv_idx}'),
                    '_template_config': csv_data.get('template_config', {}),
                    '_bank_type': self.config.detect_bank_type(
                        csv_data.get('file_name', '')
                    ),
                    '_raw_data': transaction
                }
                all_transactions.append(enhanced_transaction)
        
        return all_transactions
    
    def _detect_conflicts(self, transfer_pairs: List[Dict]) -> List[Dict]:
        """Detect transactions that could match multiple partners"""
        return []
    
    def _flag_manual_review(self, all_transactions: List[Dict], transfer_pairs: List[Dict]) -> List[Dict]:
        """Flag transactions that need manual review"""
        return []
    
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
                'amount': str(AmountParser.parse_amount(outgoing.get('Amount', '0'))),
                'date': DateParser.parse_date(outgoing.get('Date', '')).strftime('%Y-%m-%d'),
                'description': str(outgoing.get('Description', '')),
                'category': 'Balance Correction',
                'note': f"Transfer out - {pair['transfer_type']} - Pair ID: {pair['pair_id']}{exchange_note}",
                'pair_id': pair['pair_id'],
                'transfer_type': 'outgoing',
                'match_strategy': pair.get('match_strategy', 'traditional')
            })
            
            transfer_matches.append({
                'csv_index': incoming['_csv_index'],
                'amount': str(AmountParser.parse_amount(incoming.get('Amount', '0'))),
                'date': DateParser.parse_date(incoming.get('Date', '')).strftime('%Y-%m-%d'),
                'description': str(incoming.get('Description', '')),
                'category': 'Balance Correction',
                'note': f"Transfer in - {pair['transfer_type']} - Pair ID: {pair['pair_id']}{exchange_note}",
                'pair_id': pair['pair_id'],
                'transfer_type': 'incoming',
                'match_strategy': pair.get('match_strategy', 'traditional')
            })
        
        return transfer_matches
