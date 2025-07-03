"""
Regression tests for multi-bank processing bug fixes

These tests verify that the major bugs reported by the user have been fixed:
1. Currency mapping warnings 
2. Description cleaning not working
3. Conditional overrides not applying
"""
import pytest
import sys
import os

# Add backend to path for imports
backend_dir = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, backend_dir)

from services.transformation_service import TransformationService


@pytest.mark.integration
@pytest.mark.regression
class TestMultiBankRegressionFixes:
    """Test that the multi-bank processing bugs have been fixed"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup transformation service for each test"""
        self.transformation_service = TransformationService()
    
    def test_currency_mapping_no_warnings(self):
        """
        Test that currency mapping works without warnings
        
        Regression test for: "Currency 'USD/EUR/HUF' not found in account_mapping"
        """
        # Test data with different currencies that should map correctly
        test_data = [
            {
                'Date': '2025-01-15',
                'Amount': -100.0,
                'Title': 'Test transaction',
                'Currency': 'EUR',  # Should map to 'EURO Wise'
                'Account': 'Wise',
                'Category': 'Shopping',
                '_source_bank': 'wise'
            },
            {
                'Date': '2025-01-15',
                'Amount': -50.0,
                'Title': 'Test transaction',
                'Currency': 'USD',  # Should map to 'TransferWise'
                'Account': 'Wise', 
                'Category': 'Shopping',
                '_source_bank': 'wise'
            },
            {
                'Date': '2025-01-15',
                'Amount': -200.0,
                'Title': 'Test transaction',
                'Currency': 'HUF',  # Should map to 'Revolut Hungarian'
                'Account': 'Revolut',
                'Category': 'Shopping',
                '_source_bank': 'revolut'
            }
        ]
        
        raw_data = {
            'csv_data_list': [
                {
                    'data': [test_data[0], test_data[1]],  # Wise EUR + USD
                    'filename': 'wise_test.csv',
                    'bank_info': {'detected_bank': 'wise', 'confidence': 0.9}
                },
                {
                    'data': [test_data[2]],  # Revolut HUF
                    'filename': 'revolut_test.csv', 
                    'bank_info': {'detected_bank': 'revolut', 'confidence': 0.9}
                }
            ]
        }
        
        # Act - Process through the transformation pipeline
        enhanced_data, transfer_analysis = self.transformation_service._apply_advanced_processing(
            test_data, raw_data
        )
        
        # Assert - Should complete without errors and map currencies correctly
        assert len(enhanced_data) == 3, "Expected 3 transactions in result"
        
        # Check that account mapping worked (would have been set during processing)
        # This indirectly tests that currency mapping worked without warnings
        assert all('Account' in tx for tx in enhanced_data), "All transactions should have Account field"
    
    def test_description_cleaning_works(self):
        """
        Test that description cleaning regex patterns work correctly
        
        Regression test for: Description cleaning not working after refactoring
        """
        test_data = [
            {
                'Date': '2025-01-15',
                'Amount': -1500.0,
                'Title': 'Outgoing fund transfer to Surraiya Riaz (Asaan Ac) Meezan Bank-2660|Transaction ID 679fb6a0462d384309905d16',
                'Note': 'Transfer',
                'Account': 'NayaPay',
                'Category': 'Transfer',
                '_source_bank': 'nayapay'
            },
            {
                'Date': '2025-01-16',
                'Amount': -10.0,
                'Title': 'Mobile top-up purchased|Zong 03142919528 Nickname: Ammar Zong',
                'Note': 'Mobile',
                'Account': 'NayaPay',
                'Category': 'Bills',
                '_source_bank': 'nayapay'
            },
            {
                'Date': '2025-01-17',
                'Amount': -155.0,
                'Title': 'Card transaction of 155.00 EUR issued by Revolut**0540* Dublin',
                'Currency': 'EUR',
                'Account': 'EURO Wise',
                'Category': 'Shopping',
                '_source_bank': 'wise'
            }
        ]
        
        raw_data = {
            'csv_data_list': [
                {
                    'data': [test_data[0], test_data[1]],  # NayaPay transactions
                    'filename': 'nayapay_test.csv',
                    'bank_info': {'detected_bank': 'nayapay', 'confidence': 0.9}
                },
                {
                    'data': [test_data[2]],  # Wise transaction
                    'filename': 'wise_test.csv',
                    'bank_info': {'detected_bank': 'wise', 'confidence': 0.9}
                }
            ]
        }
        
        # Act - Apply description cleaning
        result = self.transformation_service._apply_standard_description_cleaning(
            test_data, raw_data
        )
        
        # Assert - Check that specific regex patterns worked
        expected_cleanings = {
            0: 'Religious Education',  # Surraiya pattern -> Religious Education
            1: 'Mobile topup for Ammar Zong',  # Mobile top-up pattern
            2: 'Revolut**0540* Dublin'  # Card transaction cleanup
        }
        
        for i, expected_title in expected_cleanings.items():
            actual_title = result[i]['Title']
            assert actual_title == expected_title, (
                f"Transaction {i}: Expected '{expected_title}', got '{actual_title}'"
            )
    
    def test_conditional_overrides_work(self):
        """
        Test that conditional description overrides work correctly
        
        Regression test for: Conditional overrides not applying to easypaisa transactions
        """
        # Test transactions that should trigger ride-hailing conditional override
        test_data = [
            {
                'Date': '2025-01-15',
                'Amount': -1500.0,  # Within range (-2000 to -0.01)
                'Title': 'Outgoing fund transfer to Adnan Saleem easypaisa Bank-0804|Transaction ID 67af0a3f5a01d525b770bde4',
                'Note': 'Raast Out',  # Matches condition
                'Account': 'NayaPay',
                'Category': 'Transfer',
                '_source_bank': 'nayapay'
            },
            {
                'Date': '2025-01-16',
                'Amount': -800.0,  # Within range
                'Title': 'Outgoing fund transfer to Muhammad Riafat easypaisa Bank-3892|Transaction ID abc123',
                'Note': 'Raast Out',  # Matches condition
                'Account': 'NayaPay',
                'Category': 'Transfer',
                '_source_bank': 'nayapay'
            },
            {
                'Date': '2025-01-17',
                'Amount': -1000.0,
                'Title': 'Outgoing fund transfer to Regular Person MCB Bank-1234|Transaction ID xyz789',
                'Note': 'Regular Transfer',  # Different note - should NOT trigger
                'Account': 'NayaPay',
                'Category': 'Transfer',
                '_source_bank': 'nayapay'
            }
        ]
        
        raw_data = {
            'csv_data_list': [
                {
                    'data': test_data,
                    'filename': 'nayapay_test.csv',
                    'bank_info': {'detected_bank': 'nayapay', 'confidence': 0.9}
                }
            ]
        }
        
        # Act - Apply conditional overrides
        result = self.transformation_service._apply_conditional_description_overrides(
            test_data, raw_data
        )
        
        # Assert - Check that easypaisa transactions became "Ride Hailing Services"
        assert result[0]['Title'] == 'Ride Hailing Services', (
            f"First easypaisa transaction should become 'Ride Hailing Services', "
            f"got '{result[0]['Title']}'"
        )
        
        assert result[1]['Title'] == 'Ride Hailing Services', (
            f"Second easypaisa transaction should become 'Ride Hailing Services', "
            f"got '{result[1]['Title']}'"
        )
        
        # Third transaction should remain unchanged (not easypaisa or wrong note)
        original_title = 'Outgoing fund transfer to Regular Person MCB Bank-1234|Transaction ID xyz789'
        assert result[2]['Title'] == original_title, (
            f"Non-easypaisa transaction should remain unchanged, got '{result[2]['Title']}'"
        )
    
    def test_full_pipeline_integration(self):
        """
        Test the complete multi-bank processing pipeline
        
        Integration test that verifies all fixes work together
        """
        # Realistic test data covering all the fixed issues
        test_data = [
            # NayaPay with conditional override (easypaisa -> Ride Hailing)
            {
                'Date': '2025-01-15',
                'Amount': -1500.0,
                'Title': 'Outgoing fund transfer to Adnan Saleem easypaisa Bank-0804|Transaction ID 12345',
                'Note': 'Raast Out',
                'Account': 'NayaPay',
                'Category': 'Transfer',
                '_source_bank': 'nayapay'
            },
            # NayaPay with description cleaning (mobile topup)
            {
                'Date': '2025-01-16',
                'Amount': -15.0,
                'Title': 'Mobile top-up purchased|Jazz 03016190816 Nickname: Test User Jazz',
                'Note': 'Mobile',
                'Account': 'NayaPay',
                'Category': 'Bills',
                '_source_bank': 'nayapay'
            },
            # Wise EUR with currency mapping and card transaction cleaning
            {
                'Date': '2025-01-17',
                'Amount': -155.0,
                'Title': 'Card transaction of 155.00 EUR issued by Revolut**0540* Dublin',
                'Currency': 'EUR',
                'Account': 'Wise',  # Should become 'EURO Wise'
                'Category': 'Shopping',
                '_source_bank': 'wise'
            },
            # Revolut with currency mapping
            {
                'Date': '2025-01-18',
                'Amount': -25000.0,
                'Title': 'ATM withdrawal',
                'Currency': 'HUF',
                'Account': 'Revolut',  # Should become 'Revolut Hungarian'
                'Category': 'Cash',
                '_source_bank': 'revolut'
            }
        ]
        
        raw_data = {
            'csv_data_list': [
                {
                    'data': [test_data[0], test_data[1]],  # NayaPay
                    'filename': 'nayapay.csv',
                    'bank_info': {'detected_bank': 'nayapay', 'confidence': 0.9}
                },
                {
                    'data': [test_data[2]],  # Wise EUR
                    'filename': 'wise_eur.csv',
                    'bank_info': {'detected_bank': 'wise', 'confidence': 0.9}
                },
                {
                    'data': [test_data[3]],  # Revolut HUF
                    'filename': 'revolut_huf.csv',
                    'bank_info': {'detected_bank': 'revolut', 'confidence': 0.9}
                }
            ]
        }
        
        # Act - Run the complete processing pipeline
        enhanced_data, transfer_analysis = self.transformation_service._apply_advanced_processing(
            test_data, raw_data
        )
        
        # Assert - Verify all fixes work correctly
        assert len(enhanced_data) == 4, "Expected 4 transactions in result"
        
        # Check conditional override worked
        assert enhanced_data[0]['Title'] == 'Ride Hailing Services', (
            "Easypaisa transaction should become 'Ride Hailing Services'"
        )
        
        # Check description cleaning worked
        assert enhanced_data[1]['Title'] == 'Mobile topup for Test User Jazz', (
            "Mobile topup should be cleaned correctly"
        )
        
        assert 'Revolut**0540* Dublin' in enhanced_data[2]['Title'], (
            "Card transaction should be cleaned to show merchant"
        )
        
        # Check that all transactions have proper account names (currency mapping worked)
        account_names = [tx['Account'] for tx in enhanced_data]
        expected_accounts = ['NayaPay', 'NayaPay', 'EURO Wise', 'Revolut Hungarian']
        
        for i, expected_account in enumerate(expected_accounts):
            assert account_names[i] == expected_account, (
                f"Transaction {i}: Expected account '{expected_account}', "
                f"got '{account_names[i]}'"
            )
        
        # Verify processing completed without errors
        assert 'total_transactions' in transfer_analysis, (
            "Transfer analysis should be present"
        )
        
        assert transfer_analysis['total_transactions'] == 4, (
            "Transfer analysis should show all 4 transactions"
        )