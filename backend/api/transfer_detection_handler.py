"""
Transfer detection logic for multi-CSV processing
Handles initialization and execution of transfer detection between CSV files
"""
from typing import List, Dict, Any
from ..transfer_detector import TransferDetector
from ..transfer_detector_improved import ImprovedTransferDetector
from ..transfer_detector_enhanced_ammar_refactored import TransferDetector as EnhancedAmmarTransferDetector


class TransferDetectionHandler:
    """Handles transfer detection logic for multi-CSV processing"""
    
    def perform_transfer_detection(self, request, all_transformed_data: List[Dict]) -> Dict:
        """Perform transfer detection between CSV files"""
        # Initialize with default values
        transfer_analysis = {
            'transfers': [],
            'summary': {
                'transfer_pairs_found': 0,
                'potential_transfers': 0,
                'conflicts': 0,
                'flagged_for_review': 0
            }
        }
        
        if not request.enable_transfer_detection or len(request.csv_data_list) <= 1:
            print("🚫 Transfer detection skipped (not enabled or insufficient CSVs)")
            return transfer_analysis
        
        try:
            print(f"🔄 Starting ENHANCED TRANSFER DETECTION between {len(request.csv_data_list)} CSVs...")
            
            # Try to use the new configuration-based transfer detector
            transfer_detector = self._initialize_transfer_detector(request)
            
            # Detect transfers
            transfer_analysis = transfer_detector.detect_transfers(request.csv_data_list)
            print(f"✅ Transfer detection complete: {transfer_analysis['summary']}")
            
            # Apply transfer categorization
            if transfer_analysis.get('transfers'):
                self._apply_transfer_categorization(transfer_detector, request, transfer_analysis, all_transformed_data)
            
            return transfer_analysis
            
        except Exception as transfer_error:
            print(f"⚠️ Transfer detection failed: {str(transfer_error)}")
            print("🔄 Continuing without transfer detection...")
            import traceback
            print(f"📚 Full error traceback: {traceback.format_exc()}")
            return transfer_analysis
    
    def _initialize_transfer_detector(self, request):
        """Initialize the best available transfer detector"""
        # Try new configuration-based detector first
        try:
            transfer_detector = EnhancedAmmarTransferDetector("configs")
            print("🚀 Using NEW Configuration-Based Transfer Detector")
            return transfer_detector
        except Exception as e1:
            print(f"⚠️ Configuration-based detector failed: {e1}")
            
            # Fallback to enhanced ammar detector with old interface
            try:
                from ..transfer_detector_enhanced_ammar import TransferDetector as LegacyEnhancedAmmarTransferDetector
                transfer_detector = LegacyEnhancedAmmarTransferDetector(
                    user_name=request.user_name,
                    date_tolerance_hours=request.date_tolerance_hours
                )
                print("🚀 Using Legacy Enhanced Ammar Transfer Detector")
                return transfer_detector
            except Exception as e2:
                print(f"⚠️ Legacy Enhanced Ammar detector failed: {e2}")
                
                # Fallback to improved detector
                try:
                    transfer_detector = ImprovedTransferDetector(
                        user_name=request.user_name,
                        date_tolerance_hours=request.date_tolerance_hours
                    )
                    print("⚠️  Using Standard Improved Transfer Detector")
                    return transfer_detector
                except Exception as e3:
                    print(f"⚠️ Improved detector failed: {e3}")
                    
                    # Last fallback to basic detector
                    transfer_detector = TransferDetector(
                        user_name=request.user_name,
                        date_tolerance_hours=request.date_tolerance_hours
                    )
                    print("⚠️  Using Basic Transfer Detector")
                    return transfer_detector
    
    def _apply_transfer_categorization(self, transfer_detector, request, transfer_analysis, all_transformed_data):
        """Apply transfer categorization to detected transfers"""
        print(f"🔄 Applying transfer categorization to {len(transfer_analysis['transfers'])} pairs...")
        
        transfer_matches = transfer_detector.apply_transfer_categorization(
            request.csv_data_list, 
            transfer_analysis['transfers']
        )
        
        print(f"📝 Created {len(transfer_matches)} transfer matches for balance correction")
        
        # Apply balance corrections
        balance_corrections_applied = 0
        
        for i, transaction in enumerate(all_transformed_data):
            for match in transfer_matches:
                # Improved matching with cleaned numeric amounts
                trans_amount = float(transaction.get('Amount', '0'))
                match_amount = float(match['amount'])
                amount_match = abs(trans_amount - match_amount) < 0.01
                date_match = transaction.get('Date', '').startswith(match['date'])
                
                if amount_match and date_match:
                    all_transformed_data[i]['Category'] = match['category']
                    all_transformed_data[i]['Note'] = match['note']
                    all_transformed_data[i]['_transfer_pair_id'] = match['pair_id']
                    all_transformed_data[i]['_transfer_type'] = match['transfer_type']
                    all_transformed_data[i]['_is_transfer'] = True
                    all_transformed_data[i]['_match_strategy'] = match.get('match_strategy', 'traditional')
                    balance_corrections_applied += 1
                    break
        
        print(f"✅ Transfer categorization applied - {balance_corrections_applied} balance corrections")
