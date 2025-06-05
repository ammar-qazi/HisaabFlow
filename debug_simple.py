#!/usr/bin/env python3
"""
Simple debug script to understand the transfer detection issue
"""

import re

def debug_patterns():
    """Debug the transfer patterns"""
    
    user_name = "Ammar Qazi"
    
    # Transfer description patterns - Enhanced with cross-bank patterns
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
    
    # Test descriptions from your actual data
    test_descriptions = [
        "Sent money to Usama Qazi",
        "Sent money to Ammar Qazi", 
        "Incoming fund transfer from Ammar Qazi Bank Alfalah-2050|Transaction ID 192351",
        "Incoming fund transfer from Usama Qazi Bank Alfalah-2050|Transaction ID 192351"
    ]
    
    print("🧪 Testing Transfer Pattern Matching")
    print("=" * 60)
    
    for desc in test_descriptions:
        print(f"\n📝 Testing: '{desc}'")
        desc_lower = desc.lower()
        
        for i, pattern in enumerate(transfer_patterns):
            try:
                if re.search(pattern, desc_lower):
                    print(f"  ✅ Pattern {i+1} MATCHES: {pattern}")
                else:
                    print(f"  ❌ Pattern {i+1} no match: {pattern}")
            except Exception as e:
                print(f"  ⚠️  Pattern {i+1} error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 KEY INSIGHTS:")
    print("- Pattern 2 should match 'Sent money to Ammar Qazi'")
    print("- Pattern 5 should match 'Incoming fund transfer from Ammar Qazi'")
    print("- Pattern 8 should match any 'Incoming fund transfer'")

if __name__ == "__main__":
    debug_patterns()
