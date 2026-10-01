"""
Logging setup for the backend. Level comes from HISAABFLOW_LOG_LEVEL
(default INFO). DEBUG shows processing details but never transaction data.
"""
import logging
import os


def configure_logging() -> None:
    level_name = os.environ.get("HISAABFLOW_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level_name, logging.INFO),
        format="%(levelname)s %(name)s: %(message)s",
    )
