#!/usr/bin/env python3
"""
Test TransferDetector standalone to identify the issue
"""

import sys
import os
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

def test_transfer_detector():
    print("🧪 Testing TransferDetector standalone")
    print("=" * 50)
    
    try:
        from transfer_detector import TransferDetector
        print("✅ TransferDetector import successful")
        
        # Create instance
        detector = TransferDetector(user_name="Ammar Qazi", date_tolerance_hours=24)
        print("✅ TransferDetector instance created")
        
        # Test with minimal data structure
        test_csv_data = [
            {
                'file_name': 'test1.csv',
                'data': [
                    {'Amount': '-100', 'Date': '2025-02-01', 'Description': 'Transfer to test'},
                    {'Amount': '100', 'Date': '2025-02-01', 'Description': 'Transfer from test'}
                ],
                'headers': ['Amount', 'Date', 'Description'],
                'template_config': {}
            }
        ]
        
        print("🔍 Testing detect_transfers method...")
        result = detector.detect_transfers(test_csv_data)
        print(f"✅ Transfer detection successful: {result['summary']}")
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
    except Exception as e:
        print(f"❌ Runtime error: {str(e)}")
        import traceback
        print(f"📚 Full traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    test_transfer_detector()
