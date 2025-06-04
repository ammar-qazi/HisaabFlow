#!/usr/bin/env python3

import sys
import os
import json

# Add the backend directory to the path
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

from enhanced_csv_parser import EnhancedCSVParser

def test_m022025_file():
    """Test the actual m022025.csv file with our fixed categorization"""
    
    print("🔍 Testing m022025.csv with Fixed Categorization")
    print("=" * 60)
    
    # Initialize parser
    parser = EnhancedCSVParser()
    
    # Load the NayaPay Enhanced Template
    template_path = "/home/ammar/claude_projects/bank_statement_parser/templates/NayaPay_Enhanced_Template.json"
    with open(template_path, 'r') as f:
        template = json.load(f)
    
    print(f"📋 Template: {template['bank_name']} v{template['version']}")
    print(f"   Rules: {len(template.get('categorization_rules', []))}")
    print()
    
    # Parse the CSV file
    csv_file = "/home/ammar/claude_projects/bank_statement_parser/m022025.csv"
    print(f"📄 Processing file: {csv_file}")
    
    # Parse with the template's configuration
    parse_result = parser.parse_with_range(
        csv_file,
        template['start_row'],  # Should be 13
        template.get('end_row'),
        template['start_col'],  # Should be 0
        template.get('end_col', 5),
        'utf-8'
    )
    
    if not parse_result['success']:
        print(f"❌ Failed to parse CSV: {parse_result['error']}")
        return
    
    print(f"✅ Parsed {parse_result['row_count']} transactions")
    print(f"📋 Headers: {parse_result['headers']}")
    print()
    
    # Transform with categorization rules
    transformed = parser.transform_to_cashew(
        parse_result['data'],
        template['column_mapping'],
        template['bank_name'],
        template.get('categorization_rules', []),
        template.get('default_category_rules'),
        template.get('account_mapping')
    )
    
    print(f"🔄 Transformed {len(transformed)} transactions")
    print()
    
    # Analyze results
    print("📊 DETAILED RESULTS:")
    print("=" * 40)
    
    ride_hailing_count = 0
    surraiya_count = 0
    mobile_topup_count = 0
    transfer_count = 0
    
    for i, result in enumerate(transformed):
        original = parse_result['data'][i]
        
        print(f"\n{i+1}. Transaction:")
        print(f"   Original: {original.get('TYPE', 'N/A')}, Amount: {original.get('AMOUNT', 'N/A')}")
        print(f"   Description: {original.get('DESCRIPTION', 'N/A')[:60]}...")
        print(f"   Result: Category='{result['Category']}', Title='{result['Title'][:60]}{'...' if len(result['Title']) > 60 else ''}'")
        
        # Check specific categorizations
        if result['Category'] == 'Travel' and result['Title'] == 'Ride Hailing App':
            print(f"   ✅ RIDE HAILING DETECTED")
            ride_hailing_count += 1
        
        if result['Title'] == 'Zunayyara Quran':
            print(f"   ✅ SURRAIYA RIAZ RULE APPLIED")
            surraiya_count += 1
            
        if result['Category'] == 'Bills & Fees' and 'Mobile charge for' in result['Title']:
            print(f"   ✅ MOBILE TOP-UP DETECTED")
            mobile_topup_count += 1
            
        if result['Category'] == 'Transfer':
            transfer_count += 1
    
    print("\n" + "=" * 60)
    print("📈 SUMMARY ANALYSIS:")
    print(f"   Total transactions: {len(transformed)}")
    print(f"   🚗 Ride Hailing (Travel): {ride_hailing_count}")
    print(f"   📱 Mobile Top-ups (Bills & Fees): {mobile_topup_count}")
    print(f"   👤 Surraiya → Zunayyara: {surraiya_count}")
    print(f"   💸 Transfers: {transfer_count}")
    print()
    
    # Specific transaction analysis
    print("🔍 KEY TRANSACTION ANALYSIS:")
    print("-" * 30)
    
    # Find Surraiya transaction
    surraiya_found = False
    for i, result in enumerate(transformed):
        original = parse_result['data'][i]
        if 'Surraiya Riaz' in original.get('DESCRIPTION', ''):
            print(f"✓ Surraiya Riaz transaction:")
            print(f"  Amount: {original['AMOUNT']}")
            print(f"  Expected: Title='Zunayyara Quran'")
            print(f"  Actual: Title='{result['Title']}'")
            print(f"  Status: {'✅ PASS' if result['Title'] == 'Zunayyara Quran' else '❌ FAIL'}")
            surraiya_found = True
            break
    
    if not surraiya_found:
        print("❌ No Surraiya Riaz transaction found in file")
    
    # Find small ride hailing transactions
    print(f"\n✓ Small Raast Out transactions (-2000 to 0):")
    small_raast_count = 0
    correctly_categorized = 0
    
    for i, result in enumerate(transformed):
        original = parse_result['data'][i]
        if (original.get('TYPE') == 'Raast Out' and 
            original.get('AMOUNT', '').replace(',', '').replace('-', '').isdigit()):
            
            amount = -abs(float(original.get('AMOUNT', '0').replace(',', '')))
            if -2000 <= amount <= 0:
                small_raast_count += 1
                status = "✅ PASS" if (result['Category'] == 'Travel' and result['Title'] == 'Ride Hailing App') else "❌ FAIL"
                print(f"  Amount {amount}: Category='{result['Category']}', Title='{result['Title'][:30]}...' - {status}")
                if result['Category'] == 'Travel' and result['Title'] == 'Ride Hailing App':
                    correctly_categorized += 1
    
    print(f"\n  Small Raast Out summary: {correctly_categorized}/{small_raast_count} correctly categorized as Ride Hailing")
    
    # Overall assessment
    if surraiya_count > 0 and correctly_categorized > 0:
        print(f"\n🎉 SUCCESS: Core categorization rules are working!")
    else:
        print(f"\n❌ ISSUES DETECTED: Some rules are not working properly")
        if surraiya_count == 0:
            print("   - Surraiya Riaz rule not working")
        if correctly_categorized == 0:
            print("   - Ride Hailing rule not working")

if __name__ == "__main__":
    test_m022025_file()
