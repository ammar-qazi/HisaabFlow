"""
Where the bank and app .conf files live.
"""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def get_config_dir() -> str:
    """
    HISAABFLOW_CONFIG_DIR if set (the Docker image sets /data/configs),
    otherwise the repository's configs/ directory.
    """
    configured = os.environ.get("HISAABFLOW_CONFIG_DIR")
    if configured:
        if not os.path.isdir(configured):
            raise RuntimeError(f"HISAABFLOW_CONFIG_DIR does not exist: {configured}")
        return configured
    return str(PROJECT_ROOT / "configs")
