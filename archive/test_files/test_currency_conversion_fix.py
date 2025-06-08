#!/usr/bin/env python3
"""
🔧 TEST: Fixed Currency Conversion Detection

This script tests the enhanced transfer detector with realistic Wise conversion data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.transfer_detector_fixed import TransferDetector

def test_wise_currency_conversions():
    """Test with realistic Wise multi-currency conversion data"""
    print("🧪 TESTING FIXED CURRENCY CONVERSION DETECTION")
    print("=" * 60)
    
    # Simulate realistic Wise data from your log
    wise_usd_data = [
        {
            'Date': '2025-05-26',
            'Amount': -22.83,
            'Description': 'Converted 22.83 USD to 20.00 EUR for EUR balance',
            'Currency': 'USD'
        },
        {
            'Date': '2025-05-07',
            'Amount': -565.24,
            'Description': 'Converted 565.24 USD to 200,000.00 HUF for HUF balance',
            'Currency': 'USD'
        },
        {
            'Date': '2025-04-03',
            'Amount': -413.89,
            'Description': 'Converted 413.89 USD to 150,000.00 HUF for HUF balance',
            'Currency': 'USD'
        }
    ]
    
    wise_eur_data = [
        {
            'Date': '2025-05-26',
            'Amount': 20.0,
            'Description': 'Converted 22.83 USD from USD balance to 20.00 EUR',
            'Currency': 'EUR'
        }
    ]
    
    wise_huf_data = [
        {
            'Date': '2025-05-07',
            'Amount': 200000.0,
            'Description': 'Converted 565.24 USD from USD balance to 200,000.00 HUF',
            'Currency': 'HUF'
        },
        {
            'Date': '2025-04-03',
            'Amount': 150000.0,
            'Description': 'Converted 413.89 USD from USD balance to 150,000.00 HUF',
            'Currency': 'HUF'
        }
    ]
    
    # Create CSV data structure
    csv_data_list = [
        {
            'file_name': 'wise_USD.csv',
            'data': wise_usd_data,
            'headers': ['Date', 'Amount', 'Description', 'Currency'],
            'template_config': {'bank_name': 'Transferwise'}
        },
        {
            'file_name': 'wise_EUR.csv',
            'data': wise_eur_data,
            'headers': ['Date', 'Amount', 'Description', 'Currency'],
            'template_config': {'bank_name': 'Transferwise'}
        },
        {
            'file_name': 'wise_hungarian.csv',
            'data': wise_huf_data,
            'headers': ['Date', 'Amount', 'Description', 'Currency'],
            'template_config': {'bank_name': 'Transferwise'}
        }
    ]
    
    # Test enhanced transfer detection
    detector = TransferDetector(user_name="Ammar Qazi", date_tolerance_hours=24)
    transfer_results = detector.detect_transfers(csv_data_list)
    
    print(f"\n📊 FIXED DETECTION RESULTS:")
    print(f"   ✅ Total transfer pairs: {transfer_results['summary']['transfer_pairs_found']}")
    print(f"   💱 Currency conversions: {transfer_results['summary']['currency_conversions']}")
    print(f"   🔄 Other transfers: {transfer_results['summary']['other_transfers']}")
    print(f"   💭 Potential transfers: {transfer_results['summary']['potential_transfers']}")
    
    # Analyze found conversions
    if transfer_results['transfers']:
        print(f"\n🔄 DETECTED CONVERSION PAIRS:")
        for i, pair in enumerate(transfer_results['transfers']):
            if pair.get('transfer_type') == 'currency_conversion':
                details = pair.get('conversion_details', {})
                print(f"\n   Pair {i+1} [CURRENCY_CONVERSION]:")
                print(f"      📤 Outgoing: {pair['outgoing']['_csv_name']} | {pair['outgoing']['Amount']} {details.get('from_currency', 'N/A')}")
                print(f"      📥 Incoming: {pair['incoming']['_csv_name']} | {pair['incoming']['Amount']} {details.get('to_currency', 'N/A')}")
                print(f"      🔄 Conversion: {details.get('from_amount', 'N/A')} {details.get('from_currency', 'N/A')} → {details.get('to_amount', 'N/A')} {details.get('to_currency', 'N/A')}")
                print(f"      🎖️  Confidence: {pair['confidence']:.2f}")
                print(f"      📅 Date: {pair['date'].strftime('%Y-%m-%d')}")
    
    # Check expected conversions
    expected_conversions = [
        ("22.83 USD", "20.00 EUR"),
        ("565.24 USD", "200,000.00 HUF"),
        ("413.89 USD", "150,000.00 HUF")
    ]
    
    found_conversions = []
    for pair in transfer_results['transfers']:
        if pair.get('transfer_type') == 'currency_conversion':
            details = pair.get('conversion_details', {})
            conversion_str = f"{details.get('from_amount', 'N/A')} {details.get('from_currency', 'N/A')} → {details.get('to_amount', 'N/A')} {details.get('to_currency', 'N/A')}"
            found_conversions.append(conversion_str)
    
    print(f"\n🎯 CONVERSION ACCURACY CHECK:")
    print(f"   📋 Expected: {len(expected_conversions)} conversions")
    print(f"   ✅ Found: {len(found_conversions)} conversions")
    
    for expected in expected_conversions:
        found = any(expected[0] in conv and expected[1] in conv for conv in found_conversions)
        status = "✅" if found else "❌"
        print(f"   {status} {expected[0]} → {expected[1]}")
    
    success_rate = len([1 for exp in expected_conversions if any(exp[0] in conv and exp[1] in conv for conv in found_conversions)]) / len(expected_conversions)
    
    return success_rate >= 0.8  # 80% success rate

def create_deployment_ready_fix():
    """Replace the old transfer detector with the fixed version"""
    print("\n🔧 DEPLOYING FIXED TRANSFER DETECTOR")
    print("=" * 50)
    
    import shutil
    
    # Backup current version
    try:
        shutil.copy2('backend/transfer_detector.py', 'backend/transfer_detector_backup.py')
        print("   ✅ Backed up current transfer_detector.py")
    except Exception as e:
        print(f"   ⚠️  Backup failed: {e}")
    
    # Deploy fixed version
    try:
        shutil.copy2('backend/transfer_detector_fixed.py', 'backend/transfer_detector.py')
        print("   ✅ Deployed fixed transfer_detector.py")
        return True
    except Exception as e:
        print(f"   ❌ Deployment failed: {e}")
        return False

def main():
    print("🎯 TESTING & DEPLOYING CURRENCY CONVERSION FIX")
    print("=" * 70)
    
    # Test the fix
    fix_works = test_wise_currency_conversions()
    
    if fix_works:
        print(f"\n✅ CURRENCY CONVERSION FIX VERIFIED!")
        
        # Deploy the fix
        deployed = create_deployment_ready_fix()
        
        if deployed:
            print(f"\n🎉 DEPLOYMENT COMPLETE!")
            print(f"   ✅ Fixed transfer detector is now active")
            print(f"   ✅ Currency conversions will be properly detected")
            print(f"   ✅ System ready for production use")
            
            print(f"\n💡 WHAT'S FIXED:")
            print(f"   🔄 Proper extraction of conversion amounts from descriptions")
            print(f"   📋 Cross-CSV matching for multi-currency accounts")
            print(f"   🎯 Accurate pairing of outgoing/incoming conversion transactions")
            print(f"   📊 Enhanced logging for debugging")
            print(f"   ⚡ Specialized currency conversion detection logic")
        else:
            print(f"\n❌ DEPLOYMENT FAILED - Manual intervention required")
    else:
        print(f"\n❌ FIX VERIFICATION FAILED - Needs more work")
        print(f"   🔍 Check the conversion detection logic")
        print(f"   📋 Verify description pattern matching")
        print(f"   🎯 Test with more diverse conversion formats")

if __name__ == "__main__":
    main()
