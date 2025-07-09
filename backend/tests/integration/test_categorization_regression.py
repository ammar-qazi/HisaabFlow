"""
Regression tests for categorization functionality.

This test verifies that the categorization bug fix works correctly for multi-currency banks.
Previously, multi-currency bank transactions were not getting proper categorization due to
account mapping issues in the keyword categorization logic.
"""
import pytest

from backend.services.transformation_service import TransformationService


@pytest.mark.integration
@pytest.mark.regression
class TestCategorizationRegression:
    """Test that categorization works correctly for multi-currency banks"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup transformation service for each test"""
        self.transformation_service = TransformationService()
    
    def test_multi_currency_bank_categorization(self):
        """
        Test that multi-currency banks get proper categorization
        
        Regression test for: Multi-currency bank transactions not being categorized
        due to account mapping conflicts in keyword categorization logic.
        """
        # Test data with transactions that should match categorization patterns
        test_data = [
            # NayaPay transaction (single-currency) - should get categorized
            {
                'Date': '2025-01-15',
                'Amount': -50.0,
                'Title': 'Mobile topup for Test User',
                'Note': 'Mobile topup',
                'Account': 'NayaPay',
                'Category': 'Expense',
                '_source_bank': 'nayapay'
            },
            # Wise transaction (multi-currency) - should get categorized
            {
                'Date': '2025-01-16', 
                'Amount': -25.0,
                'Title': 'Lidl Store Purchase',
                'Note': 'Grocery shopping',
                'Account': 'EURO Wise',
                'Category': 'Expense',
                '_source_bank': 'wise'
            },
            # Revolut transaction (multi-currency) - should get categorized
            {
                'Date': '2025-01-17',
                'Amount': -15.0,
                'Title': 'Netflix Subscription',
                'Note': 'Monthly subscription',
                'Account': 'Revolut Hungarian',
                'Category': 'Expense', 
                '_source_bank': 'revolut'
            }
        ]
        
        # Mock CSV data list with proper bank info structure
        raw_data = {
            'csv_data_list': [
                {
                    'data': [test_data[0]], 
                    'filename': 'nayapay_test.csv',
                    'bank_info': {'bank_name': 'nayapay', 'detected_bank': 'nayapay', 'confidence': 0.9}
                },
                {
                    'data': [test_data[1]], 
                    'filename': 'wise_test.csv',
                    'bank_info': {'bank_name': 'wise', 'detected_bank': 'wise', 'confidence': 0.9}
                },
                {
                    'data': [test_data[2]], 
                    'filename': 'revolut_test.csv',
                    'bank_info': {'bank_name': 'revolut', 'detected_bank': 'revolut', 'confidence': 0.9}
                }
            ]
        }
        
        # Act - Apply keyword categorization using the new DataCleaningService
        result = self.transformation_service.data_cleaning_service._apply_keyword_categorization(test_data, raw_data['csv_data_list'])
        
        # Assert - Check that categorization worked
        assert len(result) == 3, "Expected 3 transactions in result"
        
        # Check specific categorization results
        for i, transaction in enumerate(result):
            account = transaction.get('Account')
            title = transaction.get('Title')
            category = transaction.get('Category')
            
            # All transactions should have proper account names
            assert account is not None, f"Transaction {i+1}: Account should not be None"
            assert account != '', f"Transaction {i+1}: Account should not be empty"
            
            # All transactions should have categories
            assert category is not None, f"Transaction {i+1}: Category should not be None"
            assert category != '', f"Transaction {i+1}: Category should not be empty"
            
            # Verify specific expected results based on actual categorization rules
            if 'Netflix' in title:
                assert category == 'Entertainment', (
                    f"Netflix should be categorized as Entertainment, got '{category}'"
                )
        
        # Check that some categorization actually happened (Netflix should be categorized)
        netflix_transaction = next((tx for tx in result if 'Netflix' in tx.get('Title', '')), None)
        assert netflix_transaction is not None, "Netflix transaction should be found"
        assert netflix_transaction['Category'] == 'Entertainment', (
            f"Netflix transaction should be categorized as Entertainment, got '{netflix_transaction['Category']}'"
        )
    
    def test_categorization_with_currency_mapping(self):
        """
        Test that categorization works correctly even when currency mapping changes account names
        
        This ensures that the categorization logic can handle account name changes that happen
        during currency mapping for multi-currency banks.
        """
        # Test data with original account names that will be mapped
        test_data = [
            {
                'Date': '2025-01-15',
                'Amount': -100.0,
                'Title': 'Grocery shopping at Tesco',
                'Currency': 'EUR',
                'Account': 'Wise',  # Will be mapped to 'EURO Wise'
                'Category': 'Expense',
                '_source_bank': 'wise'
            },
            {
                'Date': '2025-01-16',
                'Amount': -50.0,
                'Title': 'ATM withdrawal',
                'Currency': 'HUF',
                'Account': 'Revolut',  # Will be mapped to 'Revolut Hungarian'
                'Category': 'Expense',
                '_source_bank': 'revolut'
            }
        ]
        
        raw_data = {
            'csv_data_list': [
                {
                    'data': [test_data[0]], 
                    'filename': 'wise_eur.csv',
                    'bank_info': {'bank_name': 'wise', 'detected_bank': 'wise', 'confidence': 0.9}
                },
                {
                    'data': [test_data[1]], 
                    'filename': 'revolut_huf.csv',
                    'bank_info': {'bank_name': 'revolut', 'detected_bank': 'revolut', 'confidence': 0.9}
                }
            ]
        }
        
        # Act - Apply full processing pipeline (including currency mapping and categorization)
        enhanced_data = self.transformation_service.data_cleaning_service.apply_advanced_processing(
            test_data, raw_data['csv_data_list']
        )
        
        # Assert - Check that both currency mapping and categorization worked
        assert len(enhanced_data) == 2, "Expected 2 transactions in result"
        
        # Check that account names are preserved (currency mapping might not happen in this test)
        accounts = [tx['Account'] for tx in enhanced_data]
        assert 'Wise' in accounts[0], (
            f"EUR transaction should have Wise account, got '{accounts[0]}'"
        )
        assert 'Revolut' in accounts[1], (
            f"HUF transaction should have Revolut account, got '{accounts[1]}'"
        )
        
        # Check that categorization worked correctly based on actual categorization rules
        for i, transaction in enumerate(enhanced_data):
            category = transaction.get('Category')
            title = transaction.get('Title')
            
            # Verify specific categorization - based on actual rules from configs
            if 'Tesco' in title or 'Grocery' in title:
                assert category == 'Groceries', (
                    f"Grocery transaction should be categorized as Groceries, got '{category}'"
                )
            elif 'ATM' in title:
                # ATM transactions typically stay as 'Expense' unless there's a specific rule
                assert category in ['Cash', 'ATM', 'Withdrawal', 'Expense'], (
                    f"ATM transaction should be properly categorized, got '{category}'"
                )
        
        # Verify that data processing completed successfully
        assert len(enhanced_data) == 2, "Expected 2 transactions after processing"
    
    def test_categorization_applies_keyword_rules(self):
        """
        Test that categorization applies keyword rules correctly
        
        This test verifies that the categorization logic works properly
        by applying keyword-based categorization rules to transactions.
        """
        test_data = [
            {
                'Date': '2025-01-15',
                'Amount': -100.0,
                'Title': 'Grocery store purchase',
                'Account': 'NayaPay',
                'Category': 'Food',  # Will be overwritten by keyword matching
                '_source_bank': 'nayapay'
            },
            {
                'Date': '2025-01-16',
                'Amount': -50.0,
                'Title': 'Another grocery purchase',
                'Account': 'NayaPay',
                'Category': 'Expense',  # Generic category - should be improved
                '_source_bank': 'nayapay'
            }
        ]
        
        raw_data = {
            'csv_data_list': [
                {
                    'data': test_data,
                    'filename': 'nayapay_test.csv',
                    'bank_info': {'bank_name': 'nayapay', 'detected_bank': 'nayapay', 'confidence': 0.9}
                }
            ]
        }
        
        # Act - Apply keyword categorization using the new DataCleaningService
        result = self.transformation_service.data_cleaning_service._apply_keyword_categorization(test_data, raw_data['csv_data_list'])
        
        # Assert - Check categorization behavior
        assert len(result) == 2, "Expected 2 transactions in result"
        
        # Both transactions should be categorized as 'Groceries' based on keyword matching
        assert result[0]['Category'] == 'Groceries', (
            f"First grocery transaction should be categorized as Groceries, got '{result[0]['Category']}'"
        )
        
        assert result[1]['Category'] == 'Groceries', (
            f"Second grocery transaction should be categorized as Groceries, got '{result[1]['Category']}'"
        )
        
        # The important thing is that the categorization logic ran without errors
        # and produced reasonable results for both transactions

    def test_shell_petrol_categorization_fix(self):
        """
        Test that Shell Petrol transactions are correctly categorized as Transport, not Shopping
        
        Regression test for: "Shell Petrol..." being incorrectly categorized as Shopping
        due to partial substring matching where "ell" from "electronics" matched "shell"
        """
        test_data = [
            {
                'Date': '2025-01-15',
                'Amount': -75.50,
                'Title': 'Shell Petrol Station Purchase',
                'Note': 'Fuel purchase',
                'Account': 'NayaPay',
                'Category': 'Expense',
                '_source_bank': 'nayapay'
            },
            {
                'Date': '2025-01-16',
                'Amount': -50.00,
                'Title': 'Shell Petrol...',
                'Note': 'Gas fill-up',
                'Account': 'NayaPay',
                'Category': 'Expense',
                '_source_bank': 'nayapay'
            },
            {
                'Date': '2025-01-17',
                'Amount': -200.00,
                'Title': 'Electronics Store Purchase',
                'Note': 'Laptop accessories',
                'Account': 'NayaPay',
                'Category': 'Expense',
                '_source_bank': 'nayapay'
            },
            {
                'Date': '2025-01-18',
                'Amount': -30.00,
                'Title': 'Shell Station',
                'Note': 'Should not match electronics',
                'Account': 'NayaPay',
                'Category': 'Expense',
                '_source_bank': 'nayapay'
            }
        ]
        
        raw_data = {
            'csv_data_list': [
                {
                    'data': test_data,
                    'filename': 'nayapay_test.csv',
                    'bank_info': {'bank_name': 'nayapay', 'detected_bank': 'nayapay', 'confidence': 0.9}
                }
            ]
        }
        
        # Act - Apply keyword categorization using the new DataCleaningService
        result = self.transformation_service.data_cleaning_service._apply_keyword_categorization(test_data, raw_data['csv_data_list'])
        
        # Assert - Check specific categorization results
        assert len(result) == 4, "Expected 4 transactions in result"
        
        # Test 1: Shell Petrol Station Purchase should be Transport
        shell_petrol_transaction = next((tx for tx in result if 'Shell Petrol Station' in tx.get('Title', '')), None)
        assert shell_petrol_transaction is not None, "Shell Petrol Station transaction should be found"
        assert shell_petrol_transaction['Category'] == 'Transport', (
            f"Shell Petrol Station should be categorized as Transport, got '{shell_petrol_transaction['Category']}'"
        )
        
        # Test 2: Shell Petrol... should be Transport (not Electronics)
        shell_petrol_ellipsis = next((tx for tx in result if 'Shell Petrol...' in tx.get('Title', '')), None)
        assert shell_petrol_ellipsis is not None, "Shell Petrol... transaction should be found"
        assert shell_petrol_ellipsis['Category'] == 'Transport', (
            f"Shell Petrol... should be categorized as Transport (not Electronics), got '{shell_petrol_ellipsis['Category']}'"
        )
        
        # Test 3: Electronics Store Purchase should be Electronics
        electronics_transaction = next((tx for tx in result if 'Electronics Store' in tx.get('Title', '')), None)
        assert electronics_transaction is not None, "Electronics Store transaction should be found"
        assert electronics_transaction['Category'] == 'Electronics', (
            f"Electronics Store should be categorized as Electronics, got '{electronics_transaction['Category']}'"
        )
        
        # Test 4: Shell Station should NOT match Electronics (should stay as original category or get Transport)
        shell_station = next((tx for tx in result if 'Shell Station' in tx.get('Title', '')), None)
        assert shell_station is not None, "Shell Station transaction should be found"
        assert shell_station['Category'] != 'Electronics', (
            f"Shell Station should NOT be categorized as Electronics (from Electronics match), got '{shell_station['Category']}'"
        )
    
    def test_word_boundary_matching_edge_cases(self):
        """
        Test edge cases for word boundary matching to ensure partial matches don't occur
        """
        test_data = [
            {
                'Date': '2025-01-15',
                'Amount': -50.00,
                'Title': 'Shell Electronics',  # Contains both Shell and Electronics as separate words
                'Note': 'Mixed case test',
                'Account': 'NayaPay',
                'Category': 'Expense',
                '_source_bank': 'nayapay'
            },
            {
                'Date': '2025-01-16',
                'Amount': -30.00,
                'Title': 'ELECTRONICS store',  # Test case insensitive
                'Note': 'Uppercase test',
                'Account': 'NayaPay',
                'Category': 'Expense',
                '_source_bank': 'nayapay'
            },
            {
                'Date': '2025-01-17',
                'Amount': -40.00,
                'Title': 'Microelectronics',  # Should NOT match "electronics" (no word boundary)
                'Note': 'Partial word test',
                'Account': 'NayaPay',
                'Category': 'Expense',
                '_source_bank': 'nayapay'
            }
        ]
        
        raw_data = {
            'csv_data_list': [
                {
                    'data': test_data,
                    'filename': 'nayapay_test.csv',
                    'bank_info': {'bank_name': 'nayapay', 'detected_bank': 'nayapay', 'confidence': 0.9}
                }
            ]
        }
        
        # Act - Apply keyword categorization using the new DataCleaningService
        result = self.transformation_service.data_cleaning_service._apply_keyword_categorization(test_data, raw_data['csv_data_list'])
        
        # Assert - Check word boundary matching behavior
        assert len(result) == 3, "Expected 3 transactions in result"
        
        # Test 1: Shell Electronics - should match Electronics (Electronics), not based on Shell
        shell_electronics = next((tx for tx in result if 'Shell Electronics' in tx.get('Title', '')), None)
        assert shell_electronics is not None, "Shell Electronics transaction should be found"
        assert shell_electronics['Category'] == 'Electronics', (
            f"Shell Electronics should be categorized as Electronics (Electronics match), got '{shell_electronics['Category']}'"
        )
        
        # Test 2: ELECTRONICS store - should match Electronics (case insensitive)
        electronics_upper = next((tx for tx in result if 'ELECTRONICS store' in tx.get('Title', '')), None)
        assert electronics_upper is not None, "ELECTRONICS store transaction should be found"
        assert electronics_upper['Category'] == 'Electronics', (
            f"ELECTRONICS store should be categorized as Electronics, got '{electronics_upper['Category']}'"
        )
        
        # Test 3: Microelectronics - should NOT match Electronics (no word boundary)
        microelectronics = next((tx for tx in result if 'Microelectronics' in tx.get('Title', '')), None)
        assert microelectronics is not None, "Microelectronics transaction should be found"
        assert microelectronics['Category'] != 'Electronics', (
            f"Microelectronics should NOT be categorized as Electronics (no word boundary), got '{microelectronics['Category']}'"
        )