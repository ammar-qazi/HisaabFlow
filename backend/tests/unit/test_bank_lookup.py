"""
bank_for_row, and the description cleaning that depends on it.
"""
import contextlib
import io
import shutil

import pytest

from backend.core.business_cleaning.data_cleaning_service import DataCleaningService
from backend.infrastructure.config.unified_config_service import (
    UnifiedConfigService,
    get_unified_config_service,
)
from backend.shared.utils.bank_lookup import bank_for_row


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


CSV_DATA_LIST = [
    {"bank_info": {"detected_bank": "nayapay"}},
    {"bank_info": {"bank_name": "wise"}},
    {"bank_info": {"detected_bank": "unknown"}},
]


@pytest.mark.parametrize("row,expected", [
    ({"_source_bank": "revolut", "Account": "Wise EUR"}, "revolut"),  # _source_bank wins
    ({"Account": "NayaPay"}, "nayapay"),                               # cashew_account
    ({"Account": "Wise EUR"}, "wise"),                                 # account_mapping value
    ({"_source_bank": "unknown", "Account": "Wise USD"}, "wise"),
    ({"Account": "Somewhere Else"}, None),
    ({}, None),
])
def test_bank_for_row(row, expected):
    assert _quiet(bank_for_row, row, CSV_DATA_LIST, get_unified_config_service()) == expected


def test_conditional_overrides_apply_to_multi_currency_banks(tmp_path, test_config_dir):
    # Before, only rows whose Account equalled cashew_account got overrides,
    # so Wise/Revolut rows (Account "Wise EUR" etc.) never did.
    config_dir = tmp_path / "configs"
    shutil.copytree(test_config_dir, config_dir)
    with open(config_dir / "wise.conf", "a", encoding="utf-8") as f:
        f.write("\n[conditional_overrides]\n"
                "card_fee = if_amount_max=-0.01, if_description_contains=Card fee | Wise card fee\n")

    service = _quiet(DataCleaningService)
    service.config_service = _quiet(UnifiedConfigService, str(config_dir))
    rows = [{"Date": "2025-01-01", "Amount": "-1.5", "Title": "Card fee 1234",
             "Account": "Wise EUR", "_source_bank": "wise"}]

    result = _quiet(service.apply_advanced_processing, rows, [{"bank_info": {"bank_name": "wise"}}])

    assert result[0]["Title"] == "Wise card fee"
