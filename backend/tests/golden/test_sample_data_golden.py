"""
Golden-file tests: run every file in sample_data/ through the same API calls
the frontend makes (upload -> preview -> parse -> transform -> export) and
compare the result with a stored snapshot.

These tests pin down current behaviour, bugs included, so that refactoring
cannot change output silently. When a change is meant to alter the output,
regenerate the snapshots and review the diff:

    UPDATE_GOLDEN=1 pytest backend/tests/golden
    git diff backend/tests/golden/snapshots
"""
import contextlib
import io
import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.bank_detection_cache import get_bank_detection_cache

SAMPLE_DATA_DIR = Path(__file__).resolve().parents[3] / "sample_data"
SNAPSHOT_DIR = Path(__file__).parent / "snapshots"
UPDATE = os.environ.get("UPDATE_GOLDEN") == "1"

SINGLE_FILES = sorted(p.name for p in SAMPLE_DATA_DIR.iterdir() if p.is_file())

# Files from the banks that have a config, processed together so that
# cross-bank transfer detection is exercised.
SUPPORTED_BANK_FILES = [
    "m-02-2025.csv",                                          # NayaPay
    "statement_20141677_USD_2025-01-04_2025-06-02.csv",       # Wise USD
    "statement_23243482_EUR_2025-01-04_2025-06-02.csv",       # Wise EUR
    "12345678-00000000-87654321_2025-06-01_2025-06-30.csv",   # Erste
    "account-statement_2024-04-01_2025-06-25_en-us_b9705c.csv",  # Revolut
    "AccountFullStatement.CSV",                               # Meezan
]

SCENARIOS = {f"single__{name}": [name] for name in SINGLE_FILES}
SCENARIOS["combined__supported_banks"] = SUPPORTED_BANK_FILES


def _strip_volatile(value):
    """Drop fields that change between runs or only duplicate other fields."""
    if isinstance(value, dict):
        return {
            k: _strip_volatile(v)
            for k, v in value.items()
            if k not in {"file_id", "_raw_data", "temp_path"}
        }
    if isinstance(value, list):
        return [_strip_volatile(v) for v in value]
    return value


def _run_pipeline(client: TestClient, filenames):
    """Mirror the request sequence in frontend/src/handlers/*.js."""
    get_bank_detection_cache().clear()
    result = {"files": filenames}

    file_ids, previews, parse_configs = [], [], []
    for name in filenames:
        with open(SAMPLE_DATA_DIR / name, "rb") as fh:
            upload = client.post("/api/v1/upload", files={"file": (name, fh, "text/csv")})
        assert upload.status_code == 200, upload.text
        file_id = upload.json()["file_id"]
        file_ids.append(file_id)

        preview = client.get(f"/api/v1/preview/{file_id}")
        preview_json = preview.json() if preview.status_code == 200 else {}
        previews.append(preview_json)

        # Same start_row rule as parseAllFiles in processingHandlers.js
        start_row = preview_json.get("suggested_data_start_row")
        if start_row is None and preview_json.get("suggested_header_row") is not None:
            start_row = preview_json["suggested_header_row"] + 1
        parse_configs.append({
            "start_row": start_row or 0,
            "end_row": None,
            "start_col": 0,
            "end_col": None,
            "encoding": "utf-8",
        })

    result["detection"] = [
        {"file": name, "status": 200 if p else "error", "bank_detection": p.get("bank_detection")}
        for name, p in zip(filenames, previews)
    ]

    try:
        parse = client.post(
            "/api/v1/multi-csv/parse",
            json={"file_ids": file_ids, "parse_configs": parse_configs},
        )
        result["parse_status"] = parse.status_code
        if parse.status_code != 200:
            result["parse_error"] = parse.json().get("detail")
            return result

        parsed = parse.json()["parsed_csvs"]
        result["parse"] = [
            {
                "filename": item["filename"],
                "success": item["parse_result"].get("success"),
                "bank_info": item.get("bank_info"),
                "headers": item["parse_result"].get("headers"),
                "row_count": item["parse_result"].get("row_count"),
                "error": item["parse_result"].get("error"),
            }
            for item in parsed
        ]

        # Same payload as transformAllFiles in processingHandlers.js
        csv_data_list = [
            {
                "filename": name,
                "data": item["parse_result"]["data"],
                "headers": item["parse_result"]["headers"],
                "bank_info": preview.get("bank_detection") or item.get("bank_info") or {},
            }
            for name, preview, item in zip(filenames, previews, parsed)
            if item["parse_result"].get("success")
        ]
        if not csv_data_list:
            return result

        transform = client.post("/api/v1/multi-csv/transform", json={"csv_data_list": csv_data_list})
        result["transform_status"] = transform.status_code
        if transform.status_code != 200:
            result["transform_error"] = transform.json().get("detail")
            return result
        transformed = transform.json()
        result["transformation_summary"] = transformed.get("transformation_summary")
        result["transfer_analysis"] = transformed.get("transfer_analysis")
        result["transformed_data"] = transformed.get("transformed_data")

        export = client.post("/api/v1/export", json=transformed["transformed_data"])
        result["export_status"] = export.status_code
        result["export_csv"] = export.text.splitlines()
        return result
    finally:
        for file_id in file_ids:
            client.delete(f"/api/v1/cleanup/{file_id}")


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.mark.golden
@pytest.mark.parametrize("scenario", sorted(SCENARIOS))
def test_sample_data_matches_snapshot(client, scenario):
    # The backend prints every row it touches; keep test output readable.
    with contextlib.redirect_stdout(io.StringIO()):
        actual = _strip_volatile(_run_pipeline(client, SCENARIOS[scenario]))
    actual_text = json.dumps(actual, indent=2, ensure_ascii=False, sort_keys=True) + "\n"

    snapshot = SNAPSHOT_DIR / f"{scenario}.json"
    if UPDATE or not snapshot.exists():
        SNAPSHOT_DIR.mkdir(exist_ok=True)
        snapshot.write_text(actual_text, encoding="utf-8")
        if not UPDATE:
            pytest.fail(f"Snapshot {snapshot.name} did not exist and was created. Review it and re-run.")
        return

    expected_text = snapshot.read_text(encoding="utf-8")
    assert actual_text == expected_text, (
        f"Output for {scenario} differs from {snapshot.name}. If the change is intended, "
        f"run UPDATE_GOLDEN=1 pytest backend/tests/golden and review the snapshot diff."
    )
