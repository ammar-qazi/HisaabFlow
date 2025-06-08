#!/usr/bin/env python3

import re

def test_transferwise_regex():
    """Test Transferwise regex patterns"""
    
    # Sample transactions from the log
    test_transactions = [
        "Card transaction of 25,492.52 HUF issued by National Data Base A ISLAMABAD",
        "Card transaction of 30.00 USD issued by Revolut**0540* Dublin",
        "Card transaction of 3,546.00 HUF issued by Lidl Hu 108 Cegled Cegled",
        "Card transaction of 74.94 USD issued by Kiwi.com BRNO - ZABRDO",
        "Card transaction of 8,903.00 HUF issued by Lidl Hu 108 Cegled Cegled",
        "Card transaction of 3,840.00 HUF issued by Alza.cz A.s. Prague",
        "Card transaction of 902.00 TRY issued by Pegasus UK",
        "Card transaction of 4.00 SAR issued by Riyadh Metro Riyadh",
        "Card transaction of 5.00 USD issued by Airalo SINGAPORE"
    ]
    
    # Test different regex patterns
    patterns = [
        # Original pattern
        r"Card transaction of [\d,]+\.[\d]{2} [A-Z]{3} issued by (.+)",
        
        # New improved patterns
        r"Card transaction of [\d,.]+\s+[A-Z]{3}\s+issued by\s+(.+?)$",
        r"Card transaction of [\d,.]+\.[0-9]{2}\s+[A-Z]{3}\s+issued by\s+(.+)",
        r"Card transaction of\s+[\d,.]+\s+[A-Z]{3}\s+issued by\s+(.+)",
        
        # Most flexible pattern
        r"Card transaction of\s+[\d,.]+ [A-Z]{3}\s+issued by\s+(.+)"
    ]
    
    print("🧪 Testing Transferwise Regex Patterns")
    print("=" * 80)
    
    for i, pattern in enumerate(patterns):
        print(f"\n🔍 Pattern {i+1}: {pattern}")
        print("-" * 60)
        
        for transaction in test_transactions:
            match = re.search(pattern, transaction, re.IGNORECASE)
            if match:
                extracted = match.group(1).strip()
                print(f"  ✅ '{transaction[:40]}...' → '{extracted}'")
            else:
                print(f"  ❌ '{transaction[:40]}...' → NO MATCH")
    
    print(f"\n" + "=" * 80)
    print("🎯 Recommended Pattern:")
    
    # Test the best pattern
    best_pattern = r"Card transaction of\s+[\d,.]+ [A-Z]{3}\s+issued by\s+(.+)"
    
    print(f"Pattern: {best_pattern}")
    print("-" * 60)
    
    for transaction in test_transactions:
        match = re.search(best_pattern, transaction, re.IGNORECASE)
        if match:
            extracted = match.group(1).strip()
            print(f"  ✅ {extracted}")
        else:
            print(f"  ❌ NO MATCH: {transaction}")

if __name__ == "__main__":
    test_transferwise_regex()
