"""
Shared pytest setup.

Tests run against a throwaway copy of configs/ so they never read or write
the real configuration. This module is imported by pytest before any test
module, so HISAABFLOW_CONFIG_DIR is set before backend code resolves its
config directory (backend/infrastructure/config/paths.py).
"""
import hashlib
import os
import shutil
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPO_CONFIG_DIR = PROJECT_ROOT / "configs"
SAMPLE_DATA_DIR = PROJECT_ROOT / "sample_data"

_TEST_ROOT = Path(tempfile.mkdtemp(prefix="hisaabflow-tests-"))
TEST_CONFIG_DIR = _TEST_ROOT / "configs"
shutil.copytree(REPO_CONFIG_DIR, TEST_CONFIG_DIR)

os.environ["HISAABFLOW_CONFIG_DIR"] = str(TEST_CONFIG_DIR)


def _hash_dir(path: Path) -> dict:
    return {
        p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(path.rglob("*"))
        if p.is_file()
    }


_REPO_CONFIG_HASHES = _hash_dir(REPO_CONFIG_DIR)


@pytest.fixture(scope="session", autouse=True)
def repo_configs_untouched():
    """Fail the run if any test modified the real configs/ directory."""
    yield
    assert _hash_dir(REPO_CONFIG_DIR) == _REPO_CONFIG_HASHES, (
        "A test modified files in configs/. Tests must only use TEST_CONFIG_DIR."
    )


@pytest.fixture(scope="session")
def test_config_dir() -> Path:
    return TEST_CONFIG_DIR


def pytest_unconfigure(config):
    shutil.rmtree(_TEST_ROOT, ignore_errors=True)
