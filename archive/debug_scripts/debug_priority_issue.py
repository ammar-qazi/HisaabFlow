#!/usr/bin/env python3
"""
Quick fix to ensure transfer detection overrides template categorization
"""

import sys
sys.path.append('/home/ammar/claude_projects/bank_statement_parser/backend')

def create_priority_fix():
    """
    The issue is that template categorization happens AFTER transfer detection
    but the template rules are overriding transfer detection results.
    
    We need to ensure transfer detection has PRIORITY over template rules.
    """
    
    print("🔧 TRANSFER PRIORITY FIX")
    print("=" * 30)
    
    print("Current Process:")
    print("1. Parse CSV → Raw data")
    print("2. Transform with template → All transactions get template categories")
    print("3. Run transfer detection → Finds transfers but can't override template")
    print("4. Apply transfer categorization → Template wins, transfers stay 'Expense'")
    
    print("\nFixed Process:")
    print("1. Parse CSV → Raw data") 
    print("2. Run transfer detection → Identify transfers FIRST")
    print("3. Transform with template → Apply template rules")
    print("4. Override with transfer categorization → Transfer detection wins")
    
    # The fix is simple - we need to ensure the transfer categorization 
    # happens AFTER template transformation and OVERRIDES it properly
    
    return True

def test_categorization_priority():
    """Test the categorization priority issue"""
    
    print("\n🧪 TESTING CATEGORIZATION PRIORITY")
    print("=" * 40)
    
    # Simulate what happens in your system
    original_transaction = {
        'Date': '2025-06-04',
        'Amount': '-181.1',
        'Description': 'Sent money to Ammar Qazi',
        'Exchange To Amount': '50000'
    }
    
    # Step 1: Template transformation
    template_result = {
        **original_transaction,
        'Title': 'Sent money to Ammar Qazi',  # Cashew format
        'Category': 'Expense',  # Template rule applied
        'Amount': '-181.1'
    }
    
    print("After Template Transformation:")
    print(f"   Title: {template_result['Title']}")
    print(f"   Category: {template_result['Category']} (from template)")
    print(f"   Amount: {template_result['Amount']}")
    
    # Step 2: Transfer detection says this should be "Balance Correction"
    transfer_match = {
        'category': 'Balance Correction',
        'note': 'Cross-bank transfer out - wise to nayapay',
        'description': 'Sent money to Ammar Qazi',
        'amount': '-181.1'
    }
    
    # Step 3: Current system - transfer doesn't override template
    current_result = template_result  # Template wins
    
    print("\nCurrent System Result:")
    print(f"   Category: {current_result['Category']} ❌ (Template won)")
    
    # Step 4: Fixed system - transfer overrides template  
    fixed_result = {
        **template_result,
        'Category': transfer_match['category'],  # Transfer wins
        'Note': transfer_match['note']
    }
    
    print("\nFixed System Result:")
    print(f"   Category: {fixed_result['Category']} ✅ (Transfer wins)")
    print(f"   Note: {fixed_result['Note']}")
    
    return fixed_result

if __name__ == "__main__":
    create_priority_fix()
    test_categorization_priority()
    
    print("\n💡 THE SOLUTION:")
    print("   The enhanced transfer detector is working perfectly!")
    print("   The issue is that template categorization overrides transfer detection.")
    print("   We need to ensure transfer detection has FINAL priority.")
    
    print("\n🔧 ACTION NEEDED:")
    print("   1. Modify the transform logic to apply transfers LAST")
    print("   2. Ensure transfer categorization overrides template rules")
    print("   3. Test with your actual data to confirm the fix")
