"""
Test the new bank-agnostic multi-CSV processing
"""
import sys
import os
import json

# Add backend path for imports
backend_path = '/home/ammar/claude_projects/bank_statement_parser/backend'
sys.path.insert(0, backend_path)

from bank_detection import BankDetector, BankConfigManager
from api.transform_endpoints import _extract_transform_data_per_bank, _create_fallback_mapping

def create_mock_csv_data():
    """Create mock CSV data to simulate frontend request"""
    
    # Mock NayaPay data (like nayapay_feb.csv)
    nayapay_data = [
        {
            'TIMESTAMP': '02 Feb 2025 11:17 PM',
            'TYPE': 'Raast Out', 
            'DESCRIPTION': 'Outgoing fund transfer to Surraiya Riaz',
            'AMOUNT': '-5,000',
            'BALANCE': '872.40'
        },
        {
            'TIMESTAMP': '03 Feb 2025 12:15 PM',
            'TYPE': 'IBFT In',
            'DESCRIPTION': 'Incoming fund transfer from Ammar Qazi', 
            'AMOUNT': '+50,000',
            'BALANCE': '50,872.40'
        }
    ]
    
    # Mock Wise data (like wise_USD.csv)
    wise_data = [
        {
            'Date': '02-06-25',
            'Amount': '-254.10',
            'Currency': 'USD',
            'Description': 'Sent money to Usama Qazi',
            'Payment Reference': 'eid-ul-adha-qurbani',
            'Exchange From': 'USD',
            'Exchange To': 'PKR'
        },
        {
            'Date': '01-06-25', 
            'Amount': '-164.00',
            'Currency': 'USD',
            'Description': 'Sent money to Zunayyara Khalid',
            'Payment Reference': 'Slovenia-tour',
            'Exchange From': '',
            'Exchange To': ''
        }
    ]
    
    # Create frontend-format request
    mock_request = {
        'csv_data_list': [
            {
                'filename': 'nayapay_feb.csv',
                'data': nayapay_data
            },
            {
                'filename': 'wise_USD.csv', 
                'data': wise_data
            }
        ]
    }
    
    return mock_request

def test_bank_agnostic_processing():
    """Test the new bank-agnostic multi-CSV processing"""
    
    print("🧪 Testing Bank-Agnostic Multi-CSV Processing")
    print("=" * 60)
    
    # Create mock data
    mock_request = create_mock_csv_data()
    print(f"📋 Created mock request with {len(mock_request['csv_data_list'])} CSV files")
    
    # Test the new extraction function
    try:
        print(f"\n🔄 Testing _extract_transform_data_per_bank function...")
        data, column_mapping, bank_name = _extract_transform_data_per_bank(mock_request)
        
        print(f"\n✅ RESULTS:")
        print(f"   📊 Total combined rows: {len(data)}")
        print(f"   🗺️ Column mapping: {column_mapping}")
        print(f"   🏦 Bank name: {bank_name}")
        
        if data:
            print(f"\n📄 Sample combined data:")
            for i, row in enumerate(data[:4]):  # Show first 4 rows
                print(f"   Row {i+1}: {row}")
                
        print(f"\n🎯 Expected Results:")
        print(f"   - Should have 4 total rows (2 NayaPay + 2 Wise)")
        print(f"   - NayaPay rows should have Title='Outgoing fund transfer to Surraiya Riaz', etc.")
        print(f"   - Wise rows should have Title='Sent money to Usama Qazi', etc.")
        print(f"   - All rows should have standardized column names (Date, Amount, Title, Note)")
        
        # Validate the results
        if len(data) == 4:
            print(f"✅ Correct number of rows combined")
        else:
            print(f"❌ Expected 4 rows, got {len(data)}")
            
        # Check if Title field is populated (this was the original bug)
        empty_titles = [row for row in data if not row.get('Title', '').strip()]
        if not empty_titles:
            print(f"✅ All rows have populated Title field - Bug 6 FIXED!")
        else:
            print(f"❌ Found {len(empty_titles)} rows with empty Title - Bug 6 still exists")
            
    except Exception as e:
        print(f"❌ Error testing bank-agnostic processing: {str(e)}")
        import traceback
        print(f"📖 Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_bank_agnostic_processing()
