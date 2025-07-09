"""
Integration tests for conditional description overrides

These tests verify that bank-specific conditional overrides work correctly,
particularly for NayaPay ride-hailing service detection.
"""
import pytest

from backend.services.transformation_service import TransformationService
from backend.tests.fixtures.sample_transactions import (
    nayapay_easypaisa_transactions,
    nayapay_non_easypaisa_transactions,
    raw_data_multi_csv
)


@pytest.mark.integration
@pytest.mark.multi_bank
class TestConditionalDescriptionOverrides:
    """Test conditional description overrides functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup transformation service for each test"""
        self.transformation_service = TransformationService()
    
    def test_easypaisa_transactions_become_ride_hailing_services(
        self, 
        nayapay_easypaisa_transactions,
        raw_data_multi_csv
    ):
        """
        Test that NayaPay easypaisa transactions are converted to 'Ride Hailing Services'
        
        This is the main conditional override that should work:
        - if_description_contains = Outgoing fund transfer to
        - if_amount_min = -2000 
        - if_amount_max = -0.01
        - if_note_equals = Raast Out
        - set_description = Ride Hailing Services
        """
        # Arrange
        test_data = nayapay_easypaisa_transactions.copy()
        raw_data = raw_data_multi_csv.copy()
        raw_data['csv_data_list'][0]['data'] = test_data
        
        # Act - Apply conditional overrides
        result = self.transformation_service.data_cleaning_service._apply_conditional_description_overrides(
            test_data, raw_data['csv_data_list']
        )
        
        # Assert - All easypaisa transactions should become 'Ride Hailing Services'
        expected_title = 'Ride Hailing Services'
        
        for transaction in result:
            original_title = transaction['Title']
            if 'easypaisa' in original_title:
                assert transaction['Title'] == expected_title, (
                    f"Expected '{expected_title}' but got '{transaction['Title']}' "
                    f"for transaction: {original_title}"
                )
    
    def test_non_easypaisa_transactions_unchanged(
        self,
        nayapay_non_easypaisa_transactions, 
        raw_data_multi_csv
    ):
        """
        Test that non-easypaisa NayaPay transactions are NOT changed by conditional overrides
        """
        # Arrange
        test_data = nayapay_non_easypaisa_transactions.copy()
        original_titles = [t['Title'] for t in test_data]
        raw_data = raw_data_multi_csv.copy()
        raw_data['csv_data_list'][0]['data'] = test_data
        
        # Act
        result = self.transformation_service.data_cleaning_service._apply_conditional_description_overrides(
            test_data, raw_data['csv_data_list']
        )
        
        # Assert - Titles should remain unchanged
        for i, transaction in enumerate(result):
            assert transaction['Title'] == original_titles[i], (
                f"Non-easypaisa transaction was unexpectedly changed: "
                f"'{original_titles[i]}' -> '{transaction['Title']}'"
            )
    
    def test_conditional_override_conditions_detailed(
        self,
        raw_data_multi_csv
    ):
        """
        Test specific conditional override conditions in detail
        """
        # Test transaction that should match all conditions
        matching_transaction = [{
            'Date': '2025-01-15',
            'Amount': -1500.0,  # Between -2000 and -0.01 ✓
            'Title': 'Outgoing fund transfer to Adnan Saleem easypaisa Bank-0804|Transaction ID xyz',  # Contains 'Outgoing fund transfer to' ✓
            'Note': 'Raast Out',  # Equals 'Raast Out' ✓
            'Account': 'NayaPay',
            'Category': 'Transfer', 
            '_source_bank': 'nayapay'
        }]
        
        raw_data = raw_data_multi_csv.copy()
        raw_data['csv_data_list'][0]['data'] = matching_transaction
        
        # Act
        result = self.transformation_service.data_cleaning_service._apply_conditional_description_overrides(
            matching_transaction, raw_data['csv_data_list']
        )
        
        # Assert
        assert result[0]['Title'] == 'Ride Hailing Services'
    
    def test_conditional_override_amount_boundary_conditions(
        self,
        raw_data_multi_csv
    ):
        """
        Test amount boundary conditions for conditional overrides
        """
        test_cases = [
            {
                'amount': -0.01,  # Exactly at max boundary - should match
                'should_match': True,
                'description': 'amount at max boundary'
            },
            {
                'amount': 0.0,  # Above max boundary - should not match
                'should_match': False,
                'description': 'amount above max boundary'
            },
            {
                'amount': -2000.0,  # Exactly at min boundary - should match  
                'should_match': True,
                'description': 'amount at min boundary'
            },
            {
                'amount': -2000.01,  # Below min boundary - should not match
                'should_match': False,
                'description': 'amount below min boundary'
            }
        ]
        
        for test_case in test_cases:
            # Arrange
            transaction = [{
                'Date': '2025-01-15',
                'Amount': test_case['amount'],
                'Title': 'Outgoing fund transfer to Test Person easypaisa Bank-1234|Transaction ID xyz',
                'Note': 'Raast Out',
                'Account': 'NayaPay',
                'Category': 'Transfer',
                '_source_bank': 'nayapay'
            }]
            
            original_title = transaction[0]['Title']
            raw_data = raw_data_multi_csv.copy()
            raw_data['csv_data_list'][0]['data'] = transaction
            
            # Act
            result = self.transformation_service.data_cleaning_service._apply_conditional_description_overrides(
                transaction, raw_data['csv_data_list']
            )
            
            # Assert
            if test_case['should_match']:
                assert result[0]['Title'] == 'Ride Hailing Services', (
                    f"Expected conditional override to apply for {test_case['description']} "
                    f"(amount: {test_case['amount']}), but title remained: {result[0]['Title']}"
                )
            else:
                assert result[0]['Title'] == original_title, (
                    f"Expected conditional override NOT to apply for {test_case['description']} "
                    f"(amount: {test_case['amount']}), but title changed to: {result[0]['Title']}"
                )
    
    def test_note_field_requirement(
        self,
        raw_data_multi_csv
    ):
        """
        Test that the 'if_note_equals = Raast Out' condition is properly enforced
        """
        test_cases = [
            {
                'note': 'Raast Out',
                'should_match': True,
                'description': 'exact note match'
            },
            {
                'note': 'raast out',  # Different case
                'should_match': False,
                'description': 'case mismatch'
            },
            {
                'note': 'Some other note',
                'should_match': False,
                'description': 'different note'
            },
            {
                'note': '',  # Empty note
                'should_match': False,
                'description': 'empty note'
            }
        ]
        
        for test_case in test_cases:
            # Arrange
            transaction = [{
                'Date': '2025-01-15',
                'Amount': -1500.0,
                'Title': 'Outgoing fund transfer to Test Person easypaisa Bank-1234|Transaction ID xyz',
                'Note': test_case['note'],
                'Account': 'NayaPay',
                'Category': 'Transfer',
                '_source_bank': 'nayapay'
            }]
            
            original_title = transaction[0]['Title']
            raw_data = raw_data_multi_csv.copy()
            raw_data['csv_data_list'][0]['data'] = transaction
            
            # Act
            result = self.transformation_service.data_cleaning_service._apply_conditional_description_overrides(
                transaction, raw_data['csv_data_list']
            )
            
            # Assert
            if test_case['should_match']:
                assert result[0]['Title'] == 'Ride Hailing Services', (
                    f"Expected conditional override to apply for {test_case['description']} "
                    f"(note: '{test_case['note']}'), but title remained: {result[0]['Title']}"
                )
            else:
                assert result[0]['Title'] == original_title, (
                    f"Expected conditional override NOT to apply for {test_case['description']} "
                    f"(note: '{test_case['note']}'), but title changed to: {result[0]['Title']}"
                )