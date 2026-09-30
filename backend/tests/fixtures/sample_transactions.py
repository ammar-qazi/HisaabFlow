"""
Test fixtures for multi-bank processing scenarios
"""
import pytest


@pytest.fixture
def nayapay_easypaisa_transactions():
    """Sample NayaPay transactions that should trigger conditional overrides for ride-hailing"""
    return [
        {
            'Date': '2025-01-15',
            'Amount': -1500.0,
            'Title': 'Outgoing fund transfer to Payee One easypaisa Bank-0001|Transaction ID 000000000000000000000002',
            'Note': 'Raast Out',
            'Account': 'NayaPay',
            'Category': 'Transfer',
            '_source_bank': 'nayapay'
        },
        {
            'Date': '2025-01-16', 
            'Amount': -800.0,
            'Title': 'Outgoing fund transfer to Payee Two easypaisa Bank-0002|Transaction ID 000000000000000000000003',
            'Note': 'Raast Out',
            'Account': 'NayaPay',
            'Category': 'Transfer',
            '_source_bank': 'nayapay'
        },
        {
            'Date': '2025-01-17',
            'Amount': -1200.0,
            'Title': 'Outgoing fund transfer to Payee Three easypaisa Bank-0003|Transaction ID 000000000000000000000004',
            'Note': 'Raast Out',
            'Account': 'NayaPay', 
            'Category': 'Transfer',
            '_source_bank': 'nayapay'
        }
    ]


@pytest.fixture
def nayapay_non_easypaisa_transactions():
    """Sample NayaPay transactions that should NOT trigger ride-hailing overrides"""
    return [
        {
            'Date': '2025-01-15',
            'Amount': -1500.0,
            'Title': 'Outgoing fund transfer to Account Owner Meezan Bank-0000|Transaction ID 000000000000000000000005',
            'Note': 'Regular Transfer',
            'Account': 'NayaPay',
            'Category': 'Transfer',
            '_source_bank': 'nayapay'
        },
        {
            'Date': '2025-01-16',
            'Amount': -500.0,
            'Title': 'Outgoing fund transfer to Payee Four MCB Bank-0004|Transaction ID 000000000000000000000006', 
            'Note': 'Bank Transfer',
            'Account': 'NayaPay',
            'Category': 'Transfer',
            '_source_bank': 'nayapay'
        }
    ]


@pytest.fixture
def wise_multi_currency_transactions():
    """Sample Wise transactions in different currencies for account mapping tests"""
    return [
        {
            'Date': '2025-01-15',
            'Amount': -155.0,
            'Title': 'Card transaction of 155.00 EUR issued by Revolut**0540* Dublin',
            'Currency': 'EUR',
            'Account': 'Wise',  # Should become 'EURO Wise'
            'Category': 'Shopping',
            '_source_bank': 'wise'
        },
        {
            'Date': '2025-01-16',
            'Amount': -50.0,
            'Title': 'Transfer to bank account',
            'Currency': 'USD',
            'Account': 'Wise',  # Should become 'TransferWise'
            'Category': 'Transfer',
            '_source_bank': 'wise'
        },
        {
            'Date': '2025-01-17',
            'Amount': -25000.0,
            'Title': 'ATM withdrawal',
            'Currency': 'HUF',
            'Account': 'Wise',  # Should become 'Hungarian'
            'Category': 'Cash',
            '_source_bank': 'wise'
        }
    ]


@pytest.fixture 
def revolut_multi_currency_transactions():
    """Sample Revolut transactions in different currencies"""
    return [
        {
            'Date': '2025-01-15',
            'Amount': -100.0,
            'Title': 'Card payment',
            'Currency': 'EUR',
            'Account': 'Revolut',  # Should become 'Revolut EUR'
            'Category': 'Shopping',
            '_source_bank': 'revolut'
        },
        {
            'Date': '2025-01-16',
            'Amount': -50.0,
            'Title': 'Transfer',
            'Currency': 'USD', 
            'Account': 'Revolut',  # Should become 'Revolut USD'
            'Category': 'Transfer',
            '_source_bank': 'revolut'
        },
        {
            'Date': '2025-01-17',
            'Amount': -15000.0,
            'Title': 'ATM withdrawal',
            'Currency': 'HUF',
            'Account': 'Revolut',  # Should become 'Revolut Hungarian'
            'Category': 'Cash',
            '_source_bank': 'revolut'
        }
    ]


@pytest.fixture
def cross_bank_transfer_pair():
    """Sample transactions that should be detected as cross-bank transfers"""
    return {
        'outgoing': {
            'Date': '2025-01-15',
            'Amount': -1000.0,
            'Title': 'Outgoing fund transfer to John Doe',  # Matches NayaPay pattern
            'Account': 'NayaPay',
            'Category': 'Transfer',
            '_source_bank': 'nayapay'
        },
        'incoming': {
            'Date': '2025-01-15',
            'Amount': 1000.0,
            'Title': 'Received money from Jane Smith',  # Matches Wise pattern
            'Account': 'EURO Wise',
            'Category': 'Transfer', 
            '_source_bank': 'wise'
        }
    }


@pytest.fixture
def raw_data_multi_csv():
    """Sample raw_data structure for multi-CSV processing"""
    return {
        'csv_data_list': [
            {
                'data': [],  # Will be populated in tests
                'filename': 'm-02-2025.csv',
                'bank_info': {
                    'detected_bank': 'nayapay',
                    'bank_name': 'nayapay',
                    'confidence': 0.90
                }
            },
            {
                'data': [],  # Will be populated in tests
                'filename': 'statement_23243482_EUR_2025-01-04_2025-06-02.csv',
                'bank_info': {
                    'detected_bank': 'wise',
                    'bank_name': 'wise', 
                    'confidence': 0.90
                }
            },
            {
                'data': [],  # Will be populated in tests
                'filename': 'account-statement_2024-04-01_2025-06-25_en-us_b9705c.csv',
                'bank_info': {
                    'detected_bank': 'revolut',
                    'bank_name': 'revolut',
                    'confidence': 1.00
                }
            }
        ]
    }