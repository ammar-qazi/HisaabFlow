"""
Manually confirming a transfer pair in the UI calls
/apply-transfer-categorization with the transformed rows and the pair.
Matching is done on _transaction_index, so the API has to hand it out.
"""
import contextlib
import io
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app

SAMPLE_DATA_DIR = Path(__file__).resolve().parents[3] / "sample_data"
FILES = ["m-02-2025.csv", "statement_20141677_USD_2025-01-04_2025-06-02.csv"]


def _transform(client):
    file_ids, previews = [], []
    for name in FILES:
        with open(SAMPLE_DATA_DIR / name, "rb") as fh:
            file_ids.append(client.post("/api/v1/upload", files={"file": (name, fh, "text/csv")}).json()["file_id"])
        previews.append(client.get(f"/api/v1/preview/{file_ids[-1]}").json())
    parsed = client.post("/api/v1/multi-csv/parse", json={
        "file_ids": file_ids,
        "parse_configs": [{"start_row": 0, "encoding": "utf-8"} for _ in file_ids],
    }).json()["parsed_csvs"]
    csv_data_list = [
        {"filename": name, "data": p["parse_result"]["data"], "headers": p["parse_result"]["headers"],
         "bank_info": preview["bank_detection"]}
        for name, preview, p in zip(FILES, previews, parsed)
    ]
    return client.post("/api/v1/multi-csv/transform", json={"csv_data_list": csv_data_list}).json()


def test_manually_confirmed_pair_is_categorised():
    client = TestClient(app)
    with contextlib.redirect_stdout(io.StringIO()):
        result = _transform(client)
        rows = result["transformed_data"]
        outgoing = next(r for r in rows if float(r["Amount"]) < 0 and r["Account"] == "NayaPay")
        incoming = next(r for r in rows if float(r["Amount"]) > 0 and r["Account"].startswith("Wise"))
        response = client.post("/api/v1/apply-transfer-categorization", json={
            "transformed_data": rows,
            "manually_confirmed_pairs": [{"outgoing": outgoing, "incoming": incoming, "manual": True}],
            "transfer_analysis": result["transfer_analysis"],
        }).json()

    assert response["success"]
    assert response["updated_transactions"] >= 2
    updated = {r["_transaction_index"]: r for r in response["transformed_data"]}
    for tx in (outgoing, incoming):
        assert "Transfer" in updated[tx["_transaction_index"]]["Note"]


def test_export_still_has_only_cashew_columns():
    client = TestClient(app)
    with contextlib.redirect_stdout(io.StringIO()):
        rows = _transform(client)["transformed_data"]
        csv_text = client.post("/api/v1/export", json=rows).text
    assert csv_text.splitlines()[0] == "Date,Amount,Category,Title,Note,Account"
