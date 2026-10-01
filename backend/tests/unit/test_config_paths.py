"""
get_config_dir(): where the .conf files are read from and saved to.
"""
import pytest

from backend.infrastructure.config.paths import PROJECT_ROOT, get_config_dir
from backend.infrastructure.config.unified_config_service import get_unified_config_service


def test_env_var_wins(monkeypatch, tmp_path):
    monkeypatch.setenv("HISAABFLOW_CONFIG_DIR", str(tmp_path))
    assert get_config_dir() == str(tmp_path)


def test_missing_env_dir_fails_loudly(monkeypatch, tmp_path):
    monkeypatch.setenv("HISAABFLOW_CONFIG_DIR", str(tmp_path / "nope"))
    with pytest.raises(RuntimeError, match="does not exist"):
        get_config_dir()


def test_default_is_repo_configs(monkeypatch):
    monkeypatch.delenv("HISAABFLOW_CONFIG_DIR", raising=False)
    assert get_config_dir() == str(PROJECT_ROOT / "configs")


def test_services_use_the_test_config_copy(test_config_dir):
    # Every service shares the singleton, which conftest points at a temp copy
    assert get_unified_config_service().config_dir == str(test_config_dir)
