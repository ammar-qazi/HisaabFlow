"""
/config/{name} must accept every name /configs hands out.
"""
import contextlib
import io

import pytest
from fastapi.testclient import TestClient

from backend.infrastructure.config.unified_config_service import get_unified_config_service
from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_every_listed_config_can_be_loaded(client):
    listed = client.get("/api/v1/configs").json()
    for name in listed["configurations"]:
        assert client.get(f"/api/v1/config/{name}").status_code == 200, name


def test_display_name_that_differs_from_bank_name(client, test_config_dir):
    # Banks saved from the unknown-bank panel get a display_name of their own
    conf = test_config_dir / "lookup_test.conf"
    conf.write_text((test_config_dir / "revolut.conf").read_text(encoding="utf-8")
                    .replace("name = revolut", "name = lookup_test\ndisplay_name = Something Else", 1),
                    encoding="utf-8")
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            get_unified_config_service().reload_all_configs(force=True)
        assert "Something Else Configuration" in client.get("/api/v1/configs").json()["configurations"]
        response = client.get("/api/v1/config/Something Else Configuration")
        assert response.status_code == 200
        assert response.json()["bank_name"] == "lookup_test"
    finally:
        conf.unlink()
        with contextlib.redirect_stdout(io.StringIO()):
            get_unified_config_service().reload_all_configs(force=True)
