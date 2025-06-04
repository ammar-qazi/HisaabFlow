#!/usr/bin/env python3
"""
Test improved auto-detection for NayaPay
"""

import sys
import os
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from enhanced_csv_parser import EnhancedCSVParser

def test_nayapay_detection():
    print("🧪 Testing NayaPay Auto-Detection")
    print("=" * 50)
    
    parser = EnhancedCSVParser()
    csv_path = "/home/ammar/claude_projects/bank_statement_parser/m022025.csv"
    
    print(f"📁 Testing file: {csv_path}")
    
    # Test detection
    detection = parser.detect_data_range(csv_path)
    
    if detection['success']:
        detected_row = detection['suggested_header_row']
        print(f"🎯 Detected header row: {detected_row}")
        
        # Read a few lines around the detected row to verify
        with open(csv_path, 'r') as f:
            lines = f.readlines()
            
        print(f"📋 Context around detected row {detected_row}:")
        for i in range(max(0, detected_row-2), min(len(lines), detected_row+3)):
            prefix = ">>> " if i == detected_row else "    "
            print(f"{prefix}Row {i:2}: {lines[i].strip()[:100]}")
            
        # Expected: Row 13 should be "TIMESTAMP,TYPE,DESCRIPTION,AMOUNT,BALANCE"
        if detected_row == 13:
            print("✅ Detection is CORRECT!")
        else:
            print(f"❌ Detection is wrong. Expected: 13, Got: {detected_row}")
            
    else:
        print(f"❌ Detection failed: {detection['error']}")

if __name__ == "__main__":
    test_nayapay_detection()
