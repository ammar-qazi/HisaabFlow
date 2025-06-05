#!/usr/bin/env python3

from transformation.universal_transformer import UniversalTransformer

def test_comprehensive():
    """Test the fixed universal transformer with both NayaPay and Wise data"""
    print("🧪 Testing Fixed Universal Transformer")
    
    # Initialize transformer
    transformer = UniversalTransformer()
    
    print("\n🔥 Testing NayaPay:")
    # Test with NayaPay data
    nayapay_data = [
        {
            'Date': '2025-02-02',
            'Amount': -15000.0,  # Triggers "less than -5000" rule
            'Title': 'Outgoing fund transfer to Someone',
            'Note': 'Raast Out',
            'Currency': 'PKR'
        },
        {
            'Date': '2025-02-03',
            'Amount': -800.0,
            'Title': 'Card transaction issued by Uber',
            'Note': 'Travel',
            'Currency': 'PKR'
        }
    ]
    
    column_mapping = {
        'Date': 'Date',
        'Amount': 'Amount',
        'Title': 'Title',
        'Note': 'Note',
        'Account': ''
    }
    
    nayapay_result = transformer.transform_to_cashew(nayapay_data, column_mapping, "NayaPay")
    
    print(f"\n📊 NayaPay Results:")
    for i, row in enumerate(nayapay_result):
        print(f"   Row {i}: {row['Category']} - {row['Title']} ({row['Amount']})")
    
    print("\n🔥 Testing Wise:")
    # Test with Wise data (focusing on description cleaning)
    wise_data = [
        {
            'Date': '2025-06-01',
            'Amount': -3000.0,
            'Title': 'Card transaction of 3,000.00 HUF issued by Barionpay Ltd',
            'Note': 'Payment for online service',
            'Currency': 'HUF'
        },
        {
            'Date': '2025-05-29',
            'Amount': -6288.0,
            'Title': 'Card transaction of 6,288.00 HUF issued by Lidl Hungary',
            'Note': 'Grocery shopping',
            'Currency': 'HUF'
        }
    ]
    
    wise_column_mapping = {
        'Date': 'Date',
        'Amount': 'Amount',
        'Title': 'Title',
        'Note': 'Note',
        'Account': 'Currency'
    }
    
    # Account mapping for multi-currency
    account_mapping = {
        'HUF': 'Hungarian',
        'USD': 'TransferWise',
        'EUR': 'EURO Wise'
    }
    
    wise_result = transformer.transform_to_cashew(wise_data, wise_column_mapping, "Wise", account_mapping)
    
    print(f"\n📊 Wise Results:")
    for i, row in enumerate(wise_result):
        print(f"   Row {i}: {row['Category']} - {row['Title']} ({row['Amount']}) - Account: {row['Account']}")

if __name__ == "__main__":
    test_comprehensive()
