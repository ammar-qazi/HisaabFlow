"""
Regression tests for the Phase 1 security fixes.
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.infrastructure.config.unified_config_service import (
    get_unified_config_service,
    is_valid_bank_name,
    safe_config_path,
)


@pytest.fixture
def client():
    return TestClient(app)


def _save_request(name):
    return {
        "config": {
            "bank_info": {"name": name, "bank_name": name},
            "csv_config": {},
            "column_mapping": {},
            "data_cleaning": {},
        },
        "force_overwrite": True,
    }


@pytest.mark.parametrize("name", ["../evil", "../../tmp/evil", "/etc/evil", "a/b", "evil name", ""])
def test_save_config_rejects_unsafe_bank_names(client, test_config_dir, name):
    before = {p.name for p in test_config_dir.parent.rglob("*.conf")}

    response = client.post("/api/v1/unknown-bank/save-config", json=_save_request(name))

    assert response.status_code == 400
    assert {p.name for p in test_config_dir.parent.rglob("*.conf")} == before


def test_bank_name_can_come_from_either_field(client, test_config_dir):
    # The service writes using `name` first; the endpoint must check the same field
    request = _save_request("safe_name")
    request["config"]["bank_info"]["bank_name"] = "../evil"
    request["config"]["bank_info"]["name"] = "../evil"
    assert client.post("/api/v1/unknown-bank/save-config", json=request).status_code == 400


@pytest.mark.parametrize("name,valid", [
    ("nayapay", True), ("Erste", True), ("my_bank-2", True),
    ("../x", False), ("x/y", False), ("x.y", False), ("", False), (None, False),
])
def test_is_valid_bank_name(name, valid):
    assert is_valid_bank_name(name) is valid


def test_safe_config_path_stays_inside_config_dir(test_config_dir):
    assert safe_config_path(str(test_config_dir), "wise") == str((test_config_dir / "wise.conf").resolve())
    with pytest.raises(ValueError):
        safe_config_path(str(test_config_dir), "../app")


def test_get_bank_config_ignores_path_like_names():
    assert get_unified_config_service().get_bank_config("../configs/wise") is None


def test_shutdown_endpoint_removed(client):
    assert client.post("/shutdown").status_code in (404, 405)


@pytest.mark.parametrize("origin", ["https://evil.example", "http://localhost:3000", "null"])
def test_no_cross_origin_access(client, origin):
    # The UI is same-origin (served by the backend, or proxied in dev), so no
    # other origin, including the old dev server and Electron's "null", is allowed
    response = client.get("/api/v1/configs", headers={"Origin": origin})
    assert "access-control-allow-origin" not in response.headers
    preflight = client.options("/api/v1/upload", headers={
        "Origin": origin, "Access-Control-Request-Method": "POST"})
    assert "access-control-allow-origin" not in preflight.headers
