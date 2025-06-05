#!/usr/bin/env python3
"""
Test the new Universal Transformer system with both NayaPay and Wise data
"""

import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from enhanced_csv_parser import EnhancedCSVParser
from data_cleaner import DataCleaner

def test_nayapay_transformation():
    """Test NayaPay with Universal Transformer"""
    print("🧪 TESTING NAYAPAY WITH UNIVERSAL TRANSFORMER")
    
    # Sample NayaPay data (after cleaning)
    nayapay_data = [
        {
            'Date': '2025-02-02',
            'Amount': -5000.0,
            'Title': 'Outgoing fund transfer to Someone|Transaction ID 123456',
            'Note': 'Raast Out',
            'Currency': 'PKR'
        },
        {
            'Date': '2025-02-03',
            'Amount': -800.0,
            'Title': 'Mobile topup for Ammar',
            'Note': 'P2P',
            'Currency': 'PKR'
        },
        {
            'Date': '2025-02-04',
            'Amount': 50000.0,
            'Title': 'Incoming fund transfer from Employer',
            'Note': 'IBFT In',
            'Currency': 'PKR'
        },
        {
            'Date': '2025-02-05',
            'Amount': -1200.0,
            'Title': 'Payment to EasyPaisa user',
            'Note': 'Raast Out',
            'Currency': 'PKR'
        }
    ]
    
    # Load NayaPay Universal Template
    try:
        with open('templates/NayaPay_Universal_Template.json', 'r') as f:
            template = json.load(f)
        print(f"✅ Loaded NayaPay Universal Template")
    except Exception as e:
        print(f"❌ Error loading template: {e}")
        return
    
    # Initialize parser
    parser = EnhancedCSVParser()
    
    # Test transformation
    column_mapping = template['column_mapping']
    bank_name = template['bank_name']
    
    print(f"\n🔄 Testing transformation with {len(nayapay_data)} transactions...")
    
    try:
        result = parser.transform_to_cashew(
            nayapay_data,
            column_mapping,
            bank_name,
            None,  # No legacy categorization rules
            None,  # No default category rules
            None   # No account mapping
        )
        
        print(f"✅ NayaPay transformation successful: {len(result)} transactions")
        
        # Show results
        print(f"\n📊 NAYAPAY RESULTS:")
        for i, transaction in enumerate(result):
            print(f"   {i+1}. {transaction['Category']} - {transaction['Title']} ({transaction['Amount']})")
            
    except Exception as e:
        print(f"❌ NayaPay transformation failed: {e}")
        import traceback
        traceback.print_exc()

def test_wise_transformation():
    """Test Wise with Universal Transformer"""
    print("\n🧪 TESTING WISE WITH UNIVERSAL TRANSFORMER")
    
    # Sample Wise data (after cleaning)
    wise_data = [
        {
            'Date': '2024-03-01',
            'Amount': -3000.0,
            'Description': 'Card transaction of 3000.00 HUF issued by Barionp*Yettelfelto BUDAPEST',
            'Payment Reference': 'REF001',
            'Currency': 'HUF'
        },
        {
            'Date': '2024-03-02',
            'Amount': -8500.0,
            'Description': 'Card transaction of 8500.00 HUF issued by Lidl Budapest Central',
            'Payment Reference': 'REF002',
            'Currency': 'HUF'
        },
        {
            'Date': '2024-03-03',
            'Amount': -12000.0,
            'Description': 'Card transaction of 12000.00 HUF issued by Alza.cz Online Store',
            'Payment Reference': 'REF003',
            'Currency': 'HUF'
        },
        {
            'Date': '2024-03-04',
            'Amount': -4500.0,
            'Description': 'Card transaction of 4500.00 HUF issued by Burger King Budapest',
            'Payment Reference': 'REF004',
            'Currency': 'HUF'
        },
        {
            'Date': '2024-03-05',
            'Amount': -2800.0,
            'Description': 'Card transaction of 2800.00 HUF issued by Aldi Supermarket Chain',
            'Payment Reference': 'REF005',
            'Currency': 'HUF'
        },
        {
            'Date': '2024-03-08',
            'Amount': -15000.0,
            'Description': 'Card transaction of 15000.00 HUF issued by Szamlazz.hu Payment',
            'Payment Reference': 'REF008',
            'Currency': 'HUF'
        },
        {
            'Date': '2024-03-09',
            'Amount': 50000.0,
            'Description': 'Received money from The Blogsmith',
            'Payment Reference': 'INCOME001',
            'Currency': 'HUF'
        }
    ]
    
    # Load Wise Universal Template
    try:
        with open('templates/Wise_Universal_Template.json', 'r') as f:
            template = json.load(f)
        print(f"✅ Loaded Wise Universal Template")
    except Exception as e:
        print(f"❌ Error loading template: {e}")
        return
    
    # Initialize parser
    parser = EnhancedCSVParser()
    
    # Test transformation
    column_mapping = template['column_mapping']
    bank_name = template['bank_name']
    account_mapping = template.get('account_mapping')
    
    print(f"\n🔄 Testing transformation with {len(wise_data)} transactions...")
    
    try:
        result = parser.transform_to_cashew(
            wise_data,
            column_mapping,
            bank_name,
            None,  # No legacy categorization rules
            None,  # No default category rules
            account_mapping
        )
        
        print(f"✅ Wise transformation successful: {len(result)} transactions")
        
        # Show results
        print(f"\n📊 WISE RESULTS:")
        for i, transaction in enumerate(result):
            print(f"   {i+1}. {transaction['Category']} - {transaction['Title'][:60]}... ({transaction['Amount']}) [{transaction['Account']}]")
            
    except Exception as e:
        print(f"❌ Wise transformation failed: {e}")
        import traceback
        traceback.print_exc()

def test_comparison():
    """Compare categories between banks"""
    print(f"\n📈 COMPARISON SUMMARY")
    print(f"   🎯 Universal rules should provide consistent categorization")
    print(f"   🏦 Bank-specific overrides should handle edge cases")
    print(f"   🌍 Multi-currency support should work for Wise")
    print(f"   🧹 Description cleaning should work for both banks")

def main():
    """Run all tests"""
    print("🚀 UNIVERSAL TRANSFORMER TESTING")
    print("=" * 50)
    
    # Test NayaPay
    test_nayapay_transformation()
    
    # Test Wise
    test_wise_transformation()
    
    # Summary
    test_comparison()
    
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    main()
