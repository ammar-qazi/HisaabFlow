#!/usr/bin/env python3
"""
Test script to verify the updated v2.6 template works correctly
"""

import sys
import os
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from enhanced_csv_parser import EnhancedCSVParser
import json

def test_template_categorization():
    print("🧪 Testing NayaPay Enhanced Template v2.6")
    print("=" * 50)
    
    # Initialize parser
    parser = EnhancedCSVParser()
    
    # Load the template
    template_config = parser.load_template("NayaPay_Enhanced_Template", "templates")
    print(f"📋 Loaded template version: {template_config.get('version', 'unknown')}")
    
    # Parse the CSV file
    csv_path = "/home/ammar/claude_projects/bank_statement_parser/m022025.csv"
    
    # Parse with the template settings
    parse_result = parser.parse_with_range(
        csv_path,
        template_config['start_row'],
        template_config.get('end_row'),
        template_config['start_col'],
        template_config.get('end_col', 5),
        'utf-8'
    )
    
    if not parse_result['success']:
        print(f"❌ Failed to parse CSV: {parse_result['error']}")
        return
    
    print(f"✅ Parsed {parse_result['row_count']} transactions")
    print(f"📊 Headers: {parse_result['headers']}")
    print()
    
    # Transform to Cashew format with categorization
    transformed_data = parser.transform_to_cashew(
        parse_result['data'],
        template_config['column_mapping'],
        template_config['bank_name'],
        template_config['categorization_rules'],
        template_config['default_category_rules'],
        template_config.get('account_mapping')
    )
    
    print(f"🔄 Transformed {len(transformed_data)} transactions")
    print()
    
    # Test specific cases we're interested in
    test_cases = [
        ("Mobile Top-ups", lambda t: "mobile" in t['Title'].lower() or "charge" in t['Title'].lower()),
        ("Ride Hailing", lambda t: t['Category'] == 'Travel' and 'hailing' in t['Title'].lower()),
        ("Large Transfers", lambda t: t['Category'] == 'Transfer' and abs(float(t['Amount'])) >= 5000),
        ("Surraiya Riaz", lambda t: 'zunayyara' in t['Title'].lower()),
        ("Small easypaisa transfers", lambda t: abs(float(t['Amount'])) <= 2000 and 'easypaisa' in str(t.get('Note', '')))
    ]
    
    print("🔍 **CATEGORIZATION RESULTS:**")
    print("=" * 50)
    
    for case_name, condition in test_cases:
        matching_transactions = [t for t in transformed_data if condition(t)]
        print(f"\n📋 **{case_name}** ({len(matching_transactions)} transactions):")
        for t in matching_transactions[:3]:  # Show first 3 examples
            amount = float(t['Amount'])
            print(f"   💰 {amount:>8.0f} | {t['Category']:<12} | {t['Title']}")
        if len(matching_transactions) > 3:
            print(f"   ... and {len(matching_transactions)-3} more")
    
    print("\n🎯 **KEY VALIDATION CHECKS:**")
    print("=" * 30)
    
    # Check mobile top-ups
    mobile_topups = [t for t in transformed_data if 'mobile' in t['Title'].lower() or 'topup' in str(t.get('Note', '')).lower()]
    print(f"1. Mobile Top-ups: {len(mobile_topups)} found")
    for m in mobile_topups:
        print(f"   ✅ {m['Title']} → {m['Category']}")
    
    # Check ride hailing (small easypaisa transfers)
    small_easypaisa = []
    for t in transformed_data:
        try:
            amount = float(t['Amount'])
            original_data = None
            # Find original transaction data to check for easypaisa
            for orig in parse_result['data']:
                if abs(float(parser._parse_amount(str(orig.get('AMOUNT', '0'))))) == abs(amount):
                    if 'easypaisa' in str(orig.get('DESCRIPTION', '')).lower():
                        if -2000 <= amount <= -100:
                            small_easypaisa.append(t)
                    break
        except:
            continue
    
    print(f"2. Potential Ride Hailing: {len(small_easypaisa)} found")
    for r in small_easypaisa:
        print(f"   🚗 {r['Title']} → {r['Category']} (Amount: {r['Amount']})")
    
    # Check large transfers
    large_transfers = [t for t in transformed_data if t['Category'] == 'Transfer' and abs(float(t['Amount'])) >= 5000]
    print(f"3. Large Transfers: {len(large_transfers)} found")
    for lt in large_transfers:
        print(f"   📤 {lt['Title']} → {lt['Category']} (Amount: {lt['Amount']})")
    
    print("\n📈 **SUMMARY BY CATEGORY:**")
    print("=" * 25)
    category_summary = {}
    for t in transformed_data:
        cat = t['Category']
        if cat not in category_summary:
            category_summary[cat] = {'count': 0, 'total': 0}
        category_summary[cat]['count'] += 1
        try:
            category_summary[cat]['total'] += float(t['Amount'])
        except:
            pass
    
    for cat, data in sorted(category_summary.items()):
        print(f"   {cat:<15} | {data['count']:>3} transactions | Total: {data['total']:>10.0f}")
    
    print(f"\n🎉 **TEMPLATE TEST COMPLETE!**")
    return transformed_data

if __name__ == "__main__":
    test_template_categorization()
