"""
Config loading and parse-path crashes fixed in Phase 1.
"""
import contextlib
import io
import shutil

import pytest

from backend.core.csv_processing.csv_processing_service import CSVProcessingService
from backend.infrastructure.config.unified_config_service import UnifiedConfigService


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


@pytest.fixture
def fresh_service(test_config_dir):
    """A new service with nothing lazily loaded yet."""
    return _quiet(UnifiedConfigService, str(test_config_dir))


@pytest.mark.parametrize("getter,expected_key", [
    ("get_column_mapping", "amount"),
    ("get_account_mapping", "eur"),
])
def test_getters_load_config_on_first_use(fresh_service, getter, expected_key):
    assert "revolut" not in fresh_service._bank_configs
    result = _quiet(getattr(fresh_service, getter), "revolut")
    assert expected_key in {k.lower() for k in result}


def test_csv_config_available_before_get_bank_config(fresh_service):
    csv_config = _quiet(fresh_service.get_csv_config, "revolut")
    assert csv_config is not None and csv_config.date_format == "%Y-%m-%d"


def test_description_cleaning_available_before_get_bank_config(fresh_service):
    cleaned = _quiet(
        fresh_service.apply_description_cleaning,
        "nayapay",
        "Outgoing fund transfer to Payee One easypaisa Bank-0001|Transaction ID 000000000000000000000001",
    )
    assert "Transaction ID" not in cleaned


def _processing_service(config_service):
    service = _quiet(CSVProcessingService, None, None, None)
    service.config_service = config_service
    return service


def test_missing_header_row_falls_back_instead_of_crashing(tmp_path, test_config_dir):
    config_dir = tmp_path / "configs"
    shutil.copytree(test_config_dir, config_dir)
    conf = config_dir / "revolut.conf"
    conf.write_text(
        "\n".join(line for line in conf.read_text().splitlines() if not line.startswith("header_row")),
        encoding="utf-8",
    )
    service = _processing_service(_quiet(UnifiedConfigService, str(config_dir)))
    csv_file = tmp_path / "statement.csv"
    csv_file.write_text("Type,Amount\nCARD,-1.00\n")

    _, header_info = _quiet(
        service._detect_bank_and_headers,
        str(csv_file), "statement.csv", None, "utf-8", False,
        {"bank_name": "revolut", "confidence": 1.0, "reasons": []},
    )

    assert header_info["header_row"] == 0
    assert header_info["data_start_row"] == 1
    assert "header_row" in header_info["error"]


def test_cleaning_with_bank_that_has_no_config(fresh_service):
    service = _processing_service(fresh_service)
    parse_result = {"success": True, "headers": ["Date", "Amount"], "data": [{"Date": "2025-01-01", "Amount": "1"}]}

    result = _quiet(service._apply_cleaning_if_enabled, parse_result, {"bank_name": "no_such_bank"}, True)

    assert result["success"]
