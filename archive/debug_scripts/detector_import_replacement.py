                # AMMAR SPECS: Initialize transfer detector with Ammar's specifications
                # Try Ammar-specific detector first, fallback to enhanced detector
                try:
                    from transfer_detector_enhanced_ammar import TransferDetector as AmmarTransferDetector
                    transfer_detector = AmmarTransferDetector(
                        user_name=request.user_name,
                        date_tolerance_hours=request.date_tolerance_hours
                    )
                    print("🚀 Using Ammar-Specific Transfer Detector with Exchange To Amount Support")
                except ImportError:
                    try:
                        from transfer_detector_enhanced_exchange import TransferDetector as EnhancedTransferDetector
                        transfer_detector = EnhancedTransferDetector(
                            user_name=request.user_name,
                            date_tolerance_hours=request.date_tolerance_hours
                        )
                        print("🚀 Using Enhanced Transfer Detector with Exchange Amount Support")
                    except ImportError:
                        transfer_detector = ImprovedTransferDetector(
                            user_name=request.user_name,
                            date_tolerance_hours=request.date_tolerance_hours
                        )
                        print("⚠️  Using Standard Transfer Detector (enhanced not available)")
