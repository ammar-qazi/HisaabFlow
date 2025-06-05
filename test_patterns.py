#!/usr/bin/env python3
"""
Debug script to test patterns against actual NayaPay data
"""

import re

def test_nayapay_patterns():
    """Test transfer patterns against actual NayaPay descriptions"""
    
    user_name = "Ammar Qazi"
    
    # Transfer description patterns from the detector
    transfer_patterns = [
        r"converted\s+\w+",  # "Converted USD", "Converted EUR"
        rf"sent\s+(money\s+)?to\s+{re.escape(user_name.lower())}",  # "Sent money to Ammar Qazi", "Sent to Ammar Qazi"
        rf"transfer\s+to\s+{re.escape(user_name.lower())}",  # "Transfer to Ammar Qazi"
        rf"transfer\s+from\s+{re.escape(user_name.lower())}",  # "Transfer from Ammar Qazi"
        rf"incoming\s+fund\s+transfer\s+from\s+{re.escape(user_name.lower())}",  # "Incoming fund transfer from Ammar Qazi"
        r"transfer\s+to\s+\w+",  # "Transfer to account"
        r"transfer\s+from\s+\w+",  # "Transfer from account"
        r"incoming\s+fund\s+transfer",  # NayaPay pattern
        r"fund\s+transfer\s+from",  # Bank Alfalah pattern
    ]
    
    # Actual descriptions from your NayaPay CSV
    nayapay_descriptions = [
        "Incoming fund transfer from Ammar Qazi\\nBank Alfalah-2050|Transaction ID 017707",
        "Incoming fund transfer from Ammar Qazi\\nBank Alfalah-2050|Transaction ID 192351",
        "Outgoing fund transfer to Surraiya Riaz (Asaan Ac)\\nMeezan Bank-2660|Transaction ID 679fb6a0462d384309905d16",
        "Outgoing fund transfer to Ammar Qazi\\nMeezan Bank-3212|Transaction ID 67a3837b5f678d3d7da2addd"
    ]
    
    # Expected Wise descriptions (based on your pattern)
    wise_descriptions = [
        "Sent money to Ammar Qazi",
        "Sent money to Usama Qazi", 
        "Sent money to Zunayyara Khalid"
    ]
    
    print("🧪 TESTING TRANSFER PATTERNS AGAINST ACTUAL DATA")
    print("=" * 60)
    
    print("\n📥 TESTING NAYAPAY DESCRIPTIONS:")
    for desc in nayapay_descriptions:
        print(f"\n📝 Testing: '{desc}'")
        desc_lower = desc.lower()
        
        matched = False
        for i, pattern in enumerate(transfer_patterns):
            try:
                if re.search(pattern, desc_lower):
                    print(f"  ✅ Pattern {i+1} MATCHES: {pattern}")
                    matched = True
                else:
                    print(f"  ❌ Pattern {i+1}: {pattern}")
            except Exception as e:
                print(f"  ⚠️  Pattern {i+1} error: {e}")
        
        if not matched:
            print("  🚨 NO PATTERNS MATCHED!")
    
    print("\n📤 TESTING WISE DESCRIPTIONS:")
    for desc in wise_descriptions:
        print(f"\n📝 Testing: '{desc}'")
        desc_lower = desc.lower()
        
        matched = False
        for i, pattern in enumerate(transfer_patterns):
            try:
                if re.search(pattern, desc_lower):
                    print(f"  ✅ Pattern {i+1} MATCHES: {pattern}")
                    matched = True
                else:
                    print(f"  ❌ Pattern {i+1}: {pattern}")
            except Exception as e:
                print(f"  ⚠️  Pattern {i+1} error: {e}")
        
        if not matched:
            print("  🚨 NO PATTERNS MATCHED!")
    
    print("\n" + "=" * 60)
    print("🎯 KEY FINDINGS:")
    print("✅ Pattern 2 should match: 'Sent money to Ammar Qazi'")
    print("✅ Pattern 5 should match: 'Incoming fund transfer from Ammar Qazi'") 
    print("✅ Pattern 8 should match: 'Incoming fund transfer' (general)")
    print("✅ Pattern 9 should match: 'fund transfer from'")

if __name__ == "__main__":
    test_nayapay_patterns()
