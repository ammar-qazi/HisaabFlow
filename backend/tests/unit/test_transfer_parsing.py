"""
Amount, date and name parsing used by transfer detection and the Cashew
transformer.
"""
import contextlib
import io
from datetime import datetime
from decimal import Decimal

import pytest

from backend.core.transfer_detection.amount_parser import AmountParser
from backend.core.transfer_detection.cross_bank_matcher import CrossBankMatcher
from backend.core.transfer_detection.date_parser import DateParser
from backend.infrastructure.config.unified_config_service import get_unified_config_service
from backend.services.cashew_transformer import CashewTransformer
from backend.shared.utils.amount_text import parse_amount_text

AMOUNTS = [
    ("-250.0", Decimal("-250.0")),
    (-250.5, Decimal("-250.5")),
    ("1,234.56", Decimal("1234.56")),
    ("1.234,56", Decimal("1234.56")),
    ("-6,325", Decimal("-6325")),
    ("12,50", Decimal("12.50")),
    ("1.234.567", Decimal("1234567")),
    ("PKR -500", Decimal("-500")),
    ("PKR 1,000.00", Decimal("1000.00")),
    ("500-", Decimal("-500")),
    ("(100.00)", Decimal("-100.00")),
    ("+75", Decimal("75")),
    ("€ 9,99", Decimal("9.99")),
    ("0.0", Decimal("0")),
    ("", None),
    ("nan", None),
    (None, None),
    ("abc", None),
    ("1-2", None),
    ("1,23,4", None),
]


@pytest.mark.parametrize("text,expected", AMOUNTS)
def test_parse_amount_text(text, expected):
    assert parse_amount_text(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("PKR -500", "-500.0"),
    ("500-", "-500.0"),
    ("1.234,56", "1234.56"),
    ("-250.0", "-250.0"),
    ("0.0", "0"),
    ("", "0"),
    ("abc", "0"),
])
def test_cashew_parse_amount(text, expected):
    with contextlib.redirect_stdout(io.StringIO()):
        assert CashewTransformer().parse_amount(text) == expected


def test_debit_credit_has_no_float_drift():
    with contextlib.redirect_stdout(io.StringIO()):
        rows = CashewTransformer().transform_to_cashew(
            [{"date": "2025-01-01", "title": "Fee", "debit": "0.3", "credit": "0.0"},
             {"date": "2025-01-01", "title": "Refund", "debit": "0.1", "credit": "0.4"}],
            {"date": "date", "title": "title", "debit": "debit", "credit": "credit"},
        )
    assert [r["Amount"] for r in rows] == ["-0.3", "0.3"]


def test_zero_amount_rows_are_dropped():
    with contextlib.redirect_stdout(io.StringIO()):
        rows = CashewTransformer().transform_to_cashew(
            [{"date": "2025-01-01", "title": "Zero", "amount": "0.00"},
             {"date": "2025-01-01", "title": "Real", "amount": "-5"}],
            {"date": "date", "title": "title", "amount": "amount"},
        )
    assert [r["Title"] for r in rows] == ["Real"]


@pytest.mark.parametrize("text,expected", [
    ("PKR -500", -500.0),
    ("1.234,56", 1234.56),
    ("garbage", 0.0),
])
def test_transfer_amount_parser(text, expected):
    assert AmountParser.parse_amount(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("2025-02-01", datetime(2025, 2, 1)),
    ("2025-02-01 13:45:00", datetime(2025, 2, 1, 13, 45)),
    ("2025-02-01T13:45:00", datetime(2025, 2, 1, 13, 45)),
    ("", None),
    (None, None),
    ("not a date", None),
])
def test_parse_date(text, expected):
    assert DateParser.parse_date(text) == expected


def test_unreadable_dates_never_match():
    assert not DateParser.dates_within_tolerance(None, None)
    assert not DateParser.same_day(None, datetime(2025, 1, 1))
    assert DateParser.format_date("") == ""


@pytest.fixture
def matcher():
    with contextlib.redirect_stdout(io.StringIO()):
        return CrossBankMatcher(config_service=get_unified_config_service())


def test_missing_dates_fail_the_date_tolerance_check(matcher):
    # Both used to become datetime.now(), so they looked like a same-day pair
    outgoing = {"Date": "", "Amount": "-1000"}
    incoming = {"Date": "", "Amount": "1000"}
    assert not matcher._check_date_tolerance(outgoing, incoming)


@pytest.mark.parametrize("name1,name2,match", [
    ("John Smith", "John Smith", True),
    ("John", "John Smith", True),
    ("jane doe", "Jane Doe Askari Bank-1234", True),
    ("Jane Doe Askari Bank-1234", "Jane Doe Meezan Bank-0000", True),
    ("Muhammad Ali", "Muhammad Khan", False),
    ("Ali", "Khalid Hussain", False),
    ("A B", "A C", False),
    ("", "John", False),
    (None, "John", False),
])
def test_names_match(matcher, name1, name2, match):
    assert matcher._names_match(name1, name2) is match
