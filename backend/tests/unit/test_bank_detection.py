"""
Bank detection: expected bank per sample file, the minimum-confidence rule,
and the detection cache.
"""
import contextlib
import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.core.bank_detection.bank_detector import BankDetector
from backend.infrastructure.config.unified_config_service import get_unified_config_service
from backend.main import app
from backend.services.bank_detection_cache import BankDetectionCache, get_bank_detection_cache

SAMPLE_DATA_DIR = Path(__file__).resolve().parents[3] / "sample_data"

EXPECTED_BANK = {
    "m-02-2025.csv": "nayapay",
    "test_data_asd.csv": "nayapay",
    "statement_20141677_USD_2025-01-04_2025-06-02.csv": "wise",
    "statement_23243482_EUR_2025-01-04_2025-06-02.csv": "wise",
    "12345678-00000000-87654321_2025-06-01_2025-06-30.csv": "Erste",
    "account-statement_2024-04-01_2025-06-25_en-us_b9705c.csv": "revolut",
    "AccountFullStatement.CSV": "Meezan",
    # Banks without a config must not be forced onto one that happens to
    # share a header name or a word in the filename
    "2019-03-02_11-50-46_bunq-statement.csv": "unknown",
    "CSV_A_20180414_112204.csv": "unknown",
    "umsatz-1234________1234-20180227.CSV": "unknown",
}


@pytest.fixture
def client():
    return TestClient(app)


def _preview(client, name, content=None):
    if content is None:
        content = (SAMPLE_DATA_DIR / name).read_bytes()
    with contextlib.redirect_stdout(io.StringIO()):
        file_id = client.post("/api/v1/upload", files={"file": (name, content, "text/csv")}).json()["file_id"]
        preview = client.get(f"/api/v1/preview/{file_id}").json()
        client.delete(f"/api/v1/cleanup/{file_id}")
    return preview["bank_detection"]


def test_every_sample_file_has_an_expectation():
    assert set(EXPECTED_BANK) == {p.name for p in SAMPLE_DATA_DIR.iterdir() if p.is_file()}


@pytest.mark.parametrize("name,bank", sorted(EXPECTED_BANK.items()))
def test_sample_file_detection(client, name, bank):
    get_bank_detection_cache().clear()
    assert _preview(client, name)["detected_bank"] == bank


def test_low_confidence_keeps_best_guess_in_reasons():
    detector = BankDetector(get_unified_config_service())
    with contextlib.redirect_stdout(io.StringIO()):
        partial = detector.detect_bank("export.csv", "", ["Date"])
        full = detector.detect_bank("export.csv", "", ["Date"], min_confidence=BankDetector.MIN_CONFIDENCE)
    # Partial detections are combined later, so they are not thresholded
    assert partial.bank_name != "unknown"
    assert full.bank_name == "unknown"
    assert full.reasons[0] == f"best_guess:{partial.bank_name}"


def test_same_filename_different_content_not_shared(client):
    get_bank_detection_cache().clear()
    nayapay = (SAMPLE_DATA_DIR / "m-02-2025.csv").read_bytes()
    wise = (SAMPLE_DATA_DIR / "statement_20141677_USD_2025-01-04_2025-06-02.csv").read_bytes()

    assert _preview(client, "export.csv", nayapay)["detected_bank"] == "nayapay"
    assert _preview(client, "export.csv", wise)["detected_bank"] == "wise"


def test_cache_key_uses_content(tmp_path):
    cache = BankDetectionCache()
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    a.write_text("x,y\n1,2\n")
    b.write_text("x,y\n3,4\n")  # same size, different content

    cache.set("statement.csv", str(a), {"bank_name": "first"})
    assert cache.get("statement.csv", str(a)) == {"bank_name": "first"}
    assert cache.get("statement.csv", str(b)) is None
    assert cache.get("other.csv", str(a)) is None
    assert cache.get("statement.csv", str(tmp_path / "missing.csv")) is None


def test_config_reload_clears_detection_cache(tmp_path):
    cache = get_bank_detection_cache()
    path = tmp_path / "f.csv"
    path.write_text("x\n")
    cache.set("f.csv", str(path), {"bank_name": "stale"})

    with contextlib.redirect_stdout(io.StringIO()):
        get_unified_config_service().reload_all_configs(force=True)

    assert cache.get("f.csv", str(path)) is None
